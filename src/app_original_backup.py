#!/usr/bin/env python3
"""
WordNet Explorer - Streamlit UI

A web-based interface for exploring WordNet semantic relationships
using Streamlit.
"""

import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import core functionality
from src.wordnet_explorer import (
    download_nltk_data,
    get_synsets_for_word,
    build_wordnet_graph,
    visualize_graph,
    print_word_info
)

# Set page configuration
st.set_page_config(
    page_title="WordNet Explorer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for navigation
if 'navigation_history' not in st.session_state:
    st.session_state.navigation_history = []
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'graph_center' not in st.session_state:
    st.session_state.graph_center = None

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B8BBE;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #306998;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        color: #222;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        font-family: monospace;
        white-space: pre-wrap;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">WordNet Explorer</h1>', unsafe_allow_html=True)
st.markdown("Explore semantic relationships between words using WordNet")

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    
    # Word input
    word = st.text_input(
        "Enter a word to explore", 
        value=st.session_state.current_word if st.session_state.current_word else "",
        key="word_input"
    ).strip().lower()
    
    # Navigation History - collapsible section directly under word input
    if st.session_state.navigation_history:
        with st.expander("📚 Navigation History", expanded=True):
            st.markdown("Click any word to return to it:")
            
            # Create a more compact display with fewer columns
            max_cols = min(3, len(st.session_state.navigation_history))
            if max_cols > 0:
                # Split history into rows of max 3 items
                history_items = st.session_state.navigation_history
                for i in range(0, len(history_items), max_cols):
                    row_items = history_items[i:i + max_cols]
                    cols = st.columns(len(row_items))
                    
                    for j, hist_word in enumerate(row_items):
                        with cols[j]:
                            if st.button(f"📍 {hist_word}", key=f"hist_{i+j}", help=f"Return to '{hist_word}'"):
                                # Navigate back to this word
                                # Remove everything after this word in history
                                st.session_state.navigation_history = st.session_state.navigation_history[:i+j]
                                st.session_state.current_word = hist_word
                                st.rerun()
            
            # Show current word
            if st.session_state.current_word:
                st.markdown(f"**🎯 Current: {st.session_state.current_word}**")
            
            # Clear history button
            if st.button("🗑️ Clear History", help="Clear navigation history"):
                st.session_state.navigation_history = []
                st.rerun()
    
    # Navigation controls if we have history
    if st.session_state.navigation_history:
        st.markdown("### 🧭 Quick Navigation")
        if st.button("🏠 Start Fresh", help="Clear history and start fresh"):
            st.session_state.navigation_history = []
            st.session_state.current_word = None
            st.rerun()
        
        # Show current path
        path_display = " → ".join(st.session_state.navigation_history + [st.session_state.current_word if st.session_state.current_word else ""])
        st.markdown(f"**Current Path:** {path_display}")
    
    # Basic settings
    depth = st.slider("Exploration depth", min_value=1, max_value=3, value=1, 
                     help="How deep to explore relationships (higher values create larger graphs)")
    
    # Relationship types - collapsible
    with st.expander("🔗 Relationship Types", expanded=True):
        show_hypernyms = st.checkbox("Include Hypernyms (↑)", value=True)
        show_hyponyms = st.checkbox("Include Hyponyms (↓)", value=True)
        show_meronyms = st.checkbox("Include Meronyms (⊂)", value=True)
        show_holonyms = st.checkbox("Include Holonyms (⊃)", value=True)
    
    # Advanced graph settings - collapsible
    with st.expander("🎨 Graph Appearance"):
        # Layout options
        layout_type = st.selectbox(
            "Graph Layout",
            ["Force-directed (default)", "Hierarchical", "Circular", "Grid"],
            help="Choose how nodes are arranged in the graph"
        )
        
        # Node size settings
        node_size_multiplier = st.slider(
            "Node Size", 
            min_value=0.5, 
            max_value=2.0, 
            value=1.0, 
            step=0.1,
            help="Adjust the size of nodes in the graph"
        )
        
        # Color scheme
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Default", "Pastel", "Vibrant", "Monochrome"],
            help="Choose a color scheme for the graph"
        )
    
    # Physics simulation settings - collapsible
    with st.expander("⚙️ Physics Simulation"):
        enable_physics = st.checkbox("Enable Physics", value=True, 
                                    help="Allow nodes to move and settle automatically")
        
        if enable_physics:
            spring_strength = st.slider(
                "Spring Strength", 
                min_value=0.01, 
                max_value=0.1, 
                value=0.04, 
                step=0.01,
                help="How strongly nodes are pulled together"
            )
            
            central_gravity = st.slider(
                "Central Gravity", 
                min_value=0.1, 
                max_value=1.0, 
                value=0.3, 
                step=0.1,
                help="How strongly nodes are pulled to the center"
            )
        else:
            spring_strength = 0.04
            central_gravity = 0.3
    
    # Visual options - collapsible
    with st.expander("👁️ Visual Options"):
        show_labels = st.checkbox("Show Node Labels", value=True)
        show_arrows = st.checkbox("Show Directional Arrows", value=False)
        edge_width = st.slider("Edge Width", min_value=1, max_value=5, value=2)
    
    # Display options
    with st.expander("📋 Display Options", expanded=True):
        show_info = st.checkbox("Show word information", value=True)
        show_graph = st.checkbox("Show relationship graph", value=True)
    
    # Save options - collapsible
    with st.expander("💾 Save Options"):
        save_graph = st.checkbox("Save graph to file")
        if save_graph:
            filename = st.text_input("Filename (without extension)", "wordnet_graph")
            if not filename:
                filename = "wordnet_graph"
            if not filename.endswith(".html"):
                filename += ".html"
    
    # About section
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool uses NLTK's WordNet to explore semantic relationships between words.
    
    **Navigation:**
    - Double-click any node to explore that concept
    - Use breadcrumb navigation to go back
    - Grey dotted nodes are navigation breadcrumbs
    
    **Relationship Types:**
    - 🔴 Main word
    - 🟣 Word senses
    - 🔵 Hypernyms (↑) - more general concepts
    - 🔵 Hyponyms (↓) - more specific concepts
    - 🟢 Meronyms (⊂) - part-of relationships
    - 🟡 Holonyms (⊃) - whole-of relationships
    """)

# Main content
# Check for navigation from URL parameters
query_params = st.experimental_get_query_params()
if 'navigate_to' in query_params:
    navigate_to_word = query_params['navigate_to'][0]  # Get first value
    clicked_node = query_params.get('clicked_node', [''])[0]
    
    if navigate_to_word and navigate_to_word != st.session_state.current_word:
        # Add current word to history before navigating (if not already there)
        if st.session_state.current_word and st.session_state.current_word not in st.session_state.navigation_history:
            st.session_state.navigation_history.append(st.session_state.current_word)
        
        # Set the new word as current
        st.session_state.current_word = navigate_to_word
        
        # Clear the URL parameters and rerun
        st.experimental_set_query_params()
        st.rerun()

# Use the current word from session state, or fall back to text input
current_display_word = st.session_state.current_word if st.session_state.current_word else word

if word or current_display_word:
    # Update session state if this is a new word
    if current_display_word != st.session_state.current_word:
        st.session_state.current_word = current_display_word
    
    try:
        # Download NLTK data if needed
        with st.spinner("Loading WordNet data..."):
            download_nltk_data()
        
        # Show word information if requested
        if show_info:
            st.markdown('<h2 class="sub-header">Word Information</h2>', unsafe_allow_html=True)
            
            # Create a container for word info
            info_container = st.container()
            
            # Capture the output of print_word_info
            with tempfile.TemporaryFile(mode='w+') as temp:
                # Redirect stdout to our temporary file
                original_stdout = sys.stdout
                sys.stdout = temp
                
                # Call the function
                print_word_info(current_display_word)
                
                # Reset stdout
                sys.stdout = original_stdout
                
                # Get the output
                temp.seek(0)
                word_info = temp.read()
            
            # Display the word info with formatting
            st.markdown(f"<div class='info-box'>{word_info}</div>", unsafe_allow_html=True)
        
        # Build and display graph if requested
        if show_graph:
            st.markdown('<h2 class="sub-header">Relationship Graph</h2>', unsafe_allow_html=True)
            
            # Show navigation info
            st.info("💡 **Double-click any node** to explore that concept! Your navigation history is saved above.")
            
            with st.spinner(f"Building WordNet graph for '{current_display_word}'..."):
                # Always use the regular graph building (simpler approach)
                G, node_labels = build_wordnet_graph(
                    current_display_word, depth,
                    include_hypernyms=show_hypernyms,
                    include_hyponyms=show_hyponyms,
                    include_meronyms=show_meronyms,
                    include_holonyms=show_holonyms
                )
                
                if G.number_of_nodes() > 0:
                    st.info(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
                    
                    # Generate the interactive graph
                    html_path = visualize_graph(
                        G, node_labels, current_display_word,
                        layout_type=layout_type,
                        node_size_multiplier=node_size_multiplier,
                        enable_physics=enable_physics,
                        spring_strength=spring_strength,
                        central_gravity=central_gravity,
                        show_labels=show_labels,
                        show_arrows=show_arrows,
                        edge_width=edge_width,
                        color_scheme=color_scheme
                    )
                    
                    if html_path:
                        # Read the HTML content
                        with open(html_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # Display the interactive graph
                        components.html(html_content, height=600)
                        
                        # Add a comprehensive legend below the graph
                        st.markdown("---")
                        st.markdown("### 🗝️ Graph Legend & Controls")
                        
                        # Color scheme legend
                        color_schemes = {
                            "Default": {"main": "#FF6B6B", "synset": "#DDA0DD", "hyper": "#4ECDC4", "hypo": "#45B7D1", "mero": "#96CEB4", "holo": "#FFEAA7"},
                            "Pastel": {"main": "#FFB3BA", "synset": "#BFBFFF", "hyper": "#BAFFCA", "hypo": "#B3E5FF", "mero": "#C7FFB3", "holo": "#FFFFB3"},
                            "Vibrant": {"main": "#FF0000", "synset": "#9932CC", "hyper": "#00CED1", "hypo": "#1E90FF", "mero": "#32CD32", "holo": "#FFD700"},
                            "Monochrome": {"main": "#2C2C2C", "synset": "#5A5A5A", "hyper": "#777777", "hypo": "#949494", "mero": "#B1B1B1", "holo": "#CECECE"}
                        }
                        
                        colors = color_schemes.get(color_scheme, color_schemes["Default"])
                        
                        # Create legend in columns
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 🎨 Node Types")
                            st.markdown(f"""
                            <div style="padding: 10px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 10px;">
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 20px; height: 20px; background-color: {colors['main']}; border-radius: 50%; margin-right: 10px;"></div>
                                    <strong>Main Word</strong> - Your input word
                                </div>
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 20px; height: 20px; background-color: {colors['synset']}; border-radius: 50%; margin-right: 10px;"></div>
                                    <strong>Word Senses</strong> - Different meanings of the word
                                </div>
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 20px; height: 20px; background-color: {colors['hyper']}; border-radius: 50%; margin-right: 10px;"></div>
                                    <strong>Hypernyms ↑</strong> - More general concepts
                                </div>
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 20px; height: 20px; background-color: {colors['hypo']}; border-radius: 50%; margin-right: 10px;"></div>
                                    <strong>Hyponyms ↓</strong> - More specific concepts
                                </div>
                                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                    <div style="width: 20px; height: 20px; background-color: {colors['mero']}; border-radius: 50%; margin-right: 10px;"></div>
                                    <strong>Meronyms ⊂</strong> - Part-of relationships
                                </div>
                                <div style="display: flex; align-items: center;">
                                    <div style="width: 20px; height: 20px; background-color: {colors['holo']}; border-radius: 50%; margin-right: 10px;"></div>
                                    <strong>Holonyms ⊃</strong> - Whole-of relationships
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("#### 🎮 Interactive Controls")
                            st.markdown(f"""
                            <div style="padding: 10px; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 10px; color: #333;">
                                <div style="margin-bottom: 8px;">
                                    <strong style="color: #333;">🖱️ Mouse Controls:</strong>
                                    <ul style="margin: 5px 0; padding-left: 20px; color: #333;">
                                        <li><strong>Scroll</strong> - Zoom in/out</li>
                                        <li><strong>Click & Drag</strong> - Pan around the graph</li>
                                        <li><strong>Drag Node</strong> - Move individual nodes</li>
                                        <li><strong>Hover</strong> - View definitions and details</li>
                                        <li><strong>Double-click Node</strong> - Recenter on that word</li>
                                    </ul>
                                </div>
                                <div style="margin-bottom: 8px;">
                                    <strong style="color: #333;">📊 Graph Info:</strong>
                                    <ul style="margin: 5px 0; padding-left: 20px; color: #333;">
                                        <li><strong>Nodes:</strong> {G.number_of_nodes()}</li>
                                        <li><strong>Edges:</strong> {G.number_of_edges()}</li>
                                        <li><strong>Depth:</strong> {depth} level(s)</li>
                                        <li><strong>Physics:</strong> {'Enabled' if enable_physics else 'Disabled'}</li>
                                    </ul>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Additional info section
                        st.markdown("#### 💡 Tips for Exploration")
                        
                        tips_col1, tips_col2, tips_col3 = st.columns(3)
                        
                        with tips_col1:
                            st.markdown("""
                            <div style="color: #333;">
                            <strong>🎯 Focus Your Search:</strong>
                            <ul>
                            <li>Use relationship filters to see specific connections</li>
                            <li>Adjust depth to control complexity</li>
                            <li>Try different color schemes for clarity</li>
                            <li>Double-click nodes to explore deeper</li>
                            </ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with tips_col2:
                            st.markdown("""
                            <div style="color: #333;">
                            <strong>🔍 Analyze Relationships:</strong>
                            <ul>
                            <li>Hover over nodes for definitions</li>
                            <li>Look for clusters of related concepts</li>
                            <li>Follow paths to discover semantic chains</li>
                            <li>Use breadcrumb navigation to backtrack</li>
                            </ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with tips_col3:
                            st.markdown("""
                            <div style="color: #333;">
                            <strong>⚙️ Customize Display:</strong>
                            <ul>
                            <li>Adjust node sizes for readability</li>
                            <li>Enable/disable physics for static layouts</li>
                            <li>Toggle labels on/off for cleaner views</li>
                            <li>Switch color schemes for accessibility</li>
                            </ul>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Save the graph if requested
                        if save_graph:
                            # Create a downloads directory if it doesn't exist
                            downloads_dir = Path("downloads")
                            downloads_dir.mkdir(exist_ok=True)
                            
                            # Save the file
                            save_path = downloads_dir / filename.replace('.html', '.html')
                            import shutil
                            shutil.copy(html_path, save_path)
                            st.success(f"Interactive graph saved to: {save_path}")
                        
                        # Clean up the temporary file
                        os.unlink(html_path)
                else:
                    st.warning(f"No WordNet connections found for '{current_display_word}'")
    
    except Exception as e:
        st.error(f"Error: {e}")

else:
    # Show welcome message and instructions
    st.markdown("""
    ## Welcome to WordNet Explorer!
    
    Enter a word in the sidebar to explore its semantic relationships in WordNet.
    
    ### Features:
    - 🔍 **Word Exploration**: Discover semantic relationships for any English word
    - 📊 **Graph Visualization**: Interactive network graphs showing word connections
    - 🎨 **Color-coded Relationships**: Different colors for hypernyms, hyponyms, meronyms, etc.
    - 📖 **Detailed Information**: View definitions, examples, and related words
    - 💾 **Save Graphs**: Export visualizations as PNG images
    - 🎯 **Configurable Depth**: Control how deep to explore relationships
    
    ### Example Words to Try:
    - dog
    - computer
    - tree
    - love
    - book
    """) 