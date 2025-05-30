"""
Graph display components for WordNet Explorer.
"""

import streamlit as st
import streamlit.components.v1 as components
from streamlit.runtime.scriptrunner import ScriptRunContext
import os
import shutil
from config.settings import COLOR_SCHEMES, POS_COLORS
from utils.helpers import ensure_downloads_directory, validate_filename

def render_color_legend(color_scheme, synset_search_mode=False):
    """
    Render the color legend for the graph.
    
    Args:
        color_scheme (str): The selected color scheme
        synset_search_mode (bool): Whether we're in synset search mode
    """
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["Default"])
    pos_colors = POS_COLORS.get(color_scheme, POS_COLORS["Default"])
    
    if synset_search_mode:
        # Legend for synset-focused mode
        st.markdown(f"""
        <div class="legend-container">
            <div class="legend-item">
                <div style="width: 20px; height: 20px; background-color: {colors.get('word_sense', '#FFB347')}; clip-path: polygon(50% 0%, 0% 100%, 100% 100%); margin-right: 10px;"></div>
                <strong>Word Senses</strong> - Individual word meanings in the synset
            </div>
            <div style="margin-bottom: 10px;">
                <strong>Synsets by Part of Speech:</strong>
                <div style="margin-left: 10px; margin-top: 5px;">
                    <div class="legend-item">
                        <div style="width: 20px; height: 20px; background-color: {pos_colors['n']}; margin-right: 10px;"></div>
                        <strong>Nouns</strong> - Things, people, places
                    </div>
                    <div class="legend-item">
                        <div style="width: 20px; height: 20px; background-color: {pos_colors['v']}; margin-right: 10px;"></div>
                        <strong>Verbs</strong> - Actions, states
                    </div>
                    <div class="legend-item">
                        <div style="width: 20px; height: 20px; background-color: {pos_colors['a']}; margin-right: 10px;"></div>
                        <strong>Adjectives</strong> - Descriptive words
                    </div>
                    <div class="legend-item">
                        <div style="width: 20px; height: 20px; background-color: {pos_colors['r']}; margin-right: 10px;"></div>
                        <strong>Adverbs</strong> - Modifying words
                    </div>
                </div>
            </div>
            <div class="legend-item">
                <div style="width: 20px; height: 20px; background-color: {colors['main']}; border-radius: 50%; margin-right: 10px;"></div>
                <strong>Main Words</strong> - Root forms of words in synsets
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Legend for word-focused mode
        st.markdown(f"""
        <div class="legend-container">
            <div class="legend-item">
                <div style="width: 20px; height: 20px; background-color: {colors['main']}; border-radius: 50%; margin-right: 10px;"></div>
                <strong>Main Word</strong> - Your input word
            </div>
            <div class="legend-item">
                <div style="width: 20px; height: 20px; background-color: {colors.get('word_sense', '#FFB347')}; clip-path: polygon(50% 0%, 0% 100%, 100% 100%); margin-right: 10px;"></div>
                <strong>Word Senses</strong> - Different meanings of your word
            </div>
            <div style="margin-bottom: 10px;">
                <strong>Synsets by Part of Speech:</strong>
                <div style="margin-left: 10px; margin-top: 5px;">
                    <div class="legend-item">
                        <div style="width: 20px; height: 20px; background-color: {pos_colors['n']}; margin-right: 10px;"></div>
                        <strong>Nouns</strong> - Things, people, places
                    </div>
                    <div class="legend-item">
                        <div style="width: 20px; height: 20px; background-color: {pos_colors['v']}; margin-right: 10px;"></div>
                        <strong>Verbs</strong> - Actions, states
                    </div>
                    <div class="legend-item">
                        <div style="width: 20px; height: 20px; background-color: {pos_colors['a']}; margin-right: 10px;"></div>
                        <strong>Adjectives</strong> - Descriptive words
                    </div>
                    <div class="legend-item">
                        <div style="width: 20px; height: 20px; background-color: {pos_colors['r']}; margin-right: 10px;"></div>
                        <strong>Adverbs</strong> - Modifying words
                    </div>
                </div>
            </div>
            <div class="legend-item">
                <div style="width: 20px; height: 20px; background-color: {colors['word']}; border-radius: 50%; margin-right: 10px;"></div>
                <strong>Related Words</strong> - Connected through semantic relationships
            </div>
        </div>
    
    <div style="margin-top: 15px;">
        <strong>Edge Colors & Relationships:</strong>
        <div style="margin-left: 10px; margin-top: 5px;">
            <div style="margin: 3px 0;"><span style="color: #FF4444; font-weight: bold;">→</span> <strong>Taxonomic Relations (Red)</strong> - Classification relationships</div>
            <div style="margin: 3px 0; margin-left: 15px;">• <strong>Hypernym arrows</strong> point from specific to general (\"femtosecond → time_unit\")</div>
            <div style="margin: 3px 0; margin-left: 15px;">• <strong>Hyponym arrows</strong> point from general to specific (\"time_unit → femtosecond\")</div>
            <div style="margin: 3px 0;"><span style="color: #44AA44; font-weight: bold;">→</span> <strong>Part-Whole Relations (Green)</strong> - Compositional relationships</div>
            <div style="margin: 3px 0; margin-left: 15px;">• <strong>Meronym arrows</strong> point from part to whole (\"wheel → car\")</div>
            <div style="margin: 3px 0; margin-left: 15px;">• <strong>Holonym arrows</strong> point from whole to part (\"car → wheel\")</div>
            <div style="margin: 3px 0;"><span style="color: #666666; font-weight: bold;">→</span> <strong>Word Sense (Gray)</strong> - connects word senses to synsets</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_interactive_controls(G, settings):
    """
    Render the interactive controls information.
    
    Args:
        G: The NetworkX graph
        settings (dict): Dictionary containing all graph settings including advanced options
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
                <li><strong>Nodes:</strong> {G.number_of_nodes()}{f" (max: {settings.get('max_nodes', 100)})" if settings.get('max_nodes', 100) != 100 else ""}</li>
                <li><strong>Edges:</strong> {G.number_of_edges()}</li>
                <li><strong>Depth:</strong> {settings.get('depth', 1)} level(s)</li>
                <li><strong>Max Branches:</strong> {settings.get('max_branches', 5)} per node</li>
                <li><strong>Physics:</strong> {'Enabled' if settings.get('enable_physics', True) else 'Disabled'}</li>
                {f"<li><strong>POS Filter:</strong> {', '.join(settings.get('pos_filter', ['All']))}</li>" if settings.get('pos_filter') and len(settings.get('pos_filter', [])) < 4 else ""}
                {f"<li><strong>Simplified Mode:</strong> {'Yes' if settings.get('simplified_mode', False) else 'No'}</li>" if settings.get('simplified_mode', False) else ""}
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_exploration_tips():
    """Render tips for exploration."""
    tips_col1, tips_col2, tips_col3 = st.columns(3)
    
    with tips_col1:
        st.markdown("""
        <div style="color: #FFFFFF;">
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
        <div style="color: #FFFFFF;">
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
        <div style="color: #FFFFFF;">
        <strong>⚙️ Customize Display:</strong>
        <ul>
        <li>Adjust node sizes for readability</li>
        <li>Enable/disable physics for static layouts</li>
        <li>Toggle labels on/off for cleaner views</li>
        <li>Switch color schemes for accessibility</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)


def save_graph_to_file(explorer, G, node_labels, word, settings):
    """
    Save the graph to file(s) based on settings.
    
    Args:
        explorer: WordNetExplorer instance
        G: NetworkX graph
        node_labels: Node labels dictionary
        word: The word being visualized
        settings: Settings dictionary containing filename and other options
    """
    # Generate HTML content
    html_content = explorer.visualize_graph(
        G, node_labels, word,
        save_path=None,  # Don't save to file, get HTML content
        layout_type=settings['layout_type'],
        node_size_multiplier=settings['node_size_multiplier'],
        enable_physics=settings['enable_physics'],
        spring_strength=settings['spring_strength'],
        central_gravity=settings['central_gravity'],
        show_labels=settings['show_labels'],
        edge_width=settings['edge_width'],
        color_scheme=settings['color_scheme']
    )
    
    if html_content:
        # Store HTML content in session state
        st.session_state.html_content = html_content
    
    # Generate JSON content
    from src.graph import GraphSerializer
    serializer = GraphSerializer()
    
    # Add metadata
    metadata = {
        'word': word,
        'description': f'WordNet graph for "{word}"',
        'version': '1.0',
        'visualization_config': {
            'layout_type': settings['layout_type'],
            'node_size_multiplier': settings['node_size_multiplier'],
            'enable_physics': settings['enable_physics'],
            'spring_strength': settings['spring_strength'],
            'central_gravity': settings['central_gravity'],
            'show_labels': settings['show_labels'],
            'edge_width': settings['edge_width'],
            'color_scheme': settings['color_scheme']
        }
    }
    
    # Store JSON content in session state
    st.session_state.graph_data = serializer.serialize_graph(G, node_labels, metadata)


def render_graph_visualization(word, settings, explorer=None, synset_search_mode=False):
    """
    Render the graph visualization with the given settings.
    
    Args:
        word: The word to visualize
        settings: Dictionary of visualization settings
        explorer: Optional WordNetExplorer instance
        synset_search_mode: Whether we're in synset search mode
    """
    if explorer is None:
        from src.wordnet_explorer import WordNetExplorer
        explorer = WordNetExplorer()
    
    # Check if we should force regeneration due to URL parameter changes
    force_regeneration = settings.get('url_params_changed', False)
    
    # Check for imported graph
    if 'imported_graph' in st.session_state and not force_regeneration:
        G, node_labels, metadata = st.session_state.imported_graph
        # Update visualization settings from metadata if available
        if 'visualization_config' in metadata:
            settings.update(metadata['visualization_config'])
    else:
        # Clear imported graph if we're forcing regeneration
        if force_regeneration and 'imported_graph' in st.session_state:
            del st.session_state.imported_graph
        
        # Build the graph
        if synset_search_mode:
            G, node_labels = explorer.explore_synset(word)
        else:
            G, node_labels = explorer.explore_word(word)
    
    if G.number_of_nodes() > 0:
        st.info(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Show URL parameter change indicator if applicable
        if force_regeneration:
            st.success("🔄 Graph updated from URL parameters")
        
        # Generate the interactive graph using the new modular explorer
        html_content = explorer.visualize_graph(
            G, node_labels, word,
            save_path=None,  # Don't save to file, get HTML content
            layout_type=settings['layout_type'],
            node_size_multiplier=settings['node_size_multiplier'],
            enable_physics=settings['enable_physics'],
            spring_strength=settings['spring_strength'],
            central_gravity=settings['central_gravity'],
            show_labels=settings['show_labels'],
            edge_width=settings['edge_width'],
            color_scheme=settings['color_scheme']
        )
        
        if html_content:
            # Display the HTML content directly
            components.html(html_content, height=600)
            
            # Add comprehensive legend and controls
            render_graph_legend_and_controls(G, settings, synset_search_mode)
            
            # Always save graph data for download
            save_graph_to_file(explorer, G, node_labels, word, settings)
        else:
            st.error("Failed to generate graph visualization")
    else:
        if synset_search_mode:
            st.warning(f"No WordNet connections found for synset '{word}'")
        else:
            st.warning(f"No WordNet connections found for '{word}'")


def render_graph_legend_and_controls(G, settings, synset_search_mode=False):
    """
    Render the complete legend and controls section below the graph.
    
    Args:
        G: The NetworkX graph
        settings (dict): Dictionary containing all graph settings
        synset_search_mode (bool): Whether we're in synset search mode
    """
    st.markdown("---")
    st.markdown("### 🗝️ Graph Legend & Controls")
    
    # Create legend in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Node Types")
        render_color_legend(settings['color_scheme'], synset_search_mode)
    
    with col2:
        st.markdown("#### 🎮 Interactive Controls")
        render_interactive_controls(G, settings)
    
    # Additional info section
    st.markdown("#### 💡 Tips for Exploration")
    render_exploration_tips() 