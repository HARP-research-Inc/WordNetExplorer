"""
WordNet Relationships Module

Handles extraction and management of semantic relationships between synsets.
"""

from enum import Enum
from typing import List, Dict, Any, Tuple


class RelationshipType(Enum):
    """Enumeration of WordNet relationship types."""
    HYPERNYM = "hypernym"
    HYPONYM = "hyponym" 
    MERONYM = "meronym"
    HOLONYM = "holonym"
    SENSE = "sense"


class RelationshipConfig:
    """Configuration for relationship extraction."""
    
    def __init__(self, 
                 include_hypernyms: bool = True,
                 include_hyponyms: bool = True,
                 include_meronyms: bool = True,
                 include_holonyms: bool = True):
        self.include_hypernyms = include_hypernyms
        self.include_hyponyms = include_hyponyms
        self.include_meronyms = include_meronyms
        self.include_holonyms = include_holonyms


def get_relationships(synset, config: RelationshipConfig) -> Dict[RelationshipType, List]:
    """Extract all configured relationships for a synset."""
    relationships = {}
    
    if config.include_hypernyms:
        relationships[RelationshipType.HYPERNYM] = synset.hypernyms()
    
    if config.include_hyponyms:
        relationships[RelationshipType.HYPONYM] = synset.hyponyms()
    
    if config.include_meronyms:
        relationships[RelationshipType.MERONYM] = synset.part_meronyms()
    
    if config.include_holonyms:
        relationships[RelationshipType.HOLONYM] = synset.part_holonyms()
    
    return relationships


def get_relationship_color(relationship_type: RelationshipType) -> str:
    """Get the color code for a relationship type."""
    color_map = {
        RelationshipType.HYPERNYM: '#FF4444',  # Red
        RelationshipType.HYPONYM: '#4488FF',   # Blue
        RelationshipType.MERONYM: '#44AA44',   # Green
        RelationshipType.HOLONYM: '#AA44AA',   # Purple
        RelationshipType.SENSE: '#666666'      # Grey
    }
    return color_map.get(relationship_type, '#000000')


def get_relationship_properties(relationship_type: RelationshipType) -> Dict[str, Any]:
    """Get display properties for a relationship type."""
    return {
        'color': get_relationship_color(relationship_type),
        'arrow_direction': 'to',
        'relation': relationship_type.value
    } 