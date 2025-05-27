#!/usr/bin/env python3
"""
Simple test script to verify navigation functionality.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.core import WordNetExplorer

def test_bovine_navigation():
    """Test that bovine can be explored successfully."""
    print("🧪 Testing bovine navigation...")
    
    explorer = WordNetExplorer()
    
    try:
        # Test building graph for bovine
        G, node_labels = explorer.explore_word(
            word="bovine",
            depth=1,
            include_hypernyms=True,
            include_hyponyms=True,
            include_meronyms=True,
            include_holonyms=True
        )
        
        print(f"✅ Graph built successfully!")
        print(f"   - Nodes: {G.number_of_nodes()}")
        print(f"   - Edges: {G.number_of_edges()}")
        print(f"   - Node labels: {len(node_labels)}")
        
        # Show some node labels
        print(f"   - Sample nodes: {list(node_labels.keys())[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error building graph for bovine: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wordnet_synsets():
    """Test WordNet synsets directly."""
    print("🧪 Testing WordNet synsets...")
    
    try:
        import nltk
        from nltk.corpus import wordnet as wn
        
        synsets = wn.synsets('bovine')
        print(f"✅ Found {len(synsets)} synsets for 'bovine':")
        
        for i, synset in enumerate(synsets, 1):
            print(f"   {i}. {synset.name()}: {synset.definition()}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error accessing WordNet: {e}")
        return False

if __name__ == "__main__":
    print("🔍 WordNet Navigation Test")
    print("=" * 50)
    
    # Test WordNet access
    wordnet_ok = test_wordnet_synsets()
    print()
    
    # Test graph building
    if wordnet_ok:
        graph_ok = test_bovine_navigation()
    else:
        print("⚠️ Skipping graph test due to WordNet issues")
        graph_ok = False
    
    print()
    print("=" * 50)
    if wordnet_ok and graph_ok:
        print("✅ All tests passed! Navigation should work.")
    else:
        print("❌ Some tests failed. Check the errors above.") 