"""
Unit tests for Dependency Analyzer module
"""

import unittest
from unittest.mock import Mock
from src.parsing.dependency_analyzer import (
    DependencyPath, get_children, get_ancestors, find_head_verb,
    get_dependency_distance, is_dependent_of, find_dependency_path,
    get_siblings, get_subtree, find_common_ancestor,
    get_dependency_chain, is_root
)


class TestDependencyPath(unittest.TestCase):
    """Test DependencyPath dataclass."""
    
    def test_dependency_path_creation(self):
        """Test creating DependencyPath."""
        path = DependencyPath(
            source=0,
            target=3,
            path=(0, 1, 3),
            relations=("↑nsubj", "↓dobj")
        )
        self.assertEqual(path.source, 0)
        self.assertEqual(path.target, 3)
        self.assertEqual(path.length, 2)
    
    def test_single_node_path(self):
        """Test path with single node."""
        path = DependencyPath(
            source=5,
            target=5,
            path=(5,),
            relations=()
        )
        self.assertEqual(path.length, 0)


class TestGetChildren(unittest.TestCase):
    """Test get_children function."""
    
    def test_simple_children(self):
        """Test getting children in simple tree."""
        # Create tokens: "The cat sits"
        # Structure: sits(ROOT) -> cat(nsubj) -> The(det)
        tokens = []
        
        # Token 0: "The"
        token0 = Mock()
        token0.head = Mock(i=1)  # Points to "cat"
        tokens.append(token0)
        
        # Token 1: "cat"
        token1 = Mock()
        token1.head = Mock(i=2)  # Points to "sits"
        tokens.append(token1)
        
        # Token 2: "sits"
        token2 = Mock()
        token2.head = Mock(i=2)  # Points to itself (ROOT)
        tokens.append(token2)
        
        # Test children
        self.assertEqual(get_children(0, tokens), [])  # "The" has no children
        self.assertEqual(get_children(1, tokens), [0])  # "cat" has "The" as child
        self.assertEqual(get_children(2, tokens), [1])  # "sits" has "cat" as child
    
    def test_multiple_children(self):
        """Test token with multiple children."""
        # "runs quickly home" - runs -> quickly, runs -> home
        tokens = []
        
        # Token 0: "runs" (ROOT)
        token0 = Mock()
        token0.head = Mock(i=0)
        tokens.append(token0)
        
        # Token 1: "quickly" 
        token1 = Mock()
        token1.head = Mock(i=0)
        tokens.append(token1)
        
        # Token 2: "home"
        token2 = Mock()
        token2.head = Mock(i=0)
        tokens.append(token2)
        
        children = get_children(0, tokens)
        self.assertEqual(sorted(children), [1, 2])
    
    def test_with_token_features(self):
        """Test with TokenFeatures objects."""
        from src.parsing.token_processor import TokenFeatures
        
        tokens = [
            TokenFeatures(0, "The", "the", "DET", "DT", "det", 1, False, False, False, True, "Xxx"),
            TokenFeatures(1, "cat", "cat", "NOUN", "NN", "nsubj", 2, False, False, False, True, "xxx"),
            TokenFeatures(2, "sits", "sit", "VERB", "VBZ", "ROOT", 2, False, False, False, True, "xxxx")
        ]
        
        self.assertEqual(get_children(1, tokens), [0])
        self.assertEqual(get_children(2, tokens), [1])


class TestGetAncestors(unittest.TestCase):
    """Test get_ancestors function."""
    
    def test_simple_ancestors(self):
        """Test getting ancestors in simple tree."""
        # "The big cat" - The -> big -> cat
        tokens = []
        
        # Token 0: "The"
        token0 = Mock()
        token0.head = Mock(i=1)
        tokens.append(token0)
        
        # Token 1: "big"
        token1 = Mock() 
        token1.head = Mock(i=2)
        tokens.append(token1)
        
        # Token 2: "cat"
        token2 = Mock()
        token2.head = Mock(i=2)  # ROOT
        tokens.append(token2)
        
        # Test ancestors
        self.assertEqual(get_ancestors(0, tokens), [1, 2])  # The -> big -> cat
        self.assertEqual(get_ancestors(1, tokens), [2])     # big -> cat
        self.assertEqual(get_ancestors(2, tokens), [])      # cat is ROOT
    
    def test_circular_dependency_protection(self):
        """Test protection against circular dependencies."""
        tokens = []
        
        # Create circular dependency
        token0 = Mock()
        token0.head = Mock(i=1)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=0)  # Circular!
        tokens.append(token1)
        
        # Should not infinite loop
        ancestors = get_ancestors(0, tokens)
        self.assertLessEqual(len(ancestors), len(tokens))


