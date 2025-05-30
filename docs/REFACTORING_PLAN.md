# WordNet Explorer Refactoring Plan

## Overview
This document outlines the comprehensive refactoring of WordNet Explorer to follow OOP best practices, SOLID principles, and implement consistent unit testing.

## Current Issues
1. **Mixed Responsibilities**: UI components contain business logic
2. **Tight Coupling**: Direct dependencies between layers
3. **Limited Testing**: Insufficient unit test coverage
4. **Import Errors**: Module organization issues
5. **No Dependency Injection**: Hard-coded dependencies

## Proposed Architecture

### 1. Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                    (Streamlit UI Components)                 │
├─────────────────────────────────────────────────────────────┤
│                     Application Layer                        │
│                    (Use Cases / Services)                    │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                           │
│                   (Business Logic / Entities)                │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                       │
│                 (External APIs / Persistence)                │
└─────────────────────────────────────────────────────────────┘
```

### 2. New Package Structure

```
src/
├── domain/                 # Core business logic
│   ├── entities/          # Domain models
│   │   ├── __init__.py
│   │   ├── word.py        # Word entity
│   │   ├── synset.py      # Synset entity
│   │   ├── graph.py       # Graph entity
│   │   └── relationship.py # Relationship types
│   ├── interfaces/        # Abstract interfaces
│   │   ├── __init__.py
│   │   ├── word_repository.py
│   │   ├── graph_builder.py
│   │   └── graph_visualizer.py
│   └── services/          # Domain services
│       ├── __init__.py
│       ├── graph_service.py
│       └── relationship_service.py
│
├── application/           # Application business rules
│   ├── use_cases/        # Use case implementations
│   │   ├── __init__.py
│   │   ├── explore_word.py
│   │   ├── explore_synset.py
│   │   ├── export_graph.py
│   │   └── import_graph.py
│   └── dto/              # Data Transfer Objects
│       ├── __init__.py
│       ├── graph_settings.py
│       └── export_format.py
│
├── infrastructure/        # External interfaces
│   ├── wordnet/          # WordNet implementation
│   │   ├── __init__.py
│   │   ├── nltk_repository.py
│   │   └── wordnet_mapper.py
│   ├── visualization/    # Graph visualization
│   │   ├── __init__.py
│   │   ├── pyvis_visualizer.py
│   │   └── graph_layout.py
│   └── persistence/      # File I/O
│       ├── __init__.py
│       ├── json_serializer.py
│       └── html_exporter.py
│
├── presentation/         # UI Layer
│   ├── streamlit/       # Streamlit components
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── pages/
│   │   ├── components/
│   │   └── utils/
│   └── cli/            # CLI interface
│       ├── __init__.py
│       └── commands.py
│
└── shared/             # Shared utilities
    ├── constants.py
    ├── exceptions.py
    └── validators.py
```

### 3. Key Design Patterns

#### 3.1 Repository Pattern
```python
# domain/interfaces/word_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities import Word, Synset

class WordRepository(ABC):
    @abstractmethod
    def get_word(self, word: str) -> Optional[Word]:
        pass
    
    @abstractmethod
    def get_synsets(self, word: str) -> List[Synset]:
        pass
    
    @abstractmethod
    def get_relationships(self, synset: Synset, 
                         relationship_type: str) -> List[Synset]:
        pass
```

#### 3.2 Factory Pattern
```python
# domain/services/graph_builder_factory.py
from domain.interfaces import GraphBuilder
from infrastructure.visualization import PyvisGraphBuilder

class GraphBuilderFactory:
    @staticmethod
    def create(builder_type: str = "pyvis") -> GraphBuilder:
        if builder_type == "pyvis":
            return PyvisGraphBuilder()
        raise ValueError(f"Unknown builder type: {builder_type}")
```

#### 3.3 Strategy Pattern
```python
# domain/interfaces/layout_strategy.py
from abc import ABC, abstractmethod
from domain.entities import Graph

class LayoutStrategy(ABC):
    @abstractmethod
    def apply_layout(self, graph: Graph) -> Graph:
        pass
```

#### 3.4 Dependency Injection
```python
# application/use_cases/explore_word.py
from domain.interfaces import WordRepository, GraphBuilder
from domain.entities import Graph

class ExploreWordUseCase:
    def __init__(self, 
                 word_repository: WordRepository,
                 graph_builder: GraphBuilder):
        self._word_repository = word_repository
        self._graph_builder = graph_builder
    
    def execute(self, word: str, settings: dict) -> Graph:
        # Use case implementation
        pass
