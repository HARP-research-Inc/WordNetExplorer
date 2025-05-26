"""
JavaScript Test Panel for Navigation Testing
"""

import streamlit as st


def render_js_navigation_test():
    """Render JavaScript-based navigation tests."""
    st.markdown("#### 🟨 JavaScript Navigation Test")
    
    st.markdown("""
    **Test the actual JavaScript navigation that nodes use:**
    """)
    
    # Test word input
    js_test_word = st.text_input("Word to navigate to:", "elephant", key="js_test_word")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Test JavaScript Navigation", key="js_nav_test"):
            # Create JavaScript that mimics the node double-click behavior
            navigation_js = f"""
            <script>
            console.group('🧪 JavaScript Navigation Test');
            console.log('Testing navigation to: {js_test_word}');
            
            // Mimic the exact JavaScript from the graph visualizer
            const targetWord = '{js_test_word}';
            const nodeId = targetWord + '_main';
            
            console.log('Target Word:', targetWord);
            console.log('Node ID:', nodeId);
            
            // Construct URL exactly like the graph does
            const currentUrl = window.location.href.split('?')[0];
            const newUrl = currentUrl + '?navigate_to=' + encodeURIComponent(targetWord) + '&clicked_node=' + encodeURIComponent(nodeId) + '&t=' + Date.now();
            
            console.log('Current URL:', currentUrl);
            console.log('New URL:', newUrl);
            console.log('Navigating...');
            console.groupEnd();
            
            // Actually navigate
            window.location.href = newUrl;
            </script>
            """
            st.components.v1.html(navigation_js, height=0)
            st.success(f"🚀 JavaScript navigation to '{js_test_word}' initiated! Check console for details.")
    
    with col2:
        if st.button("📋 Copy Test URL", key="js_copy_url"):
            # Show what the URL would be
            import time
            timestamp = int(time.time() * 1000)
            test_url = f"http://localhost:8514?navigate_to={js_test_word}&clicked_node={js_test_word}_main&t={timestamp}"
            st.code(test_url)
            st.info("Copy this URL and paste it in your browser to test URL navigation directly!")


def render_url_manual_test():
    """Render manual URL testing interface."""
    st.markdown("#### 🔗 Manual URL Test")
    
    st.markdown("""
    **Manually construct and test navigation URLs:**
    """)
    
    # URL components
    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_url = st.text_input("Base URL:", "http://localhost:8514", key="manual_base_url")
    
    with col2:
        nav_word = st.text_input("Navigate to word:", "tiger", key="manual_nav_word")
    
    with col3:
        node_id = st.text_input("Node ID:", f"{nav_word}_main", key="manual_node_id")
    
    # Construct full URL
    import time
    timestamp = int(time.time() * 1000)
    full_url = f"{base_url}?navigate_to={nav_word}&clicked_node={node_id}&t={timestamp}"
    
    st.markdown("**Constructed URL:**")
    st.code(full_url)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🌐 Open in New Tab", key="manual_open_tab"):
            # JavaScript to open in new tab
            open_tab_js = f"""
            <script>
            console.log('Opening URL in new tab: {full_url}');
            window.open('{full_url}', '_blank');
            </script>
            """
            st.components.v1.html(open_tab_js, height=0)
            st.success("🆕 New tab opened!")
    
    with col2:
        if st.button("🔄 Navigate Current Tab", key="manual_nav_current"):
            # JavaScript to navigate current tab
            nav_current_js = f"""
            <script>
            console.log('Navigating current tab to: {full_url}');
            window.location.href = '{full_url}';
            </script>
            """
            st.components.v1.html(nav_current_js, height=0)
            st.success("🚀 Navigation initiated!")


def render_js_test_panel():
    """Render the complete JavaScript test panel."""
    with st.expander("🟨 JavaScript & URL Tests", expanded=False):
        render_js_navigation_test()
        st.markdown("---")
        render_url_manual_test() 