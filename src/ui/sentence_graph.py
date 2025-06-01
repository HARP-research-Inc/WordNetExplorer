"""
Sentence graph visualization component for dependency trees with WordNet synsets.
"""

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import networkx as nx
from typing import Dict, List, Optional, Tuple
import json


def create_sentence_graph(analysis, settings: Dict) -> nx.DiGraph:
    """
    Create a NetworkX graph from sentence analysis.
    
    Args:
        analysis: SentenceAnalysis object
        settings: Visualization settings
        
    Returns:
        NetworkX directed graph
    """
    G = nx.DiGraph()
    
    # Add nodes for each token
    for i, token in enumerate(analysis.tokens):
        # Node attributes
        node_attrs = {
            'label': f"{token.text}\n{token.tag}",
            'title': f"<b>{token.text}</b><br>"
                    f"Lemma: {token.lemma}<br>"
                    f"POS: {token.pos} ({token.tag})<br>"
                    f"Dependency: {token.dep}<br>"
                    f"Synsets: {', '.join(token.synsets[:3]) if token.synsets else 'None'}",
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
    
    # Add synset nodes if enabled
    if settings.get('show_synsets', True) and settings.get('synset_limit', 3) > 0:
        for i, token in enumerate(analysis.tokens):
            # Only add synsets for content words (nouns, verbs, adjectives, adverbs)
            if token.pos in ['NOUN', 'VERB', 'ADJ', 'ADV'] and token.synsets:
                synsets_to_show = token.synsets[:settings.get('synset_limit', 3)]
                
                for j, synset_name in enumerate(synsets_to_show):
                    synset_id = f"synset_{i}_{j}"
                    
                    # Get synset info
                    try:
                        from nltk.corpus import wordnet as wn
                        synset = wn.synset(synset_name)
                        definition = synset.definition()
                        examples = synset.examples()
                    except:
                        definition = "Definition not available"
                        examples = []
                    
                    # Add synset node
                    G.add_node(synset_id, 
                        label=synset_name.split('.')[0],
                        title=f"<b>{synset_name}</b><br>"
                              f"Definition: {definition}<br>"
                              f"Examples: {'; '.join(examples[:2]) if examples else 'None'}",
                        is_synset=True,
                        synset_name=synset_name,
                        pos=synset_name.split('.')[1] if '.' in synset_name else 'n'
                    )
                    
                    # Add edge from token to synset
                    G.add_edge(f"token_{i}", synset_id, 
                              label="sense", 
                              edge_type="synset_link")
    
    return G


def visualize_sentence_graph(G, analysis, settings: Dict) -> str:
    """
    Create PyVis visualization of the sentence graph.
    
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
    
    # Configure physics
    if settings.get('enable_physics', True):
        net.set_options(json.dumps({
            "physics": {
                "enabled": True,
                "hierarchicalRepulsion": {
                    "centralGravity": 0.0,
                    "springLength": 100,
                    "springConstant": 0.01,
                    "nodeDistance": 120,
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
                    "direction": "UD",  # Up-Down for dependency trees
                    "sortMethod": "directed",
                    "levelSeparation": 100,
                    "nodeSpacing": 150,
                    "treeSpacing": 200
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
                    "forceDirection": "vertical"
                },
                "arrows": {
                    "to": {
                        "enabled": True,
                        "scaleFactor": 0.8
                    }
                },
                "font": {
                    "size": 12,
                    "align": "middle"
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
    
    # Get sentence analyzer for colors
    from src.services.sentence_analyzer import SentenceAnalyzer
    analyzer = SentenceAnalyzer()
    
    # Add nodes
    for node_id, attrs in G.nodes(data=True):
        if attrs.get('is_synset'):
            # Synset node styling
            color = get_synset_color(attrs.get('pos', 'n'))
            shape = "box"
            size = 20
        else:
            # Token node styling
            color = analyzer.get_pos_color(attrs.get('tag', ''))
            shape = "ellipse" if not attrs.get('is_root') else "star"
            size = 30 if not attrs.get('is_root') else 40
        
        net.add_node(
            node_id,
            label=attrs.get('label', ''),
            title=attrs.get('title', ''),
            color=color,
            shape=shape,
            size=size,
            font={'size': 14 if not attrs.get('is_root') else 16}
        )
    
    # Add edges
    for source, target, attrs in G.edges(data=True):
        if attrs.get('edge_type') == 'synset_link':
            # Synset connection styling
            color = "#666666"
            width = 1
            dashes = True
        else:
            # Dependency edge styling
            dep = attrs.get('dep', '')
            color = analyzer.get_dependency_color(dep)
            width = 2
            dashes = False
        
        net.add_edge(
            source,
            target,
            label=attrs.get('label', ''),
            color=color,
            width=width,
            dashes=dashes
        )
    
    # Generate HTML
    return net.generate_html()


def get_synset_color(pos: str) -> str:
    """Get color for synset based on POS."""
    pos_colors = {
        'n': '#FFB6C1',  # Pink for nouns
        'v': '#98D8C8',  # Mint for verbs
        'a': '#F7DC6F',  # Yellow for adjectives
        's': '#F7DC6F',  # Yellow for satellite adjectives
        'r': '#BB8FCE'   # Purple for adverbs
    }
    return pos_colors.get(pos, '#D5D8DC')


def render_sentence_graph_visualization(analysis, settings: Dict):
    """
    Render the sentence dependency graph with WordNet connections.
    
    Args:
        analysis: SentenceAnalysis object
        settings: Visualization settings
    """
    # Create the graph
    G = create_sentence_graph(analysis, settings)
    
    if G.number_of_nodes() == 0:
        st.warning("No tokens found in the sentence.")
        return
    
    # Generate visualization
    html_content = visualize_sentence_graph(G, analysis, settings)
    
    # Display the graph
    st.markdown("### 🌳 Dependency Tree with WordNet Synsets")
    
    # Info about the visualization
    token_count = len([n for n in G.nodes() if not G.nodes[n].get('is_synset', False)])
    synset_count = len([n for n in G.nodes() if G.nodes[n].get('is_synset', False)])
    
    st.info(f"📊 Showing {token_count} tokens and {synset_count} synsets")
    
    # Render the interactive graph
    components.html(html_content, height=600, scrolling=True)
    
    # Display token details
    st.markdown("---")
    st.markdown("### 📝 Token Analysis")
    
    # Create columns for token cards
    cols = st.columns(3)
    
    for i, token in enumerate(analysis.tokens):
        col_idx = i % 3
        with cols[col_idx]:
            # Token card
            st.markdown(f"""
            <div style="border: 1px solid #444; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                <h4 style="margin-top: 0;">{token.text}</h4>
                <p><strong>Lemma:</strong> {token.lemma}</p>
                <p><strong>POS:</strong> {token.pos} ({token.tag})</p>
                <p><strong>Dependency:</strong> {token.dep}</p>
                <p><strong>Synsets:</strong> {len(token.synsets) if token.synsets else 0}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show synset details if available
            if token.synsets and settings.get('show_synset_details', True):
                with st.expander(f"View synsets for '{token.text}'"):
                    for synset_name in token.synsets[:3]:
                        try:
                            from nltk.corpus import wordnet as wn
                            synset = wn.synset(synset_name)
                            st.markdown(f"**{synset_name}**")
                            st.markdown(f"*{synset.definition()}*")
                            if synset.examples():
                                st.markdown(f"Example: {synset.examples()[0]}")
                            st.markdown("---")
                        except:
                            st.markdown(f"**{synset_name}** - *Definition not available*")


def render_sentence_legend():
    """Render the legend for the sentence graph."""
    st.markdown("""
    <div class="legend-container">
        <h4>🎨 Graph Legend</h4>
        
        <div style="margin-bottom: 15px;">
            <strong>Node Types:</strong>
            <ul style="list-style: none; padding-left: 0;">
                <li>⭐ <strong>Star</strong> - Root word of the sentence</li>
                <li>⭕ <strong>Ellipse</strong> - Other words in the sentence</li>
                <li>📦 <strong>Box</strong> - WordNet synsets (word senses)</li>
            </ul>
        </div>
        
        <div style="margin-bottom: 15px;">
            <strong>Part of Speech Colors:</strong>
            <ul style="list-style: none; padding-left: 0;">
                <li><span style="color: #FFB6C1;">●</span> Nouns (person, place, thing)</li>
                <li><span style="color: #98D8C8;">●</span> Verbs (actions, states)</li>
                <li><span style="color: #F7DC6F;">●</span> Adjectives (descriptive words)</li>
                <li><span style="color: #BB8FCE;">●</span> Adverbs (modifiers)</li>
                <li><span style="color: #85C1E2;">●</span> Determiners/Pronouns</li>
                <li><span style="color: #F8C471;">●</span> Prepositions</li>
                <li><span style="color: #ABEBC6;">●</span> Conjunctions</li>
            </ul>
        </div>
        
        <div>
            <strong>Edge Types:</strong>
            <ul style="list-style: none; padding-left: 0;">
                <li>➡️ <strong>Solid arrows</strong> - Dependency relations between words</li>
                <li>- - <strong>Dashed lines</strong> - Links to WordNet synsets</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True) 