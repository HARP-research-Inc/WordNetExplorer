"""
Sidebar components for WordNet Explorer.
"""

import streamlit as st
from ..config.settings import DEFAULT_SETTINGS, LAYOUT_OPTIONS
from .navigation import render_navigation_history, render_navigation_controls
from ..utils.session_state import add_to_search_history, clear_search_history


def render_word_input():
    """Render the word input field with search history."""
    # Check if a history word was selected
    selected_word = st.session_state.get('selected_history_word', None)
    
    # Word input field
    word = st.text_input(
        "Enter a word to explore", 
        value=selected_word if selected_word else (st.session_state.current_word if st.session_state.current_word else ""),
        key="word_input",
        help="Press Enter to add the word to your search history"
    ).strip().lower()
    
    # Clear the selected history word after using it
    if selected_word:
        st.session_state.selected_history_word = None
    
    # Add word to search history when entered
    if word and word != st.session_state.get('last_searched_word', ''):
        add_to_search_history(word)
        st.session_state.last_searched_word = word
    
    return word


def render_search_history():
    """Render the search history in a collapsible expander."""
    if st.session_state.search_history:
        with st.expander("🔍 Search History", expanded=False):
            st.markdown("Click any word to explore it again:")
            
            # Create columns for history items and clear button
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Display search history as clickable buttons
                for i, hist_word in enumerate(st.session_state.search_history):
                    if st.button(f"📝 {hist_word}", key=f"search_history_{i}", help=f"Click to explore '{hist_word}'"):
                        st.session_state.selected_history_word = hist_word
                        st.rerun()
            
            with col2:
                if st.button("🗑️", help="Clear search history", key="clear_search_history"):
                    clear_search_history()
                    st.rerun()


def render_basic_settings():
    """Render basic exploration settings."""
    depth = st.slider(
        "Exploration depth", 
        min_value=1, 
        max_value=3, 
        value=DEFAULT_SETTINGS['depth'], 
        help="How deep to explore relationships (higher values create larger graphs)"
    )
    return depth


def render_relationship_types():
    """Render relationship type checkboxes."""
    with st.expander("🔗 Relationship Types", expanded=True):
        show_hypernyms = st.checkbox("Include Hypernyms (↑)", value=DEFAULT_SETTINGS['show_hypernyms'])
        show_hyponyms = st.checkbox("Include Hyponyms (↓)", value=DEFAULT_SETTINGS['show_hyponyms'])
        show_meronyms = st.checkbox("Include Meronyms (⊂)", value=DEFAULT_SETTINGS['show_meronyms'])
        show_holonyms = st.checkbox("Include Holonyms (⊃)", value=DEFAULT_SETTINGS['show_holonyms'])
    
    return show_hypernyms, show_hyponyms, show_meronyms, show_holonyms


def render_graph_appearance():
    """Render graph appearance settings."""
    with st.expander("🎨 Graph Appearance"):
        # Layout options
        layout_type = st.selectbox(
            "Graph Layout",
            LAYOUT_OPTIONS,
            index=LAYOUT_OPTIONS.index(DEFAULT_SETTINGS['layout_type']),
            help="Choose how nodes are arranged in the graph"
        )
        
        # Node size settings
        node_size_multiplier = st.slider(
            "Node Size", 
            min_value=0.5, 
            max_value=2.0, 
            value=DEFAULT_SETTINGS['node_size_multiplier'], 
            step=0.1,
            help="Adjust the size of nodes in the graph"
        )
        
        # Color scheme
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Default", "Pastel", "Vibrant", "Monochrome"],
            index=["Default", "Pastel", "Vibrant", "Monochrome"].index(DEFAULT_SETTINGS['color_scheme']),
            help="Choose a color scheme for the graph"
        )
    
    return layout_type, node_size_multiplier, color_scheme


