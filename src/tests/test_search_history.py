"""
Tests for search history functionality.
"""

import unittest
from datetime import datetime
import sys
import os

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
parent_dir = os.path.dirname(src_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now we can import with src prefix
from src.models.search_history import SearchQuery, SearchHistoryManager


class TestSearchQuery(unittest.TestCase):
    """Test the SearchQuery data model."""
    
    def test_basic_query(self):
        """Test creating a basic query."""
        query = SearchQuery(word="dog")
        self.assertEqual(query.word, "dog")
        self.assertIsNone(query.sense_number)
        self.assertFalse(query.synset_search_mode)
    
    def test_sense_query(self):
        """Test query with sense number."""
        query = SearchQuery(word="dog", sense_number=1)
        self.assertEqual(query.get_short_label(), "dog.01")
        self.assertEqual(query.get_display_label()[:6], "dog.01")
    
    def test_synset_mode_query(self):
        """Test query in synset mode."""
        query = SearchQuery(word="dog", sense_number=1, synset_search_mode=True)
        label = query.get_display_label()
        self.assertTrue(label.startswith("[S] dog.01"))
    
    def test_hash_consistency(self):
        """Test that hash is consistent for same parameters."""
        query1 = SearchQuery(word="dog", depth=2, max_nodes=50)
        query2 = SearchQuery(word="dog", depth=2, max_nodes=50)
        self.assertEqual(query1.get_hash(), query2.get_hash())
    
    def test_hash_uniqueness(self):
        """Test that hash is different for different parameters."""
        query1 = SearchQuery(word="dog", depth=2)
        query2 = SearchQuery(word="dog", depth=3)
        self.assertNotEqual(query1.get_hash(), query2.get_hash())
    
    def test_tooltip(self):
        """Test tooltip generation."""
        query = SearchQuery(
            word="dog",
            sense_number=1,
            depth=3,
            active_relationships=["hypernym", "hyponym"]
        )
        tooltip = query.get_tooltip()
        self.assertIn("Word: dog", tooltip)
        self.assertIn("Sense: 1", tooltip)
        self.assertIn("Depth: 3", tooltip)
        self.assertIn("Relationships: 2 active", tooltip)
    
    def test_from_settings(self):
        """Test creating query from settings dictionary."""
        settings = {
            'word': 'cat',
            'parsed_sense_number': 2,
            'depth': 3,
            'show_hypernym': True,
            'show_hyponym': True,
            'show_meronym': False
        }
        query = SearchQuery.from_settings(settings)
        self.assertEqual(query.word, 'cat')
        self.assertEqual(query.sense_number, 2)
        self.assertEqual(query.depth, 3)
        self.assertIn('hypernym', query.active_relationships)
        self.assertIn('hyponym', query.active_relationships)
        self.assertNotIn('meronym', query.active_relationships)


class TestSearchHistoryManager(unittest.TestCase):
    """Test the SearchHistoryManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = SearchHistoryManager()
    
    def test_add_query(self):
        """Test adding queries."""
        query = SearchQuery(word="dog")
        result = self.manager.add_query(query)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.queries), 1)
    
    def test_duplicate_detection(self):
        """Test that duplicate queries are detected."""
        query1 = SearchQuery(word="dog", depth=2)
        query2 = SearchQuery(word="dog", depth=2)
        
        self.manager.add_query(query1)
        result = self.manager.add_query(query2)
        
        self.assertFalse(result)  # Duplicate not added
        self.assertEqual(len(self.manager.queries), 1)
    
    def test_move_to_front(self):
        """Test that duplicates are moved to front."""
        query1 = SearchQuery(word="dog")
        query2 = SearchQuery(word="cat")
        query3 = SearchQuery(word="dog")  # Duplicate of query1
        
        self.manager.add_query(query1)
        self.manager.add_query(query2)
        self.manager.add_query(query3)
        
        # Dog should be at front now
        self.assertEqual(self.manager.queries[0].word, "dog")
        self.assertEqual(self.manager.queries[1].word, "cat")
        self.assertEqual(len(self.manager.queries), 2)
    
    def test_size_limit(self):
        """Test that history respects size limit."""
        manager = SearchHistoryManager(max_history_size=3)
        
        for i in range(5):
            manager.add_query(SearchQuery(word=f"word{i}"))
        
        self.assertEqual(len(manager.queries), 3)
        # Most recent should be kept
        self.assertEqual(manager.queries[0].word, "word4")
        self.assertEqual(manager.queries[1].word, "word3")
        self.assertEqual(manager.queries[2].word, "word2")
    
    def test_get_queries_for_word(self):
        """Test getting queries for a specific word."""
        self.manager.add_query(SearchQuery(word="dog", depth=2))
        self.manager.add_query(SearchQuery(word="cat", depth=2))
        self.manager.add_query(SearchQuery(word="dog", depth=3))
        
        dog_queries = self.manager.get_queries_for_word("dog")
        self.assertEqual(len(dog_queries), 2)
        self.assertTrue(all(q.word == "dog" for q in dog_queries))
    
    def test_get_unique_words(self):
        """Test getting unique words."""
        self.manager.add_query(SearchQuery(word="dog", depth=2))
        self.manager.add_query(SearchQuery(word="cat"))
        self.manager.add_query(SearchQuery(word="dog", depth=3))
        self.manager.add_query(SearchQuery(word="bird"))
        
        unique_words = self.manager.get_unique_words()
        self.assertEqual(len(unique_words), 3)
        self.assertEqual(unique_words, ["bird", "dog", "cat"])  # Most recent first
    
    def test_clear(self):
        """Test clearing history."""
        self.manager.add_query(SearchQuery(word="dog"))
        self.manager.add_query(SearchQuery(word="cat"))
        
        self.manager.clear()
        self.assertEqual(len(self.manager.queries), 0)
    
    def test_serialization(self):
        """Test converting to/from dictionary."""
        self.manager.add_query(SearchQuery(word="dog", sense_number=1))
        self.manager.add_query(SearchQuery(word="cat", depth=3))
        
        # Convert to dict
        data = self.manager.to_dict()
        self.assertEqual(len(data['queries']), 2)
        self.assertEqual(data['max_size'], 50)
        
        # Create new manager from dict
        new_manager = SearchHistoryManager.from_dict(data)
        self.assertEqual(len(new_manager.queries), 2)
        self.assertEqual(new_manager.queries[0].word, "cat")
        self.assertEqual(new_manager.queries[1].word, "dog")


class TestIntegration(unittest.TestCase):
    """Integration tests for search history."""
    
    def test_complete_workflow(self):
        """Test a complete workflow."""
        manager = SearchHistoryManager()
        
        # User searches for "dog"
        settings1 = {
            'word': 'dog',
            'depth': 2,
            'show_hypernym': True,
            'show_hyponym': True
        }
        query1 = SearchQuery.from_settings(settings1)
        manager.add_query(query1)
        
        # User searches for "dog" with sense 1
        settings2 = {
            'word': 'dog',
            'parsed_sense_number': 1,
            'depth': 2,
            'show_hypernym': True,
            'show_hyponym': True
        }
        query2 = SearchQuery.from_settings(settings2)
        manager.add_query(query2)
        
        # User searches for "cat"
        settings3 = {
            'word': 'cat',
            'depth': 3,
            'show_hypernym': True
        }
        query3 = SearchQuery.from_settings(settings3)
        manager.add_query(query3)
        
        # Check results
        self.assertEqual(len(manager.queries), 3)
        
        # Get dog queries
        dog_queries = manager.get_queries_for_word("dog")
        self.assertEqual(len(dog_queries), 2)
        
        # Check that queries have different hashes
        hashes = [q.get_hash() for q in dog_queries]
        self.assertEqual(len(set(hashes)), 2)  # All unique
        
        # Check display labels
        labels = [q.get_display_label() for q in dog_queries]
        self.assertTrue(any("dog.01" in label for label in labels))
        self.assertTrue(any("dog.01" not in label for label in labels))


if __name__ == '__main__':
    unittest.main() 