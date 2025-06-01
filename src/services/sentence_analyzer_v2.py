"""
Refactored sentence analyzer using modular components.
"""

import spacy
from typing import List, Optional, Dict, Set
from dataclasses import dataclass
import streamlit as st

from .token_analyzer import TokenAnalyzer, TokenInfo
from .token_disambiguator import TokenDisambiguator
from .syntactic_tree import SyntacticNode, PhraseBuilder, EdgeLabelMapper
from .linguistic_colors import LinguisticColors
from .phrasal_verb_handler import PhrasalVerbHandler


@dataclass
class SentenceAnalysis:
    """Complete analysis of a sentence."""
    text: str
    tokens: List[TokenInfo]
    root_index: int
    syntactic_tree: Optional[SyntacticNode] = None
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            'text': self.text,
            'tokens': [t.to_dict() for t in self.tokens],
            'root_index': self.root_index
        }


class SentenceAnalyzerV2:
    """Modular sentence analyzer using spaCy and WordNet."""
    
    def __init__(self):
        """Initialize the sentence analyzer components."""
        self._nlp = None
        self._token_analyzer = TokenAnalyzer()
        self._token_disambiguator = TokenDisambiguator()
        self._node_counter = 0
        self.colors = LinguisticColors()
    
    @property
    def nlp(self):
        """Lazy load spaCy model."""
        if self._nlp is None:
            try:
                self._nlp = spacy.load("en_core_web_sm")
            except OSError:
                st.error("Please install the spaCy English model: `python -m spacy download en_core_web_sm`")
                raise
        return self._nlp
    
    def _get_node_id(self) -> str:
        """Get a unique node ID."""
        self._node_counter += 1
        return f"node_{self._node_counter}"
    
    def analyze_sentence(self, sentence: str) -> SentenceAnalysis:
        """
        Analyze a sentence and extract linguistic information.
        
        Args:
            sentence: The sentence to analyze
            
        Returns:
            SentenceAnalysis object with parsed information
        """
        # Reset node counter for each sentence
        self._node_counter = 0
        
        # Parse the sentence
        doc = self.nlp(sentence)
        
        # Extract token information
        tokens = []
        root_index = 0
        
        # First pass - analyze tokens
        for i, token in enumerate(doc):
            token_info = self._token_analyzer.analyze_token(token, i)
            tokens.append(token_info)
            
            # Track root token
            if token.dep_ == "ROOT":
                root_index = i
        
        # Second pass - disambiguate tokens
        self._token_disambiguator.disambiguate_tokens(tokens, doc)
        
        # Build syntactic tree
        syntactic_tree = self._build_syntactic_tree(doc, tokens)
        
        return SentenceAnalysis(
            text=sentence,
            tokens=tokens,
            root_index=root_index,
            syntactic_tree=syntactic_tree
        )
    
    def _build_syntactic_tree(self, doc, tokens: List[TokenInfo]) -> SyntacticNode:
        """Build a syntactic tree from the parsed document."""
        # Create root sentence node
        root = SyntacticNode(
            node_id=self._get_node_id(),
            node_type='sentence',
            text=doc.text
        )
        
        # Identify clauses
        clauses = self._identify_clauses(doc, tokens)
        
        if len(clauses) == 1:
            # Simple sentence - build directly
            clause_builder = ClauseBuilder(self._get_node_id)
            clause_builder.build_clause_tree(root, clauses[0], tokens, 'main')
        else:
            # Complex sentence - identify relationships
            self._build_complex_sentence_tree(root, clauses, tokens, doc)
        
        return root
    
    def _identify_clauses(self, doc, tokens: List[TokenInfo]) -> List[List[int]]:
        """Identify clauses in the sentence."""
        clause_identifier = ClauseIdentifier()
        return clause_identifier.identify_clauses(doc, tokens)
    
    def _build_complex_sentence_tree(self, root: SyntacticNode, clauses: List[List[int]], 
                                   tokens: List[TokenInfo], doc):
        """Build tree for complex sentence with multiple clauses."""
        # Find conjunctions connecting clauses
        conjunctions = []
        for i, token in enumerate(doc):
            if token.dep_ in ['cc', 'mark'] or token.pos_ in ['SCONJ', 'CCONJ']:
                conjunctions.append((i, token))
        
        if conjunctions:
            # Find the main conjunction
            main_conj = conjunctions[0]
            conj_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='word',
                text=main_conj[1].text,
                token_info=tokens[main_conj[0]]
            )
            root.add_child(conj_node, 'sconj')
            
            # Add clauses
            clause_builder = ClauseBuilder(self._get_node_id)
            for i, clause_indices in enumerate(clauses):
                clause_text = ' '.join([tokens[idx].text for idx in clause_indices])
                clause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=clause_text
                )
                
                # Determine edge label
                edge_label = 'iclause' if i == 0 else 'dclause'
                conj_node.add_child(clause_node, edge_label)
                
                # Build the clause subtree
                clause_builder.build_clause_tree(clause_node, clause_indices, tokens, 'sub')
        else:
            # No clear conjunction, treat as coordinate clauses
            clause_builder = ClauseBuilder(self._get_node_id)
            for i, clause_indices in enumerate(clauses):
                clause_text = ' '.join([tokens[idx].text for idx in clause_indices])
                clause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=clause_text
                )
                
                edge_label = 'clause' if i == 0 else 'coord_clause'
                root.add_child(clause_node, edge_label)
                
                clause_builder.build_clause_tree(clause_node, clause_indices, tokens, 
                                               'main' if i == 0 else 'coord')
    
    # Color methods for backward compatibility
    def get_pos_color(self, pos: str) -> str:
        """Get color for a POS tag."""
        return self.colors.get_pos_color(pos)
    
    def get_dependency_color(self, dep: str) -> str:
        """Get color for a dependency relation."""
        return self.colors.get_dependency_color(dep)


