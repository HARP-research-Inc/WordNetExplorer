#!/usr/bin/env python3
"""
WordNet Explorer - Streamlit UI (Refactored Modular Version)

A web-based interface for exploring WordNet semantic relationships
using Streamlit with a clean, modular architecture.
"""

import streamlit as st
import sys
import os
import warnings

# Suppress specific Streamlit warnings
warnings.filterwarnings("ignore", message=".*was created with a default value but also had its value set via the Session State API.*")

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import configuration
from src.config.settings import PAGE_CONFIG

# Import core modules
from src.core import WordNetExplorer, SessionManager

# Import UI components
from src.ui.styles import load_custom_css
from src.ui.sidebar import render_sidebar
from src.ui.word_info import render_word_information
from src.ui.graph_display import render_graph_visualization
from src.ui.welcome import render_welcome_screen


def main():
    """Main application function."""
    # Set page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize core components
    session_manager = SessionManager()
    explorer = WordNetExplorer()
    
    # Load custom CSS
    load_custom_css()
    
    # App title and description
    st.markdown('<h1 class="main-header">WordNet Explorer</h1>', unsafe_allow_html=True)
    st.markdown("Explore semantic relationships between words using WordNet")
    
    # Handle URL navigation
    session_manager.handle_url_navigation()
    
    # Render sidebar and get settings
    settings = render_sidebar(session_manager)
    
    # Determine the current word to display
    current_display_word = settings.get('word') or session_manager.get_current_word()
    
    # Update session state if this is a new word from input
    if settings.get('word') and settings['word'] != session_manager.get_current_word():
        # Update session state without modifying the widget
        st.session_state.current_word = settings['word']
        st.session_state.last_searched_word = settings['word']
        session_manager.add_to_history(settings['word'])
        current_display_word = settings['word']
    
    # Main content area
    if current_display_word:
        try:
            # Check if we're in synset search mode
            synset_search_mode = settings.get('synset_search_mode', False)
            display_input = current_display_word
            
            # If in synset search mode, convert word+sense to synset name
            if synset_search_mode and settings.get('parsed_sense_number'):
                from src.wordnet import get_synsets_for_word
                synsets = get_synsets_for_word(current_display_word)
                sense_number = settings['parsed_sense_number']
                if synsets and 1 <= sense_number <= len(synsets):
                    # Use the synset name instead of the word
                    display_input = synsets[sense_number - 1].name()
                else:
                    st.error(f"Invalid sense number {sense_number} for word '{current_display_word}'")
                    synset_search_mode = False  # Fall back to word mode
            
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


if __name__ == "__main__":
    main() 