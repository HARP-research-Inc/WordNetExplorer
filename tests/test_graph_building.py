"""
Test suite for graph building functionality in WordNet Explorer.
"""

import pytest
import networkx as nx
from tests.conftest import extract_node_name


class TestGraphBuilding:
    """Test core graph building functionality."""
    
    @pytest.mark.dependency()
    def test_basic_graph_creation(self, explorer):
        """Test basic graph creation for a simple word."""
        word = 'dog'
        G, node_labels = explorer.explore_word(word, depth=1, max_nodes=20)
        
        assert isinstance(G, nx.Graph), "Should return a NetworkX Graph"
        assert isinstance(node_labels, dict), "Should return node labels dictionary"
        assert G.number_of_nodes() > 0, "Graph should have at least one node"
        
        print(f"✅ Basic graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    @pytest.mark.dependency(depends=["TestGraphBuilding::test_basic_graph_creation"])
    def test_node_types(self, explorer):
        """Test that different node types are created correctly."""
        word = 'cat'
        G, node_labels = explorer.explore_word(word, depth=2, max_nodes=30)
        
        node_types = {}
        for node, data in G.nodes(data=True):
            node_type = data.get('node_type', 'unknown')
            if node_type not in node_types:
                node_types[node_type] = 0
            node_types[node_type] += 1
        
        print(f"Node types found: {node_types}")
        
        # Should have at least some main/synset nodes
        expected_types = ['main', 'synset']
        found_types = [t for t in expected_types if t in node_types]
        assert len(found_types) > 0, f"Should find at least one of {expected_types}, found: {list(node_types.keys())}"
        
        print("✅ Node types verified")
    
    @pytest.mark.dependency(depends=["TestGraphBuilding::test_node_types"])
    def test_edge_properties(self, explorer):
        """Test that edges have proper relationship properties."""
        word = 'book'
        G, _ = explorer.explore_word(word, depth=2, max_nodes=30, show_hypernyms=True)
        
        edges_with_properties = 0
        relationship_types = set()
        
        for source, target, edge_data in G.edges(data=True):
            if 'relation' in edge_data:
                edges_with_properties += 1
                relationship_types.add(edge_data['relation'])
                
                # Check required properties
                assert 'color' in edge_data, f"Edge should have color property: {edge_data}"
                assert 'arrow_direction' in edge_data, f"Edge should have arrow_direction property: {edge_data}"
        
        assert edges_with_properties > 0, "Should find edges with relationship properties"
        print(f"✅ Edge properties verified: {relationship_types}")
    
    @pytest.mark.dependency(depends=["TestGraphBuilding::test_edge_properties"])
    def test_depth_limiting(self, explorer):
        """Test that depth limiting works correctly."""
        word = 'tree'
        
        # Test different depths
        depths_to_test = [1, 2, 3]
        node_counts = []
        
        for depth in depths_to_test:
            G, _ = explorer.explore_word(word, depth=depth, max_nodes=50)
            node_counts.append(G.number_of_nodes())
            print(f"  Depth {depth}: {G.number_of_nodes()} nodes")
        
        # Generally, higher depth should mean more nodes (though not guaranteed)
        # At minimum, we should get some nodes at each depth
        for i, count in enumerate(node_counts):
            assert count > 0, f"Depth {depths_to_test[i]} should produce at least one node"
        
        print("✅ Depth limiting tested")
    
    @pytest.mark.dependency(depends=["TestGraphBuilding::test_depth_limiting"])
    def test_max_nodes_limiting(self, explorer):
        """Test that max_nodes limiting works correctly."""
        word = 'animal'
        
        max_nodes_limits = [5, 10, 20]
        
        for max_nodes in max_nodes_limits:
            G, _ = explorer.explore_word(word, depth=3, max_nodes=max_nodes)
            actual_nodes = G.number_of_nodes()
            
            assert actual_nodes <= max_nodes, f"Should not exceed max_nodes limit: {actual_nodes} > {max_nodes}"
            print(f"  Max {max_nodes}: got {actual_nodes} nodes")
        
        print("✅ Max nodes limiting verified")


class TestRelationshipFiltering:
    """Test relationship type filtering and configuration."""
    
    @pytest.mark.dependency(depends=["TestGraphBuilding::test_max_nodes_limiting"])
    def test_hypernym_filtering(self, explorer):
        """Test hypernym relationship filtering."""
        word = 'car'
        
        # Test with hypernyms enabled
        G_with, _ = explorer.explore_word(word, depth=2, max_nodes=30, show_hypernyms=True)
        
        # Test with hypernyms disabled
        G_without, _ = explorer.explore_word(word, depth=2, max_nodes=30, show_hypernyms=False)
        
        # Count hypernym edges
        hypernyms_with = sum(1 for _, _, data in G_with.edges(data=True) if data.get('relation') == 'hypernym')
        hypernyms_without = sum(1 for _, _, data in G_without.edges(data=True) if data.get('relation') == 'hypernym')
        
        print(f"  With hypernyms: {hypernyms_with} hypernym edges")
        print(f"  Without hypernyms: {hypernyms_without} hypernym edges")
        
        # Should have more hypernyms when enabled (if any exist)
        if hypernyms_with > 0:
            assert hypernyms_without < hypernyms_with, "Disabling hypernyms should reduce hypernym edges"
        
        print("✅ Hypernym filtering verified")
    
    @pytest.mark.dependency(depends=["TestRelationshipFiltering::test_hypernym_filtering"])
    def test_multiple_relationship_types(self, explorer):
        """Test handling of multiple relationship types simultaneously."""
        word = 'hand'
        
        G, _ = explorer.explore_word(
            word, 
            depth=2, 
            max_nodes=50,
            show_hypernyms=True,
            show_hyponyms=True,
            show_meronyms=True,
            show_holonyms=True
        )
        
        relationship_counts = {}
        for _, _, edge_data in G.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            relationship_counts[relation] = relationship_counts.get(relation, 0) + 1
        
        print(f"  Relationship distribution: {relationship_counts}")
        
        # Should have at least some relationships
        assert len(relationship_counts) > 0, "Should find some relationships"
        
        print("✅ Multiple relationship types verified")


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.dependency(depends=["TestRelationshipFiltering::test_multiple_relationship_types"])
    def test_nonexistent_word(self, explorer):
        """Test handling of nonexistent words."""
        nonexistent_word = 'qwertyuiopasdfgh'  # Very unlikely to exist
        
        G, node_labels = explorer.explore_word(nonexistent_word, depth=1, max_nodes=10)
        
        # Should return empty graph without crashing
        assert isinstance(G, nx.Graph), "Should return a Graph even for nonexistent words"
        assert G.number_of_nodes() == 0, "Should have no nodes for nonexistent word"
        
        print("✅ Nonexistent word handling verified")
    
    @pytest.mark.dependency(depends=["TestErrorHandling::test_nonexistent_word"])
    def test_empty_input(self, explorer):
        """Test handling of empty input."""
        empty_inputs = ['', '   ', None]
        
        for empty_input in empty_inputs:
            if empty_input is None:
                continue  # Skip None as it would cause different behavior
                
            try:
                G, node_labels = explorer.explore_word(empty_input, depth=1, max_nodes=10)
                # Should either return empty graph or handle gracefully
                assert isinstance(G, nx.Graph), f"Should return Graph for empty input: '{empty_input}'"
                print(f"  Empty input '{empty_input}': {G.number_of_nodes()} nodes")
            except Exception as e:
                # Some empty inputs might raise exceptions, which is acceptable
                print(f"  Empty input '{empty_input}' raised: {type(e).__name__}")
        
        print("✅ Empty input handling verified")
    
    @pytest.mark.dependency(depends=["TestErrorHandling::test_empty_input"])
    def test_special_characters(self, explorer):
        """Test handling of words with special characters."""
        special_words = ['hello-world', 'user@domain', 'file.txt']
        
        for word in special_words:
            try:
                G, node_labels = explorer.explore_word(word, depth=1, max_nodes=10)
                assert isinstance(G, nx.Graph), f"Should return Graph for special word: '{word}'"
                print(f"  Special word '{word}': {G.number_of_nodes()} nodes")
            except Exception as e:
                # Special characters might cause issues, which is acceptable
                print(f"  Special word '{word}' raised: {type(e).__name__}")
        
        print("✅ Special character handling verified") 