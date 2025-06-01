"""
Token disambiguator module for selecting the best synset for tokens in context.
"""

from typing import Optional, Tuple, List
from nltk.corpus import wordnet as wn


class TokenDisambiguator:
    """Handles disambiguation of word senses based on context."""
    
    def __init__(self):
        """Initialize the disambiguator."""
        self._technical_terms = [
            'cricket', 'chemistry', 'physics', 'mathematics',
            'biology', 'medicine', 'chemical', 'baseball'
        ]
        
        self._common_words = ['run', 'friend', 'time', 'bank']
        
        self._particle_words = ['over', 'up', 'down', 'out', 'off', 'on', 'in', 'away']
    
    def disambiguate_tokens(self, tokens: List, doc) -> None:
        """
        Disambiguate all tokens in a sentence.
        
        Args:
            tokens: List of TokenInfo objects
            doc: spaCy Doc object for context
        """
        for i, (token, token_info) in enumerate(zip(doc, tokens)):
            if token_info.synsets:
                best_synset = self.get_best_synset_for_token(token, token_info, doc)
                token_info.best_synset = best_synset
    
    def get_best_synset_for_token(self, token, token_info, context_doc) -> Optional[Tuple[str, str]]:
        """
        Get the best synset for a token considering context.
        
        Args:
            token: spaCy token
            token_info: TokenInfo object
            context_doc: spaCy Doc object for context
            
        Returns:
            Tuple of (synset_name, definition) or None
        """
        synsets = token_info.synsets
        if not synsets:
            return None
        
        # Special handling for words that can be phrasal verb particles
        if token.lemma_.lower() in self._particle_words:
            return self._disambiguate_particle(token, synsets)
        
        # Filter out technical senses for common words
        if token.lemma_.lower() in self._common_words:
            filtered = self._filter_technical_synsets(synsets)
            if filtered:
                synsets = filtered
        
        # Return the first (most common) synset
        if synsets:
            try:
                synset = wn.synset(synsets[0])
                return (synsets[0], synset.definition())
            except:
                pass
        
        return None
    
    def _disambiguate_particle(self, token, synsets: List[str]) -> Optional[Tuple[str, str]]:
        """Disambiguate particles based on their syntactic role."""
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
        
        # Fallback to first synset
        try:
            synset = wn.synset(synsets[0])
            return (synsets[0], synset.definition())
        except:
            return None
    
    def _filter_technical_synsets(self, synsets: List[str]) -> List[str]:
        """Filter out overly technical synsets for common words."""
        filtered = []
        
        for synset_name in synsets:
            try:
                synset = wn.synset(synset_name)
                definition = synset.definition().lower()
                
                # Skip if it contains technical terms
                if not any(term in definition for term in self._technical_terms):
                    filtered.append(synset_name)
            except:
                continue
        
        return filtered 