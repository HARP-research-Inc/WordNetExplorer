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
        
        # First pass - create basic token info
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
                synsets=synsets,
                best_synset=None  # Will be filled in second pass
            )
            
            tokens.append(token_info)
            
            # Track root token
            if token.dep_ == "ROOT":
                root_index = i
        
        # Second pass - get best synsets with context
        for i, (token, token_info) in enumerate(zip(doc, tokens)):
            if token_info.synsets:
                best_synset = self._get_best_synset_for_token(token, doc)
                token_info.best_synset = best_synset
        
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
        # Create a mapping of token indices to nodes for easier access
        token_nodes = {}
        
        # First pass: Create all word nodes
        for idx in clause_indices:
            token = tokens[idx]
            word_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='word',
                text=token.text,
                token_info=token
            )
            token_nodes[idx] = word_node
        
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
        
        if main_verb_idx is None:
            # No verb found - just attach all nodes to clause
            for idx in clause_indices:
                clause_node.add_child(token_nodes[idx], self._get_edge_label(tokens[idx]))
            return
        
        # Identify sentence-level adverbs first (like "gleefully")
        sentence_adverbs = []
        for idx in clause_indices:
            token = tokens[idx]
            if (token.pos == 'ADV' and 
                token.head == main_verb_idx and 
                token.dep in ['advmod'] and
                idx < main_verb_idx):  # Adverbs before the verb are often sentence-level
                sentence_adverbs.append(idx)
        
        # Build verb phrase structure
        processed = set(sentence_adverbs)  # Mark sentence adverbs as processed
        verb_phrase_node, vp_indices = self._build_verb_phrase(main_verb_idx, tokens, token_nodes, clause_indices, exclude_indices=processed)
        processed.update(vp_indices)
        
        # Attach sentence-level adverbs to clause
        for adv_idx in sentence_adverbs:
            clause_node.add_child(token_nodes[adv_idx], 'adv')
        
        # Attach the verb phrase
        clause_node.add_child(verb_phrase_node, 'predicate')
        
        # Process remaining unprocessed tokens
        for idx in clause_indices:
            if idx in processed:
                continue
            
            token = tokens[idx]
            
            # Subjects attach to clause level
            if token.dep in ['nsubj', 'nsubjpass']:
                clause_node.add_child(token_nodes[idx], 'subj')
                processed.add(idx)
            # Punctuation
            elif token.pos == 'PUNCT':
                clause_node.add_child(token_nodes[idx], 'punct')
                processed.add(idx)
            # Other tokens
            elif idx not in processed:
                edge_label = self._get_edge_label(token)
                clause_node.add_child(token_nodes[idx], edge_label)
                processed.add(idx)
    
    def _build_verb_phrase(self, verb_idx: int, tokens: List[TokenInfo], 
                          token_nodes: Dict[int, SyntacticNode], 
                          clause_indices: List[int], exclude_indices: Set[int] = None) -> Tuple[SyntacticNode, Set[int]]:
        """Build a verb phrase including the verb and its complements."""
        if exclude_indices is None:
            exclude_indices = set()
            
        verb_token = tokens[verb_idx]
        indices_in_phrase = {verb_idx}
        
        # Check for phrasal verb particles
        particle_idx = None
        for idx in clause_indices:
            if idx in exclude_indices:
                continue
            token = tokens[idx]
            # Check for particles and prepositions that might be part of phrasal verbs
            if token.head == verb_idx:
                # Direct particle marker
                if token.dep == 'prt':
                    particle_idx = idx
                    indices_in_phrase.add(idx)
                    break
                # Preposition immediately after verb that takes an object (phrasal verb pattern)
                elif (token.dep == 'prep' and 
                      token.lemma.lower() in ['over', 'up', 'down', 'out', 'off', 'on', 'in', 'away'] and
                      abs(token.head - idx) == 1):  # Adjacent to verb
                    # Check if this preposition has an object (making it a phrasal verb)
                    has_object = False
                    for check_idx in clause_indices:
                        if tokens[check_idx].head == idx and tokens[check_idx].dep == 'pobj':
                            has_object = True
                            break
                    if has_object:
                        particle_idx = idx
                        indices_in_phrase.add(idx)
                        break
        
        # Collect direct objects and complements
        objects = []
        complements = []
        
        for idx in clause_indices:
            if idx == verb_idx or idx == particle_idx or idx in exclude_indices:
                continue
            
            token = tokens[idx]
            # Direct/indirect objects of the verb
            if token.head == verb_idx and token.dep in ['dobj', 'iobj']:
                objects.append(idx)
            # Objects of the particle/preposition in phrasal verbs
            elif particle_idx and token.head == particle_idx and token.dep == 'pobj':
                objects.append(idx)
            # Other complements (but not subjects or top-level adverbs)
            elif token.head == verb_idx and token.dep not in ['nsubj', 'nsubjpass']:
                complements.append(idx)
        
        # Build the verb phrase
        if particle_idx and objects:
            # Phrasal verb with object: "ran over my friend"
            # Include objects in the phrase
            for obj_idx in objects:
                if tokens[obj_idx].pos == 'NOUN':
                    obj_node, obj_indices = self._build_noun_phrase(obj_idx, tokens, token_nodes, clause_indices)
                    indices_in_phrase.update(obj_indices)
                else:
                    indices_in_phrase.add(obj_idx)
            
            # Build phrase text
            all_indices = sorted(indices_in_phrase)
            phrase_text = ' '.join([tokens[i].text for i in all_indices])
            
            vp_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='phrase',
                text=phrase_text
            )
            
            # Add verb
            vp_node.add_child(token_nodes[verb_idx], 'verb')
            
            # Create particle phrase for "over my friend"
            if objects:
                # Build "over my friend" as a unit
                particle_phrase_indices = {particle_idx}
                
                for obj_idx in objects:
                    if tokens[obj_idx].pos == 'NOUN':
                        obj_node, obj_indices = self._build_noun_phrase(obj_idx, tokens, token_nodes, clause_indices)
                        particle_phrase_indices.update(obj_indices)
                    else:
                        particle_phrase_indices.add(obj_idx)
                
                # Build text for particle phrase
                particle_phrase_indices_sorted = sorted(particle_phrase_indices)
                particle_phrase_text = ' '.join([tokens[i].text for i in particle_phrase_indices_sorted])
                
                particle_phrase_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='phrase',
                    text=particle_phrase_text
                )
                
                # Add particle
                particle_phrase_node.add_child(token_nodes[particle_idx], 'particle')
                
                # Add objects to particle phrase
                for obj_idx in objects:
                    if tokens[obj_idx].pos == 'NOUN':
                        obj_node, _ = self._build_noun_phrase(obj_idx, tokens, token_nodes, clause_indices)
                        particle_phrase_node.add_child(obj_node, 'obj')
                    else:
                        particle_phrase_node.add_child(token_nodes[obj_idx], 'obj')
                
                vp_node.add_child(particle_phrase_node, 'particle_phrase')
            
            # Add other complements (like "with my scooter")
            for comp_idx in complements:
                if comp_idx not in indices_in_phrase:
                    # Handle prepositional phrases
                    if tokens[comp_idx].pos == 'ADP':
                        pp_node, pp_indices = self._build_prep_phrase(comp_idx, tokens, token_nodes, clause_indices)
                        indices_in_phrase.update(pp_indices)
                        vp_node.add_child(pp_node, 'prep_phrase')
                    else:
                        indices_in_phrase.add(comp_idx)
                        edge_label = self._get_edge_label(tokens[comp_idx])
                        vp_node.add_child(token_nodes[comp_idx], edge_label)
            
            return vp_node, indices_in_phrase
        
        else:
            # Regular verb phrase - just return the verb
            return token_nodes[verb_idx], indices_in_phrase
    
    def _build_noun_phrase(self, noun_idx: int, tokens: List[TokenInfo], 
                          token_nodes: Dict[int, SyntacticNode], 
                          clause_indices: List[int]) -> Tuple[SyntacticNode, Set[int]]:
        """Build a noun phrase with the noun and its modifiers."""
        noun_token = tokens[noun_idx]
        indices_in_phrase = {noun_idx}
        
        # Collect modifiers of this noun
        modifiers = []
        possessives = []
        
        # Look for adjectives, determiners, etc. that modify this noun
        for idx in clause_indices:
            if idx == noun_idx:
                continue
            
            token = tokens[idx]
            # Check if this token modifies our noun
            if token.head == noun_idx:
                if token.dep == 'poss':
                    possessives.append((idx, token))
                    indices_in_phrase.add(idx)
                elif token.dep in ['amod', 'det', 'nummod', 'compound']:
                    modifiers.append((idx, token))
                    indices_in_phrase.add(idx)
        
        # If no modifiers and no possessives, just return the noun node
        if not modifiers and not possessives:
            return token_nodes[noun_idx], indices_in_phrase
        
        # Build the structure
        # If we have possessives, create "my fat friend" structure
        if possessives:
            # Build full phrase text
            all_indices = sorted(indices_in_phrase)
            full_phrase_text = ' '.join([tokens[i].text for i in all_indices])
            
            # Create top-level phrase node
            top_phrase_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='phrase',
                text=full_phrase_text
            )
            
            # Add possessives
            for poss_idx, poss_token in possessives:
                top_phrase_node.add_child(token_nodes[poss_idx], 'poss')
            
            # If we have adjectives, create intermediate "fat friend" node
            if any(mod[1].dep == 'amod' for mod in modifiers):
                # Build text without possessives
                non_poss_indices = [i for i in indices_in_phrase if i not in [p[0] for p in possessives]]
                adj_noun_text = ' '.join([tokens[i].text for i in sorted(non_poss_indices)])
                
                adj_noun_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='phrase',
                    text=adj_noun_text
                )
                
                # Add adjectives to intermediate node
                for mod_idx, mod_token in modifiers:
                    if mod_token.dep == 'amod':
                        adj_noun_node.add_child(token_nodes[mod_idx], 'adj')
                
                # Add noun to intermediate node
                adj_noun_node.add_child(token_nodes[noun_idx], 'head')
                
                # Add other modifiers (det, compound) to intermediate node
                for mod_idx, mod_token in modifiers:
                    if mod_token.dep != 'amod':
                        edge_label = {
                            'det': 'det',
                            'nummod': 'num',
                            'compound': 'compound'
                        }.get(mod_token.dep, mod_token.dep)
                        adj_noun_node.add_child(token_nodes[mod_idx], edge_label)
                
                # Add intermediate node to top node
                top_phrase_node.add_child(adj_noun_node, 'np')
            else:
                # No adjectives, just add noun directly
                top_phrase_node.add_child(token_nodes[noun_idx], 'head')
                
                # Add other modifiers
                for mod_idx, mod_token in modifiers:
                    edge_label = {
                        'det': 'det',
                        'nummod': 'num',
                        'compound': 'compound'
                    }.get(mod_token.dep, mod_token.dep)
                    top_phrase_node.add_child(token_nodes[mod_idx], edge_label)
            
            return top_phrase_node, indices_in_phrase
        
        else:
            # No possessives, build regular noun phrase
            # Build phrase text
            all_indices = sorted(indices_in_phrase)
            phrase_text = ' '.join([tokens[i].text for i in all_indices])
            
            np_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='phrase',
                text=phrase_text
            )
            
            # Add noun as head
            np_node.add_child(token_nodes[noun_idx], 'head')
            
            # Add modifiers in order
            for mod_idx, mod_token in sorted(modifiers):
                edge_label = {
                    'amod': 'adj',
                    'det': 'det',
                    'nummod': 'num',
                    'compound': 'compound'
                }.get(mod_token.dep, mod_token.dep)
                
                np_node.add_child(token_nodes[mod_idx], edge_label)
            
            return np_node, indices_in_phrase
    
    def _build_prep_phrase(self, prep_idx: int, tokens: List[TokenInfo], 
                          token_nodes: Dict[int, SyntacticNode], 
                          clause_indices: List[int]) -> Tuple[SyntacticNode, Set[int]]:
        """Build a prepositional phrase."""
        prep_token = tokens[prep_idx]
        indices_in_phrase = {prep_idx}
        
        # Find the object of the preposition
        pobj_idx = None
        for idx in clause_indices:
            token = tokens[idx]
            if token.head == prep_idx and token.dep == 'pobj':
                pobj_idx = idx
                break
        
        # Create prepositional phrase node
        if pobj_idx is not None:
            # Include the whole noun phrase if the object is a noun
            if tokens[pobj_idx].pos == 'NOUN':
                obj_node, obj_indices = self._build_noun_phrase(pobj_idx, tokens, token_nodes, clause_indices)
                indices_in_phrase.update(obj_indices)
            else:
                obj_node = token_nodes[pobj_idx]
                indices_in_phrase.add(pobj_idx)
            
            # Build phrase text
            all_indices = sorted(indices_in_phrase)
            phrase_text = ' '.join([tokens[i].text for i in all_indices])
            
            pp_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='phrase',
                text=phrase_text
            )
            
            # Add preposition and object
            pp_node.add_child(token_nodes[prep_idx], 'prep')
            pp_node.add_child(obj_node, 'pobj')
            
            return pp_node, indices_in_phrase
        else:
            # Just return the preposition if no object found
            return token_nodes[prep_idx], indices_in_phrase
    
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
        # Skip synsets for certain POS tags that WordNet doesn't handle
        skip_pos = {'PRON', 'DET', 'CCONJ', 'SCONJ', 'PART', 'PUNCT', 'SYM', 'X'}
        if token.pos_ in skip_pos:
            return []
        
        # Map spaCy POS to WordNet POS
        wn_pos = self._pos_map.get(token.pos_)
        
        # Special handling for ADP (adpositions) that might be adverbs in WordNet
        if token.pos_ == 'ADP' and token.lemma_.lower() in ['over', 'up', 'down', 'out', 'off', 'on', 'in', 'away', 'around', 'through']:
            # Try to get adverb synsets first
            adv_synsets = wn.synsets(token.lemma_, pos='r')
            if adv_synsets:
                return [s.name() for s in adv_synsets[:5]]
        
        # Try to get synsets - WordNet handles nouns, verbs, adjectives, and adverbs
        if wn_pos:
            # Get synsets with specific POS
            synsets = wn.synsets(token.lemma_, pos=wn_pos)
        else:
            # For other POS (like ADP/prepositions), still try to find synsets
            # Some words like "over" can be adverbs in WordNet even if tagged as ADP
            synsets = wn.synsets(token.lemma_)
            
            # If we found synsets, filter to only those that match WordNet POS categories
            if synsets:
                valid_synsets = []
                for s in synsets:
                    if s.pos() in ['n', 'v', 'a', 's', 'r']:  # WordNet POS categories
                        valid_synsets.append(s)
                synsets = valid_synsets
        
        # Special handling: skip certain words only if they have no synsets
        # and are being used as function words
        if not synsets and token.dep_ in ['aux', 'auxpass', 'det', 'case', 'mark']:
            return []
        
        # For potential phrasal verb particles, don't exclude them entirely
        # Let the disambiguation logic handle them
        
        # Return synset names
        return [s.name() for s in synsets[:5]]  # Limit to top 5
    
    def _get_best_synset_for_token(self, token, context_tokens) -> Optional[Tuple[str, str]]:
        """Get the best synset for a token considering context."""
        synsets = self._get_synsets_for_token(token)
        if not synsets:
            return None
        
        # For now, use simple heuristics
        # In the future, this could use the sense similarity calculator
        
        # Special handling for words that can be phrasal verb particles
        if token.lemma_.lower() in ['over', 'up', 'down', 'out', 'off', 'on', 'in', 'away']:
            # Check the dependency relation
            if token.dep_ in ['prt', 'compound:prt']:
                # It's a phrasal verb particle - prefer aspectual/completive meanings
                for synset_name in synsets:
                    try:
                        synset = wn.synset(synset_name)
                        definition = synset.definition().lower()
                        # For particles, prefer aspectual/completive meanings
                        if any(word in definition for word in ['thoroughly', 'completely', 'finished']):
                            return (synset_name, synset.definition())
                    except:
                        continue
            else:
                # It's a preposition/adverb - prefer spatial meanings
                for synset_name in synsets:
                    try:
                        synset = wn.synset(synset_name)
                        definition = synset.definition().lower()
                        # Prefer spatial/directional meanings
                        if any(word in definition for word in ['across', 'above', 'beyond', 
                                                               'position', 'location', 'space']):
                            return (synset_name, synset.definition())
                    except:
                        continue
        
        # For other words, prefer more common senses (they come first)
        # but filter out highly technical/specific senses for common words
        for synset_name in synsets:
            try:
                synset = wn.synset(synset_name)
                definition = synset.definition().lower()
                
                # Skip overly technical definitions for common words
                if token.lemma_.lower() in ['run', 'friend', 'time', 'bank']:
                    technical_terms = ['cricket', 'chemistry', 'physics', 'mathematics', 
                                     'biology', 'medicine', 'chemical', 'baseball']
                    if any(term in definition for term in technical_terms):
                        continue
                
                return (synset_name, synset.definition())
            except:
                continue
        
        # Fallback to first synset if no better option found
        if synsets:
            try:
                synset = wn.synset(synsets[0])
                return (synsets[0], synset.definition())
            except:
                pass
        
        return None
    
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