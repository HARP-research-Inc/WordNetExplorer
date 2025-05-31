"""
Sense similarity graph visualization module.
"""

import streamlit as st
from pyvis.network import Network
import tempfile
import os
from typing import List, Dict, Optional
import streamlit.components.v1 as components

# Import the SenseScore from our service
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.services.sense_similarity import SenseScore


def create_sense_graph(
    word: str,
    sense_scores: List[SenseScore],
    settings: Dict,
    width: str = "100%",
    height: str = "600px"
) -> Network:
    """Create a network graph showing sense similarities."""
    
    # Create network with similar physics to main graph
    net = Network(
        height=height,
        width=width,
        bgcolor="#ffffff",
        font_color="#000000",
        directed=True
    )
    
    # Configure physics (similar to main graph but adjusted for sense display)
    net.set_options("""
    {
        "physics": {
            "enabled": true,
            "solver": "forceAtlas2Based",
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.01,
                "springLength": 200,
                "springConstant": 0.08,
                "damping": 0.4,
                "avoidOverlap": 1
            }
        },
        "nodes": {
            "font": {
                "size": 14,
                "face": "Arial"
            }
        },
        "edges": {
            "smooth": {
                "type": "continuous"
            },
            "font": {
                "size": 12,
                "face": "Arial",
                "background": "white",
                "strokeWidth": 2,
                "strokeColor": "white"
            }
        },
        "interaction": {
            "hover": true,
            "tooltipDelay": 300,
            "hideEdgesOnDrag": false
        }
    }
    """)
    
    # Add central node (the input word)
    net.add_node(
        word,
        label=word.upper(),
        size=40,
        color="#FF6B6B",  # Red for the central word
        font={"size": 20, "color": "white"},
        title=f"Target word: {word}",
        shape="circle"
    )
    
    # Filter senses based on settings
    filtered_scores = []
    for score in sense_scores[:settings['show_top_n']]:
        if score.max_score >= settings['min_score']:
            filtered_scores.append(score)
    
    if not filtered_scores:
        # Add a message node if no senses meet criteria
        net.add_node(
            "no_matches",
            label="No matching senses",
            size=20,
            color="#CCCCCC",
            font={"size": 12},
            title="No senses met the similarity threshold"
        )
        return net
    
    # Add sense nodes
    for i, score in enumerate(filtered_scores):
        # Extract sense number from synset name (e.g., "bank.n.01" -> "1")
        sense_num = score.synset_name.split('.')[-1].lstrip('0')
        node_id = f"{word}_sense_{sense_num}"
        
        # Node color based on score strength
        max_score = score.max_score
        if max_score >= 0.7:
            node_color = "#4ECDC4"  # Teal for high similarity
        elif max_score >= 0.4:
            node_color = "#95E1D3"  # Light teal for medium
        else:
            node_color = "#F3E5F5"  # Very light for low
        
        # Create hover text with definition
        hover_text = f"Sense {sense_num}: {score.definition[:100]}..."
        if len(score.definition) > 100:
            hover_text += f"\n\nFull: {score.definition}"
        
        net.add_node(
            node_id,
            label=f"Sense {sense_num}",
            size=25 + (max_score * 15),  # Size based on score
            color=node_color,
            font={"size": 14},
            title=hover_text,
            shape="circle"
        )
        
        # Add edges with scores
        if settings['use_definition'] and score.definition_score is not None:
            edge_id = f"def_{i}"
            net.add_edge(
                word,
                node_id,
                id=edge_id,
                label=f"Def: {score.definition_score:.3f}",
                color="#2ECC71",  # Green for definition
                width=1 + (score.definition_score * 4),
                title=f"Definition similarity: {score.definition_score:.3f}",
                font={"color": "#2ECC71", "size": 10}
            )
        
        if settings['use_context'] and score.context_score is not None:
            edge_id = f"ctx_{i}"
            # If we already have a definition edge, we need to curve this one
            if settings['use_definition'] and score.definition_score is not None:
                # Add with slight curve
                net.add_edge(
                    word,
                    node_id,
                    id=edge_id,
                    label=f"Ctx: {score.context_score:.3f}",
                    color="#3498DB",  # Blue for context
                    width=1 + (score.context_score * 4),
                    title=f"Context similarity: {score.context_score:.3f}",
                    font={"color": "#3498DB", "size": 10},
                    smooth={"type": "curvedCW", "roundness": 0.2}
                )
            else:
                net.add_edge(
                    word,
                    node_id,
                    id=edge_id,
                    label=f"Ctx: {score.context_score:.3f}",
                    color="#3498DB",  # Blue for context
                    width=1 + (score.context_score * 4),
                    title=f"Context similarity: {score.context_score:.3f}",
                    font={"color": "#3498DB", "size": 10}
                )
        
        # Add combined score edge if both scores exist
        if (settings['use_definition'] and settings['use_context'] and 
            score.definition_score is not None and score.context_score is not None):
            edge_id = f"combined_{i}"
            net.add_edge(
                word,
                node_id,
                id=edge_id,
                label=f"Avg: {score.combined_score:.3f}",
                color="#9B59B6",  # Purple for combined
                width=1 + (score.combined_score * 4),
                title=f"Combined similarity: {score.combined_score:.3f}",
                font={"color": "#9B59B6", "size": 10},
                smooth={"type": "curvedCCW", "roundness": 0.2}
            )
    
    return net


def render_sense_graph_visualization(
    word: str,
    sense_scores: List[SenseScore],
    settings: Dict
):
    """Render the sense similarity graph visualization."""
    
    if not sense_scores:
        st.info("No senses found for the given word.")
        return
    
    # Create the graph
    net = create_sense_graph(word, sense_scores, settings)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as tmp:
        net.save_graph(tmp.name)
        tmp_path = tmp.name
    
    # Read the HTML content
    with open(tmp_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Display the graph
    components.html(html_content, height=650, scrolling=False)
    
    # Clean up
    os.unlink(tmp_path)
    
    # Display legend
    with st.expander("📊 Graph Legend", expanded=False):
        st.markdown("""
        **Node Size**: Larger nodes indicate higher similarity scores
        
        **Node Colors**:
        - 🔴 Red: Input word
        - 🟢 Teal: High similarity (≥0.7)
        - 🟡 Light Teal: Medium similarity (0.4-0.7)
        - ⚪ Light Purple: Low similarity (<0.4)
        
        **Edge Colors**:
        - 🟢 Green: Definition similarity
        - 🔵 Blue: Context similarity
        - 🟣 Purple: Combined average
        
        **Edge Width**: Thicker edges indicate stronger similarity
        """)
    
    # Display detailed scores
    with st.expander("📋 Detailed Scores", expanded=False):
        for score in sense_scores[:settings['show_top_n']]:
            if score.max_score >= settings['min_score']:
                sense_num = score.synset_name.split('.')[-1].lstrip('0')
                st.markdown(f"**Sense {sense_num}**: {score.definition[:60]}...")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if score.definition_score is not None:
                        st.metric("Definition", f"{score.definition_score:.3f}")
                with col2:
                    if score.context_score is not None:
                        st.metric("Context", f"{score.context_score:.3f}")
                with col3:
                    if score.combined_score is not None:
                        st.metric("Combined", f"{score.combined_score:.3f}")
                
                st.markdown("---") 