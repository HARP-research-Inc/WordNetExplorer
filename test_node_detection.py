#!/usr/bin/env python3
"""
Test script to verify node type detection logic.
"""

def test_node_detection():
    """Test the node type detection logic that's used in JavaScript."""
    
    test_cases = [
        ("ROOT_WETHER", "main word (ROOT)", "wether"),
        ("ROOT_RAM", "main word (ROOT)", "ram"),
        ("ROOT_SHEEP", "main word (ROOT)", "sheep"),
        ("dog_main", "main word", "dog"),
        ("cat_main", "main word", "cat"),
        ("animal_breadcrumb", "breadcrumb", "animal"),
        ("mammal_word", "related word", "mammal"),
        ("canine.n.02", "synset", "canine"),
        ("bovine.n.01", "synset", "bovine"),
        ("random_node", "unknown", "random_node"),
    ]
    
    print("🧪 Testing Node Type Detection Logic")
    print("=" * 50)
    
    for node_id, expected_type, expected_word in test_cases:
        # Simulate the JavaScript logic
        node_type = 'unknown'
        target_word = node_id
        
        if node_id.startswith('ROOT_'):
            node_type = 'main word (ROOT)'
            target_word = node_id.replace('ROOT_', '').lower()
        elif '_main' in node_id:
            node_type = 'main word'
            target_word = node_id.replace('_main', '')
        elif '_breadcrumb' in node_id:
            node_type = 'breadcrumb'
            target_word = node_id.replace('_breadcrumb', '')
        elif '_word' in node_id:
            node_type = 'related word'
            target_word = node_id.replace('_word', '')
        elif '.' in node_id:
            node_type = 'synset'
            target_word = node_id.split('.')[0]
        
        # Check results
        type_correct = node_type == expected_type
        word_correct = target_word == expected_word
        
        status = "✅" if (type_correct and word_correct) else "❌"
        
        print(f"{status} {node_id}")
        print(f"   Expected: {expected_type} -> {expected_word}")
        print(f"   Got:      {node_type} -> {target_word}")
        
        if not type_correct:
            print(f"   ❌ Type mismatch!")
        if not word_correct:
            print(f"   ❌ Word mismatch!")
        
        print()
    
    print("🔍 JavaScript Equivalent Test:")
    print("Copy this into browser console to test:")
    print("""
function testNodeDetection(nodeId) {
    let nodeType = 'unknown';
    let targetWord = nodeId;
    
    if (nodeId.startsWith('ROOT_')) {
        nodeType = 'main word (ROOT)';
        targetWord = nodeId.replace('ROOT_', '').toLowerCase();
    } else if (nodeId.includes('_main')) {
        nodeType = 'main word';
        targetWord = nodeId.replace('_main', '');
    } else if (nodeId.includes('_breadcrumb')) {
        nodeType = 'breadcrumb';
        targetWord = nodeId.replace('_breadcrumb', '');
    } else if (nodeId.includes('_word')) {
        nodeType = 'related word';
        targetWord = nodeId.replace('_word', '');
    } else if (nodeId.includes('.')) {
        nodeType = 'synset';
        targetWord = nodeId.split('.')[0];
    }
    
    console.log(`${nodeId} -> ${nodeType} -> ${targetWord}`);
    return {nodeType, targetWord};
}

// Test cases
testNodeDetection('ROOT_WETHER');
testNodeDetection('ROOT_RAM');
testNodeDetection('dog_main');
testNodeDetection('canine.n.02');
""")

if __name__ == "__main__":
    test_node_detection() 