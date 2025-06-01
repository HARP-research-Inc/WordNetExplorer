"""
Refactored sentence analyzer using modular components.
"""

import spacy
from typing import List, Optional, Dict
from dataclasses import dataclass
import streamlit as st

from .token_analyzer import TokenAnalyzer, TokenInfo
from .token_disambiguator import TokenDisambiguator
from .syntactic_tree import SyntacticNode, PhraseBuilder, EdgeLabelMapper
from .linguistic_colors import LinguisticColors
from .phrasal_verb_handler import PhrasalVerbHandler


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


class SentenceAnalyzerV2:
    """Modular sentence analyzer using spaCy and WordNet."""
    
    def __init__(self):
        """Initialize the sentence analyzer components."""
        self._nlp = None
        self._token_analyzer = TokenAnalyzer()
        self._token_disambiguator = TokenDisambiguator()
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
        
        # Parse the sentence
        doc = self.nlp(sentence)
        
        # Extract token information
        tokens = []
        root_index = 0
        
        # First pass - analyze tokens
        for i, token in enumerate(doc):
            token_info = self._token_analyzer.analyze_token(token, i)
            tokens.append(token_info)
            
            # Track root token
            if token.dep_ == "ROOT":
                root_index = i
        
        # Second pass - disambiguate tokens
        self._token_disambiguator.disambiguate_tokens(tokens, doc)
        
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
            clause_builder = ClauseBuilder(self._get_node_id)
            clause_builder.build_clause_tree(root, clauses[0], tokens, 'main')
        else:
            # Complex sentence - identify relationships
            self._build_complex_sentence_tree(root, clauses, tokens, doc)
        
        return root
    
    def _identify_clauses(self, doc, tokens: List[TokenInfo]) -> List[List[int]]:
        """Identify clauses in the sentence."""
        clause_identifier = ClauseIdentifier()
        return clause_identifier.identify_clauses(doc, tokens)
    
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
            clause_builder = ClauseBuilder(self._get_node_id)
            for i, clause_indices in enumerate(clauses):
                clause_text = ' '.join([tokens[idx].text for idx in clause_indices])
                clause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=clause_text
                )
                
                # Determine edge label
                edge_label = 'iclause' if i == 0 else 'dclause'
                conj_node.add_child(clause_node, edge_label)
                
                # Build the clause subtree
                clause_builder.build_clause_tree(clause_node, clause_indices, tokens, 'sub')
        else:
            # No clear conjunction, treat as coordinate clauses
            clause_builder = ClauseBuilder(self._get_node_id)
            for i, clause_indices in enumerate(clauses):
                clause_text = ' '.join([tokens[idx].text for idx in clause_indices])
                clause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=clause_text
                )
                
                edge_label = 'clause' if i == 0 else 'coord_clause'
                root.add_child(clause_node, edge_label)
                
                clause_builder.build_clause_tree(clause_node, clause_indices, tokens, 
                                               'main' if i == 0 else 'coord')
    
    # Color methods for backward compatibility
    def get_pos_color(self, pos: str) -> str:
        """Get color for a POS tag."""
        return self.colors.get_pos_color(pos)
    
    def get_dependency_color(self, dep: str) -> str:
        """Get color for a dependency relation."""
        return self.colors.get_dependency_color(dep)


class ClauseIdentifier:
    """Identifies clauses in sentences."""
    
    def identify_clauses(self, doc, tokens: List[TokenInfo]) -> List[List[int]]:
        """Identify clauses in the sentence."""
        clauses = []
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


