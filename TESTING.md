# WordNet Explorer Testing Documentation

## Overview
Comprehensive testing framework ensuring reliability, consistency, and maintainability of the WordNet Explorer application using pytest and pytest-dependency.

## Test Structure

### Test Files
- **`test_arrow_consistency.py`** - Arrow direction and semantic accuracy tests (9 tests)
- **`test_graph_building.py`** - Core graph building functionality tests (5 tests)
- **`test_url_parameter_correlation.py`** - URL parameter correlation tests (7 tests) 🆕
- **`conftest.py`** - Shared fixtures and utilities
- **`pytest.ini`** - Test configuration

### Test Categories

#### 1. Arrow Consistency (9 tests)
Ensures all taxonomic relationships point from specific to general concepts:
- WordNet Explorer setup verification
- Femtosecond relationship consistency
- Time hierarchy arrow validation
- Comprehensive specific→abstract testing  
- Tooltip accuracy verification
- Edge duplication prevention
- Arrow direction property handling
- Enhanced color scheme validation
- Quarter-hour case and cross-POS consistency

#### 2. Graph Building (5 tests)
Validates core graph construction:
- Basic graph creation and node types
- Edge properties and relationship handling
- Depth and node limiting functionality
- Relationship filtering accuracy
- Error handling for edge cases

#### 3. URL Parameter Correlation (7 tests) 🆕
Ensures URL parameters correctly correlate with rendered settings:
- Parameter mapping completeness (bidirectional)
- Type conversion accuracy (string, int, float, boolean)
- Default settings correlation
- Settings-to-URL conversion
- Invalid parameter graceful handling
- Comprehensive round-trip testing
- Parameter precedence over defaults

#### 4. System Health (1 test)
Overall system validation across multiple scenarios

## Test Results

### Current Status
- **Total Tests:** 26 tests across 4 test files
- **Success Rate:** 100% (26/26 tests passing)
- **Coverage:** Arrow consistency, graph building, URL parameters, error handling

### Key Achievements Verified
✅ **100% taxonomic arrow consistency** (specific→general direction)
✅ **Zero duplicate edges** in graph construction  
✅ **Accurate semantic tooltips** matching visual arrows
✅ **Complete URL parameter correlation** with settings
✅ **Bidirectional parameter mapping** accuracy
✅ **Robust error handling** for edge cases
✅ **Cross-POS relationship consistency**
✅ **Enhanced color scheme validation**

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Categories
```bash
# Arrow consistency
pytest tests/test_arrow_consistency.py -v

# Graph building  
pytest tests/test_graph_building.py -v

# URL parameter correlation
pytest tests/test_url_parameter_correlation.py -v
```

### With Detailed Output
```bash
pytest tests/ -v -s
```

## Key Test Features

### Arrow Direction Analysis
Validates that taxonomic relationships maintain consistent semantic direction:
- Analyzes visual arrow direction vs. relationship semantics
- Prevents the original issue where arrows were drawn in generation order
- Ensures tooltips accurately describe the visual relationships

### URL Parameter Validation
Ensures URL state consistency with UI settings:
- Tests bidirectional parameter mapping
- Validates type conversions (string ↔ int/float/boolean)
- Verifies round-trip consistency (URL → Settings → URL)
- Handles invalid parameters gracefully
- Ensures proper precedence over default values

### Dependency Management
Uses pytest-dependency to ensure tests run in proper order:
- Setup tests run before functional tests
- Core functionality verified before advanced features
- System health validated after all components

### Comprehensive Edge Case Testing
- Invalid word inputs
- Empty inputs and special characters
- Out-of-range parameter values
- Missing or malformed data
- Cross-part-of-speech consistency

## Test Data

### Common Test Words
- **Time Units:** femtosecond, picosecond, microsecond, second, minute, hour
- **Animals:** dog, cat, bird, mammal, vertebrate  
- **Objects:** car, vehicle, chair, furniture, table
- **Abstract Concepts:** emotion, happiness, sadness, feeling
- **Actions:** run, walk, move, travel
- **Properties:** big, large, huge, small, tiny

### URL Parameter Test Cases
- Valid type conversions and edge cases
- Default value correlation
- Bidirectional mapping verification
- Invalid parameter handling
- Round-trip consistency validation

## Dependencies

### Required Packages
```
pytest>=7.0.0
pytest-dependency>=0.5.1
```

### System Requirements
- WordNet corpus (via NLTK)
- NetworkX for graph operations
- Source code access (`src/` directory)

## Configuration

### pytest.ini
Defines test discovery, markers, and output formatting:
- Custom markers for test organization
- Dependency tracking setup
- Warning suppression for cleaner output

### Test Markers
- `dependency` - Tests with execution dependencies
- `arrows` - Arrow consistency related
- `graph` - Graph building related  
- `url_params` - URL parameter handling 🆕
- `integration` - Integration tests
- `unit` - Unit tests
- `slow` - Performance-sensitive tests

## Maintenance

### Adding New Tests
1. Choose appropriate test file based on functionality
2. Use dependency markers if execution order matters
3. Follow naming conventions and include descriptive docstrings
4. Add to appropriate test category in documentation

### Test Evolution
The test suite has evolved from individual debug scripts to a unified framework:
- **Previously:** 6+ individual debug scripts
- **Currently:** Unified pytest framework with 26 comprehensive tests
- **Benefits:** Better organization, dependency management, comprehensive coverage

## Integration with Development

### CI/CD Ready
Tests are designed for automated execution:
- No user interaction required
- Comprehensive error reporting
- Dependency-aware execution order

### Debugging Support
Detailed test output includes:
- Arrow direction analysis
- Relationship statistics  
- URL parameter conversion details
- Error handling verification
- Graph construction metrics

## Future Enhancements

### Potential Areas
- Performance benchmarking tests
- Memory usage validation
- UI component testing (Streamlit)
- End-to-end user workflow tests
- Regression test automation

### Scalability
Framework designed to scale with application growth:
- Modular test organization
- Reusable fixtures and utilities
- Clear separation of concerns
- Extensible marker system

---

This testing framework ensures WordNet Explorer maintains high quality and reliability while supporting continued development and feature enhancement. 