"""Domain entities for WordNet Explorer."""

from .word import Word
from .synset import Synset
from .graph import Graph
from .relationship import Relationship, RelationshipType

__all__ = [
    'Word',
    'Synset', 
    'Graph',
    'Relationship',
    'RelationshipType'
] 