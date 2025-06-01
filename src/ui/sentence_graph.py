"""
Sentence graph visualization component for dependency trees with WordNet synsets.
"""

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx
from typing import Dict, List, Optional, Tuple
import json


def create_syntactic_graph(analysis, settings: Dict) -> nx.DiGraph:
    """
    Create a NetworkX graph from syntactic tree.
    
    Args:
        analysis: SentenceAnalysis object with syntactic tree
        settings: Visualization settings
        
    Returns:
        NetworkX directed graph
    """
    G = nx.DiGraph()
    
    if not analysis.syntactic_tree:
        # Fallback to simple token graph if no syntactic tree
        return create_sentence_graph(analysis, settings)
    
    # Build graph from syntactic tree
    def add_node_recursive(node, parent_id=None):
        # Create node attributes based on node type
        if node.node_type == 'word' and node.token_info:
            # Word node with synset information
            token = node.token_info
            
            # Create simple tooltip with synset info
            if token.best_synset:
                synset_name, definition = token.best_synset
                # Extract just the sense number from synset name (e.g., "bank.n.01" -> "1")
                sense_num = synset_name.split('.')[-1].lstrip('0')
                tooltip = f"{node.text}.{sense_num}: {definition}"
            else:
                tooltip = node.text
            
            node_attrs = {
                'label': node.text,
                'title': tooltip,
                'node_type': 'word',
                'pos': token.pos,
                'tag': token.tag,
                'has_synset': bool(token.synsets)
            }
        else:
            # Clause or sentence node - just show the text
            node_attrs = {
                'label': node.text if len(node.text) < 50 else node.text[:47] + '...',
                'title': node.text,
                'node_type': node.node_type,
                'full_text': node.text
            }
        
        # Add node to graph
        G.add_node(node.node_id, **node_attrs)
        
        # Add edge from parent if exists
        if parent_id and node.edge_label:
            G.add_edge(parent_id, node.node_id, label=node.edge_label)
        
        # Recursively add children
        for child in node.children:
            add_node_recursive(child, node.node_id)
    
    # Start building from root
    add_node_recursive(analysis.syntactic_tree)
    
    return G


def create_sentence_graph(analysis, settings: Dict) -> nx.DiGraph:
    """
    Create a NetworkX graph from sentence analysis (fallback method).
    
    Args:
        analysis: SentenceAnalysis object
        settings: Visualization settings
        
    Returns:
        NetworkX directed graph
    """
    G = nx.DiGraph()
    
    # Add nodes for each token
    for i, token in enumerate(analysis.tokens):
        # Create simple tooltip
        if token.best_synset:
            synset_name, definition = token.best_synset
            sense_num = synset_name.split('.')[-1].lstrip('0')
            tooltip = f"{token.text}.{sense_num}: {definition}"
        else:
            tooltip = token.text
        
        # Node attributes
        node_attrs = {
            'label': f"{token.text}\n{token.tag}",
            'title': tooltip,
            'pos': token.pos,
            'tag': token.tag,
            'dep': token.dep,
            'lemma': token.lemma,
            'synsets': token.synsets,
            'is_root': i == analysis.root_index,
            'token_index': i
        }
        
        G.add_node(f"token_{i}", **node_attrs)
    
    # Add dependency edges
    for i, token in enumerate(analysis.tokens):
        if i != token.head and token.dep != 'ROOT':
            # Add edge from head to dependent
            G.add_edge(
                f"token_{token.head}",
                f"token_{i}",
                label=token.dep,
                dep=token.dep
            )
    
    return G


