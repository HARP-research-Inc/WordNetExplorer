"""
Debug Panel for Testing Navigation Pipeline
"""

import streamlit as st
from typing import Optional


def render_navigation_debug_panel():
    """Render a debug panel to test navigation components."""
    st.markdown("---")
    st.markdown("### 🔧 Navigation Debug Panel")
    
    with st.expander("🧪 Test Navigation Pipeline", expanded=False):
        st.markdown("**Test each step of the node double-click navigation:**")
        
        # Step 1: Test URL Parameter Detection
        st.markdown("#### 1️⃣ URL Parameter Detection")
        
        # Show current URL parameters
        try:
            query_params = st.experimental_get_query_params()
            st.write(f"**Current URL params (old API):** {query_params}")
        except:
            pass
            
        try:
            if hasattr(st, 'query_params'):
                st.write(f"**Current URL params (new API):** {dict(st.query_params)}")
        except:
            pass
        
        # Manual URL parameter test
        col1, col2 = st.columns(2)
        with col1:
            test_word = st.text_input("Test word for URL navigation:", "dog", key="debug_test_word")
        with col2:
            if st.button("🔗 Simulate URL Navigation", key="debug_url_nav"):
                # Simulate what the JavaScript does
                st.query_params["navigate_to"] = test_word
                st.query_params["clicked_node"] = f"{test_word}_main"
                st.query_params["debug_test"] = "true"
                st.rerun()
        
        # Step 2: Test Session State Updates
        st.markdown("#### 2️⃣ Session State Updates")
        
        session_info = {
            "current_word": st.session_state.get('current_word'),
            "last_searched_word": st.session_state.get('last_searched_word'),
            "word_input": st.session_state.get('word_input'),
            "previous_word_input": st.session_state.get('previous_word_input'),
            "last_processed_word_input": st.session_state.get('last_processed_word_input'),
            "search_history": st.session_state.get('search_history', []),
        }
        
        for key, value in session_info.items():
            st.write(f"**{key}:** `{value}`")
        
        # Manual session state test
        col1, col2 = st.columns(2)
        with col1:
            manual_word = st.text_input("Manually set current_word:", key="debug_manual_word")
        with col2:
            if st.button("📝 Set Session State", key="debug_set_session"):
                st.session_state.current_word = manual_word
                st.session_state.word_input = manual_word
                st.rerun()
        
        # Step 3: Test Widget Input Logic
        st.markdown("#### 3️⃣ Widget Input Logic Test")
        
        # Show the widget input calculation
        selected_word = st.session_state.get('selected_history_word')
        current_word = st.session_state.get('current_word')
        widget_value = st.session_state.get('word_input', '')
        
        st.write("**Widget Input Calculation:**")
        st.write(f"- selected_word: `{selected_word}`")
        st.write(f"- current_word: `{current_word}`")
        st.write(f"- widget_value: `{widget_value}`")
        
        # Calculate what the input value should be
        if selected_word:
            calculated_input = selected_word
            reason = "Priority 1: History word selected"
        elif current_word and current_word != widget_value:
            calculated_input = current_word
            reason = "Priority 2: URL navigation (current != widget)"
        else:
            calculated_input = widget_value
            reason = "Priority 3: Keep existing widget value"
        
        st.write(f"**Calculated input_value:** `{calculated_input}` ({reason})")
        
        # Step 4: Test Direct Navigation
        st.markdown("#### 4️⃣ Direct Navigation Test")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🐕 Navigate to 'dog'", key="debug_nav_dog"):
                st.session_state.current_word = "dog"
                st.session_state.word_input = "dog"
                st.session_state.last_searched_word = "dog"
                if "dog" not in st.session_state.get('search_history', []):
                    st.session_state.search_history = st.session_state.get('search_history', []) + ["dog"]
                st.rerun()
        
        with col2:
            if st.button("🐱 Navigate to 'cat'", key="debug_nav_cat"):
                st.session_state.current_word = "cat"
                st.session_state.word_input = "cat"
                st.session_state.last_searched_word = "cat"
                if "cat" not in st.session_state.get('search_history', []):
                    st.session_state.search_history = st.session_state.get('search_history', []) + ["cat"]
                st.rerun()
        
        with col3:
            if st.button("🧹 Clear All", key="debug_clear_all"):
                st.session_state.current_word = None
                st.session_state.word_input = ""
                st.session_state.last_searched_word = None
                st.session_state.search_history = []
                st.rerun()
        
        # Step 5: Test URL Construction
        st.markdown("#### 5️⃣ URL Construction Test")
        
        current_url = st.query_params.get("debug_current_url", "http://localhost:8514")
        st.write(f"**Current URL:** `{current_url}`")
        
        test_nav_word = st.text_input("Test navigation word:", "sheep", key="debug_url_word")
        
        # Show what the JavaScript would construct
        constructed_url = f"{current_url.split('?')[0]}?navigate_to={test_nav_word}&clicked_node={test_nav_word}_main&t=123456789"
        st.write(f"**Constructed URL:** `{constructed_url}`")
        
        if st.button("🔗 Test URL Construction", key="debug_test_url"):
            st.info(f"JavaScript would navigate to: {constructed_url}")


def render_console_test_panel():
    """Render a panel to test console logging functionality."""
    st.markdown("#### 🖥️ Console Logging Test")
    
    st.markdown("""
    **Instructions:**
    1. Open browser developer tools (F12)
    2. Go to Console tab
    3. Click the test button below
    4. Check console for test messages
    """)
    
    if st.button("🧪 Test Console Logging", key="debug_console_test"):
        # Inject JavaScript to test console logging
        console_test_js = """
        <script>
        console.group('🧪 Debug Panel Console Test');
        console.log('✅ Console logging is working!');
        console.log('🕐 Timestamp:', new Date().toISOString());
        console.log('📍 Test triggered from Streamlit debug panel');
        console.groupEnd();
        </script>
        """
        st.components.v1.html(console_test_js, height=0)
        st.success("✅ Console test executed! Check browser console for messages.")


def render_full_debug_panel():
    """Render the complete debug panel."""
    render_navigation_debug_panel()
    render_console_test_panel()
    
    # Import and render JavaScript tests
    from .js_test_panel import render_js_test_panel
    render_js_test_panel() 