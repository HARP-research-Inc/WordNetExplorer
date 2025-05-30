"""Word entity representing a word in natural language."""

from dataclasses import dataclass, field
from typing import Optional, Set
import re


@dataclass(frozen=True)
class Word:
    """
    Immutable Word entity representing a word in natural language.
    
    This is a value object in DDD terms - it has no identity beyond its attributes.
    """
    text: str
    pos: Optional[str] = None
    _normalized_text: str = field(init=False, repr=False)
    
    def __post_init__(self):
        """Validate and normalize word text."""
        if not self.text:
            raise ValueError("Word text cannot be empty")
        
        if not isinstance(self.text, str):
            raise TypeError(f"Word text must be a string, got {type(self.text)}")
        
        # Normalize text (lowercase, strip whitespace)
        normalized = self.text.strip().lower()
        object.__setattr__(self, '_normalized_text', normalized)
        
        # Validate POS if provided
        if self.pos is not None:
            valid_pos = {'n', 'v', 'a', 'r', 's'}  # noun, verb, adjective, adverb, satellite
            if self.pos not in valid_pos:
                raise ValueError(f"Invalid POS tag: {self.pos}. Must be one of {valid_pos}")
    
    @property
    def normalized_text(self) -> str:
        """Get the normalized form of the word."""
        return self._normalized_text
    
    @property
    def is_valid(self) -> bool:
        """Check if word is valid for WordNet lookup."""
        # Basic validation - can contain letters, hyphens, underscores
        pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')
        return bool(pattern.match(self._normalized_text))
    
    @property
    def is_multiword(self) -> bool:
        """Check if this is a multi-word expression."""
        return '_' in self._normalized_text
    
    def with_pos(self, pos: str) -> 'Word':
        """Create a new Word instance with specified POS."""
        return Word(text=self.text, pos=pos)
    
    def __str__(self) -> str:
        """String representation of the word."""
        if self.pos:
            return f"{self._normalized_text}.{self.pos}"
        return self._normalized_text
    
    def __hash__(self) -> int:
        """Hash based on normalized text and POS."""
        return hash((self._normalized_text, self.pos))
    
    def __eq__(self, other) -> bool:
        """Equality based on normalized text and POS."""
        if not isinstance(other, Word):
            return NotImplemented
        return (self._normalized_text, self.pos) == (other._normalized_text, other.pos) 