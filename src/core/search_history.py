"""
SearchHistory class for WordNet Explorer.
Manages search history operations with proper OOP design.
"""

from typing import List, Optional, Union, Dict, Any
import streamlit as st
from .query import Query


class SearchHistory:
    """Manages search history with Query objects."""
    
    def __init__(self, max_size: int = 10):
        """Initialize search history."""
        self.max_size = max_size
        self._ensure_session_state()
    
    def _ensure_session_state(self):
        """Ensure session state is initialized."""
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
    
    def add(self, query: Union[Query, str, Dict[str, Any]]) -> None:
        """
        Add a query to the search history.
        
        Args:
            query: Can be a Query object, string (old format), or dict
        """
        # Convert to Query object
        if isinstance(query, str):
            # Old format - just word
            query_obj = Query(word=query.strip().lower())
        elif isinstance(query, dict):
            # Dictionary format
            query_obj = Query.from_dict(query)
        elif isinstance(query, Query):
            # Already a Query object
            query_obj = query
        else:
            return  # Invalid type
        
        # Don't add empty words
        if not query_obj.word:
            return
        
        # Remove any existing equivalent queries
        self._remove_equivalent(query_obj)
        
        # Add to the beginning (most recent first)
        st.session_state.search_history.insert(0, query_obj)
        
        # Keep only the last max_size items
        st.session_state.search_history = st.session_state.search_history[:self.max_size]
    
    def _remove_equivalent(self, query: Query) -> None:
        """Remove existing equivalent queries from history."""
        st.session_state.search_history = [
            item for item in st.session_state.search_history
            if not self._is_equivalent(item, query)
        ]
    
    def _is_equivalent(self, item: Any, query: Query) -> bool:
        """Check if a history item is equivalent to a query."""
        if isinstance(item, str):
            return item == query.word
        elif isinstance(item, dict):
            return (item.get('word') == query.word and 
                   item.get('sense_number') == query.sense_number)
        elif isinstance(item, Query):
            return item.is_equivalent_to(query)
        return False
    
    def get_all(self) -> List[Query]:
        """Get all history items as Query objects."""
        self._ensure_session_state()
        result = []
        
        for item in st.session_state.search_history:
            if isinstance(item, Query):
                result.append(item)
            elif isinstance(item, str):
                result.append(Query(word=item))
            elif isinstance(item, dict):
                result.append(Query.from_dict(item))
        
        return result
    
    def get_raw(self) -> List[Any]:
        """Get raw history items (for backward compatibility)."""
        self._ensure_session_state()
        return st.session_state.search_history[:]
    
    def clear(self) -> None:
        """Clear the search history."""
        st.session_state.search_history = []
    
    def size(self) -> int:
        """Get the number of items in history."""
        self._ensure_session_state()
        return len(st.session_state.search_history)
    
    def is_empty(self) -> bool:
        """Check if history is empty."""
        return self.size() == 0
    
    def get_by_index(self, index: int) -> Optional[Query]:
        """Get a history item by index as a Query object."""
        if 0 <= index < self.size():
            item = st.session_state.search_history[index]
            if isinstance(item, Query):
                return item
            elif isinstance(item, str):
                return Query(word=item)
            elif isinstance(item, dict):
                return Query.from_dict(item)
        return None
    
    def contains_word(self, word: str) -> bool:
        """Check if history contains a specific word."""
        for query in self.get_all():
            if query.word == word:
                return True
        return False
    
    def get_display_items(self) -> List[tuple]:
        """Get history items formatted for display as (index, display_name, query)."""
        items = []
        for i, query in enumerate(self.get_all()):
            display_name = query.get_display_name()
            items.append((i, display_name, query))
        return items 