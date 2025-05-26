# Testing Documentation

## Overview
This directory contains comprehensive testing documentation for the WordNet Explorer application, including test procedures, validation criteria, and debugging guides.

## Test Categories

### 🔧 Bug Fix Tests
- **[Session State Widget Fix](session-state-widget-fix.md)** - Tests for the session state widget modification error fix
- **[Double-Enter Bug Fix](double-enter-bug-fix.md)** - Tests for navigation input field synchronization

### 🧪 Feature Tests
- **[Sense Feature Tests](../../../test_sense_feature.py)** - Automated tests for word sense functionality
- **[Graph Structure Tests](../../../test_graph_structure.py)** - Automated tests for graph data structure
- **[Root Connections Tests](../../../test_root_connections.py)** - Automated tests for root word connections

### 🔍 Integration Tests
Located in `tests/integration/` directory:
- End-to-end navigation testing
- UI component integration testing
- Data flow validation

### 🎯 Unit Tests
Located in `tests/unit/` directory:
- Individual component testing
- Function-level validation
- Mock data testing

## Quick Test Checklist

### Pre-Release Testing
- [ ] Session state widget functionality
- [ ] Double-enter bug resolution
- [ ] History navigation
- [ ] URL parameter navigation
- [ ] Graph rendering
- [ ] Word sense display
- [ ] Search functionality

### Performance Testing
- [ ] Large graph rendering
- [ ] Memory usage validation
- [ ] Response time measurement
- [ ] Browser compatibility

### Accessibility Testing
- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Color contrast validation
- [ ] Focus management

## Test Environment Setup

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python run_app.py
```

### Debug Mode
1. Open application sidebar
2. Enable "Debug Mode" checkbox
3. Monitor console for detailed logs

### Browser Setup
- Clear cache and cookies
- Disable browser extensions (for clean testing)
- Use incognito/private mode for isolated sessions

## Running Automated Tests

### Unit Tests
```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest test_sense_feature.py
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration/

# Run with verbose output
pytest tests/integration/ -v
```

### Coverage Report
```bash
# Generate coverage report
pytest --cov=src tests/
```

## Test Data

### Sample Words
Common test words used across test suites:
- **sheep** - Basic noun with clear relationships
- **dog** - Common animal with multiple senses
- **run** - Verb with multiple meanings
- **bank** - Noun with distinct senses (financial/river)

### Test Fixtures
Located in `tests/fixtures/`:
- Sample WordNet data
- Mock API responses
- Test configuration files

## Debugging Failed Tests

### Common Issues
1. **Session State Conflicts**
   - Clear browser storage
   - Restart application
   - Check for widget key conflicts

2. **Navigation Failures**
   - Verify URL parameter handling
   - Check session state synchronization
   - Monitor debug logs

3. **Graph Rendering Issues**
   - Check browser console for JavaScript errors
   - Verify data format
   - Test with different browsers

### Debug Tools
- Browser Developer Tools
- Streamlit debug mode
- Application logging
- Network request monitoring

## Contributing to Tests

### Adding New Tests
1. Create test file in appropriate directory
2. Follow naming convention: `test_[feature_name].py`
3. Include docstrings and comments
4. Add to relevant test suite

### Test Documentation
1. Document test purpose and scope
2. Include setup and teardown procedures
3. Specify expected results
4. Add troubleshooting notes

## Related Documentation
- [User Guides](../guides/README.md)
- [API Documentation](../api/README.md)
- [Troubleshooting](../troubleshooting/README.md)
- [Project README](../../../README.md) 