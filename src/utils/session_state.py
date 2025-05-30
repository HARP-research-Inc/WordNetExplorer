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


def add_to_search_history(item):
    """Add an item to search history, avoiding duplicates and maintaining order."""
    if not item:
        return
    
    # Handle both old format (string) and new format (dict)
    if isinstance(item, str):
        # Old format - convert to dict
        word = item.strip().lower()
        if not word:
            return
        search_item = {'word': word, 'timestamp': None}
    else:
        # New format - dict with query parameters
        word = item.get('word', '').strip().lower()
        if not word:
            return
        search_item = item.copy()
        search_item['word'] = word  # Ensure lowercase
    
    # Remove duplicate entries based on word and sense number
    word_to_match = search_item['word']
    sense_to_match = search_item.get('sense_number')
    
    # Remove existing items with same word and sense combination
    st.session_state.search_history = [
        hist_item for hist_item in st.session_state.search_history
        if not (
            (isinstance(hist_item, str) and hist_item == word_to_match) or
            (isinstance(hist_item, dict) and 
             hist_item.get('word') == word_to_match and 
             hist_item.get('sense_number') == sense_to_match)
        )
    ]
    
    # Add to the beginning of the list (most recent first)
    st.session_state.search_history.insert(0, search_item)
    
    # Keep only the last 10 searches
    st.session_state.search_history = st.session_state.search_history[:10]


def clear_search_history():
    """Clear the search history."""
    st.session_state.search_history = [] 