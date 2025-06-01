"""
Syntactic tree structures and builders.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple
from src.services.token_analyzer import TokenInfo


@dataclass
class SyntacticNode:
    """A node in the syntactic tree."""
    node_id: str
    node_type: str  # 'sentence', 'clause', 'phrase', 'word'
    text: str
    children: List['SyntacticNode'] = field(default_factory=list)
    parent: Optional['SyntacticNode'] = None
    edge_label: Optional[str] = None  # Label on edge from parent
    token_info: Optional[TokenInfo] = None  # For word nodes
    
    def add_child(self, child: 'SyntacticNode', edge_label: str):
        """Add a child with an edge label."""
        child.parent = self
        child.edge_label = edge_label
        self.children.append(child)


class PhraseBuilder:
    """Builds phrase structures from tokens."""
    
    def __init__(self, node_id_generator):
        """Initialize with a node ID generator function."""
        self._get_node_id = node_id_generator
    
    def build_noun_phrase(self, noun_idx: int, tokens: List[TokenInfo], 
                         token_nodes: Dict[int, SyntacticNode], 
                         clause_indices: List[int]) -> Tuple[SyntacticNode, Set[int]]:
        """Build a noun phrase with the noun and its modifiers."""
        noun_token = tokens[noun_idx]
        indices_in_phrase = {noun_idx}
        
        # Collect modifiers of this noun
        modifiers = []
        
        # Look for adjectives, determiners, etc. that modify this noun
        for idx in clause_indices:
            if idx == noun_idx:
                continue
            
            token = tokens[idx]
            # Check if this token modifies our noun
            if token.head == noun_idx and token.dep in ['amod', 'det', 'nummod', 'poss', 'compound']:
                modifiers.append((idx, token))
                indices_in_phrase.add(idx)
        
        # If no modifiers, just return the noun node
        if not modifiers:
            return token_nodes[noun_idx], indices_in_phrase
        
        # Create noun phrase node
        all_indices = sorted(indices_in_phrase)
        phrase_text = ' '.join([tokens[i].text for i in all_indices])
        
        np_node = SyntacticNode(
            node_id=self._get_node_id(),
            node_type='phrase',
            text=phrase_text
        )
        
        # Add noun as head
        np_node.add_child(token_nodes[noun_idx], 'head')
        
        # Add modifiers in order
        for mod_idx, mod_token in sorted(modifiers):
            edge_label = {
                'amod': 'adj',
                'det': 'det',
                'nummod': 'num',
                'poss': 'poss',
                'compound': 'compound'
            }.get(mod_token.dep, mod_token.dep)
            
            np_node.add_child(token_nodes[mod_idx], edge_label)
        
        return np_node, indices_in_phrase
    
    def build_prep_phrase(self, prep_idx: int, tokens: List[TokenInfo], 
                         token_nodes: Dict[int, SyntacticNode], 
                         clause_indices: List[int]) -> Tuple[SyntacticNode, Set[int]]:
        """Build a prepositional phrase."""
        prep_token = tokens[prep_idx]
        indices_in_phrase = {prep_idx}
        
        # Find the object of the preposition
        pobj_idx = None
        for idx in clause_indices:
            token = tokens[idx]
            if token.head == prep_idx and token.dep == 'pobj':
                pobj_idx = idx
                break
        
        # Create prepositional phrase node
        if pobj_idx is not None:
            # Include the whole noun phrase if the object is a noun
            if tokens[pobj_idx].pos == 'NOUN':
                obj_node, obj_indices = self.build_noun_phrase(pobj_idx, tokens, token_nodes, clause_indices)
                indices_in_phrase.update(obj_indices)
            else:
                obj_node = token_nodes[pobj_idx]
                indices_in_phrase.add(pobj_idx)
            
            # Build phrase text
            all_indices = sorted(indices_in_phrase)
            phrase_text = ' '.join([tokens[i].text for i in all_indices])
            
            pp_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='phrase',
                text=phrase_text
            )
            
            # Add preposition and object
            pp_node.add_child(token_nodes[prep_idx], 'prep')
            pp_node.add_child(obj_node, 'pobj')
            
            return pp_node, indices_in_phrase
        else:
            # Just return the preposition if no object found
            return token_nodes[prep_idx], indices_in_phrase


class EdgeLabelMapper:
    """Maps dependency relations to edge labels."""
    
    @staticmethod
    def get_edge_label(token: TokenInfo) -> str:
        """Get appropriate edge label for a token based on its role."""
        dep = token.dep
        pos = token.pos
        
        # Subject
        if dep in ['nsubj', 'nsubjpass']:
            return 'subj'
        # Object
        elif dep in ['dobj', 'iobj', 'pobj']:
            return 'obj'
        # Adverbial
        elif pos == 'ADV' or dep in ['advmod', 'advcl']:
            return 'adv'
        # Adjectival
        elif pos == 'ADJ' or dep == 'amod':
            return 'adj'
        # Prepositional
        elif pos == 'ADP' or dep == 'prep':
            return 'prep'
        # Determiner
        elif pos == 'DET' or dep == 'det':
            return 'det'
        # Auxiliary
        elif dep in ['aux', 'auxpass']:
            return 'aux'
        # Default
        else:
            return dep 