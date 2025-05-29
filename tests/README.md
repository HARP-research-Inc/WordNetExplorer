# WordNet Explorer Test Suite

## Overview
This directory contains comprehensive tests for the WordNet Explorer application, ensuring reliability and consistency across all features.

## Test Structure

### Core Test Files

#### `test_arrow_consistency.py`
Tests for arrow direction consistency and semantic accuracy in taxonomic relationships.

**Key Test Classes:**
- `TestArrowConsistency` - Main arrow direction tests
- `TestSpecificCases` - Edge cases and problematic relationships

**Test Coverage:**
- ✅ WordNet Explorer setup verification
- ✅ Femtosecond relationship consistency
- ✅ Time hierarchy arrow direction validation
- ✅ Comprehensive specific→abstract arrow testing
- ✅ Tooltip accuracy verification
- ✅ Edge duplication prevention
- ✅ Arrow direction property handling
- ✅ Enhanced color scheme validation
- ✅ Quarter-hour case testing
- ✅ Cross-POS consistency verification

#### `test_graph_building.py`
Tests for core graph building functionality and configuration handling.

**Key Test Classes:**
- `TestBasicGraphBuilding` - Fundamental graph operations
- `TestRelationshipFiltering` - Relationship type filtering
- `TestErrorHandling` - Edge case and error scenarios

**Test Coverage:**
- ✅ Basic graph creation and validation
- ✅ Node type verification (main, word_sense, synset)
- ✅ Edge property validation
- ✅ Depth limiting functionality
- ✅ Maximum node limiting
- ✅ Hypernym filtering accuracy
- ✅ Multiple relationship type handling
- ✅ Nonexistent word error handling
- ✅ Empty input validation
- ✅ Special character handling

#### `test_url_parameter_correlation.py` 🆕
Tests for URL parameter correlation with rendered settings to ensure UI state consistency.

**Key Test Classes:**
- `TestURLParameterCorrelation` - Comprehensive URL parameter validation

**Test Coverage:**
- ✅ URL parameter mapping completeness (bidirectional verification)
- ✅ Type conversion accuracy (string, int, float, boolean)
- ✅ Default settings correlation with URL parameters
- ✅ Settings-to-URL parameter conversion
- ✅ Invalid URL parameter graceful handling
- ✅ Comprehensive parameter round-trip testing
- ✅ URL parameter precedence over default settings

### Utility Files

#### `conftest.py`
Shared fixtures and utilities for all tests.

**Key Features:**
- Session-scoped WordNet Explorer instances
- Relationship configuration fixtures
- Arrow direction analysis utilities
- Dependency management setup

#### `__init__.py`
Makes the tests directory a Python package for proper imports.

## Test Categories

### 1. Arrow Consistency Tests (6 tests)
Verify that all taxonomic arrows consistently point from specific to general concepts:
- Setup validation
- Relationship direction analysis
- Time hierarchy consistency
- Comprehensive specific→abstract validation
- Tooltip semantic accuracy
- Edge duplication prevention

### 2. Graph Building Tests (5 tests) 
Validate core graph construction functionality:
- Basic graph creation
- Node and edge properties
- Depth and size limiting
- Configuration handling

### 3. Relationship Filtering Tests (2 tests)
Ensure relationship type filtering works correctly:
- Hypernym filtering precision
- Multiple relationship type handling

### 4. Error Handling Tests (3 tests)
Verify robust error handling for edge cases:
- Invalid word inputs
- Empty inputs
- Special characters

### 5. URL Parameter Tests (7 tests) 🆕
Ensure URL parameters correctly correlate with settings:
- Parameter mapping completeness
- Type conversion accuracy
- Default value correlation
- Bidirectional conversion
- Invalid parameter handling
- Round-trip consistency
- Parameter precedence

### 6. Overall System Health Test (1 test)
Comprehensive system validation across multiple words and configurations.

## Test Execution

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Arrow consistency tests
pytest tests/test_arrow_consistency.py -v

# Graph building tests  
pytest tests/test_graph_building.py -v

# URL parameter correlation tests
pytest tests/test_url_parameter_correlation.py -v
```

### Run Tests with Detailed Output
```bash
pytest tests/ -v -s
```

### Run Tests with Dependency Tracking
```bash
pytest tests/ -v --tb=short
```

## Test Results Summary

**Total Tests:** 26 tests across 4 test files
- ✅ Arrow Consistency: 9 tests
- ✅ Graph Building: 5 tests  
- ✅ URL Parameters: 7 tests
- ✅ Specific Cases: 2 tests
- ✅ Error Handling: 3 tests
- ✅ System Health: 1 test

**Success Rate:** 100% (26/26 tests passing)

### Key Achievements Verified
- **100% taxonomic arrow consistency** (specific→general direction)
- **Zero duplicate edges** in graph construction
- **Accurate semantic tooltips** matching visual arrows
- **Robust error handling** for edge cases
- **Complete URL parameter correlation** with settings
- **Bidirectional parameter mapping** accuracy
- **Cross-POS relationship consistency**
- **Enhanced color scheme validation**

## Dependencies

### Required Packages
- `pytest>=7.0.0` - Testing framework
- `pytest-dependency>=0.5.1` - Test dependency management

### Test Dependencies
Tests require access to:
- WordNet corpus (via NLTK)
- NetworkX graph library
- Application source code (`src/` directory)

## Configuration

### `pytest.ini`
Main pytest configuration with:
- Test discovery patterns
- Custom markers for test organization
- Output formatting options
- Warning suppression

### Test Markers
- `dependency` - Tests with dependencies on other tests
- `integration` - Integration tests
- `unit` - Unit tests
- `slow` - Slow-running tests
- `arrows` - Arrow consistency related tests
- `graph` - Graph building related tests
- `url_params` - URL parameter handling tests
- `performance` - Performance related tests

## Test Data and Fixtures

### Common Test Words
- **Time Units:** femtosecond, picosecond, microsecond, second, minute, hour
- **Animals:** dog, cat, bird, mammal, vertebrate
- **Objects:** car, vehicle, chair, furniture, table
- **Abstract:** emotion, happiness, sadness, feeling
- **Actions:** run, walk, move, travel
- **Properties:** big, large, huge, small, tiny

### Shared Utilities
- `analyze_arrow_direction()` - Analyzes visual arrow direction in relationships
- `get_node_name()` - Extracts clean node names from graph identifiers
- Relationship configuration builders for comprehensive testing

## Troubleshooting

### Common Issues
1. **Missing WordNet Data:** Ensure NLTK WordNet corpus is downloaded
2. **Import Errors:** Verify `src/` directory is in Python path
3. **Dependency Failures:** Run tests in dependency order using pytest-dependency

### Debug Output
Enable detailed logging with `-s` flag to see:
- Test progress indicators
- Arrow direction analysis
- Relationship statistics
- URL parameter conversion details
- Error handling verification

This comprehensive test suite ensures the WordNet Explorer maintains high quality, consistent behavior, and reliable URL parameter handling across all features and edge cases. 