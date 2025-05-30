"""
WordNet service for handling WordNet operations.
"""

from typing import List, Optional
from nltk.corpus import wordnet as wn
from src.models.word_data import WordInfo, SynsetInfo, WordSense, PartOfSpeech
from src.wordnet import download_nltk_data


class WordNetService:
    """Service for interacting with WordNet."""
    
    def __init__(self):
        """Initialize the WordNet service."""
        # Ensure WordNet data is downloaded
        download_nltk_data()
    
    def get_word_info(self, word: str) -> WordInfo:
        """
        Get complete information about a word from WordNet.
        
        Args:
            word: The word to look up
            
        Returns:
            WordInfo object containing all synsets and related information
        """
        synsets = wn.synsets(word)
        
        synset_infos = []
        for i, synset in enumerate(synsets, 1):
            # Get part of speech
            try:
                pos = PartOfSpeech(synset.pos())
            except ValueError:
                pos = PartOfSpeech.NOUN  # Default to noun if unknown
            
            # Get word senses
            word_senses = []
            for lemma in synset.lemmas():
                word_senses.append(WordSense(
                    word=lemma.name(),
                    sense_key=lemma.key(),
                    count=lemma.count()
                ))
            
            # Create synset info
            synset_info = SynsetInfo(
                synset_name=synset.name(),
                pos=pos,
                definition=synset.definition(),
                sense_number=i,
                word_senses=word_senses,
                examples=synset.examples(),
                hypernyms=[h.name() for h in synset.hypernyms()],
                hyponyms=[h.name() for h in synset.hyponyms()],
                meronyms=[m.name() for m in synset.part_meronyms() + synset.member_meronyms() + synset.substance_meronyms()],
                holonyms=[h.name() for h in synset.part_holonyms() + synset.member_holonyms() + synset.substance_holonyms()],
                antonyms=[ant.synset().name() for lemma in synset.lemmas() for ant in lemma.antonyms()],
                similar_to=[s.name() for s in synset.similar_tos()]
            )
            
            synset_infos.append(synset_info)
        
        return WordInfo(word=word, synsets=synset_infos)
    
    def get_synset_info(self, synset_name: str) -> Optional[SynsetInfo]:
        """
        Get information about a specific synset.
        
        Args:
            synset_name: The synset name (e.g., 'dog.n.01')
            
        Returns:
            SynsetInfo object or None if not found
        """
        try:
            synset = wn.synset(synset_name)
        except:
            return None
        
        # Get part of speech
        try:
            pos = PartOfSpeech(synset.pos())
        except ValueError:
            pos = PartOfSpeech.NOUN
        
        # Get word senses
        word_senses = []
        for lemma in synset.lemmas():
            word_senses.append(WordSense(
                word=lemma.name(),
                sense_key=lemma.key(),
                count=lemma.count()
            ))
        
        # Extract sense number from synset name
        try:
            sense_number = int(synset_name.split('.')[-1])
        except:
            sense_number = 1
        
        return SynsetInfo(
            synset_name=synset_name,
            pos=pos,
            definition=synset.definition(),
            sense_number=sense_number,
            word_senses=word_senses,
            examples=synset.examples(),
            hypernyms=[h.name() for h in synset.hypernyms()],
            hyponyms=[h.name() for h in synset.hyponyms()],
            meronyms=[m.name() for m in synset.part_meronyms() + synset.member_meronyms() + synset.substance_meronyms()],
            holonyms=[h.name() for h in synset.part_holonyms() + synset.member_holonyms() + synset.substance_holonyms()],
            antonyms=[ant.synset().name() for lemma in synset.lemmas() for ant in lemma.antonyms()],
            similar_to=[s.name() for s in synset.similar_tos()]
        )
    
    def search_words(self, query: str, limit: int = 10) -> List[str]:
        """
        Search for words matching a query pattern.
        
        Args:
            query: Search query (can be partial)
            limit: Maximum number of results
            
        Returns:
            List of matching words
        """
        # Get all lemma names
        all_lemmas = set()
        for synset in wn.all_synsets():
            for lemma in synset.lemmas():
                if query.lower() in lemma.name().lower():
                    all_lemmas.add(lemma.name().replace('_', ' '))
                    if len(all_lemmas) >= limit:
                        return sorted(list(all_lemmas))[:limit]
        
        return sorted(list(all_lemmas))[:limit]
    
    def validate_word(self, word: str) -> bool:
        """Check if a word exists in WordNet."""
        return len(wn.synsets(word)) > 0
    
    def validate_synset(self, synset_name: str) -> bool:
        """Check if a synset name is valid."""
        try:
            wn.synset(synset_name)
            return True
        except:
            return False 