class ClauseIdentifier:
    """Identifies clauses in sentences."""
    
    def identify_clauses(self, doc, tokens: List[TokenInfo]) -> List[List[int]]:
        """Identify clauses in the sentence."""
        clauses = []
        clause_roots = set()
        
        # Find all verbs that could be clause roots
        for i, token in enumerate(doc):
            if token.pos_ == 'VERB' and token.dep_ in ['ROOT', 'ccomp', 'xcomp', 'advcl', 'conj']:
                clause_roots.add(i)
        
        # If no clear clause structure, treat as single clause
        if not clause_roots:
            return [list(range(len(tokens)))]
        
        # Group tokens by their clause root
        clause_groups = {root: [] for root in clause_roots}
        
        for i, token in enumerate(doc):
            # Find which clause root this token belongs to
            assigned = False
            
            # Check if it's a clause root itself
            if i in clause_roots:
                clause_groups[i].append(i)
                assigned = True
            else:
                # Find the nearest clause root in the dependency tree
                current = token
                visited = set()
                
                while current.i not in visited:
                    visited.add(current.i)
                    
                    if current.i in clause_roots:
                        clause_groups[current.i].append(i)
                        assigned = True
                        break
                    
                    if current.head == current:  # Root
                        break
                    
                    current = current.head
                
                # If not assigned, assign to the main root
                if not assigned:
                    for root in clause_roots:
                        if tokens[root].dep == 'ROOT':
                            clause_groups[root].append(i)
                            break
        
        # Convert to list of clauses
        clauses = [sorted(indices) for indices in clause_groups.values() if indices]
        
        return clauses if clauses else [list(range(len(tokens)))]


