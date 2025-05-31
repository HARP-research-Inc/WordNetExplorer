"""
WordNet Explorer - Compatibility Layer

This module provides backward compatibility for existing code while
using the new modular architecture under the hood.
"""

from core import WordNetExplorer as _WordNetExplorer
from wordnet import download_nltk_data, get_synsets_for_word
from wordnet.relationships import RelationshipConfig

# Create a global instance for backward compatibility
_explorer = _WordNetExplorer()


def build_wordnet_graph(word: str, depth: int = 1, 
                        include_hypernyms: bool = True,
                        include_hyponyms: bool = True,
                        include_meronyms: bool = True,
                        include_holonyms: bool = True,
                        sense_number: int = None):
    """
    Build a NetworkX graph of WordNet connections for a given word.
    
    This is a compatibility function that uses the new modular architecture.
    """
    return _explorer.explore_word(
        word=word,
        depth=depth,
        sense_number=sense_number,
        include_hypernyms=include_hypernyms,
        include_hyponyms=include_hyponyms,
        include_meronyms=include_meronyms,
        include_holonyms=include_holonyms
    )


def visualize_graph(G, node_labels, word, save_path=None, **kwargs):
    """
    Create an interactive visualization of the WordNet graph.
    
    This is a compatibility function that uses the new modular architecture.
    """
    return _explorer.visualize_graph(G, node_labels, word, save_path, **kwargs)


def visualize_graph_static(G, node_labels, word, save_path=None):
    """
    Create a static visualization of the WordNet graph.
    
    This is a compatibility function that uses the new modular architecture.
    """
    return _explorer.visualize_static(G, node_labels, word, save_path)


def print_word_info(word: str):
    """
    Print comprehensive information about a word.
    
    This is a compatibility function that uses the new modular architecture.
    """
    info = _explorer.get_word_info(word)
    
    if not info['found']:
        print(f"No WordNet entries found for '{word}'")
        return
    
    print(f"\nWord: {info['word']}")
    print(f"Total senses: {info['total_senses']}")
    print("-" * 50)
    
    for synset_info in info['synsets']:
        print(f"\nSense {synset_info['sense_number']}: {synset_info['synset_name']}")
        print(f"Part of speech: {synset_info['pos']}")
        print(f"Definition: {synset_info['definition']}")
        print(f"Lemmas: {', '.join(synset_info['lemma_names'])}")
        
        if synset_info['examples']:
            print(f"Examples: {'; '.join(synset_info['examples'])}")


def build_focused_wordnet_graph(center_word: str, previous_word: str = None, 
                                previous_relation: str = None, **kwargs):
    """
    Build a focused graph with breadcrumb navigation.
    
    This is a compatibility function that uses the new modular architecture.
    """
    return _explorer.build_focused_graph(
        center_word=center_word,
        previous_word=previous_word,
        previous_relation=previous_relation,
        **kwargs
    )


# Export the main functions for backward compatibility
__all__ = [
    'download_nltk_data',
    'get_synsets_for_word', 
    'build_wordnet_graph',
    'visualize_graph',
    'visualize_graph_static',
    'print_word_info',
    'build_focused_wordnet_graph'
] 