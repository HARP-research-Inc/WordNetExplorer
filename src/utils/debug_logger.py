"""
Debug logging utility for WordNet Explorer.
"""

import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up file logger
log_filename = os.path.join(log_dir, f"wordnet_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logger
logger = logging.getLogger('wordnet_debug')
logger.setLevel(logging.DEBUG)

# Create file handler
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
if not logger.handlers:
    logger.addHandler(file_handler)

def log_word_input_event(event_type, **kwargs):
    """Log word input related events with detailed context."""
    timestamp = datetime.now().isoformat()
    log_message = f"[{event_type}] "
    
    for key, value in kwargs.items():
        log_message += f"{key}='{value}' "
    
    logger.info(log_message)
    print(f"🔍 LOG: {log_message}")  # Also print to console for immediate feedback

def log_session_state(prefix=""):
    """Log current session state for debugging."""
    import streamlit as st
    
    session_data = {
        'current_word': st.session_state.get('current_word', 'None'),
        'last_searched_word': st.session_state.get('last_searched_word', 'None'),
        'previous_word_input': st.session_state.get('previous_word_input', 'None'),
        'last_processed_word_input': st.session_state.get('last_processed_word_input', 'None'),
        'selected_history_word': st.session_state.get('selected_history_word', 'None'),
        'search_history_length': len(st.session_state.get('search_history', [])),
        'search_history': st.session_state.get('search_history', [])
    }
    
    log_word_input_event(f"SESSION_STATE_{prefix}", **session_data) 