# Modular Sentence Parsing Architecture

This document describes the modularized sentence parsing system, refactored from the monolithic `sentence_analyzer.py` into focused, reusable components.

## Overview

The sentence parsing functionality has been broken down into the following modules:

### 1. `token_analyzer.py`
**Purpose**: Analyzes individual tokens and retrieves WordNet synsets

**Key Components**:
- `TokenInfo`: Data class representing parsed token information
- `TokenAnalyzer`: Handles token analysis and synset retrieval
  - Maps POS tags to WordNet POS
  - Special handling for adpositions (ADP) that might be adverbs
  - Filters out function words without synsets

### 2. `token_disambiguator.py`
**Purpose**: Selects the best synset for tokens based on context

**Key Components**:
- `TokenDisambiguator`: Handles word sense disambiguation
  - Filters technical senses for common words
  - Special handling for phrasal verb particles
  - Context-aware sense selection

### 3. `syntactic_tree.py`
**Purpose**: Data structures and builders for syntactic trees

**Key Components**:
- `SyntacticNode`: Tree node structure with parent/child relationships
- `PhraseBuilder`: Builds phrase structures (noun phrases, prep phrases)
- `EdgeLabelMapper`: Maps dependency relations to semantic edge labels

### 4. `linguistic_colors.py`
**Purpose**: Centralized color mappings for visualization

**Key Components**:
- `LinguisticColors`: Static methods and constants for colors
  - POS tag colors
  - Dependency relation colors
  - Edge color mappings
  - Node type colors

### 5. `sentence_analyzer_v2.py`
**Purpose**: Main analyzer that orchestrates all components

**Key Components**:
- `SentenceAnalysis`: Data class for complete sentence analysis
- `SentenceAnalyzerV2`: Main analyzer class
  - Uses all modular components
  - Lazy loads spaCy model
  - Builds syntactic tree with clauses and phrases
- `ClauseIdentifier`: Identifies clause boundaries
- `ClauseBuilder`: Builds clause structures using phrase builders

## Benefits of Modularization

1. **Separation of Concerns**: Each module has a single, focused responsibility
2. **Reusability**: Components can be used independently in other parts of the system
3. **Testability**: Each module can be unit tested in isolation
4. **Maintainability**: Easier to modify or extend specific functionality
5. **Readability**: Smaller, focused files are easier to understand

## Usage Example

```python
from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2

# Create analyzer
analyzer = SentenceAnalyzerV2()

# Analyze a sentence
analysis = analyzer.analyze_sentence("The quick brown fox jumps over the lazy dog.")

# Access results
for token in analysis.tokens:
    if token.best_synset:
        print(f"{token.text}: {token.best_synset[1]}")

# Access syntactic tree
print(f"Root node type: {analysis.syntactic_tree.node_type}")
```

## Extension Points

The modular architecture makes it easy to extend functionality:

1. **Add new phrase types**: Extend `PhraseBuilder` with methods for verb phrases, adjective phrases, etc.
2. **Improve disambiguation**: Replace simple heuristics in `TokenDisambiguator` with ML-based approaches
3. **Custom visualizations**: Use `LinguisticColors` constants for consistent styling
4. **Alternative parsers**: Replace spaCy with other NLP libraries by modifying `TokenAnalyzer`

## Migration Notes

To use the new modular system:

1. Replace imports:
   ```python
   # Old
   from src.services.sentence_analyzer import SentenceAnalyzer
   
   # New
   from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2
   ```

2. The API remains the same - `analyze_sentence()` returns the same `SentenceAnalysis` object

3. Color methods are now accessed via the `colors` attribute:
   ```python
   # Old
   analyzer.get_pos_color(tag)
   
   # New
   analyzer.colors.get_pos_color(tag)
   ```

## Future Improvements

1. **Advanced Disambiguation**: Integrate with the existing `sense_similarity.py` module for context-based disambiguation
2. **Coreference Resolution**: Add module for tracking entity references across clauses
3. **Semantic Role Labeling**: Add module for identifying semantic roles (agent, patient, etc.)
4. **Multi-language Support**: Abstract language-specific logic into separate modules 