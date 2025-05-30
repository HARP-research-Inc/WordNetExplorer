"""Graph entity representing a semantic network."""

from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional, Tuple, FrozenSet
from collections import defaultdict
from .synset import Synset
from .relationship import Relationship, RelationshipType
from .word import Word


@dataclass
class Graph:
    """
    Mutable Graph entity representing a semantic network.
    
    This is an aggregate root in DDD terms - it maintains consistency
    of the graph structure.
    """
    _nodes: Dict[str, Synset] = field(default_factory=dict)
    _edges: Dict[str, Set[Relationship]] = field(default_factory=lambda: defaultdict(set))
    _words: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    
    def add_node(self, synset: Synset) -> None:
        """
        Add a synset node to the graph.
        
        Args:
            synset: The Synset entity to add
        """
        if not isinstance(synset, Synset):
            raise TypeError(f"Node must be a Synset, got {type(synset)}")
        
        self._nodes[synset.name] = synset
        
        # Index by lemmas for quick lookup
        for lemma in synset.lemmas:
            self._words[lemma.lower()].add(synset.name)
    
    def add_edge(self, relationship: Relationship) -> None:
        """
        Add a relationship edge to the graph.
        
        Args:
            relationship: The Relationship entity to add
        """
        if not isinstance(relationship, Relationship):
            raise TypeError(f"Edge must be a Relationship, got {type(relationship)}")
        
        # Ensure both nodes exist
        if relationship.source_synset_name not in self._nodes:
            raise ValueError(f"Source synset '{relationship.source_synset_name}' not in graph")
        if relationship.target_synset_name not in self._nodes:
            raise ValueError(f"Target synset '{relationship.target_synset_name}' not in graph")
        
        self._edges[relationship.source_synset_name].add(relationship)
        
        # Add inverse for symmetric relationships
        if relationship.is_symmetric:
            inverse = Relationship(
                source_synset_name=relationship.target_synset_name,
                target_synset_name=relationship.source_synset_name,
                type=relationship.type
            )
            self._edges[relationship.target_synset_name].add(inverse)
    
    def get_node(self, synset_name: str) -> Optional[Synset]:
        """Get a synset node by name."""
        return self._nodes.get(synset_name)
    
    def get_nodes_by_word(self, word: Word) -> List[Synset]:
        """Get all synsets containing a word."""
        synset_names = self._words.get(word.normalized_text, set())
        return [self._nodes[name] for name in synset_names if name in self._nodes]
    
    def get_edges(self, synset_name: str) -> Set[Relationship]:
        """Get all relationships from a synset."""
        return self._edges.get(synset_name, set())
    
    def get_neighbors(self, synset_name: str,
                     relationship_types: Optional[Set[RelationshipType]] = None) -> List[Synset]:
        """
        Get neighboring synsets connected by specified relationship types.
        
        Args:
            synset_name: Source synset name
            relationship_types: Optional set of relationship types to filter by
            
        Returns:
            List of neighboring Synset entities
        """
        edges = self.get_edges(synset_name)
        neighbors = []
        
        for edge in edges:
            if relationship_types is None or edge.type in relationship_types:
                neighbor = self.get_node(edge.target_synset_name)
                if neighbor:
                    neighbors.append(neighbor)
        
        return neighbors
    
    @property
    def nodes(self) -> List[Synset]:
        """Get all nodes in the graph."""
        return list(self._nodes.values())
    
    @property
    def edges(self) -> List[Relationship]:
        """Get all edges in the graph."""
        all_edges = []
        for edge_set in self._edges.values():
            all_edges.extend(edge_set)
        return all_edges
    
    @property
    def node_count(self) -> int:
        """Get the number of nodes."""
        return len(self._nodes)
    
    @property
    def edge_count(self) -> int:
        """Get the number of edges."""
        return sum(len(edges) for edges in self._edges.values())
    
    def has_node(self, synset_name: str) -> bool:
        """Check if a synset exists in the graph."""
        return synset_name in self._nodes
    
    def has_edge(self, source: str, target: str) -> bool:
        """Check if an edge exists between two synsets."""
        edges = self._edges.get(source, set())
        return any(edge.target_synset_name == target for edge in edges)
    
    def get_connected_components(self) -> List[Set[str]]:
        """
        Get connected components in the graph.
        
        Returns:
            List of sets, each containing synset names in a component
        """
        visited = set()
        components = []
        
        def dfs(node: str, component: Set[str]):
            if node in visited:
                return
            visited.add(node)
            component.add(node)
            
            for edge in self.get_edges(node):
                dfs(edge.target_synset_name, component)
        
        for node in self._nodes:
            if node not in visited:
                component = set()
                dfs(node, component)
                components.append(component)
        
        return components
    
    def get_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find shortest path between two synsets using BFS.
        
        Args:
            source: Source synset name
            target: Target synset name
            
        Returns:
            List of synset names in the path, or None if no path exists
        """
        if source not in self._nodes or target not in self._nodes:
            return None
        
        if source == target:
            return [source]
        
        from collections import deque
        
        queue = deque([(source, [source])])
        visited = {source}
        
        while queue:
            current, path = queue.popleft()
            
            for edge in self.get_edges(current):
                next_node = edge.target_synset_name
                if next_node not in visited:
                    new_path = path + [next_node]
                    if next_node == target:
                        return new_path
                    queue.append((next_node, new_path))
                    visited.add(next_node)
        
        return None
    
    def get_subgraph(self, synset_names: Set[str]) -> 'Graph':
        """
        Extract a subgraph containing only specified synsets.
        
        Args:
            synset_names: Set of synset names to include
            
        Returns:
            New Graph containing only specified nodes and their edges
        """
        subgraph = Graph()
        
        # Add nodes
        for name in synset_names:
            if name in self._nodes:
                subgraph.add_node(self._nodes[name])
        
        # Add edges between included nodes
        for name in synset_names:
            if name in self._edges:
                for edge in self._edges[name]:
                    if edge.target_synset_name in synset_names:
                        subgraph.add_edge(edge)
        
        return subgraph
    
    @classmethod
    def empty(cls) -> 'Graph':
        """Create an empty graph."""
        return cls()
    
    def __repr__(self) -> str:
        """String representation of the graph."""
        return f"Graph(nodes={self.node_count}, edges={self.edge_count})" 