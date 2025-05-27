"""
Graph Builder Module

Handles the construction of NetworkX graphs from WordNet data.
"""

import networkx as nx
from typing import Dict, Tuple, Set
from dataclasses import dataclass

from src.wordnet.synsets import (
    get_synsets_for_word, 
    get_synset_info, 
    filter_synsets_by_sense,
    create_synset_label
)
from src.wordnet.relationships import (
    RelationshipType, 
    RelationshipConfig, 
    get_relationships,
    get_relationship_properties
)
from .nodes import NodeType, create_node_id, create_node_attributes


@dataclass
class GraphConfig:
    """Configuration for graph building."""
    depth: int = 1
    sense_number: int = None
    relationship_config: RelationshipConfig = None
    
    def __post_init__(self):
        if self.relationship_config is None:
            self.relationship_config = RelationshipConfig()


class GraphBuilder:
    """Builds NetworkX graphs from WordNet data."""
    
    def __init__(self, config: GraphConfig = None):
        self.config = config or GraphConfig()
        self.visited_synsets: Set = set()
        
    def build_graph(self, word: str) -> Tuple[nx.Graph, Dict]:
        """Build a NetworkX graph for the given word."""
        G = nx.Graph()
        node_labels = {}
        self.visited_synsets.clear()
        
        synsets = get_synsets_for_word(word)
        if not synsets:
            print(f"No WordNet entries found for '{word}'")
            return G, node_labels
        
        # Filter synsets by sense number if specified
        synsets = filter_synsets_by_sense(synsets, self.config.sense_number)
        if not synsets:
            print(f"Sense number {self.config.sense_number} not found for '{word}'")
            return G, node_labels
        
        # Build graph for each synset
        for synset in synsets:
            self._add_synset_connections(G, node_labels, synset, 0, word)
        
        return G, node_labels
    
    def build_synset_graph(self, synset_name: str) -> Tuple[nx.Graph, Dict]:
        """Build a NetworkX graph focused on a specific synset."""
        G = nx.Graph()
        node_labels = {}
        self.visited_synsets.clear()
        
        # Try to get the synset by name
        try:
            from nltk.corpus import wordnet as wn
            synset = wn.synset(synset_name)
        except Exception as e:
            print(f"Error: Invalid synset name '{synset_name}': {e}")
            return G, node_labels
        
        if not synset:
            print(f"No synset found for '{synset_name}'")
            return G, node_labels
        
        # Create the main synset node (this will be the focus/center)
        synset_info = get_synset_info(synset)
        synset_node = create_node_id(NodeType.SYNSET, synset.name())
        
        # Prepare node attributes
        node_attrs = create_node_attributes(NodeType.SYNSET, **synset_info)
        node_attrs['synset_name'] = synset.name()
        G.add_node(synset_node, **node_attrs)
        
        # Create a label showing the most common word + synset index
        # Get the most frequent/common lemma (usually the first one)
        primary_lemma = synset.lemmas()[0].name().replace('_', ' ')
        synset_parts = synset.name().split('.')
        pos_part = synset_parts[1] if len(synset_parts) > 1 else 'n'
        index_part = synset_parts[2] if len(synset_parts) > 2 else '01'
        node_labels[synset_node] = f"{primary_lemma}\n{pos_part}.{index_part}"
        
        # Add all word senses that belong to this synset
        for lemma in synset.lemmas():
            lemma_word = lemma.name().replace('_', ' ')
            
            # Find the sense number for this specific word
            word_synsets = get_synsets_for_word(lemma_word)
            word_sense_number = None
            for i, word_synset in enumerate(word_synsets, 1):
                if word_synset.name() == synset.name():
                    word_sense_number = i
                    break
            
            if word_sense_number is None:
                # Fallback if we can't find the sense number
                word_sense_number = 1
            
            # Create word sense node for each word in the synset
            word_sense_node = create_node_id(NodeType.WORD_SENSE, f"{lemma_word}_{word_sense_number}")
            
            # Create word sense attributes with the correct sense number for this word
            sense_attrs = create_node_attributes(
                NodeType.WORD_SENSE,
                word=lemma_word,
                synset_name=synset.name(),
                definition=synset_info['definition'],
                pos=synset_info['pos'],
                pos_label=synset_info['pos_label'],
                sense_number=word_sense_number  # Use the word-specific sense number
            )
            G.add_node(word_sense_node, **sense_attrs)
            
            # Create label for word sense (this will show "word (pos.sense_num)")
            from .nodes import create_node_label
            node_labels[word_sense_node] = create_node_label(NodeType.WORD_SENSE, sense_attrs)
            
            # Connect word sense to synset
            sense_props = get_relationship_properties(RelationshipType.SENSE)
            G.add_edge(word_sense_node, synset_node, **sense_props)
        
        # Mark this synset as visited to avoid re-processing
        self.visited_synsets.add(synset)
        
        # Add relationship connections to other synsets
        self._add_synset_relationships(G, node_labels, synset, synset_node, 0)
        
        return G, node_labels
    
    def _add_synset_relationships(self, G: nx.Graph, node_labels: Dict,
                                 synset, synset_node: str, current_depth: int):
        """Add relationship connections for a synset in synset-focused mode."""
        # Add relationship connections
        relationships = get_relationships(synset, self.config.relationship_config)
        
        for rel_type, related_synsets in relationships.items():
            for related_synset in related_synsets:
                self._add_relationship_edge(G, node_labels, synset_node, 
                                          related_synset, rel_type, current_depth)
    
    def _add_synset_connections(self, G: nx.Graph, node_labels: Dict, 
                               synset, current_depth: int, focus_word: str = None):
        """Add connections for a synset and its relationships."""
        if current_depth > self.config.depth or synset in self.visited_synsets:
            return
        
        self.visited_synsets.add(synset)
        
        # Create synset node
        synset_info = get_synset_info(synset)
        synset_node = create_node_id(NodeType.SYNSET, synset.name())
        
        # Prepare node attributes
        node_attrs = create_node_attributes(NodeType.SYNSET, **synset_info)
        node_attrs['synset_name'] = synset.name()
        G.add_node(synset_node, **node_attrs)
        
        node_labels[synset_node] = create_synset_label(synset)
        
        # For the first level (current_depth == 0), this is a sense of the focus word
        if current_depth == 0 and focus_word:
            # Find the actual sense number for this word (position in the synsets list)
            word_synsets = get_synsets_for_word(focus_word)
            actual_sense_number = None
            for i, word_synset in enumerate(word_synsets, 1):
                if word_synset.name() == synset.name():
                    actual_sense_number = i
                    break
            
            if actual_sense_number is None:
                # Fallback if we can't find the sense number
                actual_sense_number = 1
            
            # Create word sense node for this meaning of the focus word
            word_sense_node = create_node_id(NodeType.WORD_SENSE, f"{focus_word}_{actual_sense_number}")
            
            # Create word sense attributes with the correct actual sense number
            sense_attrs = create_node_attributes(
                NodeType.WORD_SENSE,
                word=focus_word,
                synset_name=synset.name(),
                definition=synset_info['definition'],
                pos=synset_info['pos'],
                pos_label=synset_info['pos_label'],
                sense_number=actual_sense_number  # Use the actual sense number
            )
            G.add_node(word_sense_node, **sense_attrs)
            
            # Create label for word sense
            from .nodes import create_node_label
            node_labels[word_sense_node] = create_node_label(NodeType.WORD_SENSE, sense_attrs)
            
            # Create and connect root word node
            root_node = create_node_id(NodeType.MAIN, focus_word)
            
            if root_node not in G.nodes():
                G.add_node(root_node, **create_node_attributes(
                    NodeType.MAIN,
                    word=focus_word.lower()
                ))
                node_labels[root_node] = focus_word.upper()
            
            # Connect: root word -> word sense -> synset (ALL edges should go FROM root TO sense)
            sense_props = get_relationship_properties(RelationshipType.SENSE)
            G.add_edge(root_node, word_sense_node, **sense_props)
            G.add_edge(word_sense_node, synset_node, **sense_props)
        
        # Add relationship connections
        relationships = get_relationships(synset, self.config.relationship_config)
        
        for rel_type, related_synsets in relationships.items():
            for related_synset in related_synsets:
                self._add_relationship_edge(G, node_labels, synset_node, 
                                          related_synset, rel_type, current_depth)
    
    def _add_relationship_edge(self, G: nx.Graph, node_labels: Dict,
                              source_node: str, target_synset, 
                              rel_type: RelationshipType, current_depth: int):
        """Add an edge for a specific relationship."""
        target_info = get_synset_info(target_synset)
        target_node = create_node_id(NodeType.SYNSET, target_synset.name())
        
        # Create target node if it doesn't exist
        if target_node not in G.nodes():
            # Prepare node attributes
            target_attrs = create_node_attributes(NodeType.SYNSET, **target_info)
            target_attrs['synset_name'] = target_synset.name()
            G.add_node(target_node, **target_attrs)
            node_labels[target_node] = create_synset_label(target_synset)
        
        # Add edge with relationship properties
        rel_props = get_relationship_properties(rel_type)
        G.add_edge(source_node, target_node, **rel_props)
        
        # Recursively add connections if within depth limit
        if current_depth < self.config.depth:
            self._add_synset_connections(G, node_labels, target_synset, current_depth + 1) 