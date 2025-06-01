"""
Streamlined sentence analyzer using modular components.
"""

import spacy
from typing import List, Optional
from dataclasses import dataclass
import streamlit as st

from .token_analyzer import TokenAnalyzer, TokenInfo
from .token_disambiguator import TokenDisambiguator
from .syntactic_tree import SyntacticNode
from .clause_identifier import ClauseIdentifier
from .clause_builder import ClauseBuilder
from .tree_postprocessor import TreePostProcessor
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


class SentenceAnalyzer:
    """
    Streamlined sentence analyzer using modular components.
    
    This analyzer orchestrates various specialized components to:
    1. Parse sentences using spaCy
    2. Extract token information and WordNet synsets
    3. Disambiguate word senses
    4. Build syntactic tree structures
    5. Post-process for better visualization
    """
    
    def __init__(self):
        """Initialize the sentence analyzer components."""
        self._nlp = None
        self._token_analyzer = TokenAnalyzer()
        self._token_disambiguator = TokenDisambiguator()
        self._clause_identifier = ClauseIdentifier()
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
        
        # Step 1: Parse with spaCy
        doc = self.nlp(sentence)
        
        # Step 2: Analyze tokens
        tokens = self._analyze_tokens(doc)
        
        # Step 3: Disambiguate word senses
        self._token_disambiguator.disambiguate_tokens(tokens, doc)
        
        # Step 4: Build syntactic tree
        syntactic_tree = self._build_syntactic_tree(doc, tokens)
        
        # Find root token
        root_index = next((i for i, t in enumerate(tokens) if t.dep == "ROOT"), 0)
        
        return SentenceAnalysis(
            text=sentence,
            tokens=tokens,
            root_index=root_index,
            syntactic_tree=syntactic_tree
        )
    
    def _analyze_tokens(self, doc) -> List[TokenInfo]:
        """Analyze all tokens in the document."""
        tokens = []
        
        for i, token in enumerate(doc):
            token_info = self._token_analyzer.analyze_token(token, i)
            tokens.append(token_info)
        
        return tokens
    
    def _build_syntactic_tree(self, doc, tokens: List[TokenInfo]) -> SyntacticNode:
        """Build syntactic tree from tokens."""
        # Create root sentence node
        root = SyntacticNode(
            node_id=self._get_node_id(),
            node_type='sentence',
            text=doc.text
        )
        
        # Identify clauses
        clauses = self._clause_identifier.identify_clauses(doc, tokens)
        
        # Build clause structures
        if len(clauses) == 1:
            # Simple sentence
            self._build_simple_sentence(root, clauses[0], tokens)
        else:
            # Complex sentence
            self._build_complex_sentence(root, clauses, tokens, doc)
        
        return root
    
    def _build_simple_sentence(self, root: SyntacticNode, clause_indices: List[int], 
                              tokens: List[TokenInfo]):
        """Build structure for a simple sentence."""
        clause_builder = ClauseBuilder(self._get_node_id)
        tree_processor = TreePostProcessor(self._get_node_id)
        
        # Build clause tree
        clause_builder.build_clause_tree(root, clause_indices, tokens, 'main')
        
        # Apply post-processing
        tree_processor.group_object_phrases(root, tokens, clause_indices)
        tree_processor.reinterpret_phrasal_verbs(root, tokens)
        tree_processor.restructure_clause_for_presentation(root, tokens)
    
    def _build_complex_sentence(self, root: SyntacticNode, clauses: List[List[int]], 
                               tokens: List[TokenInfo], doc):
        """Build structure for a complex sentence with multiple clauses."""
        clause_builder = ClauseBuilder(self._get_node_id)
        tree_processor = TreePostProcessor(self._get_node_id)
        
        # Find conjunctions
        conjunctions = []
        for i, token in enumerate(doc):
            if token.dep_ in ['cc', 'mark'] or token.pos_ in ['SCONJ', 'CCONJ']:
                conjunctions.append((i, token))
        
        if conjunctions:
            # Create structure with conjunctions
            main_conj = conjunctions[0]
            conj_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='word',
                text=main_conj[1].text,
                token_info=tokens[main_conj[0]]
            )
            root.add_child(conj_node, 'sconj')
            
            # Add clauses
            for i, clause_indices in enumerate(clauses):
                clause_text = ' '.join([tokens[idx].text for idx in clause_indices])
                clause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=clause_text
                )
                
                edge_label = 'iclause' if i == 0 else 'dclause'
                conj_node.add_child(clause_node, edge_label)
                
                # Build clause content
                clause_builder.build_clause_tree(clause_node, clause_indices, tokens, 'sub')
                
                # Apply post-processing
                tree_processor.group_object_phrases(clause_node, tokens, clause_indices)
                tree_processor.reinterpret_phrasal_verbs(clause_node, tokens)
                tree_processor.restructure_clause_for_presentation(clause_node, tokens)
        else:
            # Coordinate clauses without explicit conjunction
            for i, clause_indices in enumerate(clauses):
                clause_text = ' '.join([tokens[idx].text for idx in clause_indices])
                clause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=clause_text
                )
                
                edge_label = 'clause' if i == 0 else 'coord_clause'
                root.add_child(clause_node, edge_label)
                
                # Build clause content
                clause_builder.build_clause_tree(clause_node, clause_indices, tokens, 
                                               'main' if i == 0 else 'coord')
                
                # Apply post-processing
                tree_processor.group_object_phrases(clause_node, tokens, clause_indices)
                tree_processor.reinterpret_phrasal_verbs(clause_node, tokens)
                tree_processor.restructure_clause_for_presentation(clause_node, tokens)
    
    # Color methods for backward compatibility
    def get_pos_color(self, pos: str) -> str:
        """Get color for a POS tag."""
        return self.colors.get_pos_color(pos)
    
    def get_dependency_color(self, dep: str) -> str:
        """Get color for a dependency relation."""
        return self.colors.get_dependency_color(dep) 