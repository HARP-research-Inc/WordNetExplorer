"""
Sentence analyzer service using spaCy for linguistic analysis.
"""

import spacy
from typing import List, Optional, Dict, Any, Tuple, Set
from dataclasses import dataclass, field
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
    best_synset: Optional[Tuple[str, str]] = None  # (synset_name, definition)
    
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
            'selected_sense': self.selected_sense,
            'best_synset': self.best_synset
        }


@dataclass
class SyntacticNode:
    """A node in the syntactic tree."""
    node_id: str
    node_type: str  # 'sentence', 'clause', 'phrase', 'word'
    text: str
    children: List['SyntacticNode'] = field(default_factory=list)
    parent: Optional['SyntacticNode'] = None
    edge_label: Optional[str] = None  # Label on edge from parent
    token_info: Optional[TokenInfo] = None  # For word nodes
    
    def add_child(self, child: 'SyntacticNode', edge_label: str):
        """Add a child with an edge label."""
        child.parent = self
        child.edge_label = edge_label
        self.children.append(child)


@dataclass
class SentenceAnalysis:
    """Complete analysis of a sentence."""
    text: str
    tokens: List[TokenInfo]
    root_index: int
    syntactic_tree: Optional[SyntacticNode] = None
    
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
        self._node_counter = 0
    
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
        # Parse the sentence
        doc = self.nlp(sentence)
        
        # Extract token information
        tokens = []
        root_index = 0
        
        for i, token in enumerate(doc):
            # Get WordNet synsets for the token
            synsets = self._get_synsets_for_token(token)
            
            # Get best synset (for now, just the first one)
            best_synset = None
            if synsets:
                try:
                    synset = wn.synset(synsets[0])
                    best_synset = (synsets[0], synset.definition())
                except:
                    pass
            
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
                synsets=synsets,
                best_synset=best_synset
            )
            
            tokens.append(token_info)
            
            # Track root token
            if token.dep_ == "ROOT":
                root_index = i
        
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
            self._build_clause_tree(root, clauses[0], tokens, 'main')
        else:
            # Complex sentence - identify relationships
            self._build_complex_sentence_tree(root, clauses, tokens, doc)
        
        return root
    
    def _identify_clauses(self, doc, tokens: List[TokenInfo]) -> List[List[int]]:
        """Identify clauses in the sentence."""
        clauses = []
        current_clause = []
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
            for i, clause_indices in enumerate(clauses):
                clause_text = ' '.join([tokens[idx].text for idx in clause_indices])
                clause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=clause_text
                )
                
                # Determine edge label
                if i == 0:
                    edge_label = 'iclause'  # independent clause
                else:
                    edge_label = 'dclause'  # dependent clause
                
                conj_node.add_child(clause_node, edge_label)
                
                # Build the clause subtree
                self._build_clause_tree(clause_node, clause_indices, tokens, 'sub')
        else:
            # No clear conjunction, treat as coordinate clauses
            for i, clause_indices in enumerate(clauses):
                clause_text = ' '.join([tokens[idx].text for idx in clause_indices])
                clause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=clause_text
                )
                
                edge_label = 'clause' if i == 0 else 'coord_clause'
                root.add_child(clause_node, edge_label)
                
                self._build_clause_tree(clause_node, clause_indices, tokens, 'main' if i == 0 else 'coord')
    
    def _build_clause_tree(self, clause_node: SyntacticNode, clause_indices: List[int], 
                          tokens: List[TokenInfo], clause_type: str):
        """Build the tree for a single clause."""
        # Find the main verb
        main_verb_idx = None
        for idx in clause_indices:
            if tokens[idx].pos == 'VERB':
                main_verb_idx = idx
                break
        
        if main_verb_idx is not None:
            # Create verb node
            verb_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='word',
                text=tokens[main_verb_idx].text,
                token_info=tokens[main_verb_idx]
            )
            clause_node.add_child(verb_node, 'tverb')  # tense verb
            
            # Add other constituents
            for idx in clause_indices:
                if idx == main_verb_idx:
                    continue
                
                token = tokens[idx]
                word_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='word',
                    text=token.text,
                    token_info=token
                )
                
                # Determine edge label based on dependency
                edge_label = self._get_edge_label(token)
                
                # Decide where to attach
                if token.head == main_verb_idx:
                    verb_node.add_child(word_node, edge_label)
                else:
                    clause_node.add_child(word_node, edge_label)
        else:
            # No verb found, add all words directly
            for idx in clause_indices:
                token = tokens[idx]
                word_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='word',
                    text=token.text,
                    token_info=token
                )
                edge_label = self._get_edge_label(token)
                clause_node.add_child(word_node, edge_label)
    
    def _get_edge_label(self, token: TokenInfo) -> str:
        """Get appropriate edge label for a token based on its role."""
        dep = token.dep
        pos = token.pos
        
        # Subject
        if dep in ['nsubj', 'nsubjpass']:
            return 'subj'
        # Object
        elif dep in ['dobj', 'iobj', 'pobj']:
            return 'obj'
        # Adverbial
        elif pos == 'ADV' or dep in ['advmod', 'advcl']:
            return 'adv'
        # Adjectival
        elif pos == 'ADJ' or dep == 'amod':
            return 'adj'
        # Prepositional
        elif pos == 'ADP' or dep == 'prep':
            return 'prep'
        # Determiner
        elif pos == 'DET' or dep == 'det':
            return 'det'
        # Auxiliary
        elif dep in ['aux', 'auxpass']:
            return 'aux'
        # Default
        else:
            return dep
    
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