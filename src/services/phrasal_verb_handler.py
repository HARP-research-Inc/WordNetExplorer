"""
Phrasal verb handler for identifying and grouping phrasal verbs.
"""

from typing import List, Set, Tuple, Dict
from src.services.token_analyzer import TokenInfo
from src.services.syntactic_tree import SyntacticNode


class PhrasalVerbHandler:
    """Handles identification and grouping of phrasal verbs."""
    
    def __init__(self):
        """Initialize the phrasal verb handler."""
        # Common phrasal verb particles
        self.particles = {
            'up', 'down', 'out', 'off', 'on', 'in', 'over', 'away', 
            'back', 'through', 'around', 'along', 'across', 'by'
        }
    
    def identify_phrasal_verbs(self, tokens: List[TokenInfo]) -> Dict[int, List[int]]:
        """
        Identify phrasal verbs in the token list.
        
        Returns:
            Dict mapping verb index to list of particle indices
        """
        phrasal_verbs = {}
        
        for i, token in enumerate(tokens):
            if token.pos == 'VERB':
                # Look for particles that depend on this verb
                particles = []
                
                # Check immediate following tokens for potential particles
                for j in range(i + 1, min(i + 3, len(tokens))):  # Check next 2 tokens
                    other_token = tokens[j]
                    
                    # Check if it's a particle tagged as prt
                    if (other_token.head == i and 
                        other_token.dep in ['prt', 'compound:prt']):
                        particles.append(j)
                    
                    # Check if it's a potential particle tagged as preposition
                    elif (other_token.head == i and
                          other_token.dep in ['prep', 'advmod'] and
                          other_token.lemma.lower() in self.particles):
                        # Additional check: is there an object directly after?
                        # For "ran over my friend", we want "ran over" as phrasal verb
                        # For "ran over the hill", we want "over the hill" as prep phrase
                        
                        # Look for a direct object of the verb
                        has_direct_obj = any(
                            t.head == i and t.dep in ['dobj', 'obj'] 
                            for t in tokens
                        )
                        
                        # If verb has a direct object, this is likely a particle
                        # E.g., "ran over my friend" -> "ran over" + "my friend"
                        if has_direct_obj:
                            particles.append(j)
                        # Otherwise check if the prep has noun dependents
                        else:
                            # Check if this preposition has a pobj
                            has_pobj = any(
                                t.head == j and t.dep == 'pobj'
                                for t in tokens
                            )
                            # If it has pobj and verb has no dobj, it's a prep phrase
                            if not has_pobj:
                                # No pobj, might be a particle
                                particles.append(j)
                
                if particles:
                    phrasal_verbs[i] = particles
        
        return phrasal_verbs
    
    def build_verb_phrase(self, verb_idx: int, particle_indices: List[int], 
                         tokens: List[TokenInfo], token_nodes: Dict[int, SyntacticNode],
                         node_id_generator) -> Tuple[SyntacticNode, Set[int]]:
        """Build a verb phrase node containing the verb and its particles."""
        indices_in_phrase = {verb_idx}
        indices_in_phrase.update(particle_indices)
        
        # Build phrase text
        all_indices = sorted(indices_in_phrase)
        phrase_parts = []
        
        # Reconstruct the phrase preserving word order
        for idx in range(min(all_indices), max(all_indices) + 1):
            if idx in indices_in_phrase:
                phrase_parts.append(tokens[idx].text)
        
        phrase_text = ' '.join(phrase_parts)
        
        # Create verb phrase node
        vp_node = SyntacticNode(
            node_id=node_id_generator(),
            node_type='phrase',
            text=phrase_text
        )
        
        # Add verb as head
        vp_node.add_child(token_nodes[verb_idx], 'verb_head')
        
        # Add particles
        for particle_idx in sorted(particle_indices):
            vp_node.add_child(token_nodes[particle_idx], 'particle')
        
        return vp_node, indices_in_phrase 