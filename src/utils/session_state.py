"""
Session state management utilities for WordNet Explorer.
"""

import streamlit as st
from src.models.search_history import SearchQuery, SearchHistoryManager


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'current_word' not in st.session_state:
        st.session_state.current_word = None
    if 'graph_center' not in st.session_state:
        st.session_state.graph_center = None
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'search_history_manager' not in st.session_state:
        st.session_state.search_history_manager = SearchHistoryManager()
        print(f"🎯 CREATED NEW SearchHistoryManager with ID: {id(st.session_state.search_history_manager)}")
    if 'selected_history_word' not in st.session_state:
        st.session_state.selected_history_word = None
    if 'selected_history_query' not in st.session_state:
        st.session_state.selected_history_query = None
    if 'previous_word_input' not in st.session_state:
        st.session_state.previous_word_input = ''
    if 'last_processed_word_input' not in st.session_state:
        st.session_state.last_processed_word_input = ''
    if 'selected_queries_for_comparison' not in st.session_state:
        st.session_state.selected_queries_for_comparison = set()  # Set of query hashes


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


def add_query_to_history(settings: dict):
    """Add a complete query to the enhanced search history."""
    # Create SearchQuery from current settings
    query = SearchQuery.from_settings(settings)
    
    print(f"🎯 ADD_QUERY_TO_HISTORY called with word='{query.word}', sense={query.sense_number}, hash={query.get_hash()}")
    print(f"🎯 History manager ID: {id(st.session_state.search_history_manager)}")
    print(f"🎯 Before add: {len(st.session_state.search_history_manager.queries)} queries")
    
    # Add to history manager
    result = st.session_state.search_history_manager.add_query(query)
    
    print(f"🎯 After add: {len(st.session_state.search_history_manager.queries)} queries")
    print(f"🎯 Add result: {'New query added' if result else 'Duplicate query moved to front'}")
    
    # Also maintain backward compatibility with simple word list
    add_to_search_history(query.word)


def get_search_history_manager() -> SearchHistoryManager:
    """Get the search history manager, creating if necessary."""
    if 'search_history_manager' not in st.session_state:
        st.session_state.search_history_manager = SearchHistoryManager()
        print(f"🎯 CREATED SearchHistoryManager in getter with ID: {id(st.session_state.search_history_manager)}")
    return st.session_state.search_history_manager


def clear_search_history():
    """Clear the search history."""
    st.session_state.search_history = []
    if 'search_history_manager' in st.session_state:
        st.session_state.search_history_manager.clear()
        print("🎯 CLEARED search history manager")


def restore_query_settings(query: SearchQuery) -> dict:
    """Restore settings from a SearchQuery object."""
    settings = {
        'word': query.word,
        'sense_number': query.sense_number,
        'parsed_sense_number': query.sense_number,
        'synset_search_mode': query.synset_search_mode,
        'depth': query.depth,
        'max_nodes': query.max_nodes,
        'max_branches': query.max_branches,
        'pos_filter': query.pos_filter,
        'simplified_mode': query.simplified_mode,
        'min_frequency': query.min_frequency
    }
    
    # Restore relationship settings
    for rel in query.active_relationships:
        settings[f'show_{rel}'] = True
    
    return settings 