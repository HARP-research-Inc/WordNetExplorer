"""Verify all the fixes for syntactic tree structure."""

from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2


def print_tree(node, indent=0):
    """Print syntactic tree structure."""
    edge_label = getattr(node, 'edge_label', 'root')
    print("  " * indent + f"[{edge_label}] {node.node_type}: '{node.text}'")
    for child in node.children:
        print_tree(child, indent + 1)


def check_verb_has_no_children(node):
    """Check that verb word nodes don't have children."""
    if node.node_type == 'word' and node.token_info and node.token_info.pos == 'VERB':
        if node.children:
            return False, f"Verb '{node.text}' has children: {[c.text for c in node.children]}"
    
    for child in node.children:
        ok, msg = check_verb_has_no_children(child)
        if not ok:
            return ok, msg
    
    return True, "OK"


def main():
    analyzer = SentenceAnalyzerV2()
    
    test_cases = [
        {
            'sentence': "I gleefully gave my fat friend a scooter to ride.",
            'expected': ["to ride"],  # Should see "to ride" not "ride to"
            'description': "Infinitive phrase ordering"
        },
        {
            'sentence': "I gleefully gave my fat friend a scooter to ride with.",
            'expected': ["to ride with"],  # Should see "to ride with" as one phrase
            'description': "Infinitive phrase with preposition"
        },
        {
            'sentence': "I gleefully ran over my fat friend with a scooter.",
            'expected': ["I gleefully ran over my fat friend with a scooter"],  # Should be one phrase
            'not_expected': ["I ran ."],  # Should NOT see this separated
            'description': "Verb phrase with prepositional phrases"
        },
        {
            'sentence': "She has been running.",
            'expected': ["has", "been"],  # Should see auxiliary verbs
            'description': "Auxiliary verbs in verb phrase"
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        print(f"\nTest: {test['description']}")
        print(f"Sentence: {test['sentence']}")
        print("-" * 60)
        
        analysis = analyzer.analyze_sentence(test['sentence'])
        
        # Print tree
        print("Tree structure:")
        print_tree(analysis.syntactic_tree)
        
        # Check verb nodes have no children
        ok, msg = check_verb_has_no_children(analysis.syntactic_tree)
        if not ok:
            print(f"❌ FAIL: {msg}")
            all_passed = False
        else:
            print("✓ Verb nodes have no children")
        
        # Get all text in the tree
        def get_all_texts(node, texts=None):
            if texts is None:
                texts = []
            texts.append(node.text)
            for child in node.children:
                get_all_texts(child, texts)
            return texts
        
        all_texts = get_all_texts(analysis.syntactic_tree)
        
        # Check expected patterns
        passed = True
        for expected in test.get('expected', []):
            found = any(expected in text for text in all_texts)
            if found:
                print(f"✓ Found expected: '{expected}'")
            else:
                print(f"❌ Missing expected: '{expected}'")
                passed = False
                all_passed = False
        
        # Check not expected patterns
        for not_expected in test.get('not_expected', []):
            found = any(not_expected == text for text in all_texts)
            if not found:
                print(f"✓ Correctly avoided: '{not_expected}'")
            else:
                print(f"❌ Found unexpected: '{not_expected}'")
                passed = False
                all_passed = False
        
        if passed:
            print("✅ PASSED")
        else:
            print("❌ FAILED")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")


if __name__ == "__main__":
    main() 