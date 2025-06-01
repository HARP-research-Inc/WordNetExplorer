#!/usr/bin/env python3
"""Test the fixed noun phrase structures."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2

def print_tree(node, level=0):
    """Print the syntactic tree structure."""
    indent = "  " * level
    edge_label = f" ({node.edge_label})" if node.edge_label else ""
    print(f"{indent}[{node.node_type}] '{node.text}'{edge_label}")
    
    for child in node.children:
        print_tree(child, level + 1)

def find_node_by_text(node, text):
    """Find a node by its text content."""
    if node.text == text:
        return node
    for child in node.children:
        result = find_node_by_text(child, text)
        if result:
            return result
    return None

# Test sentences
test_sentences = [
    "I gleefully give my fat friend a scooter.",
    "I ran over my fat friend with a scooter."
]

analyzer = SentenceAnalyzerV2()

for sentence in test_sentences:
    print(f"\nAnalyzing: {sentence}")
    print("-" * 60)
    
    result = analyzer.analyze_sentence(sentence)
    print_tree(result.syntactic_tree)
    
    # Check specific structures
    print("\nChecking specific structures:")
    
    # Check "a scooter"
    scooter_node = find_node_by_text(result.syntactic_tree, "a scooter")
    if scooter_node:
        print("\n'a scooter' structure:")
        print_tree(scooter_node, 1)
        # Verify that 'a' is a child of the phrase, not 'scooter' a child of 'a'
        for child in scooter_node.children:
            if child.text == 'a' and child.edge_label == 'det':
                print("  ✓ Correct: 'a' is child with 'det' edge")
            elif child.text == 'scooter' and child.edge_label == 'head':
                print("  ✓ Correct: 'scooter' is head")
    
    # Check "my fat friend"
    friend_node = find_node_by_text(result.syntactic_tree, "my fat friend")
    if friend_node:
        print("\n'my fat friend' structure:")
        print_tree(friend_node, 1)
        # Check for hierarchical structure
        fat_friend_node = None
        for child in friend_node.children:
            if child.text == "fat friend":
                fat_friend_node = child
                print("  ✓ Correct: Found 'fat friend' as sub-phrase")
                break
        
        if not fat_friend_node:
            # Check if it's flat structure
            has_my = any(c.text == 'my' for c in friend_node.children)
            has_fat = any(c.text == 'fat' for c in friend_node.children)
            has_friend = any(c.text == 'friend' for c in friend_node.children)
            if has_my and has_fat and has_friend:
                print("  ✗ Incorrect: Flat structure (all words at same level)")
    
    print("\n" + "=" * 60) 