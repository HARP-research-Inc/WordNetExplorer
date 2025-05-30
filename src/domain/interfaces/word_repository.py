"""Word repository interface for accessing WordNet data."""

from abc import ABC, abstractmethod
from typing import List, Optional, Set
from ..entities import Word, Synset, Relationship


class WordRepository(ABC):
    """
    Abstract interface for accessing WordNet data.
    
    This follows the Repository pattern to abstract data access
    and allow for different implementations (NLTK, database, etc.).
    """
    
    @abstractmethod
    def get_synsets(self, word: Word) -> List[Synset]:
        """
        Get all synsets for a given word.
        
        Args:
            word: The Word entity to look up
            
        Returns:
            List of Synset entities for the word
        """
        pass
    
    @abstractmethod
    def get_synset_by_name(self, synset_name: str) -> Optional[Synset]:
        """
        Get a specific synset by its name.
        
        Args:
            synset_name: The synset name (e.g., "dog.n.01")
            
        Returns:
            The Synset entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_relationships(self, synset: Synset, 
                         relationship_types: Optional[Set[str]] = None) -> List[Relationship]:
        """
        Get relationships for a synset.
        
        Args:
            synset: The source Synset entity
            relationship_types: Optional set of relationship type names to filter by
            
        Returns:
            List of Relationship entities
        """
        pass
    
    @abstractmethod
    def get_related_synsets(self, synset: Synset,
                           relationship_type: str) -> List[Synset]:
        """
        Get synsets related by a specific relationship type.
        
        Args:
            synset: The source Synset entity
            relationship_type: The type of relationship to follow
            
        Returns:
            List of related Synset entities
        """
        pass
    
    @abstractmethod
    def get_word_frequency(self, word: Word) -> int:
        """
        Get the frequency count for a word.
        
        Args:
            word: The Word entity
            
        Returns:
            Frequency count (0 if not found)
        """
        pass
    
    @abstractmethod
    def search_words(self, pattern: str, pos: Optional[str] = None) -> List[Word]:
        """
        Search for words matching a pattern.
        
        Args:
            pattern: Search pattern (can include wildcards)
            pos: Optional POS filter
            
        Returns:
            List of matching Word entities
        """
        pass 