"""
Word and synset data models.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class PartOfSpeech(Enum):
    """Enumeration of parts of speech."""
    NOUN = 'n'
    VERB = 'v'
    ADJECTIVE = 'a'
    ADJECTIVE_SATELLITE = 's'
    ADVERB = 'r'
    
    def to_full_name(self) -> str:
        """Get full name of the part of speech."""
        mapping = {
            self.NOUN: 'noun',
            self.VERB: 'verb',
            self.ADJECTIVE: 'adjective',
            self.ADJECTIVE_SATELLITE: 'adjective',
            self.ADVERB: 'adverb'
        }
        return mapping.get(self, 'unknown')


@dataclass
class WordSense:
    """Represents a single sense of a word in a synset."""
    word: str
    sense_key: Optional[str] = None
    count: int = 0  # Usage count in corpus
    
    def __str__(self) -> str:
        return self.word.replace('_', ' ')


@dataclass
class SynsetInfo:
    """Information about a single synset."""
    synset_name: str
    pos: PartOfSpeech
    definition: str
    sense_number: int
    
    # Word senses in this synset
    word_senses: List[WordSense] = field(default_factory=list)
    
    # Examples of usage
    examples: List[str] = field(default_factory=list)
    
    # Lexical relations
    hypernyms: List[str] = field(default_factory=list)
    hyponyms: List[str] = field(default_factory=list)
    meronyms: List[str] = field(default_factory=list)
    holonyms: List[str] = field(default_factory=list)
    antonyms: List[str] = field(default_factory=list)
    similar_to: List[str] = field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def lemma_names(self) -> List[str]:
        """Get all lemma names in this synset."""
        return [ws.word for ws in self.word_senses]
    
    @property
    def primary_lemma(self) -> str:
        """Get the primary (most common) lemma."""
        if self.word_senses:
            # Sort by count (descending) and return the first
            sorted_senses = sorted(self.word_senses, key=lambda ws: ws.count, reverse=True)
            return sorted_senses[0].word
        return ""
    
    def get_formatted_label(self) -> str:
        """Get a formatted label for display."""
        primary = self.primary_lemma.replace('_', ' ')
        pos_label = self.pos.to_full_name()
        return f"{primary} ({pos_label}.{self.sense_number})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'synset_name': self.synset_name,
            'pos': self.pos.value,
            'pos_label': self.pos.to_full_name(),
            'definition': self.definition,
            'sense_number': self.sense_number,
            'lemma_names': self.lemma_names,
            'examples': self.examples,
            'hypernyms': self.hypernyms,
            'hyponyms': self.hyponyms,
            'meronyms': self.meronyms,
            'holonyms': self.holonyms,
            'antonyms': self.antonyms,
            'similar_to': self.similar_to,
            **self.metadata
        }


@dataclass
class WordInfo:
    """Complete information about a word and all its senses."""
    word: str
    synsets: List[SynsetInfo] = field(default_factory=list)
    
    @property
    def found(self) -> bool:
        """Check if the word was found in WordNet."""
        return len(self.synsets) > 0
    
    @property
    def total_senses(self) -> int:
        """Get total number of senses for this word."""
        return len(self.synsets)
    
    def get_synset_by_sense(self, sense_number: int) -> Optional[SynsetInfo]:
        """Get a specific synset by sense number (1-based)."""
        if 1 <= sense_number <= len(self.synsets):
            return self.synsets[sense_number - 1]
        return None
    
    def get_synsets_by_pos(self, pos: PartOfSpeech) -> List[SynsetInfo]:
        """Get all synsets for a specific part of speech."""
        return [s for s in self.synsets if s.pos == pos]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'word': self.word,
            'found': self.found,
            'total_senses': self.total_senses,
            'synsets': [s.to_dict() for s in self.synsets]
        }


@dataclass
class NavigationContext:
    """Context for navigation in the graph."""
    current_word: str
    previous_word: Optional[str] = None
    navigation_history: List[str] = field(default_factory=list)
    clicked_node: Optional[str] = None
    
    def navigate_to(self, word: str) -> None:
        """Navigate to a new word."""
        if self.current_word and self.current_word != word:
            self.previous_word = self.current_word
            self.navigation_history.append(self.current_word)
        self.current_word = word
    
    def go_back(self) -> Optional[str]:
        """Go back to the previous word."""
        if self.navigation_history:
            self.current_word = self.navigation_history.pop()
            self.previous_word = self.navigation_history[-1] if self.navigation_history else None
            return self.current_word
        return None
    
    def get_breadcrumb_path(self, max_items: int = 5) -> List[str]:
        """Get breadcrumb path for display."""
        path = self.navigation_history[-max_items:] if len(self.navigation_history) > max_items else self.navigation_history
        if self.current_word and self.current_word not in path:
            path.append(self.current_word)
        return path 