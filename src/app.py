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
    word = st.text_input("Enter a word to explore", "").strip().lower()
    
    # Depth control
    depth = st.slider("Exploration depth", min_value=1, max_value=3, value=1, 
                     help="How deep to explore relationships (higher values create larger graphs)")
    
    # Edge type toggles
    st.markdown("### Relationship Types")
    show_hypernyms = st.checkbox("Include Hypernyms (↑)", value=True)
    show_hyponyms = st.checkbox("Include Hyponyms (↓)", value=True)
    show_meronyms = st.checkbox("Include Meronyms (⊂)", value=True)
    show_holonyms = st.checkbox("Include Holonyms (⊃)", value=True)
    
    # Display options
    st.markdown("### Display Options")
    show_info = st.checkbox("Show word information", value=True)
    show_graph = st.checkbox("Show relationship graph", value=True)
    
    # Save options
    st.markdown("### Save Options")
    save_graph = st.checkbox("Save graph to file")
    if save_graph:
        filename = st.text_input("Filename (without extension)", "wordnet_graph")
        if not filename:
            filename = "wordnet_graph"
        if not filename.endswith(".png"):
            filename += ".png"
    
    # About section
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool uses NLTK's WordNet to explore semantic relationships between words.
    
    **Relationship Types:**
    - 🔴 Main word
    - 🟣 Word senses
    - 🔵 Hypernyms (↑) - more general concepts
    - 🔵 Hyponyms (↓) - more specific concepts
    - 🟢 Meronyms (⊂) - part-of relationships
    - 🟡 Holonyms (⊃) - whole-of relationships
    """)

# Main content
if word:
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
                print_word_info(word)
                
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
            
            with st.spinner(f"Building WordNet graph for '{word}'..."):
                G, node_labels = build_wordnet_graph(
                    word, depth,
                    include_hypernyms=show_hypernyms,
                    include_hyponyms=show_hyponyms,
                    include_meronyms=show_meronyms,
                    include_holonyms=show_holonyms
                )
                
                if G.number_of_nodes() > 0:
                    st.info(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
                    
                    # Generate the interactive graph
                    html_path = visualize_graph(G, node_labels, word)
                    
                    if html_path:
                        # Read the HTML content
                        with open(html_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # Display the interactive graph
                        components.html(html_content, height=600)
                        
                        # Save the graph if requested
                        if save_graph:
                            # Create a downloads directory if it doesn't exist
                            downloads_dir = Path("downloads")
                            downloads_dir.mkdir(exist_ok=True)
                            
                            # Save the file
                            save_path = downloads_dir / filename.replace('.png', '.html')
                            import shutil
                            shutil.copy(html_path, save_path)
                            st.success(f"Interactive graph saved to: {save_path}")
                        
                        # Clean up the temporary file
                        os.unlink(html_path)
                else:
                    st.warning(f"No WordNet connections found for '{word}'")
    
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