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
        
        # Known phrasal verbs where the particle might be parsed as prep
        # Format: (verb_lemma, particle) -> is_phrasal_verb
        self.known_phrasal_verbs = {
            ('run', 'over'): True,  # run over = hit with vehicle
            ('look', 'up'): True,   # look up = search for
            ('look', 'after'): True, # look after = take care of
            ('get', 'over'): True,  # get over = recover from
            ('take', 'over'): True, # take over = assume control
            ('come', 'across'): True, # come across = find/encounter
            ('put', 'off'): True,   # put off = postpone
            ('turn', 'down'): True, # turn down = reject
            ('give', 'up'): True,   # give up = quit
            ('pick', 'up'): True,   # pick up = collect
            ('take', 'off'): True,  # take off = remove/depart
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
                        
                        # Check if this is a known phrasal verb combination
                        verb_lemma = token.lemma.lower()
                        particle_lemma = other_token.lemma.lower()
                        
                        if (verb_lemma, particle_lemma) in self.known_phrasal_verbs:
                            # This is a known phrasal verb
                            particles.append(j)
                        else:
                            # Additional check: is there an object directly after?
                            # For "ran over my friend", we want "ran over" as phrasal verb
                            # For "ran over the hill", we want "over the hill" as prep phrase
                            
                            # Look for a direct object of the verb
                            has_direct_obj = any(
                                t.head == i and t.dep in ['dobj', 'obj'] 
                                for t in tokens
                            )
                            
                            # If verb has a direct object, this is likely a particle
                            # E.g., "looked up the word" -> "looked up" + "the word"
                            if has_direct_obj:
                                particles.append(j)
                            else:
                                # Check if this preposition has a pobj
                                has_pobj = any(
                                    t.head == j and t.dep == 'pobj'
                                    for t in tokens
                                )
                                
                                # For some verbs, even with pobj, it might be phrasal
                                # Check semantic clues
                                if has_pobj and j + 1 < len(tokens):
                                    # If the "object" is animate/person, likely phrasal
                                    # e.g. "ran over my friend" vs "ran over the bridge"
                                    next_noun_idx = None
                                    for k in range(j + 1, len(tokens)):
                                        if tokens[k].pos == 'NOUN' and tokens[k].head == j:
                                            next_noun_idx = k
                                            break
                                    
                                    # Simple heuristic: if followed by possessive pronoun,
                                    # more likely to be phrasal verb
                                    if (j + 1 < len(tokens) and 
                                        tokens[j + 1].pos == 'PRON' and 
                                        tokens[j + 1].dep == 'poss'):
                                        particles.append(j)
                                
                                elif not has_pobj:
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