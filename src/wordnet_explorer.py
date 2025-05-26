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
                        include_holonyms: bool = True,
                        sense_number: int = None) -> Tuple[nx.Graph, Dict]:
    """
    Build a NetworkX graph of WordNet connections for a given word.
    Uses a cleaner structure with:
    - Root word node
    - Word sense nodes (synsets)
    - Labeled edges for relationships (instead of separate nodes)
    
    Args:
        word: The input word to explore
        depth: How many levels deep to explore relationships
        include_hypernyms: Whether to include hypernym relationships
        include_hyponyms: Whether to include hyponym relationships
        include_meronyms: Whether to include meronym relationships
        include_holonyms: Whether to include holonym relationships
        sense_number: Specific sense number to display (1-based, None for all)
        
    Returns:
        Tuple of (graph, node_labels)
    """
    from nltk.corpus import wordnet as wn
    
    G = nx.Graph()
    node_labels = {}
    visited_synsets = set()
    
    synsets = get_synsets_for_word(word)
    if not synsets:
        print(f"No WordNet entries found for '{word}'")
        return G, node_labels
    
    # Filter synsets by sense number if specified
    if sense_number is not None:
        if sense_number <= len(synsets):
            synsets = [synsets[sense_number - 1]]  # Convert to 0-based index
        else:
            print(f"Sense number {sense_number} not found for '{word}' (only {len(synsets)} senses available)")
            return G, node_labels
    
    # Start with the main word node
    main_node = f"{word}_main"
    G.add_node(main_node, node_type='main', word=word)
    node_labels[main_node] = word.upper()
    
    def add_synset_connections(synset, current_depth, parent_word_node=None):
        """Add connections for a synset and its relationships."""
        if current_depth > depth or synset in visited_synsets:
            return
        
        visited_synsets.add(synset)
        
        # Create synset node
        synset_node = f"{synset.name()}"
        G.add_node(synset_node, 
                  node_type='synset',
                  synset_name=synset.name(),
                  definition=synset.definition(),
                  pos=synset.pos())
        
        # Create a more descriptive label for synsets
        pos_map = {'n': 'noun', 'v': 'verb', 'a': 'adj', 's': 'adj', 'r': 'adv'}
        pos_label = pos_map.get(synset.pos(), synset.pos())
        sense_num = synset.name().split('.')[-1]
        node_labels[synset_node] = f"{synset.lemma_names()[0].replace('_', ' ')} ({pos_label}.{sense_num})"
        
        # Connect synset to parent word node (only for root connections)
        if parent_word_node:
            G.add_edge(parent_word_node, synset_node, relation='sense')
        
        # Add relationship connections directly to other synsets (no intermediate nodes)
        if include_hypernyms:
            for hypernym in synset.hypernyms():
                # Create the target synset node directly
                hyper_synset_node = f"{hypernym.name()}"
                if hyper_synset_node not in G.nodes():
                    G.add_node(hyper_synset_node, 
                              node_type='synset',
                              synset_name=hypernym.name(),
                              definition=hypernym.definition(),
                              pos=hypernym.pos())
                    
                    # Create label for the hypernym synset
                    hyper_pos_label = pos_map.get(hypernym.pos(), hypernym.pos())
                    hyper_sense_num = hypernym.name().split('.')[-1]
                    node_labels[hyper_synset_node] = f"{hypernym.lemma_names()[0].replace('_', ' ')} ({hyper_pos_label}.{hyper_sense_num})"
                
                # Connect synsets directly with colored edge
                G.add_edge(synset_node, hyper_synset_node, 
                          relation='hypernym', 
                          color='#FF4444',  # Red for hypernyms
                          arrow_direction='to')
                
                if current_depth < depth:
                    add_synset_connections(hypernym, current_depth + 1)
        
        if include_hyponyms:
            for hyponym in synset.hyponyms():
                # Create the target synset node directly
                hypo_synset_node = f"{hyponym.name()}"
                if hypo_synset_node not in G.nodes():
                    G.add_node(hypo_synset_node, 
                              node_type='synset',
                              synset_name=hyponym.name(),
                              definition=hyponym.definition(),
                              pos=hyponym.pos())
                    
                    # Create label for the hyponym synset
                    hypo_pos_label = pos_map.get(hyponym.pos(), hyponym.pos())
                    hypo_sense_num = hyponym.name().split('.')[-1]
                    node_labels[hypo_synset_node] = f"{hyponym.lemma_names()[0].replace('_', ' ')} ({hypo_pos_label}.{hypo_sense_num})"
                
                # Connect synsets directly with colored edge
                G.add_edge(synset_node, hypo_synset_node, 
                          relation='hyponym', 
                          color='#4488FF',  # Blue for hyponyms
                          arrow_direction='to')
                
                if current_depth < depth:
                    add_synset_connections(hyponym, current_depth + 1)
        
        if include_meronyms:
            for meronym in synset.part_meronyms():
                # Create the target synset node directly
                mero_synset_node = f"{meronym.name()}"
                if mero_synset_node not in G.nodes():
                    G.add_node(mero_synset_node, 
                              node_type='synset',
                              synset_name=meronym.name(),
                              definition=meronym.definition(),
                              pos=meronym.pos())
                    
                    # Create label for the meronym synset
                    mero_pos_label = pos_map.get(meronym.pos(), meronym.pos())
                    mero_sense_num = meronym.name().split('.')[-1]
                    node_labels[mero_synset_node] = f"{meronym.lemma_names()[0].replace('_', ' ')} ({mero_pos_label}.{mero_sense_num})"
                
                # Connect synsets directly with colored edge
                G.add_edge(synset_node, mero_synset_node, 
                          relation='meronym', 
                          color='#44AA44',  # Green for meronyms
                          arrow_direction='to')
        
        if include_holonyms:
            for holonym in synset.part_holonyms():
                # Create the target synset node directly
                holo_synset_node = f"{holonym.name()}"
                if holo_synset_node not in G.nodes():
                    G.add_node(holo_synset_node, 
                              node_type='synset',
                              synset_name=holonym.name(),
                              definition=holonym.definition(),
                              pos=holonym.pos())
                    
                    # Create label for the holonym synset
                    holo_pos_label = pos_map.get(holonym.pos(), holonym.pos())
                    holo_sense_num = holonym.name().split('.')[-1]
                    node_labels[holo_synset_node] = f"{holonym.lemma_names()[0].replace('_', ' ')} ({holo_pos_label}.{holo_sense_num})"
                
                # Connect synsets directly with colored edge
                G.add_edge(synset_node, holo_synset_node, 
                          relation='holonym', 
                          color='#FFAA00',  # Orange for holonyms
                          arrow_direction='to')
    
    # Process each synset of the main word
    for synset in synsets:
        synset_node = f"{synset.name()}"
        G.add_edge(main_node, synset_node, relation='sense')
        add_synset_connections(synset, 0, main_node)
    
    return G, node_labels

