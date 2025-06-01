# Modular Sentence Parsing Architecture

This directory contains a highly modular sentence parsing system designed for maximum maintainability and extensibility.

## 📦 Components Overview

### Core Analysis Modules

#### 1. `token_analyzer.py`
- **Purpose**: Analyzes individual tokens and retrieves WordNet synsets
- **Key Classes**: 
  - `TokenInfo`: Data class containing token linguistic information
  - `TokenAnalyzer`: Extracts token features and synsets
- **Responsibilities**:
  - Extract POS tags, dependencies, lemmas
  - Retrieve all possible WordNet synsets for each token

#### 2. `token_disambiguator.py`
- **Purpose**: Selects the best WordNet sense for each token based on context
- **Key Classes**: `TokenDisambiguator`
- **Responsibilities**:
  - Filter out overly technical or domain-specific definitions
  - Select most appropriate sense based on context

### Tree Building Modules

#### 3. `syntactic_tree.py`
- **Purpose**: Defines tree structures and phrase building utilities
- **Key Classes**:
  - `SyntacticNode`: Core tree node structure
  - `PhraseBuilder`: Builds noun phrases and prepositional phrases
  - `EdgeLabelMapper`: Maps dependencies to edge labels
- **Responsibilities**:
  - Create hierarchical noun phrases with proper layering
  - Build prepositional phrases
  - Map dependency relations to tree edge labels

#### 4. `clause_identifier.py`
- **Purpose**: Identifies clause boundaries in sentences
- **Key Classes**: `ClauseIdentifier`
- **Responsibilities**:
  - Detect main and subordinate clauses
  - Group tokens by their clause membership
  - Handle simple and complex sentence structures

#### 5. `clause_builder.py`
- **Purpose**: Builds syntactic tree structures for clauses
- **Key Classes**: `ClauseBuilder`
- **Responsibilities**:
  - Create word nodes for tokens
  - Build phrases from tokens
  - Handle sentence-level adverbs
  - Attach phrases to appropriate parents

#### 6. `tree_postprocessor.py`
- **Purpose**: Refines tree structures for better visualization
- **Key Classes**: `TreePostProcessor`
- **Responsibilities**:
  - Group related object phrases
  - Reinterpret phrasal verbs
  - Restructure clauses for cleaner presentation
  - Move punctuation to appropriate positions
  - Apply lemma decomposition (when enabled)

### Utility Modules

#### 7. `phrasal_verb_handler.py`
- **Purpose**: Identifies and handles multi-word verb constructions
- **Key Classes**: `PhrasalVerbHandler`
- **Responsibilities**:
  - Detect phrasal verbs (e.g., "run over", "look up")
  - Create verb phrase nodes
  - Handle verb particles correctly

#### 8. `lemma_decomposer.py`
- **Purpose**: Decomposes words into lemmas with grammatical annotations
- **Key Classes**: `LemmaDecomposer`
- **Responsibilities**:
  - Identify words that differ from their lemmas
  - Create hierarchical structure showing lemma + grammatical form
  - Generate appropriate edge labels (past, plural, comparative, etc.)
  - Handle verbs, nouns, adjectives, and adverbs

#### 9. `linguistic_colors.py`
- **Purpose**: Centralized color mappings for visualization
- **Key Classes**: `LinguisticColors`
- **Data**:
  - POS tag colors
  - Dependency relation colors
  - Edge colors for syntactic tree
  - Node type colors
  - Lemma decomposition edge colors

### Main Orchestrators

#### 10. `sentence_analyzer_v2.py` (Legacy)
- **Purpose**: Original modular implementation
- **Status**: Fully functional but larger file

#### 11. `sentence_analyzer_v3.py` (Recommended)
- **Purpose**: Streamlined orchestrator using all modular components
- **Key Classes**:
  - `SentenceAnalysis`: Output data structure
  - `SentenceAnalyzer`: Main orchestrator
- **Workflow**:
  1. Parse with spaCy
  2. Analyze tokens
  3. Disambiguate senses
  4. Identify clauses
  5. Build clause trees
  6. Post-process for visualization
  7. Apply lemma decomposition (optional)

## 🔄 Processing Pipeline

```
Input Sentence
    ↓
spaCy Parsing
    ↓
Token Analysis (token_analyzer.py)
    ↓
Sense Disambiguation (token_disambiguator.py)
    ↓
Clause Identification (clause_identifier.py)
    ↓
For each clause:
    ├── Phrasal Verb Detection (phrasal_verb_handler.py)
    ├── Phrase Building (syntactic_tree.py)
    └── Clause Tree Construction (clause_builder.py)
    ↓
Post-Processing (tree_postprocessor.py)
    ├── Group objects
    ├── Restructure clauses
    └── Lemma Decomposition (optional, lemma_decomposer.py)
    ↓
Final Syntactic Tree
```

## 🎯 Design Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Loose Coupling**: Components communicate through well-defined interfaces
3. **High Cohesion**: Related functionality is grouped together
4. **Testability**: Each component can be tested in isolation
5. **Extensibility**: New features can be added without modifying existing code

## 🔧 Usage Example

```python
from src.services.sentence_analyzer_v3 import SentenceAnalyzer

analyzer = SentenceAnalyzer()

# Basic analysis
analysis = analyzer.analyze_sentence("I gleefully ran over my fat friend with a scooter")

# With lemma decomposition
analysis = analyzer.analyze_sentence(
    "The dogs were running quickly",
    decompose_lemmas=True
)

# Access results
print(f"Tokens: {len(analysis.tokens)}")
print(f"Root: {analysis.tokens[analysis.root_index].text}")
print(f"Tree: {analysis.syntactic_tree}")
```

## 📊 Key Improvements

1. **Modular Architecture**: 11 focused modules instead of 1-2 large files
2. **Hierarchical Noun Phrases**: Proper layering of determiners, adjectives, etc.
3. **Phrasal Verb Support**: Correctly handles multi-word verbs
4. **Clean Visualization**: Post-processed trees for better display
5. **Maintainable Code**: Each module is small and focused
6. **Lemma Decomposition**: Optional feature to show word forms with grammatical info

## 🔄 Migration Notes

To use the new modular system in existing code:

```python
# Old import
from src.services.sentence_analyzer import SentenceAnalyzer

# New import (recommended)
from src.services.sentence_analyzer_v3 import SentenceAnalyzer

# The API remains the same!
```

The new system maintains backward compatibility while providing cleaner, more maintainable code. 