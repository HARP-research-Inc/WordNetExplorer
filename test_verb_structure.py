"""Test script to verify verb nodes don't have children."""

from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2


def check_verb_nodes(node, path=""):
    """Recursively check that verb word nodes don't have children."""
    current_path = f"{path}/{node.node_type}:{node.text}"
    
    if node.node_type == 'word' and node.token_info and node.token_info.pos == 'VERB':
        if node.children:
            print(f"❌ ERROR: Verb word node has children!")
            print(f"   Path: {current_path}")
            print(f"   Children: {[f'{c.edge_label}:{c.text}' for c in node.children]}")
            return False
        else:
            print(f"✓ Verb word node has no children: {current_path}")
    
    # Check all children
    all_good = True
    for child in node.children:
        if not check_verb_nodes(child, current_path):
            all_good = False
    
    return all_good


def main():
    analyzer = SentenceAnalyzerV2()
    
    test_sentences = [
        "The cat eats fish.",
        "She looked up the word.",
        "The teacher gave the students homework.",
        "She has been running.",
        "I ran over my friend's cat with the car.",
        "When it rains, I stay inside."
    ]
    
    all_passed = True
    
    for sentence in test_sentences:
        print(f"\nTesting: {sentence}")
        print("-" * 50)
        
        analysis = analyzer.analyze_sentence(sentence)
        
        if check_verb_nodes(analysis.syntactic_tree):
            print("✅ PASS: No verb word nodes have children")
        else:
            print("❌ FAIL: Found verb word nodes with children")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")


if __name__ == "__main__":
    main() 