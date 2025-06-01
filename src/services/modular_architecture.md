# Modular Sentence Parsing Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SentenceAnalyzerV2                          │
│  (Main orchestrator - sentence_analyzer_v2.py)                  │
├─────────────────────────────────────────────────────────────────┤
│  • Manages spaCy model loading                                  │
│  • Coordinates all components                                   │
│  • Returns SentenceAnalysis object                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │ Uses
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Component Modules                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐  ┌──────────────────────┐            │
│  │   TokenAnalyzer     │  │  TokenDisambiguator  │            │
│  │ (token_analyzer.py) │  │(token_disambiguator.py)           │
│  ├─────────────────────┤  ├──────────────────────┤            │
│  │ • Analyzes tokens   │  │ • Selects best sense │            │
│  │ • Gets synsets      │  │ • Filters technical  │            │
│  │ • Maps POS tags     │  │ • Context-aware      │            │
│  └─────────────────────┘  └──────────────────────┘            │
│                                                                 │
│  ┌─────────────────────┐  ┌──────────────────────┐            │
│  │   SyntacticTree     │  │  LinguisticColors    │            │
│  │(syntactic_tree.py)  │  │(linguistic_colors.py)│            │
│  ├─────────────────────┤  ├──────────────────────┤            │
│  │ • Tree structures   │  │ • POS tag colors     │            │
│  │ • Phrase builders   │  │ • Edge colors        │            │
│  │ • Edge mapping      │  │ • Node colors        │            │
│  └─────────────────────┘  └──────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Supporting Classes                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐  ┌──────────────────────┐            │
│  │  ClauseIdentifier   │  │   ClauseBuilder      │            │
│  │                     │  │                      │            │
│  ├─────────────────────┤  ├──────────────────────┤            │
│  │ • Finds clauses     │  │ • Builds clause tree │            │
│  │ • Groups tokens     │  │ • Attaches phrases   │            │
│  └─────────────────────┘  └──────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Data Flow:
1. Text → spaCy → TokenAnalyzer → TokenInfo[]
2. TokenInfo[] → TokenDisambiguator → Best synsets
3. TokenInfo[] → ClauseIdentifier → Clause boundaries
4. Clauses → ClauseBuilder → SyntacticTree
5. SyntacticTree → Visualization (using LinguisticColors)
```

## Key Benefits

✅ **Separation of Concerns** - Each module has one job  
✅ **Testability** - Components can be tested independently  
✅ **Reusability** - Modules can be used in other contexts  
✅ **Maintainability** - Easy to modify specific functionality  
✅ **Extensibility** - Simple to add new features 