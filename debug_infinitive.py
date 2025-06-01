"""Debug script to see the infinitive clause structure."""

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

# Test both sentences
for sentence in ["I want to burn this house to the ground.", 
                 "I want to burn this house to the fucking ground."]:
    print(f"\n{'='*60}")
    print(f"Sentence: {sentence}")
    print('='*60)
    
    analyzer = SentenceAnalyzerV2()
    analysis = analyzer.analyze_sentence(sentence)
    
    print("\nSyntactic Tree:")
    print_tree(analysis.syntactic_tree)
    
    # Find the infinitive clause
    def find_infinitive_clause(node):
        if node.node_type == 'phrase' and 'to burn' in node.text.lower() and node.edge_label == 'obj':
            return node
        for child in node.children:
            result = find_infinitive_clause(child)
            if result:
                return result
        return None
    
    inf_clause = find_infinitive_clause(analysis.syntactic_tree)
    if inf_clause:
        print(f"\nInfinitive Clause Found: '{inf_clause.text}'")
        print("Children:")
        for child in inf_clause.children:
            print(f"  [{child.edge_label}] {child.node_type}: '{child.text}'") 