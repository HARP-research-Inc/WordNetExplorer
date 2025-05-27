"""
WordNet Explorer Core Module

Main interface for exploring WordNet relationships using the modularized components.
"""

from typing import Tuple, Dict, Optional
import networkx as nx

from src.wordnet import download_nltk_data, get_synsets_for_word
from src.wordnet.relationships import RelationshipConfig
from src.graph import GraphBuilder, GraphConfig, GraphVisualizer, VisualizationConfig


class WordNetExplorer:
    """Main interface for WordNet exploration functionality."""
    
    def __init__(self):
        """Initialize the WordNet Explorer."""
        # Ensure NLTK data is available
        download_nltk_data()
        
        # Initialize default configurations
        self.graph_config = GraphConfig()
        self.viz_config = VisualizationConfig()
        
        # Initialize components
        self.graph_builder = GraphBuilder(self.graph_config)
        self.visualizer = GraphVisualizer(self.viz_config)
    
    def explore_word(self, word: str, 
                    depth: int = 1,
                    sense_number: int = None,
                    **relationship_kwargs) -> Tuple[nx.Graph, Dict]:
        """
        Explore a word and build its relationship graph.
        
        Args:
            word: The word to explore
            depth: How many levels deep to explore relationships
            sense_number: Specific sense number to display (1-based, None for all)
            **relationship_kwargs: All relationship type settings
            
        Returns:
            Tuple of (graph, node_labels)
        """
        # Update configuration with all relationship settings
        relationship_config = RelationshipConfig(**relationship_kwargs)
        
        graph_config = GraphConfig(
            depth=depth,
            sense_number=sense_number,
            relationship_config=relationship_config
        )
        
        # Update builder with new config
        self.graph_builder.config = graph_config
        
        # Build and return graph
        return self.graph_builder.build_graph(word)
    
    def explore_synset(self, synset_name: str, 
                      depth: int = 1,
                      **relationship_kwargs) -> Tuple[nx.Graph, Dict]:
        """
        Explore a synset and build its relationship graph, focusing on the synset node.
        
        Args:
            synset_name: The synset name to explore (e.g., 'dog.n.01')
            depth: How many levels deep to explore relationships
            **relationship_kwargs: All relationship type settings
            
        Returns:
            Tuple of (graph, node_labels)
        """
        # Update configuration with all relationship settings
        relationship_config = RelationshipConfig(**relationship_kwargs)
        
        graph_config = GraphConfig(
            depth=depth,
            sense_number=None,  # Not applicable for synset search
            relationship_config=relationship_config
        )
        
        # Update builder with new config
        self.graph_builder.config = graph_config
        
        # Build synset-focused graph
        return self.graph_builder.build_synset_graph(synset_name)
    
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