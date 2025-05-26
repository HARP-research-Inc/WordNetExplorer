"""
Graph display components for WordNet Explorer.
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import shutil
from ..config.settings import COLOR_SCHEMES
from ..utils.helpers import ensure_downloads_directory, validate_filename
from ..wordnet_explorer import build_wordnet_graph, visualize_graph


def render_color_legend(color_scheme):
    """
    Render the color legend for the graph.
    
    Args:
        color_scheme (str): The selected color scheme
    """
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["Default"])
    
    st.markdown(f"""
    <div class="legend-container">
        <div class="legend-item">
            <div style="width: 20px; height: 20px; background-color: {colors['main']}; border-radius: 50%; margin-right: 10px;"></div>
            <strong>Main Word</strong> - Your input word
        </div>
        <div class="legend-item">
            <div style="width: 20px; height: 20px; background-color: {colors['synset']}; border-radius: 50%; margin-right: 10px;"></div>
            <strong>Word Senses</strong> - Different meanings of the word
        </div>
        <div class="legend-item">
            <div style="width: 20px; height: 20px; background-color: {colors['hyper']}; border-radius: 50%; margin-right: 10px;"></div>
            <strong>Hypernyms ↑</strong> - More general concepts
        </div>
        <div class="legend-item">
            <div style="width: 20px; height: 20px; background-color: {colors['hypo']}; border-radius: 50%; margin-right: 10px;"></div>
            <strong>Hyponyms ↓</strong> - More specific concepts
        </div>
        <div class="legend-item">
            <div style="width: 20px; height: 20px; background-color: {colors['mero']}; border-radius: 50%; margin-right: 10px;"></div>
            <strong>Meronyms ⊂</strong> - Part-of relationships
        </div>
        <div class="legend-item">
            <div style="width: 20px; height: 20px; background-color: {colors['holo']}; border-radius: 50%; margin-right: 10px;"></div>
            <strong>Holonyms ⊃</strong> - Whole-of relationships
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_interactive_controls(G, depth, enable_physics):
    """
    Render the interactive controls information.
    
    Args:
        G: The NetworkX graph
        depth (int): The exploration depth
        enable_physics (bool): Whether physics is enabled
    """
    st.markdown(f"""
    <div class="legend-container">
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


def render_exploration_tips():
    """Render tips for exploration."""
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


def render_graph_visualization(word, settings):
    """
    Render the complete graph visualization section.
    
    Args:
        word (str): The word to visualize
        settings (dict): Dictionary containing all graph settings
    """
    st.markdown('<h2 class="sub-header">Relationship Graph</h2>', unsafe_allow_html=True)
    
    # Show navigation info
    st.info("💡 **Double-click any node** to explore that concept! Your navigation history is saved above.")
    
    with st.spinner(f"Building WordNet graph for '{word}'..."):
        # Build the graph
        G, node_labels = build_wordnet_graph(
            word, 
            settings['depth'],
            include_hypernyms=settings['show_hypernyms'],
            include_hyponyms=settings['show_hyponyms'],
            include_meronyms=settings['show_meronyms'],
            include_holonyms=settings['show_holonyms']
        )
        
        if G.number_of_nodes() > 0:
            st.info(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Generate the interactive graph
            html_path = visualize_graph(
                G, node_labels, word,
                layout_type=settings['layout_type'],
                node_size_multiplier=settings['node_size_multiplier'],
                enable_physics=settings['enable_physics'],
                spring_strength=settings['spring_strength'],
                central_gravity=settings['central_gravity'],
                show_labels=settings['show_labels'],
                show_arrows=settings['show_arrows'],
                edge_width=settings['edge_width'],
                color_scheme=settings['color_scheme']
            )
            
            if html_path:
                # Read and display the HTML content
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                components.html(html_content, height=600)
                
                # Add comprehensive legend and controls
                render_graph_legend_and_controls(G, settings)
                
                # Save the graph if requested
                if settings['save_graph']:
                    save_graph_file(html_path, settings['filename'])
                
                # Clean up the temporary file
                os.unlink(html_path)
            else:
                st.error("Failed to generate graph visualization")
        else:
            st.warning(f"No WordNet connections found for '{word}'")


def render_graph_legend_and_controls(G, settings):
    """
    Render the complete legend and controls section below the graph.
    
    Args:
        G: The NetworkX graph
        settings (dict): Dictionary containing all graph settings
    """
    st.markdown("---")
    st.markdown("### 🗝️ Graph Legend & Controls")
    
    # Create legend in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Node Types")
        render_color_legend(settings['color_scheme'])
    
    with col2:
        st.markdown("#### 🎮 Interactive Controls")
        render_interactive_controls(G, settings['depth'], settings['enable_physics'])
    
    # Additional info section
    st.markdown("#### 💡 Tips for Exploration")
    render_exploration_tips()


def save_graph_file(html_path, filename):
    """
    Save the graph HTML file to the downloads directory.
    
    Args:
        html_path (str): Path to the temporary HTML file
        filename (str): Desired filename for the saved file
    """
    downloads_dir = ensure_downloads_directory()
    validated_filename = validate_filename(filename, ".html")
    save_path = downloads_dir / validated_filename
    
    shutil.copy(html_path, save_path)
    st.success(f"Interactive graph saved to: {save_path}") 