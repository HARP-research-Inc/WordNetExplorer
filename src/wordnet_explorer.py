#!/usr/bin/env python3
"""
WordNet Explorer Core Module

Core functionality for exploring WordNet semantic relationships.
Provides functions for building and visualizing word relationship graphs.
"""

import nltk
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import Set, Dict, List, Tuple

def download_nltk_data():
    """Download required NLTK data if not already present."""
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading WordNet data...")
        nltk.download('wordnet')
    
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        print("Downloading additional WordNet data...")
        nltk.download('omw-1.4')

def get_synsets_for_word(word: str) -> List:
    """Get all synsets (word senses) for a given word."""
    from nltk.corpus import wordnet as wn
    return wn.synsets(word)

def build_wordnet_graph(word: str, depth: int = 1) -> Tuple[nx.Graph, Dict]:
    """
    Build a NetworkX graph of WordNet connections for a given word.
    
    Args:
        word: The input word to explore
        depth: How many levels deep to explore relationships
        
    Returns:
        Tuple of (graph, node_labels)
    """
    from nltk.corpus import wordnet as wn
    
    G = nx.Graph()
    node_labels = {}
    visited = set()
    
    synsets = get_synsets_for_word(word)
    if not synsets:
        print(f"No WordNet entries found for '{word}'")
        return G, node_labels
    
    # Start with the main word
    main_node = f"{word}_main"
    G.add_node(main_node)
    node_labels[main_node] = word.upper()
    
    def add_synset_connections(synset, current_depth, parent_node=None):
        if current_depth > depth or synset in visited:
            return
        
        visited.add(synset)
        synset_node = f"{synset.name()}"
        
        # Add synset node
        G.add_node(synset_node)
        node_labels[synset_node] = synset.lemma_names()[0].replace('_', ' ')
        
        # Connect to parent
        if parent_node:
            G.add_edge(parent_node, synset_node)
        
        # Add definition as node attribute
        G.nodes[synset_node]['definition'] = synset.definition()
        
        # Add hypernyms (more general concepts)
        for hypernym in synset.hypernyms():
            hyper_node = f"{hypernym.name()}_hyper"
            G.add_node(hyper_node)
            node_labels[hyper_node] = f"↑ {hypernym.lemma_names()[0].replace('_', ' ')}"
            G.add_edge(synset_node, hyper_node)
            G.nodes[hyper_node]['definition'] = hypernym.definition()
            G.nodes[hyper_node]['relation_type'] = 'hypernym'
            
            if current_depth < depth:
                add_synset_connections(hypernym, current_depth + 1, hyper_node)
        
        # Add hyponyms (more specific concepts)
        for hyponym in synset.hyponyms():
            hypo_node = f"{hyponym.name()}_hypo"
            G.add_node(hypo_node)
            node_labels[hypo_node] = f"↓ {hyponym.lemma_names()[0].replace('_', ' ')}"
            G.add_edge(synset_node, hypo_node)
            G.nodes[hypo_node]['definition'] = hyponym.definition()
            G.nodes[hypo_node]['relation_type'] = 'hyponym'
            
            if current_depth < depth:
                add_synset_connections(hyponym, current_depth + 1, hypo_node)
        
        # Add meronyms (part-of relationships)
        for meronym in synset.part_meronyms():
            mero_node = f"{meronym.name()}_mero"
            G.add_node(mero_node)
            node_labels[mero_node] = f"⊂ {meronym.lemma_names()[0].replace('_', ' ')}"
            G.add_edge(synset_node, mero_node)
            G.nodes[mero_node]['definition'] = meronym.definition()
            G.nodes[mero_node]['relation_type'] = 'meronym'
        
        # Add holonyms (whole-of relationships)
        for holonym in synset.part_holonyms():
            holo_node = f"{holonym.name()}_holo"
            G.add_node(holo_node)
            node_labels[holo_node] = f"⊃ {holonym.lemma_names()[0].replace('_', ' ')}"
            G.add_edge(synset_node, holo_node)
            G.nodes[holo_node]['definition'] = holonym.definition()
            G.nodes[holo_node]['relation_type'] = 'holonym'
    
    # Process each synset of the main word
    for synset in synsets:
        synset_node = f"{synset.name()}"
        G.add_edge(main_node, synset_node)
        add_synset_connections(synset, 0, main_node)
    
    return G, node_labels

