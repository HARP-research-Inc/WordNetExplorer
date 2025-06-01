# Modular Sentence Parsing System Design

## Overview
A robust, modular system for parsing sentences with comprehensive unit testing and edge case handling.

## Architecture Principles
1. **Single Responsibility**: Each component has one clear purpose
2. **Testability**: All functions are pure when possible, with clear inputs/outputs
3. **Edge Case Handling**: Explicit handling of edge cases with tests
4. **Immutability**: Data structures are immutable where possible
5. **Clear Interfaces**: Well-defined interfaces between components

## Core Components

### 1. Token Processor
**Responsibility**: Process individual tokens from spaCy
**Functions**:
- `extract_token_features(token) -> TokenFeatures`
- `normalize_token_text(text) -> str`
- `get_token_lemma(token) -> str`
- `is_content_word(token) -> bool`
- `is_function_word(token) -> bool`

### 2. Dependency Analyzer
**Responsibility**: Analyze dependency relationships
**Functions**:
- `get_children(token, doc) -> List[Token]`
- `get_ancestors(token) -> List[Token]`
- `find_head_verb(token) -> Optional[Token]`
- `get_dependency_distance(token1, token2) -> int`
- `is_dependent_of(child, parent) -> bool`

### 3. Phrase Detector
**Responsibility**: Detect various phrase types
**Functions**:
- `detect_noun_phrases(tokens) -> List[PhraseSpan]`
- `detect_verb_phrases(tokens) -> List[PhraseSpan]`
- `detect_prepositional_phrases(tokens) -> List[PhraseSpan]`
- `detect_adjectival_phrases(tokens) -> List[PhraseSpan]`
- `detect_adverbial_phrases(tokens) -> List[PhraseSpan]`

### 4. Clause Segmenter
**Responsibility**: Segment sentences into clauses
**Functions**:
- `find_clause_boundaries(tokens) -> List[ClauseBoundary]`
- `classify_clause_type(clause_tokens) -> ClauseType`
- `find_clause_relationships(clauses) -> List[ClauseRelation]`
- `is_subordinate_clause(clause) -> bool`
- `find_main_clause(clauses) -> Optional[Clause]`

### 5. Syntactic Tree Builder
**Responsibility**: Build hierarchical tree structures
**Functions**:
- `build_token_tree(tokens) -> SyntaxTree`
- `build_phrase_tree(phrases, tokens) -> SyntaxTree`
- `build_clause_tree(clauses) -> SyntaxTree`
- `merge_trees(trees) -> SyntaxTree`
- `validate_tree_structure(tree) -> List[ValidationError]`

### 6. WordNet Integrator
**Responsibility**: Integrate WordNet senses
**Functions**:
- `get_applicable_synsets(token) -> List[Synset]`
- `filter_synsets_by_pos(synsets, pos) -> List[Synset]`
- `rank_synsets_by_frequency(synsets) -> List[Synset]`
- `disambiguate_in_context(token, context) -> Optional[Synset]`
- `get_synset_definition(synset) -> str`

### 7. Edge Case Handler
**Responsibility**: Handle specific edge cases
**Functions**:
- `handle_phrasal_verbs(tokens) -> List[PhrasalVerb]`
- `handle_compound_nouns(tokens) -> List[CompoundNoun]`
- `handle_contractions(tokens) -> List[Contraction]`
- `handle_ellipsis(tokens) -> List[Ellipsis]`
- `handle_fragments(tokens) -> List[Fragment]`

### 8. Tree Visualizer
**Responsibility**: Convert trees to visualization format
**Functions**:
- `tree_to_graph_nodes(tree) -> List[GraphNode]`
- `tree_to_graph_edges(tree) -> List[GraphEdge]`
- `apply_visual_styling(nodes, edges) -> StyledGraph`
- `generate_node_tooltips(nodes) -> Dict[str, str]`
- `optimize_layout(graph) -> LayoutInfo`

## Data Structures

### TokenFeatures
```python
@dataclass(frozen=True)
class TokenFeatures:
    index: int
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    head: int
    is_space: bool
    is_punct: bool
    is_stop: bool
```

### PhraseSpan
```python
@dataclass(frozen=True)
class PhraseSpan:
    start: int
    end: int
    phrase_type: PhraseType
    head_index: int
    modifiers: List[int]
```

### ClauseBoundary
```python
@dataclass(frozen=True)
class ClauseBoundary:
    start: int
    end: int
    clause_type: ClauseType
    verb_indices: List[int]
    subject_indices: List[int]
```

## Testing Strategy

### Unit Tests
Each function will have comprehensive unit tests covering:
1. Normal cases
2. Edge cases
3. Error cases
4. Boundary conditions

### Test Categories
1. **Token Processing Tests**
   - Various POS tags
   - Special characters
   - Unicode handling
   - Empty tokens

2. **Dependency Tests**
   - Complex dependency trees
   - Circular dependencies
   - Missing heads
   - Multiple roots

3. **Phrase Detection Tests**
   - Nested phrases
   - Overlapping phrases
   - Single-word phrases
   - Complex modifiers

4. **Clause Segmentation Tests**
   - Simple sentences
   - Complex sentences
   - Fragments
   - Run-on sentences

5. **Tree Building Tests**
   - Balanced trees
   - Deep trees
   - Single-node trees
   - Disconnected components

6. **WordNet Integration Tests**
   - Common words
   - Rare words
   - Non-existent words
   - Multiple POS

7. **Edge Case Tests**
   - Phrasal verbs
   - Idioms
   - Contractions
   - Punctuation

## Error Handling

### Error Types
1. **ParseError**: When spaCy parsing fails
2. **InvalidTokenError**: When token data is corrupted
3. **TreeConstructionError**: When tree building fails
4. **WordNetError**: When WordNet lookup fails

### Recovery Strategies
1. Graceful degradation
2. Fallback to simpler analysis
3. Clear error messages
4. Partial results when possible

## Performance Considerations
1. Lazy loading of resources
2. Caching of common lookups
3. Efficient tree traversal
4. Minimal object creation

## Integration Points
1. SpaCy for base parsing
2. WordNet for semantic information
3. PyViz for visualization
4. Streamlit for UI

## Future Extensions
1. Multi-language support
2. Domain-specific parsing
3. Real-time parsing
4. Batch processing 