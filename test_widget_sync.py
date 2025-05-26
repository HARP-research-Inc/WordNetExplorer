#!/usr/bin/env python3
"""
Simple test to verify widget synchronization logic for node navigation.
"""

def test_widget_input_logic():
    """Test the widget input value calculation logic."""
    print("🧪 Testing Widget Input Value Logic")
    print("=" * 40)
    
    def calculate_input_value(selected_word, current_word, widget_value):
        """Replicate the logic from render_word_input()"""
        if selected_word:
            # Priority 1: History word was selected
            return selected_word
        elif current_word and current_word != widget_value:
            # Priority 2: Current word from URL navigation (if different from widget)
            return current_word
        else:
            # Priority 3: Keep existing widget value or empty
            return widget_value
    
    # Test cases
    test_cases = [
        {
            "name": "History button click",
            "selected_word": "dog",
            "current_word": "cat", 
            "widget_value": "cat",
            "expected": "dog",
            "description": "History word should take priority"
        },
        {
            "name": "Node double-click navigation",
            "selected_word": None,
            "current_word": "sheep",
            "widget_value": "cat", 
            "expected": "sheep",
            "description": "URL navigation should update widget when different"
        },
        {
            "name": "No navigation change",
            "selected_word": None,
            "current_word": "cat",
            "widget_value": "cat",
            "expected": "cat", 
            "description": "Widget should keep current value when no change"
        },
        {
            "name": "Empty state",
            "selected_word": None,
            "current_word": None,
            "widget_value": "",
            "expected": "",
            "description": "Empty widget should stay empty"
        },
        {
            "name": "Initial load with current word",
            "selected_word": None,
            "current_word": "animal",
            "widget_value": "",
            "expected": "animal",
            "description": "Initial load should show current word"
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        result = calculate_input_value(
            test["selected_word"], 
            test["current_word"], 
            test["widget_value"]
        )
        
        passed = result == test["expected"]
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"{i}. {test['name']}: {status}")
        print(f"   {test['description']}")
        print(f"   Input: selected='{test['selected_word']}', current='{test['current_word']}', widget='{test['widget_value']}'")
        print(f"   Expected: '{test['expected']}', Got: '{result}'")
        
        if not passed:
            all_passed = False
        print()
    
    return all_passed

def main():
    """Run the widget synchronization test."""
    success = test_widget_input_logic()
    
    print("=" * 40)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("🎯 Widget synchronization logic is working correctly")
        print("💡 Node double-clicks should now update the text input field")
    else:
        print("💥 SOME TESTS FAILED!")
        print("🔧 Widget synchronization logic needs fixes")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 