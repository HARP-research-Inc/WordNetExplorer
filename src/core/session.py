"""
Session Manager Module

Handles Streamlit session state management for the WordNet Explorer application.
"""

from typing import List, Optional, Any
import streamlit as st


class SessionManager:
    """Manages Streamlit session state for the WordNet Explorer."""
    
    def __init__(self):
        """Initialize session manager and set up default state."""
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables with default values."""
        defaults = {
            'current_word': None,
            'last_searched_word': None,
            'word_input': '',
            'previous_word_input': '',
            'last_processed_word_input': '',
            'search_history': [],
            'debug_mode': False,
            'graph_data': None,
            'node_labels': None,
            'last_graph_html': None
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def navigate_to_word(self, word: str):
        """
        Navigate to a specific word using the consistent navigation pattern.
        
        Args:
            word: The word to navigate to
        """
        st.session_state.current_word = word
        st.session_state.last_searched_word = word
        st.session_state.previous_word_input = word
        st.session_state.last_processed_word_input = word
        
        # Only set word_input if it doesn't exist yet (before widget creation)
        if 'word_input' not in st.session_state:
            st.session_state.word_input = word
        
        # Add to history if not already present
        if word not in st.session_state.search_history:
            st.session_state.search_history.append(word)
        
        if self.is_debug_mode():
            st.write(f"🔍 LOG: [NAVIGATION] Navigated to word: {word}")
    
    def get_current_word(self) -> Optional[str]:
        """Get the current word being displayed."""
        return st.session_state.get('current_word')
    
    def get_word_input(self) -> str:
        """Get the current word input value."""
        return st.session_state.get('word_input', '')
    
    def set_word_input(self, word: str):
        """Set the word input value."""
        st.session_state.word_input = word
    
    def get_search_history(self) -> List[str]:
        """Get the search history."""
        return st.session_state.get('search_history', [])
    
    def add_to_history(self, word: str):
        """Add a word to search history if not already present."""
        history = self.get_search_history()
        if word not in history:
            history.append(word)
            st.session_state.search_history = history
    
    def clear_history(self):
        """Clear the search history."""
        st.session_state.search_history = []
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return st.session_state.get('debug_mode', False)
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        st.session_state.debug_mode = enabled
    
    def store_graph_data(self, graph_data: Any, node_labels: dict):
        """Store graph data in session state."""
        st.session_state.graph_data = graph_data
        st.session_state.node_labels = node_labels
    
    def get_graph_data(self) -> tuple:
        """Get stored graph data."""
        return (
            st.session_state.get('graph_data'),
            st.session_state.get('node_labels', {})
        )
    
    def store_graph_html(self, html: str):
        """Store the last generated graph HTML."""
        st.session_state.last_graph_html = html
    
    def get_graph_html(self) -> Optional[str]:
        """Get the last generated graph HTML."""
        return st.session_state.get('last_graph_html')
    
    def sync_widget_state(self, current_word: str, selected_word: Optional[str] = None):
        """
        Synchronize widget state with current word for navigation.
        
        Args:
            current_word: The current word being displayed
            selected_word: Any word selected from UI components
        """
        # Only sync if widget hasn't been created yet
        if current_word and not selected_word and 'word_input' not in st.session_state:
            st.session_state.word_input = current_word
            
            if self.is_debug_mode():
                st.write(f"🔍 LOG: [WIDGET_SYNC] Synced widget to: {current_word}")
    
    def handle_url_navigation(self):
        """Handle navigation from URL parameters."""
        # Use experimental_get_query_params for older Streamlit versions
        try:
            query_params = st.experimental_get_query_params()
            navigate_to_word = query_params.get("navigate_to", [None])[0]
        except AttributeError:
            # For newer Streamlit versions
            try:
                navigate_to_word = st.query_params.get("navigate_to")
            except AttributeError:
                navigate_to_word = None
        
        if navigate_to_word and navigate_to_word != st.session_state.get('current_word'):
            # Set session state for navigation
            st.session_state.current_word = navigate_to_word
            st.session_state.last_searched_word = navigate_to_word
            self.add_to_history(navigate_to_word)
            
            # CRITICAL FIX: Set the widget input to show the new word
            # This ensures the text input field displays the navigated word
            st.session_state.word_input = navigate_to_word
            
            # Also update the tracking variables for consistency
            st.session_state.previous_word_input = navigate_to_word
            st.session_state.last_processed_word_input = navigate_to_word
            
            # Clear the URL parameters to prevent repeated navigation
            try:
                st.experimental_set_query_params()
            except AttributeError:
                try:
                    st.query_params.clear()
                except AttributeError:
                    pass
            
            if self.is_debug_mode():
                st.write(f"🔍 LOG: [URL_NAVIGATION] Navigated from URL to: {navigate_to_word}")
                st.write(f"🔍 LOG: [WIDGET_SYNC] Set word_input to: {navigate_to_word}")
            
            # Trigger rerun to update the UI
            st.rerun()
    
    def log_debug_info(self):
        """Display debug information if debug mode is enabled."""
        if self.is_debug_mode():
            st.sidebar.markdown("### Debug Information")
            st.sidebar.write(f"**Current Word:** {self.get_current_word()}")
            st.sidebar.write(f"**Word Input:** {self.get_word_input()}")
            st.sidebar.write(f"**Last Searched:** {st.session_state.get('last_searched_word')}")
            st.sidebar.write(f"**History:** {self.get_search_history()}")
            
            # Show all session state for debugging
            with st.sidebar.expander("Full Session State"):
                for key, value in st.session_state.items():
                    if not key.startswith('_'):  # Skip private streamlit keys
                        st.write(f"**{key}:** {value}")
    
    def reset_session(self):
        """Reset the session state to defaults."""
        keys_to_clear = [
            'current_word', 'last_searched_word', 'word_input',
            'previous_word_input', 'last_processed_word_input',
            'search_history', 'graph_data', 'node_labels', 'last_graph_html'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        self._initialize_session_state()
        
        if self.is_debug_mode():
            st.write("🔍 LOG: [SESSION] Session reset completed") 