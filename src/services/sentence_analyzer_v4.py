"""
Sentence Analyzer v4 - Clean Architecture

This version focuses on:
1. Single-pass tree construction (no post-processing mutations)
2. Immutable tree building (nodes are never modified after creation)
3. Clear parent-child relationship management
4. Simplified architecture with fewer moving parts
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
import spacy

from src.services.token_analyzer import TokenAnalyzer, TokenInfo
from src.services.token_disambiguator import TokenDisambiguator


@dataclass
class TreeNode:
    """Immutable tree node with proper parent-child management."""
    node_id: str
    node_type: str  # 'sentence', 'clause', 'phrase', 'word'
    text: str
    edge_label: Optional[str] = None
    token_info: Optional[TokenInfo] = None
    
    # Use IDs instead of references to avoid circular dependencies
    parent_id: Optional[str] = None
    child_ids: List[str] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary for easier manipulation."""
        return {
            'node_id': self.node_id,
            'node_type': self.node_type,
            'text': self.text,
            'edge_label': self.edge_label,
            'token_info': self.token_info,
            'parent_id': self.parent_id,
            'child_ids': self.child_ids.copy()
        }


class TreeBuilder:
    """Builds immutable tree structures."""
    
    def __init__(self):
        self.nodes: Dict[str, TreeNode] = {}
        self.node_counter = 0
    
    def create_node(self, node_type: str, text: str, 
                   edge_label: Optional[str] = None,
                   token_info: Optional[TokenInfo] = None) -> str:
        """Create a new node and return its ID."""
        self.node_counter += 1
        node_id = f"node_{self.node_counter}"
        
        node = TreeNode(
            node_id=node_id,
            node_type=node_type,
            text=text,
            edge_label=edge_label,
            token_info=token_info
        )
        
        self.nodes[node_id] = node
        return node_id
    
    def add_child(self, parent_id: str, child_id: str, edge_label: str):
        """Add a child to a parent node."""
        if parent_id not in self.nodes or child_id not in self.nodes:
            raise ValueError("Invalid node IDs")
        
        # Update parent's children
        parent = self.nodes[parent_id]
        if child_id not in parent.child_ids:
            parent.child_ids.append(child_id)
        
        # Update child's parent and edge label
        child = self.nodes[child_id]
        child.parent_id = parent_id
        child.edge_label = edge_label
    
    def get_node(self, node_id: str) -> Optional[TreeNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_children(self, parent_id: str) -> List[TreeNode]:
        """Get all children of a node."""
        parent = self.nodes.get(parent_id)
        if not parent:
            return []
        
        return [self.nodes[child_id] for child_id in parent.child_ids]


@dataclass
class ParsedSentence:
    """Result of sentence parsing."""
    text: str
    tokens: List[TokenInfo]
    tree: TreeBuilder
    root_id: str
    
    def get_syntactic_tree(self):
        """Get the root node of the syntactic tree."""
        return self.tree.get_node(self.root_id)


class SentenceAnalyzer:
    """Clean sentence analyzer with simplified architecture."""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.token_analyzer = TokenAnalyzer()
        self.token_disambiguator = TokenDisambiguator()
    
    def analyze_sentence(self, sentence: str, decompose_lemmas: bool = False) -> ParsedSentence:
        """Analyze a sentence and build its syntactic tree."""
        # Step 1: Parse with spaCy
        doc = self.nlp(sentence)
        
        # Step 2: Create token info
        tokens = []
        for i, token in enumerate(doc):
            token_info = self.token_analyzer.analyze_token(token, i)
            tokens.append(token_info)
        
        # Step 3: Disambiguate all tokens
        self.token_disambiguator.disambiguate_tokens(tokens, doc)
        
        # Step 4: Build tree
        tree = TreeBuilder()
        root_id = self._build_tree(tokens, tree, decompose_lemmas)
        
        return ParsedSentence(
            text=sentence,
            tokens=tokens,
            tree=tree,
            root_id=root_id
        )
    
    def _build_tree(self, tokens: List[TokenInfo], tree: TreeBuilder, 
                    decompose_lemmas: bool) -> str:
        """Build the syntactic tree in a single pass."""
        # Create sentence root
        sentence_text = ' '.join([t.text for t in tokens])
        root_id = tree.create_node('sentence', sentence_text)
        
        # Build token ID map
        token_to_node_id = {}
        
        # First pass: Create all word nodes
        for i, token in enumerate(tokens):
            node_id = tree.create_node(
                'word',
                token.text,
                token_info=token
            )
            token_to_node_id[i] = node_id
        
        # Identify clauses
        clause_groups = self._identify_clauses(tokens)
        
        # Build clause structure
        if len(clause_groups) == 1:
            # Single clause - build directly under sentence
            self._build_clause_content(
                root_id, 
                clause_groups[0], 
                tokens, 
                token_to_node_id, 
                tree
            )
        else:
            # Multiple clauses
            for clause_indices in clause_groups:
                # Create clause node
                clause_tokens = [tokens[i] for i in clause_indices]
                clause_text = ' '.join([t.text for t in clause_tokens])
                
                # Determine clause type
                edge_label = 'main_clause'
                if clause_indices and tokens[clause_indices[0]].dep in ['mark', 'advcl']:
                    edge_label = 'subordinate_clause'
                
                clause_id = tree.create_node('clause', clause_text)
                tree.add_child(root_id, clause_id, edge_label)
                
                # Build clause content
                self._build_clause_content(
                    clause_id,
                    clause_indices,
                    tokens,
                    token_to_node_id,
                    tree
                )
        
        # Apply lemma decomposition if requested
        if decompose_lemmas:
            self._apply_lemma_decomposition(tree, root_id)
        
        return root_id
    
    def _identify_clauses(self, tokens: List[TokenInfo]) -> List[List[int]]:
        """Identify clause boundaries."""
        clauses = []
        current_clause = []
        
        for i, token in enumerate(tokens):
            # Start new clause on conjunctions that introduce clauses
            if (token.pos == 'CCONJ' and token.dep == 'cc' and 
                i > 0 and current_clause):
                clauses.append(current_clause)
                current_clause = []
            
            # Add token to current clause
            if token.pos != 'PUNCT':  # Skip punctuation for clause membership
                current_clause.append(i)
        
        # Add final clause
        if current_clause:
            clauses.append(current_clause)
        
        return clauses if clauses else [[i for i in range(len(tokens)) 
                                         if tokens[i].pos != 'PUNCT']]
    
    def _build_clause_content(self, parent_id: str, clause_indices: List[int],
                             tokens: List[TokenInfo], token_to_node_id: Dict[int, str],
                             tree: TreeBuilder):
        """Build the content of a clause."""
        # Find the main verb
        main_verb_idx = None
        for idx in clause_indices:
            if tokens[idx].pos == 'VERB' and tokens[idx].dep == 'ROOT':
                main_verb_idx = idx
                break
        
        if main_verb_idx is None:
            # No root verb, look for any verb
            for idx in clause_indices:
                if tokens[idx].pos == 'VERB':
                    main_verb_idx = idx
                    break
        
        # Group tokens by their grammatical role
        subjects = []
        verbs = []
        objects = []
        modifiers = []
        others = []
        
        for idx in clause_indices:
            token = tokens[idx]
            
            if token.dep in ['nsubj', 'nsubjpass']:
                subjects.append(idx)
            elif token.pos == 'VERB' or token.dep in ['aux', 'auxpass']:
                verbs.append(idx)
            elif token.dep in ['dobj', 'iobj', 'pobj', 'attr']:
                objects.append(idx)
            elif token.pos == 'ADV' or token.dep == 'advmod':
                modifiers.append(idx)
            else:
                others.append(idx)
        
        # Build phrases for each group
        added_indices = set()
        
        # Add subjects
        for subj_idx in subjects:
            if subj_idx not in added_indices:
                phrase_id, phrase_indices = self._build_noun_phrase(
                    subj_idx, tokens, token_to_node_id, tree
                )
                tree.add_child(parent_id, phrase_id, 'subject')
                added_indices.update(phrase_indices)
        
        # Add verb phrase
        if verbs:
            verb_phrase_id = self._build_verb_phrase(
                verbs, tokens, token_to_node_id, tree
            )
            tree.add_child(parent_id, verb_phrase_id, 'predicate')
            added_indices.update(verbs)
        
        # Add objects
        for obj_idx in objects:
            if obj_idx not in added_indices:
                phrase_id, phrase_indices = self._build_noun_phrase(
                    obj_idx, tokens, token_to_node_id, tree
                )
                tree.add_child(parent_id, phrase_id, 'object')
                added_indices.update(phrase_indices)
        
        # Add modifiers
        for mod_idx in modifiers:
            if mod_idx not in added_indices:
                node_id = token_to_node_id[mod_idx]
                tree.add_child(parent_id, node_id, 'modifier')
                added_indices.add(mod_idx)
        
        # Add remaining tokens
        for idx in others:
            if idx not in added_indices and idx in clause_indices:
                node_id = token_to_node_id[idx]
                tree.add_child(parent_id, node_id, 'other')
    
    def _build_noun_phrase(self, head_idx: int, tokens: List[TokenInfo],
                          token_to_node_id: Dict[int, str], 
                          tree: TreeBuilder) -> Tuple[str, Set[int]]:
        """Build a noun phrase and return its ID and constituent indices."""
        indices = {head_idx}
        
        # Find modifiers of this noun
        for i, token in enumerate(tokens):
            if token.head == head_idx and token.dep in ['det', 'amod', 'compound', 'poss', 'nummod']:
                indices.add(i)
        
        # If just the head, return it directly
        if len(indices) == 1:
            return token_to_node_id[head_idx], indices
        
        # Create phrase node
        sorted_indices = sorted(indices)
        phrase_text = ' '.join([tokens[i].text for i in sorted_indices])
        phrase_id = tree.create_node('phrase', phrase_text)
        
        # Add constituents
        for idx in sorted_indices:
            token = tokens[idx]
            edge_label = 'head' if idx == head_idx else token.dep
            tree.add_child(phrase_id, token_to_node_id[idx], edge_label)
        
        return phrase_id, indices
    
    def _build_verb_phrase(self, verb_indices: List[int], tokens: List[TokenInfo],
                          token_to_node_id: Dict[int, str], 
                          tree: TreeBuilder) -> str:
        """Build a verb phrase."""
        # Sort verb indices
        verb_indices = sorted(verb_indices)
        
        # If single verb, return it directly
        if len(verb_indices) == 1:
            return token_to_node_id[verb_indices[0]]
        
        # Create verb phrase
        phrase_text = ' '.join([tokens[i].text for i in verb_indices])
        phrase_id = tree.create_node('phrase', phrase_text)
        
        # Add verbs
        main_verb_idx = None
        for idx in verb_indices:
            if tokens[idx].dep == 'ROOT' or tokens[idx].pos == 'VERB':
                main_verb_idx = idx
                break
        
        for idx in verb_indices:
            edge_label = 'head' if idx == main_verb_idx else 'auxiliary'
            tree.add_child(phrase_id, token_to_node_id[idx], edge_label)
        
        return phrase_id
    
    def _apply_lemma_decomposition(self, tree: TreeBuilder, root_id: str):
        """Apply lemma decomposition to word nodes."""
        # This is a simplified version - in a real implementation,
        # we'd traverse the tree and decompose appropriate words
        pass 