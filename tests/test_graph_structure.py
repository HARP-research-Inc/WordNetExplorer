#!/usr/bin/env python3
"""
Test script to verify the graph structure has proper sense-to-root connections
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wordnet_explorer import build_wordnet_graph, get_synsets_for_word

def test_graph_structure():
    """Test that the graph has proper sense-to-root connections."""
    word = "dog"
    
    print(f"Testing graph structure for word: '{word}'")
    
    # Get synsets
    synsets = get_synsets_for_word(word)
    print(f"Found {len(synsets)} senses for '{word}':")
    for i, synset in enumerate(synsets, 1):
        print(f"  {i}. {synset.name()} - {synset.definition()}")
    
    print("\n" + "="*60)
    
    # Build graph
    print("Building graph...")
    G, node_labels = build_wordnet_graph(word, depth=1)
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Check for main node
    main_node = f"{word}_main"
    if main_node in G.nodes():
        print(f"✓ Main node '{main_node}' found")
    else:
        print(f"✗ Main node '{main_node}' NOT found")
        return
    
    # Check sense connections
    print("\nChecking sense connections:")
    sense_connections = []
    for edge in G.edges(data=True):
        source, target, edge_data = edge
        if edge_data.get('relation') == 'sense':
            sense_connections.append((source, target, edge_data))
            print(f"  ✓ Sense connection: {source} → {target}")
            if 'color' in edge_data:
                print(f"    Color: {edge_data['color']}")
            else:
                print(f"    ⚠️  No color attribute")
    
    print(f"\nFound {len(sense_connections)} sense connections")
    
    # Check that each synset is connected to the main node
    synset_nodes = [node for node in G.nodes() if '.' in node and node != main_node]
    print(f"\nFound {len(synset_nodes)} synset nodes:")
    
    connected_synsets = 0
    for synset_node in synset_nodes:
        # Check if there's a sense connection from main to this synset
        has_connection = False
        for source, target, edge_data in sense_connections:
            if source == main_node and target == synset_node:
                has_connection = True
                connected_synsets += 1
                break
        
        if has_connection:
            print(f"  ✓ {synset_node} connected to root")
        else:
            print(f"  ✗ {synset_node} NOT connected to root")
    
    print(f"\nSummary: {connected_synsets}/{len(synset_nodes)} synsets connected to root")
    
    # Check other relationship types
    relationship_counts = {}
    for edge in G.edges(data=True):
        relation = edge[2].get('relation', 'unknown')
        relationship_counts[relation] = relationship_counts.get(relation, 0) + 1
    
    print(f"\nRelationship breakdown:")
    for relation, count in relationship_counts.items():
        print(f"  {relation}: {count} edges")

if __name__ == "__main__":
    test_graph_structure() 