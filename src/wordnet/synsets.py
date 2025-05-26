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
    info = get_synset_info(synset)
    primary_lemma = info['lemma_names'][0].replace('_', ' ')
    return f"{primary_lemma} ({info['pos_label']}.{info['sense_number']})" 