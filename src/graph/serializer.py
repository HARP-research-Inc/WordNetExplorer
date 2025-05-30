"""
Graph Serializer Module

Handles JSON serialization and deserialization of WordNet graphs,
preserving both WordNet connectivity and display data.
"""

import json
import networkx as nx
from typing import Dict, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from .nodes import NodeType
from .visualizer import VisualizationConfig


@dataclass
class SerializedGraph:
    """Container for serialized graph data."""
    nodes: Dict[str, Dict[str, Any]]
    edges: list[Dict[str, Any]]
    node_labels: Dict[str, str]
    metadata: Dict[str, Any]


class GraphSerializer:
    """Handles serialization and deserialization of WordNet graphs."""
    
    def __init__(self, visualization_config: Optional[VisualizationConfig] = None):
        """Initialize serializer with optional visualization config."""
        self.visualization_config = visualization_config or VisualizationConfig()
    
    def serialize_graph(self, G: nx.Graph, node_labels: Dict[str, str], 
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Serialize a graph to JSON format.
        
        Args:
            G: NetworkX graph to serialize
            node_labels: Dictionary of node labels
            metadata: Optional metadata about the graph
            
        Returns:
            JSON string containing serialized graph data
        """
        # Prepare nodes with all attributes
        nodes = {}
        for node_id, attrs in G.nodes(data=True):
            # Ensure all attributes are JSON-serializable
            serialized_attrs = {}
            for key, value in attrs.items():
                if isinstance(value, (str, int, float, bool, list, dict)):
                    serialized_attrs[key] = value
                else:
                    serialized_attrs[key] = str(value)
            nodes[node_id] = serialized_attrs
        
        # Prepare edges with all attributes
        edges = []
        for source, target, attrs in G.edges(data=True):
            # Ensure all attributes are JSON-serializable
            serialized_attrs = {}
            for key, value in attrs.items():
                if isinstance(value, (str, int, float, bool, list, dict)):
                    serialized_attrs[key] = value
                else:
                    serialized_attrs[key] = str(value)
            
            edge_data = {
                'source': source,
                'target': target,
                'attributes': serialized_attrs
            }
            edges.append(edge_data)
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Add search history if available (from Streamlit session state)
        try:
            import streamlit as st
            if hasattr(st, 'session_state') and 'search_history' in st.session_state:
                metadata['search_history'] = st.session_state.search_history
        except ImportError:
            # Streamlit not available (e.g., in standalone use)
            pass
        
        # Add visualization config to metadata
        metadata['visualization_config'] = asdict(self.visualization_config)
        
        # Create serialized graph container
        serialized = SerializedGraph(
            nodes=nodes,
            edges=edges,
            node_labels=node_labels,
            metadata=metadata
        )
        
        # Convert to JSON
        return json.dumps(asdict(serialized), indent=2)
    
    def deserialize_graph(self, json_str: str) -> Tuple[nx.Graph, Dict[str, str], Dict[str, Any]]:
        """
        Deserialize a graph from JSON format.
        
        Args:
            json_str: JSON string containing serialized graph data
            
        Returns:
            Tuple of (NetworkX graph, node labels dictionary, metadata dictionary)
        """
        # Parse JSON
        data = json.loads(json_str)
        serialized = SerializedGraph(**data)
        
        # Create new graph
        G = nx.Graph()
        
        # Add nodes with attributes
        for node_id, attrs in serialized.nodes.items():
            G.add_node(node_id, **attrs)
        
        # Add edges with attributes
        for edge in serialized.edges:
            source = edge['source']
            target = edge['target']
            attrs = edge['attributes']
            G.add_edge(source, target, **attrs)
        
        # Extract visualization config if present
        metadata = serialized.metadata
        if 'visualization_config' in metadata:
            config_dict = metadata.pop('visualization_config')
            self.visualization_config = VisualizationConfig(**config_dict)
        
        return G, serialized.node_labels, metadata
    
    def save_graph(self, G: nx.Graph, node_labels: Dict[str, str], 
                  filepath: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Save a graph to a JSON file.
        
        Args:
            G: NetworkX graph to save
            node_labels: Dictionary of node labels
            filepath: Path to save the JSON file
            metadata: Optional metadata about the graph
        """
        json_str = self.serialize_graph(G, node_labels, metadata)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
    
    def load_graph(self, filepath: str) -> Tuple[nx.Graph, Dict[str, str], Dict[str, Any]]:
        """
        Load a graph from a JSON file.
        
        Args:
            filepath: Path to the JSON file
            
        Returns:
            Tuple of (NetworkX graph, node labels dictionary, metadata dictionary)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            json_str = f.read()
        return self.deserialize_graph(json_str) 