"""
Comprehensive test suite for the sentence parser.

Tests various aspects of the modular sentence parsing system including:
- Basic sentence structures
- Complex sentences with multiple clauses
- Phrasal verbs
- Noun phrases
- Prepositional phrases
- Tree structure integrity
- Lemma decomposition
"""

import pytest
from src.services.tree_adapter import SentenceAnalyzerAdapter as SentenceAnalyzer
from src.services.syntactic_tree import SyntacticNode


class TestSentenceParser:
    """Test suite for sentence parser functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a sentence analyzer instance."""
        return SentenceAnalyzer()
    
    def verify_tree_structure(self, node, visited=None):
        """Verify the tree is well-formed without cycles."""
        if visited is None:
            visited = set()
        
        # Check for cycles
        node_id = id(node)
        assert node_id not in visited, f"Cycle detected at node '{node.text}'"
        visited.add(node_id)
        
        # Check parent-child consistency
        for child in node.children:
            assert child.parent == node, f"Child '{child.text}' has incorrect parent reference"
            assert child.edge_label is not None, f"Child '{child.text}' missing edge label"
            
            # Recursive check
            self.verify_tree_structure(child, visited.copy())
        
        # Check for duplicate children
        child_ids = [id(child) for child in node.children]
        assert len(child_ids) == len(set(child_ids)), f"Duplicate children in node '{node.text}'"
    
    def count_nodes_by_type(self, node, node_types=None):
        """Count nodes by type in the tree."""
        if node_types is None:
            node_types = {}
        
        node_type = node.node_type
        node_types[node_type] = node_types.get(node_type, 0) + 1
        
        for child in node.children:
            self.count_nodes_by_type(child, node_types)
        
        return node_types
    
    def find_nodes_by_text(self, node, text, found=None):
        """Find all nodes with specific text."""
        if found is None:
            found = []
        
        if node.text.lower() == text.lower():
            found.append(node)
        
        for child in node.children:
            self.find_nodes_by_text(child, text, found)
        
        return found
    
    # Basic sentence structure tests
    
    def test_simple_sentence(self, analyzer):
        """Test basic subject-verb-object sentence."""
        analysis = analyzer.analyze_sentence("The cat eats fish.")
        
        # Verify tree structure
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Check node types
        node_types = self.count_nodes_by_type(analysis.syntactic_tree)
        assert node_types['sentence'] == 1
        assert 'word' in node_types
        assert 'phrase' in node_types  # Should have noun phrases
    
    def test_sentence_with_adjectives(self, analyzer):
        """Test sentence with adjective modifiers."""
        analysis = analyzer.analyze_sentence("The big brown dog chases the small cat.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Find noun phrases
        dog_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "the big brown dog")
        assert len(dog_nodes) > 0, "Should find 'the big brown dog' phrase"
        
        cat_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "the small cat")
        assert len(cat_nodes) > 0, "Should find 'the small cat' phrase"
    
    def test_sentence_with_adverbs(self, analyzer):
        """Test sentence with adverbs."""
        analysis = analyzer.analyze_sentence("She quickly ran to the store.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Find adverb
        quickly_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "quickly")
        assert len(quickly_nodes) > 0, "Should find 'quickly' adverb"
    
    # Complex sentence tests
    
    def test_compound_sentence(self, analyzer):
        """Test compound sentence with conjunction."""
        analysis = analyzer.analyze_sentence("I like coffee, but she prefers tea.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should have multiple clauses
        node_types = self.count_nodes_by_type(analysis.syntactic_tree)
        assert node_types.get('clause', 0) >= 2, "Should have at least 2 clauses"
    
    def test_complex_sentence_with_subordinate_clause(self, analyzer):
        """Test complex sentence with subordinate clause."""
        analysis = analyzer.analyze_sentence("I will go to the store if it stops raining.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should find conjunction
        if_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "if")
        assert len(if_nodes) > 0, "Should find 'if' conjunction"
    
    def test_problematic_sentence(self, analyzer):
        """Test the specific problematic sentence mentioned by user."""
        sentence = "I would like to run the world someday, but only if my 401k goes up."
        analysis = analyzer.analyze_sentence(sentence)
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Check that all expected tokens are present
        expected_words = ["I", "would", "like", "to", "run", "the", "world", 
                         "someday", "but", "only", "if", "my", "401k", "goes", "up"]
        
        for word in expected_words:
            nodes = self.find_nodes_by_text(analysis.syntactic_tree, word)
            assert len(nodes) > 0, f"Should find '{word}' in tree"
    
    # Phrasal verb tests
    
    def test_phrasal_verb_simple(self, analyzer):
        """Test simple phrasal verb."""
        analysis = analyzer.analyze_sentence("She looked up the word.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should identify "looked up" as phrasal verb
        looked_up_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "looked up")
        assert len(looked_up_nodes) > 0, "Should identify 'looked up' as phrasal verb"
    
    def test_phrasal_verb_complex(self, analyzer):
        """Test phrasal verb in complex context."""
        analysis = analyzer.analyze_sentence("I ran over my friend with a scooter.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should identify "ran over" as phrasal verb
        ran_over_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "ran over")
        assert len(ran_over_nodes) > 0, "Should identify 'ran over' as phrasal verb"
    
    # Prepositional phrase tests
    
    def test_prepositional_phrases(self, analyzer):
        """Test sentence with multiple prepositional phrases."""
        analysis = analyzer.analyze_sentence("The book on the table in the room is mine.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should have prepositional phrases
        on_table_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "on the table")
        in_room_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "in the room")
        
        assert len(on_table_nodes) > 0 or any("on" in n.text and "table" in n.text 
                                               for n in analysis.syntactic_tree.children), \
               "Should have 'on the table' phrase structure"
    
    def test_nested_prepositional_phrases(self, analyzer):
        """Test nested prepositional phrases."""
        analysis = analyzer.analyze_sentence("The man with the hat on his head walked by.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
    
    # Noun phrase tests
    
    def test_complex_noun_phrase(self, analyzer):
        """Test complex noun phrase with multiple modifiers."""
        analysis = analyzer.analyze_sentence("The three small brown wooden boxes fell.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should create hierarchical noun phrase
        boxes_phrases = [n for n in self._get_all_nodes(analysis.syntactic_tree) 
                        if "boxes" in n.text and n.node_type == 'phrase']
        assert len(boxes_phrases) > 0, "Should have phrase containing 'boxes'"
    
    def test_possessive_noun_phrase(self, analyzer):
        """Test possessive noun phrases."""
        analysis = analyzer.analyze_sentence("John's mother's car is red.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should handle possessives correctly
        assert any("John" in n.text for n in self._get_all_nodes(analysis.syntactic_tree))
    
    # Lemma decomposition tests
    
    def test_lemma_decomposition_verbs(self, analyzer):
        """Test lemma decomposition for verbs."""
        analysis = analyzer.analyze_sentence("She runs quickly.", decompose_lemmas=True)
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should decompose "runs" to "run"
        run_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "run")
        assert len(run_nodes) > 0, "Should decompose 'runs' to 'run'"
        
        # Check for grammatical label
        runs_parent = self._find_parent_of_text(analysis.syntactic_tree, "run")
        if runs_parent:
            assert any(child.edge_label == 'present_3sg' for child in runs_parent.children), \
                   "Should have present_3sg edge label"
    
    def test_lemma_decomposition_nouns(self, analyzer):
        """Test lemma decomposition for plural nouns."""
        analysis = analyzer.analyze_sentence("The dogs were barking.", decompose_lemmas=True)
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should decompose "dogs" to "dog"
        dog_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "dog")
        assert len(dog_nodes) > 0, "Should decompose 'dogs' to 'dog'"
        
        # Should decompose "barking" to "bark"
        bark_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "bark")
        assert len(bark_nodes) > 0, "Should decompose 'barking' to 'bark'"
    
    def test_lemma_decomposition_no_particles(self, analyzer):
        """Test that particles like 'to' are not decomposed."""
        analysis = analyzer.analyze_sentence("I want to run quickly.", decompose_lemmas=True)
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # "to" should not be decomposed
        to_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "to")
        assert len(to_nodes) > 0, "Should find 'to' in tree"
        
        # Make sure "to" doesn't have children (not decomposed)
        for to_node in to_nodes:
            if to_node.node_type == 'word':
                assert len(to_node.children) == 0, "'to' should not be decomposed"
    
    def test_lemma_decomposition_comparatives(self, analyzer):
        """Test lemma decomposition for comparatives and superlatives."""
        analysis = analyzer.analyze_sentence("This is better than the best option.", 
                                           decompose_lemmas=True)
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should decompose "better" to "well" or "good"
        # Should decompose "best" to "well" or "good"
        good_well_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "well") + \
                         self.find_nodes_by_text(analysis.syntactic_tree, "good")
        assert len(good_well_nodes) > 0, "Should decompose comparatives/superlatives"
    
    # Edge case tests
    
    def test_sentence_with_numbers(self, analyzer):
        """Test sentence with numbers like 401k."""
        analysis = analyzer.analyze_sentence("My 401k account has grown by 10 percent.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should handle "401k" correctly
        fourohone_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "401k")
        assert len(fourohone_nodes) > 0, "Should handle '401k' correctly"
    
    def test_sentence_with_contractions(self, analyzer):
        """Test sentence with contractions."""
        analysis = analyzer.analyze_sentence("I'd like to go, but I can't.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should handle contractions
        assert any("'" in n.text for n in self._get_all_nodes(analysis.syntactic_tree))
    
    def test_sentence_with_punctuation(self, analyzer):
        """Test sentence with various punctuation."""
        analysis = analyzer.analyze_sentence("Well, I think - no, I know - it's true!")
        
        self.verify_tree_structure(analysis.syntactic_tree)
    
    def test_infinitive_phrases(self, analyzer):
        """Test infinitive phrases."""
        analysis = analyzer.analyze_sentence("I want to learn to play the piano.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should handle multiple "to" infinitives correctly
        to_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "to")
        assert len(to_nodes) >= 2, "Should find multiple 'to' infinitives"
    
    def test_relative_clauses(self, analyzer):
        """Test relative clauses."""
        analysis = analyzer.analyze_sentence("The man who sold the world is here.")
        
        self.verify_tree_structure(analysis.syntactic_tree)
        
        # Should handle relative clause with "who"
        who_nodes = self.find_nodes_by_text(analysis.syntactic_tree, "who")
        assert len(who_nodes) > 0, "Should find relative pronoun 'who'"
    
    # Helper methods
    
    def _get_all_nodes(self, node, nodes=None):
        """Get all nodes in the tree."""
        if nodes is None:
            nodes = []
        
        nodes.append(node)
        for child in node.children:
            self._get_all_nodes(child, nodes)
        
        return nodes
    
    def _find_parent_of_text(self, node, text):
        """Find the parent node of a node with specific text."""
        for child in node.children:
            if child.text.lower() == text.lower():
                return node
            
            result = self._find_parent_of_text(child, text)
            if result:
                return result
        
        return None 