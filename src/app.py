#!/usr/bin/env python3
"""
WordNet Explorer - Streamlit UI (Refactored Modular Version)

A web-based interface for exploring WordNet semantic relationships
using Streamlit with a clean, modular architecture.
"""

import streamlit as st
import sys
import os

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
    settings = render_sidebar()
    
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
            # Show word information if requested
            if settings.get('show_info', False):
                render_word_information(current_display_word)
            
            # Build and display graph if requested
            if settings.get('show_graph', True):
                render_graph_visualization(current_display_word, settings, explorer)
        
        except Exception as e:
            st.error(f"Error: {e}")
            st.error("Please check that you have entered a valid English word.")
    
    else:
        # Show welcome screen
        render_welcome_screen()
    
    # Display debug information if enabled
    session_manager.log_debug_info()


if __name__ == "__main__":
    main() 