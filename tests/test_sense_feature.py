#!/usr/bin/env python3
"""
Test script for the sense number feature
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wordnet_explorer import build_wordnet_graph, get_synsets_for_word

def test_sense_feature():
    """Test the sense number filtering feature."""
    word = "bank"
    
    print(f"Testing sense feature with word: '{word}'")
    
    # Get all synsets
    synsets = get_synsets_for_word(word)
    print(f"Found {len(synsets)} senses for '{word}':")
    for i, synset in enumerate(synsets, 1):
        print(f"  {i}. {synset.name()} - {synset.definition()}")
    
    print("\n" + "="*50)
    
    # Test with all senses (default)
    print("Building graph with all senses...")
    G_all, labels_all = build_wordnet_graph(word, depth=1)
    print(f"Graph with all senses: {G_all.number_of_nodes()} nodes, {G_all.number_of_edges()} edges")
    
    # Test with specific sense
    sense_num = 1
    print(f"\nBuilding graph with sense {sense_num} only...")
    G_sense, labels_sense = build_wordnet_graph(word, depth=1, sense_number=sense_num)
    print(f"Graph with sense {sense_num}: {G_sense.number_of_nodes()} nodes, {G_sense.number_of_edges()} edges")
    
    # Test with invalid sense number
    invalid_sense = len(synsets) + 1
    print(f"\nTesting with invalid sense number {invalid_sense}...")
    G_invalid, labels_invalid = build_wordnet_graph(word, depth=1, sense_number=invalid_sense)
    print(f"Graph with invalid sense: {G_invalid.number_of_nodes()} nodes, {G_invalid.number_of_edges()} edges")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_sense_feature() 