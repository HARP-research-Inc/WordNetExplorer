"""
WordNet Synsets Module

Handles synset operations and information extraction.
"""

from typing import List, Dict, Any
from nltk.corpus import wordnet as wn


def get_synsets_for_word(word: str) -> List:
    """Get all synsets (word senses) for a given word."""
    return wn.synsets(word)


def get_synset_info(synset) -> Dict[str, Any]:
    """Extract comprehensive information from a synset."""
    pos_map = {'n': 'noun', 'v': 'verb', 'a': 'adj', 's': 'adj', 'r': 'adv'}
    
    return {
        'name': synset.name(),
        'definition': synset.definition(),
        'pos': synset.pos(),
        'pos_label': pos_map.get(synset.pos(), synset.pos()),
        'lemma_names': synset.lemma_names(),
        'sense_number': synset.name().split('.')[-1],
        'examples': synset.examples() if hasattr(synset, 'examples') else []
    }


def filter_synsets_by_sense(synsets: List, sense_number: int = None) -> List:
    """Filter synsets by sense number if specified."""
    if sense_number is not None:
        if sense_number <= len(synsets):
            return [synsets[sense_number - 1]]  # Convert to 0-based index
        else:
            return []
    return synsets


def create_synset_label(synset) -> str:
    """Create a descriptive label for a synset."""
    # Get the most frequent/common lemma (usually the first one)
    primary_lemma = synset.lemmas()[0].name().replace('_', ' ')
    synset_parts = synset.name().split('.')
    pos_part = synset_parts[1] if len(synset_parts) > 1 else 'n'
    index_part = synset_parts[2] if len(synset_parts) > 2 else '01'
    return f"{primary_lemma}\n{pos_part}.{index_part}" 