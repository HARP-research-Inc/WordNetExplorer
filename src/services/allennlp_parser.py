"""AllenNLP-based parser for generating syntactic trees.

This replaces the complex spaCy dependency-to-constituency conversion
with a direct constituency parser.
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from allennlp_models import pretrained
    ALLENNLP_AVAILABLE = True
except ImportError:
    ALLENNLP_AVAILABLE = False
    logger.warning("AllenNLP not installed. Install with: pip install allennlp allennlp-models")

from ..syntactic_tree import SyntacticNode
from ..token_analyzer import TokenInfo


class AllenNLPParser:
    """Parser using AllenNLP's constituency parser."""
    
    def __init__(self):
        """Initialize the parser."""
        self._parser = None
        self._node_counter = 0
        
    @property
    def parser(self):
        """Lazy load the parser model."""
        if self._parser is None and ALLENNLP_AVAILABLE:
            logger.info("Loading AllenNLP constituency parser...")
            # Use the constituency parser which gives us the tree structure we want
            self._parser = pretrained.load_predictor("structured-prediction-constituency-parser")
            logger.info("Parser loaded successfully")
        return self._parser
    
    def _get_node_id(self) -> str:
        """Get a unique node ID."""
        self._node_counter += 1
        return f"node_{self._node_counter}"
    
    def parse_sentence(self, sentence: str) -> Optional[SyntacticNode]:
        """Parse a sentence and return a syntactic tree.
        
        Args:
            sentence: The sentence to parse
            
        Returns:
            SyntacticNode representing the parse tree, or None if parsing fails
        """
        if not ALLENNLP_AVAILABLE:
            logger.error("AllenNLP not available")
            return None
            
        if not self.parser:
            logger.error("Failed to load parser")
            return None
        
        # Reset node counter
        self._node_counter = 0
        
        try:
            # Get the constituency parse
            result = self.parser.predict(sentence=sentence)
            
            # The result contains a 'trees' field with the parse tree
            tree_str = result.get('trees', '')
            
            # Also get the POS tags and tokens
            tokens = result.get('tokens', [])
            pos_tags = result.get('pos_tags', [])
            
            logger.info(f"Parse tree: {tree_str}")
            
            # Convert the bracketed tree string to our SyntacticNode structure
            root = self._parse_tree_string(tree_str, tokens, pos_tags)
            
            return root
            
        except Exception as e:
            logger.error(f"Error parsing sentence: {e}")
            return None
    
    def _parse_tree_string(self, tree_str: str, tokens: List[str], pos_tags: List[str]) -> SyntacticNode:
        """Convert AllenNLP's tree string to our SyntacticNode structure.
        
        The tree string looks like: (S (NP (PRP She)) (VP (MD should) ...))
        """
        # Create a simple parser for the bracketed notation
        self._tokens = tokens
        self._pos_tags = pos_tags
        self._token_index = 0
        
        # Parse the tree
        return self._parse_node(tree_str.strip())
    
    def _parse_node(self, s: str) -> Optional[SyntacticNode]:
        """Parse a node from the bracketed string."""
        s = s.strip()
        
        if not s.startswith('('):
            # Terminal node (word)
            return None
            
        # Find the label
        label_end = s.find(' ', 1)
        if label_end == -1:
            label_end = s.find(')', 1)
        
        label = s[1:label_end]
        
        # Create node
        node = SyntacticNode(
            node_id=self._get_node_id(),
            node_type='phrase' if label not in self._pos_tags else 'word',
            text=''  # Will be filled in
        )
        
        # Parse children
        children_str = s[label_end:].strip()
        if children_str.startswith(')'):
            # No children
            return node
            
        # Extract children
        children = self._extract_children(children_str)
        
        for child_str in children:
            child_str = child_str.strip()
            
            if child_str.startswith('('):
                # Non-terminal child
                child_node = self._parse_node(child_str)
                if child_node:
                    # Determine edge label based on constituent type
                    edge_label = self._get_edge_label(label, child_node)
                    node.add_child(child_node, edge_label)
            else:
                # Terminal child (word)
                if self._token_index < len(self._tokens):
                    word = self._tokens[self._token_index]
                    pos = self._pos_tags[self._token_index] if self._token_index < len(self._pos_tags) else 'UNK'
                    
                    # Create word node
                    word_node = SyntacticNode(
                        node_id=self._get_node_id(),
                        node_type='word',
                        text=word,
                        token_info=TokenInfo(
                            text=word,
                            lemma=word.lower(),  # Simple lemmatization
                            pos=pos,
                            dep='',  # No dependency info from constituency parse
                            head=0,
                            index=self._token_index
                        )
                    )
                    
                    edge_label = 'head' if len(node.children) == 0 else 'word'
                    node.add_child(word_node, edge_label)
                    self._token_index += 1
        
        # Set node text based on children
        if node.children:
            node.text = ' '.join([child.text for child in node.children if child.text])
        
        return node
    
    def _extract_children(self, s: str) -> List[str]:
        """Extract child constituents from a bracketed string."""
        children = []
        depth = 0
        current = []
        
        for char in s:
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                
            current.append(char)
            
            if depth == 0 and current:
                child_str = ''.join(current).strip()
                if child_str and child_str != ')':
                    children.append(child_str)
                current = []
                
        return children
    
    def _get_edge_label(self, parent_label: str, child_node: SyntacticNode) -> str:
        """Determine edge label based on constituent types."""
        # Map common constituent labels to edge labels
        if child_node.node_type == 'word':
            return 'word'
        
        child_label = child_node.text.split()[0] if child_node.text else ''
        
        # Common patterns
        if parent_label == 'S':
            if child_label == 'NP':
                return 'subj'
            elif child_label == 'VP':
                return 'pred'
                
        elif parent_label == 'VP':
            if child_label == 'VB' or child_label.startswith('VB'):
                return 'verb'
            elif child_label == 'NP':
                return 'obj'
            elif child_label == 'PP':
                return 'prep_phrase'
            elif child_label.startswith('RB'):
                return 'adv_mod'
                
        elif parent_label == 'NP':
            if child_label == 'DT':
                return 'det'
            elif child_label.startswith('JJ'):
                return 'adj'
            elif child_label.startswith('NN'):
                return 'head'
                
        # Default
        return 'child'
    
    def generate_list_parse(self, node: SyntacticNode) -> str:
        """Generate a list-based representation of the parse tree.
        
        This is much simpler than with the dependency parser since
        we already have the hierarchical structure.
        """
        if node.node_type == 'word':
            return f"[{node.text}]"
            
        # For phrases, recursively process children
        children_repr = []
        for child in node.children:
            children_repr.append(self.generate_list_parse(child))
            
        return f"[{' '.join(children_repr)}]" 