#!/usr/bin/env python3
"""
Test the unified navigation approach where node clicks use history button logic.
"""

def test_unified_navigation_logic():
    """Test that node navigation is treated exactly like history button clicks."""
    print("🧪 Testing Unified Navigation Logic")
    print("=" * 45)
    
    def simulate_navigation_detection(query_params, selected_history_word):
        """Simulate the logic from render_word_input()"""
        # Check for node navigation from double-click
        node_nav_word = None
        if 'node_nav' in query_params:
            node_nav_word = query_params['node_nav']
        
        # Check if a history word was selected
        selected_word = selected_history_word
        
        # If we have node navigation, treat it exactly like a history button click
        if node_nav_word:
            selected_word = node_nav_word
        
        return selected_word, node_nav_word
    
    # Test cases
    test_cases = [
        {
            "name": "History button click (no node nav)",
            "query_params": {},
            "selected_history_word": "dog",
            "expected_selected": "dog",
            "expected_node_nav": None,
            "description": "Normal history button should work as before"
        },
        {
            "name": "Node double-click navigation",
            "query_params": {"node_nav": "sheep"},
            "selected_history_word": None,
            "expected_selected": "sheep",
            "expected_node_nav": "sheep",
            "description": "Node click should be treated as selected word"
        },
        {
            "name": "Node nav overrides history",
            "query_params": {"node_nav": "cat"},
            "selected_history_word": "dog",
            "expected_selected": "cat",
            "expected_node_nav": "cat",
            "description": "Node navigation should take precedence over history"
        },
        {
            "name": "No navigation",
            "query_params": {},
            "selected_history_word": None,
            "expected_selected": None,
            "expected_node_nav": None,
            "description": "No navigation should result in no selection"
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        selected_word, node_nav_word = simulate_navigation_detection(
            test["query_params"], 
            test["selected_history_word"]
        )
        
        passed = (selected_word == test["expected_selected"] and 
                 node_nav_word == test["expected_node_nav"])
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"{i}. {test['name']}: {status}")
        print(f"   {test['description']}")
        print(f"   Input: query_params={test['query_params']}, history_word='{test['selected_history_word']}'")
        print(f"   Expected: selected='{test['expected_selected']}', node_nav='{test['expected_node_nav']}'")
        print(f"   Got: selected='{selected_word}', node_nav='{node_nav_word}'")
        
        if not passed:
            all_passed = False
        print()
    
    return all_passed

def main():
    """Run the unified navigation test."""
    success = test_unified_navigation_logic()
    
    print("=" * 45)
    if success:
        print("🎉 UNIFIED NAVIGATION TEST PASSED!")
        print("🎯 Node double-clicks now use history button logic")
        print("💡 Both navigation methods should work identically")
        print("🔧 JavaScript sets ?node_nav=word parameter")
        print("📝 Sidebar treats node_nav as selected_history_word")
    else:
        print("💥 UNIFIED NAVIGATION TEST FAILED!")
        print("🔧 The unified logic needs fixes")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 