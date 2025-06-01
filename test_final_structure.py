#!/usr/bin/env python3
"""Final test of the sentence structure."""

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

# Test sentence
test_sentence = "I gleefully ran over my fat friend with a scooter."

print(f"Analyzing: {test_sentence}")
print("-" * 50)

analyzer = SentenceAnalyzerV2()
result = analyzer.analyze_sentence(test_sentence)

print("\nSyntactic Tree:")
print_tree(result.syntactic_tree)

print("\n✓ Second tier has:")
print("  - 'gleefully' (adverb modifier)")
print("  - 'I ran over my fat friend with a scooter' (main clause)")

print("\n✗ Third tier should have:")
print("  - 'I' (subject)")
print("  - 'ran over' (phrasal verb)")
print("  - 'my fat friend with a scooter' (object)")

print("\nActual third tier:")
for child in result.syntactic_tree.children:
    if child.node_type == 'clause':
        for grandchild in child.children:
            print(f"  - '{grandchild.text}' ({grandchild.edge_label})") 