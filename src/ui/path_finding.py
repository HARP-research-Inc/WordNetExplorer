"""
Path Finding View Module

Handles finding and visualizing paths between WordNet synsets.
"""

import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
from nltk.corpus import wordnet as wn


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
        
        # Build and visualize the path
        path_graph, path_labels = _build_path_graph(best_path['path'])
        
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
        
        # Show path relationship legend
        _render_path_legend()
        
        # Show alternative paths if any
        if len(all_paths) > 1:
            _render_alternative_paths(all_paths)
        
    except Exception as e:
        st.error(f"Error finding path: {e}")
        import traceback
        st.code(traceback.format_exc())


def _build_path_graph(path):
    """Build a graph representation of a synset path."""
    path_graph = nx.DiGraph()
    path_labels = {}
    
    # Add nodes and edges for the path
    for i, synset in enumerate(path):
        node_id = synset.name()
        path_graph.add_node(node_id)
        
        # Set node attributes
        if i == 0:
            path_graph.nodes[node_id]['node_type'] = 'main'
            path_graph.nodes[node_id]['title'] = f"START: {synset.definition()}"
        elif i == len(path) - 1:
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
            prev_synset = path[i-1]
            relationship_type, edge_color, edge_title = _determine_relationship(prev_synset, synset)
            
            path_graph.add_edge(prev_synset.name(), node_id)
            path_graph.edges[prev_synset.name(), node_id]['relationship'] = relationship_type
            path_graph.edges[prev_synset.name(), node_id]['color'] = edge_color
            path_graph.edges[prev_synset.name(), node_id]['title'] = edge_title
    
    return path_graph, path_labels


def _determine_relationship(prev_synset, synset):
    """Determine the relationship type between two synsets."""
    relationship_type = 'path'  # Default to generic path relationship
    edge_color = '#888888'
    
    # Check if current is hypernym of previous (generalization)
    if synset in prev_synset.hypernyms():
        relationship_type = 'hypernym'
        edge_color = '#FF4444'
    # Check if current is hyponym of previous (specialization)
    elif synset in prev_synset.hyponyms():
        relationship_type = 'hyponym'
        edge_color = '#4488FF'
    # Check if previous is hypernym of current (reverse check)
    elif prev_synset in synset.hypernyms():
        relationship_type = 'hyponym'  # From perspective of edge direction
        edge_color = '#4488FF'
    # Check if previous is hyponym of current (reverse check)
    elif prev_synset in synset.hyponyms():
        relationship_type = 'hypernym'  # From perspective of edge direction
        edge_color = '#FF4444'
    # Check if they are sister terms (share a hypernym)
    else:
        prev_hypernyms = set(prev_synset.hypernyms())
        curr_hypernyms = set(synset.hypernyms())
        common_hypernyms = prev_hypernyms & curr_hypernyms
        
        if common_hypernyms:
            relationship_type = 'sister_term'
            edge_color = '#AA44AA'
            # Get the most specific common hypernym for the edge title
            common_hypernym = list(common_hypernyms)[0]
            common_name = ', '.join(common_hypernym.lemma_names()[:2])
            edge_title = f"{relationship_type} (via {common_name})"
            return relationship_type, edge_color, edge_title
        # Check for meronym relationships
        elif synset in prev_synset.part_meronyms() or synset in prev_synset.substance_meronyms() or synset in prev_synset.member_meronyms():
            relationship_type = 'meronym'
            edge_color = '#44AA44'
        elif prev_synset in synset.part_meronyms() or prev_synset in synset.substance_meronyms() or prev_synset in synset.member_meronyms():
            relationship_type = 'holonym'  # Reverse of meronym
            edge_color = '#FFAA00'
        # Check for holonym relationships
        elif synset in prev_synset.part_holonyms() or synset in prev_synset.substance_holonyms() or synset in prev_synset.member_holonyms():
            relationship_type = 'holonym'
            edge_color = '#FFAA00'
        elif prev_synset in synset.part_holonyms() or prev_synset in synset.substance_holonyms() or prev_synset in synset.member_holonyms():
            relationship_type = 'meronym'  # Reverse of holonym
            edge_color = '#44AA44'
        # Check for other relationships
        elif synset in prev_synset.similar_tos():
            relationship_type = 'similar_to'
            edge_color = '#9999FF'
        elif synset in prev_synset.also_sees():
            relationship_type = 'also_see'
            edge_color = '#FF9999'
    
    # Create edge title
    edge_title = relationship_type.replace('_', ' ').title()
    
    return relationship_type, edge_color, edge_title


def _render_path_legend():
    """Render the legend for path relationship types."""
    st.markdown("#### Path Relationship Types")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **Hypernym** (🔴): More general concept
        - **Hyponym** (🔵): More specific concept  
        - **Sister Term** (🟣): Share common parent
        - **Meronym** (🟢): Part of
        """)
    
    with col2:
        st.markdown("""
        - **Holonym** (🟠): Has as part
        - **Similar To** (🔷): Similar meaning
        - **Also See** (🔶): Related concept
        - **Path** (⚫): Generic connection
        """)


def _render_alternative_paths(all_paths):
    """Render alternative paths in an expander."""
    with st.expander(f"Alternative paths ({len(all_paths) - 1} more)"):
        for i, path_info in enumerate(all_paths[1:], 1):
            st.write(f"**Path {i+1}** ({path_info['length']} steps):")
            st.write(f"{path_info['from'].name()} → ... → {path_info['to'].name()}")
            path_str = " → ".join([s.name() for s in path_info['path']])
            st.code(path_str, language=None) 