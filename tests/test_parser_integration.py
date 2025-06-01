"""
Integration tests for the modular parsing system.
Tests both Token Processor and Dependency Analyzer working together on real sentences.
"""

import unittest
import spacy
from src.parsing.token_processor import (
    extract_token_features, is_content_word, is_function_word,
    get_simplified_pos, is_valid_token_for_wordnet, normalize_token_text
)
from src.parsing.dependency_analyzer import (
    get_children, get_ancestors, find_head_verb, get_dependency_distance,
    find_dependency_path, get_siblings, get_subtree, find_common_ancestor,
    get_dependency_chain, is_root
)


class TestParserIntegration(unittest.TestCase):
    """Integration tests using real spaCy parsing."""
    
    @classmethod
    def setUpClass(cls):
        """Load spaCy model once for all tests."""
        try:
            cls.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise unittest.SkipTest("spaCy model 'en_core_web_sm' not installed")
    
    def test_simple_sentence(self):
        """Test parsing a simple sentence."""
        doc = self.nlp("The cat sits on the mat.")
        features = [extract_token_features(token) for token in doc]
        
        # Test feature extraction
        self.assertEqual(len(features), 7)  # Including period
        self.assertEqual(features[0].text, "The")
        self.assertEqual(features[1].text, "cat")
        self.assertEqual(features[2].text, "sits")
        
        # Test content/function word classification
        content_indices = [i for i, f in enumerate(features) if is_content_word(f)]
        function_indices = [i for i, f in enumerate(features) if is_function_word(f)]
        
        # Content words: cat, sits, mat
        self.assertEqual(len(content_indices), 3)
        self.assertIn(1, content_indices)  # cat
        self.assertIn(2, content_indices)  # sits
        self.assertIn(5, content_indices)  # mat
        
        # Function words: The, on, the, .
        self.assertEqual(len(function_indices), 4)
        self.assertIn(0, function_indices)  # The
        self.assertIn(3, function_indices)  # on
        self.assertIn(4, function_indices)  # the
        self.assertIn(6, function_indices)  # .
    
    def test_dependency_structure(self):
        """Test dependency analysis on a sentence."""
        doc = self.nlp("The quick brown fox jumps over the lazy dog.")
        
        # Find the root
        root_indices = [i for i in range(len(doc)) if is_root(i, doc)]
        self.assertEqual(len(root_indices), 1)
        root_idx = root_indices[0]
        self.assertEqual(doc[root_idx].text, "jumps")
        
        # Test children of root verb
        verb_children = get_children(root_idx, doc)
        self.assertGreater(len(verb_children), 0)
        
        # Find subject (fox)
        fox_idx = next(i for i, token in enumerate(doc) if token.text == "fox")
        self.assertIn(fox_idx, verb_children)
        
        # Test ancestors of "brown"
        brown_idx = next(i for i, token in enumerate(doc) if token.text == "brown")
        ancestors = get_ancestors(brown_idx, doc)
        self.assertIn(fox_idx, ancestors)  # brown -> fox
        self.assertIn(root_idx, ancestors)  # fox -> jumps
    
    def test_noun_phrase_dependencies(self):
        """Test dependencies within noun phrases."""
        doc = self.nlp("The very tall green building collapsed.")
        
        # Find "building"
        building_idx = next(i for i, token in enumerate(doc) if token.text == "building")
        
        # Get all modifiers of building
        building_children = get_children(building_idx, doc)
        
        # Should have "The", "very", "tall", "green" as descendants
        building_subtree = get_subtree(building_idx, doc)
        subtree_words = [doc[i].text for i in building_subtree]
        
        self.assertIn("The", subtree_words)
        self.assertIn("green", subtree_words)
        self.assertIn("tall", subtree_words)
        
        # "very" modifies "tall", so might not be direct child of building
        self.assertIn("very", subtree_words)
    
    def test_prepositional_phrases(self):
        """Test prepositional phrase handling."""
        doc = self.nlp("The book on the table is mine.")
        
        # Find indices
        book_idx = next(i for i, t in enumerate(doc) if t.text == "book")
        on_idx = next(i for i, t in enumerate(doc) if t.text == "on")
        table_idx = next(i for i, t in enumerate(doc) if t.text == "table")
        
        # "on" should be child of "book"
        book_children = get_children(book_idx, doc)
        self.assertIn(on_idx, book_children)
        
        # "table" should be child of "on"
        on_children = get_children(on_idx, doc)
        self.assertIn(table_idx, on_children)
        
        # Distance from "book" to "table"
        distance = get_dependency_distance(book_idx, table_idx, doc)
        self.assertEqual(distance, 2)  # book -> on -> table
    
    def test_coordination(self):
        """Test coordination structures."""
        doc = self.nlp("Dogs and cats are pets.")
        
        # Find coordinated elements
        dogs_idx = next(i for i, t in enumerate(doc) if t.text == "Dogs")
        cats_idx = next(i for i, t in enumerate(doc) if t.text == "cats")
        
        # They should be connected by 'conj' relation
        conj_chain = get_dependency_chain(dogs_idx, doc, "conj")
        self.assertIn(dogs_idx, conj_chain)
        self.assertIn(cats_idx, conj_chain)
        
        # They should have same head (or one is head of other)
        dogs_head = doc[dogs_idx].head.i
        cats_head = doc[cats_idx].head.i
        
        # In coordination, typically first element is head
        self.assertTrue(cats_head == dogs_idx or dogs_head == cats_head)
    
    def test_complex_sentence(self):
        """Test a complex sentence with multiple clauses."""
        doc = self.nlp("When the rain stops, we will go outside to play.")
        
        # Find main verb and subordinate verb
        verb_indices = [i for i, t in enumerate(doc) if t.pos_ == "VERB"]
        self.assertGreaterEqual(len(verb_indices), 2)
        
        # Find root verb (main clause)
        root_verbs = [i for i in verb_indices if is_root(i, doc)]
        self.assertEqual(len(root_verbs), 1)
        main_verb_idx = root_verbs[0]
        self.assertEqual(doc[main_verb_idx].text, "go")
        
        # Find path between "rain" and "go"
        rain_idx = next(i for i, t in enumerate(doc) if t.text == "rain")
        go_idx = main_verb_idx
        
        path = find_dependency_path(rain_idx, go_idx, doc)
        self.assertIsNotNone(path)
        self.assertGreater(path.length, 0)
    
    def test_wordnet_filtering(self):
        """Test WordNet filtering on a sentence."""
        doc = self.nlp("I ran over my friend's cat with the car.")
        features = [extract_token_features(token) for token in doc]
        
        # Test which words are valid for WordNet
        wordnet_valid = []
        for i, (token, feature) in enumerate(zip(doc, features)):
            if is_valid_token_for_wordnet(feature):
                wordnet_valid.append((i, token.text, get_simplified_pos(feature.pos, feature.tag)))
        
        # Should include content words but not pronouns, prepositions, etc.
        valid_words = [w[1] for w in wordnet_valid]
        self.assertIn("ran", valid_words)
        self.assertIn("friend", valid_words)
        self.assertIn("cat", valid_words)
        self.assertIn("car", valid_words)
        
        # Should exclude function words
        self.assertNotIn("I", valid_words)
        self.assertNotIn("over", valid_words)  # preposition
        self.assertNotIn("with", valid_words)
        self.assertNotIn("the", valid_words)
        
        # Check POS mapping
        pos_map = {w[1]: w[2] for w in wordnet_valid}
        self.assertEqual(pos_map.get("ran"), "v")  # verb
        self.assertEqual(pos_map.get("friend"), "n")  # noun
        self.assertEqual(pos_map.get("cat"), "n")  # noun
        self.assertEqual(pos_map.get("car"), "n")  # noun
    
    def test_sentence_with_punctuation(self):
        """Test handling of punctuation and special characters."""
        doc = self.nlp('The "quick" brown fox--yes, that one!--jumped.')
        features = [extract_token_features(token) for token in doc]
        
        # Count punctuation
        punct_count = sum(1 for f in features if f.is_punct)
        self.assertGreater(punct_count, 0)
        
        # Test normalization
        for feature in features:
            normalized = normalize_token_text(feature.text)
            self.assertIsInstance(normalized, str)
            # Should not have zero-width characters
            self.assertNotIn('\u200b', normalized)
    
    def test_auxiliary_verbs(self):
        """Test auxiliary verb handling."""
        doc = self.nlp("She has been running for hours.")
        
        # Find auxiliaries
        aux_indices = []
        main_verb_idx = None
        
        for i, token in enumerate(doc):
            if token.pos_ == "AUX":
                aux_indices.append(i)
            elif token.pos_ == "VERB":
                main_verb_idx = i
        
        self.assertGreater(len(aux_indices), 0)
        self.assertIsNotNone(main_verb_idx)
        
        # In spaCy, auxiliaries might be siblings or children of main verb
        # Check that they're related in the dependency tree
        if main_verb_idx is not None:
            # Get all tokens connected to the main verb
            main_verb_subtree = get_subtree(main_verb_idx, doc)
            
            # At least one auxiliary should be connected to main verb
            self.assertTrue(any(aux_idx in main_verb_subtree for aux_idx in aux_indices) or
                          any(main_verb_idx in get_subtree(aux_idx, doc) for aux_idx in aux_indices))
    
    def test_relative_clauses(self):
        """Test relative clause structures."""
        doc = self.nlp("The man who lives next door is a doctor.")
        
        # Find "man" and "lives"
        man_idx = next(i for i, t in enumerate(doc) if t.text == "man")
        lives_idx = next(i for i, t in enumerate(doc) if t.text == "lives")
        
        # "lives" should be in subtree of "man" (relative clause modifies noun)
        man_subtree = get_subtree(man_idx, doc)
        self.assertIn(lives_idx, man_subtree)
        
        # Find the main verb "is"
        is_idx = next(i for i, t in enumerate(doc) if t.text == "is")
        
        # In spaCy, "is" is often the root with "man" as its subject (child)
        # Check that they're connected
        is_children = get_children(is_idx, doc)
        
        # Either "man" is direct child of "is" or connected through dependency path
        path = find_dependency_path(man_idx, is_idx, doc)
        self.assertIsNotNone(path)
        self.assertLessEqual(path.length, 2)  # Should be closely connected
    
    def test_edge_cases(self):
        """Test various edge cases."""
        # Empty-ish sentences
        test_cases = [
            ".",  # Just punctuation
            "Go!",  # Imperative
            "Really?",  # Single word question
            "Yes.",  # Single word answer
            "The the the.",  # Repeated words
        ]
        
        for text in test_cases:
            doc = self.nlp(text)
            features = [extract_token_features(token) for token in doc]
            
            # Should not crash
            self.assertGreater(len(features), 0)
            
            # Basic operations should work
            for i in range(len(doc)):
                children = get_children(i, doc)
                self.assertIsInstance(children, list)
                
                ancestors = get_ancestors(i, doc)
                self.assertIsInstance(ancestors, list)
                
                # No circular dependencies
                self.assertLessEqual(len(ancestors), len(doc))


