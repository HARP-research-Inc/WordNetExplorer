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


def prepare_download_content(explorer, G, node_labels, word, settings):
    """
    Prepare download content for HTML and JSON based on button clicks.
    
    Args:
        explorer: WordNetExplorer instance
        G: NetworkX graph
        node_labels: Node labels dictionary
        word: The word being visualized
        settings: Settings dictionary containing download options
    
    Returns:
        tuple: (html_content, json_content) where content is None if not requested
    """
    html_content = None
    json_content = None
    
    # Prepare HTML content if button was clicked
    if settings.get('save_html_button'):
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
    
    # Prepare JSON content if button was clicked
    if settings.get('export_json_button'):
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
        
        # Get JSON string
        json_content = serializer.serialize_graph(G, node_labels, metadata)
    
    return html_content, json_content


def render_graph_visualization(word, settings, explorer=None, synset_search_mode=False):
    """
    Render the complete graph visualization section.
    
    Args:
        word (str): The word to visualize (or synset name if in synset mode)
        settings (dict): Dictionary containing all graph settings
        explorer: WordNetExplorer instance (optional, will create if not provided)
        synset_search_mode (bool): Whether we're searching by synset instead of word
    """
    st.markdown('<h2 class="sub-header">Relationship Graph</h2>', unsafe_allow_html=True)
    
    # Check for imported graph
    if 'imported_graph' in st.session_state:
        G, node_labels, metadata = st.session_state.imported_graph
        st.info("📥 Using imported graph data")
        
        # Apply visualization settings from metadata if available
        if 'visualization_config' in metadata:
            vis_config = metadata['visualization_config']
            settings.update({
                'layout_type': vis_config.get('layout_type', settings['layout_type']),
                'node_size_multiplier': vis_config.get('node_size_multiplier', settings['node_size_multiplier']),
                'enable_physics': vis_config.get('enable_physics', settings['enable_physics']),
                'spring_strength': vis_config.get('spring_strength', settings['spring_strength']),
                'central_gravity': vis_config.get('central_gravity', settings['central_gravity']),
                'show_labels': vis_config.get('show_labels', settings['show_labels']),
                'edge_width': vis_config.get('edge_width', settings['edge_width']),
                'color_scheme': vis_config.get('color_scheme', settings['color_scheme'])
            })
    else:
        # Show navigation info - different message for synset mode
        if synset_search_mode:
            st.info(f"💡 **Synset Mode**: Exploring synset `{word}` and its word senses. **Double-click any node** to explore further!")
        else:
            st.info("💡 **Double-click any node** to explore that concept! Your navigation history is saved above.")
        
        # Create explorer if not provided
        if explorer is None:
            from src.core import WordNetExplorer
            explorer = WordNetExplorer()
        
        if synset_search_mode:
            with st.spinner(f"Building WordNet graph for synset '{word}'..."):
                # Build synset-focused graph - pass all relationship settings and advanced settings
                G, node_labels = explorer.explore_synset(
                    synset_name=word, 
                    depth=settings['depth'],
                    max_nodes=settings.get('max_nodes', 100),
                    max_branches=settings.get('max_branches', 5),
                    min_frequency=settings.get('min_frequency', 0),
                    pos_filter=settings.get('pos_filter', ["Nouns", "Verbs", "Adjectives", "Adverbs"]),
                    enable_clustering=settings.get('enable_clustering', False),
                    enable_cross_connections=settings.get('enable_cross_connections', True),
                    simplified_mode=settings.get('simplified_mode', False),
                    **{k: v for k, v in settings.items() if k.startswith('show_')}
                )
        else:
            with st.spinner(f"Building WordNet graph for '{word}'..."):
                # Build the graph using the new modular explorer - pass all relationship settings and advanced settings
                G, node_labels = explorer.explore_word(
                    word=word, 
                    depth=settings['depth'],
                    sense_number=settings.get('parsed_sense_number'),
                    max_nodes=settings.get('max_nodes', 100),
                    max_branches=settings.get('max_branches', 5),
                    min_frequency=settings.get('min_frequency', 0),
                    pos_filter=settings.get('pos_filter', ["Nouns", "Verbs", "Adjectives", "Adverbs"]),
                    enable_clustering=settings.get('enable_clustering', False),
                    enable_cross_connections=settings.get('enable_cross_connections', True),
                    simplified_mode=settings.get('simplified_mode', False),
                    **{k: v for k, v in settings.items() if k.startswith('show_')}
                )
    
    if G.number_of_nodes() > 0:
        st.info(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Generate the interactive graph for display
        display_html = explorer.visualize_graph(
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
        
        if display_html:
            # Display the HTML content directly
            components.html(display_html, height=600)
            
            # Add comprehensive legend and controls
            render_graph_legend_and_controls(G, settings, synset_search_mode)
            
            # Handle downloads if buttons were clicked
            download_html, download_json = prepare_download_content(explorer, G, node_labels, word, settings)
            
            # Show download buttons if content is ready
            if download_html:
                st.download_button(
                    label="📥 Download HTML",
                    data=download_html,
                    file_name=settings.get('html_filename', f"{word}_graph.html"),
                    mime="text/html",
                    help="Download the interactive graph as an HTML file"
                )
            
            if download_json:
                st.download_button(
                    label="📥 Download JSON", 
                    data=download_json,
                    file_name=settings.get('json_filename', f"{word}_graph.json"),
                    mime="application/json",
                    help="Download the graph data as a JSON file"
                )
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