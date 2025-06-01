# Sentence Parser Test Suite

This directory contains comprehensive tests for the modular sentence parser. The tests are designed to catch structural issues, edge cases, and ensure the parser maintains proper tree integrity.

## Test Files

- **`test_sentence_parser.py`** - Main test suite covering:
  - Basic sentence structures
  - Complex sentences with multiple clauses
  - Phrasal verbs
  - Noun phrases
  - Prepositional phrases
  - Lemma decomposition

- **`test_tree_structure.py`** - Focused tests for syntactic tree integrity:
  - No cycles in the tree
  - Proper parent-child bidirectional references
  - No duplicate children
  - No orphaned nodes
  - Consistent edge labels

- **`test_edge_cases.py`** - Tests for problematic and edge case sentences:
  - The 401k sentence: "I would like to run the world someday, but only if my 401k goes up."
  - Multiple infinitives
  - Complex punctuation
  - Contractions and possessives
  - Numbers and symbols
  - Ambiguous word roles
  - Nested structures

## Running Tests

### Run all tests:
```bash
python run_tests.py
```

### Run specific test file:
```bash
python -m pytest test/test_edge_cases.py -v
```

### Run specific test:
```bash
python -m pytest test/test_edge_cases.py::TestEdgeCases::test_401k_sentence -v
```

### Run tests matching a pattern:
```bash
python -m pytest -k "401k" -v
```

### Run with coverage:
```bash
pip install pytest-cov
python -m pytest --cov=src/services --cov-report=html
```

## Current Known Issues

As of the test creation, the parser has several structural issues:

1. **Cycle Detection**: The problematic sentence "I would like to run the world someday, but only if my 401k goes up." creates cycles in the syntactic tree.

2. **Parent-Child References**: Even simple sentences like "The cat eats fish." have incorrect parent references where children don't properly point back to their parents.

3. **Tree Integrity**: The tree structure is not maintaining proper bidirectional parent-child relationships.

## Test Structure

Each test class includes:
- Helper methods for tree verification
- Fixtures for test data
- Parameterized tests for multiple similar cases
- Clear assertions with helpful error messages

## Adding New Tests

To add new tests:

1. Add test sentences to the appropriate test class
2. Use the verification helper methods to check tree structure
3. Add specific assertions for the expected behavior
4. Document any new edge cases discovered

## Expected Behavior

When all tests pass, the parser should:
- Create valid tree structures without cycles
- Maintain proper parent-child relationships
- Handle all edge cases gracefully
- Decompose lemmas correctly when requested
- Group phrases hierarchically
- Identify and handle phrasal verbs

## Debugging Failed Tests

When a test fails:
1. Run with `-vv` for verbose output
2. Check the tree structure using the debug utilities
3. Verify parent-child relationships
4. Look for cycles or orphaned nodes
5. Ensure all tokens are accounted for in the tree 