def visualize_graph(G: nx.Graph, node_labels: Dict, word: str, save_path: str = None):
    """Visualize the WordNet graph using matplotlib."""
    if G.number_of_nodes() == 0:
        print("No graph to display - no WordNet connections found.")
        return
    
    plt.figure(figsize=(14, 10))
    
    # Create layout
    if G.number_of_nodes() > 50:
        pos = nx.spring_layout(G, k=2, iterations=50)
    else:
        pos = nx.spring_layout(G, k=3, iterations=100)
    
    # Define colors for different node types
    node_colors = []
    for node in G.nodes():
        if '_main' in node:
            node_colors.append('#FF6B6B')  # Red for main word
        elif '_hyper' in node:
            node_colors.append('#4ECDC4')  # Teal for hypernyms
        elif '_hypo' in node:
            node_colors.append('#45B7D1')  # Blue for hyponyms
        elif '_mero' in node:
            node_colors.append('#96CEB4')  # Green for meronyms
        elif '_holo' in node:
            node_colors.append('#FFEAA7')  # Yellow for holonyms
        else:
            node_colors.append('#DDA0DD')  # Purple for synsets
    
    # Draw the graph
    nx.draw(G, pos, 
            node_color=node_colors,
            node_size=1000,
            with_labels=False,
            edge_color='gray',
            width=1.5,
            alpha=0.8)
    
    # Add labels
    nx.draw_networkx_labels(G, pos, node_labels, font_size=8, font_weight='bold')
    
    # Add title and legend
    plt.title(f"WordNet Connections for '{word.upper()}'", fontsize=16, fontweight='bold')
    
    # Create legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', markersize=10, label='Main Word'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#DDA0DD', markersize=10, label='Word Senses'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', markersize=10, label='Hypernyms (↑)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#45B7D1', markersize=10, label='Hyponyms (↓)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#96CEB4', markersize=10, label='Part-of (⊂)'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFEAA7', markersize=10, label='Whole-of (⊃)')
    ]
    
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Graph saved to: {save_path}")
    
    plt.show()

def print_word_info(word: str):
    """Print detailed information about the word's synsets."""
    synsets = get_synsets_for_word(word)
    
    if not synsets:
        print(f"No WordNet entries found for '{word}'")
        return
    
    print(f"\n=== WordNet Information for '{word.upper()}' ===")
    print(f"Found {len(synsets)} word sense(s):\n")
    
    for i, synset in enumerate(synsets, 1):
        print(f"{i}. {synset.name()} ({synset.pos()})")
        print(f"   Definition: {synset.definition()}")
        
        if synset.examples():
            print(f"   Examples: {'; '.join(synset.examples())}")
        
        # Show lemmas (different word forms)
        lemmas = [lemma.name().replace('_', ' ') for lemma in synset.lemmas()]
        print(f"   Related words: {', '.join(lemmas)}")
        
        # Show relationships
        if synset.hypernyms():
            hypernyms = [h.lemma_names()[0].replace('_', ' ') for h in synset.hypernyms()]
            print(f"   More general: {', '.join(hypernyms)}")
        
        if synset.hyponyms():
            hyponyms = [h.lemma_names()[0].replace('_', ' ') for h in synset.hyponyms()[:3]]
            if len(synset.hyponyms()) > 3:
                hyponyms.append(f"... and {len(synset.hyponyms()) - 3} more")
            print(f"   More specific: {', '.join(hyponyms)}")
        
        print() 