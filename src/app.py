#!/usr/bin/env python3
"""
WordNet Explorer - Streamlit UI (Refactored Modular Version)

A web-based interface for exploring WordNet semantic relationships
using Streamlit with a clean, modular architecture.
"""

import streamlit as st
import sys
import os
import importlib
import time

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

# Force reload of modules to ensure we get the latest code
if 'src.graph.visualizer' in sys.modules:
    importlib.reload(sys.modules['src.graph.visualizer'])
if 'src.ui.graph_display' in sys.modules:
    importlib.reload(sys.modules['src.ui.graph_display'])





def add_main_window_navigation_listener():
    """Add JavaScript listener in the main window to handle navigation messages from iframes."""
    cache_buster = int(time.time())
    
    # Enhanced, more robust navigation listener
    navigation_listener_script = f"""
    <script>
        (function() {{
            var timestamp = {cache_buster};
            console.log('🔧 MainWindow: Installing enhanced navigation listener v' + timestamp + '...');
            
            // Prevent multiple installations
            if (window.mainWindowListenerInstalled) {{
                console.log('⚠️ MainWindow: Listener already installed, skipping...');
                return;
            }}
            
            function handleNavigationMessage(event) {{
                console.log('📨 MainWindow: Received message v' + timestamp + ':', event.data);
                console.log('📨 MainWindow: Message origin:', event.origin);
                console.log('📨 MainWindow: Event source:', event.source);
                console.log('📨 MainWindow: Current window:', window.location.href);
                
                // Filter out Streamlit internal messages
                if (event.data && event.data.stCommVersion) {{
                    console.log('🔄 MainWindow: Ignoring Streamlit internal message');
                    return;
                }}
                
                // Handle navigation requests
                if (event.data && event.data.type === 'streamlit-navigate') {{
                    console.log('🎯 MainWindow: Processing navigation to:', event.data.targetWord);
                    console.log('🎯 MainWindow: Clicked node:', event.data.clickedNode);
                    
                    try {{
                        var url = new URL(window.location.href);
                        url.searchParams.set('word', event.data.targetWord);
                        url.searchParams.set('clicked_node', event.data.clickedNode);
                        
                        console.log('🔗 MainWindow: Navigating to:', url.toString());
                        window.location.href = url.toString();
                    }} catch (e) {{
                        console.error('❌ MainWindow: Navigation failed:', e);
                    }}
                }} else {{
                    console.log('🔍 MainWindow: Message type mismatch. Expected: streamlit-navigate, Got:', 
                               event.data ? event.data.type : 'undefined');
                    console.log('🔍 MainWindow: Full event data:', event.data);
                }}
            }}
            
            // Install the message listener
            window.addEventListener('message', handleNavigationMessage, false);
            window.mainWindowListenerInstalled = true;
            
            console.log('✅ MainWindow: Enhanced navigation listener installed successfully v' + timestamp);
            console.log('🔍 MainWindow: Window context:', {{
                'location': window.location.href,
                'parent': window.parent === window ? 'is top window' : 'has parent',
                'top': window.top === window ? 'is top window' : 'has top'
            }});
            
            // Test the listener immediately
            setTimeout(function() {{
                console.log('🧪 MainWindow: Testing listener installation...');
                window.postMessage({{
                    type: 'test-message',
                    test: true
                }}, '*');
            }}, 100);
        }})();
    </script>
    """
    st.markdown(navigation_listener_script, unsafe_allow_html=True)


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
    
    # TEST: Add navigation test buttons
    st.markdown("### 🧪 Navigation Test Buttons")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🐕 Navigate to 'dog'"):
            st.markdown('<script>window.location.href = "?word=dog&clicked_node=test_button";</script>', unsafe_allow_html=True)
    
    with col2:
        if st.button("🐱 Navigate to 'cat'"):
            st.markdown('<script>window.location.href = "?word=cat&clicked_node=test_button";</script>', unsafe_allow_html=True)
    
    with col3:
        if st.button("🐑 Navigate to 'sheep'"):
            st.markdown('<script>window.location.href = "?word=sheep&clicked_node=test_button";</script>', unsafe_allow_html=True)
    
    with col4:
        if st.button("🐄 Navigate to 'bovine'"):
            st.markdown('<script>window.location.href = "?word=bovine&clicked_node=test_button";</script>', unsafe_allow_html=True)
    
    # TEST: Add postMessage test
    st.markdown("### 🧪 PostMessage Navigation Test")
    test_col1, test_col2 = st.columns(2)
    
    with test_col1:
        if st.button("📨 Test PostMessage to 'bovine'"):
            test_script = """
            <script>
                console.log('🧪 TEST: Sending postMessage for bovine...');
                window.postMessage({
                    type: 'streamlit-navigate',
                    targetWord: 'bovine',
                    clickedNode: 'test_postmessage'
                }, '*');
            </script>
            """
            st.markdown(test_script, unsafe_allow_html=True)
    
    with test_col2:
        if st.button("📨 Test PostMessage to 'canine'"):
            test_script = """
            <script>
                console.log('🧪 TEST: Sending postMessage for canine...');
                window.postMessage({
                    type: 'streamlit-navigate',
                    targetWord: 'canine',
                    clickedNode: 'test_postmessage'
                }, '*');
            </script>
            """
            st.markdown(test_script, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Handle URL navigation
    session_manager.handle_url_navigation()
    
    # DEBUG: Show current URL parameters and session state
    st.markdown("### 🔍 Debug Information")
    debug_col1, debug_col2 = st.columns(2)
    
    with debug_col1:
        st.markdown("**URL Parameters:**")
        query_params = session_manager.get_query_params()
        if query_params:
            for key, value in query_params.items():
                st.write(f"- `{key}`: {value}")
        else:
            st.write("No URL parameters")
    
    with debug_col2:
        st.markdown("**Session State:**")
        st.write(f"- Current Word: `{session_manager.get_current_word()}`")
        st.write(f"- Word Input: `{session_manager.get_word_input()}`")
        st.write(f"- Last Searched: `{st.session_state.get('last_searched_word')}`")
    
    # DEBUG: Show what handle_url_navigation detected
    navigate_to_word = query_params.get("word") or query_params.get("navigate_to")
    clicked_node = query_params.get("clicked_node")
    if navigate_to_word:
        st.info(f"🔍 URL Navigation detected: word='{navigate_to_word}', clicked_node='{clicked_node}'")
    else:
        st.info("🔍 No URL navigation parameters found")
    
    st.markdown("---")
    
    # Add main window navigation listener for iframe messages
    add_main_window_navigation_listener()
    
    # TEST: Verify navigation listener is working
    st.markdown("### 🧪 Navigation Listener Test")
    if st.button("🔧 Test Navigation Listener"):
        test_listener_script = """
        <script>
            console.log('🧪 TEST: Testing navigation listener...');
            
            // Check if listener is installed
            if (window.mainWindowListenerInstalled) {
                console.log('✅ Navigation listener is installed');
                
                // Send a test message to ourselves
                window.postMessage({
                    type: 'streamlit-navigate',
                    targetWord: 'test',
                    clickedNode: 'test_listener'
                }, '*');
                
                console.log('📤 Test message sent');
            } else {
                console.error('❌ Navigation listener is NOT installed');
            }
        </script>
        """
        st.markdown(test_listener_script, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Render sidebar and get settings
    settings = render_sidebar(session_manager)
    
    # DEBUG: Show what sidebar returned
    st.markdown("### 🔍 Sidebar Settings")
    st.write(f"- Word from sidebar: `{settings.get('word')}`")
    st.write(f"- Current display word: `{settings.get('word') or session_manager.get_current_word()}`")
    
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