"""
Graph display components for WordNet Explorer.
"""

import streamlit as st
import streamlit.components.v1 as components
import os
import shutil
from src.config.settings import COLOR_SCHEMES
from src.utils.helpers import ensure_downloads_directory, validate_filename
import time

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
            <strong>Word Senses</strong> - Different meanings/synsets of the word
        </div>
        <div class="legend-item">
            <div style="width: 20px; height: 20px; background-color: {colors['word']}; border-radius: 50%; margin-right: 10px;"></div>
            <strong>Related Words</strong> - Connected through semantic relationships
        </div>
    </div>
    
    <div style="margin-top: 15px;">
        <strong>Edge Colors & Relationships:</strong>
        <div style="margin-left: 10px; margin-top: 5px;">
            <div style="margin: 3px 0;"><span style="color: #FF4444; font-weight: bold;">→</span> <strong>Hypernym</strong> - "is a type of" (more general)</div>
            <div style="margin: 3px 0;"><span style="color: #4488FF; font-weight: bold;">→</span> <strong>Hyponym</strong> - "type includes" (more specific)</div>
            <div style="margin: 3px 0;"><span style="color: #44AA44; font-weight: bold;">→</span> <strong>Meronym</strong> - "has part"</div>
            <div style="margin: 3px 0;"><span style="color: #FFAA00; font-weight: bold;">→</span> <strong>Holonym</strong> - "part of"</div>
            <div style="margin: 3px 0;"><span style="color: #666666; font-weight: bold;">→</span> <strong>Sense</strong> - connects word to its meanings</div>
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


def render_graph_visualization(word, settings, explorer=None):
    """
    Render the complete graph visualization section.
    
    Args:
        word (str): The word to visualize
        settings (dict): Dictionary containing all graph settings
        explorer: WordNetExplorer instance (optional, will create if not provided)
    """
    st.markdown('<h2 class="sub-header">Relationship Graph</h2>', unsafe_allow_html=True)
    
    # Show navigation info
    st.info("💡 **Double-click any node** to explore that concept! Your navigation history is saved above.")
    
    # Create explorer if not provided
    if explorer is None:
        from src.core import WordNetExplorer
        explorer = WordNetExplorer()
    
    with st.spinner(f"Building WordNet graph for '{word}'..."):
        # Build the graph using the new modular explorer
        G, node_labels = explorer.explore_word(
            word=word, 
            depth=settings['depth'],
            sense_number=settings.get('parsed_sense_number'),
            include_hypernyms=settings['show_hypernyms'],
            include_hyponyms=settings['show_hyponyms'],
            include_meronyms=settings['show_meronyms'],
            include_holonyms=settings['show_holonyms']
        )
        
        if G.number_of_nodes() > 0:
            st.info(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
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
                # Add navigation listener using st.markdown to ensure it runs in the top-level context
                cache_buster = int(time.time())
                
                # Intermediate Relay Iframe (receives messages from graph, navigates top window directly)
                relay_iframe_script = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Navigation Relay</title>
                    <script type="text/javascript">
                        // Relay Iframe Script v{cache_buster} - Direct Navigation
                        console.log('🔧 RelayIframe: Initializing DIRECT navigation v{cache_buster}...');
                        window.addEventListener('message', function(event) {{
                            console.log('📨 RelayIframe: Message received from graph v{cache_buster}:', event.data);
                            if (event.data && event.data.type === 'navigate') {{
                                console.log('🚀 RelayIframe: Performing DIRECT navigation v{cache_buster}');
                                const targetWord = event.data.targetWord;
                                const clickedNode = event.data.clickedNode;
                                if (targetWord) {{
                                    console.log('🔍 RelayIframe: Processing navigation v{cache_buster}:', targetWord);
                                    try {{
                                        const url = new URL(window.top.location.href);
                                        url.searchParams.set('word', targetWord);
                                        url.searchParams.set('clicked_node', clickedNode);
                                        url.searchParams.delete('navigate_to');
                                        console.log('🔗 RelayIframe: Navigating top window to v{cache_buster}:', url.toString());
                                        window.top.location.href = url.toString();
                                    }} catch (error) {{
                                        console.error('❌ RelayIframe: Navigation failed v{cache_buster}:', error);
                                    }}
                                }} else {{
                                    console.log('❌ RelayIframe: No targetWord in message v{cache_buster}');
                                }}
                            }}
                        }}, false);
                        console.log('✅ RelayIframe: DIRECT navigation listener installed v{cache_buster}. Ready for graph messages.');
                    </script>
                </head>
                <body>
                    <p>Navigation Relay Iframe - Direct Navigation Mode</p>
                </body>
                </html>
                """
                components.html(relay_iframe_script, height=0) 

                # Display the HTML content (graph) in its iframe
                components.html(html_content, height=600)
                
                # Add comprehensive legend and controls
                render_graph_legend_and_controls(G, settings)
                
                # Save the graph if requested
                if settings['save_graph']:
                    save_graph_to_file(explorer, G, node_labels, word, settings)
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


def save_graph_to_file(explorer, G, node_labels, word, settings):
    """
    Save the graph HTML file to the downloads directory.
    
    Args:
        explorer: WordNetExplorer instance
        G: NetworkX graph
        node_labels: Node labels dictionary
        word: The word being visualized
        settings: Settings dictionary containing filename and other options
    """
    downloads_dir = ensure_downloads_directory()
    validated_filename = validate_filename(settings['filename'], ".html")
    save_path = downloads_dir / validated_filename
    
    # Generate HTML and save to file
    explorer.visualize_graph(
        G, node_labels, word,
        save_path=str(save_path),
        layout_type=settings['layout_type'],
        node_size_multiplier=settings['node_size_multiplier'],
        enable_physics=settings['enable_physics'],
        spring_strength=settings['spring_strength'],
        central_gravity=settings['central_gravity'],
        show_labels=settings['show_labels'],
        edge_width=settings['edge_width'],
        color_scheme=settings['color_scheme']
    )
    
    st.success(f"Interactive graph saved to: {save_path}") 