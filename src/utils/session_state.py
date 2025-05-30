"""
Session state management utilities for WordNet Explorer.
"""

import streamlit as st
from datetime import datetime


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
    if 'selected_history_query' not in st.session_state:
        st.session_state.selected_history_query = None
    if 'previous_word_input' not in st.session_state:
        st.session_state.previous_word_input = ''
    if 'last_processed_word_input' not in st.session_state:
        st.session_state.last_processed_word_input = ''


def create_query_object(word, settings):
    """
    Create a comprehensive query object that captures all search parameters.
    
    Args:
        word (str): The search word
        settings (dict): All current settings from the sidebar
    
    Returns:
        dict: Complete query object
    """
    query = {
        'word': word,
        'sense_number': settings.get('parsed_sense_number'),
        'synset_search_mode': settings.get('synset_search_mode', False),
        'timestamp': datetime.now().isoformat(),
        
        # Graph exploration settings
        'depth': settings.get('depth', 1),
        'max_nodes': settings.get('max_nodes', 100),
        'max_branches': settings.get('max_branches', 5),
        'min_frequency': settings.get('min_frequency', 0),
        'pos_filter': settings.get('pos_filter', ["Nouns", "Verbs", "Adjectives", "Adverbs"]),
        'enable_clustering': settings.get('enable_clustering', False),
        'enable_cross_connections': settings.get('enable_cross_connections', True),
        'simplified_mode': settings.get('simplified_mode', False),
        
        # Relationship types
        'relationship_settings': {k: v for k, v in settings.items() if k.startswith('show_')},
        
        # Visual settings
        'layout_type': settings.get('layout_type', 'spring'),
        'node_size_multiplier': settings.get('node_size_multiplier', 1.0),
        'color_scheme': settings.get('color_scheme', 'Default'),
        'enable_physics': settings.get('enable_physics', True),
        'spring_strength': settings.get('spring_strength', 0.05),
        'central_gravity': settings.get('central_gravity', 0.3),
        'show_labels': settings.get('show_labels', True),
        'edge_width': settings.get('edge_width', 2),
        
        # Display options
        'show_info': settings.get('show_info', True),
        'show_graph': settings.get('show_graph', True)
    }
    
    return query


def get_query_display_string(query):
    """
    Generate a human-readable string for displaying a query in the history.
    
    Args:
        query (dict): Query object
        
    Returns:
        str: Display string
    """
    word = query['word']
    sense = query.get('sense_number')
    synset_mode = query.get('synset_search_mode', False)
    depth = query.get('depth', 1)
    
    display_parts = [word]
    
    if sense:
        display_parts.append(f"sense {sense}")
    
    if synset_mode:
        display_parts.append("(synset mode)")
    
    if depth > 1:
        display_parts.append(f"depth {depth}")
    
    return " • ".join(display_parts)


def add_to_search_history(word, settings=None):
    """
    Add a word and its full query to search history, avoiding duplicates and maintaining order.
    
    Args:
        word (str): The search word
        settings (dict, optional): Full settings dictionary for comprehensive query storage
    """
    if word and word.strip():
        word = word.strip().lower()
        
        # Create comprehensive query object if settings provided
        if settings:
            query = create_query_object(word, settings)
        else:
            # Fallback for backward compatibility
            query = {
                'word': word,
                'timestamp': datetime.now().isoformat(),
                'sense_number': None,
                'synset_search_mode': False,
                'depth': 1
            }
        
        # Remove any existing entry with the same word to avoid duplicates
        st.session_state.search_history = [
            q for q in st.session_state.search_history 
            if q.get('word', '') != word
        ]
        
        # Add to the beginning of the list (most recent first)
        st.session_state.search_history.insert(0, query)
        
        # Keep only the last 15 searches (increased for more comprehensive history)
        st.session_state.search_history = st.session_state.search_history[:15]


def clear_search_history():
    """Clear the search history."""
    st.session_state.search_history = []


def get_search_history():
    """
    Get the search history with backward compatibility for old word-only entries.
    
    Returns:
        list: List of query objects
    """
    history = st.session_state.get('search_history', [])
    
    # Convert old string entries to query objects for backward compatibility
    converted_history = []
    for item in history:
        if isinstance(item, str):
            # Old format - convert to query object
            converted_history.append({
                'word': item,
                'timestamp': datetime.now().isoformat(),
                'sense_number': None,
                'synset_search_mode': False,
                'depth': 1
            })
        else:
            # New format - already a query object
            converted_history.append(item)
    
    return converted_history 