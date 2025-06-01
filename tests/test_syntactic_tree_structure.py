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
        
        # Should have auxiliary verbs as children or within the structure
        aux_count = sum(1 for label in child_labels if 'aux' in label)
        self.assertGreaterEqual(aux_count, 1, 
                               "Should have auxiliary verbs in verb phrase")
    
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


if __name__ == '__main__':
    unittest.main() 