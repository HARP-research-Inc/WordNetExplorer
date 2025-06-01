# Verb Phrase Structure Test Specification

## Overview

This document describes the expected verb phrase structure and the tests added to verify this behavior. The key principle is that verbs should be wrapped in phrase nodes with their arguments (subject, object, etc.) as sibling children.

## Expected Structure

### Basic Principle

Verbs are structured as **phrase nodes** containing:
- The verb itself as a child
- Subject as a sibling child 
- Object(s) as sibling children
- Other arguments and modifiers as siblings

### Examples

#### Simple SVO Sentence: "The cat eats fish."
```
verb_phrase
├── subj: noun_phrase("The cat")
├── verb: word("eats")
└── obj: word("fish")
```

#### Intransitive Verb: "The dog sleeps."
```
verb_phrase
├── subj: noun_phrase("The dog")
└── verb: word("sleeps")
```

#### Ditransitive Verb: "She gave him the book."
```
verb_phrase
├── subj: word("She")
├── verb: word("gave")
├── iobj: word("him")
└── dobj: noun_phrase("the book")
```

#### Auxiliary Verbs: "She has been running."
```
verb_phrase
├── subj: word("She")
├── aux: word("has")
├── aux: word("been")
└── verb: word("running")
```

#### Phrasal Verb: "She looked up the word."
```
verb_phrase
├── subj: word("She")
├── phrasal_verb: phrase("looked up")
│   ├── verb: word("looked")
│   └── particle: word("up")
└── obj: noun_phrase("the word")
```

## Tests Added to test_parser_integration.py

A new test class `TestVerbPhraseStructure` has been added with the following tests:

1. **test_simple_svo_verb_phrase** - Tests basic subject-verb-object sentences
2. **test_intransitive_verb_phrase** - Tests verbs with only subjects
3. **test_ditransitive_verb_phrase** - Tests verbs with direct and indirect objects
4. **test_auxiliary_verb_phrase** - Tests auxiliary verb inclusion
5. **test_phrasal_verb_structure** - Tests phrasal verbs within verb phrases
6. **test_verb_phrase_with_modifiers** - Tests adverbial modifiers
7. **test_complex_verb_phrase_dependencies** - Tests preservation of dependencies
8. **test_nested_verb_phrases** - Tests multiple verbs in sentences

## Key Differences from Current Implementation

### Current Behavior
- Verbs are often standalone word nodes
- Arguments (subject, object) may be attached to different parts of the tree
- Subjects might be attached to the clause level
- Objects might be children of the verb word node

### Expected Behavior
- Verbs are wrapped in phrase nodes
- All arguments are siblings within the verb phrase
- Clear hierarchical structure with verb phrase as organizing unit
- Preserves dependency relationships while grouping related elements

## Implementation Notes

These tests serve as a **specification** for the expected behavior. The actual implementation in the sentence analyzer modules would need to:

1. Create verb phrase nodes during parsing
2. Group verb arguments as siblings within the phrase
3. Handle special cases like phrasal verbs and auxiliaries
4. Maintain this structure through any post-processing steps

## Running the Tests

```bash
# Run just the verb phrase structure tests
python -m pytest tests/test_parser_integration.py::TestVerbPhraseStructure -v

# Run all integration tests
python -m pytest tests/test_parser_integration.py -v
```

## Why This Structure?

This verb phrase structure provides:
- **Clarity**: All verb arguments are clearly grouped together
- **Consistency**: Similar structure across different verb types
- **Accessibility**: Easy to find all arguments of a verb
- **Hierarchical Organization**: Natural grouping of related elements 