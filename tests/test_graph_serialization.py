"""
Test suite for graph serialization functionality.
"""

import pytest
import networkx as nx
import json
import os
from src.graph import (
    GraphBuilder, GraphConfig, GraphSerializer, 
    GraphVisualizer, VisualizationConfig
)


class TestGraphSerialization:
    """Test graph serialization and deserialization."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.builder = GraphBuilder()
        self.serializer = GraphSerializer()
        self.test_word = "dog"
    
    def test_basic_serialization(self):
        """Test basic graph serialization and deserialization."""
        print("\n🔍 Testing basic graph serialization...")
        
        # Build a test graph
        G, node_labels = self.builder.build_graph(self.test_word)
        
        # Serialize to JSON
        json_str = self.serializer.serialize_graph(G, node_labels)
        
        # Verify JSON structure
        data = json.loads(json_str)
        assert 'nodes' in data
        assert 'edges' in data
        assert 'node_labels' in data
        assert 'metadata' in data
        
        # Verify node data
        assert len(data['nodes']) == G.number_of_nodes()
        for node_id, attrs in data['nodes'].items():
            assert node_id in G.nodes()
            for key, value in attrs.items():
                assert key in G.nodes[node_id]
        
        # Verify edge data
        assert len(data['edges']) == G.number_of_edges()
        for edge in data['edges']:
            assert 'source' in edge
            assert 'target' in edge
            assert 'attributes' in edge
            assert G.has_edge(edge['source'], edge['target'])
        
        # Verify node labels
        assert len(data['node_labels']) == len(node_labels)
        for node_id, label in data['node_labels'].items():
            assert node_id in node_labels
            assert label == node_labels[node_id]
        
        print(f"✅ Verified JSON structure with {len(data['nodes'])} nodes and {len(data['edges'])} edges")
    
    def test_round_trip_serialization(self):
        """Test that serialization and deserialization preserves all data."""
        print("\n🔍 Testing round-trip serialization...")
        
        # Build a test graph
        G, node_labels = self.builder.build_graph(self.test_word)
        
        # Add some metadata
        metadata = {
            'word': self.test_word,
            'description': 'Test graph for serialization',
            'version': '1.0'
        }
        
        # Serialize to JSON
        json_str = self.serializer.serialize_graph(G, node_labels, metadata)
        
        # Deserialize back
        G2, node_labels2, metadata2 = self.serializer.deserialize_graph(json_str)
        
        # Verify graph structure
        assert G2.number_of_nodes() == G.number_of_nodes()
        assert G2.number_of_edges() == G.number_of_edges()
        
        # Verify node attributes
        for node_id in G.nodes():
            assert node_id in G2.nodes()
            for key, value in G.nodes[node_id].items():
                if isinstance(value, (str, int, float, bool, list, dict)):
                    assert G2.nodes[node_id][key] == value
                else:
                    assert str(G2.nodes[node_id][key]) == str(value)
        
        # Verify edge attributes
        for source, target, attrs in G.edges(data=True):
            assert G2.has_edge(source, target)
            for key, value in attrs.items():
                if isinstance(value, (str, int, float, bool, list, dict)):
                    assert G2.edges[source, target][key] == value
                else:
                    assert str(G2.edges[source, target][key]) == str(value)
        
        # Verify node labels
        assert node_labels2 == node_labels
        
        # Verify metadata
        assert metadata2['word'] == metadata['word']
        assert metadata2['description'] == metadata['description']
        assert metadata2['version'] == metadata['version']
        
        print("✅ Verified round-trip serialization preserves all data")
    
    def test_file_io(self):
        """Test saving and loading graphs to/from files."""
        print("\n🔍 Testing file I/O operations...")
        
        # Build a test graph
        G, node_labels = self.builder.build_graph(self.test_word)
        
        # Add metadata
        metadata = {
            'word': self.test_word,
            'description': 'Test graph for file I/O'
        }
        
        # Save to file
        test_file = 'test_graph.json'
        try:
            self.serializer.save_graph(G, node_labels, test_file, metadata)
            
            # Verify file exists
            assert os.path.exists(test_file)
            
            # Load from file
            G2, node_labels2, metadata2 = self.serializer.load_graph(test_file)
            
            # Verify loaded data
            assert G2.number_of_nodes() == G.number_of_nodes()
            assert G2.number_of_edges() == G.number_of_edges()
            assert node_labels2 == node_labels
            assert metadata2['word'] == metadata['word']
            assert metadata2['description'] == metadata['description']
            
            print("✅ Verified file I/O operations")
            
        finally:
            # Clean up test file
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_visualization_config_preservation(self):
        """Test that visualization configuration is preserved."""
        print("\n🔍 Testing visualization config preservation...")
        
        # Create custom visualization config
        config = VisualizationConfig(
            layout_type="Hierarchical",
            node_size_multiplier=1.5,
            enable_physics=False,
            spring_strength=0.05,
            central_gravity=0.4,
            show_labels=True,
            edge_width=3,
            color_scheme="Vibrant"
        )
        
        # Create serializer with custom config
        serializer = GraphSerializer(config)
        
        # Build and serialize graph
        G, node_labels = self.builder.build_graph(self.test_word)
        json_str = serializer.serialize_graph(G, node_labels)
        
        # Deserialize
        G2, node_labels2, metadata2 = serializer.deserialize_graph(json_str)
        
        # Verify config was preserved
        assert 'visualization_config' in metadata2
        config_dict = metadata2['visualization_config']
        assert config_dict['layout_type'] == config.layout_type
        assert config_dict['node_size_multiplier'] == config.node_size_multiplier
        assert config_dict['enable_physics'] == config.enable_physics
        assert config_dict['spring_strength'] == config.spring_strength
        assert config_dict['central_gravity'] == config.central_gravity
        assert config_dict['show_labels'] == config.show_labels
        assert config_dict['edge_width'] == config.edge_width
        assert config_dict['color_scheme'] == config.color_scheme
        
        print("✅ Verified visualization config preservation")
    
    def test_wordnet_connectivity(self):
        """Test that WordNet connectivity is preserved."""
        print("\n🔍 Testing WordNet connectivity preservation...")
        
        # Build a test graph
        G, node_labels = self.builder.build_graph(self.test_word)
        
        # Serialize and deserialize
        json_str = self.serializer.serialize_graph(G, node_labels)
        G2, node_labels2, _ = self.serializer.deserialize_graph(json_str)
        
        # Verify synset names are preserved
        for node_id, attrs in G.nodes(data=True):
            if attrs.get('node_type') == 'synset':
                assert 'synset_name' in attrs
                synset_name = attrs['synset_name']
                assert G2.nodes[node_id]['synset_name'] == synset_name
        
        # Verify relationship types are preserved
        for source, target, attrs in G.edges(data=True):
            assert 'relation' in attrs
            relation = attrs['relation']
            assert G2.edges[source, target]['relation'] == relation
            
            # Verify arrow direction
            if 'arrow_direction' in attrs:
                arrow_dir = attrs['arrow_direction']
                assert G2.edges[source, target]['arrow_direction'] == arrow_dir
        
        print("✅ Verified WordNet connectivity preservation")


if __name__ == "__main__":
    # Run the tests with verbose output
    pytest.main([__file__, "-v", "-s"]) 