"""
Settings data models using dataclasses for type safety and validation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from src.constants import DEFAULT_DEPTH, DEFAULT_MAX_NODES, DEFAULT_MAX_BRANCHES


@dataclass
class RelationshipSettings:
    """Settings for which relationships to include in the graph."""
    # Taxonomic Relations
    show_hypernym: bool = False
    show_hyponym: bool = False
    show_instance_hypernym: bool = False
    show_instance_hyponym: bool = False
    
    # Part-Whole Relations
    show_member_holonym: bool = False
    show_substance_holonym: bool = False
    show_part_holonym: bool = False
    show_member_meronym: bool = False
    show_substance_meronym: bool = False
    show_part_meronym: bool = False
    
    # Similarity & Opposition
    show_antonym: bool = False
    show_similar_to: bool = False
    
    # Other Relations
    show_entailment: bool = False
    show_cause: bool = False
    show_attribute: bool = False
    show_also_see: bool = False
    show_verb_group: bool = False
    show_participle_of_verb: bool = False
    show_derivationally_related_form: bool = False
    show_pertainym: bool = False
    show_derived_from: bool = False
    
    # Domain Relations
    show_domain_of_synset_topic: bool = False
    show_member_of_domain_topic: bool = False
    show_domain_of_synset_region: bool = False
    show_member_of_domain_region: bool = False
    show_domain_of_synset_usage: bool = False
    show_member_of_domain_usage: bool = False
    
    def get_active_relationships(self) -> List[str]:
        """Get list of active relationship types."""
        active = []
        for attr, value in vars(self).items():
            if attr.startswith('show_') and value:
                # Convert show_xxx to xxx
                rel_type = attr[5:]
                active.append(rel_type)
        return active
    
    def has_any_active(self) -> bool:
        """Check if any relationships are enabled."""
        return any(value for attr, value in vars(self).items() 
                  if attr.startswith('show_') and value)


@dataclass
class ExplorationSettings:
    """Settings for graph exploration parameters."""
    depth: int = DEFAULT_DEPTH
    max_nodes: int = DEFAULT_MAX_NODES
    max_branches: int = DEFAULT_MAX_BRANCHES
    min_frequency: int = 0
    pos_filter: List[str] = field(default_factory=lambda: ["Nouns", "Verbs", "Adjectives", "Adverbs"])
    enable_clustering: bool = False
    enable_cross_connections: bool = True
    simplified_mode: bool = False
    
    # Word/synset specific settings
    word: Optional[str] = None
    sense_number: Optional[int] = None
    synset_search_mode: bool = False
    
    def validate(self) -> List[str]:
        """Validate settings and return list of errors."""
        errors = []
        
        if self.depth < 1 or self.depth > 10:
            errors.append(f"Depth must be between 1 and 10 (got {self.depth})")
        
        if self.max_nodes < 1 or self.max_nodes > 1000:
            errors.append(f"Max nodes must be between 1 and 1000 (got {self.max_nodes})")
        
        if self.max_branches < 1 or self.max_branches > 20:
            errors.append(f"Max branches must be between 1 and 20 (got {self.max_branches})")
        
        if self.min_frequency < 0 or self.min_frequency > 100:
            errors.append(f"Min frequency must be between 0 and 100 (got {self.min_frequency})")
        
        valid_pos = ["Nouns", "Verbs", "Adjectives", "Adverbs"]
        for pos in self.pos_filter:
            if pos not in valid_pos:
                errors.append(f"Invalid POS filter: {pos}")
        
        return errors


@dataclass
class VisualizationSettings:
    """Settings for graph visualization."""
    layout_type: str = "Force-directed (default)"
    node_size_multiplier: float = 1.0
    enable_physics: bool = True
    spring_strength: float = 0.04
    central_gravity: float = 0.3
    show_labels: bool = True
    edge_width: int = 2
    color_scheme: str = "Default"
    show_info: bool = False
    show_graph: bool = True
    
    def validate(self) -> List[str]:
        """Validate visualization settings."""
        errors = []
        
        valid_layouts = ["Force-directed (default)", "Hierarchical", "Circular", "Grid"]
        if self.layout_type not in valid_layouts:
            errors.append(f"Invalid layout type: {self.layout_type}")
        
        if self.node_size_multiplier < 0.1 or self.node_size_multiplier > 5.0:
            errors.append(f"Node size multiplier must be between 0.1 and 5.0")
        
        if self.spring_strength < 0.001 or self.spring_strength > 1.0:
            errors.append(f"Spring strength must be between 0.001 and 1.0")
        
        if self.central_gravity < 0.0 or self.central_gravity > 1.0:
            errors.append(f"Central gravity must be between 0.0 and 1.0")
        
        if self.edge_width < 1 or self.edge_width > 10:
            errors.append(f"Edge width must be between 1 and 10")
        
        valid_schemes = ["Default", "Pastel", "Vibrant", "Monochrome"]
        if self.color_scheme not in valid_schemes:
            errors.append(f"Invalid color scheme: {self.color_scheme}")
        
        return errors


@dataclass 
class AppSettings:
    """Complete application settings combining all sub-settings."""
    exploration: ExplorationSettings = field(default_factory=ExplorationSettings)
    visualization: VisualizationSettings = field(default_factory=VisualizationSettings)
    relationships: RelationshipSettings = field(default_factory=RelationshipSettings)
    
    def validate(self) -> List[str]:
        """Validate all settings."""
        errors = []
        errors.extend(self.exploration.validate())
        errors.extend(self.visualization.validate())
        return errors
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AppSettings':
        """Create AppSettings from dictionary (for backward compatibility)."""
        # Extract sub-settings
        exploration_data = {}
        visualization_data = {}
        relationship_data = {}
        
        # Map old keys to new structure
        key_mapping = {
            # Exploration settings
            'depth': ('exploration', 'depth'),
            'max_nodes': ('exploration', 'max_nodes'),
            'max_branches': ('exploration', 'max_branches'),
            'min_frequency': ('exploration', 'min_frequency'),
            'pos_filter': ('exploration', 'pos_filter'),
            'enable_clustering': ('exploration', 'enable_clustering'),
            'enable_cross_connections': ('exploration', 'enable_cross_connections'),
            'simplified_mode': ('exploration', 'simplified_mode'),
            'word': ('exploration', 'word'),
            'sense_number': ('exploration', 'sense_number'),
            'parsed_sense_number': ('exploration', 'sense_number'),
            'synset_search_mode': ('exploration', 'synset_search_mode'),
            
            # Visualization settings
            'layout_type': ('visualization', 'layout_type'),
            'node_size_multiplier': ('visualization', 'node_size_multiplier'),
            'enable_physics': ('visualization', 'enable_physics'),
            'spring_strength': ('visualization', 'spring_strength'),
            'central_gravity': ('visualization', 'central_gravity'),
            'show_labels': ('visualization', 'show_labels'),
            'edge_width': ('visualization', 'edge_width'),
            'color_scheme': ('visualization', 'color_scheme'),
            'show_info': ('visualization', 'show_info'),
            'show_graph': ('visualization', 'show_graph'),
        }
        
        # Process relationship settings (all show_* keys)
        for key, value in data.items():
            if key.startswith('show_') and key not in ['show_info', 'show_graph', 'show_labels']:
                relationship_data[key] = value
            elif key in key_mapping:
                category, attr = key_mapping[key]
                if category == 'exploration':
                    exploration_data[attr] = value
                elif category == 'visualization':
                    visualization_data[attr] = value
        
        # Create sub-objects
        exploration = ExplorationSettings(**exploration_data)
        visualization = VisualizationSettings(**visualization_data)
        relationships = RelationshipSettings(**relationship_data)
        
        return cls(
            exploration=exploration,
            visualization=visualization,
            relationships=relationships
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary (for backward compatibility)."""
        result = {}
        
        # Add exploration settings
        for key, value in vars(self.exploration).items():
            result[key] = value
        
        # Add visualization settings
        for key, value in vars(self.visualization).items():
            result[key] = value
        
        # Add relationship settings
        for key, value in vars(self.relationships).items():
            result[key] = value
        
        return result 