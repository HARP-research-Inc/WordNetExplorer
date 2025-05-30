"""
QueryNavigator class for WordNet Explorer.
Handles navigation operations and query state management.
"""

from typing import Optional, Tuple
import streamlit as st
from .query import Query
from .search_history import SearchHistory


class QueryNavigator:
    """Manages query navigation and state transitions."""
    
    def __init__(self, session_manager):
        """Initialize the navigator."""
        self.session_manager = session_manager
        self.history = SearchHistory()
        self._ensure_session_state()
    
    def _ensure_session_state(self):
        """Ensure required session state variables exist."""
        defaults = {
            'current_query': None,
            'selected_history_query': None,
            'last_processed_word': '',
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def get_current_query(self) -> Optional[Query]:
        """Get the current active query."""
        return st.session_state.get('current_query')
    
    def set_current_query(self, query: Query) -> None:
        """Set the current active query."""
        st.session_state.current_query = query
        st.session_state.last_processed_word = query.word
    
    def create_query_from_sidebar(self, settings: dict) -> Query:
        """Create a Query object from sidebar settings."""
        return Query.from_sidebar_settings(settings)
    
    def create_query_from_url(self) -> Query:
        """Create a Query object from URL parameters."""
        return Query.from_url_params(self.session_manager)
    
    def navigate_to_query(self, query: Query) -> None:
        """Navigate to a specific query."""
        # Add to history if it's different from current
        current = self.get_current_query()
        if not current or not query.is_equivalent_to(current):
            self.history.add(query)
        
        # Set as current
        self.set_current_query(query)
    
    def navigate_from_history(self, index: int) -> Optional[Query]:
        """Navigate to a query from history by index."""
        query = self.history.get_by_index(index)
        if query:
            st.session_state.selected_history_query = query
            return query
        return None
    
    def get_selected_history_query(self) -> Optional[Query]:
        """Get the currently selected history query."""
        return st.session_state.get('selected_history_query')
    
    def clear_selected_history_query(self) -> None:
        """Clear the selected history query."""
        st.session_state.selected_history_query = None
    
    def process_word_input(self, word: str, sense_number: Optional[int] = None, 
                          synset_search_mode: bool = False) -> Tuple[Query, bool]:
        """
        Process word input and determine if it's a new query.
        
        Returns:
            Tuple of (Query object, whether it's a new/changed query)
        """
        # Check if we have a selected history query first
        selected_query = self.get_selected_history_query()
        if selected_query:
            self.clear_selected_history_query()
            return selected_query, True
        
        # Check if word has changed
        last_word = st.session_state.get('last_processed_word', '')
        word_changed = bool(word and word != last_word)
        
        # Create query from current inputs, preserving URL settings if available
        if word_changed:
            # New word - start with URL settings and update with current inputs
            base_query = self.create_query_from_url()
            query = base_query.update(
                word=word,
                sense_number=sense_number,
                synset_search_mode=synset_search_mode
            )
        else:
            # Same word - use current query or create from current settings
            current = self.get_current_query()
            if current and current.word == word:
                query = current.update(
                    sense_number=sense_number,
                    synset_search_mode=synset_search_mode
                )
            else:
                # Fallback to URL settings
                base_query = self.create_query_from_url()
                query = base_query.update(
                    word=word,
                    sense_number=sense_number,
                    synset_search_mode=synset_search_mode
                )
        
        return query, word_changed
    
    def update_url_with_query(self, query: Query, force_update: bool = False) -> None:
        """Update URL parameters with query settings."""
        if force_update:
            url_params = query.to_url_params()
            if url_params:
                self.session_manager.set_query_params(url_params)
    
    def handle_apply_button(self, current_query: Query) -> None:
        """Handle Apply button click."""
        if current_query:
            # Update URL
            self.update_url_with_query(current_query, force_update=True)
            
            # Update history with complete settings
            self.history.add(current_query)
            
            # Set as current
            self.set_current_query(current_query)
    
    def get_widget_values_for_query(self, query: Optional[Query]) -> dict:
        """Get widget default values for a given query."""
        if not query:
            return {}
        
        return {
            'word_input': query.word,
            'sense_number_input': str(query.sense_number) if query.sense_number else "",
            'synset_search_mode': query.synset_search_mode,
        }
    
    def merge_with_sidebar_settings(self, query: Query, sidebar_settings: dict) -> Query:
        """Merge a query with current sidebar settings."""
        # Update the query with all sidebar settings except word-specific ones
        word_specific_keys = {'word', 'sense_number', 'synset_search_mode', 'timestamp'}
        
        update_dict = {}
        for key, value in sidebar_settings.items():
            if key not in word_specific_keys:
                update_dict[key] = value
        
        return query.update(**update_dict)
    
    def navigate_to_url(self, query: Query) -> None:
        """Navigate to a query by constructing and setting the URL."""
        # Log the constructed URL for debugging
        url = query.log_constructed_url()
        
        # Get URL parameters
        url_params = query.to_url_params()
        
        if url_params:
            # Update the URL with all parameters
            self.session_manager.set_query_params(url_params)
            print(f"🔗 NAVIGATED TO: {url}")
        else:
            print(f"🔗 NO PARAMS TO NAVIGATE WITH")
    
    def navigate_from_history_simple(self, index: int) -> bool:
        """Simple navigation to a query from history by URL construction."""
        query = self.history.get_by_index(index)
        if query:
            print(f"🔗 NAVIGATING TO HISTORY ITEM {index}: {query.get_display_name()}")
            self.navigate_to_url(query)
            return True
        else:
            print(f"🔗 FAILED TO GET HISTORY ITEM {index}")
            return False
    
    def redirect_to_query(self, query: Query) -> None:
        """Redirect user to a specific query by setting URL parameters."""
        # Get URL parameters from query
        url_params = query.to_url_params()
        
        # Log to browser (visible to user)
        st.write(f"🔗 **Redirecting to:** {query.get_display_name()}")
        st.write(f"🔗 **URL Parameters:** {url_params}")
        
        if url_params:
            try:
                # Clear existing query params first
                st.query_params.clear()
                
                # Set new query parameters using modern API
                for key, value in url_params.items():
                    st.query_params[key] = value
                
                st.write(f"✅ **Successfully set {len(url_params)} URL parameters**")
                st.write("🔄 **URL updated! The page should reload automatically...**")
                
                # Streamlit should automatically rerun when query params change
                # But we can force it if needed
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ **Failed to redirect:** {str(e)}")
                
                # Show the constructed URL for manual copy-paste
                constructed_url = query.construct_url()
                st.write(f"**Manual URL:** `{constructed_url}`")
                st.write("**Copy the URL above and paste it in your browser address bar**")
        else:
            st.warning("⚠️ **No URL parameters to redirect with**")
    
    def redirect_from_history_button(self, index: int) -> bool:
        """Handle history button click with visible logging and proper redirection."""
        st.write(f"🔘 **History button clicked:** Item {index}")
        
        query = self.history.get_by_index(index)
        if query:
            st.write(f"📋 **Found query:** {query.get_display_name()}")
            st.write(f"📋 **Query details:** depth={query.depth}, relationships={[k for k,v in query.to_dict().items() if k.startswith('show_') and v]}")
            
            # Redirect to this query
            self.redirect_to_query(query)
            return True
        else:
            st.error(f"❌ **Failed to find history item {index}**")
            return False 