class TestFindHeadVerb(unittest.TestCase):
    """Test find_head_verb function."""
    
    def test_verb_token_itself(self):
        """Test when token itself is a verb."""
        token = Mock()
        token.pos_ = "VERB"
        tokens = [token]
        
        self.assertEqual(find_head_verb(0, tokens), 0)
    
    def test_noun_with_verb_parent(self):
        """Test noun with verb parent."""
        # "cat sits" - cat(NOUN) -> sits(VERB)
        tokens = []
        
        # Token 0: "cat"
        token0 = Mock()
        token0.pos_ = "NOUN"
        token0.head = Mock(i=1)
        tokens.append(token0)
        
        # Token 1: "sits"
        token1 = Mock()
        token1.pos_ = "VERB"
        token1.head = Mock(i=1)  # ROOT
        tokens.append(token1)
        
        self.assertEqual(find_head_verb(0, tokens), 1)
    
    def test_deep_tree_verb_search(self):
        """Test finding verb in deep tree."""
        # "The very big cat sits" 
        # The -> very -> big -> cat -> sits
        tokens = []
        
        for i in range(4):
            token = Mock()
            token.pos_ = ["DET", "ADV", "ADJ", "NOUN"][i]
            token.head = Mock(i=i+1 if i < 3 else 4)
            tokens.append(token)
        
        # Token 4: "sits"
        token4 = Mock()
        token4.pos_ = "VERB"
        token4.head = Mock(i=4)
        tokens.append(token4)
        
        self.assertEqual(find_head_verb(0, tokens), 4)
    
    def test_no_verb_found(self):
        """Test when no verb exists."""
        # "Very nice!" - no verb
        tokens = []
        
        token0 = Mock()
        token0.pos_ = "ADV"
        token0.head = Mock(i=1)
        tokens.append(token0)
        
        token1 = Mock()
        token1.pos_ = "ADJ"
        token1.head = Mock(i=1)
        tokens.append(token1)
        
        self.assertIsNone(find_head_verb(0, tokens))


class TestDependencyDistance(unittest.TestCase):
    """Test get_dependency_distance function."""
    
    def test_same_token(self):
        """Test distance to same token is 0."""
        tokens = [Mock()]
        self.assertEqual(get_dependency_distance(0, 0, tokens), 0)
    
    def test_parent_child_distance(self):
        """Test distance between parent and child."""
        tokens = []
        
        # Token 0 -> Token 1
        token0 = Mock()
        token0.head = Mock(i=1)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=1)
        tokens.append(token1)
        
        self.assertEqual(get_dependency_distance(0, 1, tokens), 1)
        self.assertEqual(get_dependency_distance(1, 0, tokens), 1)
    
    def test_sibling_distance(self):
        """Test distance between siblings."""
        # Both tokens point to token 2
        tokens = []
        
        token0 = Mock()
        token0.head = Mock(i=2)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=2)
        tokens.append(token1)
        
        token2 = Mock()
        token2.head = Mock(i=2)
        tokens.append(token2)
        
        # Distance: 0 -> 2 -> 1 = 2
        self.assertEqual(get_dependency_distance(0, 1, tokens), 2)
    
    def test_disconnected_trees(self):
        """Test distance between disconnected subtrees."""
        # Two separate roots
        tokens = []
        
        token0 = Mock()
        token0.head = Mock(i=0)  # Root 1
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=1)  # Root 2
        tokens.append(token1)
        
        self.assertEqual(get_dependency_distance(0, 1, tokens), -1)


class TestIsDependentOf(unittest.TestCase):
    """Test is_dependent_of function."""
    
    def test_direct_dependent(self):
        """Test direct dependency."""
        tokens = []
        
        # Token 0 -> Token 1
        token0 = Mock()
        token0.head = Mock(i=1)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=1)
        tokens.append(token1)
        
        self.assertTrue(is_dependent_of(0, 1, tokens))
        self.assertFalse(is_dependent_of(1, 0, tokens))
    
    def test_indirect_dependent(self):
        """Test indirect dependency."""
        # 0 -> 1 -> 2
        tokens = []
        
        token0 = Mock()
        token0.head = Mock(i=1)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=2)
        tokens.append(token1)
        
        token2 = Mock()
        token2.head = Mock(i=2)
        tokens.append(token2)
        
        self.assertTrue(is_dependent_of(0, 2, tokens))
        self.assertFalse(is_dependent_of(2, 0, tokens))
    
    def test_same_token(self):
        """Test token is not dependent of itself."""
        tokens = [Mock()]
        self.assertFalse(is_dependent_of(0, 0, tokens))


class TestFindDependencyPath(unittest.TestCase):
    """Test find_dependency_path function."""
    
    def test_simple_path(self):
        """Test finding simple path."""
        # 0 -> 1 -> 2
        tokens = []
        
        token0 = Mock()
        token0.head = Mock(i=1)
        token0.dep_ = "det"
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=2)
        token1.dep_ = "nsubj"
        tokens.append(token1)
        
        token2 = Mock()
        token2.head = Mock(i=2)
        token2.dep_ = "ROOT"
        tokens.append(token2)
        
        path = find_dependency_path(0, 2, tokens)
        self.assertIsNotNone(path)
        self.assertEqual(path.path, (0, 1, 2))
        self.assertEqual(len(path.relations), 2)
    
    def test_no_path(self):
        """Test when no path exists."""
        # Disconnected nodes
        tokens = []
        
        token0 = Mock()
        token0.head = Mock(i=0)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=1)
        tokens.append(token1)
        
        path = find_dependency_path(0, 1, tokens)
        self.assertIsNone(path)


