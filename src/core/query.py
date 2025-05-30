"""
Query class for WordNet Explorer.
Encapsulates all search parameters and provides clean methods for parameter handling.
"""

from dataclasses import dataclass, asdict, field, fields
from typing import Dict, Any, Optional, List
from datetime import datetime
import copy
import hashlib


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
        url_params = {}
        data = self.to_dict()
        
        # Core parameters
        if data.get('word'):
            url_params['word'] = data['word']
        if data.get('sense_number'):
            url_params['sense'] = str(data['sense_number'])
        if data.get('synset_search_mode'):
            url_params['synset_search_mode'] = str(data['synset_search_mode']).lower()
        
        # Graph parameters
        if data.get('depth', 1) != 1:
            url_params['depth'] = str(data['depth'])
        if data.get('max_nodes', 100) != 100:
            url_params['max_nodes'] = str(data['max_nodes'])
        if data.get('max_branches', 5) != 5:
            url_params['max_branches'] = str(data['max_branches'])
        if data.get('min_frequency', 0) != 0:
            url_params['min_frequency'] = str(data['min_frequency'])
        
        # Relationship parameters (only include if True)
        relationship_mappings = {
            'show_hypernyms': 'hypernyms',
            'show_hyponyms': 'hyponyms', 
            'show_meronyms': 'meronyms',
            'show_holonyms': 'holonyms',
            'show_hypernym': 'hypernym',
            'show_hyponym': 'hyponym',
            'show_member_meronym': 'member_meronym',
            'show_part_meronym': 'part_meronym',
            'show_member_holonym': 'member_holonym',
            'show_part_holonym': 'part_holonym',
            'show_antonym': 'antonym',
            'show_similar_to': 'similar_to',
            'show_entailment': 'entailment',
            'show_cause': 'cause',
            'show_attribute': 'attribute',
            'show_also_see': 'also_see'
        }
        
        for internal_key, url_key in relationship_mappings.items():
            if data.get(internal_key):
                url_params[url_key] = 'true'
        
        # Visual parameters
        if data.get('layout_type') and data['layout_type'] != 'Force-directed (default)':
            url_params['layout'] = data['layout_type']
        if data.get('node_size_multiplier', 1.0) != 1.0:
            url_params['node_size'] = str(data['node_size_multiplier'])
        if data.get('color_scheme') and data['color_scheme'] != 'Default':
            url_params['color'] = data['color_scheme']
        if data.get('enable_physics') is not None and data['enable_physics'] != True:
            url_params['physics'] = str(data['enable_physics']).lower()
        if data.get('spring_strength', 0.04) != 0.04:
            url_params['spring'] = str(data['spring_strength'])
        if data.get('central_gravity', 0.3) != 0.3:
            url_params['gravity'] = str(data['central_gravity'])
        if data.get('show_labels') is not None and data['show_labels'] != True:
            url_params['labels'] = str(data['show_labels']).lower()
        if data.get('edge_width', 2) != 2:
            url_params['edge_width'] = str(data['edge_width'])
        if data.get('show_info'):
            url_params['show_info'] = str(data['show_info']).lower()
        if data.get('show_graph') is not None and data['show_graph'] != True:
            url_params['show_graph'] = str(data['show_graph']).lower()
        
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
    
    def generate_settings_hash(self) -> str:
        """Generate a short hash based on the important settings."""
        # Get all settings except word, sense_number, timestamp
        settings_data = self.to_dict()
        
        # Remove word-specific and timestamp data for hash generation
        hash_data = {k: v for k, v in settings_data.items() 
                    if k not in ['word', 'sense_number', 'timestamp', 'synset_search_mode']}
        
        # Convert to string and hash
        settings_str = str(sorted(hash_data.items()))
        hash_digest = hashlib.md5(settings_str.encode()).hexdigest()
        
        # Return first 6 characters for readability
        return hash_digest[:6]
    
    def get_settings_summary(self) -> str:
        """Generate a human-readable summary of key settings."""
        summary_parts = []
        
        # Add depth if not default
        if self.depth != 1:
            summary_parts.append(f"d{self.depth}")
        
        # Add active relationships
        active_relationships = []
        if self.show_hypernym or self.show_hypernyms:
            active_relationships.append("hyper")
        if self.show_hyponym or self.show_hyponyms:
            active_relationships.append("hypo")
        if any([self.show_member_meronym, self.show_part_meronym, self.show_meronyms]):
            active_relationships.append("mero")
        if any([self.show_member_holonym, self.show_part_holonym, self.show_holonyms]):
            active_relationships.append("holo")
        if self.show_antonym:
            active_relationships.append("ant")
        if self.show_similar_to:
            active_relationships.append("sim")
        
        if active_relationships:
            summary_parts.append("+".join(active_relationships))
        
        # Add max_nodes if not default
        if self.max_nodes != 100:
            summary_parts.append(f"n{self.max_nodes}")
        
        # Add layout if not default
        if self.layout_type != "Force-directed (default)":
            layout_short = self.layout_type.replace(" ", "").replace("-", "")[:4].lower()
            summary_parts.append(f"lay:{layout_short}")
        
        return "-".join(summary_parts) if summary_parts else "default"

    def get_display_name(self) -> str:
        """Get enhanced display name for this query with settings identifier."""
        base_name = self.word
        if self.sense_number:
            base_name += f".{self.sense_number}"
        
        # Add settings summary
        settings_summary = self.get_settings_summary()
        settings_hash = self.generate_settings_hash()
        
        if settings_summary != "default":
            return f"{base_name} [{settings_summary}#{settings_hash}]"
        else:
            return f"{base_name} [#{settings_hash}]"
    
    def is_equivalent_to(self, other: 'Query') -> bool:
        """Check if this query is equivalent to another (same word and sense)."""
        return (self.word == other.word and 
                self.sense_number == other.sense_number)
    
    def construct_url(self, base_url: str = "") -> str:
        """Construct a complete URL with all query parameters."""
        url_params = self.to_url_params()
        
        if not url_params:
            return base_url
        
        # Convert parameters to URL query string
        param_string = "&".join([f"{key}={value}" for key, value in url_params.items()])
        
        # Construct full URL
        if base_url:
            separator = "&" if "?" in base_url else "?"
            full_url = f"{base_url}{separator}{param_string}"
        else:
            full_url = f"?{param_string}"
        
        return full_url
    
    def log_constructed_url(self, base_url: str = "") -> str:
        """Construct URL and log it to console for debugging."""
        url = self.construct_url(base_url)
        print(f"🔗 CONSTRUCTED URL: {url}")
        print(f"🔗 URL PARAMS: {self.to_url_params()}")
        return url
    
    def __str__(self) -> str:
        """String representation."""
        return f"Query(word='{self.word}', sense={self.sense_number}, depth={self.depth})" 