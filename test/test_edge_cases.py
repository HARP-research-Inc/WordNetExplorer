"""
Test suite for edge cases and problematic sentences.

Tests sentences that have been known to cause issues or that
contain unusual constructions.
"""

import pytest
from src.services.tree_adapter import SentenceAnalyzerAdapter as SentenceAnalyzer


class TestEdgeCases:
    """Test suite for edge cases and problematic sentences."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a sentence analyzer instance."""
        return SentenceAnalyzer()
    
    def verify_no_errors(self, analyzer, sentence):
        """Verify sentence parses without errors and has valid structure."""
        try:
            analysis = analyzer.analyze_sentence(sentence)
            
            # Basic checks
            assert analysis is not None
            assert analysis.syntactic_tree is not None
            assert len(analysis.tokens) > 0
            
            # Verify tree structure
            self._verify_tree(analysis.syntactic_tree)
            
            return analysis
        except Exception as e:
            pytest.fail(f"Failed to parse sentence: '{sentence}'. Error: {str(e)}")
    
    def _verify_tree(self, node, visited=None):
        """Basic tree verification."""
        if visited is None:
            visited = set()
        
        if id(node) in visited:
            raise AssertionError("Cycle detected in tree")
        
        visited.add(id(node))
        
        for child in node.children:
            assert child.parent == node
            self._verify_tree(child, visited.copy())
    
    # Specific problematic sentences
    
    def test_401k_sentence(self, analyzer):
        """Test the specific sentence mentioned with 401k."""
        sentence = "I would like to run the world someday, but only if my 401k goes up."
        analysis = self.verify_no_errors(analyzer, sentence)
        
        # Verify all words are present
        words = [t.text for t in analysis.tokens]
        assert "401k" in words
        assert "would" in words
        assert "someday" in words
    
    def test_multiple_infinitives(self, analyzer):
        """Test sentences with multiple infinitive constructions."""
        sentences = [
            "I want to learn to speak Spanish fluently.",
            "She needs to remember to bring the documents.",
            "They decided to try to fix it themselves.",
            "He promised to help me to understand the problem."
        ]
        
        for sentence in sentences:
            analysis = self.verify_no_errors(analyzer, sentence)
            
            # Count "to" instances
            to_count = sum(1 for t in analysis.tokens if t.text.lower() == "to")
            assert to_count >= 2, f"Should have multiple 'to' in: {sentence}"
    
    def test_complex_punctuation(self, analyzer):
        """Test sentences with complex punctuation."""
        sentences = [
            "Well, I thought—no, I knew—it was wrong!",
            "The items (all of them, in fact) were damaged.",
            "She said, 'I'll be there'; however, she didn't show up.",
            "What?! You can't be serious!"
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_contractions_and_possessives(self, analyzer):
        """Test various contractions and possessives."""
        sentences = [
            "I'd've gone if I'd known you'd be there.",
            "It's been a while since it's shown its true colors.",
            "They're sure their friends'll be there.",
            "Who's seen whose book?"
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_numbers_and_symbols(self, analyzer):
        """Test sentences with numbers and symbols."""
        sentences = [
            "My 401k increased by 15% last year.",
            "The temperature is -5°C today.",
            "Email me at john@example.com by 3:30 PM.",
            "The product costs $19.99 + tax.",
            "She scored 98/100 on the test."
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_ambiguous_word_roles(self, analyzer):
        """Test words that can be multiple parts of speech."""
        sentences = [
            "The can can can things.",  # can as noun, modal, and verb
            "Time flies like an arrow; fruit flies like a banana.",
            "Buffalo buffalo Buffalo buffalo buffalo buffalo Buffalo buffalo.",
            "Rose rose to put rose roes on her rows of roses."
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_nested_structures(self, analyzer):
        """Test deeply nested grammatical structures."""
        sentences = [
            "The man who said that the woman who lives in the house that Jack built is nice is here.",
            "I know that you know that I know that you're lying.",
            "The book that the student who the teacher who the principal hired taught read was interesting."
        ]
        
        for sentence in sentences:
            analysis = self.verify_no_errors(analyzer, sentence)
            
            # Should create nested clause structures
            assert any(n.node_type == 'clause' for n in self._get_all_nodes(analysis.syntactic_tree))
    
    def test_ellipsis_and_fragments(self, analyzer):
        """Test sentences with ellipsis and fragments."""
        sentences = [
            "Going to the store. Be back soon.",
            "Coffee? Yes, please.",
            "The more, the merrier.",
            "So tired... Must sleep...",
            "Him? Never!"
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_questions(self, analyzer):
        """Test various question forms."""
        sentences = [
            "What did you say?",
            "Who's going to the party tonight?",
            "Where did you put the keys that I gave you yesterday?",
            "Why would anyone do such a thing?",
            "How many times do I have to tell you?"
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_imperatives(self, analyzer):
        """Test imperative sentences."""
        sentences = [
            "Go to the store.",
            "Please sit down and be quiet.",
            "Don't forget to lock the door!",
            "Let's try to finish this today.",
            "Just do it!"
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_quoted_speech(self, analyzer):
        """Test sentences with quoted speech."""
        sentences = [
            'She said, "I will be there soon."',
            '"Why," he asked, "would you do that?"',
            'The sign read "No Parking" in big red letters.',
            "'I don't know,' she replied quietly."
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_lists_and_coordination(self, analyzer):
        """Test sentences with lists and complex coordination."""
        sentences = [
            "I need eggs, milk, bread, and butter.",
            "She can sing, dance, play piano, and speak three languages.",
            "Either you or I will have to go, but not both.",
            "I like coffee and tea, but not juice or soda."
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_comparative_constructions(self, analyzer):
        """Test comparative and superlative constructions."""
        sentences = [
            "She runs faster than her brother.",
            "This is the best day ever!",
            "The more you practice, the better you get.",
            "He's as tall as, if not taller than, his father."
        ]
        
        for sentence in sentences:
            self.verify_no_errors(analyzer, sentence)
    
    def test_with_lemma_decomposition(self, analyzer):
        """Test edge cases with lemma decomposition enabled."""
        sentences = [
            "The geese were flying south.",  # geese -> goose
            "The children's toys were scattered.",  # children -> child
            "He does what he's told.",  # does -> do, 's -> is
            "The oxen were grazing peacefully."  # oxen -> ox
        ]
        
        for sentence in sentences:
            analysis = self.verify_no_errors(analyzer, sentence)
            
            # Also test with lemma decomposition
            analysis_lemma = analyzer.analyze_sentence(sentence, decompose_lemmas=True)
            self._verify_tree(analysis_lemma.syntactic_tree)
    
    # Helper methods
    
    def _get_all_nodes(self, node, nodes=None):
        """Get all nodes in the tree."""
        if nodes is None:
            nodes = []
        
        nodes.append(node)
        for child in node.children:
            self._get_all_nodes(child, nodes)
        
        return nodes 