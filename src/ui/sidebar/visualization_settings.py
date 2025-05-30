"""
Visualization settings components for the sidebar.
"""

import streamlit as st
from config.settings import DEFAULT_SETTINGS, LAYOUT_OPTIONS


def get_url_default(session_manager, setting_key: str, default_value):
    """Get default value from URL parameters or fall back to default."""
    url_settings = session_manager.get_settings_from_url()
    return url_settings.get(setting_key, default_value)


def render_graph_appearance(session_manager):
    """Render graph appearance settings."""
    st.markdown("### 🎨 Graph Appearance")
    
    # Layout selection
    default_layout = get_url_default(session_manager, 'layout_type', DEFAULT_SETTINGS['layout_type'])
    # Handle the case where the default might not be in the list
    default_index = 0
    if default_layout in LAYOUT_OPTIONS:
        default_index = LAYOUT_OPTIONS.index(default_layout)
    
    st.selectbox(
        "Graph layout",
        options=LAYOUT_OPTIONS,
        index=default_index,
        key="layout_type",
        help="Choose how nodes are arranged in the graph"
    )
    
    # Node size
    st.slider(
        "Node size",
        min_value=0.5,
        max_value=2.0,
        value=get_url_default(session_manager, 'node_size_multiplier', DEFAULT_SETTINGS['node_size_multiplier']),
        step=0.1,
        key="node_size_multiplier",
        help="Adjust the size of nodes in the graph"
    )
    
    # Edge width
    st.slider(
        "Edge width",
        min_value=1,
        max_value=5,
        value=get_url_default(session_manager, 'edge_width', DEFAULT_SETTINGS['edge_width']),
        key="edge_width",
        help="Adjust the thickness of connections between nodes"
    )
    
    # Color scheme
    color_schemes = ["Default", "Pastel", "Vibrant", "Monochrome"]
    st.selectbox(
        "Color scheme",
        options=color_schemes,
        index=color_schemes.index(get_url_default(session_manager, 'color_scheme', DEFAULT_SETTINGS['color_scheme'])),
        key="color_scheme",
        help="Choose a color palette for the graph"
    )
    
    # Show labels
    st.checkbox(
        "Show node labels",
        value=get_url_default(session_manager, 'show_labels', DEFAULT_SETTINGS['show_labels']),
        key="show_labels",
        help="Display text labels on nodes"
    )


def render_physics_simulation(session_manager):
    """Render physics simulation settings."""
    st.markdown("### ⚙️ Physics Simulation")
    
    # Physics enabled
    enable_physics = st.checkbox(
        "Enable physics simulation",
        value=get_url_default(session_manager, 'enable_physics', DEFAULT_SETTINGS['enable_physics']),
        key="enable_physics",
        help="Allow nodes to move and settle into position"
    )
    
    if enable_physics:
        # Spring strength
        st.slider(
            "Spring strength",
            min_value=0.001,
            max_value=0.1,
            value=get_url_default(session_manager, 'spring_strength', DEFAULT_SETTINGS['spring_strength']),
            step=0.001,
            format="%.3f",
            key="spring_strength",
            help="How strongly connected nodes attract each other"
        )
        
        # Central gravity
        st.slider(
            "Central gravity",
            min_value=0.0,
            max_value=1.0,
            value=get_url_default(session_manager, 'central_gravity', DEFAULT_SETTINGS['central_gravity']),
            step=0.05,
            key="central_gravity",
            help="How strongly nodes are pulled toward the center"
        )


def render_visual_options(session_manager):
    """Render both graph appearance and physics settings."""
    render_graph_appearance(session_manager)
    render_physics_simulation(session_manager)


def render_display_options(session_manager):
    """Render display options for showing/hiding elements."""
    show_info = st.checkbox(
        "📊 Show word information", 
        value=get_url_default(session_manager, 'show_info', False),
        help="Display detailed information about the word"
    )
    
    show_graph = st.checkbox(
        "🕸️ Show relationship graph", 
        value=get_url_default(session_manager, 'show_graph', True),
        help="Display the visual graph of word relationships"
    )
    
    return show_info, show_graph 