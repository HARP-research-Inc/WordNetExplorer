"""
Unit tests for Token Processor module
"""

import unittest
from unittest.mock import Mock
from src.parsing.token_processor import (
    TokenFeatures, extract_token_features, normalize_token_text,
    get_token_lemma, is_content_word, is_function_word,
    get_token_shape_category, is_valid_token_for_wordnet,
    get_simplified_pos, is_auxiliary_verb,
    FUNCTION_WORDS, CONTENT_POS_TAGS, FUNCTION_POS_TAGS
)


class TestTokenFeatures(unittest.TestCase):
    """Test TokenFeatures dataclass."""
    
    def test_token_features_creation(self):
        """Test creating TokenFeatures."""
        features = TokenFeatures(
            index=0, text="hello", lemma="hello", pos="NOUN",
            tag="NN", dep="nsubj", head=1, is_space=False,
            is_punct=False, is_stop=False, is_alpha=True,
            shape="xxxxx"
        )
        self.assertEqual(features.text, "hello")
        self.assertEqual(features.pos, "NOUN")
        
    def test_token_features_immutable(self):
        """Test that TokenFeatures is immutable."""
        features = TokenFeatures(
            index=0, text="hello", lemma="hello", pos="NOUN",
            tag="NN", dep="nsubj", head=1, is_space=False,
            is_punct=False, is_stop=False, is_alpha=True,
            shape="xxxxx"
        )
        with self.assertRaises(AttributeError):
            features.text = "world"
    
    def test_token_features_str(self):
        """Test string representation."""
        features = TokenFeatures(
            index=0, text="runs", lemma="run", pos="VERB",
            tag="VBZ", dep="ROOT", head=0, is_space=False,
            is_punct=False, is_stop=False, is_alpha=True,
            shape="xxxx"
        )
        self.assertEqual(str(features), "runs(VERB/ROOT)")


class TestExtractTokenFeatures(unittest.TestCase):
    """Test extract_token_features function."""
    
    def test_normal_token(self):
        """Test extracting features from normal token."""
        token = Mock()
        token.i = 2
        token.text = "running"
        token.lemma_ = "run"
        token.pos_ = "VERB"
        token.tag_ = "VBG"
        token.dep_ = "ROOT"
        token.head = Mock(i=2)
        token.is_space = False
        token.is_punct = False
        token.is_stop = False
        token.is_alpha = True
        token.shape_ = "xxxxx"
        
        features = extract_token_features(token)
        self.assertEqual(features.index, 2)
        self.assertEqual(features.text, "running")
        self.assertEqual(features.lemma, "run")
        self.assertEqual(features.pos, "VERB")
        self.assertEqual(features.tag, "VBG")
        self.assertEqual(features.dep, "ROOT")
        self.assertEqual(features.head, 2)
        self.assertFalse(features.is_space)
        self.assertFalse(features.is_punct)
        self.assertFalse(features.is_stop)
        self.assertTrue(features.is_alpha)
        self.assertEqual(features.shape, "xxxxx")
    
    def test_punctuation_token(self):
        """Test extracting features from punctuation."""
        token = Mock()
        token.i = 5
        token.text = "."
        token.lemma_ = "."
        token.pos_ = "PUNCT"
        token.tag_ = "."
        token.dep_ = "punct"
        token.head = Mock(i=4)
        token.is_space = False
        token.is_punct = True
        token.is_stop = False
        token.is_alpha = False
        token.shape_ = "."
        
        features = extract_token_features(token)
        self.assertTrue(features.is_punct)
        self.assertFalse(features.is_alpha)


class TestNormalizeTokenText(unittest.TestCase):
    """Test normalize_token_text function."""
    
    def test_normal_text(self):
        """Test normalizing normal text."""
        self.assertEqual(normalize_token_text("hello"), "hello")
        self.assertEqual(normalize_token_text("Hello"), "Hello")
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        self.assertEqual(normalize_token_text("hello  world"), "hello world")
        self.assertEqual(normalize_token_text("hello\nworld"), "hello world")
        self.assertEqual(normalize_token_text("hello\tworld"), "hello world")
    
    def test_unicode_normalization(self):
        """Test Unicode normalization."""
        # Composed vs decomposed forms
        self.assertEqual(normalize_token_text("café"), "café")
        self.assertEqual(normalize_token_text("cafe\u0301"), "café")
    
    def test_zero_width_removal(self):
        """Test removing zero-width characters."""
        self.assertEqual(normalize_token_text("hello\u200bworld"), "helloworld")
        self.assertEqual(normalize_token_text("hello\u200cworld"), "helloworld")
    
    def test_empty_text(self):
        """Test empty text."""
        self.assertEqual(normalize_token_text(""), "")
        self.assertEqual(normalize_token_text(None), "")