def render_physics_simulation():
    """Render physics simulation settings."""
    with st.expander("⚙️ Physics Simulation"):
        enable_physics = st.checkbox(
            "Enable Physics", 
            value=DEFAULT_SETTINGS['enable_physics'], 
            help="Allow nodes to move and settle automatically"
        )
        
        if enable_physics:
            spring_strength = st.slider(
                "Spring Strength", 
                min_value=0.01, 
                max_value=0.1, 
                value=DEFAULT_SETTINGS['spring_strength'], 
                step=0.01,
                help="How strongly nodes are pulled together"
            )
            
            central_gravity = st.slider(
                "Central Gravity", 
                min_value=0.1, 
                max_value=1.0, 
                value=DEFAULT_SETTINGS['central_gravity'], 
                step=0.1,
                help="How strongly nodes are pulled to the center"
            )
        else:
            spring_strength = DEFAULT_SETTINGS['spring_strength']
            central_gravity = DEFAULT_SETTINGS['central_gravity']
    
    return enable_physics, spring_strength, central_gravity


def render_visual_options():
    """Render visual options settings."""
    with st.expander("👁️ Visual Options"):
        show_labels = st.checkbox("Show Node Labels", value=DEFAULT_SETTINGS['show_labels'])
        show_arrows = st.checkbox("Show Directional Arrows", value=DEFAULT_SETTINGS['show_arrows'])
        edge_width = st.slider("Edge Width", min_value=1, max_value=5, value=DEFAULT_SETTINGS['edge_width'])
    
    return show_labels, show_arrows, edge_width


def render_display_options():
    """Render display options settings."""
    with st.expander("📋 Display Options", expanded=True):
        show_info = st.checkbox("Show word information", value=DEFAULT_SETTINGS['show_info'])
        show_graph = st.checkbox("Show relationship graph", value=DEFAULT_SETTINGS['show_graph'])
    
    return show_info, show_graph


def render_save_options():
    """Render save options settings."""
    with st.expander("💾 Save Options"):
        save_graph = st.checkbox("Save graph to file")
        filename = "wordnet_graph"
        if save_graph:
            filename = st.text_input("Filename (without extension)", "wordnet_graph")
            if not filename:
                filename = "wordnet_graph"
            if not filename.endswith(".html"):
                filename += ".html"
    
    return save_graph, filename


def render_about_section():
    """Render the about/help section."""
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


def render_sidebar():
    """Render the complete sidebar with all components."""
    with st.sidebar:
        st.markdown("### Settings")
        
        # Word input
        word = render_word_input()
        
        # Search history
        render_search_history()
        
        # Navigation history
        render_navigation_history()
        
        # Navigation controls
        render_navigation_controls()
        
        # Basic settings
        depth = render_basic_settings()
        
        # Relationship types
        show_hypernyms, show_hyponyms, show_meronyms, show_holonyms = render_relationship_types()
        
        # Graph appearance
        layout_type, node_size_multiplier, color_scheme = render_graph_appearance()
        
        # Physics simulation
        enable_physics, spring_strength, central_gravity = render_physics_simulation()
        
        # Visual options
        show_labels, show_arrows, edge_width = render_visual_options()
        
        # Display options
        show_info, show_graph = render_display_options()
        
        # Save options
        save_graph, filename = render_save_options()
        
        # About section
        render_about_section()
        
        return {
            'word': word,
            'depth': depth,
            'show_hypernyms': show_hypernyms,
            'show_hyponyms': show_hyponyms,
            'show_meronyms': show_meronyms,
            'show_holonyms': show_holonyms,
            'layout_type': layout_type,
            'node_size_multiplier': node_size_multiplier,
            'color_scheme': color_scheme,
            'enable_physics': enable_physics,
            'spring_strength': spring_strength,
            'central_gravity': central_gravity,
            'show_labels': show_labels,
            'show_arrows': show_arrows,
            'edge_width': edge_width,
            'show_info': show_info,
            'show_graph': show_graph,
            'save_graph': save_graph,
            'filename': filename
        } 