def visualize_syntactic_graph(G, analysis, settings: Dict) -> str:
    """
    Create PyVis visualization of the syntactic graph.
    
    Args:
        G: NetworkX graph
        analysis: SentenceAnalysis object
        settings: Visualization settings
        
    Returns:
        HTML string for the visualization
    """
    # Create PyVis network
    net = Network(
        height="600px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        directed=True
    )
    
    # Configure physics for hierarchical layout
    if settings.get('enable_physics', True):
        net.set_options(json.dumps({
            "physics": {
                "enabled": True,
                "hierarchicalRepulsion": {
                    "centralGravity": 0.0,
                    "springLength": 150,
                    "springConstant": 0.01,
                    "nodeDistance": 200,
                    "damping": 0.09
                },
                "solver": "hierarchicalRepulsion",
                "stabilization": {
                    "enabled": True,
                    "iterations": 1000,
                    "updateInterval": 50
                }
            },
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "direction": "UD",  # Up-Down for tree
                    "sortMethod": "directed",
                    "levelSeparation": 120,
                    "nodeSpacing": 200,
                    "treeSpacing": 250,
                    "parentCentralization": True
                }
            },
            "nodes": {
                "font": {
                    "size": 14,
                    "face": "arial"
                }
            },
            "edges": {
                "smooth": {
                    "type": "cubicBezier",
                    "forceDirection": "vertical",
                    "roundness": 0.4
                },
                "arrows": {
                    "to": {
                        "enabled": True,
                        "scaleFactor": 0.8
                    }
                },
                "font": {
                    "size": 12,
                    "align": "middle",
                    "background": "rgba(0,0,0,0.7)"
                }
            },
            "interaction": {
                "hover": True,
                "tooltipDelay": 200,
                "zoomView": True,
                "dragView": True
            }
        }))
    else:
        net.toggle_physics(False)
    
    # Get color helper
    from src.services.linguistic_colors import LinguisticColors
    colors = LinguisticColors()
    
    # Add nodes
    for node_id, attrs in G.nodes(data=True):
        node_type = attrs.get('node_type', 'word')
        
        if node_type == 'sentence':
            # Sentence node - root
            color = '#FFD700'  # Gold
            shape = 'box'
            size = 40
            font_size = 16
        elif node_type == 'clause':
            # Clause node
            color = '#87CEEB'  # Sky blue
            shape = 'ellipse'
            size = 35
            font_size = 14
        elif node_type == 'phrase':
            # Phrase node (noun phrases, prep phrases, etc.)
            color = '#DDA0DD'  # Plum
            shape = 'box'
            size = 30
            font_size = 12
        elif node_type == 'word':
            # Word node
            if attrs.get('pos'):
                color = colors.get_pos_color(attrs.get('tag', ''))
            else:
                color = '#D5D8DC'
            shape = 'dot'
            size = 25
            font_size = 12
            
            # Highlight words with synsets
            if attrs.get('has_synset'):
                shape = 'diamond'
        else:
            # Default
            color = '#B8B8B8'
            shape = 'dot'
            size = 20
            font_size = 12
        
        net.add_node(
            node_id,
            label=attrs.get('label', ''),
            title=attrs.get('title', ''),
            color=color,
            shape=shape,
            size=size,
            font={'size': font_size, 'color': 'white'}
        )
    
    # Add edges with custom styling
    edge_colors = LinguisticColors.EDGE_COLORS
    
    for source, target, attrs in G.edges(data=True):
        edge_label = attrs.get('label', '')
        color = edge_colors.get(edge_label, '#888888')
        
        net.add_edge(
            source,
            target,
            label=edge_label,
            color=color,
            width=2,
            font={'size': 10, 'color': color}
        )
    
    # Generate HTML
    return net.generate_html()


