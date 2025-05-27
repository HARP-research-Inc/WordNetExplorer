# URL Parameters Feature Summary

## Overview
The WordNet Explorer now supports storing search settings in URL parameters, making it easy to share specific configurations and explorations with others.

## Key Features Added

### 1. URL Parameter Support
- All search settings are now stored in URL parameters
- Settings are automatically loaded when visiting a URL with parameters
- Supports all configuration options including word, sense, depth, relationships, appearance, and physics settings

### 2. Smart URL Updates
The URL is updated only when:
- **Enter is pressed** after typing a word
- **Apply Settings button** is clicked
- **Word is selected** from search history

The URL is **NOT** updated when:
- Sliders or checkboxes are adjusted
- Settings are changed without explicit action

This prevents the URL from changing constantly as users explore different settings.

### 3. Apply Button
- Added a prominent "🔄 Apply Settings" button at the top of the sidebar
- Allows users to manually update the URL with current settings
- Updates the text input fields to reflect the current word and sense
- Useful for sharing specific configurations

## Supported URL Parameters

| Parameter | Description | Type | Example |
|-----------|-------------|------|---------|
| `word` | The word to explore | string | `word=dog` |
| `sense` | Specific sense number (1-based) | integer | `sense=2` |
| `depth` | Exploration depth | integer (1-3) | `depth=2` |
| `hypernyms` | Include hypernyms | boolean | `hypernyms=true` |
| `hyponyms` | Include hyponyms | boolean | `hyponyms=false` |
| `meronyms` | Include meronyms | boolean | `meronyms=true` |
| `holonyms` | Include holonyms | boolean | `holonyms=false` |
| `layout` | Graph layout | string | `layout=Hierarchical` |
| `node_size` | Node size multiplier | float (0.5-2.0) | `node_size=1.5` |
| `color` | Color scheme | string | `color=Vibrant` |
| `physics` | Enable physics simulation | boolean | `physics=true` |
| `spring` | Spring strength | float (0.01-0.1) | `spring=0.06` |
| `gravity` | Central gravity | float (0.1-1.0) | `gravity=0.5` |
| `labels` | Show node labels | boolean | `labels=true` |
| `edge_width` | Edge width | integer (1-5) | `edge_width=3` |
| `show_info` | Show word information | boolean | `show_info=true` |
| `show_graph` | Show relationship graph | boolean | `show_graph=true` |

## Example URLs

### Basic word search
```
http://localhost:8501?word=dog
```

### Word with specific sense
```
http://localhost:8501?word=bank&sense=1
```

### Complex configuration
```
http://localhost:8501?word=animal&depth=2&hypernyms=true&hyponyms=true&meronyms=false&holonyms=false&layout=Hierarchical&color=Vibrant&physics=false&show_info=true&show_graph=true
```

### Custom graph appearance with sense
```
http://localhost:8501?word=tree&sense=2&depth=1&layout=Circular&node_size=1.5&color=Pastel&physics=true&spring=0.06&gravity=0.5&labels=true&edge_width=3
```

## Technical Implementation

### Files Modified
1. **`src/core/session.py`**
   - Added URL parameter handling methods
   - Added settings extraction from URL
   - Added conditional URL updating

2. **`src/ui/sidebar.py`**
   - Modified all render functions to use URL defaults
   - Added Apply button
   - Added word change detection
   - Updated URL update logic

3. **`src/app.py`**
   - Updated to pass session_manager to sidebar

### Key Methods Added
- `get_query_params()` - Cross-version URL parameter retrieval
- `set_query_params()` - Cross-version URL parameter setting
- `get_settings_from_url()` - Extract settings from URL parameters
- `update_url_with_settings()` - Update URL with current settings
- `get_url_default()` - Get setting value from URL or default

## Usage Instructions

1. **Loading from URL**: Simply paste a URL with parameters into your browser
2. **Sharing configurations**: Use the Apply button to update the URL, then copy and share
3. **Quick exploration**: Type a word and press Enter to automatically update the URL
4. **History navigation**: Click words in search history to explore and update URL

## Benefits

- **Shareable links**: Easy to share specific word explorations and configurations
- **Bookmarkable**: Save interesting configurations as bookmarks
- **Reproducible**: Exact settings can be recreated from URLs
- **User-friendly**: URL updates only when intended, not on every setting change
- **Cross-platform**: Works with any browser and can be shared across different systems

## Backward Compatibility

- All existing functionality remains unchanged
- URLs without parameters work exactly as before
- Default settings are used when parameters are not specified
- Graceful handling of invalid or missing parameters 