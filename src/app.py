#!/usr/bin/env python3
"""
WordNet Explorer - Streamlit UI (Refactored Modular Version)

A web-based interface for exploring WordNet semantic relationships
using Streamlit with a clean, modular architecture.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import warnings
import networkx as nx

# Suppress specific Streamlit warnings more comprehensively
warnings.filterwarnings("ignore", message=".*was created with a default value but also had its value set via the Session State API.*")
warnings.filterwarnings("ignore", message=".*widget.*default value.*Session State API.*")
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

# Add parent directory to path to allow imports (works for both local and deployment)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import configuration
from config.settings import PAGE_CONFIG

# Import core modules
from core import WordNetExplorer, SessionManager

# Import UI components
from ui.styles import load_custom_css
from ui.sidebar import render_sidebar
from ui.word_info import render_word_information
from ui.graph_display import render_graph_visualization, render_graph_legend_and_controls
from ui.welcome import render_welcome_screen

# Import enhanced history functionality
from utils.session_state import add_query_to_history, initialize_session_state


def render_header():
    """Render the header with title."""
    # App title and description
    st.markdown('<h1 class="main-header">WordNet Explorer</h1>', unsafe_allow_html=True)
    st.markdown("Explore semantic relationships between words using WordNet")


def render_footer():
    """Render the footer with logo, copyright and link."""
    st.markdown("---")
    
    # Display logo using HTML for full control
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "T-Shirt Logo.png")
        if os.path.exists(logo_path):
            import base64
            
            # Read and encode the image
            with open(logo_path, "rb") as img_file:
                img_bytes = img_file.read()
                img_base64 = base64.b64encode(img_bytes).decode()
            
            # Display using HTML with full control
            st.markdown(
                f"""
                <div style="text-align: center; padding: 20px 0;">
                    <img src="data:image/png;base64,{img_base64}" 
                         style="width: 300px; 
                                border-radius: 0px !important; 
                                border: none !important;
                                box-shadow: none !important;
                                display: block;
                                margin: 0 auto;" 
                         alt="HARP Research Logo">
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception as e:
        # If logo fails to load, just continue without it
        st.markdown('<div style="text-align: center; padding: 20px 0;"></div>', unsafe_allow_html=True)
    
    # Get WordNet version information
    try:
        from nltk.corpus import wordnet as wn
        import nltk
        
        # Try to get WordNet version info
        try:
            # Check if we can access WordNet info
            wn.synsets('test')  # Test access
            wordnet_version = "WordNet 3.0"  # Default assumption for NLTK
            
            # Try to get more specific version info if available
            try:
                # Some NLTK installations have version info
                if hasattr(wn, '_LazyCorpusLoader__args'):
                    wordnet_version = "WordNet 3.0 (NLTK)"
                else:
                    wordnet_version = "WordNet 3.0 (NLTK)"
            except:
                wordnet_version = "WordNet 3.0"
                
        except:
            wordnet_version = "WordNet (version unavailable)"
            
        nltk_version = nltk.__version__
        version_info = f"Powered by {wordnet_version} via NLTK {nltk_version}"
        
    except Exception:
        version_info = "Powered by WordNet via NLTK"
    
    # Copyright, version info, and link
    st.markdown(
        f"""
        <div style="text-align: center; padding: 10px 0; color: #666; font-size: 14px;">
            <p style="margin: 5px 0;">{version_info}</p>
            <p style="margin: 5px 0;">© 2025 HARP Research, Inc. | <a href="https://harpresearch.ai" target="_blank" style="color: #1f77b4; text-decoration: none;">https://harpresearch.ai</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    """Main application function."""
    # Set page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize session state for enhanced history
    initialize_session_state()
    
    # Initialize core components
    session_manager = SessionManager()
    explorer = WordNetExplorer()
    
    # Load custom CSS
    load_custom_css()
    
    # Render header with logo
    render_header()
    
    # Check if we're in comparison mode
    compare_mode = st.session_state.get('compare_mode', False)
    path_finding_mode = st.session_state.get('path_finding_mode', False)
    
    if path_finding_mode:
        # Path finding mode
        render_path_finding_view(explorer)
    elif compare_mode:
        # Comparison mode - render merged graph
        render_comparison_view(explorer)
    else:
        # Normal mode - single graph view
        # Handle URL navigation
        session_manager.handle_url_navigation()
        
        # Render sidebar and get settings
        settings = render_sidebar(session_manager)
        
        # Determine the current word to display
        current_display_word = settings.get('word') or session_manager.get_current_word()
        
        # Debug logging
        print(f"🔍 APP: current_display_word='{current_display_word}', settings_word='{settings.get('word')}', current_word='{session_manager.get_current_word()}'")
        print(f"🔍 APP: word_changed={settings.get('word_changed', False)}, parsed_sense={settings.get('parsed_sense_number')}")
        
        # Check if this is a new query that should be added to history
        # This happens when word_changed is True OR when we have a word that's being displayed
        should_add_to_history = False
        
        # Update session state if this is a new word from input
        if settings.get('word') and settings['word'] != session_manager.get_current_word():
            # Update session state without modifying the widget
            st.session_state.current_word = settings['word']
            st.session_state.last_searched_word = settings['word']
            session_manager.add_to_history(settings['word'])
            should_add_to_history = True
            current_display_word = settings['word']
            print(f"🔍 APP: New word detected, should_add_to_history=True")
        
        # Also add to history if word_changed flag is set (user pressed Enter)
        if settings.get('word_changed', False) and settings.get('word'):
            should_add_to_history = True
            print(f"🔍 APP: word_changed flag set, should_add_to_history=True")
        
        print(f"🔍 APP: Final should_add_to_history={should_add_to_history}")
        
        # Main content area
        if current_display_word:
            try:
                # Check if we're in synset search mode
                synset_search_mode = settings.get('synset_search_mode', False)
                display_input = current_display_word
                
                # If in synset search mode, convert word+sense to synset name
                if synset_search_mode and settings.get('parsed_sense_number'):
                    from wordnet import get_synsets_for_word
                    synsets = get_synsets_for_word(current_display_word)
                    sense_number = settings['parsed_sense_number']
                    if synsets and 1 <= sense_number <= len(synsets):
                        # Use the synset name instead of the word
                        display_input = synsets[sense_number - 1].name()
                    else:
                        st.error(f"Invalid sense number {sense_number} for word '{current_display_word}'")
                        synset_search_mode = False  # Fall back to word mode
                
                # Add complete query to enhanced history if needed
                if should_add_to_history:
                    print(f"🔍 APP: Calling add_query_to_history with settings")
                    add_query_to_history(settings)
                else:
                    print(f"🔍 APP: NOT calling add_query_to_history")
                    # Fallback: If we're displaying a word but it's not in history, add it
                    from utils.session_state import get_search_history_manager
                    from src.models.search_history import SearchQuery
                    
                    history_manager = get_search_history_manager()
                    current_query = SearchQuery.from_settings(settings)
                    
                    # Check if this exact query exists in history
                    query_exists = any(q.get_hash() == current_query.get_hash() for q in history_manager.queries)
                    
                    if not query_exists and current_display_word:
                        print(f"🔍 APP: Query not in history, adding as fallback")
                        add_query_to_history(settings)
                
                # Show word information if requested (not applicable in synset mode)
                if settings.get('show_info', False) and not synset_search_mode:
                    render_word_information(current_display_word)
                
                # Build and display graph if requested
                if settings.get('show_graph', True):
                    render_graph_visualization(display_input, settings, explorer, synset_search_mode)
            
            except Exception as e:
                st.error(f"Error: {e}")
                if settings.get('synset_search_mode', False):
                    st.error("Please check that you have entered a valid synset name (e.g., 'dog.n.01').")
                else:
                    st.error("Please check that you have entered a valid English word.")
        
        else:
            # Show welcome screen
            render_welcome_screen()
    
    # Display debug information if enabled
    session_manager.log_debug_info()
    
    # Render footer
    render_footer()


def render_comparison_view(explorer):
    """Render comparison view with merged graph."""
    st.sidebar.markdown("## 📊 Comparison Mode")
    
    # Exit comparison mode button
    if st.sidebar.button("← Back to Single View", key="exit_compare", type="primary"):
        st.session_state.compare_mode = False
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Get selected queries
    from utils.session_state import get_search_history_manager
    from src.models.search_history import SearchQuery
    
    history_manager = get_search_history_manager()
    selected_hashes = st.session_state.get('selected_queries_for_comparison', set())
    
    # Find the actual query objects
    selected_queries = []
    for query in history_manager.queries:
        if query.get_hash() in selected_hashes:
            selected_queries.append(query)
    
    if not selected_queries:
        st.warning("No queries selected for comparison. Please go back and select some queries.")
        return
    
    st.markdown(f"### Comparing {len(selected_queries)} Word Graphs (Merged View)")
    
    # Show what's being compared
    comparison_info = "**Comparing:** " + " | ".join([q.get_display_label() for q in selected_queries])
    st.info(comparison_info)
    
    # Create a merged graph
    merged_graph = nx.DiGraph()
    merged_node_labels = {}
    
    # Track which queries contributed to each node
    node_sources = {}  # node_id -> set of query labels
    
    # Build each individual graph and merge
    with st.spinner("Building and merging graphs..."):
        for query in selected_queries:
            # Restore settings from query
            from utils.session_state import restore_query_settings
            settings = restore_query_settings(query)
            
            # Determine display input
            display_input = query.word
            synset_search_mode = query.synset_search_mode
            
            if synset_search_mode and query.sense_number:
                from wordnet import get_synsets_for_word
                synsets = get_synsets_for_word(query.word)
                if synsets and 1 <= query.sense_number <= len(synsets):
                    display_input = synsets[query.sense_number - 1].name()
            
            try:
                # Build individual graph
                if synset_search_mode:
                    G, node_labels = explorer.explore_synset(
                        synset_name=display_input,
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
                    G, node_labels = explorer.explore_word(
                        word=query.word,
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
                
                # Merge into the combined graph
                query_label = query.get_short_label()
                
                # Add nodes
                for node in G.nodes():
                    if node not in merged_graph:
                        merged_graph.add_node(node)
                        # Copy all node attributes
                        for attr, value in G.nodes[node].items():
                            merged_graph.nodes[node][attr] = value
                        merged_node_labels[node] = node_labels.get(node, node)
                        node_sources[node] = {query_label}
                    else:
                        # Node already exists - track that this query also has it
                        node_sources[node].add(query_label)
                        # Update node type to show it's shared
                        if 'node_type' in merged_graph.nodes[node]:
                            if merged_graph.nodes[node]['node_type'] != 'main':
                                merged_graph.nodes[node]['node_type'] = 'shared'
                
                # Add edges
                for u, v in G.edges():
                    if not merged_graph.has_edge(u, v):
                        merged_graph.add_edge(u, v)
                        # Copy all edge attributes
                        for attr, value in G.edges[u, v].items():
                            merged_graph[u][v][attr] = value
                    else:
                        # Edge already exists - could update attributes if needed
                        pass
                
            except Exception as e:
                st.error(f"Error processing graph for {query.get_display_label()}: {e}")
    
    # Add source information to node labels
    for node, sources in node_sources.items():
        if len(sources) > 1:
            # Node appears in multiple queries
            merged_node_labels[node] = f"{merged_node_labels[node]} [{', '.join(sorted(sources))}]"
    
    # Display the merged graph
    st.info(f"Merged graph contains {merged_graph.number_of_nodes()} nodes and {merged_graph.number_of_edges()} edges")
    
    # Use the first query's visualization settings as defaults
    if selected_queries:
        from utils.session_state import restore_query_settings
        vis_settings = restore_query_settings(selected_queries[0])
    else:
        vis_settings = {}
    
    # Ensure default values for visualization settings
    vis_settings.setdefault('color_scheme', 'Default')
    vis_settings.setdefault('layout_type', 'force')
    vis_settings.setdefault('node_size_multiplier', 1.0)
    vis_settings.setdefault('enable_physics', True)
    vis_settings.setdefault('spring_strength', 0.005)
    vis_settings.setdefault('central_gravity', 0.3)
    vis_settings.setdefault('show_labels', True)
    vis_settings.setdefault('edge_width', 1)
    
    # Render the merged graph
    display_html = explorer.visualize_graph(
        merged_graph, 
        merged_node_labels, 
        "Comparison Graph",
        save_path=None,
        layout_type=vis_settings.get('layout_type', 'force'),
        node_size_multiplier=vis_settings.get('node_size_multiplier', 1.0),
        enable_physics=vis_settings.get('enable_physics', True),
        spring_strength=vis_settings.get('spring_strength', 0.005),
        central_gravity=vis_settings.get('central_gravity', 0.3),
        show_labels=vis_settings.get('show_labels', True),
        edge_width=vis_settings.get('edge_width', 1),
        color_scheme=vis_settings.get('color_scheme', 'Default')
    )
    
    if display_html:
        # Display the HTML content directly
        components.html(display_html, height=600, scrolling=True)
        
        # Show legend and controls
        render_graph_legend_and_controls(merged_graph, vis_settings)


def render_path_finding_view(explorer):
    """Render path finding view between two word senses."""
    st.sidebar.markdown("## 🛤️ Path Finding Mode")
    
    # Exit path finding mode button
    if st.sidebar.button("← Back to Single View", key="exit_path_finding", type="primary"):
        st.session_state.path_finding_mode = False
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Get path endpoints
    path_from = st.session_state.get('path_from', {})
    path_to = st.session_state.get('path_to', {})
    
    if not path_from or not path_to:
        st.warning("Please specify both source and target words.")
        return
    
    from_word = path_from.get('word', '')
    from_sense = path_from.get('sense', 1)
    to_word = path_to.get('word', '')
    to_sense = path_to.get('sense', 1)
    
    st.markdown(f"### Finding Path: {from_word}.{from_sense if from_sense > 0 else 'all'} → {to_word}.{to_sense if to_sense > 0 else 'all'}")
    
    try:
        # Import WordNet functions
        from wordnet import get_synsets_for_word
        from nltk.corpus import wordnet as wn
        
        # Get synsets for both words
        from_synsets = get_synsets_for_word(from_word)
        to_synsets = get_synsets_for_word(to_word)
        
        if not from_synsets:
            st.error(f"No WordNet entries found for '{from_word}'")
            return
        if not to_synsets:
            st.error(f"No WordNet entries found for '{to_word}'")
            return
        
        # Select specific synsets or use all
        if from_sense > 0 and from_sense <= len(from_synsets):
            from_synsets = [from_synsets[from_sense - 1]]
        elif from_sense > len(from_synsets):
            st.error(f"'{from_word}' only has {len(from_synsets)} senses")
            return
            
        if to_sense > 0 and to_sense <= len(to_synsets):
            to_synsets = [to_synsets[to_sense - 1]]
        elif to_sense > len(to_synsets):
            st.error(f"'{to_word}' only has {len(to_synsets)} senses")
            return
        
        # Try to find paths between all combinations
        all_paths = []
        
        with st.spinner("Searching for paths..."):
            for from_synset in from_synsets:
                for to_synset in to_synsets:
                    # Find path using hypernym relationships
                    path = explorer.find_path_between_synsets(from_synset, to_synset)
                    if path:
                        all_paths.append({
                            'from': from_synset,
                            'to': to_synset,
                            'path': path,
                            'length': len(path)
                        })
        
        if not all_paths:
            st.warning("No path found between the specified word senses.")
            st.info("Try using hypernym relationships or broader senses.")
            return
        
        # Sort paths by length
        all_paths.sort(key=lambda x: x['length'])
        
        # Display the shortest path
        best_path = all_paths[0]
        st.success(f"Found {len(all_paths)} path(s)! Showing the shortest path ({best_path['length']} steps):")
        
        # Build a graph for the path
        path_graph = nx.DiGraph()
        path_labels = {}
        
        # Add nodes and edges for the path
        for i, synset in enumerate(best_path['path']):
            node_id = synset.name()
            path_graph.add_node(node_id)
            
            # Set node attributes
            if i == 0:
                path_graph.nodes[node_id]['node_type'] = 'main'
                path_graph.nodes[node_id]['title'] = f"START: {synset.definition()}"
            elif i == len(best_path['path']) - 1:
                path_graph.nodes[node_id]['node_type'] = 'main'
                path_graph.nodes[node_id]['title'] = f"END: {synset.definition()}"
            else:
                path_graph.nodes[node_id]['node_type'] = 'synset'
                path_graph.nodes[node_id]['title'] = synset.definition()
            
            path_graph.nodes[node_id]['pos'] = synset.pos()
            
            # Add label
            lemmas = ', '.join([l.name() for l in synset.lemmas()[:3]])
            path_labels[node_id] = f"{lemmas}\n({synset.name()})"
            
            # Add edge to previous node
            if i > 0:
                prev_synset = best_path['path'][i-1]
                path_graph.add_edge(prev_synset.name(), node_id)
                path_graph.edges[prev_synset.name(), node_id]['relationship'] = 'path'
                path_graph.edges[prev_synset.name(), node_id]['color'] = '#FF4444'
        
        # Display the path graph
        st.info(f"Path visualization: {best_path['length']} nodes connected")
        
        # Generate visualization
        display_html = explorer.visualize_graph(
            path_graph,
            path_labels,
            f"Path: {from_word} → {to_word}",
            save_path=None,
            layout_type='hierarchical',  # Use hierarchical for clear path display
            node_size_multiplier=1.5,
            enable_physics=False,  # Disable physics for static path
            show_labels=True,
            edge_width=3,
            color_scheme='Default'
        )
        
        if display_html:
            components.html(display_html, height=600, scrolling=True)
        
        # Show alternative paths if any
        if len(all_paths) > 1:
            with st.expander(f"Alternative paths ({len(all_paths) - 1} more)"):
                for i, path_info in enumerate(all_paths[1:], 1):
                    st.write(f"**Path {i+1}** ({path_info['length']} steps):")
                    st.write(f"{path_info['from'].name()} → ... → {path_info['to'].name()}")
                    path_str = " → ".join([s.name() for s in path_info['path']])
                    st.code(path_str, language=None)
        
    except Exception as e:
        st.error(f"Error finding path: {e}")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main() 