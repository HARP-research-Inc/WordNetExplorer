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
        """Add a child with an edge label, ensuring tree integrity."""
        # If child already has a parent, detach it from the old parent
        if child.parent is not None:
            if child in child.parent.children:
                child.parent.children.remove(child)
            # Set child's old parent to None, in case it was only partially detached
            # child.parent = None 
            # Re-evaluating if setting child.parent to None here is always safe or if it could mask issues.
            # For now, the removal from old parent's children list is the primary goal.

        # Set new parent-child relationship
        child.parent = self
        child.edge_label = edge_label
        
        # Add to children list, ensuring no duplicates by object identity
        if child not in self.children:
            self.children.append(child)
        else:
            # If child is already in list, update its edge_label if different
            # This can happen if a node is moved under the same parent with a new role
            for existing_child in self.children:
                if existing_child is child:
                    existing_child.edge_label = edge_label
                    break
    
    def remove_child(self, child_to_remove: 'SyntacticNode'):
        """Remove a specific child node."""
        if child_to_remove in self.children:
            self.children.remove(child_to_remove)
            child_to_remove.parent = None
            child_to_remove.edge_label = None


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
        
        # Collect modifiers of this noun by type
        adjectives = []  # amod
        determiners = []  # det
        possessives = []  # poss
        numerals = []    # nummod
        compounds = []   # compound
        
        # Look for modifiers that directly modify this noun
        for idx in clause_indices:
            if idx == noun_idx:
                continue
            
            token = tokens[idx]
            # Check if this token modifies our noun
            if token.head == noun_idx:
                if token.dep == 'amod':
                    adjectives.append((idx, token))
                    indices_in_phrase.add(idx)
                elif token.dep == 'det':
                    determiners.append((idx, token))
                    indices_in_phrase.add(idx)
                elif token.dep == 'poss':
                    possessives.append((idx, token))
                    indices_in_phrase.add(idx)
                elif token.dep == 'nummod':
                    numerals.append((idx, token))
                    indices_in_phrase.add(idx)
                elif token.dep == 'compound':
                    compounds.append((idx, token))
                    indices_in_phrase.add(idx)
        
        # If no modifiers, just return the noun node
        if not any([adjectives, determiners, possessives, numerals, compounds]):
            return token_nodes[noun_idx], indices_in_phrase
        
        # Build hierarchical structure
        # Start with the noun as the innermost element
        # Use the token node but ensure it has no children
        current_node = token_nodes[noun_idx]
        current_node.children = []  # Clear any existing children
        
        # Layer 1: Add compounds and adjectives closest to the noun
        if compounds or adjectives:
            # Create phrase for noun + its immediate modifiers
            immediate_indices = {noun_idx}
            immediate_parts = []
            
            # Add compounds (they come before the noun)
            for comp_idx, _ in sorted(compounds):
                immediate_indices.add(comp_idx)
            
            # Add adjectives
            for adj_idx, _ in sorted(adjectives):
                immediate_indices.add(adj_idx)
            
            # Build text for this sub-phrase
            for idx in sorted(immediate_indices):
                immediate_parts.append(tokens[idx].text)
            
            immediate_text = ' '.join(immediate_parts)
            
            # Create sub-phrase node
            immediate_np = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='phrase',
                text=immediate_text
            )
            
            # Add compounds in order
            for comp_idx, _ in sorted(compounds):
                token_nodes[comp_idx].children = []  # Clear any existing children
                immediate_np.add_child(token_nodes[comp_idx], 'compound')
            
            # Add adjectives in order
            for adj_idx, _ in sorted(adjectives):
                token_nodes[adj_idx].children = []  # Clear any existing children
                immediate_np.add_child(token_nodes[adj_idx], 'adj')
            
            # Add noun as head
            immediate_np.add_child(current_node, 'head')
            
            current_node = immediate_np
        
        # Layer 2: Add possessives and numerals
        if possessives or numerals:
            # Get all indices including what we have so far
            outer_indices = set()
            
            # Add all indices from current node
            if current_node.node_type == 'phrase':
                # Extract indices from the phrase text
                for token in tokens:
                    if token.text in current_node.text.split():
                        outer_indices.add(tokens.index(token))
            else:
                outer_indices.add(noun_idx)
            
            # Add possessives and numerals
            for poss_idx, _ in possessives:
                outer_indices.add(poss_idx)
            for num_idx, _ in numerals:
                outer_indices.add(num_idx)
            
            # Build text
            outer_parts = []
            for idx in sorted(outer_indices):
                outer_parts.append(tokens[idx].text)
            
            outer_text = ' '.join(outer_parts)
            
            # Create outer phrase
            outer_np = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='phrase',
                text=outer_text
            )
            
            # Add possessives first
            for poss_idx, _ in sorted(possessives):
                token_nodes[poss_idx].children = []  # Clear any existing children
                outer_np.add_child(token_nodes[poss_idx], 'poss')
            
            # Add numerals
            for num_idx, _ in sorted(numerals):
                token_nodes[num_idx].children = []  # Clear any existing children
                outer_np.add_child(token_nodes[num_idx], 'num')
            
            # Add the inner phrase
            outer_np.add_child(current_node, 'head' if current_node.node_type == 'word' else 'core')
            
            current_node = outer_np
        
        # Layer 3: Add determiners last (outermost)
        if determiners:
            # Build final phrase with determiners
            all_indices = sorted(indices_in_phrase)
            final_text = ' '.join([tokens[i].text for i in all_indices])
            
            final_np = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='phrase',
                text=final_text
            )
            
            # Add determiners first
            for det_idx, _ in sorted(determiners):
                token_nodes[det_idx].children = []  # Clear any existing children
                final_np.add_child(token_nodes[det_idx], 'det')
            
            # Add the rest of the phrase
            final_np.add_child(current_node, 'head' if current_node.node_type == 'word' else 'core')
            
            return final_np, indices_in_phrase
        
        return current_node, indices_in_phrase
    
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