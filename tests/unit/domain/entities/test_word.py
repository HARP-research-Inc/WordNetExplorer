"""Unit tests for the Word entity."""

import pytest
from src.domain.entities import Word


class TestWord:
    """Test cases for Word entity."""
    
    def test_create_valid_word(self):
        """Test creating a valid word."""
        word = Word("Dog")
        assert word.text == "Dog"
        assert word.normalized_text == "dog"
        assert word.pos is None
        assert word.is_valid
    
    def test_create_word_with_pos(self):
        """Test creating a word with POS tag."""
        word = Word("run", pos='v')
        assert word.text == "run"
        assert word.pos == 'v'
        assert str(word) == "run.v"
    
    def test_word_normalization(self):
        """Test that words are properly normalized."""
        test_cases = [
            ("DOG", "dog"),
            ("  cat  ", "cat"),
            ("HOUSE", "house"),
            ("multi_word", "multi_word"),
        ]
        
        for input_text, expected in test_cases:
            word = Word(input_text)
            assert word.normalized_text == expected
    
    def test_empty_word_raises_error(self):
        """Test that empty word raises ValueError."""
        with pytest.raises(ValueError, match="Word text cannot be empty"):
            Word("")
        
        with pytest.raises(ValueError, match="Word text cannot be empty"):
            Word("   ")
    
    def test_invalid_type_raises_error(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="Word text must be a string"):
            Word(123)
        
        with pytest.raises(TypeError, match="Word text must be a string"):
            Word(None)
    
    def test_invalid_pos_raises_error(self):
        """Test that invalid POS tag raises ValueError."""
        with pytest.raises(ValueError, match="Invalid POS tag"):
            Word("dog", pos='x')
    
    def test_valid_pos_tags(self):
        """Test all valid POS tags."""
        valid_pos = ['n', 'v', 'a', 'r', 's']
        
        for pos in valid_pos:
            word = Word("test", pos=pos)
            assert word.pos == pos
    
    def test_is_valid_word(self):
        """Test word validation."""
        valid_words = [
            "dog",
            "run",
            "multi_word",
            "test123",
            "word-with-hyphen"
        ]
        
        invalid_words = [
            "123test",  # starts with number
            "@word",    # special character
            "word!",    # special character
            "",         # empty (but this raises exception earlier)
        ]
        
        for text in valid_words:
            word = Word(text)
            assert word.is_valid, f"{text} should be valid"
        
        for text in invalid_words[:-1]:  # Skip empty string as it raises exception
            word = Word(text)
            assert not word.is_valid, f"{text} should be invalid"
    
    def test_is_multiword(self):
        """Test multiword detection."""
        assert Word("single").is_multiword is False
        assert Word("multi_word").is_multiword is True
        assert Word("three_word_phrase").is_multiword is True
    
    def test_with_pos_creates_new_instance(self):
        """Test that with_pos creates a new instance."""
        word1 = Word("run")
        word2 = word1.with_pos('v')
        
        assert word1 is not word2
        assert word1.pos is None
        assert word2.pos == 'v'
        assert word1.text == word2.text
    
    def test_word_equality(self):
        """Test word equality."""
        word1 = Word("dog")
        word2 = Word("DOG")
        word3 = Word("dog", pos='n')
        word4 = Word("cat")
        
        assert word1 == word2  # Same normalized text
        assert word1 != word3  # Different POS
        assert word1 != word4  # Different text
        assert word1 != "dog"  # Different type
    
    def test_word_hash(self):
        """Test word hashing for use in sets/dicts."""
        word1 = Word("dog")
        word2 = Word("DOG")
        word3 = Word("dog", pos='n')
        
        # Same normalized text should have same hash
        assert hash(word1) == hash(word2)
        
        # Different POS should have different hash
        assert hash(word1) != hash(word3)
        
        # Can be used in sets
        word_set = {word1, word2, word3}
        assert len(word_set) == 2  # word1 and word2 are considered equal
    
    def test_word_immutability(self):
        """Test that Word is immutable."""
        word = Word("dog")
        
        with pytest.raises(AttributeError):
            word.text = "cat"
        
        with pytest.raises(AttributeError):
            word.pos = 'n'
        
        with pytest.raises(AttributeError):
            word._normalized_text = "cat"
    
    def test_string_representation(self):
        """Test string representation of Word."""
        assert str(Word("dog")) == "dog"
        assert str(Word("CAT")) == "cat"
        assert str(Word("run", pos='v')) == "run.v"
        assert str(Word("BLUE", pos='a')) == "blue.a" 