def render_sentence_graph_visualization(analysis, settings: Dict):
    """
    Render the sentence syntactic graph.
    
    Args:
        analysis: SentenceAnalysis object
        settings: Visualization settings
    """
    # Create the graph - use syntactic tree if available
    if analysis.syntactic_tree:
        G = create_syntactic_graph(analysis, settings)
    else:
        G = create_sentence_graph(analysis, settings)
    
    if G.number_of_nodes() == 0:
        st.warning("No tokens found in the sentence.")
        return
    
    # Generate visualization
    html_content = visualize_syntactic_graph(G, analysis, settings)
    
    # Display the graph
    st.markdown("### 🌳 Syntactic Tree with WordNet Senses")
    
    # Info about the visualization
    node_types = {}
    for _, attrs in G.nodes(data=True):
        node_type = attrs.get('node_type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    info_parts = []
    if 'sentence' in node_types:
        info_parts.append(f"{node_types['sentence']} sentence")
    if 'clause' in node_types:
        info_parts.append(f"{node_types['clause']} clause(s)")
    if 'word' in node_types:
        info_parts.append(f"{node_types['word']} words")
    
    st.info(f"📊 Showing {' • '.join(info_parts)}")
    
    # Render the interactive graph
    components.html(html_content, height=600, scrolling=True)
    
    # Display token details if we have them
    if hasattr(analysis, 'tokens') and analysis.tokens:
        st.markdown("---")
        st.markdown("### 📝 Word Analysis")
        
        # Create columns for token cards
        cols = st.columns(3)
        
        for i, token in enumerate(analysis.tokens):
            col_idx = i % 3
            with cols[col_idx]:
                # Token card with synset info
                synset_info = ""
                if token.best_synset:
                    synset_name, definition = token.best_synset
                    synset_info = f"""
                    <div style="margin-top: 8px; padding: 8px; background-color: rgba(255,255,255,0.1); border-radius: 4px;">
                        <p style="margin: 0;"><strong>Synset:</strong> {synset_name}</p>
                        <p style="margin: 0; font-size: 0.9em; font-style: italic;">{definition[:100]}{'...' if len(definition) > 100 else ''}</p>
                    </div>
                    """
                
                st.markdown(f"""
                <div style="border: 1px solid #444; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                    <h4 style="margin-top: 0;">{token.text}</h4>
                    <p><strong>Lemma:</strong> {token.lemma}</p>
                    <p><strong>POS:</strong> {token.pos} ({token.tag})</p>
                    <p><strong>Dependency:</strong> {token.dep}</p>
                    <p><strong>Synsets:</strong> {len(token.synsets) if token.synsets else 0}</p>
                    {synset_info}
                </div>
                """, unsafe_allow_html=True)


def render_sentence_legend():
    """Render the legend for the sentence graph."""
    st.markdown("""
    <div class="legend-container">
        <h4>🎨 Graph Legend</h4>
        
        <div style="margin-bottom: 15px;">
            <strong>Node Types:</strong>
            <ul style="list-style: none; padding-left: 0;">
                <li>📦 <strong>Box (Gold)</strong> - Complete sentence</li>
                <li>⭕ <strong>Ellipse (Blue)</strong> - Clauses</li>
                <li>📦 <strong>Box (Plum)</strong> - Phrases (noun phrases, prep phrases)</li>
                <li>💎 <strong>Diamond</strong> - Words with synsets</li>
                <li>⚫ <strong>Dot</strong> - Other words</li>
            </ul>
        </div>
        
        <div style="margin-bottom: 15px;">
            <strong>Edge Labels & Colors:</strong>
            <ul style="list-style: none; padding-left: 0;">
                <li><span style="color: #4169E1;">●</span> <strong>head</strong> - Head word of a phrase</li>
                <li><span style="color: #F7DC6F;">●</span> <strong>adj</strong> - Adjective modifier</li>
                <li><span style="color: #85C1E2;">●</span> <strong>det</strong> - Determiner (the, a, an)</li>
                <li><span style="color: #FF7F50;">●</span> <strong>prep_phrase</strong> - Prepositional phrase</li>
                <li><span style="color: #F8C471;">●</span> <strong>prep</strong> - Preposition</li>
                <li><span style="color: #00CED1;">●</span> <strong>pobj</strong> - Object of preposition</li>
                <li><span style="color: #FFD93D;">●</span> <strong>tverb</strong> - Main (tensed) verb</li>
                <li><span style="color: #FF8B94;">●</span> <strong>subj</strong> - Subject</li>
                <li><span style="color: #6BCB77;">●</span> <strong>obj</strong> - Object</li>
                <li><span style="color: #FF69B4;">●</span> <strong>num</strong> - Numeral modifier</li>
                <li><span style="color: #9370DB;">●</span> <strong>poss</strong> - Possessive (my, her, their)</li>
                <li><span style="color: #20B2AA;">●</span> <strong>compound</strong> - Compound modifier</li>
                <li><span style="color: #87CEEB;">●</span> <strong>core</strong> - Core of a phrase</li>
            </ul>
        </div>
        
        <div style="margin-bottom: 15px;">
            <strong>Lemma Decomposition Labels:</strong>
            <ul style="list-style: none; padding-left: 0;">
                <li><span style="color: #8B008B;">●</span> <strong>past</strong> - Past tense verb</li>
                <li><span style="color: #FF1493;">●</span> <strong>present</strong> - Present tense verb</li>
                <li><span style="color: #DA70D6;">●</span> <strong>gerund</strong> - Gerund/progressive form</li>
                <li><span style="color: #9932CC;">●</span> <strong>past_part</strong> - Past participle</li>
                <li><span style="color: #2E8B57;">●</span> <strong>singular</strong> - Singular noun</li>
                <li><span style="color: #3CB371;">●</span> <strong>plural</strong> - Plural noun</li>
                <li><span style="color: #1E90FF;">●</span> <strong>comparative</strong> - Comparative form</li>
                <li><span style="color: #0000CD;">●</span> <strong>superlative</strong> - Superlative form</li>
            </ul>
        </div>
        
        <div style="margin-bottom: 15px;">
            <strong>Part of Speech Colors (Words):</strong>
            <ul style="list-style: none; padding-left: 0;">
                <li><span style="color: #FFB6C1;">●</span> Nouns</li>
                <li><span style="color: #98D8C8;">●</span> Verbs</li>
                <li><span style="color: #F7DC6F;">●</span> Adjectives</li>
                <li><span style="color: #BB8FCE;">●</span> Adverbs</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True) 