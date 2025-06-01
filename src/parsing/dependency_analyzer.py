"""
Dependency Analyzer Module - Analyzes dependency relationships between tokens
"""

from typing import List, Optional, Set, Tuple
from dataclasses import dataclass
from collections import deque


@dataclass(frozen=True)
class DependencyPath:
    """Represents a dependency path between two tokens."""
    source: int
    target: int
    path: Tuple[int, ...]
    relations: Tuple[str, ...]
    
    @property
    def length(self) -> int:
        """Get the length of the path."""
        return len(self.path) - 1


def get_children(token_idx: int, tokens: List) -> List[int]:
    """
    Get all direct children of a token.
    
    Args:
        token_idx: Index of the parent token
        tokens: List of tokens (spaCy tokens or TokenFeatures)
        
    Returns:
        List of child token indices
    """
    children = []
    for i, token in enumerate(tokens):
        # Handle both spaCy tokens and TokenFeatures
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        # Check if this token's head is our target token
        if head_idx == token_idx and i != token_idx:
            children.append(i)
    
    return children


def get_ancestors(token_idx: int, tokens: List) -> List[int]:
    """
    Get all ancestors of a token (path to root).
    
    Args:
        token_idx: Index of the token
        tokens: List of tokens
        
    Returns:
        List of ancestor indices (immediate parent first)
    """
    ancestors = []
    current_idx = token_idx
    visited = set()
    
    while current_idx not in visited:
        visited.add(current_idx)
        
        # Get head
        token = tokens[current_idx]
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        # Check if we've reached the root
        if head_idx == current_idx:
            break
            
        ancestors.append(head_idx)
        current_idx = head_idx
        
        # Safety check for circular dependencies
        if len(ancestors) > len(tokens):
            break
    
    return ancestors


def find_head_verb(token_idx: int, tokens: List) -> Optional[int]:
    """
    Find the head verb governing a token.
    
    Args:
        token_idx: Index of the token
        tokens: List of tokens
        
    Returns:
        Index of head verb or None
    """
    # Check if token itself is a verb
    token = tokens[token_idx]
    token_pos = token.pos_ if hasattr(token, 'pos_') else token.pos
    
    if token_pos == 'VERB':
        return token_idx
    
    # Search ancestors for a verb
    ancestors = get_ancestors(token_idx, tokens)
    
    for ancestor_idx in ancestors:
        ancestor = tokens[ancestor_idx]
        ancestor_pos = ancestor.pos_ if hasattr(ancestor, 'pos_') else ancestor.pos
        
        if ancestor_pos == 'VERB':
            return ancestor_idx
    
    return None


def get_dependency_distance(token1_idx: int, token2_idx: int, tokens: List) -> int:
    """
    Get the dependency distance between two tokens.
    
    Distance is the number of dependency edges in the shortest path.
    Returns -1 if tokens are not connected.
    
    Args:
        token1_idx: Index of first token
        token2_idx: Index of second token
        tokens: List of tokens
        
    Returns:
        Distance or -1 if not connected
    """
    if token1_idx == token2_idx:
        return 0
    
    # Find common ancestor using paths to root
    ancestors1 = {token1_idx: 0}
    current_idx = token1_idx
    distance = 0
    
    # Build path from token1 to root
    while True:
        token = tokens[current_idx]
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        if head_idx == current_idx:  # Root
            break
            
        distance += 1
        ancestors1[head_idx] = distance
        current_idx = head_idx
        
        # Safety check
        if distance > len(tokens):
            return -1
    
    # Trace path from token2 to find common ancestor
    current_idx = token2_idx
    distance2 = 0
    
    while True:
        if current_idx in ancestors1:
            # Found common ancestor
            return ancestors1[current_idx] + distance2
        
        token = tokens[current_idx]
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        if head_idx == current_idx:  # Root
            break
            
        distance2 += 1
        current_idx = head_idx
        
        # Safety check
        if distance2 > len(tokens):
            return -1
    
    return -1  # Not connected


def is_dependent_of(child_idx: int, parent_idx: int, tokens: List) -> bool:
    """
    Check if child is a dependent of parent (direct or indirect).
    
    Args:
        child_idx: Index of potential child
        parent_idx: Index of potential parent
        tokens: List of tokens
        
    Returns:
        True if child is dependent of parent
    """
    if child_idx == parent_idx:
        return False
    
    current_idx = child_idx
    visited = set()
    
    while current_idx not in visited:
        visited.add(current_idx)
        
        token = tokens[current_idx]
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        if head_idx == parent_idx:
            return True
            
        if head_idx == current_idx:  # Root
            return False
            
        current_idx = head_idx
        
        # Safety check
        if len(visited) > len(tokens):
            return False
    
    return False


