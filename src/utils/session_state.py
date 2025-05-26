"""
Session state management utilities for WordNet Explorer.
"""

import streamlit as st


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'current_word' not in st.session_state:
        st.session_state.current_word = None
    if 'graph_center' not in st.session_state:
        st.session_state.graph_center = None
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'selected_history_word' not in st.session_state:
        st.session_state.selected_history_word = None
    if 'previous_word_input' not in st.session_state:
        st.session_state.previous_word_input = ''
    if 'last_processed_word_input' not in st.session_state:
        st.session_state.last_processed_word_input = ''





def add_to_search_history(word):
    """Add a word to search history, avoiding duplicates and maintaining order."""
    if word and word.strip():
        word = word.strip().lower()
        # Remove word if it already exists to avoid duplicates
        if word in st.session_state.search_history:
            st.session_state.search_history.remove(word)
        # Add to the beginning of the list (most recent first)
        st.session_state.search_history.insert(0, word)
        # Keep only the last 10 searches
        st.session_state.search_history = st.session_state.search_history[:10]


def clear_search_history():
    """Clear the search history."""
    st.session_state.search_history = [] 