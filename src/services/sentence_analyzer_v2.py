"""
Refactored sentence analyzer using modular components.
"""

import spacy
from typing import List, Optional
from dataclasses import dataclass
import streamlit as st

from .token_analyzer import TokenAnalyzer, TokenInfo
from .token_disambiguator import TokenDisambiguator
from .syntactic_tree import SyntacticNode, PhraseBuilder, EdgeLabelMapper
from .linguistic_colors import LinguisticColors


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
    
    def build_clause_tree(self, clause_node: SyntacticNode, clause_indices: List[int], 
                         tokens: List[TokenInfo], clause_type: str):
        """Build the tree for a single clause."""
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
        
        # Build phrase structures
        processed = set()
        
        # Find the main verb
        main_verb_idx = None
        for idx in clause_indices:
            if tokens[idx].pos == 'VERB' and tokens[idx].dep == 'ROOT':
                main_verb_idx = idx
                break
        
        # If no ROOT verb, find any verb
        if main_verb_idx is None:
            for idx in clause_indices:
                if tokens[idx].pos == 'VERB':
                    main_verb_idx = idx
                    break
        
        # Process each token to build phrases
        for idx in clause_indices:
            if idx in processed:
                continue
            
            token = tokens[idx]
            
            # Handle noun phrases
            if token.pos == 'NOUN' and idx not in processed:
                noun_phrase_node, phrase_indices = self._phrase_builder.build_noun_phrase(
                    idx, tokens, token_nodes, clause_indices)
                processed.update(phrase_indices)
                
                # Attach noun phrase
                self._attach_noun_phrase(noun_phrase_node, token, main_verb_idx, 
                                       token_nodes, clause_node)
            
            # Handle prepositional phrases
            elif token.pos == 'ADP' and idx not in processed:
                prep_phrase_node, phrase_indices = self._phrase_builder.build_prep_phrase(
                    idx, tokens, token_nodes, clause_indices)
                processed.update(phrase_indices)
                
                # Attach prepositional phrase
                if token.head < len(tokens) and token.head in token_nodes:
                    token_nodes[token.head].add_child(prep_phrase_node, 'prep_phrase')
                else:
                    clause_node.add_child(prep_phrase_node, 'prep_phrase')
            
            # Handle standalone verbs
            elif token.pos == 'VERB' and idx not in processed:
                processed.add(idx)
                edge_label = 'tverb' if idx == main_verb_idx else 'verb'
                clause_node.add_child(token_nodes[idx], edge_label)
            
            # Handle other standalone words
            elif idx not in processed:
                processed.add(idx)
                edge_label = self._edge_mapper.get_edge_label(token)
                
                # Attach to appropriate parent
                if token.head < len(tokens) and token.head in token_nodes and token.head != idx:
                    token_nodes[token.head].add_child(token_nodes[idx], edge_label)
                else:
                    clause_node.add_child(token_nodes[idx], edge_label)
    
    def _attach_noun_phrase(self, noun_phrase_node: SyntacticNode, token: TokenInfo,
                           main_verb_idx: Optional[int], token_nodes: dict, 
                           clause_node: SyntacticNode):
        """Attach a noun phrase to the appropriate parent."""
        if token.dep in ['nsubj', 'nsubjpass'] and main_verb_idx is not None:
            token_nodes[main_verb_idx].add_child(noun_phrase_node, 'subj')
        elif token.dep in ['dobj', 'iobj'] and main_verb_idx is not None:
            token_nodes[main_verb_idx].add_child(noun_phrase_node, 'obj')
        elif token.dep == 'pobj':
            # Object of preposition - handled by prep phrase
            pass
        else:
            edge_label = self._edge_mapper.get_edge_label(token)
            clause_node.add_child(noun_phrase_node, edge_label) 