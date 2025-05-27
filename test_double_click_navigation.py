#!/usr/bin/env python3
"""
Test script to verify double-click navigation with URL parameters.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core import WordNetExplorer
from src.graph.visualizer import GraphVisualizer, VisualizationConfig

def test_double_click_navigation():
    """Test that double-click navigation preserves URL parameters."""
    print("🧪 Testing Double-Click Navigation with URL Parameters")
    print("=" * 60)
    
    # Create explorer and visualizer
    explorer = WordNetExplorer()
    config = VisualizationConfig(
        layout_type="Force-directed (default)",
        node_size_multiplier=1.2,
        enable_physics=True,
        spring_strength=0.05,
        central_gravity=0.4,
        show_labels=True,
        edge_width=3,
        color_scheme="Vibrant"
    )
    visualizer = GraphVisualizer(config)
    
    # Build a graph for testing
    print("📊 Building graph for 'dog'...")
    G, node_labels = explorer.explore_word("dog", depth=2, include_hypernyms=True, include_hyponyms=True)
    
    if G.number_of_nodes() == 0:
        print("❌ No graph nodes found")
        return False
    
    print(f"✅ Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Generate HTML with enhanced navigation
    print("🔧 Generating HTML with double-click navigation...")
    html_content = visualizer.visualize_interactive(G, node_labels, "dog")
    
    if not html_content:
        print("❌ Failed to generate HTML content")
        return False
    
    # Check if our enhanced JavaScript is present
    required_js_features = [
        "// Send message to parent page to handle navigation",
        "type: 'navigate',",
        "targetWord: targetWord,",
        "clickedNode: nodeId,",
        "window.parent.postMessage(navigationData, '*');",
        "console.log('📤 Sending navigation message to parent:', navigationData);",
        "nodeId.startsWith('ROOT_')"
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
    
    print("✅ All double-click navigation features found in HTML")
    
    # Save test file with URL parameters
    test_file = "test_double_click_navigation.html"
    
    # Simulate a URL with parameters
    test_url_params = "?word=dog&depth=2&hypernyms=true&hyponyms=true&layout=Force-directed%20(default)&node_size=1.2&physics=true&spring=0.05&gravity=0.4&labels=true&edge_width=3&color=Vibrant"
    
    # Add a comment and test parent page listener to the HTML
    html_with_test_info = f"""
<!-- Test URL with parameters: 
     http://localhost:8501/{test_url_params}
     
     When you double-click any node, it should send a postMessage to the parent page.
     For standalone testing, it will fall back to direct URL navigation.
-->
<script>
// Test parent page message listener (for standalone testing)
window.addEventListener('message', function(event) {{
    if (event.data && event.data.type === 'navigate') {{
        console.log('🎯 Parent received navigation message:', event.data);
        
        const targetWord = event.data.targetWord;
        const clickedNode = event.data.clickedNode;
        
        if (targetWord) {{
            // Simulate URL update (in real Streamlit, this would be handled by the main page)
            const url = new URL(window.location);
            url.searchParams.set('word', targetWord);
            url.searchParams.set('clicked_node', clickedNode);
            url.searchParams.delete('navigate_to');
            
            console.log('🔗 Would navigate to:', url.toString());
            alert('Navigation would go to: ' + targetWord + '\\nFull URL: ' + url.toString());
        }}
    }}
}});
console.log('✅ Test parent message listener installed');
</script>
{html_content}
"""
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_with_test_info)
    
    print(f"💾 Test HTML saved to: {test_file}")
    print("\n🎯 To test the double-click navigation:")
    print(f"   1. Open {test_file} in your web browser")
    print("   2. Open browser developer tools (F12)")
    print("   3. Go to the Console tab")
    print("   4. Double-click any node in the graph")
    print("   5. Check the console for the navigation URL")
    print("   6. Verify that all original parameters are preserved")
    print("\n📝 Expected behavior:")
    print("   - Double-click should send postMessage to parent")
    print("   - Console should show: '📤 Sending navigation message to parent: [data]'")
    print("   - For standalone testing, alert should show navigation details")
    print("   - In Streamlit, parent page should handle URL update")
    print("\n🔗 Example messages that should be sent:")
    print("   - Double-click 'animal' node: {type: 'navigate', targetWord: 'animal', clickedNode: 'ROOT_ANIMAL'}")
    print("   - Double-click 'canine' synset: {type: 'navigate', targetWord: 'canine', clickedNode: 'canine.n.02'}")
    print("   - Double-click 'wether' node: {type: 'navigate', targetWord: 'wether', clickedNode: 'ROOT_WETHER'}")
    
    return True

if __name__ == "__main__":
    success = test_double_click_navigation()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1) 