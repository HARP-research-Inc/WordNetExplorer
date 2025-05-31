"""
Search history data models with query hashing.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import json


@dataclass
class SearchQuery:
    """Represents a single search query with all its parameters."""
    word: str
    sense_number: Optional[int] = None
    synset_search_mode: bool = False
    
    # Exploration parameters
    depth: int = 2
    max_nodes: int = 50
    max_branches: int = 5
    pos_filter: List[str] = field(default_factory=lambda: ["Nouns", "Verbs", "Adjectives", "Adverbs"])
    
    # Relationship filters
    active_relationships: List[str] = field(default_factory=list)
    
    # Additional settings
    simplified_mode: bool = False
    min_frequency: int = 0
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_hash(self) -> str:
        """Generate a unique hash for this query configuration."""
        # Create a dictionary of all relevant parameters
        params = {
            'word': self.word,
            'sense': self.sense_number,
            'synset_mode': self.synset_search_mode,
            'depth': self.depth,
            'max_nodes': self.max_nodes,
            'max_branches': self.max_branches,
            'pos_filter': sorted(self.pos_filter),  # Sort for consistency
            'relationships': sorted(self.active_relationships),
            'simplified': self.simplified_mode,
            'min_freq': self.min_frequency
        }
        
        # Convert to JSON string for hashing
        param_str = json.dumps(params, sort_keys=True)
        
        # Generate hash
        hash_obj = hashlib.md5(param_str.encode())
        return hash_obj.hexdigest()[:8]  # Use first 8 characters
    
    def get_display_label(self) -> str:
        """Get a human-readable label for this query."""
        base_label = self.word
        
        if self.sense_number:
            base_label = f"{self.word}.{self.sense_number:02d}"
        
        if self.synset_search_mode:
            base_label = f"[S] {base_label}"
        
        # Add hash
        hash_code = self.get_hash()
        return f"{base_label} #{hash_code}"
    
    def get_short_label(self) -> str:
        """Get a shorter label for compact display."""
        if self.sense_number:
            return f"{self.word}.{self.sense_number:02d}"
        return self.word
    
    def get_tooltip(self) -> str:
        """Get detailed tooltip text for this query."""
        lines = [
            f"Word: {self.word}",
        ]
        
        if self.sense_number:
            lines.append(f"Sense: {self.sense_number}")
        
        if self.synset_search_mode:
            lines.append("Mode: Synset Search")
        
        lines.extend([
            f"Depth: {self.depth}",
            f"Max nodes: {self.max_nodes}",
            f"Relationships: {len(self.active_relationships)} active"
        ])
        
        if self.simplified_mode:
            lines.append("Simplified mode: ON")
        
        lines.append(f"Hash: {self.get_hash()}")
        lines.append(f"Time: {self.timestamp.strftime('%H:%M:%S')}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'word': self.word,
            'sense_number': self.sense_number,
            'synset_search_mode': self.synset_search_mode,
            'depth': self.depth,
            'max_nodes': self.max_nodes,
            'max_branches': self.max_branches,
            'pos_filter': self.pos_filter,
            'active_relationships': self.active_relationships,
            'simplified_mode': self.simplified_mode,
            'min_frequency': self.min_frequency,
            'timestamp': self.timestamp.isoformat(),
            'hash': self.get_hash()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchQuery':
        """Create from dictionary."""
        # Handle timestamp
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        else:
            timestamp = datetime.now()
        
        return cls(
            word=data['word'],
            sense_number=data.get('sense_number'),
            synset_search_mode=data.get('synset_search_mode', False),
            depth=data.get('depth', 2),
            max_nodes=data.get('max_nodes', 50),
            max_branches=data.get('max_branches', 5),
            pos_filter=data.get('pos_filter', ["Nouns", "Verbs", "Adjectives", "Adverbs"]),
            active_relationships=data.get('active_relationships', []),
            simplified_mode=data.get('simplified_mode', False),
            min_frequency=data.get('min_frequency', 0),
            timestamp=timestamp
        )
    
    @classmethod
    def from_settings(cls, settings: Dict[str, Any]) -> 'SearchQuery':
        """Create from application settings dictionary."""
        # Extract active relationships
        active_relationships = []
        for key, value in settings.items():
            if key.startswith('show_') and value and key not in ['show_info', 'show_graph', 'show_labels']:
                rel_type = key[5:]  # Remove 'show_' prefix
                active_relationships.append(rel_type)
        
        return cls(
            word=settings.get('word', ''),
            sense_number=settings.get('parsed_sense_number') or settings.get('sense_number'),
            synset_search_mode=settings.get('synset_search_mode', False),
            depth=settings.get('depth', 2),
            max_nodes=settings.get('max_nodes', 50),
            max_branches=settings.get('max_branches', 5),
            pos_filter=settings.get('pos_filter', ["Nouns", "Verbs", "Adjectives", "Adverbs"]),
            active_relationships=active_relationships,
            simplified_mode=settings.get('simplified_mode', False),
            min_frequency=settings.get('min_frequency', 0)
        )


@dataclass
class SearchHistoryManager:
    """Manages search history with deduplication and organization."""
    queries: List[SearchQuery] = field(default_factory=list)
    max_history_size: int = 50
    
    def add_query(self, query: SearchQuery) -> bool:
        """
        Add a query to history. Returns True if added, False if duplicate.
        """
        # Check if this exact query already exists
        query_hash = query.get_hash()
        for existing in self.queries:
            if existing.get_hash() == query_hash:
                # Move to front (most recent)
                self.queries.remove(existing)
                self.queries.insert(0, query)
                return False
        
        # Add new query to front
        self.queries.insert(0, query)
        
        # Maintain size limit
        if len(self.queries) > self.max_history_size:
            self.queries = self.queries[:self.max_history_size]
        
        return True
    
    def get_queries_for_word(self, word: str) -> List[SearchQuery]:
        """Get all queries for a specific word."""
        return [q for q in self.queries if q.word == word]
    
    def get_unique_words(self) -> List[str]:
        """Get list of unique words in history."""
        words = []
        seen = set()
        for query in self.queries:
            if query.word not in seen:
                words.append(query.word)
                seen.add(query.word)
        return words
    
    def clear(self) -> None:
        """Clear all history."""
        self.queries.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'queries': [q.to_dict() for q in self.queries],
            'max_size': self.max_history_size
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SearchHistoryManager':
        """Create from dictionary."""
        queries = [SearchQuery.from_dict(q) for q in data.get('queries', [])]
        return cls(
            queries=queries,
            max_history_size=data.get('max_size', 50)
        ) 