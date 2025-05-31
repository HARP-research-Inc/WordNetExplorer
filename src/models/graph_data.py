"""
Graph data models for encapsulating graph structures.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple
import networkx as nx
from enum import Enum


class NodeType(Enum):
    """Enumeration of node types."""
    MAIN = 'main'
    SYNSET = 'synset'
    WORD = 'word'
    WORD_SENSE = 'word_sense'
    BREADCRUMB = 'breadcrumb'
    UNKNOWN = 'unknown'


class EdgeType(Enum):
    """Enumeration of edge types."""
    SENSE = 'sense'
    HYPERNYM = 'hypernym'
    HYPONYM = 'hyponym'
    MERONYM = 'meronym'
    HOLONYM = 'holonym'
    ANTONYM = 'antonym'
    SIMILAR_TO = 'similar_to'
    ENTAILMENT = 'entailment'
    CAUSE = 'cause'
    ATTRIBUTE = 'attribute'
    ALSO_SEE = 'also_see'
    UNKNOWN = 'unknown'


@dataclass
class NodeData:
    """Data for a single node in the graph."""
    node_id: str
    node_type: NodeType
    label: str = ""
    
    # Common attributes
    word: Optional[str] = None
    definition: Optional[str] = None
    
    # Synset-specific attributes
    synset_name: Optional[str] = None
    pos: Optional[str] = None
    
    # Word sense attributes
    sense_number: Optional[int] = None
    
    # Breadcrumb attributes
    original_word: Optional[str] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for NetworkX compatibility."""
        result = {
            'node_type': self.node_type.value,
            'label': self.label
        }
        
        # Add optional fields if present
        if self.word is not None:
            result['word'] = self.word
        if self.definition is not None:
            result['definition'] = self.definition
        if self.synset_name is not None:
            result['synset_name'] = self.synset_name
        if self.pos is not None:
            result['pos'] = self.pos
        if self.sense_number is not None:
            result['sense_number'] = self.sense_number
        if self.original_word is not None:
            result['original_word'] = self.original_word
        
        # Add metadata
        result.update(self.metadata)
        
        return result
    
    @classmethod
    def from_dict(cls, node_id: str, data: Dict[str, Any]) -> 'NodeData':
        """Create NodeData from dictionary."""
        # Extract node type
        node_type_str = data.get('node_type', 'unknown')
        try:
            node_type = NodeType(node_type_str)
        except ValueError:
            node_type = NodeType.UNKNOWN
        
        # Extract known fields
        return cls(
            node_id=node_id,
            node_type=node_type,
            label=data.get('label', ''),
            word=data.get('word'),
            definition=data.get('definition'),
            synset_name=data.get('synset_name'),
            pos=data.get('pos'),
            sense_number=data.get('sense_number'),
            original_word=data.get('original_word'),
            metadata={k: v for k, v in data.items() 
                     if k not in ['node_type', 'label', 'word', 'definition', 
                                 'synset_name', 'pos', 'sense_number', 'original_word']}
        )


@dataclass
class EdgeData:
    """Data for a single edge in the graph."""
    source: str
    target: str
    edge_type: EdgeType
    
    # Visual properties
    color: Optional[str] = None
    arrow_direction: str = 'to'
    weight: float = 1.0
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for NetworkX compatibility."""
        result = {
            'relation': self.edge_type.value,
            'arrow_direction': self.arrow_direction,
            'weight': self.weight
        }
        
        if self.color is not None:
            result['color'] = self.color
        
        result.update(self.metadata)
        return result
    
    @classmethod
    def from_dict(cls, source: str, target: str, data: Dict[str, Any]) -> 'EdgeData':
        """Create EdgeData from dictionary."""
        # Extract edge type
        edge_type_str = data.get('relation', 'unknown')
        try:
            edge_type = EdgeType(edge_type_str)
        except ValueError:
            edge_type = EdgeType.UNKNOWN
        
        return cls(
            source=source,
            target=target,
            edge_type=edge_type,
            color=data.get('color'),
            arrow_direction=data.get('arrow_direction', 'to'),
            weight=data.get('weight', 1.0),
            metadata={k: v for k, v in data.items()
                     if k not in ['relation', 'color', 'arrow_direction', 'weight']}
        )


@dataclass
class GraphData:
    """Encapsulates a graph and its node labels."""
    graph: nx.Graph
    node_labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_node(self, node_data: NodeData) -> None:
        """Add a node to the graph."""
        self.graph.add_node(node_data.node_id, **node_data.to_dict())
        if node_data.label:
            self.node_labels[node_data.node_id] = node_data.label
    
    def add_edge(self, edge_data: EdgeData) -> None:
        """Add an edge to the graph."""
        self.graph.add_edge(edge_data.source, edge_data.target, **edge_data.to_dict())
    
    def get_node_data(self, node_id: str) -> Optional[NodeData]:
        """Get NodeData for a specific node."""
        if node_id not in self.graph.nodes:
            return None
        
        node_dict = dict(self.graph.nodes[node_id])
        return NodeData.from_dict(node_id, node_dict)
    
    def get_edge_data(self, source: str, target: str) -> Optional[EdgeData]:
        """Get EdgeData for a specific edge."""
        if not self.graph.has_edge(source, target):
            return None
        
        edge_dict = self.graph[source][target]
        return EdgeData.from_dict(source, target, edge_dict)
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[NodeData]:
        """Get all nodes of a specific type."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get('node_type') == node_type.value:
                nodes.append(NodeData.from_dict(node_id, data))
        return nodes
    
    def get_edges_by_type(self, edge_type: EdgeType) -> List[EdgeData]:
        """Get all edges of a specific type."""
        edges = []
        for source, target, data in self.graph.edges(data=True):
            if data.get('relation') == edge_type.value:
                edges.append(EdgeData.from_dict(source, target, data))
        return edges
    
    @property
    def num_nodes(self) -> int:
        """Get number of nodes in the graph."""
        return self.graph.number_of_nodes()
    
    @property
    def num_edges(self) -> int:
        """Get number of edges in the graph."""
        return self.graph.number_of_edges()
    
    def to_tuple(self) -> Tuple[nx.Graph, Dict[str, str]]:
        """Convert to tuple for backward compatibility."""
        return self.graph, self.node_labels
    
    @classmethod
    def from_tuple(cls, graph: nx.Graph, node_labels: Dict[str, str]) -> 'GraphData':
        """Create from tuple for backward compatibility."""
        return cls(graph=graph, node_labels=node_labels) 