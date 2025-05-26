#!/usr/bin/env python3
"""
Test script to verify that all synsets have root word connections
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wordnet_explorer import build_wordnet_graph, get_synsets_for_word

def test_root_connections():
    """Test that all synsets have connections to root words."""
    word = "sheep"
    
    print(f"Testing root connections for word: '{word}'")
    
    # Build graph
    print("Building graph with all senses...")
    G, node_labels = build_wordnet_graph(word, depth=1)
    
    print(f"\nGraph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Analyze node types
    main_nodes = []
    synset_nodes = []
    
    for node in G.nodes():
        node_data = G.nodes[node]
        node_type = node_data.get('node_type', 'unknown')
        
        if node_type == 'main':
            main_nodes.append(node)
        elif node_type == 'synset':
            synset_nodes.append(node)
    
    print(f"\nNode breakdown:")
    print(f"  Root words (main): {len(main_nodes)}")
    print(f"  Word senses (synset): {len(synset_nodes)}")
    
    print(f"\nRoot words found:")
    for main_node in main_nodes:
        print(f"  - {node_labels.get(main_node, main_node)}")
    
    # Check that every synset has a root connection
    print(f"\nChecking root connections for synsets:")
    synsets_with_roots = 0
    synsets_without_roots = 0
    
    for synset_node in synset_nodes:
        # Find connections to root nodes
        root_connections = []
        for neighbor in G.neighbors(synset_node):
            if G.nodes[neighbor].get('node_type') == 'main':
                edge_data = G.get_edge_data(neighbor, synset_node)
                if edge_data and edge_data.get('relation') == 'sense':
                    root_connections.append(neighbor)
        
        if root_connections:
            synsets_with_roots += 1
            root_word = node_labels.get(root_connections[0], root_connections[0])
            synset_label = node_labels.get(synset_node, synset_node)
            print(f"  ✓ {synset_label} ← {root_word}")
        else:
            synsets_without_roots += 1
            synset_label = node_labels.get(synset_node, synset_node)
            print(f"  ✗ {synset_label} (NO ROOT CONNECTION)")
    
    print(f"\nSummary:")
    print(f"  Synsets with root connections: {synsets_with_roots}")
    print(f"  Synsets without root connections: {synsets_without_roots}")
    
    if synsets_without_roots == 0:
        print("  🎉 SUCCESS: All synsets have root connections!")
    else:
        print("  ⚠️  WARNING: Some synsets are missing root connections")
    
    # Show some example edges
    print(f"\nExample edges:")
    edge_count = 0
    for edge in G.edges(data=True):
        if edge_count >= 10:  # Limit output
            break
        source, target, edge_data = edge
        relation = edge_data.get('relation', 'unknown')
        color = edge_data.get('color', 'unknown')
        source_label = node_labels.get(source, source)
        target_label = node_labels.get(target, target)
        print(f"  {source_label} --[{relation}]--> {target_label} (color: {color})")
        edge_count += 1

if __name__ == "__main__":
    test_root_connections() 