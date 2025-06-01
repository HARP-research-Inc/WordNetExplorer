"""Debug script to inspect phrasal verb structure."""

from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2


def print_tree(node, indent=0):
    """Print syntactic tree structure."""
    print("  " * indent + f"{node.node_type}: '{node.text}' (edge: {node.edge_label if hasattr(node, 'edge_label') else 'root'})")
    for child in node.children:
        child_edge = child.edge_label if hasattr(child, 'edge_label') else 'no_edge'
        print("  " * (indent + 1) + f"[{child_edge}] {child.node_type}: '{child.text}'")
        if child.children:
            for grandchild in child.children:
                print_tree(grandchild, indent + 2)


def main():
    analyzer = SentenceAnalyzerV2()
    
    # Test sentence with phrasal verb
    sentence = "She looked up the word."
    print(f"Analyzing: {sentence}")
    print("-" * 50)
    
    analysis = analyzer.analyze_sentence(sentence)
    
    # Print the full tree
    print_tree(analysis.syntactic_tree)
    
    # Find verb phrases
    print("\n" + "-" * 50)
    print("Looking for verb phrases...")
    
    def find_verb_phrases(node, found=None):
        if found is None:
            found = []
        
        if node.node_type == 'phrase':
            # Check if this phrase contains a verb
            has_verb = False
            for child in node.children:
                if (child.node_type == 'word' and 
                    child.token_info and 
                    child.token_info.pos == 'VERB'):
                    has_verb = True
                    break
                elif child.edge_label in ['verb', 'verb_head', 'tverb']:
                    has_verb = True
                    break
            
            if has_verb:
                found.append(node)
                print(f"\nFound verb phrase: '{node.text}'")
                print(f"Children: {[f'{c.edge_label}: {c.text}' for c in node.children]}")
        
        for child in node.children:
            find_verb_phrases(child, found)
        
        return found
    
    verb_phrases = find_verb_phrases(analysis.syntactic_tree)
    print(f"\nTotal verb phrases found: {len(verb_phrases)}")


if __name__ == "__main__":
    main() 