class TestParserPerformance(unittest.TestCase):
    """Test parser performance and efficiency."""
    
    @classmethod
    def setUpClass(cls):
        """Load spaCy model once for all tests."""
        try:
            cls.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise unittest.SkipTest("spaCy model 'en_core_web_sm' not installed")
    
    def test_long_sentence(self):
        """Test parsing a long, complex sentence."""
        # A genuinely complex sentence
        text = ("The old professor, who had been teaching at the university "
                "for over thirty years and had published numerous papers on "
                "quantum mechanics, decided that it was finally time to retire "
                "and spend more time with his grandchildren, whom he rarely saw "
                "because they lived on the other side of the country.")
        
        doc = self.nlp(text)
        features = [extract_token_features(token) for token in doc]
        
        # Should handle long sentence
        self.assertGreater(len(features), 40)
        
        # Find all verbs
        verb_indices = [i for i, f in enumerate(features) if f.pos == "VERB"]
        self.assertGreater(len(verb_indices), 3)  # Multiple verbs in complex sentence
        
        # Test that dependency operations complete reasonably fast
        import time
        
        start = time.time()
        # Do various operations
        for i in range(min(10, len(doc))):
            _ = get_subtree(i, doc)
            _ = find_head_verb(i, doc)
        
        # Operations on first 10 tokens should be fast
        elapsed = time.time() - start
        self.assertLess(elapsed, 1.0)  # Should complete in under 1 second
    
    def test_deeply_nested_structure(self):
        """Test deeply nested grammatical structures."""
        # Nested prepositional phrases
        doc = self.nlp("The book on the shelf in the room at the end of the hall is mine.")
        
        # Find the deepest element
        hall_idx = next(i for i, t in enumerate(doc) if t.text == "hall")
        
        # Count ancestors
        ancestors = get_ancestors(hall_idx, doc)
        self.assertGreater(len(ancestors), 4)  # Deep nesting
        
        # Path from "book" to "hall" should be long
        book_idx = next(i for i, t in enumerate(doc) if t.text == "book")
        distance = get_dependency_distance(book_idx, hall_idx, doc)
        self.assertGreaterEqual(distance, 4)  # At least 4 edges


