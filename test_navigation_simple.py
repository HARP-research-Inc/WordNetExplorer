#!/usr/bin/env python3
"""
Simple Navigation Test

Test the navigation functionality step by step.
"""

import streamlit as st
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    st.title("🧪 Simple Navigation Test")
    
    st.markdown("""
    **Test the navigation pipeline step by step:**
    
    1. **URL Parameter Test**: Check if URL parameters are detected
    2. **Session State Test**: Check if session state updates correctly  
    3. **Widget Test**: Check if text input shows the right value
    """)
    
    # Step 1: URL Parameter Detection
    st.markdown("### 1️⃣ URL Parameter Detection")
    
    try:
        url_params = dict(st.query_params)
        st.write(f"**Current URL Parameters:** {url_params}")
        
        navigate_to = st.query_params.get("navigate_to")
        if navigate_to:
            st.success(f"✅ Found navigate_to parameter: '{navigate_to}'")
        else:
            st.info("ℹ️ No navigate_to parameter found")
            
    except Exception as e:
        st.error(f"❌ Error accessing URL parameters: {e}")
    
    # Step 2: Session State
    st.markdown("### 2️⃣ Session State")
    
    session_info = {
        "current_word": st.session_state.get('current_word'),
        "word_input": st.session_state.get('word_input'),
        "last_searched_word": st.session_state.get('last_searched_word'),
    }
    
    for key, value in session_info.items():
        st.write(f"**{key}:** `{value}`")
    
    # Step 3: Manual Navigation Test
    st.markdown("### 3️⃣ Manual Navigation Test")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_word = st.text_input("Test word:", "elephant")
        
    with col2:
        if st.button("🔗 Navigate via URL"):
            # Set URL parameters and rerun
            st.query_params["navigate_to"] = test_word
            st.query_params["test"] = "manual"
            st.rerun()
    
    # Step 4: Widget Input Test
    st.markdown("### 4️⃣ Widget Input Test")
    
    # Simple text input to see what value it gets
    current_word = st.session_state.get('current_word')
    widget_value = st.session_state.get('word_input', '')
    
    # Calculate input value using the same logic as the main app
    if current_word and current_word != widget_value:
        input_value = current_word
        reason = "Using current_word from navigation"
    else:
        input_value = widget_value
        reason = "Using existing widget value"
    
    st.write(f"**Calculated input value:** `{input_value}` ({reason})")
    
    # Test input field
    word_input = st.text_input("Word input field:", value=input_value, key="test_word_input")
    st.write(f"**Actual widget value:** `{word_input}`")
    
    # Step 5: URL Construction Test
    st.markdown("### 5️⃣ URL Construction Test")
    
    base_url = "http://localhost:8515"  # Updated port
    test_nav_word = st.text_input("Test navigation word:", "dog")
    
    constructed_url = f"{base_url}?navigate_to={test_nav_word}&clicked_node={test_nav_word}_main&t=123456"
    st.code(constructed_url)
    
    if st.button("📋 Copy URL to clipboard"):
        st.info("Copy the URL above and paste it in your browser address bar to test!")

if __name__ == "__main__":
    main() 