class TestGetTokenLemma(unittest.TestCase):
    """Test get_token_lemma function."""
    
    def test_normal_token(self):
        """Test getting lemma from normal token."""
        token = Mock()
        token.pos_ = "NOUN"
        token.lemma_ = "dog"
        token.text = "dogs"
        self.assertEqual(get_token_lemma(token), "dog")
    
    def test_pronoun(self):
        """Test pronouns return lowercase form."""
        token = Mock()
        token.pos_ = "PRON"
        token.lemma_ = "-PRON-"
        token.text = "I"
        self.assertEqual(get_token_lemma(token), "i")
    
    def test_proper_noun(self):
        """Test proper nouns preserve capitalization."""
        token = Mock()
        token.pos_ = "PROPN"
        token.lemma_ = "john"
        token.text = "John"
        self.assertEqual(get_token_lemma(token), "John")
    
    def test_pron_lemma_handling(self):
        """Test -PRON- lemma handling."""
        token = Mock()
        token.pos_ = "PRON"
        token.lemma_ = "-PRON-"
        token.text = "She"
        self.assertEqual(get_token_lemma(token), "she")


class TestContentFunctionWords(unittest.TestCase):
    """Test is_content_word and is_function_word functions."""
    
    def test_content_words_by_pos(self):
        """Test content word detection by POS."""
        # Test with Mock token
        for pos in CONTENT_POS_TAGS:
            token = Mock()
            token.pos_ = pos
            token.text = "word"
            self.assertTrue(is_content_word(token))
        
        # Test with TokenFeatures
        features = TokenFeatures(
            index=0, text="cat", lemma="cat", pos="NOUN",
            tag="NN", dep="nsubj", head=1, is_space=False,
            is_punct=False, is_stop=False, is_alpha=True,
            shape="xxx"
        )
        self.assertTrue(is_content_word(features))
    
    def test_function_words_by_pos(self):
        """Test function word detection by POS."""
        for pos in FUNCTION_POS_TAGS:
            token = Mock()
            token.pos_ = pos
            token.text = "word"
            self.assertTrue(is_function_word(token))
    
    def test_function_words_by_text(self):
        """Test function word detection by text."""
        for word in ['the', 'a', 'and', 'or', 'but']:
            token = Mock()
            token.pos_ = "DET"
            token.text = word
            self.assertTrue(is_function_word(token))
    
    def test_auxiliary_verbs_as_content(self):
        """Test auxiliary verbs that might be content words."""
        # 'have' as AUX but content word
        token = Mock()
        token.pos_ = "AUX"
        token.text = "having"  # As in "having fun"
        self.assertFalse(is_content_word(token))  # Still function word
        
        # But non-auxiliary marked as AUX
        token.text = "test"
        self.assertTrue(is_content_word(token))
    
    def test_punctuation_is_function(self):
        """Test punctuation is function word."""
        token = Mock()
        token.pos_ = "PUNCT"
        token.text = "."
        token.is_punct = True
        token.is_space = False
        self.assertTrue(is_function_word(token))


class TestTokenShapeCategory(unittest.TestCase):
    """Test get_token_shape_category function."""
    
    def test_lowercase(self):
        """Test lowercase detection."""
        self.assertEqual(get_token_shape_category("xxxxx"), "lower")
        self.assertEqual(get_token_shape_category("xxx"), "lower")
    
    def test_uppercase(self):
        """Test uppercase detection."""
        self.assertEqual(get_token_shape_category("XXXXX"), "upper")
        self.assertEqual(get_token_shape_category("XXX"), "upper")
    
    def test_title_case(self):
        """Test title case detection."""
        self.assertEqual(get_token_shape_category("Xxxxx"), "title")
    
    def test_mixed_case(self):
        """Test mixed case detection."""
        self.assertEqual(get_token_shape_category("XxXx"), "mixed")
        self.assertEqual(get_token_shape_category("xXxX"), "mixed")
    
    def test_digit(self):
        """Test digit detection."""
        self.assertEqual(get_token_shape_category("ddd"), "digit")
        self.assertEqual(get_token_shape_category("xxd"), "digit")
    
    def test_punctuation(self):
        """Test punctuation detection."""
        self.assertEqual(get_token_shape_category("."), "punct")
        self.assertEqual(get_token_shape_category("..."), "punct")
    
    def test_empty_shape(self):
        """Test empty shape."""
        self.assertEqual(get_token_shape_category(""), "other")


