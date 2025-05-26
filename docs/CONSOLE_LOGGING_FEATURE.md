# Enhanced Console Logging Feature

## Overview

The WordNet Explorer now includes **enhanced console logging** for node interactions in the graph visualization. When you double-click any node in the interactive graph, detailed information is logged to the browser's console.

## How to Use

1. **Open the WordNet Explorer** in your web browser
2. **Generate a graph** for any word
3. **Open browser developer tools** (F12 or right-click → Inspect)
4. **Go to the Console tab** in the developer tools
5. **Double-click any node** in the graph
6. **View the detailed logging information** in the console

## What Gets Logged

When you double-click a node, the following information is logged to the console:

### 🖱️ Node Double-Click Event
- **Node ID**: The unique identifier of the clicked node
- **Node Label**: The display label of the node
- **Node Title**: The tooltip/title text of the node
- **Node Color**: The color of the node
- **Node Size**: The size of the node
- **Click Position**: The DOM coordinates where you clicked
- **Canvas Position**: The canvas coordinates of the click
- **Timestamp**: ISO timestamp of when the click occurred
- **Detected Node Type**: The type of node (main word, synset, breadcrumb, etc.)
- **Target Word for Navigation**: The word that would be navigated to

### Additional Logging

The feature also logs:
- **Single clicks** on nodes (basic information)
- **Hover events** when you mouse over nodes
- **Initialization status** when the graph loads

## Example Console Output

```
🖱️ Node Double-Click Event
  Node ID: dog_main
  Node Label: dog
  Node Title: Main word: DOG
  Node Color: #FF6B6B
  Node Size: 30
  Click Position: {x: 450, y: 300}
  Canvas Position: {x: 200, y: 150}
  Timestamp: 2024-01-15T10:30:45.123Z
  Detected Node Type: main word
  Target Word for Navigation: dog
```

## Technical Details

### Implementation
- The logging is implemented using JavaScript injected into the pyvis-generated HTML
- Uses `console.group()` and `console.groupEnd()` for organized output
- Accesses node data directly from the vis.js network object
- Handles different node types with appropriate parsing

### Node Types Detected
- **Main Word** (`_main` suffix): The primary word being explored
- **Synset** (contains `.`): WordNet synset nodes
- **Breadcrumb** (`_breadcrumb` suffix): Navigation breadcrumb nodes
- **Related Word** (`_word` suffix): Related word nodes

### Browser Compatibility
- Works in all modern browsers that support:
  - ES6 JavaScript features
  - Console API
  - vis.js network library

## Debugging Benefits

This feature is particularly useful for:
- **Understanding graph structure**: See exactly what nodes contain
- **Debugging navigation**: Verify that clicks are being detected correctly
- **Performance analysis**: Monitor click response times
- **Development**: Test new features and node types
- **User support**: Help users understand what they're clicking on

## Privacy Note

All logging happens locally in your browser's console. No data is sent to external servers or stored permanently. The logs are cleared when you refresh the page or close the browser tab. 