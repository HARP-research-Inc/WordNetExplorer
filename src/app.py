#!/usr/bin/env python3
"""
WordNet Explorer - Streamlit UI (Refactored Modular Version)

A web-based interface for exploring WordNet semantic relationships
using Streamlit with a clean, modular architecture.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import warnings

# Suppress specific Streamlit warnings more comprehensively
warnings.filterwarnings("ignore", message=".*was created with a default value but also had its value set via the Session State API.*")
warnings.filterwarnings("ignore", message=".*widget.*default value.*Session State API.*")
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

# Add parent directory to path to allow imports (works for both local and deployment)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import configuration
from config.settings import PAGE_CONFIG

# Import core modules
from core import WordNetExplorer, SessionManager

# Import UI components
from ui.styles import load_custom_css
from ui.sidebar import render_sidebar
from ui.word_info import render_word_information
from ui.graph_display import render_graph_visualization, render_graph_legend_and_controls
from ui.welcome import render_welcome_screen
from ui.footer import render_footer
from ui.comparison import render_comparison_view
from ui.path_finding import render_path_finding_view

# Import enhanced history functionality
from utils.session_state import add_query_to_history, initialize_session_state


def render_header():
    """Render the header with title."""
    # App title and description
    st.markdown('<h1 class="main-header">WordNet Explorer</h1>', unsafe_allow_html=True)
    st.markdown("Explore semantic relationships between words using WordNet")


def main():
    """Main application function."""
    # Set page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize session state for enhanced history
    initialize_session_state()
    
    # Initialize core components
    session_manager = SessionManager()
    explorer = WordNetExplorer()
    
    # Load custom CSS
    load_custom_css()
    
    # Render header with logo
    render_header()
    
    # Check if we're in comparison mode
    compare_mode = st.session_state.get('compare_mode', False)
    path_finding_mode = st.session_state.get('path_finding_mode', False)
    
    if path_finding_mode:
        # Path finding mode
        render_path_finding_view(explorer)
    elif compare_mode:
        # Comparison mode - render merged graph
        render_comparison_view(explorer)
    else:
        # Normal mode - single graph view
        # Handle URL navigation
        session_manager.handle_url_navigation()
        
        # Render sidebar and get settings
        settings = render_sidebar(session_manager)
        
        # Determine the current word to display
        current_display_word = settings.get('word') or session_manager.get_current_word()
        
        # Debug logging
        print(f"🔍 APP: current_display_word='{current_display_word}', settings_word='{settings.get('word')}', current_word='{session_manager.get_current_word()}'")
        print(f"🔍 APP: word_changed={settings.get('word_changed', False)}, parsed_sense={settings.get('parsed_sense_number')}")
        
        # Check if this is a new query that should be added to history
        # This happens when word_changed is True OR when we have a word that's being displayed
        should_add_to_history = False
        
        # Update session state if this is a new word from input
        if settings.get('word') and settings['word'] != session_manager.get_current_word():
            # Update session state without modifying the widget
            st.session_state.current_word = settings['word']
            st.session_state.last_searched_word = settings['word']
            session_manager.add_to_history(settings['word'])
            should_add_to_history = True
            current_display_word = settings['word']
            print(f"🔍 APP: New word detected, should_add_to_history=True")
        
        # Also add to history if word_changed flag is set (user pressed Enter)
        if settings.get('word_changed', False) and settings.get('word'):
            should_add_to_history = True
            print(f"🔍 APP: word_changed flag set, should_add_to_history=True")
        
        print(f"🔍 APP: Final should_add_to_history={should_add_to_history}")
        
        # Main content area
        if current_display_word:
            try:
                # Check if we're in synset search mode
                synset_search_mode = settings.get('synset_search_mode', False)
                display_input = current_display_word
                
                # If in synset search mode, convert word+sense to synset name
                if synset_search_mode and settings.get('parsed_sense_number'):
                    from wordnet import get_synsets_for_word
                    synsets = get_synsets_for_word(current_display_word)
                    sense_number = settings['parsed_sense_number']
                    if synsets and 1 <= sense_number <= len(synsets):
                        # Use the synset name instead of the word
                        display_input = synsets[sense_number - 1].name()
                    else:
                        st.error(f"Invalid sense number {sense_number} for word '{current_display_word}'")
                        synset_search_mode = False  # Fall back to word mode
                
                # Add complete query to enhanced history if needed
                if should_add_to_history:
                    print(f"🔍 APP: Calling add_query_to_history with settings")
                    add_query_to_history(settings)
                else:
                    print(f"🔍 APP: NOT calling add_query_to_history")
                    # Fallback: If we're displaying a word but it's not in history, add it
                    from utils.session_state import get_search_history_manager
                    from src.models.search_history import SearchQuery
                    
                    history_manager = get_search_history_manager()
                    current_query = SearchQuery.from_settings(settings)
                    
                    # Check if this exact query exists in history
                    query_exists = any(q.get_hash() == current_query.get_hash() for q in history_manager.queries)
                    
                    if not query_exists and current_display_word:
                        print(f"🔍 APP: Query not in history, adding as fallback")
                        add_query_to_history(settings)
                
                # Show word information if requested (not applicable in synset mode)
                if settings.get('show_info', False) and not synset_search_mode:
                    render_word_information(current_display_word)
                
                # Build and display graph if requested
                if settings.get('show_graph', True):
                    render_graph_visualization(display_input, settings, explorer, synset_search_mode)
            
            except Exception as e:
                st.error(f"Error: {e}")
                if settings.get('synset_search_mode', False):
                    st.error("Please check that you have entered a valid synset name (e.g., 'dog.n.01').")
                else:
                    st.error("Please check that you have entered a valid English word.")
        
        else:
            # Show welcome screen
            render_welcome_screen()
    
    # Display debug information if enabled
    session_manager.log_debug_info()
    
    # Render footer
    render_footer()


if __name__ == "__main__":
    main() 