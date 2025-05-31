"""
Comparison View Module

Handles the merged graph comparison view for multiple WordNet queries.
"""

import streamlit as st
import streamlit.components.v1 as components
import networkx as nx


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
        from ui.graph_display import render_graph_legend_and_controls
        render_graph_legend_and_controls(merged_graph, vis_settings) 