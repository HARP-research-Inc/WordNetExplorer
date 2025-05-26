"""
Navigation components for WordNet Explorer.
"""

import streamlit as st
from ..utils.session_state import add_to_search_history


def handle_url_navigation():
    """Handle navigation from URL parameters."""
    query_params = st.query_params
    if 'navigate_to' in query_params:
        navigate_to_word = query_params['navigate_to']  # Get value directly
        
        if navigate_to_word and navigate_to_word != st.session_state.current_word:
            # Add the navigated word to search history
            add_to_search_history(navigate_to_word)
            
            # Set the new word as current
            st.session_state.current_word = navigate_to_word
            st.session_state.last_searched_word = navigate_to_word
            
            # Clear the URL parameters and rerun
            st.query_params.clear()
            st.rerun() 