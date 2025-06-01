#!/usr/bin/env python3
"""Test the improved sentence structure for the given example."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2

def print_tree(node, level=0):
    """Print the syntactic tree structure."""
    indent = "  " * level
    edge_label = f" ({node.edge_label})" if node.edge_label else ""
    print(f"{indent}{node.node_type}: '{node.text}'{edge_label}")
    
    for child in node.children:
        print_tree(child, level + 1)

# Create a custom analyzer to debug
class DebugSentenceAnalyzer(SentenceAnalyzerV2):
    def analyze_sentence(self, sentence: str):
        # Call parent implementation
        result = super().analyze_sentence(sentence)
        
        # Print intermediate steps
        print("\nDEBUG: Tree structure after initial build:")
        print_tree(result.syntactic_tree)
        
        return result

# Test sentence
test_sentence = "I gleefully ran over my fat friend with a scooter."

print(f"Analyzing: {test_sentence}")
print("-" * 50)

analyzer = DebugSentenceAnalyzer()
result = analyzer.analyze_sentence(test_sentence)

print("\nFinal Syntactic Tree Structure:")
print_tree(result.syntactic_tree)

print("\nToken Details:")
for i, token in enumerate(result.tokens):
    print(f"{i}: {token.text} - POS: {token.pos}, DEP: {token.dep}, HEAD: {token.head}")
    if token.best_synset:
        print(f"   Synset: {token.best_synset[0]}")

print("\nExpected structure:")
print("sentence: 'I gleefully ran over my fat friend with a scooter.'")
print("  word: 'gleefully' (adv_mod)")
print("  clause: 'I ran over my fat friend with a scooter' (main_clause)")
print("    word: 'I' (subj)")
print("    phrase: 'ran over' (tverb)")
print("      word: 'ran' (verb_head)")
print("      word: 'over' (particle)")
print("    phrase: 'my fat friend with a scooter' (obj)")
print("      ...") 