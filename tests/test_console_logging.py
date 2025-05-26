#!/usr/bin/env python3
"""
Test script to verify enhanced console logging in graph visualization.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import WordNetExplorer

def test_console_logging():
    """Test that the enhanced console logging is properly integrated."""
    print("🧪 Testing Enhanced Console Logging for Node Double-Clicks")
    print("=" * 60)
    
    # Create explorer
    explorer = WordNetExplorer()
    
    # Build a simple graph
    print("📊 Building graph for 'dog'...")
    G, node_labels = explorer.explore_word("dog", depth=1)
    
    if G.number_of_nodes() == 0:
        print("❌ No graph nodes found")
        return False
    
    print(f"✅ Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Generate HTML with enhanced logging
    print("🔧 Generating HTML with enhanced console logging...")
    html_content = explorer.visualize_graph(G, node_labels, "dog")
    
    if not html_content:
        print("❌ Failed to generate HTML content")
        return False
    
    # Check if our enhanced JavaScript is present
    required_js_features = [
        "console.group('🖱️ Node Double-Click Event')",
        "console.log('Node ID:', nodeId)",
        "console.log('Node Label:', nodeData",
        "console.log('Detected Node Type:', nodeType)",
        "console.log('Target Word for Navigation:', targetWord)",
        "console.groupEnd()",
        "Enhanced double-click navigation and logging enabled",
        "hoverNode",
        "Single-click on node"
    ]
    
    missing_features = []
    for feature in required_js_features:
        if feature not in html_content:
            missing_features.append(feature)
    
    if missing_features:
        print("❌ Missing JavaScript features:")
        for feature in missing_features:
            print(f"   - {feature}")
        return False
    
    print("✅ All enhanced console logging features found in HTML")
    
    # Save test file
    test_file = "test_console_logging_output.html"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"💾 Test HTML saved to: {test_file}")
    print("\n🎯 To test the console logging:")
    print(f"   1. Open {test_file} in your web browser")
    print("   2. Open browser developer tools (F12)")
    print("   3. Go to the Console tab")
    print("   4. Double-click any node in the graph")
    print("   5. You should see detailed logging information!")
    print("\n📝 Expected console output:")
    print("   🖱️ Node Double-Click Event")
    print("     Node ID: [node_id]")
    print("     Node Label: [label]")
    print("     Node Title: [title]")
    print("     Node Color: [color]")
    print("     Node Size: [size]")
    print("     Click Position: [x, y]")
    print("     Canvas Position: [x, y]")
    print("     Timestamp: [ISO timestamp]")
    print("     Detected Node Type: [type]")
    print("     Target Word for Navigation: [word]")
    
    return True

if __name__ == "__main__":
    success = test_console_logging()
    if success:
        print("\n🎉 Enhanced console logging test completed successfully!")
    else:
        print("\n❌ Enhanced console logging test failed!")
        sys.exit(1) 