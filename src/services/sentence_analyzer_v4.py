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
        
        # Track depth for nested clauses
        clause_starters = {'that', 'who', 'which', 'where', 'when', 'if', 'because', 'although', 'while'}
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Check for clause starters
            if (token.text.lower() in clause_starters or 
                token.dep in ['mark', 'ccomp', 'advcl'] or
                (token.pos == 'CCONJ' and token.dep == 'cc' and current_clause)):
                
                # Save current clause if it has content
                if current_clause:
                    clauses.append(current_clause)
                    current_clause = []
            
            # Add non-punctuation tokens to current clause
            if token.pos != 'PUNCT':
                current_clause.append(i)
            
            i += 1
        
        # Add final clause
        if current_clause:
            clauses.append(current_clause)
        
        # If no clauses identified, treat whole sentence as one clause
        if not clauses:
            clauses = [[i for i in range(len(tokens)) if tokens[i].pos != 'PUNCT']]
        
        return clauses
    
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
        prepositions = []
        punctuation = []
        others = []
        
        # First, also check all tokens (not just clause_indices) for punctuation
        all_indices = set(clause_indices)
        for i, token in enumerate(tokens):
            if token.pos == 'PUNCT' and i not in all_indices:
                all_indices.add(i)
        
        for idx in all_indices:
            token = tokens[idx]
            
            if token.dep in ['nsubj', 'nsubjpass']:
                subjects.append(idx)
            elif token.pos == 'VERB' or token.dep in ['aux', 'auxpass']:
                verbs.append(idx)
            elif token.dep in ['dobj', 'iobj', 'attr']:
                objects.append(idx)
            elif token.dep == 'pobj':
                # Handle separately to build prep phrases
                pass
            elif token.pos == 'ADP' or token.dep == 'prep':
                prepositions.append(idx)
            elif token.pos == 'ADV' or token.dep == 'advmod':
                modifiers.append(idx)
            elif token.pos == 'PUNCT':
                punctuation.append(idx)
            else:
                others.append(idx)
        
        # Build phrases for each group
        added_indices = set()
        
        # Check for phrasal verbs first
        phrasal_verb_indices = set()
        if verbs:
            phrasal_verb_id, phrasal_indices = self._check_and_build_phrasal_verb(
                verbs[0] if verbs else main_verb_idx, tokens, token_to_node_id, tree
            )
            if phrasal_verb_id:
                tree.add_child(parent_id, phrasal_verb_id, 'predicate')
                added_indices.update(phrasal_indices)
                phrasal_verb_indices = phrasal_indices
        
        # Add subjects
        for subj_idx in subjects:
            if subj_idx not in added_indices:
                phrase_id, phrase_indices = self._build_noun_phrase(
                    subj_idx, tokens, token_to_node_id, tree
                )
                tree.add_child(parent_id, phrase_id, 'subject')
                added_indices.update(phrase_indices)
        
        # Add verb phrase (if not already added as phrasal verb)
        if verbs and not phrasal_verb_indices:
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
        
        # Build prepositional phrases
        for prep_idx in prepositions:
            if prep_idx not in added_indices:
                prep_phrase_id, prep_indices = self._build_prep_phrase(
                    prep_idx, tokens, token_to_node_id, tree
                )
                if prep_phrase_id:
                    tree.add_child(parent_id, prep_phrase_id, 'prep_phrase')
                    added_indices.update(prep_indices)
        
        # Add modifiers
        for mod_idx in modifiers:
            if mod_idx not in added_indices:
                node_id = token_to_node_id[mod_idx]
                tree.add_child(parent_id, node_id, 'modifier')
                added_indices.add(mod_idx)
        
        # Add remaining tokens
        for idx in others:
            if idx not in added_indices:
                node_id = token_to_node_id[idx]
                tree.add_child(parent_id, node_id, 'other')
                added_indices.add(idx)
        
        # Add punctuation at the end
        for punct_idx in punctuation:
            if punct_idx not in added_indices:
                node_id = token_to_node_id[punct_idx]
                tree.add_child(parent_id, node_id, 'punct')
                added_indices.add(punct_idx)
    
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
            # Keep original dependency label
            edge_label = token.dep if token.dep else 'word'
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
            # Use original dependency label or 'aux'/'ROOT' as appropriate
            if idx == main_verb_idx:
                edge_label = 'ROOT' if tokens[idx].dep == 'ROOT' else 'verb'
            else:
                edge_label = tokens[idx].dep if tokens[idx].dep in ['aux', 'auxpass'] else 'aux'
            tree.add_child(phrase_id, token_to_node_id[idx], edge_label)
        
        return phrase_id
    
    def _apply_lemma_decomposition(self, tree: TreeBuilder, root_id: str):
        """Apply lemma decomposition to word nodes."""
        # Get all word nodes
        word_nodes = []
        nodes_to_check = [root_id]
        
        while nodes_to_check:
            node_id = nodes_to_check.pop(0)
            node = tree.get_node(node_id)
            if node:
                if node.node_type == 'word' and node.token_info:
                    word_nodes.append(node_id)
                nodes_to_check.extend(node.child_ids)
        
        # Process each word node
        for word_id in word_nodes:
            word_node = tree.get_node(word_id)
            if not word_node or not word_node.token_info:
                continue
            
            token = word_node.token_info
            
            # Check if decomposition is needed
            if token.lemma.lower() == token.text.lower():
                continue
            
            # Skip certain POS tags
            if token.pos in ['DET', 'PRON', 'ADP', 'CCONJ', 'SCONJ', 'PART', 'PUNCT']:
                continue
            
            # Find parent
            parent_id = word_node.parent_id
            if not parent_id:
                continue
            
            parent = tree.get_node(parent_id)
            if not parent:
                continue
            
            # Create wrapper phrase
            wrapper_id = tree.create_node('phrase', word_node.text)
            
            # Create lemma node
            lemma_id = tree.create_node('word', token.lemma, token_info=token)
            
            # Get grammatical label
            gram_label = self._get_grammatical_label(token)
            
            # Build the decomposition structure
            tree.add_child(wrapper_id, lemma_id, gram_label)
            
            # Replace word node with wrapper in parent's children
            parent.child_ids = [wrapper_id if cid == word_id else cid 
                               for cid in parent.child_ids]
            
            # Update wrapper's parent info
            wrapper_node = tree.get_node(wrapper_id)
            wrapper_node.parent_id = parent_id
            wrapper_node.edge_label = word_node.edge_label
    
    def _get_grammatical_label(self, token: TokenInfo) -> str:
        """Get grammatical label for decomposition."""
        if token.pos == 'VERB':
            verb_labels = {
                'VBD': 'past',
                'VBG': 'gerund',
                'VBN': 'past_part',
                'VBP': 'present',
                'VBZ': 'present_3sg'
            }
            return verb_labels.get(token.tag, 'verb_form')
        elif token.pos == 'NOUN':
            if token.tag == 'NNS' or token.tag == 'NNPS':
                return 'plural'
            return 'singular'
        elif token.pos == 'ADJ':
            if token.tag == 'JJR':
                return 'comparative'
            elif token.tag == 'JJS':
                return 'superlative'
            return 'positive'
        elif token.pos == 'ADV':
            if token.tag == 'RBR':
                return 'comparative'
            elif token.tag == 'RBS':
                return 'superlative'
            return 'positive'
        else:
            return 'form'

    def _check_and_build_phrasal_verb(self, verb_idx: int, tokens: List[TokenInfo],
                                     token_to_node_id: Dict[int, str], 
                                     tree: TreeBuilder) -> Tuple[Optional[str], Set[int]]:
        """Check if this verb forms a phrasal verb and build it."""
        if verb_idx is None:
            return None, set()
        
        verb_token = tokens[verb_idx]
        indices = {verb_idx}
        
        # Common phrasal verb patterns
        phrasal_patterns = {
            'look': ['up', 'over', 'into', 'after'],
            'run': ['over', 'into', 'down', 'up'],
            'turn': ['on', 'off', 'over', 'down'],
            'take': ['over', 'off', 'out', 'up'],
            'put': ['on', 'off', 'up', 'down'],
            'get': ['up', 'down', 'over', 'off']
        }
        
        verb_lemma = verb_token.lemma.lower()
        if verb_lemma not in phrasal_patterns:
            return None, set()
        
        # Look for particle after verb
        for i in range(verb_idx + 1, min(verb_idx + 4, len(tokens))):
            token = tokens[i]
            if (token.text.lower() in phrasal_patterns[verb_lemma] and
                (token.dep == 'prt' or token.pos in ['ADP', 'ADV'])):
                # Found phrasal verb
                indices.add(i)
                
                # Create phrasal verb node
                phrase_text = f"{verb_token.text} {token.text}"
                phrase_id = tree.create_node('phrase', phrase_text)
                
                # Add verb and particle
                tree.add_child(phrase_id, token_to_node_id[verb_idx], 'verb')
                tree.add_child(phrase_id, token_to_node_id[i], 'particle')
                
                return phrase_id, indices
        
        return None, set()
    
    def _build_prep_phrase(self, prep_idx: int, tokens: List[TokenInfo],
                          token_to_node_id: Dict[int, str], 
                          tree: TreeBuilder) -> Tuple[Optional[str], Set[int]]:
        """Build a prepositional phrase."""
        prep_token = tokens[prep_idx]
        indices = {prep_idx}
        
        # Find object of preposition
        pobj_idx = None
        for i, token in enumerate(tokens):
            if token.head == prep_idx and token.dep == 'pobj':
                pobj_idx = i
                break
        
        if pobj_idx is None:
            return None, set()
        
        # Build the object (might be a noun phrase)
        obj_id, obj_indices = self._build_noun_phrase(
            pobj_idx, tokens, token_to_node_id, tree
        )
        indices.update(obj_indices)
        
        # Create prepositional phrase
        sorted_indices = sorted(indices)
        phrase_text = ' '.join([tokens[i].text for i in sorted_indices])
        phrase_id = tree.create_node('phrase', phrase_text)
        
        # Add preposition and object
        tree.add_child(phrase_id, token_to_node_id[prep_idx], 'prep')
        tree.add_child(phrase_id, obj_id, 'pobj')
        
        return phrase_id, indices 