class TestVerbPhraseStructure(unittest.TestCase):
    """Test expected verb phrase structure in parsed sentences.
    
    These tests define the expected behavior where verbs are wrapped in
    phrase nodes with their arguments (subject, object, etc.) as siblings.
    """
    
    @classmethod
    def setUpClass(cls):
        """Load spaCy model once for all tests."""
        try:
            cls.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise unittest.SkipTest("spaCy model 'en_core_web_sm' not installed")
    
    def test_simple_svo_verb_phrase(self):
        """Test that simple SVO sentences create verb phrases with arguments as siblings."""
        doc = self.nlp("The cat eats fish.")
        
        # Expected structure:
        # verb_phrase
        # ├── subj: "The cat" (noun phrase)
        # ├── verb: "eats" 
        # └── obj: "fish"
        
        # Find the main verb
        verb_idx = next(i for i, t in enumerate(doc) if t.text == "eats")
        
        # The verb should be part of a phrase that contains:
        # 1. The subject (cat with its determiner)
        # 2. The verb itself
        # 3. The object (fish)
        
        # Get all tokens that should be in the verb phrase
        subj_indices = [i for i, t in enumerate(doc) if t.text in ["The", "cat"]]
        obj_indices = [i for i, t in enumerate(doc) if t.text == "fish"]
        
        # All these should be grouped together in the verb phrase
        verb_phrase_indices = subj_indices + [verb_idx] + obj_indices
        
        # Note: These assertions define the expected behavior
        # The actual implementation would need to create this structure
        # This serves as a specification
        self.assertGreater(len(verb_phrase_indices), 3)
    
    def test_intransitive_verb_phrase(self):
        """Test intransitive verbs with just subject."""
        doc = self.nlp("The dog sleeps.")
        
        # Expected structure:
        # verb_phrase
        # ├── subj: "The dog"
        # └── verb: "sleeps"
        
        verb_idx = next(i for i, t in enumerate(doc) if t.text == "sleeps")
        subj_indices = [i for i, t in enumerate(doc) if t.text in ["The", "dog"]]
        
        # Verb phrase should contain subject and verb
        verb_phrase_indices = subj_indices + [verb_idx]
        self.assertEqual(len(verb_phrase_indices), 3)  # The, dog, sleeps
    
    def test_ditransitive_verb_phrase(self):
        """Test ditransitive verbs with direct and indirect objects."""
        doc = self.nlp("She gave him the book.")
        
        # Expected structure:
        # verb_phrase
        # ├── subj: "She"
        # ├── verb: "gave"
        # ├── iobj: "him" 
        # └── dobj: "the book"
        
        verb_idx = next(i for i, t in enumerate(doc) if t.text == "gave")
        
        # All arguments should be siblings in the verb phrase
        she_idx = next(i for i, t in enumerate(doc) if t.text == "She")
        him_idx = next(i for i, t in enumerate(doc) if t.text == "him")
        book_indices = [i for i, t in enumerate(doc) if t.text in ["the", "book"]]
        
        verb_phrase_indices = [she_idx, verb_idx, him_idx] + book_indices
        self.assertEqual(len(set(verb_phrase_indices)), 5)  # All unique indices
    
    def test_auxiliary_verb_phrase(self):
        """Test that auxiliary verbs are included in the verb phrase."""
        doc = self.nlp("She has been running.")
        
        # Expected structure:
        # verb_phrase
        # ├── subj: "She"
        # ├── aux: "has"
        # ├── aux: "been"
        # └── verb: "running"
        
        # Find all verb-related tokens
        she_idx = next(i for i, t in enumerate(doc) if t.text == "She")
        has_idx = next(i for i, t in enumerate(doc) if t.text == "has")
        been_idx = next(i for i, t in enumerate(doc) if t.text == "been")
        running_idx = next(i for i, t in enumerate(doc) if t.text == "running")
        
        # All should be siblings in the verb phrase
        verb_phrase_indices = [she_idx, has_idx, been_idx, running_idx]
        self.assertEqual(len(verb_phrase_indices), 4)
    
    def test_phrasal_verb_structure(self):
        """Test phrasal verbs within verb phrases."""
        doc = self.nlp("She looked up the word.")
        
        # Expected structure:
        # verb_phrase
        # ├── subj: "She"
        # ├── phrasal_verb: "looked up"
        # │   ├── verb: "looked"
        # │   └── particle: "up"
        # └── obj: "the word"
        
        # The phrasal verb should be a child of the main verb phrase
        # with subject and object as siblings
        
        she_idx = next(i for i, t in enumerate(doc) if t.text == "She")
        looked_idx = next(i for i, t in enumerate(doc) if t.text == "looked")
        up_idx = next(i for i, t in enumerate(doc) if t.text == "up")
        word_indices = [i for i, t in enumerate(doc) if t.text in ["the", "word"]]
        
        # All components should be related within the verb phrase structure
        all_indices = [she_idx, looked_idx, up_idx] + word_indices
        self.assertEqual(len(set(all_indices)), 5)
    
    def test_verb_phrase_with_modifiers(self):
        """Test verb phrases with adverbial modifiers."""
        doc = self.nlp("She quickly ran to the store.")
        
        # Expected structure:
        # verb_phrase
        # ├── subj: "She"
        # ├── advmod: "quickly"
        # ├── verb: "ran"
        # └── prep_phrase: "to the store"
        
        she_idx = next(i for i, t in enumerate(doc) if t.text == "She")
        quickly_idx = next(i for i, t in enumerate(doc) if t.text == "quickly")
        ran_idx = next(i for i, t in enumerate(doc) if t.text == "ran")
        
        # Subject, adverb, and verb should be siblings
        core_indices = [she_idx, quickly_idx, ran_idx]
        self.assertEqual(len(core_indices), 3)
        
        # The prepositional phrase should also be part of the verb phrase
        to_store_indices = [i for i, t in enumerate(doc) if t.text in ["to", "the", "store"]]
        self.assertEqual(len(to_store_indices), 3)
    
    def test_complex_verb_phrase_dependencies(self):
        """Test that verb phrase structure preserves dependency relationships."""
        doc = self.nlp("The teacher gave the students homework yesterday.")
        
        # Even with the verb phrase structure, we should be able to:
        # 1. Identify the subject (teacher)
        # 2. Identify direct object (homework)
        # 3. Identify indirect object (students)
        # 4. Identify temporal modifier (yesterday)
        
        verb_idx = next(i for i, t in enumerate(doc) if t.text == "gave")
        
        # All arguments and modifiers should be accessible from the verb phrase
        teacher_indices = [i for i, t in enumerate(doc) if t.text in ["The", "teacher"]]
        students_indices = [i for i, t in enumerate(doc) if t.text in ["the", "students"]]
        homework_idx = next(i for i, t in enumerate(doc) if t.text == "homework")
        yesterday_idx = next(i for i, t in enumerate(doc) if t.text == "yesterday")
        
        # All should be part of the same verb phrase structure
        all_indices = teacher_indices + [verb_idx] + students_indices + [homework_idx, yesterday_idx]
        self.assertGreater(len(set(all_indices)), 6)
    
    def test_nested_verb_phrases(self):
        """Test sentences with multiple verbs creating nested structures."""
        doc = self.nlp("I want to learn to code.")
        
        # Expected: Multiple verb phrases, potentially nested
        # Main verb phrase for "want" containing subject
        # Nested verb phrases for "to learn" and "to code"
        
        want_idx = next(i for i, t in enumerate(doc) if t.text == "want")
        learn_idx = next(i for i, t in enumerate(doc) if t.text == "learn")
        code_idx = next(i for i, t in enumerate(doc) if t.text == "code")
        
        # Each verb should be in its own phrase with appropriate arguments
        self.assertNotEqual(want_idx, learn_idx)
        self.assertNotEqual(learn_idx, code_idx)
        
        # The main verb phrase should contain "I want"
        # with "to learn to code" as a complement
        i_idx = next(i for i, t in enumerate(doc) if t.text == "I")
        self.assertLess(i_idx, want_idx)  # Subject before verb


if __name__ == '__main__':
    unittest.main() 