class TestGetSiblings(unittest.TestCase):
    """Test get_siblings function."""
    
    def test_simple_siblings(self):
        """Test getting siblings."""
        # 0 and 1 both point to 2
        tokens = []
        
        token0 = Mock()
        token0.head = Mock(i=2)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=2)
        tokens.append(token1)
        
        token2 = Mock()
        token2.head = Mock(i=2)
        tokens.append(token2)
        
        self.assertEqual(get_siblings(0, tokens), [1])
        self.assertEqual(get_siblings(1, tokens), [0])
        self.assertEqual(get_siblings(2, tokens), [])  # Root has no siblings


class TestGetSubtree(unittest.TestCase):
    """Test get_subtree function."""
    
    def test_simple_subtree(self):
        """Test getting subtree."""
        # Tree: 2 -> 1 -> 0
        tokens = []
        
        token0 = Mock()
        token0.head = Mock(i=1)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=2)
        tokens.append(token1)
        
        token2 = Mock()
        token2.head = Mock(i=2)
        tokens.append(token2)
        
        # Subtree rooted at 2 includes all
        self.assertEqual(get_subtree(2, tokens), {0, 1, 2})
        
        # Subtree rooted at 1 includes 0 and 1
        self.assertEqual(get_subtree(1, tokens), {0, 1})
        
        # Subtree rooted at 0 includes only 0
        self.assertEqual(get_subtree(0, tokens), {0})


class TestCommonAncestor(unittest.TestCase):
    """Test find_common_ancestor function."""
    
    def test_simple_common_ancestor(self):
        """Test finding common ancestor."""
        # Tree: 3 -> 2 -> {0, 1}
        tokens = []
        
        token0 = Mock()
        token0.head = Mock(i=2)
        tokens.append(token0)
        
        token1 = Mock()
        token1.head = Mock(i=2)
        tokens.append(token1)
        
        token2 = Mock()
        token2.head = Mock(i=3)
        tokens.append(token2)
        
        token3 = Mock()
        token3.head = Mock(i=3)
        tokens.append(token3)
        
        # Common ancestor of siblings
        self.assertEqual(find_common_ancestor(0, 1, tokens), 2)
        
        # Common ancestor of parent-child
        self.assertEqual(find_common_ancestor(0, 2, tokens), 2)
        
        # Common ancestor with root
        self.assertEqual(find_common_ancestor(0, 3, tokens), 3)


class TestDependencyChain(unittest.TestCase):
    """Test get_dependency_chain function."""
    
    def test_coordination_chain(self):
        """Test finding coordination chain."""
        # "cats and dogs and birds" - all connected by "conj"
        tokens = []
        
        # Token 0: "cats" (root of coordination)
        token0 = Mock()
        token0.head = Mock(i=0)
        token0.dep_ = "ROOT"
        tokens.append(token0)
        
        # Token 1: "and"
        token1 = Mock()
        token1.head = Mock(i=0)
        token1.dep_ = "cc"
        tokens.append(token1)
        
        # Token 2: "dogs"
        token2 = Mock()
        token2.head = Mock(i=0)
        token2.dep_ = "conj"
        tokens.append(token2)
        
        # Token 3: "and"
        token3 = Mock()
        token3.head = Mock(i=2)
        token3.dep_ = "cc"
        tokens.append(token3)
        
        # Token 4: "birds"
        token4 = Mock()
        token4.head = Mock(i=2)
        token4.dep_ = "conj"
        tokens.append(token4)
        
        chain = get_dependency_chain(0, tokens, "conj")
        self.assertEqual(sorted(chain), [0, 2, 4])


class TestIsRoot(unittest.TestCase):
    """Test is_root function."""
    
    def test_root_by_self_reference(self):
        """Test root detection by self-reference."""
        token = Mock()
        token.head = Mock(i=0)
        token.dep_ = "ROOT"
        tokens = [token]
        
        self.assertTrue(is_root(0, tokens))
    
    def test_root_by_dep_only(self):
        """Test root detection by dependency only."""
        token = Mock()
        token.head = Mock(i=1)  # Points elsewhere
        token.dep_ = "ROOT"
        tokens = [token]
        
        self.assertTrue(is_root(0, tokens))
    
    def test_not_root(self):
        """Test non-root token."""
        token = Mock()
        token.head = Mock(i=1)
        token.dep_ = "nsubj"
        tokens = [token]
        
        self.assertFalse(is_root(0, tokens))


if __name__ == '__main__':
    unittest.main() 