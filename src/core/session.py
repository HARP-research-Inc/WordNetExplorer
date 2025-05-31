"""
Session Manager Module

Handles Streamlit session state management for the WordNet Explorer application.
"""

from typing import List, Optional, Any, Dict
import streamlit as st
from streamlit.runtime.scriptrunner import ScriptRunContext
from urllib.parse import urlencode


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
    
    def get_query_params(self) -> Dict[str, Any]:
        """Get query parameters from URL, handling different Streamlit versions."""
        try:
            # Try newer Streamlit API first
            return dict(st.query_params)
        except AttributeError:
            try:
                # Fall back to experimental API
                params = st.experimental_get_query_params()
                # Convert list values to single values for consistency
                return {k: v[0] if isinstance(v, list) and v else v for k, v in params.items()}
            except AttributeError:
                return {}
    
    def set_query_params(self, params: Dict[str, Any]):
        """Set query parameters in URL, handling different Streamlit versions."""
        try:
            # Try newer Streamlit API first
            st.query_params.update(params)
        except AttributeError:
            try:
                # Fall back to experimental API
                # Convert single values to lists for experimental API
                list_params = {k: [str(v)] if not isinstance(v, list) else v for k, v in params.items()}
                st.experimental_set_query_params(**list_params)
            except AttributeError:
                # If neither API is available, just log in debug mode
                if self.is_debug_mode():
                    st.write(f"🔍 LOG: [URL_PARAMS] Would set params: {params}")
    
    def get_settings_from_url(self) -> Dict[str, Any]:
        """Get search settings from URL parameters."""
        query_params = self.get_query_params()
        settings = {}
        
        # Define parameter mappings with type conversions
        param_mappings = {
            'word': ('word', str),
            'depth': ('depth', int),
            'sense': ('sense_number', int),
            'hypernyms': ('show_hypernyms', lambda x: x.lower() == 'true'),
            'hyponyms': ('show_hyponyms', lambda x: x.lower() == 'true'),
            'meronyms': ('show_meronyms', lambda x: x.lower() == 'true'),
            'holonyms': ('show_holonyms', lambda x: x.lower() == 'true'),
            'layout': ('layout_type', str),
            'node_size': ('node_size_multiplier', float),
            'color': ('color_scheme', str),
            'physics': ('enable_physics', lambda x: x.lower() == 'true'),
            'spring': ('spring_strength', float),
            'gravity': ('central_gravity', float),
            'labels': ('show_labels', lambda x: x.lower() == 'true'),
            'edge_width': ('edge_width', int),
            'show_info': ('show_info', lambda x: x.lower() == 'true'),
            'show_graph': ('show_graph', lambda x: x.lower() == 'true'),
        }
        
        for url_param, (setting_key, converter) in param_mappings.items():
            if url_param in query_params:
                try:
                    value = query_params[url_param]
                    if value is not None and value != '':
                        settings[setting_key] = converter(value)
                except (ValueError, TypeError) as e:
                    if self.is_debug_mode():
                        st.write(f"🔍 LOG: [URL_PARAMS] Error converting {url_param}={value}: {e}")
        
        return settings
    
    def update_url_with_settings(self, settings: Dict[str, Any], force_update: bool = False):
        """Update URL parameters with current search settings."""
        # Only update URL if forced (Apply button or Enter pressed)
        if not force_update:
            return
            
        # Define reverse parameter mappings
        reverse_mappings = {
            'word': 'word',
            'depth': 'depth',
            'sense_number': 'sense',
            'show_hypernyms': 'hypernyms',
            'show_hyponyms': 'hyponyms',
            'show_meronyms': 'meronyms',
            'show_holonyms': 'holonyms',
            'layout_type': 'layout',
            'node_size_multiplier': 'node_size',
            'color_scheme': 'color',
            'enable_physics': 'physics',
            'spring_strength': 'spring',
            'central_gravity': 'gravity',
            'show_labels': 'labels',
            'edge_width': 'edge_width',
            'show_info': 'show_info',
            'show_graph': 'show_graph',
        }
        
        url_params = {}
        for setting_key, url_param in reverse_mappings.items():
            if setting_key in settings and settings[setting_key] is not None:
                value = settings[setting_key]
                # Convert boolean values to lowercase strings
                if isinstance(value, bool):
                    url_params[url_param] = str(value).lower()
                else:
                    url_params[url_param] = str(value)
        
        # Only update if we have parameters to set
        if url_params:
            self.set_query_params(url_params)
            
            if self.is_debug_mode():
                st.write(f"🔍 LOG: [URL_PARAMS] Updated URL with: {url_params}")
    
    def handle_url_navigation(self):
        """Handle navigation from URL parameters."""
        query_params = self.get_query_params()
        
        # Handle word navigation
        navigate_to_word = query_params.get("word") or query_params.get("navigate_to")
        
        if navigate_to_word:
            # Set session state without modifying widgets
            st.session_state.current_word = navigate_to_word
            st.session_state.last_searched_word = navigate_to_word
            self.add_to_history(navigate_to_word)
            
            if self.is_debug_mode():
                st.write(f"🔍 LOG: [URL_NAVIGATION] Navigated from URL to: {navigate_to_word}")
    
    def log_debug_info(self):
        """Display debug information if debug mode is enabled."""
        if self.is_debug_mode():
            st.sidebar.markdown("### Debug Information")
            st.sidebar.write(f"**Current Word:** {self.get_current_word()}")
            st.sidebar.write(f"**Word Input:** {self.get_word_input()}")
            st.sidebar.write(f"**Last Searched:** {st.session_state.get('last_searched_word')}")
            st.sidebar.write(f"**History:** {self.get_search_history()}")
            
            # Show URL parameters
            url_params = self.get_query_params()
            if url_params:
                st.sidebar.write(f"**URL Params:** {url_params}")
            
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