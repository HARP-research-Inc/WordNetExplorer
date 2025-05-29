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
    max_nodes: int = 100
    max_branches: int = 5
    min_frequency: int = 0
    pos_filter: list = None
    enable_clustering: bool = False
    simplified_mode: bool = False
    
    def __post_init__(self):
        if self.relationship_config is None:
            self.relationship_config = RelationshipConfig()
        if self.pos_filter is None:
            self.pos_filter = ["Nouns", "Verbs", "Adjectives", "Adverbs"]


class GraphBuilder:
    """Builds NetworkX graphs from WordNet data."""
    
    def __init__(self, config: GraphConfig = None):
        self.config = config or GraphConfig()
        self.visited_synsets: Set = set()
        self.node_count: int = 0
        self.created_synsets: Set = set()  # Track which synsets we've created nodes for
        
    def _should_add_node(self) -> bool:
        """Check if we should add another node based on max_nodes limit."""
        return self.node_count < self.config.max_nodes
        
    def _should_filter_pos(self, pos: str) -> bool:
        """Check if a part-of-speech should be filtered out."""
        pos_mapping = {
            'n': 'Nouns',
            'v': 'Verbs', 
            'a': 'Adjectives',
            's': 'Adjectives',  # Satellite adjectives
            'r': 'Adverbs'
        }
        pos_name = pos_mapping.get(pos, 'Unknown')
        return pos_name in self.config.pos_filter
        
    def _add_node_with_limit(self, G: nx.Graph, node_id: str, **attrs) -> bool:
        """Add a node to the graph if within limits."""
        if not self._should_add_node():
            return False
        
        # Check POS filter
        if 'pos' in attrs and not self._should_filter_pos(attrs['pos']):
            return False
            
        G.add_node(node_id, **attrs)
        self.node_count += 1
        return True
    
    def build_graph(self, word: str) -> Tuple[nx.Graph, Dict]:
        """Build a NetworkX graph for the given word."""
        G = nx.Graph()
        node_labels = {}
        self.visited_synsets.clear()
        self.created_synsets.clear()
        self.node_count = 0  # Reset node count
        
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
            if not self._should_add_node():  # Check node limit
                break
            self._add_synset_connections(G, node_labels, synset, 0, word)
        
        # Add cross-connections between existing nodes
        self._add_cross_connections(G, node_labels)
        
        return G, node_labels
    
    def build_synset_graph(self, synset_name: str) -> Tuple[nx.Graph, Dict]:
        """Build a NetworkX graph focused on a specific synset."""
        G = nx.Graph()
        node_labels = {}
        self.visited_synsets.clear()
        self.created_synsets.clear()
        self.node_count = 0  # Reset node count
        
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
        
        # Use the new node adding method
        if not self._add_node_with_limit(G, synset_node, **node_attrs):
            return G, node_labels  # Node was filtered out
        
        self.created_synsets.add(synset)
        
        # Create a label showing the most common word + synset index
        # Get the most frequent/common lemma (usually the first one)
        primary_lemma = synset.lemmas()[0].name().replace('_', ' ')
        synset_parts = synset.name().split('.')
        pos_part = synset_parts[1] if len(synset_parts) > 1 else 'n'
        index_part = synset_parts[2] if len(synset_parts) > 2 else '01'
        node_labels[synset_node] = f"{primary_lemma}\n{pos_part}.{index_part}"
        
        # Add all word senses that belong to this synset (with branch limiting)
        lemmas_to_process = synset.lemmas()[:self.config.max_branches]  # Limit branches
        for lemma in lemmas_to_process:
            if not self._should_add_node():  # Check node limit
                break
                
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
            
            # Use the new node adding method
            if self._add_node_with_limit(G, word_sense_node, **sense_attrs):
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
        
        # Add cross-connections between existing nodes
        self._add_cross_connections(G, node_labels)
        
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
        if current_depth > self.config.depth:
            return
        
        if not self._should_add_node():  # Check node limit
            return

        # Check if we've already created this synset node
        synset_node = create_node_id(NodeType.SYNSET, synset.name())
        synset_already_exists = synset_node in G.nodes()
        
        # If synset was visited but we still have room, we can add relationships to existing nodes
        if synset in self.visited_synsets and synset_already_exists:
            # Still add relationships from this synset to other nodes, but don't recurse deeper
            if current_depth < self.config.depth:
                relationships = get_relationships(synset, self.config.relationship_config)
                for rel_type, related_synsets in relationships.items():
                    limited_synsets = related_synsets[:self.config.max_branches]
                    for related_synset in limited_synsets:
                        if not self._should_add_node():
                            break
                        self._add_relationship_edge(G, node_labels, synset_node, 
                                                  related_synset, rel_type, current_depth)
            return

        self.visited_synsets.add(synset)
        
        # Create synset node if it doesn't exist
        if not synset_already_exists:
            # Create synset node
            synset_info = get_synset_info(synset)
            
            # Prepare node attributes
            node_attrs = create_node_attributes(NodeType.SYNSET, **synset_info)
            node_attrs['synset_name'] = synset.name()
            
            # Use the new node adding method
            if not self._add_node_with_limit(G, synset_node, **node_attrs):
                return  # Node was filtered out or limit reached
                
            node_labels[synset_node] = create_synset_label(synset)
            self.created_synsets.add(synset)
        
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
                definition=synset_info['definition'] if not synset_already_exists else G.nodes[synset_node].get('definition', ''),
                pos=synset_info['pos'] if not synset_already_exists else G.nodes[synset_node].get('pos', 'n'),
                pos_label=synset_info['pos_label'] if not synset_already_exists else G.nodes[synset_node].get('pos_label', 'noun'),
                sense_number=actual_sense_number  # Use the actual sense number
            )
            
            # Use the new node adding method
            if self._add_node_with_limit(G, word_sense_node, **sense_attrs):
                # Create label for word sense
                from .nodes import create_node_label
                node_labels[word_sense_node] = create_node_label(NodeType.WORD_SENSE, sense_attrs)
                
                # Create and connect root word node
                root_node = create_node_id(NodeType.MAIN, focus_word)
                
                if root_node not in G.nodes():
                    if self._add_node_with_limit(G, root_node, **create_node_attributes(
                        NodeType.MAIN,
                        word=focus_word.lower()
                    )):
                        node_labels[root_node] = focus_word.upper()
                
                # Connect: root word -> word sense -> synset (ALL edges should go FROM root TO sense)
                sense_props = get_relationship_properties(RelationshipType.SENSE)
                if root_node in G.nodes():
                    G.add_edge(root_node, word_sense_node, **sense_props)
                G.add_edge(word_sense_node, synset_node, **sense_props)
        
        # Add relationship connections with branch limiting
        relationships = get_relationships(synset, self.config.relationship_config)
        
        for rel_type, related_synsets in relationships.items():
            # Limit branches per relationship type
            limited_synsets = related_synsets[:self.config.max_branches]
            for related_synset in limited_synsets:
                if not self._should_add_node():  # Check node limit before each relationship
                    break
                self._add_relationship_edge(G, node_labels, synset_node, 
                                          related_synset, rel_type, current_depth)
    
    def _add_relationship_edge(self, G: nx.Graph, node_labels: Dict,
                              source_node: str, target_synset, 
                              rel_type: RelationshipType, current_depth: int):
        """Add an edge for a specific relationship."""
        if not self._should_add_node():  # Check node limit
            return
            
        target_info = get_synset_info(target_synset)
        target_node = create_node_id(NodeType.SYNSET, target_synset.name())
        
        # Create target node if it doesn't exist
        if target_node not in G.nodes():
            # Prepare node attributes
            target_attrs = create_node_attributes(NodeType.SYNSET, **target_info)
            target_attrs['synset_name'] = target_synset.name()
            
            # Use the new node adding method
            if not self._add_node_with_limit(G, target_node, **target_attrs):
                return  # Node was filtered out or limit reached
                
            node_labels[target_node] = create_synset_label(target_synset)
        
        # Add edge with relationship properties
        rel_props = get_relationship_properties(rel_type)
        G.add_edge(source_node, target_node, **rel_props)
        
        # Recursively add connections if within depth limit
        if current_depth < self.config.depth:
            self._add_synset_connections(G, node_labels, target_synset, current_depth + 1)
    
    def _add_cross_connections(self, G: nx.Graph, node_labels: Dict):
        """Add cross-connections between existing nodes in the graph."""
        synset_nodes = [node for node, data in G.nodes(data=True) 
                       if data.get('node_type') == 'synset']
        
        # For each pair of synset nodes, check if they have relationships
        for i, source_node in enumerate(synset_nodes):
            if i >= len(synset_nodes) - 1:  # Don't check the last node against nothing
                break
                
            source_synset_name = G.nodes[source_node].get('synset_name')
            if not source_synset_name:
                continue
                
            try:
                from nltk.corpus import wordnet as wn
                source_synset = wn.synset(source_synset_name)
                relationships = get_relationships(source_synset, self.config.relationship_config)
                
                # Check if any of the remaining nodes are related to this source
                for target_node in synset_nodes[i+1:]:
                    target_synset_name = G.nodes[target_node].get('synset_name')
                    if not target_synset_name:
                        continue
                        
                    try:
                        target_synset = wn.synset(target_synset_name)
                        
                        # Check if these synsets are related
                        for rel_type, related_synsets in relationships.items():
                            if target_synset in related_synsets:
                                # Add edge if it doesn't exist
                                if not G.has_edge(source_node, target_node):
                                    rel_props = get_relationship_properties(rel_type)
                                    G.add_edge(source_node, target_node, **rel_props)
                                    
                        # Also check reverse relationships (target -> source)
                        target_relationships = get_relationships(target_synset, self.config.relationship_config)
                        for rel_type, related_synsets in target_relationships.items():
                            if source_synset in related_synsets:
                                # Add edge if it doesn't exist (reverse direction)
                                if not G.has_edge(target_node, source_node):
                                    rel_props = get_relationship_properties(rel_type)
                                    G.add_edge(target_node, source_node, **rel_props)
                                    
                    except Exception:
                        continue  # Skip invalid synset names
                        
            except Exception:
                continue  # Skip invalid synset names 