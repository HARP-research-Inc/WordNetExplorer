# Navigation System Guide

## Overview
The WordNet Explorer features a multi-modal navigation system that allows users to explore word relationships through various interaction methods. This guide explains how each navigation method works and how they integrate with the application's session state management.

## Navigation Methods

### 1. Text Input Navigation
**Primary Method**: Direct word entry in the sidebar input field

**How it works**:
1. User types a word in the input field
2. Presses Enter or clicks outside the field
3. Application processes the word and updates the graph
4. Word is added to search history

**Session State Updates**:
```python
st.session_state.current_word = entered_word
st.session_state.last_searched_word = entered_word
st.session_state.word_input = entered_word
```

### 2. History Navigation
**Method**: Clicking buttons in the search history panel

**How it works**:
1. User clicks a history button (e.g., "📝 sheep")
2. Application extracts the word from the button
3. Updates session state and input field
4. Reloads graph for the selected word

**Implementation**:
```python
if st.button(f"📝 {word}", key=f"hist_{word}"):
    st.session_state.current_word = word
    st.session_state.word_input = word
    st.rerun()
```

### 3. URL Parameter Navigation
**Method**: Direct URL manipulation with query parameters

**Supported Parameters**:
- `navigate_to=word` - Navigate to a specific word
- `debug=true` - Enable debug mode

**Example URLs**:
```
http://localhost:8513/?navigate_to=dog
http://localhost:8513/?navigate_to=sheep&debug=true
```

**Implementation**:
```python
navigate_to_word = st.query_params.get("navigate_to")
if navigate_to_word:
    st.session_state.current_word = navigate_to_word
    st.session_state.word_input = navigate_to_word
```

### 4. Graph Node Navigation (Future)
**Method**: Double-clicking nodes in the graph visualization

**Planned Implementation**:
1. User double-clicks a node in the graph
2. JavaScript event captures the clicked word
3. Streamlit receives the word via component communication
4. Session state updates and graph reloads

## Session State Management

### Core State Variables
The navigation system maintains several session state variables for consistency:

```python
# Primary word state
st.session_state.current_word          # Currently displayed word
st.session_state.last_searched_word    # Last word that was searched
st.session_state.word_input           # Input field value

# Navigation tracking
st.session_state.previous_word_input   # Previous input value
st.session_state.last_processed_word_input  # Last processed input

# History management
st.session_state.search_history       # List of searched words
```

### State Synchronization Pattern
All navigation methods follow this consistent pattern:

```python
def navigate_to_word(target_word):
    """Standard navigation pattern for all methods"""
    st.session_state.current_word = target_word
    st.session_state.last_searched_word = target_word
    st.session_state.previous_word_input = target_word
    st.session_state.last_processed_word_input = target_word
    st.session_state.word_input = target_word  # Widget synchronization
    
    # Add to history if not already present
    if target_word not in st.session_state.search_history:
        st.session_state.search_history.append(target_word)
```

## Widget State Management

### The Session State Widget Pattern
The application uses a "session state only" approach for widget management to avoid Streamlit's restrictions on mixing `value` parameters with session state APIs.

**Before (Problematic)**:
```python
# This caused conflicts
word = st.text_input(
    "Enter a word:",
    value=current_word,  # ❌ Conflicts with session state
    key="word_input"
)
```

**After (Fixed)**:
```python
# Session state only approach
word = st.text_input(
    "Enter a word:",
    key="word_input"  # ✅ Only session state control
)
# Widget value controlled via st.session_state.word_input
```

### Widget Synchronization
To ensure the input field displays the correct value during navigation:

```python
# Force widget synchronization during navigation
if current_word and not selected_word:
    if 'word_input' not in st.session_state or st.session_state.word_input != current_word:
        st.session_state.word_input = current_word
```

## Navigation Flow Diagram

```
User Action
    ↓
Navigation Method
    ↓
Session State Update
    ↓
Widget Synchronization
    ↓
Graph Update
    ↓
History Update
```

## Error Handling

### Common Navigation Issues

1. **Empty Input Field After Navigation**
   - **Cause**: Widget state not synchronized
   - **Solution**: Explicit `st.session_state.word_input` setting

2. **Double-Enter Required**
   - **Cause**: Mixed `value` and session state usage
   - **Solution**: Session state only approach

3. **History Not Updating**
   - **Cause**: Navigation not triggering history addition
   - **Solution**: Consistent state update pattern

### Debug Mode
Enable debug mode to monitor navigation:

```python
if st.session_state.get('debug_mode', False):
    st.write(f"🔍 Current Word: {st.session_state.current_word}")
    st.write(f"🔍 Input Value: {st.session_state.word_input}")
    st.write(f"🔍 History: {st.session_state.search_history}")
```

## Best Practices

### For Developers

1. **Always Use Session State Pattern**
   ```python
   # ✅ Good
   st.session_state.word_input = new_word
   
   # ❌ Avoid
   st.text_input("Word:", value=new_word, key="word_input")
   ```

2. **Maintain State Consistency**
   - Update all related state variables together
   - Use the standard navigation pattern
   - Test all navigation methods

3. **Handle Edge Cases**
   - Empty words
   - Invalid words
   - Network failures
   - Session state corruption

### For Users

1. **Navigation Tips**
   - Use Enter key for quick word entry
   - Click history buttons for quick revisits
   - Use URLs for bookmarking specific words

2. **Troubleshooting**
   - Refresh page if navigation becomes unresponsive
   - Clear browser cache for persistent issues
   - Enable debug mode for detailed information

## Future Enhancements

### Planned Features
1. **Graph Node Double-Click Navigation**
   - Direct node interaction
   - Seamless graph exploration
   - Visual feedback for clickable nodes

2. **Keyboard Shortcuts**
   - Arrow keys for history navigation
   - Escape key to clear input
   - Tab navigation for accessibility

3. **Advanced URL Parameters**
   - Multiple word comparison: `?compare=dog,cat`
   - Graph layout options: `?layout=hierarchical`
   - Filter parameters: `?pos=noun`

### Technical Improvements
1. **Navigation Performance**
   - Lazy loading for large graphs
   - Caching for frequently accessed words
   - Optimized state updates

2. **Error Recovery**
   - Automatic retry for failed navigations
   - Graceful degradation for network issues
   - Session state backup and restore

## Related Documentation
- [Session State Widget Fix Test](../testing/session-state-widget-fix.md)
- [Double-Enter Bug Fix Test](../testing/double-enter-bug-fix.md)
- [Widget State Management](../api/widget-state.md)
- [Troubleshooting Navigation](../troubleshooting/navigation-issues.md) 