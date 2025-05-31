"""
Graph service for building and manipulating WordNet graphs.
"""

from typing import Optional, Set, Dict, Any
import networkx as nx

from src.models.graph_data import GraphData, NodeData, EdgeData, NodeType, EdgeType
from src.models.settings import AppSettings
from src.services.wordnet_service import WordNetService
from src.graph.builder import GraphBuilder


class GraphService:
    """Service for building and manipulating WordNet graphs."""
    
    def __init__(self, wordnet_service: Optional[WordNetService] = None):
        """Initialize the graph service."""
        self.wordnet_service = wordnet_service or WordNetService()
        self.builder = GraphBuilder()
    
    def build_graph(self, settings: AppSettings) -> GraphData:
        """
        Build a graph based on the provided settings.
        
        Args:
            settings: Application settings
            
        Returns:
            GraphData object containing the built graph
        """
        # Get the word from settings
        word = settings.exploration.word if hasattr(settings, 'exploration') else None
        if not word:
            return GraphData(graph=nx.Graph())
        
        # Use GraphBuilder to build the graph
        G, node_labels = self.builder.build_graph(word)
        
        # Convert to GraphData
        return GraphData.from_tuple(G, node_labels)
    
    def build_oop_graph(self, settings: AppSettings) -> GraphData:
        """
        Build a graph using the new OOP approach.
        
        Args:
            settings: Application settings
            
        Returns:
            GraphData object containing the built graph
        """
        # Create graph data
        graph_data = GraphData(graph=nx.Graph())
        
        # Get exploration settings
        word = settings.exploration.word
        if not word:
            return graph_data
        
        # Handle synset vs word search
        if settings.exploration.synset_search_mode and '.' in word:
            # Direct synset search
            synset_info = self.wordnet_service.get_synset_info(word)
            if synset_info:
                self._add_synset_to_graph(graph_data, synset_info, settings, depth=0)
        else:
            # Word search
            word_info = self.wordnet_service.get_word_info(word)
            if not word_info.found:
                return graph_data
            
            # Add main word node
            main_node = NodeData(
                node_id=f"{word}_main",
                node_type=NodeType.MAIN,
                label=word.upper(),
                word=word
            )
            graph_data.add_node(main_node)
            
            # Handle specific sense or all senses
            if settings.exploration.sense_number:
                synset_info = word_info.get_synset_by_sense(settings.exploration.sense_number)
                if synset_info:
                    self._add_sense_to_graph(graph_data, f"{word}_main", synset_info, settings, depth=0)
            else:
                # Add all senses based on POS filter
                for synset_info in word_info.synsets:
                    pos_name = synset_info.pos.to_full_name().capitalize() + 's'
                    if pos_name in settings.exploration.pos_filter:
                        self._add_sense_to_graph(graph_data, f"{word}_main", synset_info, settings, depth=0)
        
        # Add breadcrumb if there's a previous word
        if hasattr(settings.exploration, 'previous_word') and settings.exploration.previous_word:
            breadcrumb_node = NodeData(
                node_id=f"{settings.exploration.previous_word}_breadcrumb",
                node_type=NodeType.BREADCRUMB,
                label=f"← {settings.exploration.previous_word}",
                original_word=settings.exploration.previous_word
            )
            graph_data.add_node(breadcrumb_node)
        
        return graph_data
    
    def _add_sense_to_graph(self, graph_data: GraphData, parent_id: str, 
                           synset_info: Any, settings: AppSettings, depth: int) -> None:
        """Add a word sense and its relations to the graph."""
        if depth > settings.exploration.depth:
            return
        
        # Check node limit
        if graph_data.num_nodes >= settings.exploration.max_nodes:
            return
        
        # Create sense node
        sense_node = NodeData(
            node_id=f"{synset_info.synset_name}_sense",
            node_type=NodeType.WORD_SENSE,
            label=synset_info.get_formatted_label(),
            word=synset_info.primary_lemma,
            synset_name=synset_info.synset_name,
            definition=synset_info.definition,
            sense_number=synset_info.sense_number
        )
        graph_data.add_node(sense_node)
        
        # Add edge from parent
        edge = EdgeData(
            source=parent_id,
            target=sense_node.node_id,
            edge_type=EdgeType.SENSE
        )
        graph_data.add_edge(edge)
        
        # Add synset
        self._add_synset_to_graph(graph_data, synset_info, settings, depth)
    
    def _add_synset_to_graph(self, graph_data: GraphData, synset_info: Any,
                            settings: AppSettings, depth: int) -> None:
        """Add a synset and its relations to the graph."""
        if depth > settings.exploration.depth:
            return
        
        # Create synset node
        synset_node = NodeData(
            node_id=synset_info.synset_name,
            node_type=NodeType.SYNSET,
            label=f"{synset_info.synset_name}\n{synset_info.definition[:50]}...",
            synset_name=synset_info.synset_name,
            definition=synset_info.definition,
            pos=synset_info.pos.value
        )
        
        # Check if node already exists
        existing_node = graph_data.get_node_data(synset_node.node_id)
        if not existing_node:
            graph_data.add_node(synset_node)
        
        # Add relationships based on settings
        active_relationships = settings.relationships.get_active_relationships()
        
        # Process each type of relationship
        if 'hypernym' in active_relationships:
            for hypernym in synset_info.hypernyms[:settings.exploration.max_branches]:
                self._add_related_synset(graph_data, synset_info.synset_name, 
                                       hypernym, EdgeType.HYPERNYM, settings, depth + 1)
        
        if 'hyponym' in active_relationships:
            for hyponym in synset_info.hyponyms[:settings.exploration.max_branches]:
                self._add_related_synset(graph_data, synset_info.synset_name,
                                       hyponym, EdgeType.HYPONYM, settings, depth + 1)
        
        # Add other relationships similarly...
    
    def _add_related_synset(self, graph_data: GraphData, source_id: str,
                           target_synset_name: str, edge_type: EdgeType,
                           settings: AppSettings, depth: int) -> None:
        """Add a related synset to the graph."""
        if depth > settings.exploration.depth:
            return
        
        # Get synset info
        synset_info = self.wordnet_service.get_synset_info(target_synset_name)
        if not synset_info:
            return
        
        # Add the synset
        self._add_synset_to_graph(graph_data, synset_info, settings, depth)
        
        # Add edge
        edge = EdgeData(
            source=source_id,
            target=target_synset_name,
            edge_type=edge_type
        )
        graph_data.add_edge(edge) 