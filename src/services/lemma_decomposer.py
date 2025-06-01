"""
Lemma decomposer module for breaking down words into base forms with grammatical annotations.
"""

from typing import Dict, Optional, Tuple
from src.services.token_analyzer import TokenInfo
from src.services.syntactic_tree import SyntacticNode


class LemmaDecomposer:
    """Decomposes words into lemmas with grammatical information."""
    
    def __init__(self, node_id_generator):
        """Initialize with node ID generator."""
        self._get_node_id = node_id_generator
    
    def should_decompose(self, token: TokenInfo) -> bool:
        """Check if a token should be decomposed."""
        # Don't decompose if lemma is same as text
        if token.lemma.lower() == token.text.lower():
            return False
        
        # Don't decompose single character tokens
        if len(token.text) <= 1:
            return False
        
        # Don't decompose particles, prepositions, determiners, etc.
        # These don't have inflected forms that need decomposition
        non_decomposable_pos = ['PART', 'ADP', 'DET', 'CCONJ', 'SCONJ', 'PRON', 'INTJ', 'PUNCT', 'SYM', 'X']
        if token.pos in non_decomposable_pos:
            return False
        
        # Don't decompose "to" when it's an infinitive marker
        if token.text.lower() == 'to' and token.tag == 'TO':
            return False
        
        # Only decompose verbs, nouns, adjectives, and adverbs
        return token.pos in ['VERB', 'NOUN', 'ADJ', 'ADV']
    
    def get_grammatical_label(self, token: TokenInfo) -> str:
        """Get grammatical label for the decomposition edge."""
        pos = token.pos
        tag = token.tag
        
        if pos == 'VERB':
            return self._get_verb_label(tag)
        elif pos == 'NOUN':
            return self._get_noun_label(tag)
        elif pos == 'ADJ':
            return self._get_adjective_label(tag)
        elif pos == 'ADV':
            return self._get_adverb_label(tag)
        else:
            return 'form'
    
    def _get_verb_label(self, tag: str) -> str:
        """Get verb conjugation/aspect label."""
        # Penn Treebank verb tags
        verb_labels = {
            'VB': 'base',           # base form
            'VBD': 'past',          # past tense
            'VBG': 'gerund',        # gerund/present participle
            'VBN': 'past_part',     # past participle
            'VBP': 'present',       # present, non-3rd person singular
            'VBZ': 'present_3sg'    # present, 3rd person singular
        }
        
        return verb_labels.get(tag, 'verb_form')
    
    def _get_noun_label(self, tag: str) -> str:
        """Get noun number label."""
        noun_labels = {
            'NN': 'singular',       # noun, singular
            'NNS': 'plural',        # noun, plural
            'NNP': 'proper_sg',     # proper noun, singular
            'NNPS': 'proper_pl'     # proper noun, plural
        }
        
        return noun_labels.get(tag, 'noun_form')
    
    def _get_adjective_label(self, tag: str) -> str:
        """Get adjective degree label."""
        adj_labels = {
            'JJ': 'positive',       # adjective
            'JJR': 'comparative',   # adjective, comparative
            'JJS': 'superlative'    # adjective, superlative
        }
        
        return adj_labels.get(tag, 'adj_form')
    
    def _get_adverb_label(self, tag: str) -> str:
        """Get adverb degree label."""
        adv_labels = {
            'RB': 'positive',       # adverb
            'RBR': 'comparative',   # adverb, comparative
            'RBS': 'superlative'    # adverb, superlative
        }
        
        return adv_labels.get(tag, 'adv_form')
    
    def decompose_word_node(self, word_node: SyntacticNode) -> SyntacticNode:
        """
        Decompose a word node into lemma + form.
        
        Returns the decomposed structure or the original node if no decomposition needed.
        """
        token = word_node.token_info
        
        if not token or not self.should_decompose(token):
            return word_node
        
        # Create a wrapper phrase node
        wrapper_node = SyntacticNode(
            node_id=self._get_node_id(),
            node_type='phrase',
            text=word_node.text
        )
        
        # Create lemma node
        lemma_node = SyntacticNode(
            node_id=self._get_node_id(),
            node_type='word',
            text=token.lemma,
            token_info=token  # Keep token info for synsets
        )
        
        # Get grammatical label
        gram_label = self.get_grammatical_label(token)
        
        # Add lemma as child with grammatical edge
        wrapper_node.add_child(lemma_node, gram_label)
        
        return wrapper_node
    
    def get_detailed_verb_info(self, token: TokenInfo) -> Dict[str, str]:
        """Get detailed verb information including tense, aspect, mood, and voice."""
        tag = token.tag
        info = {}
        
        # Basic tense from tag
        if tag == 'VBD' or tag == 'VBN':
            info['tense'] = 'past'
        elif tag in ['VBP', 'VBZ']:
            info['tense'] = 'present'
        else:
            info['tense'] = 'non-finite'
        
        # Aspect
        if tag == 'VBG':
            info['aspect'] = 'progressive'
        elif tag == 'VBN':
            info['aspect'] = 'perfect'
        else:
            info['aspect'] = 'simple'
        
        # Voice (requires checking dependency)
        if token.dep == 'auxpass':
            info['voice'] = 'passive'
        else:
            info['voice'] = 'active'
        
        # Mood (simplified)
        if token.dep == 'ROOT':
            info['mood'] = 'indicative'
        
        return info 