def visualize_graph(G: nx.Graph, node_labels: Dict, word: str, save_path: str = None,
                   layout_type: str = "Force-directed (default)",
                   node_size_multiplier: float = 1.0,
                   enable_physics: bool = True,
                   spring_strength: float = 0.04,
                   central_gravity: float = 0.3,
                   show_labels: bool = True,
                   edge_width: int = 2,
                   color_scheme: str = "Default"):
    """Create an interactive visualization of the WordNet graph using pyvis."""
    if G.number_of_nodes() == 0:
        print("No graph to display - no WordNet connections found.")
        return None
    
    # Create a pyvis network - always directed for relationship clarity
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black",
        directed=True
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
    
    # Define color schemes - simplified for new structure (only main and synset)
    color_schemes = {
        "Default": {
            "main": "#FF6B6B", "synset": "#DDA0DD"
        },
        "Pastel": {
            "main": "#FFB3BA", "synset": "#BFBFFF"
        },
        "Vibrant": {
            "main": "#FF0000", "synset": "#9932CC"
        },
        "Monochrome": {
            "main": "#2C2C2C", "synset": "#5A5A5A"
        }
    }
    
    colors = color_schemes.get(color_scheme, color_schemes["Default"])
    
    # Add nodes with custom colors and properties
    for node in G.nodes():
        node_data = G.nodes[node]
        node_type = node_data.get('node_type', 'unknown')
        
        # Check if it's a breadcrumb node
        if node_type == 'breadcrumb':
            color = '#CCCCCC'  # Light grey for breadcrumb
            size = int(20 * node_size_multiplier)
            title = f"Back to: {node_data.get('original_word', 'Previous word')}"
            # Special styling for breadcrumb
            node_style = {
                'borderWidth': 3,
                'borderWidthSelected': 4,
                'borderDashes': [5, 5],  # Dotted border
                'chosen': True
            }
        else:
            node_style = {}
            # Determine node color and size based on node types (only main and synset)
            if node_type == 'main':
                color = colors["main"]
                size = int(30 * node_size_multiplier)
                title = f"Main word: {node_data.get('word', word).upper()}"
            elif node_type == 'synset':
                color = colors["synset"]
                size = int(25 * node_size_multiplier)
                synset_name = node_data.get('synset_name', node)
                definition = node_data.get('definition', 'No definition')
                title = f"Word sense: {node_labels.get(node, node)}\nSynset: {synset_name}\nDefinition: {definition}"
            else:
                # Fallback for any unrecognized node types
                color = colors.get("synset", "#CCCCCC")
                size = int(20 * node_size_multiplier)
                title = f"Node: {node_labels.get(node, node)}"
        
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
    
    # Add edges with colored relationships (using colors from edge data)
    for edge in G.edges(data=True):
        source, target, edge_data = edge
        relation = edge_data.get('relation', 'unknown')
        
        # Use color from edge data if available, otherwise use default colors by relationship
        if 'color' in edge_data:
            color = edge_data['color']
        else:
            # Fallback colors if not set in edge data
            edge_colors = {
                'sense': '#666666',      # Dark grey for sense connections
                'hypernym': '#FF4444',   # Bright red for "is a type of"
                'hyponym': '#4488FF',    # Bright blue for "type includes"
                'meronym': '#44AA44',    # Green for "has part"
                'holonym': '#FFAA00'     # Orange for "part of"
            }
            color = edge_colors.get(relation, '#888888')
        
        # Define relationship descriptions for tooltips
        relation_descriptions = {
            'sense': 'Word sense connection',
            'hypernym': 'Is a type of (more general)',
            'hyponym': 'Type includes (more specific)',
            'meronym': 'Has part',
            'holonym': 'Part of'
        }
        
        description = relation_descriptions.get(relation, relation)
        
        # Configure edge properties
        edge_config = {
            'color': color,
            'width': edge_width + 1 if relation != 'sense' else edge_width,  # Slightly thicker for relationships
            'title': description,
            'arrows': 'to'  # Always show arrows since it's directed
        }
        
        net.add_edge(source, target, **edge_config)
    
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
                            
                            // Handle different node types in new structure
                            if (nodeId.includes('_main')) {
                                targetWord = nodeId.replace('_main', '');
                            } else if (nodeId.includes('_breadcrumb')) {
                                targetWord = nodeId.replace('_breadcrumb', '');
                            } else if (nodeId.includes('_word')) {
                                // It's a word node - extract the word part
                                targetWord = nodeId.replace('_word', '');
                            } else if (nodeId.includes('.')) {
                                // It's a synset - extract the lemma
                                targetWord = nodeId.split('.')[0];
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
    
    # Define colors for different node types (new structure)
    node_colors = []
    for node in G.nodes():
        node_data = G.nodes[node]
        node_type = node_data.get('node_type', 'unknown')
        
        if node_type == 'main' or '_main' in node:
            node_colors.append('#FF6B6B')  # Red for main word
        elif node_type == 'word' or '_word' in node:
            node_colors.append('#4ECDC4')  # Teal for related words
        elif node_type == 'synset' or '.' in node:
            node_colors.append('#DDA0DD')  # Purple for synsets
        else:
            node_colors.append('#CCCCCC')  # Grey for unknown/breadcrumb
    
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
    
    # Create legend for new structure
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF6B6B', markersize=10, label='Main Word'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#DDA0DD', markersize=10, label='Word Senses'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4ECDC4', markersize=10, label='Related Words')
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
                                include_holonyms: bool = True,
                                sense_number: int = None) -> Tuple[nx.Graph, Dict]:
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
        sense_number: Specific sense number to display (1-based, None for all)
        
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