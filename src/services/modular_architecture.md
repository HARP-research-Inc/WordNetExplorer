# Modular Sentence Parsing Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SentenceAnalyzer (v3)                          │
│                         (Main Orchestrator)                              │
└────────────────────────┬────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────────────────────┐
        │                                                 │
        ▼                                                 ▼
┌──────────────────┐                          ┌─────────────────────┐
│ spaCy Parser     │                          │ LinguisticColors    │
│ (External)       │                          │ • POS colors        │
└────────┬─────────┘                          │ • Edge colors       │
         │                                    │ • Node colors       │
         ▼                                    └─────────────────────┘
┌──────────────────┐
│ TokenAnalyzer    │
│ • Extract tokens │
│ • Get synsets    │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│ TokenDisambiguator   │
│ • Select best sense  │
│ • Filter technical   │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ ClauseIdentifier     │
│ • Find clauses       │
│ • Group tokens       │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐       ┌──────────────────────┐
│ ClauseBuilder        │◄──────┤ PhrasalVerbHandler   │
│ • Build clause tree  │       │ • Detect phrasal     │
│ • Handle adverbs     │       │ • Build verb phrases │
└────────┬─────────────┘       └──────────────────────┘
         │                              ▲
         │                              │
         ▼                              │
┌──────────────────────┐               │
│ SyntacticTree        ├───────────────┘
│ • SyntacticNode      │
│ • PhraseBuilder      │
│ • EdgeLabelMapper    │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ TreePostProcessor    │
│ • Group objects      │
│ • Restructure        │
│ • Clean presentation │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Final Tree Structure │
└──────────────────────┘
```

## Component Dependencies

```
sentence_analyzer_v3.py
├── token_analyzer.py
├── token_disambiguator.py
├── clause_identifier.py
├── clause_builder.py
│   ├── syntactic_tree.py
│   └── phrasal_verb_handler.py
├── tree_postprocessor.py
│   └── phrasal_verb_handler.py
└── linguistic_colors.py

syntactic_tree.py
└── token_analyzer.py (TokenInfo)

clause_builder.py
├── token_analyzer.py (TokenInfo)
├── syntactic_tree.py (SyntacticNode, PhraseBuilder, EdgeLabelMapper)
└── phrasal_verb_handler.py

tree_postprocessor.py
├── token_analyzer.py (TokenInfo)
├── syntactic_tree.py (SyntacticNode)
└── phrasal_verb_handler.py
```

## Data Flow

1. **Input**: Raw sentence text
2. **spaCy Parsing**: Creates Doc object with tokens
3. **Token Analysis**: Extract linguistic features and synsets
4. **Disambiguation**: Select best word senses
5. **Clause Identification**: Find clause boundaries
6. **Tree Building**: 
   - Create nodes for each token
   - Build phrases (noun, prep, verb)
   - Connect with appropriate edges
7. **Post-Processing**:
   - Group related objects
   - Restructure for visualization
   - Handle special cases
8. **Output**: SentenceAnalysis with syntactic tree

## Module Responsibilities

| Module | Lines | Responsibility |
|--------|-------|----------------|
| `token_analyzer.py` | 122 | Token feature extraction |
| `token_disambiguator.py` | 121 | Word sense disambiguation |
| `syntactic_tree.py` | 275 | Tree structures and phrase building |
| `clause_identifier.py` | 70 | Clause boundary detection |
| `clause_builder.py` | 226 | Clause tree construction |
| `tree_postprocessor.py` | 323 | Tree refinement and cleanup |
| `phrasal_verb_handler.py` | 111 | Phrasal verb handling |
| `linguistic_colors.py` | 83 | Color constants |
| `sentence_analyzer_v3.py` | 219 | Main orchestration |
| **Total** | **1,550** | Full system |

Compare to original: `sentence_analyzer.py` (679 lines)

## Key Design Benefits

1. **Modularity**: Average module size ~172 lines (vs 679 monolithic)
2. **Testability**: Each component can be tested independently
3. **Reusability**: Components can be used in other contexts
4. **Maintainability**: Changes are localized to specific modules
5. **Clarity**: Each module has a single, clear purpose
6. **Extensibility**: New features can be added as new modules