def find_dependency_path(source_idx: int, target_idx: int, tokens: List) -> Optional[DependencyPath]:
    """
    Find the dependency path between two tokens.
    
    Args:
        source_idx: Source token index
        target_idx: Target token index  
        tokens: List of tokens
        
    Returns:
        DependencyPath or None if no path exists
    """
    if source_idx == target_idx:
        return DependencyPath(
            source=source_idx,
            target=target_idx,
            path=(source_idx,),
            relations=()
        )
    
    # BFS to find shortest path
    queue = deque([(source_idx, [source_idx], [])])
    visited = {source_idx}
    
    while queue:
        current_idx, path, relations = queue.popleft()
        
        # Check all possible moves (to parent or children)
        token = tokens[current_idx]
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        # Move to parent
        if head_idx != current_idx and head_idx not in visited:
            new_path = path + [head_idx]
            dep = token.dep_ if hasattr(token, 'dep_') else token.dep
            new_relations = relations + [f"↑{dep}"]
            
            if head_idx == target_idx:
                return DependencyPath(
                    source=source_idx,
                    target=target_idx,
                    path=tuple(new_path),
                    relations=tuple(new_relations)
                )
            
            visited.add(head_idx)
            queue.append((head_idx, new_path, new_relations))
        
        # Move to children
        for child_idx in get_children(current_idx, tokens):
            if child_idx not in visited:
                new_path = path + [child_idx]
                child_token = tokens[child_idx]
                dep = child_token.dep_ if hasattr(child_token, 'dep_') else child_token.dep
                new_relations = relations + [f"↓{dep}"]
                
                if child_idx == target_idx:
                    return DependencyPath(
                        source=source_idx,
                        target=target_idx,
                        path=tuple(new_path),
                        relations=tuple(new_relations)
                    )
                
                visited.add(child_idx)
                queue.append((child_idx, new_path, new_relations))
    
    return None


def get_siblings(token_idx: int, tokens: List) -> List[int]:
    """
    Get sibling tokens (tokens with same head).
    
    Args:
        token_idx: Token index
        tokens: List of tokens
        
    Returns:
        List of sibling indices (excluding self)
    """
    token = tokens[token_idx]
    head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
    
    # Root has no siblings
    if head_idx == token_idx:
        return []
    
    # Find all children of the same head
    siblings = []
    for i, other_token in enumerate(tokens):
        if i == token_idx:
            continue
            
        other_head_idx = other_token.head.i if hasattr(other_token, 'head') and hasattr(other_token.head, 'i') else other_token.head
        
        # Check if other token has same head and is not the head itself
        if other_head_idx == head_idx and i != head_idx:
            siblings.append(i)
    
    return siblings


def get_subtree(root_idx: int, tokens: List) -> Set[int]:
    """
    Get all tokens in the subtree rooted at given token.
    
    Args:
        root_idx: Root token index
        tokens: List of tokens
        
    Returns:
        Set of token indices in subtree
    """
    subtree = {root_idx}
    queue = deque([root_idx])
    
    while queue:
        current_idx = queue.popleft()
        
        # Add all children
        for child_idx in get_children(current_idx, tokens):
            if child_idx not in subtree:
                subtree.add(child_idx)
                queue.append(child_idx)
    
    return subtree


def find_common_ancestor(token1_idx: int, token2_idx: int, tokens: List) -> Optional[int]:
    """
    Find the lowest common ancestor of two tokens.
    
    Args:
        token1_idx: First token index
        token2_idx: Second token index
        tokens: List of tokens
        
    Returns:
        Index of common ancestor or None
    """
    # Get ancestors of token1
    ancestors1 = {token1_idx}
    current_idx = token1_idx
    
    while True:
        token = tokens[current_idx]
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        if head_idx == current_idx:  # Root
            ancestors1.add(current_idx)
            break
            
        ancestors1.add(head_idx)
        current_idx = head_idx
    
    # Trace token2's path until we find common ancestor
    current_idx = token2_idx
    
    while True:
        if current_idx in ancestors1:
            return current_idx
            
        token = tokens[current_idx]
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        if head_idx == current_idx:  # Root
            if current_idx in ancestors1:
                return current_idx
            break
            
        current_idx = head_idx
    
    return None


def get_dependency_chain(token_idx: int, tokens: List, relation: str) -> List[int]:
    """
    Get chain of tokens connected by specific dependency relation.
    
    For example, get all tokens connected by 'conj' relations.
    
    Args:
        token_idx: Starting token
        tokens: List of tokens
        relation: Dependency relation to follow
        
    Returns:
        List of connected token indices
    """
    chain = [token_idx]
    visited = {token_idx}
    queue = deque([token_idx])
    
    while queue:
        current_idx = queue.popleft()
        
        # Check children with matching relation
        for child_idx in get_children(current_idx, tokens):
            if child_idx not in visited:
                child_token = tokens[child_idx]
                child_dep = child_token.dep_ if hasattr(child_token, 'dep_') else child_token.dep
                
                if child_dep == relation:
                    chain.append(child_idx)
                    visited.add(child_idx)
                    queue.append(child_idx)
        
        # Check if parent connection matches
        token = tokens[current_idx]
        token_dep = token.dep_ if hasattr(token, 'dep_') else token.dep
        head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
        
        if token_dep == relation and head_idx not in visited and head_idx != current_idx:
            chain.append(head_idx)
            visited.add(head_idx)
            queue.append(head_idx)
    
    return sorted(chain)


def is_root(token_idx: int, tokens: List) -> bool:
    """
    Check if token is the root of the dependency tree.
    
    Args:
        token_idx: Token index
        tokens: List of tokens
        
    Returns:
        True if token is root
    """
    token = tokens[token_idx]
    head_idx = token.head.i if hasattr(token, 'head') and hasattr(token.head, 'i') else token.head
    
    # Root points to itself
    if head_idx == token_idx:
        return True
    
    # Also check dependency relation
    dep = token.dep_ if hasattr(token, 'dep_') else token.dep
    return dep == 'ROOT' 