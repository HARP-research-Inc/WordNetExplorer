"""
Sentence analyzer v3 - uses AllenNLP constituency parser when available,
falls back to improved spaCy dependency parsing otherwise.
"""

import logging
from typing import Optional

from .sentence_analyzer_v2 import SentenceAnalyzerV2, SentenceAnalysis
from .syntactic_tree import SyntacticNode

logger = logging.getLogger(__name__)

try:
    from .allennlp_parser import AllenNLPParser, ALLENNLP_AVAILABLE
except ImportError:
    ALLENNLP_AVAILABLE = False
    AllenNLPParser = None


class SentenceAnalyzerV3:
    """Hybrid sentence analyzer using best available parser."""
    
    def __init__(self, prefer_constituency=True):
        """Initialize the analyzer.
        
        Args:
            prefer_constituency: If True, use AllenNLP constituency parser when available
        """
        self.prefer_constituency = prefer_constituency
        self._allennlp_parser = None
        self._spacy_analyzer = None
        
        # Check what's available
        self.has_allennlp = ALLENNLP_AVAILABLE
        self.has_spacy = True  # SpaCy is required
        
        logger.info(f"SentenceAnalyzerV3 initialized:")
        logger.info(f"  AllenNLP available: {self.has_allennlp}")
        logger.info(f"  Using: {'AllenNLP' if self.use_allennlp else 'spaCy'}")
    
    @property
    def use_allennlp(self):
        """Whether to use AllenNLP parser."""
        return self.prefer_constituency and self.has_allennlp
    
    @property
    def allennlp_parser(self):
        """Get AllenNLP parser (lazy load)."""
        if self._allennlp_parser is None and self.has_allennlp:
            self._allennlp_parser = AllenNLPParser()
        return self._allennlp_parser
    
    @property
    def spacy_analyzer(self):
        """Get spaCy analyzer (lazy load)."""
        if self._spacy_analyzer is None:
            self._spacy_analyzer = SentenceAnalyzerV2()
        return self._spacy_analyzer
    
    def analyze_sentence(self, sentence: str, decompose_lemmas: bool = False) -> SentenceAnalysis:
        """Analyze a sentence using the best available parser.
        
        Args:
            sentence: The sentence to analyze
            decompose_lemmas: Whether to decompose words into lemmas (only for spaCy)
            
        Returns:
            SentenceAnalysis object
        """
        if self.use_allennlp:
            logger.debug("Using AllenNLP constituency parser")
            # Try AllenNLP first
            tree = self.allennlp_parser.parse_sentence(sentence)
            
            if tree:
                # Create a SentenceAnalysis object
                # Extract tokens from the tree
                tokens = []
                self._extract_tokens(tree, tokens)
                
                # Generate list parse
                list_parse = self.allennlp_parser.generate_list_parse(tree)
                logger.info(f"List-based parse: {list_parse}")
                
                return SentenceAnalysis(
                    text=sentence,
                    tokens=tokens,
                    root_index=0,  # Not meaningful for constituency parse
                    syntactic_tree=tree
                )
            else:
                logger.warning("AllenNLP parsing failed, falling back to spaCy")
        
        # Fall back to spaCy
        logger.debug("Using spaCy dependency parser")
        return self.spacy_analyzer.analyze_sentence(sentence, decompose_lemmas)
    
    def _extract_tokens(self, node: SyntacticNode, tokens: list):
        """Extract tokens from a syntactic tree."""
        if node.node_type == 'word' and node.token_info:
            tokens.append(node.token_info)
        
        for child in node.children:
            self._extract_tokens(child, tokens)
    
    def generate_list_parse(self, tree: SyntacticNode) -> str:
        """Generate list-based parse representation."""
        if self.use_allennlp and self._allennlp_parser:
            return self._allennlp_parser.generate_list_parse(tree)
        else:
            return self.spacy_analyzer.generate_list_parse(tree) 