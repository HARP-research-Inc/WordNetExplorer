"""
Sentence analyzer service using spaCy for linguistic analysis.
"""

import spacy
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from nltk.corpus import wordnet as wn
import streamlit as st


@dataclass
class TokenInfo:
    """Information about a parsed token."""
    text: str
    lemma: str
    pos: str  # Universal POS tag
    tag: str  # Detailed POS tag
    dep: str  # Dependency relation
    head: int  # Index of head token
    children: List[int]  # Indices of child tokens
    synsets: List[str]  # WordNet synsets
    selected_sense: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'text': self.text,
            'lemma': self.lemma,
            'pos': self.pos,
            'tag': self.tag,
            'dep': self.dep,
            'head': self.head,
            'children': self.children,
            'synsets': self.synsets,
            'selected_sense': self.selected_sense
        }


@dataclass
class SentenceAnalysis:
    """Complete analysis of a sentence."""
    text: str
    tokens: List[TokenInfo]
    root_index: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'text': self.text,
            'tokens': [t.to_dict() for t in self.tokens],
            'root_index': self.root_index
        }


class SentenceAnalyzer:
    """Analyze sentences using spaCy and link to WordNet."""
    
    def __init__(self):
        """Initialize the sentence analyzer."""
        self._nlp = None
        self._pos_map = {
            'NOUN': 'n',
            'VERB': 'v',
            'ADJ': 'a',
            'ADV': 'r'
        }
    
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
    
    def analyze_sentence(self, sentence: str) -> SentenceAnalysis:
        """
        Analyze a sentence and extract linguistic information.
        
        Args:
            sentence: The sentence to analyze
            
        Returns:
            SentenceAnalysis object with parsed information
        """
        # Parse the sentence
        doc = self.nlp(sentence)
        
        # Extract token information
        tokens = []
        root_index = 0
        
        for i, token in enumerate(doc):
            # Get WordNet synsets for the token
            synsets = self._get_synsets_for_token(token)
            
            # Get children indices
            children = [child.i for child in token.children]
            
            # Create token info
            token_info = TokenInfo(
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                tag=token.tag_,
                dep=token.dep_,
                head=token.head.i if token.head != token else i,
                children=children,
                synsets=synsets
            )
            
            tokens.append(token_info)
            
            # Track root token
            if token.dep_ == "ROOT":
                root_index = i
        
        return SentenceAnalysis(
            text=sentence,
            tokens=tokens,
            root_index=root_index
        )
    
    def _get_synsets_for_token(self, token) -> List[str]:
        """Get WordNet synsets for a spaCy token."""
        # Map spaCy POS to WordNet POS
        wn_pos = self._pos_map.get(token.pos_)
        
        if wn_pos:
            # Get synsets with specific POS
            synsets = wn.synsets(token.lemma_, pos=wn_pos)
        else:
            # Get all synsets
            synsets = wn.synsets(token.lemma_)
        
        # Return synset names
        return [s.name() for s in synsets[:5]]  # Limit to top 5
    
    def disambiguate_token(self, token_info: TokenInfo, context: str) -> Optional[str]:
        """
        Disambiguate a token to find the most likely synset.
        
        Args:
            token_info: Token information
            context: The sentence context
            
        Returns:
            The most likely synset name or None
        """
        if not token_info.synsets:
            return None
        
        # For now, use a simple heuristic - return the first (most common) synset
        # In a more sophisticated implementation, we could use the sense similarity
        # calculator from the disambiguation tab
        return token_info.synsets[0]
    
    def get_pos_color(self, pos: str) -> str:
        """Get color for a POS tag."""
        # Map detailed POS tags to colors
        if pos.startswith('NN'):  # Nouns
            return '#FFB6C1'
        elif pos.startswith('VB'):  # Verbs
            return '#98D8C8'
        elif pos.startswith('JJ'):  # Adjectives
            return '#F7DC6F'
        elif pos.startswith('RB'):  # Adverbs
            return '#BB8FCE'
        elif pos in ['DT', 'PRP', 'PRP$', 'WDT', 'WP', 'WP$']:  # Determiners/Pronouns
            return '#85C1E2'
        elif pos in ['IN', 'TO']:  # Prepositions
            return '#F8C471'
        elif pos in ['CC']:  # Conjunctions
            return '#ABEBC6'
        else:
            return '#D5D8DC'  # Default gray
    
    def get_dependency_color(self, dep: str) -> str:
        """Get color for a dependency relation."""
        # Core grammatical relations
        if dep in ['nsubj', 'nsubjpass']:
            return '#FF6B6B'  # Red - subjects
        elif dep in ['dobj', 'iobj', 'pobj']:
            return '#4ECDC4'  # Teal - objects
        elif dep in ['amod', 'advmod', 'nummod']:
            return '#95E1D3'  # Mint - modifiers
        elif dep == 'ROOT':
            return '#FFD93D'  # Gold - root
        elif dep in ['aux', 'auxpass', 'cop']:
            return '#6BCB77'  # Green - auxiliaries
        elif dep in ['prep', 'pcomp']:
            return '#FF8B94'  # Pink - prepositions
        else:
            return '#B4B4B4'  # Gray - other 