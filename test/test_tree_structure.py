"""
Test suite specifically for syntactic tree structure integrity.

Focuses on ensuring the tree remains a proper tree structure without:
- Cycles
- Duplicate edges
- Incorrect parent references
- Orphaned nodes
"""

import pytest
from src.services.sentence_analyzer_v3 import SentenceAnalyzer
from src.services.syntactic_tree import SyntacticNode


class TestTreeStructure:
    """Test suite for tree structure integrity."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a sentence analyzer instance."""
        return SentenceAnalyzer()
    
    def check_tree_invariants(self, root):
        """
        Check all tree invariants:
        1. No cycles
        2. Every child has correct parent reference
        3. No duplicate children
        4. All nodes reachable from root
        5. Edge labels are present
        """
        # Track all nodes and their relationships
        all_nodes = set()
        parent_child_pairs = set()
        
        def collect_nodes(node, path=None):
            if path is None:
                path = []
            
            # Check for cycles
            if id(node) in [id(n) for n in path]:
                raise AssertionError(f"Cycle detected: {[n.text for n in path + [node]]}")
            
            all_nodes.add(id(node))
            path.append(node)
            
            # Check children
            child_ids = []
            for child in node.children:
                # Check for duplicate children
                if id(child) in child_ids:
                    raise AssertionError(f"Duplicate child '{child.text}' in node '{node.text}'")
                child_ids.append(id(child))
                
                # Check parent reference
                if child.parent is not node:
                    raise AssertionError(
                        f"Child '{child.text}' has incorrect parent. "
                        f"Expected '{node.text}', got '{child.parent.text if child.parent else None}'"
                    )
                
                # Check edge label
                if not child.edge_label:
                    raise AssertionError(f"Child '{child.text}' of '{node.text}' missing edge label")
                
                # Record parent-child pair
                pair = (id(node), id(child))
                if pair in parent_child_pairs:
                    raise AssertionError(f"Duplicate parent-child relationship: {node.text} -> {child.text}")
                parent_child_pairs.add(pair)
                
                # Recurse
                collect_nodes(child, path.copy())
        
        collect_nodes(root)
        return True
    
    def test_basic_tree_structure(self, analyzer):
        """Test tree structure for a basic sentence."""
        analysis = analyzer.analyze_sentence("The cat sat on the mat.")
        assert self.check_tree_invariants(analysis.syntactic_tree)
    
    def test_complex_tree_structure(self, analyzer):
        """Test tree structure for complex sentence."""
        analysis = analyzer.analyze_sentence(
            "When the rain stops, I will go to the store and buy some milk."
        )
        assert self.check_tree_invariants(analysis.syntactic_tree)
    
    def test_deeply_nested_structure(self, analyzer):
        """Test deeply nested tree structure."""
        analysis = analyzer.analyze_sentence(
            "The old man who lives in the house on the hill with the red door told me a story."
        )
        assert self.check_tree_invariants(analysis.syntactic_tree)
    
    def test_tree_with_lemma_decomposition(self, analyzer):
        """Test tree structure remains valid after lemma decomposition."""
        analysis = analyzer.analyze_sentence(
            "The dogs were running quickly through the woods.",
            decompose_lemmas=True
        )
        assert self.check_tree_invariants(analysis.syntactic_tree)
    
    def test_multiple_phrasal_verbs(self, analyzer):
        """Test tree with multiple phrasal verbs."""
        analysis = analyzer.analyze_sentence(
            "She looked up the word and then wrote it down."
        )
        assert self.check_tree_invariants(analysis.syntactic_tree)
    
    def test_coordinated_clauses(self, analyzer):
        """Test tree with coordinated clauses."""
        analysis = analyzer.analyze_sentence(
            "I wanted to go, but she preferred to stay, so we compromised."
        )
        assert self.check_tree_invariants(analysis.syntactic_tree)
    
    def test_node_reachability(self, analyzer):
        """Test that all tokens are reachable from root."""
        sentence = "The quick brown fox jumps over the lazy dog."
        analysis = analyzer.analyze_sentence(sentence)
        
        # Collect all reachable text
        def collect_text(node, texts=None):
            if texts is None:
                texts = set()
            
            # Add words from this node's text
            words = node.text.split()
            texts.update(word.strip('.,!?;:') for word in words)
            
            for child in node.children:
                collect_text(child, texts)
            
            return texts
        
        reachable_texts = collect_text(analysis.syntactic_tree)
        
        # Check all tokens are reachable
        for token in analysis.tokens:
            assert token.text in reachable_texts, f"Token '{token.text}' not reachable from root"
    
    def test_edge_label_consistency(self, analyzer):
        """Test that edge labels are consistent and meaningful."""
        analysis = analyzer.analyze_sentence("The cat quickly caught the mouse.")
        
        def check_edge_labels(node):
            for child in node.children:
                # Edge label should be non-empty string
                assert isinstance(child.edge_label, str), \
                       f"Edge label for '{child.text}' is not a string"
                assert len(child.edge_label) > 0, \
                       f"Edge label for '{child.text}' is empty"
                
                # Common edge labels should be correct
                if child.node_type == 'word' and child.token_info:
                    token = child.token_info
                    
                    # Check some common patterns
                    if token.dep == 'nsubj':
                        assert child.edge_label in ['subj', 'nsubj'], \
                               f"Subject '{child.text}' has unexpected edge label '{child.edge_label}'"
                    elif token.dep == 'dobj':
                        assert child.edge_label in ['obj', 'dobj'], \
                               f"Object '{child.text}' has unexpected edge label '{child.edge_label}'"
                
                # Recurse
                check_edge_labels(child)
        
        check_edge_labels(analysis.syntactic_tree)
    
    def test_parent_child_bidirectionality(self, analyzer):
        """Test that parent-child relationships are bidirectional."""
        analysis = analyzer.analyze_sentence(
            "If you build it, they will come."
        )
        
        def check_bidirectional(node):
            for child in node.children:
                # Child's parent should point back to this node
                assert child.parent is node, \
                       f"Broken bidirectional link: {node.text} -> {child.text}"
                
                # Node should contain child in its children list
                assert child in node.children, \
                       f"Child {child.text} not in parent's children list"
                
                # Recurse
                check_bidirectional(child)
        
        check_bidirectional(analysis.syntactic_tree)
    
    def test_no_orphaned_nodes(self, analyzer):
        """Test that no nodes are orphaned (except root)."""
        analysis = analyzer.analyze_sentence(
            "Despite the rain, we decided to go hiking anyway."
        )
        
        root = analysis.syntactic_tree
        
        def check_no_orphans(node, is_root=False):
            if not is_root:
                assert node.parent is not None, f"Orphaned node found: '{node.text}'"
            else:
                assert node.parent is None, f"Root node has parent: '{node.parent.text}'"
            
            for child in node.children:
                check_no_orphans(child, is_root=False)
        
        check_no_orphans(root, is_root=True) 