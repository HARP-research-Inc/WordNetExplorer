"""
Session state management utilities for WordNet Explorer.
"""

import streamlit as st


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'navigation_history' not in st.session_state:
        st.session_state.navigation_history = []
    if 'current_word' not in st.session_state:
        st.session_state.current_word = None
    if 'graph_center' not in st.session_state:
        st.session_state.graph_center = None


def add_to_navigation_history(word):
    """Add a word to navigation history if it's not already there."""
    if word and word not in st.session_state.navigation_history:
        st.session_state.navigation_history.append(word)


def navigate_to_word(word):
    """Navigate to a specific word, updating session state appropriately."""
    if word != st.session_state.current_word:
        # Add current word to history before navigating
        if st.session_state.current_word:
            add_to_navigation_history(st.session_state.current_word)
        
        # Set the new word as current
        st.session_state.current_word = word


def clear_navigation_history():
    """Clear the navigation history."""
    st.session_state.navigation_history = []
    st.session_state.current_word = None


def navigate_back_to_word(word, history_index):
    """Navigate back to a word in the history, truncating history after that point."""
    # Remove everything after this word in history
    st.session_state.navigation_history = st.session_state.navigation_history[:history_index]
    st.session_state.current_word = word


def get_current_path_display():
    """Get a formatted display of the current navigation path."""
    if not st.session_state.navigation_history and not st.session_state.current_word:
        return ""
    
    path_parts = st.session_state.navigation_history.copy()
    if st.session_state.current_word:
        path_parts.append(st.session_state.current_word)
    
    return " → ".join(path_parts) 