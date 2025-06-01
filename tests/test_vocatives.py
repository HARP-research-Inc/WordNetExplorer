"""Test suite for vocative parsing."""

import unittest
from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2
from src.services.syntactic_tree import SyntacticNode


class TestVocatives(unittest.TestCase):
    """Test vocative identification and parsing."""
    
    def setUp(self):
        """Create analyzer instance for tests."""
        self.analyzer = SentenceAnalyzerV2()
    
    def find_vocatives(self, node):
        """Find all vocative nodes in the tree."""
        vocatives = []
        
        if node.edge_label == 'vocative':
            vocatives.append(node)
        
        for child in node.children:
            vocatives.extend(self.find_vocatives(child))
        
        return vocatives
    
    def test_end_vocative_with_comma(self):
        """Test vocative at end of sentence after comma."""
        analysis = self.analyzer.analyze_sentence("I gave you a scooter to ride with, you ungrateful jerk.")
        
        # Should have vocative as top-level clause
        top_level_children = analysis.syntactic_tree.children
        vocative_nodes = [child for child in top_level_children if child.edge_label == 'vocative']
        
        self.assertEqual(len(vocative_nodes), 1, "Should have one vocative at top level")
        
        vocative = vocative_nodes[0]
        self.assertEqual(vocative.text, ", you ungrateful jerk .", "Vocative should include comma and punctuation")
        
        # Check internal structure
        self.assertGreater(len(vocative.children), 2, "Vocative should have internal structure")
        
        # Should have main clause without vocative
        main_clauses = [child for child in top_level_children if child.edge_label == 'main_clause']
        self.assertEqual(len(main_clauses), 1, "Should have main clause")
        self.assertNotIn("jerk", main_clauses[0].text, "Main clause should not contain vocative")
    
    def test_beginning_vocative_with_name(self):
        """Test vocative at beginning with proper name."""
        analysis = self.analyzer.analyze_sentence("John, please help me.")
        
        vocatives = self.find_vocatives(analysis.syntactic_tree)
        self.assertEqual(len(vocatives), 1, "Should have one vocative")
        
        vocative = vocatives[0]
        self.assertIn("John", vocative.text, "Vocative should contain name")
        self.assertIn(",", vocative.text, "Vocative should include comma")
    
    def test_vocative_in_quoted_speech(self):
        """Test vocative within quoted speech remains inside quote."""
        analysis = self.analyzer.analyze_sentence('He said "stop hitting me, you bastard."')
        
        # Find quote node
        quote_nodes = []
        for child in analysis.syntactic_tree.children:
            if child.node_type == 'quote':
                quote_nodes.append(child)
        
        self.assertEqual(len(quote_nodes), 1, "Should have one quote node")
        
        # Check vocative is inside quote
        quote = quote_nodes[0]
        vocatives_in_quote = self.find_vocatives(quote)
        
        self.assertGreater(len(vocatives_in_quote), 0, "Should have vocative inside quote")
        
        vocative = vocatives_in_quote[0]
        self.assertIn("you bastard", vocative.text, "Vocative should contain 'you bastard'")
    
    def test_vocative_with_adjectives(self):
        """Test vocative with adjective modifiers."""
        analysis = self.analyzer.analyze_sentence("Stop that immediately, young man!")
        
        vocatives = self.find_vocatives(analysis.syntactic_tree)
        self.assertGreater(len(vocatives), 0, "Should detect 'young man' as vocative")
        
        vocative = vocatives[0]
        self.assertIn("young man", vocative.text, "Vocative should contain 'young man'")
    
    def test_vocative_internal_structure(self):
        """Test that vocatives have proper internal parsing."""
        analysis = self.analyzer.analyze_sentence("Come here, you silly little boy.")
        
        vocatives = self.find_vocatives(analysis.syntactic_tree)
        self.assertGreater(len(vocatives), 0, "Should detect vocative")
        
        vocative = vocatives[0]
        
        # Check that vocative has internal structure
        word_nodes = [child for child in vocative.children if child.node_type == 'word']
        self.assertGreater(len(word_nodes), 2, "Vocative should have multiple word nodes")
        
        # Should have noun phrase structure for complex vocatives
        has_np = any(child.edge_label == 'np' for child in vocative.children)
        if len(word_nodes) > 2:
            self.assertTrue(has_np, "Complex vocative should have noun phrase structure")
    
    def test_no_false_positive_vocatives(self):
        """Test that regular comma-separated phrases aren't mistaken for vocatives."""
        analysis = self.analyzer.analyze_sentence("I went to the store, bought some milk, and came home.")
        
        vocatives = self.find_vocatives(analysis.syntactic_tree)
        self.assertEqual(len(vocatives), 0, "Should not detect false vocatives in lists")
    
    def test_vocative_with_pronoun_noun(self):
        """Test vocative pattern like 'you fool'."""
        analysis = self.analyzer.analyze_sentence("You fool, I told you not to do that.")
        
        vocatives = self.find_vocatives(analysis.syntactic_tree)
        self.assertEqual(len(vocatives), 1, "Should detect 'You fool' as vocative")
        
        vocative = vocatives[0]
        self.assertIn("You fool", vocative.text, "Vocative should be 'You fool'")
        
        # Check structure
        det_nodes = [child for child in vocative.children if child.edge_label == 'det']
        head_nodes = [child for child in vocative.children if child.edge_label == 'head']
        
        self.assertEqual(len(det_nodes), 1, "Should have determiner")
        self.assertEqual(len(head_nodes), 1, "Should have head noun")
    
    def test_multiple_vocatives(self):
        """Test handling of multiple vocatives."""
        # This is a known limitation - multiple vocatives at beginning need work
        analysis = self.analyzer.analyze_sentence("John, Mary, please come here.")
        
        # For now, just ensure it doesn't crash
        vocatives = self.find_vocatives(analysis.syntactic_tree)
        self.assertGreaterEqual(len(vocatives), 1, "Should detect at least one vocative")


if __name__ == '__main__':
    unittest.main() 