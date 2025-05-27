#!/usr/bin/env python3
"""
Debug script to test JavaScript generation and node detection.
"""

import sys
import os
import importlib

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_js_generation():
    """Test that the JavaScript generation includes our enhanced debugging."""
    print("🔧 Testing JavaScript Generation")
    print("=" * 50)
    
    try:
        # Import and reload modules to ensure we get the latest code
        from src.graph import visualizer
        from src.core import WordNetExplorer
        
        # Force reload the visualizer module
        importlib.reload(visualizer)
        
        print("✅ Modules imported successfully")
        
        # Create instances
        explorer = WordNetExplorer()
        config = visualizer.VisualizationConfig()
        vis = visualizer.GraphVisualizer(config)
        
        print("✅ Instances created successfully")
        
        # Build a simple graph
        G, node_labels = explorer.explore_word("sheep", depth=1, include_hypernyms=True)
        print(f"✅ Graph created with {G.number_of_nodes()} nodes")
        
        # Generate HTML
        html_content = vis.visualize_interactive(G, node_labels, "sheep")
        print("✅ HTML generated successfully")
        
        # Check for our enhanced debugging features
        checks = [
            ("Enhanced debugging", "Node ID Analysis:" in html_content),
            ("startsWith check", "nodeId.startsWith('ROOT_')" in html_content),
            ("Detected ROOT_ prefix", "Detected ROOT_ prefix" in html_content),
            ("Enhanced parent detection", "Enhanced parent detection" in html_content),
            ("Message sent to window.parent", "Message sent to window.parent" in html_content),
            ("Final Detection Results", "Final Detection Results" in html_content),
        ]
        
        print("\n🔍 JavaScript Feature Checks:")
        all_passed = True
        for feature, found in checks:
            status = "✅" if found else "❌"
            print(f"  {status} {feature}")
            if not found:
                all_passed = False
        
        if all_passed:
            print("\n✅ All enhanced debugging features found in generated HTML!")
        else:
            print("\n❌ Some enhanced debugging features are missing!")
            
        # Save test HTML file
        test_file = "debug_test_output.html"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n💾 Test HTML saved to: {test_file}")
        
        # Extract and show the navigation JavaScript
        import re
        js_pattern = r'if \(nodeId\.startsWith\(\'ROOT_\'\)\) \{.*?\}'
        js_match = re.search(js_pattern, html_content, re.DOTALL)
        
        if js_match:
            print("\n📝 Found ROOT_ detection JavaScript:")
            print(js_match.group(0)[:300] + "...")
        else:
            print("\n❌ Could not find ROOT_ detection JavaScript")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_browser_js():
    """Generate JavaScript test code for browser console."""
    print("\n🌐 Browser Console Test Code:")
    print("=" * 50)
    print("Copy and paste this into your browser console:")
    print("""
// Test the exact same logic as in our Python code
function testNodeDetectionFixed(nodeId) {
    console.log('🔍 Testing Node ID:', nodeId);
    
    let nodeType = 'unknown';
    let targetWord = nodeId;
    
    console.log('  - nodeId.startsWith("ROOT_"):', nodeId.startsWith('ROOT_'));
    
    if (nodeId.startsWith('ROOT_')) {
        nodeType = 'main word (ROOT)';
        targetWord = nodeId.replace('ROOT_', '').toLowerCase();
        console.log('✅ Detected ROOT_ prefix');
    } else if (nodeId.includes('_main')) {
        nodeType = 'main word';
        targetWord = nodeId.replace('_main', '');
        console.log('✅ Detected _main suffix');
    } else if (nodeId.includes('_breadcrumb')) {
        nodeType = 'breadcrumb';
        targetWord = nodeId.replace('_breadcrumb', '');
        console.log('✅ Detected _breadcrumb suffix');
    } else if (nodeId.includes('_word')) {
        nodeType = 'related word';
        targetWord = nodeId.replace('_word', '');
        console.log('✅ Detected _word suffix');
    } else if (nodeId.includes('.')) {
        nodeType = 'synset';
        targetWord = nodeId.split('.')[0];
        console.log('✅ Detected synset format');
    } else {
        console.log('❌ No pattern matched');
    }
    
    console.log('🎯 Result:', nodeType, '->', targetWord);
    return {nodeType, targetWord};
}

// Test the problematic cases
testNodeDetectionFixed('ROOT_WETHER');
testNodeDetectionFixed('ROOT_RAM');
testNodeDetectionFixed('sheep_main');
testNodeDetectionFixed('canine.n.02');
""")

if __name__ == "__main__":
    success = test_js_generation()
    test_browser_js()
    
    if success:
        print("\n✅ JavaScript generation test passed!")
        print("💡 Try refreshing your Streamlit app and clearing browser cache")
    else:
        print("\n❌ JavaScript generation test failed!")
        print("💡 There may be a module import or caching issue") 