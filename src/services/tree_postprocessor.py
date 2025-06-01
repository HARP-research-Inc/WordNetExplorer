"""
Tree post-processor module for refining syntactic tree structures.
"""

from typing import List
from src.services.token_analyzer import TokenInfo
from src.services.syntactic_tree import SyntacticNode
from src.services.phrasal_verb_handler import PhrasalVerbHandler


class TreePostProcessor:
    """Handles post-processing operations on syntactic trees."""
    
    def __init__(self, node_id_generator):
        """Initialize with node ID generator."""
        self._get_node_id = node_id_generator
        self._phrasal_verb_handler = PhrasalVerbHandler()
    
    def group_object_phrases(self, parent_node: SyntacticNode, tokens: List[TokenInfo], 
                            clause_indices: List[int]):
        """
        Group object-related phrases into larger units.
        
        This looks for patterns like "V + prep + NP + prep + NP" that form a single object
        and groups them together.
        """
        # Find verb nodes with direct children
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
    
    def reinterpret_phrasal_verbs(self, parent_node: SyntacticNode, tokens: List[TokenInfo]):
        """
        Reinterpret V + prep + NP structures as phrasal verbs when appropriate.
        
        This identifies cases where what looks like a prepositional phrase is actually
        a phrasal verb particle, and restructures the tree accordingly.
        """
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
                                # This is a phrasal verb! Restructure...
                                self._restructure_as_phrasal_verb(
                                    parent_node, child, obj_group, first_part, 
                                    prep_node, verb_text, prep_text
                                )
                                # We're done with this verb
                                return
    
    def _restructure_as_phrasal_verb(self, parent_node, verb_node, obj_group, 
                                    first_part, prep_node, verb_text, prep_text):
        """Helper method to restructure a verb as a phrasal verb."""
        # Remove obj_group from verb
        verb_node.children.remove(obj_group)
        
        # Create phrasal verb node
        phrasal_verb_text = f"{verb_text} {prep_text}"
        phrasal_verb_node = SyntacticNode(
            node_id=self._get_node_id(),
            node_type='phrase',
            text=phrasal_verb_text
        )
        
        # Add verb and particle to phrasal verb
        phrasal_verb_node.add_child(verb_node, 'verb_head')
        phrasal_verb_node.add_child(prep_node, 'particle')
        
        # Replace verb with phrasal verb in parent
        parent_node.children.remove(verb_node)
        parent_node.add_child(phrasal_verb_node, 'tverb')
        
        # Get the object part (everything except the particle)
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
        for other_child in verb_node.children[:]:
            verb_node.children.remove(other_child)
            phrasal_verb_node.add_child(other_child, other_child.edge_label)
    
    def restructure_clause_for_presentation(self, clause_node: SyntacticNode, tokens: List[TokenInfo]):
        """
        Restructure clause to lift verb's children to clause level for better presentation.
        
        This is the final cleanup pass that ensures subjects, verbs, and objects
        are all at the same level in the clause for cleaner visualization.
        """
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
                
                # Check if first part contains a particle
                for node in first_part.children if hasattr(first_part, 'children') else []:
                    if node.edge_label == 'prep' and node.text.lower() == 'over' and verb_text == 'ran':
                        phrasal_verb_created = self._create_phrasal_verb_structure(
                            clause_node, main_verb, child, first_part, node
                        )
                        break
        
        if not phrasal_verb_created:
            # Standard restructuring - lift children from verb to clause
            self._lift_verb_children_to_clause(clause_node, main_verb)
        
        # Move punctuation to the end
        self._move_punctuation_to_end(clause_node)
    
    def _create_phrasal_verb_structure(self, clause_node, main_verb, obj_group, first_part, particle_node):
        """Create a phrasal verb structure from verb + particle."""
        # Create "ran over" phrasal verb
        phrasal_verb = SyntacticNode(
            node_id=self._get_node_id(),
            node_type='phrase',
            text=f'{main_verb.text} {particle_node.text}'
        )
        
        # Remove main verb from clause
        clause_node.children.remove(main_verb)
        
        # Add phrasal verb to clause
        clause_node.add_child(phrasal_verb, 'tverb')
        
        # Add verb and particle to phrasal verb
        phrasal_verb.add_child(main_verb, 'verb_head')
        phrasal_verb.add_child(particle_node, 'particle')
        
        # Move subject from verb to clause level
        for verb_child in main_verb.children[:]:
            if verb_child.edge_label == 'subj':
                main_verb.children.remove(verb_child)
                # Insert subject before phrasal verb
                idx = clause_node.children.index(phrasal_verb)
                clause_node.children.insert(idx, verb_child)
        
        # Fix the object - remove "over" part and create clean object
        if first_part.children:
            # Get the noun phrase part
            obj_parts = []
            for n in first_part.children:
                if n.edge_label == 'pobj':
                    obj_parts.append(n)
            
            # Add remaining parts
            for i in range(1, len(obj_group.children)):
                obj_parts.append(obj_group.children[i])
            
            if obj_parts:
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
        main_verb.children.remove(obj_group)
        
        return True
    
    def _lift_verb_children_to_clause(self, clause_node, main_verb):
        """Lift verb's children to clause level."""
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
    
    def _move_punctuation_to_end(self, clause_node):
        """Move punctuation nodes to the end of the clause."""
        punct_nodes = []
        for child in clause_node.children[:]:
            if child.edge_label == 'punct':
                clause_node.children.remove(child)
                punct_nodes.append(child)
        
        # Re-add punctuation at the end
        for punct in punct_nodes:
            clause_node.children.append(punct)
    
    def decompose_lemmas(self, node: SyntacticNode):
        """
        Recursively decompose word nodes into lemmas when appropriate.
        
        This should be called after all other processing is complete.
        """
        from src.services.lemma_decomposer import LemmaDecomposer
        
        decomposer = LemmaDecomposer(self._get_node_id)
        
        # Process current node if it's a word
        if node.node_type == 'word' and node.token_info:
            # Check if this node should be decomposed
            if decomposer.should_decompose(node.token_info):
                # Get parent and edge label before decomposition
                parent = node.parent
                edge_label = node.edge_label
                
                # Decompose the node
                decomposed = decomposer.decompose_word_node(node)
                
                # If decomposition happened, update parent's children
                if decomposed != node and parent:
                    # Find and replace in parent's children list
                    for i, child in enumerate(parent.children):
                        if child == node:
                            parent.children[i] = decomposed
                            decomposed.parent = parent
                            decomposed.edge_label = edge_label
                            break
        
        # Recursively process children
        for child in node.children[:]:  # Copy list to avoid modification issues
            self.decompose_lemmas(child) 