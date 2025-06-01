"""
Test suite for syntactic tree structure produced by the sentence analyzer.

These tests verify that the syntactic tree structure follows the expected pattern
where verbs are wrapped in phrase nodes with their arguments as siblings.
"""

import unittest
from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2
from src.services.syntactic_tree import SyntacticNode


class TestSyntacticTreeStructure(unittest.TestCase):
    """Test the syntactic tree structure produced by SentenceAnalyzerV2."""
    
    def setUp(self):
        """Create analyzer instance for tests."""
        self.analyzer = SentenceAnalyzerV2()
    
    def find_nodes_by_type(self, node, node_type, found=None):
        """Recursively find all nodes of a given type."""
        if found is None:
            found = []
        
        if node.node_type == node_type:
            found.append(node)
        
        for child in node.children:
            self.find_nodes_by_type(child, node_type, found)
        
        return found
    
    def find_verb_phrases(self, node, found=None):
        """Find all phrase nodes that contain verbs."""
        if found is None:
            found = []
        
        if node.node_type == 'phrase':
            # Check if this phrase contains a verb
            has_verb = False
            for child in node.children:
                if (child.node_type == 'word' and 
                    child.token_info and 
                    child.token_info.pos == 'VERB'):
                    has_verb = True
                    break
                elif child.edge_label in ['verb', 'verb_head', 'tverb']:
                    has_verb = True
                    break
            
            if has_verb:
                found.append(node)
        
        for child in node.children:
            self.find_verb_phrases(child, found)
        
        return found
    
    def get_child_edge_labels(self, node):
        """Get all edge labels of a node's children."""
        return [child.edge_label for child in node.children]
    
    def get_child_texts(self, node):
        """Get all texts of a node's children."""
        return [child.text for child in node.children]
    
    def test_simple_svo_creates_verb_phrase(self):
        """Test that simple SVO sentence creates a verb phrase with arguments as siblings."""
        analysis = self.analyzer.analyze_sentence("The cat eats fish.")
        
        # Find verb phrases in the syntactic tree
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        # EXPECTED: Should have at least one verb phrase
        self.assertGreater(len(verb_phrases), 0, 
                          "Should have at least one verb phrase node")
        
        # The verb phrase should contain subject, verb, and object as siblings
        vp = verb_phrases[0]
        child_labels = self.get_child_edge_labels(vp)
        
        # EXPECTED: Verb phrase contains subject, verb, and object
        self.assertIn('subj', child_labels, 
                     "Verb phrase should have subject as child")
        self.assertIn('obj', child_labels, 
                     "Verb phrase should have object as child")
        self.assertTrue(any(label in ['verb', 'verb_head', 'tverb'] for label in child_labels),
                       "Verb phrase should have verb as child")
    
    def test_intransitive_verb_phrase_structure(self):
        """Test intransitive verb gets wrapped in phrase with subject."""
        analysis = self.analyzer.analyze_sentence("The dog sleeps.")
        
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        # Should have verb phrase
        self.assertGreater(len(verb_phrases), 0, 
                          "Should have verb phrase for intransitive verb")
        
        vp = verb_phrases[0]
        child_labels = self.get_child_edge_labels(vp)
        
        # Should have subject and verb
        self.assertIn('subj', child_labels, "Should have subject")
        self.assertTrue(any(label in ['verb', 'verb_head', 'tverb'] for label in child_labels),
                       "Should have verb")
    
    def test_auxiliary_verbs_in_verb_phrase(self):
        """Test that auxiliary verbs are included in the verb phrase."""
        analysis = self.analyzer.analyze_sentence("She has been running.")
        
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        self.assertGreater(len(verb_phrases), 0, 
                          "Should have verb phrase with auxiliaries")
        
        vp = verb_phrases[0]
        child_labels = self.get_child_edge_labels(vp)
        child_texts = self.get_child_texts(vp)
        
        # Should have subject
        self.assertIn('subj', child_labels, "Should have subject")
        
        # Should have a verb sub-phrase that contains auxiliaries
        verb_subphrase = None
        for child in vp.children:
            if child.edge_label == 'verb' and child.node_type == 'phrase':
                verb_subphrase = child
                break
        
        self.assertIsNotNone(verb_subphrase, 
                            "Should have verb sub-phrase containing auxiliaries and main verb")
        
        # Check the verb sub-phrase contains auxiliaries
        subphrase_labels = self.get_child_edge_labels(verb_subphrase)
        aux_count = sum(1 for label in subphrase_labels if label == 'aux')
        self.assertGreaterEqual(aux_count, 2, 
                               "Should have 'has' and 'been' as auxiliaries")
        
        # Should have the main verb
        self.assertIn('verb_head', subphrase_labels, "Should have main verb")
        
        # Check the text includes all parts
        self.assertEqual(verb_subphrase.text, "has been running",
                        "Verb sub-phrase should contain all auxiliary verbs and main verb")
    
    def test_verb_not_directly_under_clause(self):
        """Test that verbs are not direct children of clauses but wrapped in phrases."""
        analysis = self.analyzer.analyze_sentence("The teacher explains the lesson clearly.")
        
        # Find all clause nodes
        clauses = self.find_nodes_by_type(analysis.syntactic_tree, 'clause')
        if not clauses:
            # If no explicit clause, check sentence node
            clauses = [analysis.syntactic_tree] if analysis.syntactic_tree.node_type == 'sentence' else []
        
        for clause in clauses:
            # Check that no verb word nodes are direct children of clause
            for child in clause.children:
                if child.node_type == 'word' and child.token_info:
                    self.assertNotEqual(child.token_info.pos, 'VERB',
                                       f"Verb '{child.text}' should not be direct child of clause")
    
    def test_phrasal_verb_structure(self):
        """Test that phrasal verbs are properly structured within verb phrases."""
        analysis = self.analyzer.analyze_sentence("She looked up the word.")
        
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        self.assertGreater(len(verb_phrases), 0, 
                          "Should have verb phrase for phrasal verb")
        
        # Find the verb phrase that contains the subject (the outermost one)
        vp_with_subject = None
        for vp in verb_phrases:
            child_labels = self.get_child_edge_labels(vp)
            if 'subj' in child_labels:
                vp_with_subject = vp
                break
        
        self.assertIsNotNone(vp_with_subject, "Should find verb phrase with subject")
        
        vp = vp_with_subject
        child_labels = self.get_child_edge_labels(vp)
        
        # Should have subject and object as siblings
        self.assertIn('subj', child_labels, "Should have subject")
        self.assertIn('obj', child_labels, "Should have object")
        
        # Should have phrasal verb structure (either as single node or verb+particle)
        has_phrasal = False
        for child in vp.children:
            if 'look' in child.text.lower() and 'up' in child.text.lower():
                has_phrasal = True
                break
            elif child.node_type == 'phrase' and child.text == 'looked up':
                has_phrasal = True
                break
        
        self.assertTrue(has_phrasal, "Should have phrasal verb structure")
    
    def test_complex_sentence_verb_phrases(self):
        """Test that complex sentences have appropriate verb phrase structures."""
        analysis = self.analyzer.analyze_sentence("When it rains, I stay inside.")
        
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        # Should have multiple verb phrases for multiple verbs
        self.assertGreaterEqual(len(verb_phrases), 2, 
                               "Complex sentence should have multiple verb phrases")
        
        # Each verb phrase should have appropriate structure
        for vp in verb_phrases:
            child_labels = self.get_child_edge_labels(vp)
            
            # Should have at least a verb
            has_verb = any(label in ['verb', 'verb_head', 'tverb'] for label in child_labels)
            self.assertTrue(has_verb, f"Verb phrase '{vp.text}' should contain a verb")
            
            # Most should have a subject (except maybe embedded clauses)
            if 'stay' in vp.text or 'rain' in vp.text:
                self.assertTrue('subj' in child_labels or 'nsubj' in child_labels,
                              f"Main verb phrase '{vp.text}' should have subject")
    
    def test_verb_phrase_contains_all_arguments(self):
        """Test that verb phrases contain all their arguments."""
        analysis = self.analyzer.analyze_sentence("The teacher gave the students homework.")
        
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        self.assertGreater(len(verb_phrases), 0, "Should have verb phrase")
        
        vp = verb_phrases[0]
        child_texts = ' '.join(self.get_child_texts(vp)).lower()
        
        # All arguments should be represented in the verb phrase
        self.assertIn('teacher', child_texts, "Subject should be in verb phrase")
        self.assertIn('gave', child_texts, "Verb should be in verb phrase")
        self.assertIn('students', child_texts, "Indirect object should be in verb phrase")
        self.assertIn('homework', child_texts, "Direct object should be in verb phrase")
    
    def test_quoted_speech(self):
        """Test handling of quoted speech with complex internal structure."""
        analysis = self.analyzer.analyze_sentence('He said "stop hitting me you bastard."')
        
        # Find verb phrases
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        # Should have at least the main verb "said"
        self.assertGreater(len(verb_phrases), 0, "Should have verb phrases")
        
        # Find the "said" verb phrase
        said_vp = None
        for vp in verb_phrases:
            if 'said' in vp.text:
                said_vp = vp
                break
        
        self.assertIsNotNone(said_vp, "Should find 'said' verb phrase")
        
        # Check structure of "said" verb phrase
        child_labels = self.get_child_edge_labels(said_vp)
        self.assertIn('subj', child_labels, "Should have subject 'He'")
        self.assertIn('verb_head', child_labels, "Should have verb 'said'")
        
        # With new structure, quote is separate at root level
        # Find quote node at root level
        quote_nodes = [child for child in analysis.syntactic_tree.children 
                      if child.node_type == 'quote']
        self.assertEqual(len(quote_nodes), 1, "Should have quote node at root level")
        
        quote = quote_nodes[0]
        # The quoted speech should contain "stop"
        self.assertIn('stop', quote.text.lower(), "Quote should contain 'stop'")
        self.assertIn('hitting', quote.text.lower(), "Quote should contain 'hitting'")
        self.assertIn('bastard', quote.text.lower(), "Quote should contain 'bastard'")
    
    def test_quoted_speech_exact_structure(self):
        """Test exact tree structure for quoted speech with imperative and vocative."""
        # Test without comma
        analysis = self.analyzer.analyze_sentence('He said "stop hitting me you bastard."')
        
        # Navigate to the exact structure
        root = analysis.syntactic_tree
        self.assertEqual(root.node_type, 'sentence', "Root should be sentence")
        
        # With new structure, find the main verb phrase and quote separately
        main_vp = None
        quote_node = None
        for child in root.children:
            if child.edge_label == 'tverb' and 'said' in child.text:
                main_vp = child
            elif child.node_type == 'quote':
                quote_node = child
        
        self.assertIsNotNone(main_vp, "Should have main verb phrase")
        self.assertIsNotNone(quote_node, "Should have quote node")
        self.assertEqual(main_vp.node_type, 'phrase', "Main VP should be phrase")
        
        # Check main VP has correct children
        main_vp_children = {child.edge_label: child for child in main_vp.children}
        self.assertIn('subj', main_vp_children, "Main VP should have subject")
        self.assertIn('verb_head', main_vp_children, "Main VP should have verb_head")
        
        # Check the quoted speech structure
        self.assertEqual(quote_node.node_type, 'quote', "Should be quote node")
        self.assertIn('stop hitting me', quote_node.text, 
                     "Quote should contain main content")
        
        # Check internal structure of quote
        # With vocatives, the structure might be different
        # The quote should have some internal structure - either main clause or other elements
        self.assertGreater(len(quote_node.children), 2, 
                          "Quote should have internal structure beyond just punctuation")
    
    def test_quoted_speech_with_comma(self):
        """Test quoted speech with comma before vocative."""
        analysis = self.analyzer.analyze_sentence('He said "stop hitting me, you bastard."')
        
        # Navigate to the quoted speech
        root = analysis.syntactic_tree
        main_vp = None
        quote_node = None
        for child in root.children:
            if child.edge_label == 'tverb' and 'said' in child.text:
                main_vp = child
            elif child.node_type == 'quote':
                quote_node = child
        
        self.assertIsNotNone(main_vp, "Should have main verb phrase")
        self.assertIsNotNone(quote_node, "Should have quote node")
        
        # The quoted speech should contain all the words
        self.assertIn('stop', quote_node.text, "Should contain 'stop'")
        self.assertIn('hitting', quote_node.text, "Should contain 'hitting'")
        self.assertIn('me', quote_node.text, "Should contain 'me'")
        self.assertIn('you', quote_node.text, "Should contain 'you'")
        self.assertIn('bastard', quote_node.text, "Should contain 'bastard'")
        
        # Check that it has proper internal structure with vocative
        # Find vocative within quote
        vocatives = []
        for child in quote_node.children:
            if child.edge_label == 'vocative':
                vocatives.append(child)
        
        self.assertGreater(len(vocatives), 0, "Quote should have vocative")
        
        vocative = vocatives[0]
        self.assertEqual(vocative.text, ', you bastard .', "Vocative should be ', you bastard .'")
        
        # Should also have main clause with the verb content
        main_clauses = [child for child in quote_node.children 
                        if child.edge_label == 'main_clause']
        self.assertGreater(len(main_clauses), 0, "Quote should have main clause")
        
        main_clause = main_clauses[0]
        self.assertIn('stop', main_clause.text, "Main clause should contain 'stop'")
        self.assertIn('hitting', main_clause.text, "Main clause should contain 'hitting'")
        self.assertIn('me', main_clause.text, "Main clause should contain 'me'")
    
    def test_syntactic_tree_has_hierarchical_structure(self):
        """Test that the syntactic tree has proper hierarchical structure."""
        analysis = self.analyzer.analyze_sentence("The quick brown fox jumps over the lazy dog.")
        
        # Should have a root node
        self.assertIsNotNone(analysis.syntactic_tree, "Should have syntactic tree")
        
        # Root should be sentence type
        self.assertEqual(analysis.syntactic_tree.node_type, 'sentence', 
                        "Root should be sentence node")
        
        # Should have hierarchical structure with phrases
        phrases = self.find_nodes_by_type(analysis.syntactic_tree, 'phrase')
        self.assertGreater(len(phrases), 0, "Should have phrase nodes")
        
        # Should have verb phrase
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        self.assertGreater(len(verb_phrases), 0, "Should have verb phrase")
    
    def test_adverb_placement_above_verb_phrase(self):
        """Test that adverbs modifying verbs are placed at clause level, not in verb phrase."""
        analysis = self.analyzer.analyze_sentence("I gleefully gave my friend a gift.")
        
        # Find the verb phrase
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        vp_with_subject = None
        for vp in verb_phrases:
            child_labels = self.get_child_edge_labels(vp)
            if 'subj' in child_labels:
                vp_with_subject = vp
                break
        
        self.assertIsNotNone(vp_with_subject, "Should find verb phrase with subject")
        
        # The verb phrase text should NOT include "gleefully"
        self.assertNotIn('gleefully', vp_with_subject.text.lower(), 
                        "Verb phrase should not contain the adverb")
        
        # Find the parent of the verb phrase (should be clause or sentence)
        parent = vp_with_subject.parent
        self.assertIsNotNone(parent, "Verb phrase should have a parent")
        
        # The parent should have the adverb as a separate child
        adverb_found = False
        for child in parent.children:
            if child.node_type == 'word' and child.text.lower() == 'gleefully':
                adverb_found = True
                self.assertEqual(child.edge_label, 'adv_mod', 
                               "Adverb should have 'adv_mod' edge label")
                break
        
        self.assertTrue(adverb_found, "Adverb should be a sibling of verb phrase at clause level")
    
    def test_modal_auxiliary_verbs(self):
        """Test that modal auxiliary verbs (will, would, can, etc.) are grouped with main verb."""
        analysis = self.analyzer.analyze_sentence("I will burn this house to the ground.")
        
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        self.assertGreater(len(verb_phrases), 0, 
                          "Should have verb phrase with modal auxiliary")
        
        # Find the main verb phrase
        main_vp = None
        for vp in verb_phrases:
            if 'burn' in vp.text:
                main_vp = vp
                break
        
        self.assertIsNotNone(main_vp, "Should find verb phrase containing 'burn'")
        
        # Check that there's a sub-phrase containing "will burn"
        modal_verb_phrase_found = False
        for child in main_vp.children:
            if (child.node_type == 'phrase' and 
                'will' in child.text.lower() and 
                'burn' in child.text.lower()):
                modal_verb_phrase_found = True
                
                # Check structure of modal+verb phrase
                child_labels = self.get_child_edge_labels(child)
                self.assertIn('aux', child_labels, "Should have auxiliary")
                self.assertIn('verb_head', child_labels, "Should have verb head")
                
                # Verify specific children
                has_will = any(c.text.lower() == 'will' and c.edge_label == 'aux' 
                              for c in child.children)
                has_burn = any(c.text.lower() == 'burn' and c.edge_label == 'verb_head' 
                              for c in child.children)
                
                self.assertTrue(has_will, "Should have 'will' as aux child")
                self.assertTrue(has_burn, "Should have 'burn' as verb_head child")
                break
        
        self.assertTrue(modal_verb_phrase_found, 
                       "Modal auxiliary 'will' should be grouped with verb 'burn' in a phrase")
    
    def test_phrasal_verb_run_over(self):
        """Test that 'run over' is recognized as a phrasal verb, not verb + prepositional phrase."""
        analysis = self.analyzer.analyze_sentence("I ran over my friend.")
        
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        self.assertGreater(len(verb_phrases), 0, "Should have verb phrase")
        
        # Check for phrasal verb structure
        phrasal_verb_found = False
        for vp in verb_phrases:
            # Look for a phrase node containing "ran over"
            for child in vp.children:
                if (child.node_type == 'phrase' and 
                    'ran' in child.text.lower() and 
                    'over' in child.text.lower()):
                    phrasal_verb_found = True
                    # Check that it has both verb and particle as children
                    child_labels = self.get_child_edge_labels(child)
                    self.assertIn('verb_head', child_labels, 
                                 "Phrasal verb should have verb_head")
                    self.assertIn('particle', child_labels, 
                                 "Phrasal verb should have particle")
                    break
            
            if phrasal_verb_found:
                break
        
        self.assertTrue(phrasal_verb_found, 
                       "'ran over' should be recognized as a phrasal verb")
    
    def test_infinitive_clause_with_want(self):
        """Test that infinitive clauses are properly recognized as complements with full structure."""
        analysis = self.analyzer.analyze_sentence("I want to burn this house to the ground.")
        
        # Find verb phrases
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        
        # Should have at least 2 verb phrases: one for "want" and one for "to burn"
        self.assertGreaterEqual(len(verb_phrases), 2, 
                               "Should have verb phrases for both 'want' and 'to burn'")
        
        # Find the "want" verb phrase
        want_vp = None
        for vp in verb_phrases:
            if 'want' in vp.text and 'I want' in vp.text:
                want_vp = vp
                break
        
        self.assertIsNotNone(want_vp, "Should find verb phrase containing 'want'")
        
        # The "want" phrase should NOT include "I want ." as a single phrase
        # Instead, it should have subject and verb as separate elements
        self.assertNotEqual(want_vp.text.strip(), "I want .", 
                           "Verb phrase should not be just 'I want .'")
        
        # Should have an infinitive complement
        infinitive_clause = None
        for child in want_vp.children:
            if (child.node_type == 'phrase' and 
                'to burn' in child.text.lower()):
                infinitive_clause = child
                self.assertIn('obj', child.edge_label, 
                             "Infinitive should be object/complement, not prepositional phrase")
                break
        
        self.assertIsNotNone(infinitive_clause, 
                            "Should have infinitive clause as complement of 'want'")
        
        # Check the internal structure of the infinitive clause
        # It should directly contain the verb components, not wrap another phrase
        inf_child_labels = self.get_child_edge_labels(infinitive_clause)
        
        # Should have aux, verb_head, obj, and prep_phrase as direct children
        self.assertIn('aux', inf_child_labels, "Should have auxiliary 'to'")
        self.assertIn('verb_head', inf_child_labels, "Should have verb head 'burn'")
        self.assertIn('obj', inf_child_labels, "Should have object")
        self.assertIn('prep_phrase', inf_child_labels, "Should have prepositional phrase")
        
        # Verify it doesn't have a redundant verb phrase child
        for child in infinitive_clause.children:
            if child.node_type == 'phrase' and child.edge_label == 'verb':
                self.assertNotEqual(child.text, infinitive_clause.text,
                                   "Should not have a verb phrase child with the same text")
        
        # Check specific components
        has_to = any(child.text == 'to' and child.edge_label == 'aux' 
                     for child in infinitive_clause.children)
        has_burn = any(child.text == 'burn' and child.edge_label == 'verb_head' 
                      for child in infinitive_clause.children)
        
        self.assertTrue(has_to, "Should have 'to' as auxiliary")
        self.assertTrue(has_burn, "Should have 'burn' as verb head")
    
    def test_infinitive_clause_with_profanity(self):
        """Test infinitive clause with emphatic adjective."""
        analysis = self.analyzer.analyze_sentence("I want to burn this house to the fucking ground.")
        
        # Find the main verb phrase
        verb_phrases = self.find_verb_phrases(analysis.syntactic_tree)
        want_vp = None
        for vp in verb_phrases:
            if 'want' in vp.text and 'I want' in vp.text:
                want_vp = vp
                break
        
        self.assertIsNotNone(want_vp, "Should find 'want' verb phrase")
        
        # Find the infinitive clause
        infinitive_clause = None
        for child in want_vp.children:
            if child.node_type == 'phrase' and 'to burn' in child.text.lower():
                infinitive_clause = child
                break
        
        self.assertIsNotNone(infinitive_clause, "Should find infinitive clause")
        
        # Should have proper internal structure
        # The infinitive clause should directly contain the components
        inf_child_labels = self.get_child_edge_labels(infinitive_clause)
        
        # Should have the components as direct children
        self.assertIn('aux', inf_child_labels, "Should have auxiliary 'to'")
        self.assertIn('verb_head', inf_child_labels, "Should have verb head")
        self.assertIn('obj', inf_child_labels, "Should have object")
        self.assertIn('prep_phrase', inf_child_labels, "Should have prepositional phrase")
        
        # Verify the text contains all components
        self.assertIn('fucking', infinitive_clause.text, 
                     "Infinitive clause should contain all words including emphatic adjective")


if __name__ == '__main__':
    unittest.main() 