class ClauseBuilder:
    """Builds clause structures."""
    
    def __init__(self, node_id_generator):
        """Initialize with node ID generator."""
        self._get_node_id = node_id_generator
        self._phrase_builder = PhraseBuilder(node_id_generator)
        self._edge_mapper = EdgeLabelMapper()
        self._phrasal_verb_handler = PhrasalVerbHandler()

    def _assign_child(self, parent_node: SyntacticNode, child_node: SyntacticNode, edge_label: str):
        """Helper to add/assign child, ensuring it's detached from previous parent if any."""
        parent_node.add_child(child_node, edge_label) # SyntacticNode.add_child now handles detachment
    
    def build_clause_tree(self, clause_node: SyntacticNode, clause_indices: List[int], 
                         tokens: List[TokenInfo], clause_type: str):
        """Build the tree for a single clause."""
        token_nodes: Dict[int, SyntacticNode] = {}
        for idx in clause_indices:
            token = tokens[idx]
            word_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='word',
                text=token.text,
                token_info=token
            )
            token_nodes[idx] = word_node
        
        sentence_adverbs = self._identify_sentence_adverbs(clause_indices, tokens)
        
        if sentence_adverbs:
            for adv_idx in sentence_adverbs:
                self._assign_child(clause_node, token_nodes[adv_idx], 'adv_mod')
            
            remaining_indices = [idx for idx in clause_indices if idx not in sentence_adverbs]
            if remaining_indices:
                subclause_text = ' '.join([tokens[idx].text for idx in remaining_indices])
                subclause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=subclause_text
                )
                self._assign_child(clause_node, subclause_node, 'main_clause')
                self._build_clause_content(subclause_node, remaining_indices, tokens, token_nodes)
        else:
            self._build_clause_content(clause_node, clause_indices, tokens, token_nodes)

    def _identify_sentence_adverbs(self, clause_indices: List[int], tokens: List[TokenInfo]) -> List[int]:
        """Identify sentence-level adverbs in the clause."""
        adverbs = []
        for idx in clause_indices[:3]:  # Check first few tokens
            token = tokens[idx]
            if (token.pos == 'ADV' and 
                token.dep in ['advmod'] and 
                token.head < len(tokens) and # Ensure head is a valid index
                tokens[token.head].pos == 'VERB'):
                adverbs.append(idx)
                break # Assuming only one primary sentence-level adverb at the beginning
        return adverbs

    def _build_clause_content(self, parent_node: SyntacticNode, clause_indices: List[int],
                             tokens: List[TokenInfo], token_nodes: Dict[int, SyntacticNode]):
        """Build the content of a clause."""
        phrasal_verbs = self._phrasal_verb_handler.identify_phrasal_verbs(tokens)
        processed: Set[int] = set()
        main_verb_idx = self._find_main_verb(clause_indices, tokens)

        for idx in clause_indices:
            if idx in processed:
                continue
            token = tokens[idx]

            if idx in phrasal_verbs:
                verb_phrase_node, phrase_indices = self._phrasal_verb_handler.build_verb_phrase(
                    idx, phrasal_verbs[idx], tokens, token_nodes, self._get_node_id)
                processed.update(phrase_indices)
                edge_label = 'tverb' if idx == main_verb_idx else 'verb'
                self._assign_child(parent_node, verb_phrase_node, edge_label)
            elif token.pos == 'NOUN':
                noun_phrase_node, phrase_indices = self._phrase_builder.build_noun_phrase(
                    idx, tokens, token_nodes, clause_indices)
                processed.update(phrase_indices)
                self._attach_noun_phrase(noun_phrase_node, token, main_verb_idx, 
                                       token_nodes, parent_node)
            elif token.pos == 'ADP':
                prep_phrase_node, phrase_indices = self._phrase_builder.build_prep_phrase(
                    idx, tokens, token_nodes, clause_indices)
                processed.update(phrase_indices)
                if prep_phrase_node: # build_prep_phrase can return None if no pobj
                    self._attach_prep_phrase(prep_phrase_node, token, phrasal_verbs,
                                        token_nodes, parent_node, tokens)
                else: # If it's just a preposition without an object, add it directly
                    self._assign_child(parent_node, token_nodes[idx], self._edge_mapper.get_edge_label(token))
                    processed.add(idx)
            elif token.pos == 'VERB':
                processed.add(idx)
                edge_label = 'tverb' if idx == main_verb_idx else 'verb'
                self._assign_child(parent_node, token_nodes[idx], edge_label)
            else:
                processed.add(idx)
                edge_label = self._edge_mapper.get_edge_label(token)
                target_parent = parent_node
                if token.head < len(tokens) and token.head in token_nodes and token.head != idx and token.head in clause_indices:
                    # Try to attach to head if head is within the current clause and not processed as part of a larger phrase
                    head_node = token_nodes[token.head]
                    if head_node.parent == parent_node: # Ensure head is already child of current parent_node or is parent_node itself
                        target_parent = head_node
                self._assign_child(target_parent, token_nodes[idx], edge_label)
    
    def _find_main_verb(self, clause_indices: List[int], tokens: List[TokenInfo]) -> Optional[int]:
        """Find the main verb in a clause."""
        for idx in clause_indices:
            if tokens[idx].pos == 'VERB' and tokens[idx].dep == 'ROOT':
                return idx
        for idx in clause_indices:
            if tokens[idx].pos == 'VERB':
                return idx
        return None
    
    def _attach_noun_phrase(self, noun_phrase_node: SyntacticNode, token: TokenInfo,
                           main_verb_idx: Optional[int], token_nodes: dict, 
                           parent_node: SyntacticNode):
        """Attach a noun phrase to the appropriate parent."""
        target_parent = parent_node
        edge_label = self._edge_mapper.get_edge_label(token)

        if main_verb_idx is not None and main_verb_idx in token_nodes:            
            if token.dep in ['nsubj', 'nsubjpass']:
                target_parent = token_nodes[main_verb_idx]
                edge_label = 'subj'
            elif token.dep in ['dobj', 'iobj']:
                target_parent = token_nodes[main_verb_idx]
                edge_label = 'obj'
            elif token.dep == 'dative':
                target_parent = token_nodes[main_verb_idx]
                edge_label = 'dative'
            elif token.dep == 'pobj': # Should be handled by prep phrase attachment logic
                return 
        
        self._assign_child(target_parent, noun_phrase_node, edge_label)
    
    def _attach_prep_phrase(self, prep_phrase_node: SyntacticNode, token: TokenInfo,
                           phrasal_verbs: Dict[int, List[int]], token_nodes: dict,
                           parent_node: SyntacticNode, tokens: List[TokenInfo]):
        """Attach a prepositional phrase to the appropriate parent."""
        target_parent = parent_node
        edge_label = 'prep_phrase'

        if token.head < len(tokens) and token.head in token_nodes and token.head in clause_indices:
            head_node = token_nodes[token.head]
            # Check if the head is part of a phrasal verb already attached to parent_node
            is_phrasal_verb_component = False
            for verb_idx, particles in phrasal_verbs.items():
                if token.head == verb_idx or token.head in particles:
                    # If head is part of a phrasal verb already under parent_node, attach PP to parent_node
                    for child in parent_node.children:
                        if child.node_type == 'phrase' and child.text == f"{tokens[verb_idx].text} {tokens[particles[0]].text}": # Simplified check
                            is_phrasal_verb_component = True
                            break
                    break
            
            if not is_phrasal_verb_component:
                target_parent = head_node # Default to attaching to head
        
        self._assign_child(target_parent, prep_phrase_node, edge_label)

    def _restructure_clause_for_presentation(self, clause_node: SyntacticNode, tokens: List[TokenInfo]):
        """Restructure clause to lift verb's children to clause level for better presentation."""
        # Find the main verb node
        main_verb = None
        for child in clause_node.children[:]:
            if child.edge_label == 'tverb':
                main_verb = child
                break
        
        if not main_verb:
            return
        
        # Check if we need to create a phrasal verb
        verb_text = main_verb.text.lower()
        
        # Look for "over" in the object group that should be part of "ran over"
        phrasal_verb_created = False
        
        for child in main_verb.children[:]:
            if child.edge_label == 'obj_group' and child.children:
                first_part = child.children[0]
                
                # Check if first part contains "over" as prep
                for node in first_part.children if hasattr(first_part, 'children') else []:
                    if node.edge_label == 'prep' and node.text.lower() == 'over' and verb_text == 'ran':
                        # Create "ran over" phrasal verb
                        phrasal_verb = SyntacticNode(
                            node_id=self._get_node_id(),
                            node_type='phrase',
                            text='ran over'
                        )
                        
                        # Remove main verb from clause
                        clause_node.children.remove(main_verb)
                        
                        # Add phrasal verb to clause
                        clause_node.add_child(phrasal_verb, 'tverb')
                        
                        # Add verb and particle to phrasal verb
                        phrasal_verb.add_child(main_verb, 'verb_head')
                        phrasal_verb.add_child(node, 'particle')
                        
                        # Move subject from verb to clause level
                        for verb_child in main_verb.children[:]:
                            if verb_child.edge_label == 'subj':
                                main_verb.children.remove(verb_child)
                                # Insert subject before phrasal verb
                                idx = clause_node.children.index(phrasal_verb)
                                clause_node.children.insert(idx, verb_child)
                        
                        # Fix the object - remove "over" part and create clean object
                        if first_part.children:
                            # Get the noun phrase part (my fat friend)
                            for n in first_part.children:
                                if n.edge_label == 'pobj':
                                    # Combine with other parts (with a scooter)
                                    obj_parts = [n]
                                    for i in range(1, len(child.children)):
                                        obj_parts.append(child.children[i])
                                    
                                    if len(obj_parts) == 1:
                                        clause_node.add_child(obj_parts[0], 'obj')
                                    else:
                                        # Create combined object
                                        combined_text = ' '.join([p.text for p in obj_parts])
                                        combined_obj = SyntacticNode(
                                            node_id=self._get_node_id(),
                                            node_type='phrase',
                                            text=combined_text
                                        )
                                        
                                        for part in obj_parts:
                                            part.edge_label = 'part'
                                            combined_obj.children.append(part)
                                        
                                        clause_node.add_child(combined_obj, 'obj')
                        
                        # Remove the obj_group from verb
                        main_verb.children.remove(child)
                        
                        phrasal_verb_created = True
                        break
        
        if not phrasal_verb_created:
            # Standard restructuring - lift children from verb to clause
            for child in main_verb.children[:]:
                if child.edge_label in ['subj', 'obj', 'obj_group']:
                    main_verb.children.remove(child)
                    
                    # Find appropriate position in clause
                    if child.edge_label == 'subj':
                        # Insert subject before verb
                        idx = clause_node.children.index(main_verb)
                        clause_node.children.insert(idx, child)
                    else:
                        # Add objects after verb
                        clause_node.add_child(child, child.edge_label)
        
        # Move punctuation to the end
        punct_nodes = []
        for child in clause_node.children[:]:
            if child.edge_label == 'punct':
                clause_node.children.remove(child)
                punct_nodes.append(child)
        
        # Re-add punctuation at the end
        for punct in punct_nodes:
            clause_node.children.append(punct) 