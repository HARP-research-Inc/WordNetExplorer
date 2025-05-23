#!/usr/bin/env python3
"""
WordNet Explorer Core Module

Core functionality for exploring WordNet semantic relationships.
Provides functions for building and visualizing word relationship graphs.
"""

import nltk
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
from collections import defaultdict
from typing import Set, Dict, List, Tuple
import tempfile
import os

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

def build_wordnet_graph(word: str, depth: int = 1, 
                        include_hypernyms: bool = True,
                        include_hyponyms: bool = True,
                        include_meronyms: bool = True,
                        include_holonyms: bool = True) -> Tuple[nx.Graph, Dict]:
    """
    Build a NetworkX graph of WordNet connections for a given word.
    
    Args:
        word: The input word to explore
        depth: How many levels deep to explore relationships
        include_hypernyms: Whether to include hypernym relationships
        include_hyponyms: Whether to include hyponym relationships
        include_meronyms: Whether to include meronym relationships
        include_holonyms: Whether to include holonym relationships
        
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
        
        # Add hypernyms (more general concepts) - only if enabled
        if include_hypernyms:
            for hypernym in synset.hypernyms():
                hyper_node = f"{hypernym.name()}_hyper"
                G.add_node(hyper_node)
                node_labels[hyper_node] = f"↑ {hypernym.lemma_names()[0].replace('_', ' ')}"
                G.add_edge(synset_node, hyper_node)
                G.nodes[hyper_node]['definition'] = hypernym.definition()
                G.nodes[hyper_node]['relation_type'] = 'hypernym'
                
                if current_depth < depth:
                    add_synset_connections(hypernym, current_depth + 1, hyper_node)
        
        # Add hyponyms (more specific concepts) - only if enabled
        if include_hyponyms:
            for hyponym in synset.hyponyms():
                hypo_node = f"{hyponym.name()}_hypo"
                G.add_node(hypo_node)
                node_labels[hypo_node] = f"↓ {hyponym.lemma_names()[0].replace('_', ' ')}"
                G.add_edge(synset_node, hypo_node)
                G.nodes[hypo_node]['definition'] = hyponym.definition()
                G.nodes[hypo_node]['relation_type'] = 'hyponym'
                
                if current_depth < depth:
                    add_synset_connections(hyponym, current_depth + 1, hypo_node)
        
        # Add meronyms (part-of relationships) - only if enabled
        if include_meronyms:
            for meronym in synset.part_meronyms():
                mero_node = f"{meronym.name()}_mero"
                G.add_node(mero_node)
                node_labels[mero_node] = f"⊂ {meronym.lemma_names()[0].replace('_', ' ')}"
                G.add_edge(synset_node, mero_node)
                G.nodes[mero_node]['definition'] = meronym.definition()
                G.nodes[mero_node]['relation_type'] = 'meronym'
        
        # Add holonyms (whole-of relationships) - only if enabled
        if include_holonyms:
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

def visualize_graph(G: nx.Graph, node_labels: Dict, word: str, save_path: str = None,
                   layout_type: str = "Force-directed (default)",
                   node_size_multiplier: float = 1.0,
                   enable_physics: bool = True,
                   spring_strength: float = 0.04,
                   central_gravity: float = 0.3,
                   show_labels: bool = True,
                   show_arrows: bool = False,
                   edge_width: int = 2,
                   color_scheme: str = "Default"):
    """Create an interactive visualization of the WordNet graph using pyvis."""
    if G.number_of_nodes() == 0:
        print("No graph to display - no WordNet connections found.")
        return None
    
    # Create a pyvis network
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        directed=show_arrows
    )
    
    # Configure physics based on settings
    if enable_physics:
        physics_options = f"""
        var options = {{
          "physics": {{
            "enabled": true,
            "stabilization": {{"iterations": 100}},
            "barnesHut": {{
              "gravitationalConstant": -8000,
              "centralGravity": {central_gravity},
              "springLength": 95,
              "springConstant": {spring_strength},
              "damping": 0.09
            }}
          }}
        }}
        """
    else:
        physics_options = """
        var options = {
          "physics": {"enabled": false}
        }
        """
    
    net.set_options(physics_options)
    
    # Define color schemes
    color_schemes = {
        "Default": {
            "main": "#FF6B6B", "synset": "#DDA0DD", "hyper": "#4ECDC4",
            "hypo": "#45B7D1", "mero": "#96CEB4", "holo": "#FFEAA7"
        },
        "Pastel": {
            "main": "#FFB3BA", "synset": "#BFBFFF", "hyper": "#BAFFCA",
            "hypo": "#B3E5FF", "mero": "#C7FFB3", "holo": "#FFFFB3"
        },
        "Vibrant": {
            "main": "#FF0000", "synset": "#9932CC", "hyper": "#00CED1",
            "hypo": "#1E90FF", "mero": "#32CD32", "holo": "#FFD700"
        },
        "Monochrome": {
            "main": "#2C2C2C", "synset": "#5A5A5A", "hyper": "#777777",
            "hypo": "#949494", "mero": "#B1B1B1", "holo": "#CECECE"
        }
    }
    
    colors = color_schemes.get(color_scheme, color_schemes["Default"])
    
    # Add nodes with custom colors and properties
    for node in G.nodes():
        # Check if it's a breadcrumb node
        if G.nodes[node].get('node_type') == 'breadcrumb':
            color = '#CCCCCC'  # Light grey for breadcrumb
            size = int(20 * node_size_multiplier)
            title = f"Back to: {G.nodes[node].get('original_word', 'Previous word')}"
            # Special styling for breadcrumb
            node_style = {
                'borderWidth': 3,
                'borderWidthSelected': 4,
                'borderDashes': [5, 5],  # Dotted border
                'chosen': True
            }
        else:
            node_style = {}
            # Determine node color and size based on type
            if '_main' in node:
                color = colors["main"]
                size = int(25 * node_size_multiplier)
                title = f"Main word: {word.upper()}"
            elif '_hyper' in node:
                color = colors["hyper"]
                size = int(20 * node_size_multiplier)
                title = f"Hypernym: {node_labels.get(node, node)}\nDefinition: {G.nodes[node].get('definition', 'No definition')}"
            elif '_hypo' in node:
                color = colors["hypo"]
                size = int(20 * node_size_multiplier)
                title = f"Hyponym: {node_labels.get(node, node)}\nDefinition: {G.nodes[node].get('definition', 'No definition')}"
            elif '_mero' in node:
                color = colors["mero"]
                size = int(18 * node_size_multiplier)
                title = f"Meronym (part-of): {node_labels.get(node, node)}\nDefinition: {G.nodes[node].get('definition', 'No definition')}"
            elif '_holo' in node:
                color = colors["holo"]
                size = int(18 * node_size_multiplier)
                title = f"Holonym (whole-of): {node_labels.get(node, node)}\nDefinition: {G.nodes[node].get('definition', 'No definition')}"
            else:
                color = colors["synset"]
                size = int(22 * node_size_multiplier)
                title = f"Word sense: {node_labels.get(node, node)}\nDefinition: {G.nodes[node].get('definition', 'No definition')}"
        
        # Add the node
        label = node_labels.get(node, node) if show_labels else ""
        
        # Create node configuration
        node_config = {
            'label': label,
            'color': color,
            'size': size,
            'title': title,
            'font': {'size': int(12 * node_size_multiplier), 'color': 'black'}
        }
        
        # Add special styling for breadcrumb nodes
        if node_style:
            node_config.update(node_style)
        
        # Add the node with ID as first argument
        net.add_node(node, **node_config)
    
    # Add edges
    edge_color = '#888888' if color_scheme != "Monochrome" else '#333333'
    for edge in G.edges():
        net.add_edge(edge[0], edge[1], color=edge_color, width=edge_width)
    
    # Add JavaScript for double-click navigation (for Streamlit)
    if not save_path:  # Only for Streamlit display
        navigation_js = """
        <script type="text/javascript">
        window.addEventListener('load', function() {
            // Wait for the network to be created
            setTimeout(function() {
                if (window.network) {
                    window.network.on("doubleClick", function (params) {
                        if (params.nodes.length > 0) {
                            const nodeId = params.nodes[0];
                            console.log('Double-clicked node:', nodeId);
                            
                            // Extract the word/synset name from the node ID
                            let targetWord = nodeId;
                            
                            // Handle different node types
                            if (nodeId.includes('_main')) {
                                targetWord = nodeId.replace('_main', '');
                            } else if (nodeId.includes('_breadcrumb')) {
                                targetWord = nodeId.replace('_breadcrumb', '');
                            } else if (nodeId.includes('.')) {
                                // It's a synset - extract the lemma
                                targetWord = nodeId.split('.')[0];
                            } else if (nodeId.includes('_')) {
                                // Remove relationship suffixes
                                targetWord = nodeId.replace(/_hyper$|_hypo$|_mero$|_holo$/g, '');
                                if (targetWord.includes('.')) {
                                    targetWord = targetWord.split('.')[0];
                                }
                            }
                            
                            // Navigate by setting URL parameter
                            const url = new URL(window.location);
                            url.searchParams.set('navigate_to', targetWord);
                            url.searchParams.set('clicked_node', nodeId);
                            window.location.href = url.toString();
                        }
                    });
                    
                    console.log('Double-click navigation enabled');
                } else {
                    console.log('Network not found, retrying...');
                    // Retry after a longer delay
                    setTimeout(arguments.callee, 1000);
                }
            }, 500);
        });
        </script>
        """
        
        # Save to file and inject JavaScript
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        net.save_graph(temp_file.name)
        
        # Read the HTML and inject our JavaScript
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject our navigation JavaScript before closing body tag
        html_content = html_content.replace('</body>', navigation_js + '</body>')
        
        # Write back the modified HTML
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return temp_file.name

    # Save to file for CLI usage
    if save_path.endswith('.png'):
        save_path = save_path.replace('.png', '.html')
    net.save_graph(save_path)
    print(f"Interactive graph saved to: {save_path}")
    return save_path

def visualize_graph_static(G: nx.Graph, node_labels: Dict, word: str, save_path: str = None):
    """Create a static matplotlib visualization (fallback option)."""
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

def build_focused_wordnet_graph(center_word: str, previous_word: str = None, 
                                previous_relation: str = None, depth: int = 1,
                                include_hypernyms: bool = True,
                                include_hyponyms: bool = True,
                                include_meronyms: bool = True,
                                include_holonyms: bool = True) -> Tuple[nx.Graph, Dict]:
    """
    Build a focused WordNet graph centered on a specific word, with breadcrumb navigation.
    
    Args:
        center_word: The word to center the graph on
        previous_word: The word we navigated from (for breadcrumb)
        previous_relation: The relationship type we followed
        depth: How many levels deep to explore relationships
        include_hypernyms: Whether to include hypernym relationships
        include_hyponyms: Whether to include hyponym relationships
        include_meronyms: Whether to include meronym relationships
        include_holonyms: Whether to include holonym relationships
        
    Returns:
        Tuple of (graph, node_labels)
    """
    from nltk.corpus import wordnet as wn
    
    G = nx.Graph()
    node_labels = {}
    visited = set()
    
    # Get the center word (could be a synset name like 'dog.n.01' or just 'dog')
    if '.' in center_word:
        # It's a specific synset
        try:
            center_synset = wn.synset(center_word)
            center_lemma = center_synset.lemma_names()[0].replace('_', ' ')
        except:
            # Fallback to regular word
            center_lemma = center_word.replace('_', ' ')
            synsets = get_synsets_for_word(center_lemma)
            if synsets:
                center_synset = synsets[0]
            else:
                return G, node_labels
    else:
        # It's a regular word
        center_lemma = center_word
        synsets = get_synsets_for_word(center_word)
        if not synsets:
            print(f"No WordNet entries found for '{center_word}'")
            return G, node_labels
        center_synset = synsets[0]
    
    # Start with the center word as main node
    main_node = f"{center_lemma}_main"
    G.add_node(main_node)
    node_labels[main_node] = center_lemma.upper()
    
    # Add breadcrumb node if we have a previous word
    if previous_word:
        breadcrumb_node = f"{previous_word}_breadcrumb"
        G.add_node(breadcrumb_node)
        node_labels[breadcrumb_node] = f"← {previous_word.upper()}"
        G.add_edge(main_node, breadcrumb_node)
        # Mark as breadcrumb for special styling
        G.nodes[breadcrumb_node]['node_type'] = 'breadcrumb'
        G.nodes[breadcrumb_node]['original_word'] = previous_word
        if previous_relation:
            G.nodes[breadcrumb_node]['relation'] = previous_relation
    
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
        G.nodes[synset_node]['synset_name'] = synset.name()
        
        # Add hypernyms (more general concepts) - only if enabled
        if include_hypernyms:
            for hypernym in synset.hypernyms():
                hyper_node = f"{hypernym.name()}_hyper"
                G.add_node(hyper_node)
                node_labels[hyper_node] = f"↑ {hypernym.lemma_names()[0].replace('_', ' ')}"
                G.add_edge(synset_node, hyper_node)
                G.nodes[hyper_node]['definition'] = hypernym.definition()
                G.nodes[hyper_node]['relation_type'] = 'hypernym'
                G.nodes[hyper_node]['synset_name'] = hypernym.name()
                
                if current_depth < depth:
                    add_synset_connections(hypernym, current_depth + 1, hyper_node)
        
        # Add hyponyms (more specific concepts) - only if enabled
        if include_hyponyms:
            for hyponym in synset.hyponyms():
                hypo_node = f"{hyponym.name()}_hypo"
                G.add_node(hypo_node)
                node_labels[hypo_node] = f"↓ {hyponym.lemma_names()[0].replace('_', ' ')}"
                G.add_edge(synset_node, hypo_node)
                G.nodes[hypo_node]['definition'] = hyponym.definition()
                G.nodes[hypo_node]['relation_type'] = 'hyponym'
                G.nodes[hypo_node]['synset_name'] = hyponym.name()
                
                if current_depth < depth:
                    add_synset_connections(hyponym, current_depth + 1, hypo_node)
        
        # Add meronyms (part-of relationships) - only if enabled
        if include_meronyms:
            for meronym in synset.part_meronyms():
                mero_node = f"{meronym.name()}_mero"
                G.add_node(mero_node)
                node_labels[mero_node] = f"⊂ {meronym.lemma_names()[0].replace('_', ' ')}"
                G.add_edge(synset_node, mero_node)
                G.nodes[mero_node]['definition'] = meronym.definition()
                G.nodes[mero_node]['relation_type'] = 'meronym'
                G.nodes[mero_node]['synset_name'] = meronym.name()
        
        # Add holonyms (whole-of relationships) - only if enabled
        if include_holonyms:
            for holonym in synset.part_holonyms():
                holo_node = f"{holonym.name()}_holo"
                G.add_node(holo_node)
                node_labels[holo_node] = f"⊃ {holonym.lemma_names()[0].replace('_', ' ')}"
                G.add_edge(synset_node, holo_node)
                G.nodes[holo_node]['definition'] = holonym.definition()
                G.nodes[holo_node]['relation_type'] = 'holonym'
                G.nodes[holo_node]['synset_name'] = holonym.name()
    
    # Process the center synset
    synset_node = f"{center_synset.name()}"
    G.add_edge(main_node, synset_node)
    add_synset_connections(center_synset, 0, main_node)
    
    return G, node_labels 