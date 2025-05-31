"""
Main sidebar component that orchestrates all sidebar sections.
"""

import streamlit as st
from .word_input import render_word_input, render_search_history
from .relationship_types import render_relationship_types
from .exploration_settings import render_basic_settings
from .visualization_settings import render_visual_options, render_display_options
from .about import render_about_section

# Fix import path - need to go up to src directory
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from utils.session_state import restore_query_settings


def render_sidebar(session_manager):
    """
    Render the complete sidebar with all sections.
    
    Args:
        session_manager: SessionManager instance for URL handling
    
    Returns:
        dict: Dictionary containing all settings
    """
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">🔤 Word Explorer</h2>', unsafe_allow_html=True)
        
        # Initialize settings dictionary
        settings = {}
        
        # Check if a query was selected from history
        selected_query = st.session_state.get('selected_history_query', None)
        if selected_query:
            # Restore settings from the selected query
            restored_settings = restore_query_settings(selected_query)
            
            # Update session state with restored settings for various widgets
            for key, value in restored_settings.items():
                if key in ['depth', 'max_nodes', 'max_branches', 'min_frequency', 
                          'enable_clustering', 'enable_cross_connections', 
                          'simplified_mode', 'pos_filter']:
                    st.session_state[key] = value
        
        # Word input section
        word, parsed_sense_number, word_changed, synset_search_mode = render_word_input(session_manager)
        settings['word'] = word
        settings['parsed_sense_number'] = parsed_sense_number
        settings['word_changed'] = word_changed
        settings['synset_search_mode'] = synset_search_mode
        
        # Path Finding section
        with st.expander("🛤️ Path Finder", expanded=False):
            st.markdown("Find a path between two word senses:")
            
            st.markdown("**From:**")
            from_word = st.text_input("From word", placeholder="e.g., cat", key="path_from_word", label_visibility="collapsed")
            from_sense = st.number_input("From sense number", min_value=0, value=1, key="path_from_sense", help="0 for all senses")
            
            st.markdown("**To:**")
            to_word = st.text_input("To word", placeholder="e.g., dog", key="path_to_word", label_visibility="collapsed")
            to_sense = st.number_input("To sense number", min_value=0, value=1, key="path_to_sense", help="0 for all senses")
            
            if st.button("🔍 Find Path", key="find_path", type="primary", disabled=not (from_word and to_word)):
                st.session_state.path_finding_mode = True
                st.session_state.path_from = {'word': from_word.strip().lower(), 'sense': from_sense}
                st.session_state.path_to = {'word': to_word.strip().lower(), 'sense': to_sense}
                st.rerun()
        
        st.markdown("---")
        
        # Search history section
        render_search_history()
        
        st.markdown("---")
        
        # Relationship types section
        basic_relationships = render_relationship_types(session_manager)
        # Store in session state for access by advanced options
        st.session_state['basic_relationships'] = basic_relationships
        
        st.markdown("---")
        
        # Basic settings section
        depth, advanced_settings = render_basic_settings(session_manager)
        
        st.markdown("---")
        
        # Visual options section
        render_visual_options(session_manager)
        
        st.markdown("---")
        
        # Display options
        show_info, show_graph = render_display_options(session_manager)
        
        st.markdown("---")
        
        # About section
        render_about_section()
        
        # Collect all settings from various sources
        settings = {
            'word': word,
            'sense_number': parsed_sense_number,
            'parsed_sense_number': parsed_sense_number,
            'word_changed': word_changed,
            'synset_search_mode': synset_search_mode,
            'depth': depth,
            'show_info': show_info,
            'show_graph': show_graph,
            
            # Include basic relationship settings
            **basic_relationships,
            
            # Include advanced settings (which may override basic relationships)
            **advanced_settings,
            
            # Get visual settings from session state (set by Streamlit widgets)
            'layout_type': st.session_state.get('layout_type', 'Force-directed (default)'),
            'node_size_multiplier': st.session_state.get('node_size_multiplier', 1.0),
            'edge_width': st.session_state.get('edge_width', 2),
            'color_scheme': st.session_state.get('color_scheme', 'Default'),
            'show_labels': st.session_state.get('show_labels', True),
            'enable_physics': st.session_state.get('enable_physics', True),
            'spring_strength': st.session_state.get('spring_strength', 0.04),
            'central_gravity': st.session_state.get('central_gravity', 0.3),
            
            # Legacy settings for backward compatibility
            'include_hypernyms': basic_relationships.get('show_hypernyms', True),
            'include_hyponyms': basic_relationships.get('show_hyponyms', True),
            'include_meronyms': basic_relationships.get('show_meronyms', False),
            'include_holonyms': basic_relationships.get('show_holonyms', False),
        }
        
        # If a query was selected, override with its settings
        if selected_query:
            settings.update(restored_settings)
        
        return settings 