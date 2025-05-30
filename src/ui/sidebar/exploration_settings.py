"""
Exploration settings components for the sidebar.
"""

import streamlit as st
from config.settings import DEFAULT_SETTINGS
from .relationship_types import render_advanced_relationship_types


def get_url_default(session_manager, setting_key: str, default_value):
    """Get default value from URL parameters or fall back to default."""
    url_settings = session_manager.get_settings_from_url()
    return url_settings.get(setting_key, default_value)


def render_basic_settings(session_manager):
    """Render basic exploration settings."""
    depth = st.slider(
        "Exploration depth", 
        min_value=1, 
        max_value=3, 
        value=get_url_default(session_manager, 'depth', DEFAULT_SETTINGS['depth']), 
        help="How deep to explore relationships (higher values create larger graphs)"
    )
    
    # Advanced Options
    with st.expander("⚙️ Advanced Options", expanded=False):
        st.markdown("**Advanced Graph Parameters**")
        
        # Advanced depth setting (allows higher values)
        advanced_depth = st.slider(
            "Advanced Exploration Depth", 
            min_value=1, 
            max_value=10, 
            value=get_url_default(session_manager, 'advanced_depth', depth), 
            help="Higher depth values for complex exploration (warning: values above 3 may create very large graphs)"
        )
        
        # Use advanced depth if it's different from basic depth
        if advanced_depth != depth:
            depth = advanced_depth
            if advanced_depth > 3:
                st.warning(f"⚠️ Depth {advanced_depth} may create very large graphs. Consider using relationship filters to limit complexity.")
        
        # Maximum nodes limit
        max_nodes = st.number_input(
            "Maximum Nodes", 
            min_value=10, 
            max_value=1000, 
            value=get_url_default(session_manager, 'max_nodes', 100),
            step=10,
            help="Limit the total number of nodes in the graph to prevent performance issues"
        )
        
        # Branch limiting
        max_branches = st.slider(
            "Max Branches per Node",
            min_value=1,
            max_value=20,
            value=get_url_default(session_manager, 'max_branches', 5),
            help="Maximum number of related concepts to show for each node"
        )
        
        # Node filtering options
        st.markdown("**Node Filtering**")
        
        # Minimum frequency threshold
        min_frequency = st.slider(
            "Minimum Word Frequency",
            min_value=0,
            max_value=100,
            value=get_url_default(session_manager, 'min_frequency', 0),
            help="Filter out rare words (0 = no filtering). Higher values show only common words."
        )
        
        # Show only certain POS types
        pos_filter = st.multiselect(
            "Part-of-Speech Filter",
            options=["Nouns", "Verbs", "Adjectives", "Adverbs"],
            default=get_url_default(session_manager, 'pos_filter', ["Nouns", "Verbs", "Adjectives", "Adverbs"]),
            help="Show only specific parts of speech"
        )
        
        # Performance settings
        st.markdown("**Performance Settings**")
        
        # Enable/disable heavy computations
        enable_clustering = st.checkbox(
            "Enable Node Clustering",
            value=get_url_default(session_manager, 'enable_clustering', False),
            help="Group related nodes together (may slow down large graphs)"
        )
        
        # Cross-connections option
        enable_cross_connections = st.checkbox(
            "Enable Cross-Connections",
            value=get_url_default(session_manager, 'enable_cross_connections', True),
            help="Find and display relationships between existing nodes (creates richer graphs but may be slower)"
        )
        
        # Simplified mode for large graphs
        simplified_mode = st.checkbox(
            "Simplified Mode",
            value=get_url_default(session_manager, 'simplified_mode', False),
            help="Use simplified rendering for better performance with large graphs"
        )
        
        # Add detailed relationship types in advanced options
        st.markdown("---")
        st.markdown("**Detailed Relationship Types**")
        st.markdown("Fine-tune specific WordNet edge types (overrides basic relationship selections above):")
        
        # Get basic relationship settings from main section
        basic_relationships = st.session_state.get('basic_relationships', {})
        
        # Render advanced relationship controls
        advanced_relationship_settings = render_advanced_relationship_types(session_manager, basic_relationships)
        
        # Return all advanced settings as a dictionary
        advanced_settings = {
            'max_nodes': max_nodes,
            'max_branches': max_branches,
            'min_frequency': min_frequency,
            'pos_filter': pos_filter,
            'enable_clustering': enable_clustering,
            'enable_cross_connections': enable_cross_connections,
            'simplified_mode': simplified_mode
        }
        
        # Include advanced relationship settings
        advanced_settings.update(advanced_relationship_settings)
        
    return depth, advanced_settings 