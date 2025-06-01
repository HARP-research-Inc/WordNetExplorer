"""Debug script to understand parsing issues with modal auxiliaries and phrasal verbs."""

from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2
from src.services.syntactic_tree import SyntacticNode

def print_tree(node, indent=0):
    """Print the syntactic tree structure."""
    prefix = "  " * indent
    edge = f"[{node.edge_label}] " if node.edge_label else ""
    token_info = ""
    if node.token_info:
        token_info = f" (POS: {node.token_info.pos}, DEP: {node.token_info.dep})"
    
    print(f"{prefix}{edge}{node.node_type}: '{node.text}'{token_info}")
    
    for child in node.children:
        print_tree(child, indent + 1)

def analyze_sentence(text):
    """Analyze a sentence and print the syntactic tree."""
    print(f"\n{'='*60}")
    print(f"Sentence: {text}")
    print('='*60)
    
    analyzer = SentenceAnalyzerV2()
    analysis = analyzer.analyze_sentence(text)
    
    # Also print token information
    print("\nTokens:")
    for i, token in enumerate(analysis.tokens):
        print(f"  {i}: '{token.text}' - POS: {token.pos}, DEP: {token.dep}, HEAD: {token.head}")
    
    print("\nSyntactic Tree:")
    print_tree(analysis.syntactic_tree)
    
    # Find verb phrases
    print("\nVerb Phrases Found:")
    find_verb_phrases(analysis.syntactic_tree)

def find_verb_phrases(node, indent=0):
    """Find and print verb phrases."""
    prefix = "  " * indent
    
    if node.node_type == 'phrase':
        # Check if this phrase contains a verb
        has_verb = False
        verb_text = None
        for child in node.children:
            if (child.node_type == 'word' and 
                child.token_info and 
                child.token_info.pos == 'VERB'):
                has_verb = True
                verb_text = child.text
                break
            elif child.edge_label in ['verb', 'verb_head', 'tverb']:
                has_verb = True
                verb_text = child.text
                break
        
        if has_verb:
            print(f"{prefix}Verb Phrase: '{node.text}'")
            print(f"{prefix}  Children:")
            for child in node.children:
                print(f"{prefix}    [{child.edge_label}] {child.text}")
    
    for child in node.children:
        find_verb_phrases(child, indent + 1)

# Test the problematic sentences
analyze_sentence("I will burn this house to the ground.")
analyze_sentence("I ran over my friend.")
analyze_sentence("I will burn this house to the fucking ground.") 