"""
WordNet Module

This module contains all WordNet-specific functionality including
synset operations, relationship extraction, and data access.
"""

from .synsets import get_synsets_for_word, get_synset_info
from .relationships import get_relationships, RelationshipType
from .data_access import download_nltk_data

__all__ = [
    'get_synsets_for_word',
    'get_synset_info', 
    'get_relationships',
    'RelationshipType',
    'download_nltk_data'
] 