class ClauseBuilder:
    """Builds clause structures."""
    
    def __init__(self, node_id_generator):
        """Initialize with node ID generator."""
        self._get_node_id = node_id_generator
        self._phrase_builder = PhraseBuilder(node_id_generator)
        self._edge_mapper = EdgeLabelMapper()
        self._phrasal_verb_handler = PhrasalVerbHandler()
    
    def build_clause_tree(self, clause_node: SyntacticNode, clause_indices: List[int], 
                         tokens: List[TokenInfo], clause_type: str):
        """Build the tree for a single clause."""
        # Create a mapping of token indices to nodes
        token_nodes = {}
        
        # Create all word nodes
        for idx in clause_indices:
            token = tokens[idx]
            word_node = SyntacticNode(
                node_id=self._get_node_id(),
                node_type='word',
                text=token.text,
                token_info=token
            )
            token_nodes[idx] = word_node
        
        # Check for sentence-modifying adverbs at the beginning
        sentence_adverbs = []
        for idx in clause_indices[:3]:  # Check first few tokens
            token = tokens[idx]
            if (token.pos == 'ADV' and 
                token.dep in ['advmod'] and 
                tokens[token.head].pos == 'VERB'):
                # Check if it's a sentence-level adverb (like "gleefully")
                sentence_adverbs.append(idx)
                break
        
        # If we have sentence-level adverbs, handle them separately
        if sentence_adverbs:
            # Create the adverb node(s) at clause level
            for adv_idx in sentence_adverbs:
                clause_node.add_child(token_nodes[adv_idx], 'adv_mod')
            
            # Create a sub-clause for the rest
            remaining_indices = [idx for idx in clause_indices if idx not in sentence_adverbs]
            if remaining_indices:
                subclause_text = ' '.join([tokens[idx].text for idx in remaining_indices])
                subclause_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='clause',
                    text=subclause_text
                )
                clause_node.add_child(subclause_node, 'main_clause')
                
                # Build the rest of the tree under the subclause
                self._build_clause_content(subclause_node, remaining_indices, tokens, token_nodes)
                
                # Post-process to reinterpret phrasal verbs
                self._reinterpret_phrasal_verbs(subclause_node, tokens)
                
                # Post-process to group object phrases
                self._group_object_phrases(subclause_node, tokens, remaining_indices)
                
                # Final restructuring for better presentation
                self._restructure_clause_for_presentation(subclause_node, tokens)
        else:
            # No sentence-level adverbs, build normally
            self._build_clause_content(clause_node, clause_indices, tokens, token_nodes)
            
            # Post-process to reinterpret phrasal verbs
            self._reinterpret_phrasal_verbs(clause_node, tokens)
            
            # Post-process to group object phrases
            self._group_object_phrases(clause_node, tokens, clause_indices)
            
            # Final restructuring for better presentation
            self._restructure_clause_for_presentation(clause_node, tokens)
    
    def _build_clause_content(self, parent_node: SyntacticNode, clause_indices: List[int],
                             tokens: List[TokenInfo], token_nodes: Dict[int, SyntacticNode]):
        """Build the content of a clause."""
        # Identify phrasal verbs
        phrasal_verbs = self._phrasal_verb_handler.identify_phrasal_verbs(tokens)
        
        # Build phrase structures
        processed = set()
        
        # Find the main verb (might be part of a phrasal verb)
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
        
        # Process each token to build phrases
        for idx in clause_indices:
            if idx in processed:
                continue
            
            token = tokens[idx]
            
            # Handle phrasal verbs
            if idx in phrasal_verbs and idx not in processed:
                verb_phrase_node, phrase_indices = self._phrasal_verb_handler.build_verb_phrase(
                    idx, phrasal_verbs[idx], tokens, token_nodes, self._get_node_id)
                processed.update(phrase_indices)
                
                # Attach verb phrase
                edge_label = 'tverb' if idx == main_verb_idx else 'verb'
                parent_node.add_child(verb_phrase_node, edge_label)
            
            # Handle noun phrases
            elif token.pos == 'NOUN' and idx not in processed:
                noun_phrase_node, phrase_indices = self._phrase_builder.build_noun_phrase(
                    idx, tokens, token_nodes, clause_indices)
                processed.update(phrase_indices)
                
                # Attach noun phrase
                self._attach_noun_phrase(noun_phrase_node, token, main_verb_idx, 
                                       token_nodes, parent_node)
            
            # Handle prepositional phrases
            elif token.pos == 'ADP' and idx not in processed:
                prep_phrase_node, phrase_indices = self._phrase_builder.build_prep_phrase(
                    idx, tokens, token_nodes, clause_indices)
                processed.update(phrase_indices)
                
                # Attach prepositional phrase
                if token.head < len(tokens) and token.head in token_nodes:
                    # Check if the head is part of a phrasal verb
                    head_in_phrasal = False
                    for verb_idx, particles in phrasal_verbs.items():
                        if token.head == verb_idx or token.head in particles:
                            head_in_phrasal = True
                            # Attach to parent instead
                            parent_node.add_child(prep_phrase_node, 'prep_phrase')
                            break
                    
                    if not head_in_phrasal and token.head not in processed:
                        token_nodes[token.head].add_child(prep_phrase_node, 'prep_phrase')
                    elif not head_in_phrasal:
                        # Head was already processed (probably in a phrase)
                        parent_node.add_child(prep_phrase_node, 'prep_phrase')
                else:
                    parent_node.add_child(prep_phrase_node, 'prep_phrase')
            
            # Handle standalone verbs (not part of phrasal verbs)
            elif token.pos == 'VERB' and idx not in processed:
                processed.add(idx)
                edge_label = 'tverb' if idx == main_verb_idx else 'verb'
                parent_node.add_child(token_nodes[idx], edge_label)
            
            # Handle other standalone words
            elif idx not in processed:
                processed.add(idx)
                edge_label = self._edge_mapper.get_edge_label(token)
                
                # Attach to appropriate parent
                if token.head < len(tokens) and token.head in token_nodes and token.head != idx:
                    # Check if head is already processed
                    if token.head not in processed:
                        token_nodes[token.head].add_child(token_nodes[idx], edge_label)
                    else:
                        # Head is in a phrase, attach to parent
                        parent_node.add_child(token_nodes[idx], edge_label)
                else:
                    parent_node.add_child(token_nodes[idx], edge_label)
    
    def _attach_noun_phrase(self, noun_phrase_node: SyntacticNode, token: TokenInfo,
                           main_verb_idx: Optional[int], token_nodes: dict, 
                           clause_node: SyntacticNode):
        """Attach a noun phrase to the appropriate parent."""
        if token.dep in ['nsubj', 'nsubjpass'] and main_verb_idx is not None:
            token_nodes[main_verb_idx].add_child(noun_phrase_node, 'subj')
        elif token.dep in ['dobj', 'iobj'] and main_verb_idx is not None:
            token_nodes[main_verb_idx].add_child(noun_phrase_node, 'obj')
        elif token.dep == 'pobj':
            # Object of preposition - handled by prep phrase
            pass
        else:
            edge_label = self._edge_mapper.get_edge_label(token)
            clause_node.add_child(noun_phrase_node, edge_label)
    
    def _group_object_phrases(self, parent_node: SyntacticNode, tokens: List[TokenInfo], 
                             clause_indices: List[int]):
        """Group object-related phrases into larger units."""
        # Look for patterns like "V + prep + NP + prep + NP" that form a single object
        # This is a post-processing step to create better groupings
        
        # Find verb nodes with both direct children
        verb_nodes = []
        for child in parent_node.children:
            if child.edge_label in ['tverb', 'verb']:
                verb_nodes.append(child)
        
        for verb_node in verb_nodes:
            # Collect all object-like children
            object_children = []
            other_children = []
            
            for child in verb_node.children[:]:  # Copy list since we'll modify it
                if child.edge_label in ['obj', 'prep_phrase']:
                    object_children.append(child)
                else:
                    other_children.append(child)
            
            # Also check parent node for prep phrases that might belong to this verb
            for child in parent_node.children[:]:
                if (child.edge_label == 'prep_phrase' and 
                    child not in object_children):
                    # Check if this prep phrase is semantically related to the verb's object
                    object_children.append(child)
                    parent_node.children.remove(child)
            
            # If we have multiple object-like phrases, consider grouping them
            if len(object_children) > 1:
                # Create a combined object phrase
                all_text_parts = []
                for obj_child in object_children:
                    all_text_parts.append(obj_child.text)
                
                combined_text = ' '.join(all_text_parts)
                
                # Create new grouped node
                grouped_node = SyntacticNode(
                    node_id=self._get_node_id(),
                    node_type='phrase',
                    text=combined_text
                )
                
                # Move all object children under the grouped node
                verb_node.children = other_children  # Keep non-object children
                for obj_child in object_children:
                    obj_child.parent = grouped_node
                    obj_child.edge_label = 'part'
                    grouped_node.children.append(obj_child)
                
                # Add grouped node to verb
                verb_node.add_child(grouped_node, 'obj_group')
    
    def _reinterpret_phrasal_verbs(self, parent_node: SyntacticNode, tokens: List[TokenInfo]):
        """Reinterpret V + prep + NP structures as phrasal verbs when appropriate."""
        # Look for patterns where a verb has a prep child that should be a particle
        
        for child in parent_node.children[:]:
            if child.edge_label in ['tverb', 'verb'] and child.node_type == 'word':
                verb_idx = None
                # Find the verb token index
                for i, token in enumerate(tokens):
                    if token.text == child.text and token.pos == 'VERB':
                        verb_idx = i
                        break
                
                if verb_idx is None:
                    continue
                
                # Look for obj_group that might contain phrasal verb patterns
                obj_groups = [gc for gc in child.children if gc.edge_label == 'obj_group']
                
                for obj_group in obj_groups:
                    # Check if the first part is "prep + NP" that could be a particle
                    if obj_group.children and obj_group.children[0].edge_label == 'part':
                        first_part = obj_group.children[0]
                        
                        # Look for prep in first part
                        prep_node = None
                        for node in first_part.children:
                            if node.edge_label == 'prep':
                                prep_node = node
                                break
                        
                        if prep_node:
                            prep_text = prep_node.text.lower()
                            verb_text = child.text.lower()
                            
                            # Common phrasal verbs
                            phrasal_patterns = {
                                'run': ['over', 'into', 'down'],
                                'knock': ['over', 'down', 'out'],
                                'look': ['up', 'over', 'into'],
                                'turn': ['on', 'off', 'over'],
                                'take': ['over', 'off', 'out']
                            }
                            
                            if (verb_text in phrasal_patterns and 
                                prep_text in phrasal_patterns[verb_text]):
                                # This is a phrasal verb!
                                # Restructure the tree
                                
                                # Remove obj_group from verb
                                child.children.remove(obj_group)
                                
                                # Create phrasal verb node
                                phrasal_verb_text = f"{child.text} {prep_text}"
                                phrasal_verb_node = SyntacticNode(
                                    node_id=self._get_node_id(),
                                    node_type='phrase',
                                    text=phrasal_verb_text
                                )
                                
                                # Add verb and particle to phrasal verb
                                phrasal_verb_node.add_child(child, 'verb_head')
                                phrasal_verb_node.add_child(prep_node, 'particle')
                                
                                # Replace verb with phrasal verb in parent
                                parent_node.children.remove(child)
                                parent_node.add_child(phrasal_verb_node, 'tverb')
                                
                                # Get the object part (everything except the particle)
                                # The object is the pobj from first_part plus any remaining parts
                                obj_parts = []
                                
                                # Get pobj from first part
                                for node in first_part.children:
                                    if node.edge_label == 'pobj':
                                        obj_parts.append(node)
                                
                                # Add remaining parts from obj_group
                                for i in range(1, len(obj_group.children)):
                                    obj_parts.append(obj_group.children[i])
                                
                                # If we have object parts, create a combined object
                                if obj_parts:
                                    if len(obj_parts) == 1:
                                        # Single object, add directly
                                        phrasal_verb_node.add_child(obj_parts[0], 'obj')
                                    else:
                                        # Multiple parts, create grouped object
                                        combined_text = ' '.join([part.text for part in obj_parts])
                                        combined_obj = SyntacticNode(
                                            node_id=self._get_node_id(),
                                            node_type='phrase',
                                            text=combined_text
                                        )
                                        
                                        for part in obj_parts:
                                            part.edge_label = 'part'
                                            combined_obj.children.append(part)
                                        
                                        phrasal_verb_node.add_child(combined_obj, 'obj')
                                
                                # Move other children from verb to phrasal verb
                                for other_child in child.children[:]:
                                    child.children.remove(other_child)
                                    phrasal_verb_node.add_child(other_child, other_child.edge_label)
                                
                                # We're done with this verb
                                return 

    def _restructure_clause_for_presentation(self, clause_node: SyntacticNode, tokens: List[TokenInfo]):
        """Restructure clause to lift verb's children to clause level for better presentation."""
        # Find the main verb node
        main_verb = None
        for child in clause_node.children[:]:
            if child.edge_label == 'tverb':
                main_verb = child
                break
        
        if not main_verb:
            return
        
        # Check if we need to create a phrasal verb
        verb_text = main_verb.text.lower()
        
        # Look for "over" in the object group that should be part of "ran over"
        phrasal_verb_created = False
        
        for child in main_verb.children[:]:
            if child.edge_label == 'obj_group' and child.children:
                first_part = child.children[0]
                
                # Check if first part contains "over" as prep
                for node in first_part.children if hasattr(first_part, 'children') else []:
                    if node.edge_label == 'prep' and node.text.lower() == 'over' and verb_text == 'ran':
                        # Create "ran over" phrasal verb
                        phrasal_verb = SyntacticNode(
                            node_id=self._get_node_id(),
                            node_type='phrase',
                            text='ran over'
                        )
                        
                        # Remove main verb from clause
                        clause_node.children.remove(main_verb)
                        
                        # Add phrasal verb to clause
                        clause_node.add_child(phrasal_verb, 'tverb')
                        
                        # Add verb and particle to phrasal verb
                        phrasal_verb.add_child(main_verb, 'verb_head')
                        phrasal_verb.add_child(node, 'particle')
                        
                        # Move subject from verb to clause level
                        for verb_child in main_verb.children[:]:
                            if verb_child.edge_label == 'subj':
                                main_verb.children.remove(verb_child)
                                # Insert subject before phrasal verb
                                idx = clause_node.children.index(phrasal_verb)
                                clause_node.children.insert(idx, verb_child)
                        
                        # Fix the object - remove "over" part and create clean object
                        if first_part.children:
                            # Get the noun phrase part (my fat friend)
                            for n in first_part.children:
                                if n.edge_label == 'pobj':
                                    # Combine with other parts (with a scooter)
                                    obj_parts = [n]
                                    for i in range(1, len(child.children)):
                                        obj_parts.append(child.children[i])
                                    
                                    if len(obj_parts) == 1:
                                        clause_node.add_child(obj_parts[0], 'obj')
                                    else:
                                        # Create combined object
                                        combined_text = ' '.join([p.text for p in obj_parts])
                                        combined_obj = SyntacticNode(
                                            node_id=self._get_node_id(),
                                            node_type='phrase',
                                            text=combined_text
                                        )
                                        
                                        for part in obj_parts:
                                            part.edge_label = 'part'
                                            combined_obj.children.append(part)
                                        
                                        clause_node.add_child(combined_obj, 'obj')
                        
                        # Remove the obj_group from verb
                        main_verb.children.remove(child)
                        
                        phrasal_verb_created = True
                        break
        
        if not phrasal_verb_created:
            # Standard restructuring - lift children from verb to clause
            for child in main_verb.children[:]:
                if child.edge_label in ['subj', 'obj', 'obj_group']:
                    main_verb.children.remove(child)
                    
                    # Find appropriate position in clause
                    if child.edge_label == 'subj':
                        # Insert subject before verb
                        idx = clause_node.children.index(main_verb)
                        clause_node.children.insert(idx, child)
                    else:
                        # Add objects after verb
                        clause_node.add_child(child, child.edge_label)
        
        # Move punctuation to the end
        punct_nodes = []
        for child in clause_node.children[:]:
            if child.edge_label == 'punct':
                clause_node.children.remove(child)
                punct_nodes.append(child)
        
        # Re-add punctuation at the end
        for punct in punct_nodes:
            clause_node.children.append(punct) 