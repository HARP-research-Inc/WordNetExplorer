"""Synset entity representing a WordNet synset."""

from dataclasses import dataclass, field
from typing import List, Set, Optional, FrozenSet
from .word import Word


@dataclass(frozen=True)
class Synset:
    """
    Immutable Synset entity representing a WordNet synset.
    
    A synset (synonym set) is a group of words that share the same meaning
    in a particular context.
    """
    name: str  # e.g., "dog.n.01"
    definition: str
    examples: List[str] = field(default_factory=list)
    lemmas: FrozenSet[str] = field(default_factory=frozenset)
    pos: str = field(init=False)
    offset: Optional[int] = None
    
    def __post_init__(self):
        """Validate and extract synset properties."""
        if not self.name:
            raise ValueError("Synset name cannot be empty")
        
        if not self.definition:
            raise ValueError("Synset definition cannot be empty")
        
        # Extract POS from synset name (e.g., "dog.n.01" -> "n")
        parts = self.name.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid synset name format: {self.name}")
        
        pos = parts[1]
        if pos not in {'n', 'v', 'a', 'r', 's'}:
            raise ValueError(f"Invalid POS in synset name: {pos}")
        
        object.__setattr__(self, 'pos', pos)
        
        # Ensure lemmas is a frozenset for immutability
        if not isinstance(self.lemmas, frozenset):
            object.__setattr__(self, 'lemmas', frozenset(self.lemmas))
        
        # Ensure examples is a tuple for immutability
        if not isinstance(self.examples, tuple):
            object.__setattr__(self, 'examples', tuple(self.examples))
    
    @property
    def word_form(self) -> str:
        """Get the primary word form from the synset name."""
        return self.name.split('.')[0]
    
    @property
    def sense_number(self) -> int:
        """Get the sense number from the synset name."""
        return int(self.name.split('.')[2])
    
    @property
    def primary_word(self) -> Word:
        """Get the primary Word entity for this synset."""
        return Word(text=self.word_form, pos=self.pos)
    
    @property
    def all_words(self) -> Set[Word]:
        """Get all Word entities associated with this synset."""
        words = set()
        for lemma in self.lemmas:
            words.add(Word(text=lemma, pos=self.pos))
        return words
    
    def has_lemma(self, lemma: str) -> bool:
        """Check if synset contains a specific lemma."""
        return lemma.lower() in {l.lower() for l in self.lemmas}
    
    def similarity_key(self) -> tuple:
        """Get a key for similarity comparison."""
        return (self.pos, frozenset(self.lemmas))
    
    def __str__(self) -> str:
        """String representation of the synset."""
        return f"{self.name}: {self.definition[:50]}..."
    
    def __repr__(self) -> str:
        """Detailed representation of the synset."""
        return (f"Synset(name='{self.name}', "
                f"definition='{self.definition[:30]}...', "
                f"lemmas={len(self.lemmas)})")
    
    def __hash__(self) -> int:
        """Hash based on synset name (unique identifier)."""
        return hash(self.name)
    
    def __eq__(self, other) -> bool:
        """Equality based on synset name."""
        if not isinstance(other, Synset):
            return NotImplemented
        return self.name == other.name 