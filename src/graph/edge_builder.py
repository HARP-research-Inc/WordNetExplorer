"""
Edge builder for graph visualization.
"""

from typing import Dict, Any, Tuple, Optional
from src.constants import RELATIONSHIP_TYPES, RELATIONSHIP_COLORS


class EdgeBuilder:
    """Builds edges with appropriate properties for graph visualization."""
    
    def __init__(self, edge_width: int = 2):
        self.edge_width = edge_width
        self.relationship_descriptions = {
            'sense': 'Word sense connection',
            'hypernym': 'Is-a relationship (more general)',
            'hyponym': 'Is-a relationship (more specific)',
            'member_meronym': 'Part-of relationship (member)',
            'substance_meronym': 'Part-of relationship (substance)',
            'part_meronym': 'Part-of relationship (part)',
            'member_holonym': 'Has-part relationship (has member)',
            'substance_holonym': 'Has-part relationship (has substance)',
            'part_holonym': 'Has-part relationship (has part)',
            'similar_to': 'Similar to',
            'antonym': 'Opposite of',
            'also_see': 'Related to',
            'entailment': 'Entails',
            'entails': 'Entails',
            'cause': 'Causes',
            'causes': 'Causes',
            'attribute': 'Attribute of',
            'verb_group': 'Verb group',
            'derivationally_related_form': 'Derived from',
            'pertainym': 'Pertains to'
        }
    
    def build_edge_config(self, source: str, target: str, edge_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build complete edge configuration for visualization.
        
        Args:
            source: Source node ID
            target: Target node ID
            edge_data: Edge data from the graph
            
        Returns:
            Dictionary containing edge configuration and actual source/target
        """
        relation = edge_data.get('relation', 'unknown')
        arrow_direction = edge_data.get('arrow_direction', 'to')
        
        # Determine actual source and target based on relationship type
        actual_source, actual_target = self._determine_edge_direction(
            source, target, relation, arrow_direction
        )
        
        # Get edge color
        color = edge_data.get('color', RELATIONSHIP_COLORS.get(relation, RELATIONSHIP_COLORS['default']))
        
        # Generate description
        description = self._generate_edge_description(actual_source, actual_target, relation)
        
        # Build edge configuration
        config = {
            'source': actual_source,
            'target': actual_target,
            'color': color,
            'width': self._get_edge_width(relation),
            'title': description,
            'arrows': 'to'
        }
        
        return config
    
    def _determine_edge_direction(self, source: str, target: str, 
                                relation: str, arrow_direction: str) -> Tuple[str, str]:
        """
        Determine the actual source and target for the edge based on relationship semantics.
        
        Args:
            source: Original source node
            target: Original target node
            relation: Type of relationship
            arrow_direction: Configured arrow direction
            
        Returns:
            Tuple of (actual_source, actual_target)
        """
        # For taxonomic relationships, ensure consistent direction: specific → general
        if relation in ['hypernym', 'hyponym']:
            if relation == 'hypernym':
                # Hypernym: source is more specific than target
                # Arrow goes source → target (specific → general)
                return source, target
            else:  # hyponym
                # Hyponym: source is more general than target
                # Arrow goes target → source (specific → general)
                return target, source
        
        # For other relationships, respect the arrow_direction parameter
        if arrow_direction == 'from':
            return target, source
        else:
            return source, target
    
    def _generate_edge_description(self, source: str, target: str, relation: str) -> str:
        """
        Generate a human-readable description for the edge.
        
        Args:
            source: Source node (after direction adjustment)
            target: Target node (after direction adjustment)
            relation: Type of relationship
            
        Returns:
            Description string
        """
        # Extract meaningful names from node IDs
        source_name = self._extract_node_name(source)
        target_name = self._extract_node_name(target)
        
        # Get base description
        base_desc = self.relationship_descriptions.get(relation, relation.replace('_', ' ').title())
        
        # Special formatting for specific relationship types
        if relation in ['hypernym', 'hyponym']:
            return f"{base_desc}: {source_name} is a type of {target_name}"
        elif relation in ['member_meronym', 'substance_meronym', 'part_meronym']:
            return f"{base_desc}: {source_name} is part of {target_name}"
        elif relation in ['member_holonym', 'substance_holonym', 'part_holonym']:
            return f"{base_desc}: {source_name} has {target_name}"
        elif relation == 'antonym':
            return f"{base_desc}: {source_name} ↔ {target_name}"
        else:
            return f"{base_desc}: {source_name} → {target_name}"
    
    def _extract_node_name(self, node_id: str) -> str:
        """
        Extract a readable name from a node ID.
        
        Args:
            node_id: The node identifier
            
        Returns:
            Human-readable name
        """
        # Handle synset names (e.g., 'dog.n.01')
        if '.' in node_id and node_id.count('.') == 2:
            return node_id.split('.')[0]
        
        # Handle special node types
        for suffix in ['_main', '_breadcrumb', '_word', '_sense']:
            if node_id.endswith(suffix):
                return node_id[:-len(suffix)].replace('_', ' ')
        
        # Handle ROOT_ prefix
        if node_id.startswith('ROOT_'):
            return node_id[5:].lower()
        
        # Default: return as is
        return node_id.replace('_', ' ')
    
    def _get_edge_width(self, relation: str) -> int:
        """
        Get the width for an edge based on its relationship type.
        
        Args:
            relation: Type of relationship
            
        Returns:
            Edge width in pixels
        """
        # Sense connections are thinner
        if relation == 'sense':
            return self.edge_width
        
        # All other relationships are slightly thicker
        return self.edge_width + 1 