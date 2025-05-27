# Double-Click Navigation with URL Parameters

## Overview

The WordNet Explorer now supports **double-click navigation** that preserves all current search settings in the URL. When you double-click any node in the graph, the application navigates to that word while maintaining all your current configuration settings.

## How It Works

### 1. URL Parameter Preservation
When you double-click a node, the JavaScript automatically:
- Preserves all existing URL parameters (depth, relationships, appearance settings, etc.)
- Updates only the `word` parameter to the clicked word
- Adds a `clicked_node` parameter to track the navigation source
- Removes any old `navigate_to` parameters

### 2. Seamless Navigation
The navigation maintains your complete exploration context:
- **Search settings** (depth, relationship types)
- **Graph appearance** (layout, colors, node sizes)
- **Physics settings** (spring strength, gravity)
- **Display options** (labels, info panels)

## Example Usage

### Scenario: Exploring Animal Relationships
1. **Start with a configured search:**
   ```
   http://localhost:8501/?word=dog&depth=2&hypernyms=true&hyponyms=true&layout=Force-directed&node_size=1.2&physics=true&color=Vibrant
   ```

2. **Double-click the "animal" node**

3. **Result URL automatically becomes:**
   ```
   http://localhost:8501/?word=animal&depth=2&hypernyms=true&hyponyms=true&layout=Force-directed&node_size=1.2&physics=true&color=Vibrant&clicked_node=animal_main
   ```

### Key Benefits
- ✅ **All settings preserved** - depth, relationships, appearance remain the same
- ✅ **Shareable URLs** - send the exact configuration to others
- ✅ **Bookmarkable** - save specific exploration states
- ✅ **Navigation tracking** - `clicked_node` parameter shows how you got there

## Technical Implementation

### JavaScript Navigation Code
The double-click handler preserves URL parameters:

```javascript
// Navigate by preserving current URL parameters and updating word
const url = new URL(window.location);

// Update the word parameter while preserving all other settings
url.searchParams.set('word', targetWord);
url.searchParams.set('clicked_node', nodeId);

// Remove old navigate_to parameter if it exists
url.searchParams.delete('navigate_to');

console.log('🔗 Navigating to URL:', url.toString());
window.location.href = url.toString();
```

### Node Type Detection
The system intelligently extracts the target word from different node types:

| Node Type | Node ID Format | Target Word Extraction |
|-----------|----------------|------------------------|
| Main word (new) | `ROOT_DOG` | Remove `ROOT_` prefix, lowercase |
| Main word (legacy) | `dog_main` | Remove `_main` suffix |
| Breadcrumb | `cat_breadcrumb` | Remove `_breadcrumb` suffix |
| Related word | `animal_word` | Remove `_word` suffix |
| Synset | `canine.n.02` | Extract word before first dot |

### URL Parameter Mapping
All search settings are preserved through URL parameters:

| Setting | URL Parameter | Example Value |
|---------|---------------|---------------|
| Word | `word` | `dog` |
| Sense | `sense` | `2` |
| Depth | `depth` | `2` |
| Hypernyms | `hypernyms` | `true` |
| Hyponyms | `hyponyms` | `false` |
| Meronyms | `meronyms` | `true` |
| Holonyms | `holonyms` | `true` |
| Layout | `layout` | `Force-directed` |
| Node Size | `node_size` | `1.2` |
| Color Scheme | `color` | `Vibrant` |
| Physics | `physics` | `true` |
| Spring Strength | `spring` | `0.05` |
| Gravity | `gravity` | `0.4` |
| Show Labels | `labels` | `true` |
| Show Info | `show_info` | `false` |
| Show Graph | `show_graph` | `true` |
| Edge Width | `edge_width` | `3` |
| Clicked Node | `clicked_node` | `animal_main` |

## Console Logging

### Enhanced Debug Information
When you double-click a node, detailed information is logged to the browser console:

```
🖱️ Node Double-Click Event
  Node ID: animal_main
  Node Label: ANIMAL
  Node Title: Main word: ANIMAL
  Node Color: #FF0000
  Node Size: 36
  Click Position: {x: 450, y: 300}
  Canvas Position: {x: 200, y: 150}
  Timestamp: 2024-01-15T10:30:45.123Z
  Detected Node Type: main word
  Target Word for Navigation: animal
🔗 Navigating to URL: http://localhost:8501/?word=animal&depth=2&hypernyms=true&...
```

### How to View Console Logs
1. Open browser developer tools (F12)
2. Go to the Console tab
3. Double-click any node in the graph
4. View the detailed logging information

## Testing the Feature

### Manual Testing Steps
1. **Set up a complex configuration:**
   - Choose a word (e.g., "dog")
   - Set depth to 2
   - Enable specific relationships
   - Choose custom appearance settings
   - Enable physics with custom parameters

2. **Generate the graph and note the URL**

3. **Double-click various nodes:**
   - Main word nodes (red circles)
   - Synset nodes (purple circles)
   - Related word nodes

4. **Verify URL preservation:**
   - Check that all original parameters remain
   - Confirm only `word` parameter changes
   - Note the `clicked_node` parameter addition

### Automated Testing
Run the test script to verify functionality:

```bash
python test_double_click_navigation.py
```

This generates a test HTML file with sample parameters that you can open in a browser to test the navigation behavior.

## Browser Compatibility

### Supported Browsers
- ✅ **Chrome** (recommended)
- ✅ **Firefox**
- ✅ **Safari**
- ✅ **Edge**

### Requirements
- JavaScript enabled
- Modern browser with URL API support
- Console access for debugging (optional)

## Troubleshooting

### Common Issues

#### 1. Navigation Not Working
**Symptoms:** Double-clicking nodes doesn't navigate
**Solutions:**
- Check browser console for JavaScript errors
- Ensure JavaScript is enabled
- Try refreshing the page
- Clear browser cache

#### 2. Parameters Not Preserved
**Symptoms:** URL parameters are lost during navigation
**Solutions:**
- Check console logs for navigation URL
- Verify original URL has parameters
- Ensure browser supports URL API

#### 3. Console Logging Not Visible
**Symptoms:** No debug information in console
**Solutions:**
- Open developer tools (F12)
- Switch to Console tab
- Check console filter settings
- Refresh page and try again

### Debug Mode
Enable debug mode by adding `?debug=true` to your URL to see additional logging information in the Streamlit interface.

## Related Features

### Search History Integration
Double-click navigation automatically adds words to your search history, allowing you to:
- Track your exploration path
- Quickly return to previous words
- Share exploration sequences

### Breadcrumb Navigation
When navigating via double-click, the system can add breadcrumb nodes to help you track your path through the semantic network.

### URL Sharing
The preserved URL parameters make it easy to:
- Share specific explorations with others
- Bookmark interesting configurations
- Return to exact search states

## Future Enhancements

### Planned Improvements
1. **Visual feedback** for clickable nodes
2. **Keyboard shortcuts** for navigation
3. **Navigation history** in the interface
4. **Undo/redo** functionality
5. **Batch navigation** for multiple words

### Advanced Features
1. **Path visualization** showing navigation history
2. **Comparison mode** for multiple words
3. **Export navigation sequences**
4. **Custom navigation behaviors**

## API Reference

### JavaScript Events
The graph visualization exposes these events:
- `doubleClick` - Node double-click navigation
- `click` - Single-click logging
- `hoverNode` - Node hover information

### URL Parameters
See the complete URL parameter mapping table above for all supported parameters and their formats.

### Console API
Access navigation information via browser console:
- Node details on double-click
- Navigation URLs
- Error messages and warnings 