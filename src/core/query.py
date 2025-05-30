"""
Query class for WordNet Explorer.
Encapsulates all search parameters and provides clean methods for parameter handling.
"""

from dataclasses import dataclass, asdict, field, fields
from typing import Dict, Any, Optional, List
from datetime import datetime
import copy


@dataclass
class Query:
    """Represents a complete WordNet search query with all parameters."""
    
    # Core search parameters
    word: str = ""
    sense_number: Optional[int] = None
    synset_search_mode: bool = False
    
    # Graph parameters
    depth: int = 1
    max_nodes: int = 100
    max_branches: int = 5
    min_frequency: int = 0
    pos_filter: List[str] = field(default_factory=lambda: ["Nouns", "Verbs", "Adjectives", "Adverbs"])
    
    # Relationship parameters
    show_hypernyms: bool = False
    show_hyponyms: bool = False
    show_meronyms: bool = False
    show_holonyms: bool = False
    show_hypernym: bool = False
    show_hyponym: bool = False
    show_member_meronym: bool = False
    show_part_meronym: bool = False
    show_member_holonym: bool = False
    show_part_holonym: bool = False
    show_antonym: bool = False
    show_similar_to: bool = False
    show_entailment: bool = False
    show_cause: bool = False
    show_attribute: bool = False
    show_also_see: bool = False
    show_instance_hypernym: bool = False
    show_instance_hyponym: bool = False
    show_substance_holonym: bool = False
    show_substance_meronym: bool = False
    show_verb_group: bool = False
    show_participle_of_verb: bool = False
    show_derivationally_related_form: bool = False
    show_pertainym: bool = False
    show_derived_from: bool = False
    show_domain_of_synset_topic: bool = False
    show_member_of_domain_topic: bool = False
    show_domain_of_synset_region: bool = False
    show_member_of_domain_region: bool = False
    show_domain_of_synset_usage: bool = False
    show_member_of_domain_usage: bool = False
    
    # Advanced parameters
    enable_clustering: bool = False
    enable_cross_connections: bool = True
    simplified_mode: bool = False
    
    # Visual parameters
    layout_type: str = "Force-directed (default)"
    node_size_multiplier: float = 1.0
    color_scheme: str = "Default"
    enable_physics: bool = True
    spring_strength: float = 0.04
    central_gravity: float = 0.3
    show_labels: bool = True
    edge_width: int = 2
    show_info: bool = False
    show_graph: bool = True
    
    # Metadata
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Query':
        """Create a Query from a dictionary, handling missing keys gracefully."""
        # Get all field names from the dataclass
        field_names = set(field.name for field in fields(cls))
        
        # Filter the data to only include valid fields
        filtered_data = {k: v for k, v in data.items() if k in field_names}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_url_params(cls, session_manager) -> 'Query':
        """Create a Query from URL parameters."""
        url_settings = session_manager.get_settings_from_url()
        return cls.from_dict(url_settings)
    
    @classmethod
    def from_sidebar_settings(cls, settings: Dict[str, Any]) -> 'Query':
        """Create a Query from sidebar settings."""
        return cls.from_dict(settings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_url_params(self) -> Dict[str, str]:
        """Convert to URL parameters format."""
        # Define mapping from internal names to URL parameter names
        url_mappings = {
            'word': 'word',
            'depth': 'depth',
            'sense_number': 'sense',
            'show_hypernyms': 'hypernyms',
            'show_hyponyms': 'hyponyms',
            'show_meronyms': 'meronyms',
            'show_holonyms': 'holonyms',
            'layout_type': 'layout',
            'node_size_multiplier': 'node_size',
            'color_scheme': 'color',
            'enable_physics': 'physics',
            'spring_strength': 'spring',
            'central_gravity': 'gravity',
            'show_labels': 'labels',
            'edge_width': 'edge_width',
            'show_info': 'show_info',
            'show_graph': 'show_graph',
        }
        
        url_params = {}
        data = self.to_dict()
        
        for internal_key, url_key in url_mappings.items():
            if internal_key in data and data[internal_key] is not None:
                value = data[internal_key]
                # Convert boolean values to lowercase strings
                if isinstance(value, bool):
                    url_params[url_key] = str(value).lower()
                else:
                    url_params[url_key] = str(value)
        
        return url_params
    
    def copy(self) -> 'Query':
        """Create a deep copy of this query."""
        return copy.deepcopy(self)
    
    def update(self, **kwargs) -> 'Query':
        """Create a new Query with updated parameters."""
        new_query = self.copy()
        for key, value in kwargs.items():
            if hasattr(new_query, key):
                setattr(new_query, key, value)
        return new_query
    
    def get_display_name(self) -> str:
        """Get display name for this query (word or word.sense)."""
        if self.sense_number:
            return f"{self.word}.{self.sense_number}"
        return self.word
    
    def is_equivalent_to(self, other: 'Query') -> bool:
        """Check if this query is equivalent to another (same word and sense)."""
        return (self.word == other.word and 
                self.sense_number == other.sense_number)
    
    def __str__(self) -> str:
        """String representation."""
        return f"Query(word='{self.word}', sense={self.sense_number}, depth={self.depth})" 