class TestValidTokenForWordNet(unittest.TestCase):
    """Test is_valid_token_for_wordnet function."""
    
    def test_valid_content_words(self):
        """Test valid content words."""
        token = Mock()
        token.pos_ = "NOUN"
        token.text = "cat"
        self.assertTrue(is_valid_token_for_wordnet(token))
        
        token.pos_ = "VERB"
        token.text = "run"
        self.assertTrue(is_valid_token_for_wordnet(token))
    
    def test_function_words_invalid(self):
        """Test function words are invalid."""
        token = Mock()
        token.pos_ = "DET"
        token.text = "the"
        self.assertFalse(is_valid_token_for_wordnet(token))
    
    def test_single_chars(self):
        """Test single character handling."""
        token = Mock()
        token.pos_ = "PRON"
        token.text = "I"
        self.assertFalse(is_valid_token_for_wordnet(token))  # Function word
        
        token.pos_ = "NOUN"
        token.text = "a"
        self.assertTrue(is_valid_token_for_wordnet(token))  # 'a' as noun
        
        token.text = "x"
        self.assertFalse(is_valid_token_for_wordnet(token))
    
    def test_digits_invalid(self):
        """Test digits are invalid."""
        token = Mock()
        token.pos_ = "NUM"
        token.text = "123"
        self.assertFalse(is_valid_token_for_wordnet(token))
    
    def test_special_chars_invalid(self):
        """Test special characters are invalid."""
        token = Mock()
        token.pos_ = "NOUN"
        token.text = "@#$"
        self.assertFalse(is_valid_token_for_wordnet(token))


class TestSimplifiedPOS(unittest.TestCase):
    """Test get_simplified_pos function."""
    
    def test_noun_mapping(self):
        """Test noun POS mapping."""
        self.assertEqual(get_simplified_pos("NOUN"), "n")
        self.assertEqual(get_simplified_pos("PROPN"), "n")
    
    def test_verb_mapping(self):
        """Test verb POS mapping."""
        self.assertEqual(get_simplified_pos("VERB"), "v")
    
    def test_adjective_mapping(self):
        """Test adjective POS mapping."""
        self.assertEqual(get_simplified_pos("ADJ"), "a")
    
    def test_adverb_mapping(self):
        """Test adverb POS mapping."""
        self.assertEqual(get_simplified_pos("ADV"), "r")
    
    def test_unmapped_pos(self):
        """Test unmapped POS returns None."""
        self.assertIsNone(get_simplified_pos("DET"))
        self.assertIsNone(get_simplified_pos("PRON"))
    
    def test_tag_handling(self):
        """Test special tag handling."""
        # Gerund
        self.assertEqual(get_simplified_pos("VERB", "VBG"), "v")
        # Past participle
        self.assertEqual(get_simplified_pos("VERB", "VBN"), "v")


class TestAuxiliaryVerb(unittest.TestCase):
    """Test is_auxiliary_verb function."""
    
    def test_aux_pos(self):
        """Test AUX POS tag."""
        token = Mock()
        token.pos_ = "AUX"
        token.text = "is"
        self.assertTrue(is_auxiliary_verb(token))
    
    def test_common_auxiliaries(self):
        """Test common auxiliary verbs."""
        aux_verbs = ['be', 'am', 'is', 'are', 'was', 'were',
                     'have', 'has', 'had', 'do', 'does', 'did',
                     'will', 'would', 'can', 'could', 'may', 'might']
        
        for verb in aux_verbs:
            token = Mock()
            token.pos_ = "VERB"
            token.text = verb
            self.assertTrue(is_auxiliary_verb(token))
    
    def test_non_auxiliary(self):
        """Test non-auxiliary verbs."""
        token = Mock()
        token.pos_ = "VERB"
        token.text = "run"
        self.assertFalse(is_auxiliary_verb(token))
    
    def test_token_features(self):
        """Test with TokenFeatures object."""
        features = TokenFeatures(
            index=0, text="will", lemma="will", pos="AUX",
            tag="MD", dep="aux", head=1, is_space=False,
            is_punct=False, is_stop=False, is_alpha=True,
            shape="xxxx"
        )
        self.assertTrue(is_auxiliary_verb(features))


if __name__ == '__main__':
    unittest.main() 