```

### 4. Testing Strategy

#### 4.1 Test Structure
```
tests/
├── unit/                    # Unit tests
│   ├── domain/
│   │   ├── entities/
│   │   ├── services/
│   │   └── interfaces/
│   ├── application/
│   │   └── use_cases/
│   └── infrastructure/
│
├── integration/            # Integration tests
│   ├── test_wordnet_integration.py
│   └── test_visualization_integration.py
│
├── e2e/                   # End-to-end tests
│   └── test_streamlit_app.py
│
├── fixtures/              # Test fixtures
│   ├── sample_words.py
│   └── mock_data.py
│
└── conftest.py           # Pytest configuration
```

#### 4.2 Testing Principles
- **Unit Tests**: Test individual components in isolation
- **Mocking**: Use mocks for external dependencies
- **Test Coverage**: Aim for >80% code coverage
- **TDD**: Write tests before implementation
- **Fixtures**: Reusable test data

### 5. Implementation Steps

#### Phase 1: Core Domain (Week 1)
1. Create domain entities
2. Define interfaces
3. Implement domain services
4. Write unit tests

#### Phase 2: Infrastructure (Week 2)
1. Implement WordNet repository
2. Create visualization adapters
3. Build serialization services
4. Write integration tests

#### Phase 3: Application Layer (Week 3)
1. Implement use cases
2. Create DTOs
3. Add validation
4. Write use case tests

#### Phase 4: Presentation Layer (Week 4)
1. Refactor Streamlit components
2. Implement dependency injection
3. Create component tests
4. End-to-end testing

#### Phase 5: Migration (Week 5)
1. Create migration scripts
2. Update documentation
3. Performance testing
4. Deploy refactored version

### 6. Example Implementations

#### 6.1 Domain Entity
```python
# domain/entities/word.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass(frozen=True)
class Word:
    """Immutable Word entity."""
    text: str
    pos: Optional[str] = None
    
    def __post_init__(self):
        if not self.text:
            raise ValueError("Word text cannot be empty")
        
        # Normalize text
        object.__setattr__(self, 'text', self.text.strip().lower())
    
    @property
    def is_valid(self) -> bool:
        """Check if word is valid."""
        return bool(self.text) and self.text.isalpha()
```

#### 6.2 Use Case with Tests
```python
# application/use_cases/explore_word.py
from typing import Dict, Any
from domain.interfaces import WordRepository, GraphBuilder
from domain.entities import Graph, Word
from application.dto import GraphSettings

class ExploreWordUseCase:
    def __init__(self, 
                 word_repository: WordRepository,
                 graph_builder: GraphBuilder):
        self._word_repo = word_repository
        self._graph_builder = graph_builder
    
    def execute(self, word_text: str, 
                settings: GraphSettings) -> Graph:
        # Validate input
        word = Word(text=word_text)
        if not word.is_valid:
            raise ValueError(f"Invalid word: {word_text}")
        
        # Get synsets
        synsets = self._word_repo.get_synsets(word.text)
        if not synsets:
            return Graph.empty()
        
        # Build graph
        return self._graph_builder.build(
            word=word,
            synsets=synsets,
            settings=settings
        )

# tests/unit/application/use_cases/test_explore_word.py
import pytest
from unittest.mock import Mock
from application.use_cases import ExploreWordUseCase
from domain.entities import Word, Graph

class TestExploreWordUseCase:
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def mock_builder(self):
        return Mock()
    
    @pytest.fixture
    def use_case(self, mock_repository, mock_builder):
        return ExploreWordUseCase(mock_repository, mock_builder)
    
    def test_execute_valid_word(self, use_case, mock_repository):
        # Arrange
        mock_repository.get_synsets.return_value = [Mock()]
        
        # Act
        result = use_case.execute("dog", Mock())
        
        # Assert
        assert isinstance(result, Graph)
        mock_repository.get_synsets.assert_called_once_with("dog")
    
    def test_execute_invalid_word_raises_error(self, use_case):
        # Act & Assert
        with pytest.raises(ValueError):
            use_case.execute("123", Mock())
```

### 7. Benefits of Refactoring

1. **Testability**: Each component can be tested in isolation
2. **Maintainability**: Clear separation of concerns
3. **Extensibility**: Easy to add new features
4. **Reusability**: Components can be reused
5. **Documentation**: Self-documenting code structure

### 8. Migration Strategy

1. **Parallel Development**: Keep old code while building new
2. **Feature Flags**: Gradually switch to new implementation
3. **Backward Compatibility**: Ensure existing functionality works
4. **Data Migration**: Convert existing data formats
5. **User Communication**: Inform users of changes

## Next Steps

1. Review and approve plan
2. Set up new package structure
3. Begin Phase 1 implementation
4. Create CI/CD pipeline for tests
5. Document as we go 