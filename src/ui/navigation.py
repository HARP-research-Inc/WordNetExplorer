"""
Navigation components for WordNet Explorer.
"""

import streamlit as st
from ..utils.session_state import (
    navigate_back_to_word, 
    clear_navigation_history,
    get_current_path_display
)


def render_navigation_history():
    """Render the navigation history section in the sidebar."""
    if st.session_state.navigation_history:
        with st.expander("📚 Navigation History", expanded=True):
            st.markdown("Click any word to return to it:")
            
            # Create a more compact display with fewer columns
            max_cols = min(3, len(st.session_state.navigation_history))
            if max_cols > 0:
                # Split history into rows of max 3 items
                history_items = st.session_state.navigation_history
                for i in range(0, len(history_items), max_cols):
                    row_items = history_items[i:i + max_cols]
                    cols = st.columns(len(row_items))
                    
                    for j, hist_word in enumerate(row_items):
                        with cols[j]:
                            if st.button(f"📍 {hist_word}", key=f"hist_{i+j}", help=f"Return to '{hist_word}'"):
                                # Navigate back to this word
                                navigate_back_to_word(hist_word, i+j)
                                st.rerun()
            
            # Show current word
            if st.session_state.current_word:
                st.markdown(f"**🎯 Current: {st.session_state.current_word}**")
            
            # Clear history button
            if st.button("🗑️ Clear History", help="Clear navigation history"):
                clear_navigation_history()
                st.rerun()


def render_navigation_controls():
    """Render the navigation controls section in the sidebar."""
    if st.session_state.navigation_history:
        st.markdown("### 🧭 Quick Navigation")
        if st.button("🏠 Start Fresh", help="Clear history and start fresh"):
            clear_navigation_history()
            st.rerun()
        
        # Show current path
        path_display = get_current_path_display()
        if path_display:
            st.markdown(f"**Current Path:** {path_display}")


def handle_url_navigation():
    """Handle navigation from URL parameters."""
    query_params = st.query_params
    if 'navigate_to' in query_params:
        navigate_to_word = query_params['navigate_to']  # Get value directly
        
        if navigate_to_word and navigate_to_word != st.session_state.current_word:
            # Add current word to history before navigating (if not already there)
            if st.session_state.current_word and st.session_state.current_word not in st.session_state.navigation_history:
                st.session_state.navigation_history.append(st.session_state.current_word)
            
            # Set the new word as current
            st.session_state.current_word = navigate_to_word
            
            # Clear the URL parameters and rerun
            st.query_params.clear()
            st.rerun() 