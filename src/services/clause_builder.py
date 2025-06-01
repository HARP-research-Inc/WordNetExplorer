"""
Clause builder module for constructing syntactic tree structures.
"""

from typing import List, Dict, Optional
from src.services.token_analyzer import TokenInfo
from src.services.syntactic_tree import SyntacticNode, PhraseBuilder, EdgeLabelMapper
from src.services.phrasal_verb_handler import PhrasalVerbHandler


class ClauseBuilder:
    """Builds clause structures from token sequences."""
    
    def __init__(self, node_id_generator):
        """Initialize with node ID generator."""
        self._get_node_id = node_id_generator
        self._phrase_builder = PhraseBuilder(node_id_generator)
        self._edge_mapper = EdgeLabelMapper()
        self._phrasal_verb_handler = PhrasalVerbHandler()
    
    def build_clause_tree(self, clause_node: SyntacticNode, clause_indices: List[int], 
                         tokens: List[TokenInfo], clause_type: str):
        """
        Build the tree for a single clause.
        
        Args:
            clause_node: The clause node to build under
            clause_indices: Indices of tokens in this clause
            tokens: All tokens in the sentence
            clause_type: Type of clause ('main', 'sub', 'coord')
        """
        # Create a mapping of token indices to nodes
        token_nodes = {}
        
        # Create all word nodes
        for idx in clause_indices:
            token = tokens[idx]
            word_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='word',
                text=token.text,
                token_info=token
            )
            token_nodes[idx] = word_node
        
        # Check for sentence-modifying adverbs at the beginning
        sentence_adverbs = self._identify_sentence_adverbs(clause_indices, tokens)
        
        # If we have sentence-level adverbs, handle them separately
        if sentence_adverbs:
            # Create the adverb node(s) at clause level
            for adv_idx in sentence_adverbs:
                clause_node.add_child(token_nodes[adv_idx], 'adv_mod')
            
            # Create a sub-clause for the rest
            remaining_indices = [idx for idx in clause_indices if idx not in sentence_adverbs]
            if remaining_indices:
                subclause_text = ' '.join([tokens[idx].text for idx in remaining_indices])
                subclause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=subclause_text
                )
                clause_node.add_child(subclause_node, 'main_clause')
                
                # Build the rest of the tree under the subclause
                self._build_clause_content(subclause_node, remaining_indices, tokens, token_nodes)
        else:
            # No sentence-level adverbs, build normally
            self._build_clause_content(clause_node, clause_indices, tokens, token_nodes)
    
    def _identify_sentence_adverbs(self, clause_indices: List[int], tokens: List[TokenInfo]) -> List[int]:
        """Identify sentence-level adverbs (like 'gleefully')."""
        sentence_adverbs = []
        
        # Check first few tokens
        for idx in clause_indices[:3]:
            token = tokens[idx]
            if (token.pos == 'ADV' and 
                token.dep in ['advmod'] and 
                tokens[token.head].pos == 'VERB'):
                # Check if it's a sentence-level adverb
                sentence_adverbs.append(idx)
                break
        
        return sentence_adverbs
    
    def _build_clause_content(self, parent_node: SyntacticNode, clause_indices: List[int],
                             tokens: List[TokenInfo], token_nodes: Dict[int, SyntacticNode]):
        """Build the content of a clause."""
        # Identify phrasal verbs
        phrasal_verbs = self._phrasal_verb_handler.identify_phrasal_verbs(tokens)
        
        # Build phrase structures
        processed = set()
        
        # Find the main verb
        main_verb_idx = self._find_main_verb(clause_indices, tokens)
        
        # Process each token to build phrases
        for idx in clause_indices:
            if idx in processed:
                continue
            
            token = tokens[idx]
            
            # Handle phrasal verbs
            if idx in phrasal_verbs and idx not in processed:
                verb_phrase_node, phrase_indices = self._phrasal_verb_handler.build_verb_phrase(
                    idx, phrasal_verbs[idx], tokens, token_nodes, self._get_node_id)
                processed.update(phrase_indices)
                
                # Attach verb phrase
                edge_label = 'tverb' if idx == main_verb_idx else 'verb'
                parent_node.add_child(verb_phrase_node, edge_label)
            
            # Handle noun phrases
            elif token.pos == 'NOUN' and idx not in processed:
                noun_phrase_node, phrase_indices = self._phrase_builder.build_noun_phrase(
                    idx, tokens, token_nodes, clause_indices)
                processed.update(phrase_indices)
                
                # Attach noun phrase
                self._attach_noun_phrase(noun_phrase_node, token, main_verb_idx, 
                                       token_nodes, parent_node)
            
            # Handle prepositional phrases
            elif token.pos == 'ADP' and idx not in processed:
                prep_phrase_node, phrase_indices = self._phrase_builder.build_prep_phrase(
                    idx, tokens, token_nodes, clause_indices)
                processed.update(phrase_indices)
                
                # Attach prepositional phrase
                self._attach_prep_phrase(prep_phrase_node, token, phrasal_verbs,
                                       token_nodes, parent_node, tokens)
            
            # Handle standalone verbs
            elif token.pos == 'VERB' and idx not in processed:
                processed.add(idx)
                edge_label = 'tverb' if idx == main_verb_idx else 'verb'
                parent_node.add_child(token_nodes[idx], edge_label)
            
            # Handle other standalone words
            elif idx not in processed:
                processed.add(idx)
                edge_label = self._edge_mapper.get_edge_label(token)
                
                # Attach to appropriate parent
                if token.head < len(tokens) and token.head in token_nodes and token.head != idx:
                    # Check if head is already processed
                    if token.head not in processed:
                        token_nodes[token.head].add_child(token_nodes[idx], edge_label)
                    else:
                        # Head is in a phrase, attach to parent
                        parent_node.add_child(token_nodes[idx], edge_label)
                else:
                    parent_node.add_child(token_nodes[idx], edge_label)
    
    def _find_main_verb(self, clause_indices: List[int], tokens: List[TokenInfo]) -> Optional[int]:
        """Find the main verb in a clause."""
        # First look for ROOT verb
        for idx in clause_indices:
            if tokens[idx].pos == 'VERB' and tokens[idx].dep == 'ROOT':
                return idx
        
        # If no ROOT verb, find any verb
        for idx in clause_indices:
            if tokens[idx].pos == 'VERB':
                return idx
        
        return None
    
    def _attach_noun_phrase(self, noun_phrase_node: SyntacticNode, token: TokenInfo,
                           main_verb_idx: Optional[int], token_nodes: dict, 
                           parent_node: SyntacticNode):
        """Attach a noun phrase to the appropriate parent."""
        if token.dep in ['nsubj', 'nsubjpass'] and main_verb_idx is not None:
            token_nodes[main_verb_idx].add_child(noun_phrase_node, 'subj')
        elif token.dep in ['dobj', 'iobj'] and main_verb_idx is not None:
            token_nodes[main_verb_idx].add_child(noun_phrase_node, 'obj')
        elif token.dep == 'dative' and main_verb_idx is not None:
            token_nodes[main_verb_idx].add_child(noun_phrase_node, 'dative')
        elif token.dep == 'pobj':
            # Object of preposition - handled by prep phrase
            pass
        else:
            edge_label = self._edge_mapper.get_edge_label(token)
            parent_node.add_child(noun_phrase_node, edge_label)
    
    def _attach_prep_phrase(self, prep_phrase_node: SyntacticNode, token: TokenInfo,
                           phrasal_verbs: Dict[int, List[int]], token_nodes: dict,
                           parent_node: SyntacticNode, tokens: List[TokenInfo]):
        """Attach a prepositional phrase to the appropriate parent."""
        if token.head < len(tokens) and token.head in token_nodes:
            # Check if the head is part of a phrasal verb
            head_in_phrasal = False
            for verb_idx, particles in phrasal_verbs.items():
                if token.head == verb_idx or token.head in particles:
                    head_in_phrasal = True
                    # Attach to parent instead
                    parent_node.add_child(prep_phrase_node, 'prep_phrase')
                    break
            
            if not head_in_phrasal and token.head in token_nodes:
                # Check if head is already processed
                if token_nodes[token.head].parent is None:
                    token_nodes[token.head].add_child(prep_phrase_node, 'prep_phrase')
                else:
                    # Head was already processed (probably in a phrase)
                    parent_node.add_child(prep_phrase_node, 'prep_phrase')
        else:
            parent_node.add_child(prep_phrase_node, 'prep_phrase') 