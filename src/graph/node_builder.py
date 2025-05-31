"""
Node builder for graph visualization.
"""

from typing import Dict, Any, Tuple
from src.constants import NODE_TYPES, POS_MAP
from src.graph.color_schemes import get_node_color, get_pos_color, get_node_style, get_node_size


class NodeBuilder:
    """Builds nodes with appropriate properties for graph visualization."""
    
    def __init__(self, color_scheme: str = "Default", size_multiplier: float = 1.0):
        self.color_scheme = color_scheme
        self.size_multiplier = size_multiplier
    
    def build_node_config(self, node_id: str, node_data: Dict[str, Any], 
                         node_labels: Dict[str, str], show_labels: bool = True) -> Dict[str, Any]:
        """
        Build complete node configuration for visualization.
        
        Args:
            node_id: The node identifier
            node_data: Node data from the graph
            node_labels: Mapping of node IDs to labels
            show_labels: Whether to show labels on nodes
            
        Returns:
            Dictionary of node configuration properties
        """
        node_type = node_data.get('node_type', 'unknown')
        
        # Get base configuration based on node type
        if node_type == NODE_TYPES['BREADCRUMB']:
            config = self._build_breadcrumb_node(node_id, node_data)
        elif node_type == NODE_TYPES['MAIN']:
            config = self._build_main_node(node_id, node_data)
        elif node_type == NODE_TYPES['WORD_SENSE']:
            config = self._build_word_sense_node(node_id, node_data)
        elif node_type == NODE_TYPES['SYNSET']:
            config = self._build_synset_node(node_id, node_data)
        elif node_type == NODE_TYPES['WORD']:
            config = self._build_word_node(node_id, node_data)
        else:
            config = self._build_default_node(node_id, node_data)
        
        # Add label
        label = node_labels.get(node_id, node_id) if show_labels else ""
        config['label'] = label
        
        # Add font configuration
        config['font'] = {
            'size': int(12 * self.size_multiplier),
            'color': 'black'
        }
        
        return config
    
    def _build_breadcrumb_node(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build configuration for breadcrumb node."""
        return {
            'color': get_node_color('breadcrumb', self.color_scheme),
            'size': get_node_size('breadcrumb', self.size_multiplier),
            'title': f"Back to: {node_data.get('original_word', 'Previous word')}",
            **get_node_style('breadcrumb')
        }
    
    def _build_main_node(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build configuration for main word node."""
        return {
            'color': get_node_color('main', self.color_scheme),
            'size': get_node_size('main', self.size_multiplier),
            'title': f"Main word: {node_data.get('word', '').upper()}",
            **get_node_style('main')
        }
    
    def _build_word_sense_node(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build configuration for word sense node."""
        synset_name = node_data.get('synset_name', node_id)
        definition = node_data.get('definition', 'No definition')
        word = node_data.get('word', '')
        sense_num = node_data.get('sense_number', '')
        
        return {
            'color': get_node_color('word_sense', self.color_scheme),
            'size': get_node_size('word_sense', self.size_multiplier),
            'title': f"Word sense: {word} (sense {sense_num})\nSynset: {synset_name}\nDefinition: {definition}",
            **get_node_style('word_sense')
        }
    
    def _build_synset_node(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build configuration for synset node."""
        pos = node_data.get('pos', 'n')
        synset_name = node_data.get('synset_name', node_id)
        definition = node_data.get('definition', 'No definition')
        pos_label = POS_MAP.get(pos, 'noun')
        
        return {
            'color': get_pos_color(pos, self.color_scheme),
            'size': get_node_size('synset', self.size_multiplier),
            'title': f"Synset: {synset_name}\nPOS: {pos_label}\nDefinition: {definition}",
            **get_node_style('synset')
        }
    
    def _build_word_node(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build configuration for word node."""
        word = node_data.get('word', node_id)
        
        return {
            'color': get_node_color('word', self.color_scheme),
            'size': get_node_size('word', self.size_multiplier),
            'title': f"Word: {word}",
            **get_node_style('word')
        }
    
    def _build_default_node(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build configuration for unknown node types."""
        return {
            'color': '#CCCCCC',
            'size': get_node_size('default', self.size_multiplier),
            'title': f"Node: {node_id}"
        } 