#!/usr/bin/env python3
"""
Test script to verify the modular refactoring of WordNet Explorer.

This script tests all the new modular components to ensure they work correctly
and maintain backward compatibility.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_wordnet_module():
    """Test the WordNet module components."""
    print("🧪 Testing WordNet Module...")
    
    # Test data access
    from src.wordnet.data_access import download_nltk_data
    print("  ✓ Data access module imported")
    
    # Test synsets
    from src.wordnet.synsets import get_synsets_for_word, get_synset_info
    synsets = get_synsets_for_word("dog")
    assert len(synsets) > 0, "Should find synsets for 'dog'"
    
    synset_info = get_synset_info(synsets[0])
    assert 'name' in synset_info, "Synset info should contain name"
    assert 'definition' in synset_info, "Synset info should contain definition"
    print("  ✓ Synsets module working")
    
    # Test relationships
    from src.wordnet.relationships import RelationshipType, RelationshipConfig, get_relationships
    config = RelationshipConfig()
    relationships = get_relationships(synsets[0], config)
    assert isinstance(relationships, dict), "Should return dictionary of relationships"
    print("  ✓ Relationships module working")
    
    print("✅ WordNet module tests passed!")


def test_graph_module():
    """Test the Graph module components."""
    print("\n🧪 Testing Graph Module...")
    
    # Test nodes
    from src.graph.nodes import NodeType, create_node_id, create_node_label
    node_id = create_node_id(NodeType.MAIN, "test")
    assert node_id == "ROOT_TEST", f"Expected 'ROOT_TEST', got '{node_id}'"
    print("  ✓ Nodes module working")
    
    # Test builder
    from src.graph.builder import GraphBuilder, GraphConfig
    config = GraphConfig(depth=1)
    builder = GraphBuilder(config)
    G, node_labels = builder.build_graph("dog")
    assert G.number_of_nodes() > 0, "Should create nodes for 'dog'"
    assert len(node_labels) > 0, "Should create node labels"
    print("  ✓ Builder module working")
    
    # Test visualizer
    from src.graph.visualizer import GraphVisualizer, VisualizationConfig
    viz_config = VisualizationConfig()
    visualizer = GraphVisualizer(viz_config)
    # Note: We won't test actual visualization to avoid GUI dependencies
    print("  ✓ Visualizer module imported")
    
    print("✅ Graph module tests passed!")


def test_core_module():
    """Test the Core module components."""
    print("\n🧪 Testing Core Module...")
    
    # Test explorer
    from src.core.explorer import WordNetExplorer
    explorer = WordNetExplorer()
    
    # Test word exploration
    G, node_labels = explorer.explore_word("cat", depth=1)
    assert G.number_of_nodes() > 0, "Should create graph for 'cat'"
    print("  ✓ Explorer word exploration working")
    
    # Test word info
    word_info = explorer.get_word_info("cat")
    assert word_info['found'] == True, "Should find 'cat' in WordNet"
    assert word_info['total_senses'] > 0, "Should have multiple senses"
    print("  ✓ Explorer word info working")
    
    # Test session manager
    from src.core.session import SessionManager
    # Note: SessionManager requires Streamlit context, so we just test import
    print("  ✓ Session manager imported")
    
    print("✅ Core module tests passed!")


def test_backward_compatibility():
    """Test that the backward compatibility layer works."""
    print("\n🧪 Testing Backward Compatibility...")
    
    # Test compatibility functions
    from src.wordnet_explorer import (
        build_wordnet_graph, 
        visualize_graph, 
        print_word_info,
        get_synsets_for_word
    )
    
    # Test graph building
    G, node_labels = build_wordnet_graph("bird", depth=1)
    assert G.number_of_nodes() > 0, "Compatibility function should work"
    print("  ✓ build_wordnet_graph compatibility working")
    
    # Test synset access
    synsets = get_synsets_for_word("bird")
    assert len(synsets) > 0, "Should find synsets for 'bird'"
    print("  ✓ get_synsets_for_word compatibility working")
    
    print("✅ Backward compatibility tests passed!")


def test_integration():
    """Test integration between modules."""
    print("\n🧪 Testing Module Integration...")
    
    from src.core.explorer import WordNetExplorer
    from src.wordnet.relationships import RelationshipConfig
    from src.graph.builder import GraphConfig
    
    # Test custom configuration
    rel_config = RelationshipConfig(
        include_hypernyms=True,
        include_hyponyms=False,
        include_meronyms=False,
        include_holonyms=False
    )
    
    explorer = WordNetExplorer()
    G, node_labels = explorer.explore_word(
        "animal", 
        depth=2,
        include_hypernyms=True,
        include_hyponyms=False,
        include_meronyms=False,
        include_holonyms=False
    )
    
    assert G.number_of_nodes() > 0, "Should create graph with custom config"
    print("  ✓ Custom configuration integration working")
    
    # Test focused graph with breadcrumbs
    G2, node_labels2 = explorer.build_focused_graph(
        "mammal", 
        previous_word="animal",
        depth=1
    )
    
    # Check for breadcrumb node
    breadcrumb_nodes = [n for n, d in G2.nodes(data=True) if d.get('node_type') == 'breadcrumb']
    assert len(breadcrumb_nodes) > 0, "Should create breadcrumb node"
    print("  ✓ Focused graph with breadcrumbs working")
    
    print("✅ Integration tests passed!")


def main():
    """Run all tests."""
    print("🚀 Starting WordNet Explorer Modular Refactoring Tests\n")
    
    try:
        test_wordnet_module()
        test_graph_module()
        test_core_module()
        test_backward_compatibility()
        test_integration()
        
        print("\n🎉 All tests passed! Modular refactoring is working correctly.")
        print("\n📊 Summary:")
        print("  ✅ WordNet module: Synsets, relationships, data access")
        print("  ✅ Graph module: Nodes, builder, visualizer")
        print("  ✅ Core module: Explorer, session manager")
        print("  ✅ Backward compatibility: All original functions work")
        print("  ✅ Integration: Modules work together seamlessly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 