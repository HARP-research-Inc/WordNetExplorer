"""Debug script for 'ran over' phrasal verb detection."""

from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2
from src.services.phrasal_verb_handler import PhrasalVerbHandler


def print_token_info(tokens):
    """Print token information."""
    print("\nToken Information:")
    print("-" * 60)
    for i, token in enumerate(tokens):
        print(f"{i}: '{token.text}' - POS: {token.pos}, DEP: {token.dep}, HEAD: {token.head} ({tokens[token.head].text if token.head < len(tokens) else 'ROOT'})")


def main():
    analyzer = SentenceAnalyzerV2()
    
    sentence = "I ran over my friend's cat with the car."
    print(f"Analyzing: {sentence}")
    
    # Parse with spacy
    nlp = analyzer.nlp
    doc = nlp(sentence)
    
    # Get token info
    tokens = []
    for i, token in enumerate(doc):
        token_info = analyzer._token_analyzer.analyze_token(token, i)
        tokens.append(token_info)
    
    print_token_info(tokens)
    
    # Check phrasal verb detection
    handler = PhrasalVerbHandler()
    phrasal_verbs = handler.identify_phrasal_verbs(tokens)
    
    print(f"\nPhrasal verbs detected: {phrasal_verbs}")
    
    # Check specific conditions for "ran over"
    ran_idx = 1  # "ran" is at index 1
    over_idx = 2  # "over" is at index 2
    
    print(f"\nChecking 'ran over' detection:")
    print(f"- 'over' head index: {tokens[over_idx].head}")
    print(f"- 'over' dependency: {tokens[over_idx].dep}")
    print(f"- Is 'over' in particles: {'over' in handler.particles}")
    
    # Check for direct object
    has_dobj = any(t.head == ran_idx and t.dep in ['dobj', 'obj'] for t in tokens)
    print(f"- Verb has direct object: {has_dobj}")
    
    # Full analysis
    print("\n" + "=" * 60)
    analysis = analyzer.analyze_sentence(sentence)
    
    def print_tree(node, indent=0):
        print("  " * indent + f"[{node.edge_label if hasattr(node, 'edge_label') else 'root'}] {node.node_type}: '{node.text}'")
        for child in node.children:
            print_tree(child, indent + 1)
    
    print_tree(analysis.syntactic_tree)


if __name__ == "__main__":
    main() 