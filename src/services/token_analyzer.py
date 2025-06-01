"""
Token analyzer module for processing individual tokens and retrieving synsets.
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from nltk.corpus import wordnet as wn


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
    best_synset: Optional[Tuple[str, str]] = None  # (synset_name, definition)
    
    def to_dict(self):
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
            'selected_sense': self.selected_sense,
            'best_synset': self.best_synset
        }


class TokenAnalyzer:
    """Analyzes tokens and retrieves WordNet synsets."""
    
    def __init__(self):
        """Initialize the token analyzer."""
        self._pos_map = {
            'NOUN': 'n',
            'VERB': 'v',
            'ADJ': 'a',
            'ADV': 'r'
        }
        # POS tags that WordNet doesn't handle
        self._skip_pos = {'PRON', 'DET', 'CCONJ', 'SCONJ', 'PART', 'PUNCT', 'SYM', 'X'}
    
    def analyze_token(self, token, token_index: int) -> TokenInfo:
        """
        Analyze a spaCy token and create TokenInfo.
        
        Args:
            token: spaCy token object
            token_index: Index of this token in the sentence
            
        Returns:
            TokenInfo object
        """
        # Get WordNet synsets for the token
        synsets = self.get_synsets_for_token(token)
        
        # Get children indices
        children = [child.i for child in token.children]
        
        # Create token info
        return TokenInfo(
            text=token.text,
            lemma=token.lemma_,
            pos=token.pos_,
            tag=token.tag_,
            dep=token.dep_,
            head=token.head.i if token.head != token else token_index,
            children=children,
            synsets=synsets,
            best_synset=None  # Will be filled by disambiguation
        )
    
    def get_synsets_for_token(self, token) -> List[str]:
        """Get WordNet synsets for a spaCy token."""
        # Skip synsets for certain POS tags that WordNet doesn't handle
        if token.pos_ in self._skip_pos:
            return []
        
        # Map spaCy POS to WordNet POS
        wn_pos = self._pos_map.get(token.pos_)
        
        # Special handling for ADP (adpositions) that might be adverbs in WordNet
        if token.pos_ == 'ADP' and token.lemma_.lower() in ['over', 'up', 'down', 'out', 'off', 'on', 'in', 'away', 'around', 'through']:
            # Try to get adverb synsets first
            adv_synsets = wn.synsets(token.lemma_, pos='r')
            if adv_synsets:
                return [s.name() for s in adv_synsets[:5]]
        
        # Try to get synsets
        if wn_pos:
            # Get synsets with specific POS
            synsets = wn.synsets(token.lemma_, pos=wn_pos)
        else:
            # For other POS, still try to find synsets
            synsets = wn.synsets(token.lemma_)
            
            # Filter to only those that match WordNet POS categories
            if synsets:
                valid_synsets = []
                for s in synsets:
                    if s.pos() in ['n', 'v', 'a', 's', 'r']:
                        valid_synsets.append(s)
                synsets = valid_synsets
        
        # Special handling: skip certain words only if they have no synsets
        # and are being used as function words
        if not synsets and token.dep_ in ['aux', 'auxpass', 'det', 'case', 'mark']:
            return []
        
        # Return synset names
        return [s.name() for s in synsets[:5]]  # Limit to top 5 