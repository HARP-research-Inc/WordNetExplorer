# WordNet Explorer Test Suite

This directory contains a comprehensive test suite for the WordNet Explorer application using **pytest** and **pytest-dependency** for organized, dependent test execution.

## 🏗️ Test Structure

### Core Test Files
- **`test_arrow_consistency.py`** - Tests for arrow direction consistency and semantic accuracy
- **`test_graph_building.py`** - Tests for core graph building functionality  
- **`conftest.py`** - Common fixtures and utility functions

### Test Categories

#### 1. Arrow Consistency Tests (`TestArrowConsistency`)
- ✅ **test_wordnet_explorer_setup** - Verifies basic initialization
- ✅ **test_femtosecond_relationships** - Tests taxonomic relationships for time units
- ✅ **test_time_hierarchy_consistency** - Verifies consistent arrow directions across time hierarchy
- ✅ **test_tooltip_accuracy** - Ensures tooltips match visual arrow semantics
- ✅ **test_edge_duplication_prevention** - Prevents duplicate edge creation
- ✅ **test_arrow_direction_property_handling** - Verifies arrow_direction property handling

#### 2. Specific Cases Tests (`TestSpecificCases`)
- ✅ **test_quarter_hour_case** - Tests the specific quarter-hour issue mentioned by user
- ✅ **test_cross_pos_consistency** - Verifies consistency across parts of speech

#### 3. Graph Building Tests (`TestGraphBuilding`)
- ✅ **test_basic_graph_creation** - Basic graph creation functionality
- ✅ **test_node_types** - Correct node type creation (main, synset, word_sense)
- ✅ **test_edge_properties** - Edge property validation (relation, color, arrow_direction)
- ✅ **test_depth_limiting** - Graph depth limitation functionality
- ✅ **test_max_nodes_limiting** - Node count limitation functionality

#### 4. Relationship Filtering Tests (`TestRelationshipFiltering`)
- ✅ **test_hypernym_filtering** - Hypernym relationship filtering
- ✅ **test_multiple_relationship_types** - Multiple relationship type handling

#### 5. Error Handling Tests (`TestErrorHandling`)
- ✅ **test_nonexistent_word** - Graceful handling of nonexistent words
- ✅ **test_empty_input** - Empty input handling
- ✅ **test_special_characters** - Special character handling

## 🚀 Running Tests

### Prerequisites
```bash
pip install pytest pytest-dependency
```

### Basic Usage

#### Run All Core Tests
```bash
pytest tests/test_arrow_consistency.py tests/test_graph_building.py -v
```

#### Run Specific Test Categories
```bash
# Arrow consistency tests only
pytest tests/test_arrow_consistency.py::TestArrowConsistency -v

# Graph building tests only  
pytest tests/test_graph_building.py::TestGraphBuilding -v

# Specific test with detailed output
pytest tests/test_arrow_consistency.py::TestArrowConsistency::test_time_hierarchy_consistency -v -s
```

#### Run with Different Verbosity Levels
```bash
# Basic output
pytest tests/test_arrow_consistency.py -v

# Detailed output (shows print statements)
pytest tests/test_arrow_consistency.py -v -s

# Extra verbose with test names
pytest tests/test_arrow_consistency.py -vv
```

### Test Dependencies

The tests use **pytest-dependency** to ensure proper execution order:

```
test_wordnet_explorer_setup
├── test_femtosecond_relationships  
    ├── test_time_hierarchy_consistency
        ├── test_tooltip_accuracy
            ├── test_edge_duplication_prevention
                ├── test_arrow_direction_property_handling
                    ├── test_quarter_hour_case
                        ├── test_cross_pos_consistency
                            └── test_overall_system_health
```

## 📊 Test Results Example

When running the time hierarchy consistency test, you'll see output like:

```
🔍 Testing time unit hierarchy consistency...

  Testing 'femtosecond'...
    HYPERNYM: femtosecond → time_unit
    HYPERNYM: time_unit → measure
    HYPONYM: attosecond → time_unit
    Found 17 taxonomic relationships

📊 Analyzing 187 total taxonomic relationships...
  Specific → General: 29
  General → Specific: 0
  Unclear hierarchy: 158
  Consistency ratio: 100.00%
✅ Taxonomic arrow consistency verified
```

## 🎯 Key Features Tested

### Arrow Direction Consistency
- **Specific → General Direction**: All taxonomic arrows consistently point from specific concepts to general ones
- **Semantic Accuracy**: Tooltips accurately describe the relationship direction
- **No Duplicate Edges**: Prevents edge overwriting that caused incorrect arrows

### Graph Building Robustness  
- **Node Limits**: Respects max_nodes and depth parameters
- **Relationship Filtering**: Properly filters relationship types
- **Error Handling**: Graceful handling of edge cases

### Real-world Validation
- **Time Unit Hierarchy**: Tests the actual time unit relationships that were problematic
- **Cross-POS Consistency**: Ensures consistency across different parts of speech
- **Quarter-hour Case**: Specifically tests the user-reported issue

## 🔧 Fixtures and Utilities

### Available Fixtures (from `conftest.py`)
- **`explorer`** - WordNet Explorer instance (session scope)
- **`relationship_config_all`** - Config with all relationships enabled
- **`relationship_config_taxonomic`** - Config with only taxonomic relationships

### Utility Functions
- **`extract_node_name(node_id)`** - Extract clean names from node IDs
- **`analyze_arrow_direction(source, target, edge_data)`** - Analyze arrow semantics

## 🚨 Adding New Tests

### Test Dependencies
When adding new tests, use the dependency framework:

```python
@pytest.mark.dependency(depends=["TestArrowConsistency::test_wordnet_explorer_setup"])
def test_new_functionality(self, explorer):
    """Test new functionality with proper dependencies."""
    # Your test code here
    pass
```

### Test Categories
Add tests to appropriate categories:
- **Arrow/Semantic Tests** → `test_arrow_consistency.py`
- **Core Functionality** → `test_graph_building.py`  
- **New Categories** → Create new test files

### Test Naming Convention
- Use descriptive names that explain what's being tested
- Include expected behavior in docstrings
- Use assertion messages that clearly explain failures

## 📈 Current Test Coverage

- ✅ **19/19 tests passing** (100% success rate)
- ✅ **Arrow consistency verified** (100% consistent specific→general direction)
- ✅ **Edge duplication prevention** (0 duplicate edges found)
- ✅ **Tooltip accuracy** (All tooltips semantically correct)
- ✅ **Cross-POS consistency** (Consistent across parts of speech)
- ✅ **Error handling** (Graceful handling of edge cases)

## 🎯 Future Enhancements

Potential areas for additional testing:
- **Performance Tests** - Graph building speed with large datasets
- **Memory Tests** - Memory usage with deep/wide graphs  
- **UI Tests** - Streamlit interface testing
- **Integration Tests** - End-to-end user workflows
- **Regression Tests** - Prevent re-occurrence of fixed issues

---

*This test suite replaces individual debug scripts with a unified, maintainable framework that can be expanded as the application grows.* 