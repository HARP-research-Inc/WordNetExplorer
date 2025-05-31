"""
WordNet Explorer Core Module

Main interface for exploring WordNet relationships using the modularized components.
"""

from typing import Tuple, Dict, Optional
import networkx as nx

from src.wordnet import initialize_wordnet, get_synsets_for_word
from src.wordnet.relationships import RelationshipConfig
from src.graph import GraphBuilder, GraphConfig, GraphVisualizer, VisualizationConfig


class WordNetExplorer:
    """Main interface for WordNet exploration functionality."""
    
    def __init__(self):
        """Initialize the WordNet Explorer."""
        # Ensure NLTK data is available with robust initialization
        if not initialize_wordnet():
            raise RuntimeError("Failed to initialize WordNet. Please check your internet connection and try again.")
        
        # Initialize default configurations
        self.graph_config = GraphConfig()
        self.viz_config = VisualizationConfig()
        
        # Initialize components
        self.graph_builder = GraphBuilder(self.graph_config)
        self.visualizer = GraphVisualizer(self.viz_config)
    
    def explore_word(self, word: str, 
                    depth: int = 1,
                    sense_number: int = None,
                    max_nodes: int = 100,
                    max_branches: int = 5,
                    min_frequency: int = 0,
                    pos_filter: list = None,
                    enable_clustering: bool = False,
                    enable_cross_connections: bool = True,
                    simplified_mode: bool = False,
                    show_word_senses: bool = True,
                    **relationship_kwargs) -> Tuple[nx.Graph, Dict]:
        """
        Explore a word and build its relationship graph.
        
        Args:
            word: The word to explore
            depth: How many levels deep to explore relationships
            sense_number: Specific sense number to display (1-based, None for all)
            max_nodes: Maximum number of nodes to include in graph
            max_branches: Maximum branches per node
            min_frequency: Minimum word frequency to include
            pos_filter: List of parts of speech to include
            enable_clustering: Whether to enable node clustering
            enable_cross_connections: Whether to find cross-connections between nodes
            simplified_mode: Whether to use simplified rendering
            show_word_senses: Whether to show word senses (lemmas) for synsets
            **relationship_kwargs: Relationship configuration (show_hypernyms, etc.)
            
        Returns:
            Tuple of (NetworkX graph, node labels dict)
        """
        # Create relationship configuration
        relationship_config = RelationshipConfig(**relationship_kwargs)
        
        # Create graph configuration
        config = GraphConfig(
            depth=depth,
            sense_number=sense_number,
            relationship_config=relationship_config,
            max_nodes=max_nodes,
            max_branches=max_branches,
            min_frequency=min_frequency,
            pos_filter=pos_filter,
            enable_clustering=enable_clustering,
            enable_cross_connections=enable_cross_connections,
            simplified_mode=simplified_mode,
            show_word_senses=show_word_senses
        )
        
        # Build and return the graph
        builder = GraphBuilder(config)
        return builder.build_graph(word)
    
    def explore_synset(self, synset_name: str, 
                      depth: int = 1,
                      max_nodes: int = 100,
                      max_branches: int = 5,
                      min_frequency: int = 0,
                      pos_filter: list = None,
                      enable_clustering: bool = False,
                      enable_cross_connections: bool = True,
                      simplified_mode: bool = False,
                      show_word_senses: bool = True,
                      **relationship_kwargs) -> Tuple[nx.Graph, Dict]:
        """
        Explore a synset and build its relationship graph, focusing on the synset node.
        
        Args:
            synset_name: The synset name to explore (e.g., 'dog.n.01')
            depth: How many levels deep to explore relationships
            max_nodes: Maximum number of nodes to include in graph
            max_branches: Maximum branches per node
            min_frequency: Minimum word frequency to include
            pos_filter: List of parts of speech to include
            enable_clustering: Whether to enable node clustering
            enable_cross_connections: Whether to find cross-connections between nodes
            simplified_mode: Whether to use simplified rendering
            show_word_senses: Whether to show word senses (lemmas) for synsets
            **relationship_kwargs: Relationship configuration (show_hypernyms, etc.)
            
        Returns:
            Tuple of (NetworkX graph, node labels dict)
        """
        # Create relationship configuration
        relationship_config = RelationshipConfig(**relationship_kwargs)
        
        # Create graph configuration
        config = GraphConfig(
            depth=depth,
            sense_number=None,  # Not applicable for synset search
            relationship_config=relationship_config,
            max_nodes=max_nodes,
            max_branches=max_branches,
            min_frequency=min_frequency,
            pos_filter=pos_filter,
            enable_clustering=enable_clustering,
            enable_cross_connections=enable_cross_connections,
            simplified_mode=simplified_mode,
            show_word_senses=show_word_senses
        )
        
        # Build and return the graph
        builder = GraphBuilder(config)
        return builder.build_synset_graph(synset_name)
    
    def visualize_graph(self, G: nx.Graph, node_labels: Dict, word: str,
                       save_path: str = None,
                       layout_type: str = "Force-directed (default)",
                       node_size_multiplier: float = 1.0,
                       enable_physics: bool = True,
                       spring_strength: float = 0.04,
                       central_gravity: float = 0.3,
                       show_labels: bool = True,
                       edge_width: int = 2,
                       color_scheme: str = "Default") -> Optional[str]:
        """
        Create an interactive visualization of the graph.
        
        Args:
            G: NetworkX graph to visualize
            node_labels: Dictionary mapping node IDs to display labels
            word: The word being visualized
            save_path: Optional path to save the visualization
            layout_type: Layout algorithm to use
            node_size_multiplier: Multiplier for node sizes
            enable_physics: Whether to enable physics simulation
            spring_strength: Strength of spring forces
            central_gravity: Central gravity force
            show_labels: Whether to show node labels
            edge_width: Width of edges
            color_scheme: Color scheme to use
            
        Returns:
            HTML string if not saving to file, file path if saving
        """
        # Update visualization configuration
        viz_config = VisualizationConfig(
            layout_type=layout_type,
            node_size_multiplier=node_size_multiplier,
            enable_physics=enable_physics,
            spring_strength=spring_strength,
            central_gravity=central_gravity,
            show_labels=show_labels,
            edge_width=edge_width,
            color_scheme=color_scheme
        )
        
        # Update visualizer with new config
        self.visualizer.config = viz_config
        
        # Create visualization
        return self.visualizer.visualize_interactive(G, node_labels, word, save_path)
    
    def visualize_static(self, G: nx.Graph, node_labels: Dict, word: str,
                        save_path: str = None) -> Optional[str]:
        """
        Create a static matplotlib visualization of the graph.
        
        Args:
            G: NetworkX graph to visualize
            node_labels: Dictionary mapping node IDs to display labels
            word: The word being visualized
            save_path: Optional path to save the visualization
            
        Returns:
            File path if saving, None otherwise
        """
        return self.visualizer.visualize_static(G, node_labels, word, save_path)
    
    def get_word_info(self, word: str) -> Dict:
        """
        Get comprehensive information about a word.
        
        Args:
            word: The word to analyze
            
        Returns:
            Dictionary containing word information
        """
        synsets = get_synsets_for_word(word)
        
        if not synsets:
            return {
                'word': word,
                'found': False,
                'synsets': [],
                'total_senses': 0
            }
        
        synset_info = []
        for i, synset in enumerate(synsets, 1):
            info = {
                'sense_number': i,
                'synset_name': synset.name(),
                'definition': synset.definition(),
                'pos': synset.pos(),
                'lemma_names': synset.lemma_names(),
                'examples': synset.examples() if hasattr(synset, 'examples') else []
            }
            synset_info.append(info)
        
        return {
            'word': word,
            'found': True,
            'synsets': synset_info,
            'total_senses': len(synsets)
        }
    
    def build_focused_graph(self, center_word: str, previous_word: str = None,
                           previous_relation: str = None, **kwargs) -> Tuple[nx.Graph, Dict]:
        """
        Build a focused graph with breadcrumb navigation.
        
        Args:
            center_word: The word to focus on
            previous_word: Previous word for breadcrumb navigation
            previous_relation: Relationship to previous word
            **kwargs: Additional arguments passed to explore_word
            
        Returns:
            Tuple of (graph, node_labels)
        """
        # Build the main graph
        G, node_labels = self.explore_word(center_word, **kwargs)
        
        # Add breadcrumb if previous word is specified
        if previous_word and G.number_of_nodes() > 0:
            breadcrumb_node = f"{previous_word}_breadcrumb"
            G.add_node(breadcrumb_node, 
                      node_type='breadcrumb',
                      original_word=previous_word)
            node_labels[breadcrumb_node] = f"← {previous_word.upper()}"
            
            # Connect breadcrumb to a main node if available
            main_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'main']
            if main_nodes:
                G.add_edge(breadcrumb_node, main_nodes[0], 
                          relation='breadcrumb', 
                          color='#CCCCCC',
                          arrow_direction='to')
        
        return G, node_labels
    
    def find_path_between_synsets(self, from_synset, to_synset, max_depth=10):
        """
        Find a path between two synsets using hypernym relationships.
        
        Args:
            from_synset: Source synset
            to_synset: Target synset
            max_depth: Maximum search depth
            
        Returns:
            list: Path of synsets from source to target, or None if no path found
        """
        from collections import deque
        
        # Handle same synset
        if from_synset == to_synset:
            return [from_synset]
        
        # BFS to find shortest path
        queue = deque([(from_synset, [from_synset])])
        visited = {from_synset}
        
        while queue and len(visited) < 100000:  # Limit to prevent infinite loops
            current, path = queue.popleft()
            
            if len(path) > max_depth:
                continue
            
            # Try direct relationships
            neighbors = []
            
            # Add hypernyms (more general)
            neighbors.extend(current.hypernyms())
            
            # Add hyponyms (more specific)
            neighbors.extend(current.hyponyms())
            
            # Add sister terms (shared hypernyms)
            for hypernym in current.hypernyms():
                neighbors.extend(hypernym.hyponyms())
            
            # Check each neighbor
            for neighbor in neighbors:
                if neighbor == to_synset:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        # If no direct path found, try to find common hypernyms
        # Get all hypernyms of both synsets
        from_hypernyms = set()
        to_hypernyms = set()
        
        # Collect hypernyms up to max_depth/2 levels
        current_level = {from_synset}
        for _ in range(max_depth // 2):
            next_level = set()
            for synset in current_level:
                hypernyms = synset.hypernyms()
                next_level.update(hypernyms)
                from_hypernyms.update(hypernyms)
            current_level = next_level
            if not current_level:
                break
        
        current_level = {to_synset}
        for _ in range(max_depth // 2):
            next_level = set()
            for synset in current_level:
                hypernyms = synset.hypernyms()
                next_level.update(hypernyms)
                to_hypernyms.update(hypernyms)
            current_level = next_level
            if not current_level:
                break
        
        # Find common hypernyms
        common = from_hypernyms & to_hypernyms
        
        if common:
            # Find the lowest common hypernym (closest to both)
            best_common = None
            best_distance = float('inf')
            
            for common_synset in common:
                # Calculate combined distance
                from_dist = self._hypernym_distance(from_synset, common_synset)
                to_dist = self._hypernym_distance(to_synset, common_synset)
                total_dist = from_dist + to_dist
                
                if total_dist < best_distance:
                    best_distance = total_dist
                    best_common = common_synset
            
            if best_common:
                # Build path through common hypernym
                path_to_common = self._path_to_hypernym(from_synset, best_common)
                path_from_common = self._path_to_hypernym(to_synset, best_common)
                
                if path_to_common and path_from_common:
                    # Reverse the second path and remove duplicate common node
                    return path_to_common + path_from_common[-2::-1]
        
        return None
    
    def _hypernym_distance(self, synset, hypernym):
        """Calculate the distance from synset to its hypernym."""
        if synset == hypernym:
            return 0
        
        distance = 0
        current = {synset}
        visited = {synset}
        
        while current and distance < 20:
            distance += 1
            next_level = set()
            
            for s in current:
                for h in s.hypernyms():
                    if h == hypernym:
                        return distance
                    if h not in visited:
                        visited.add(h)
                        next_level.add(h)
            
            current = next_level
        
        return float('inf')
    
    def _path_to_hypernym(self, synset, hypernym):
        """Find the path from synset to its hypernym."""
        if synset == hypernym:
            return [synset]
        
        # BFS to find path
        from collections import deque
        queue = deque([(synset, [synset])])
        visited = {synset}
        
        while queue:
            current, path = queue.popleft()
            
            for h in current.hypernyms():
                if h == hypernym:
                    return path + [h]
                
                if h not in visited:
                    visited.add(h)
                    queue.append((h, path + [h]))
        
        return None 