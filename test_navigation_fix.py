#!/usr/bin/env python3
"""
Test script to verify that node double-click navigation fix works correctly.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_navigation_fix():
    """Test that the navigation fix properly syncs widget state."""
    print("🧪 Testing Node Double-Click Navigation Fix")
    print("=" * 50)
    
    # Import after path setup
    from src.core.session import SessionManager
    
    # Create a mock session state for testing
    class MockSessionState:
        def __init__(self):
            self.data = {}
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
    
    # Mock streamlit
    class MockQueryParams:
        def __init__(self):
            self.data = {'navigate_to': 'dog'}
        
        def get(self, key):
            return self.data.get(key)
        
        def clear(self):
            self.data.clear()
            print("  🧹 URL parameters cleared")
    
    class MockStreamlit:
        def __init__(self):
            self.session_state = MockSessionState()
            self.query_params = MockQueryParams()
        
        def write(self, text):
            print(f"  📝 {text}")
        
        def rerun(self):
            print("  🔄 st.rerun() called")
        
        def experimental_get_query_params(self):
            # Return old format for compatibility
            return {'navigate_to': [self.query_params.data.get('navigate_to')]}
        
        def experimental_set_query_params(self):
            self.query_params.clear()
    
    # Replace streamlit import
    import src.core.session as session_module
    mock_st = MockStreamlit()
    
    # Patch the streamlit module in the session module
    session_module.st = mock_st
    
    # Test the fix
    print("📊 Testing SessionManager URL navigation...")
    
    # Initialize session manager
    session_manager = SessionManager()
    
    # Set initial state
    mock_st.session_state['current_word'] = 'cat'
    mock_st.session_state['word_input'] = 'cat'
    
    print(f"  🔍 Initial state: current_word='{mock_st.session_state.get('current_word')}', word_input='{mock_st.session_state.get('word_input')}'")
    
    # Simulate URL navigation (like from node double-click)
    print("  🖱️ Simulating node double-click navigation to 'dog'...")
    print(f"  🔍 Query params before: {mock_st.query_params.data}")
    
    # Enable debug mode to see what happens
    mock_st.session_state['debug_mode'] = True
    
    session_manager.handle_url_navigation()
    
    print(f"  🔍 Query params after: {mock_st.query_params.data}")
    print(f"  🔍 Session state data: {mock_st.session_state.data}")
    
    # Check results
    current_word = mock_st.session_state.get('current_word')
    word_input = mock_st.session_state.get('word_input')
    
    print(f"  🔍 After navigation: current_word='{current_word}', word_input='{word_input}'")
    
    # Verify the fix
    if current_word == 'dog' and word_input == 'dog':
        print("  ✅ SUCCESS: Widget state properly synchronized!")
        print("  ✅ Node double-click navigation should now work correctly")
        return True
    else:
        print("  ❌ FAILED: Widget state not synchronized")
        print(f"  ❌ Expected: current_word='dog', word_input='dog'")
        print(f"  ❌ Got: current_word='{current_word}', word_input='{word_input}'")
        return False

def main():
    """Run the navigation fix test."""
    try:
        success = test_navigation_fix()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 NAVIGATION FIX TEST PASSED!")
            print("🎯 Node double-clicks should now work the same as history buttons")
            print("💡 The text input field will update when you double-click nodes")
        else:
            print("💥 NAVIGATION FIX TEST FAILED!")
            print("🔧 The fix may need additional work")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 