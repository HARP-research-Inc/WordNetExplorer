# WordNet Explorer

A powerful tool that uses NLTK and NetworkX to visualize WordNet semantic relationships for any word. Explore word meanings, synonyms, hypernyms, hyponyms, and more through **interactive** visualizations.

## Features

- 🔍 **Word Exploration**: Discover semantic relationships for any English word
- 🎮 **Interactive Graphs**: Zoom, pan, drag nodes, and hover for definitions
- 🎨 **Color-coded Relationships**: Different colors for hypernyms, hyponyms, meronyms, etc.
- 📖 **Detailed Information**: View definitions, examples, and related words
- 💾 **Save Graphs**: Export interactive visualizations as HTML files
- 🎯 **Configurable Depth**: Control how deep to explore relationships
- 🎛️ **Relationship Filtering**: Toggle which types of relationships to display
- ⚡ **Fast Setup**: Automatic NLTK data download
- 🌐 **Web Interface**: User-friendly Streamlit UI for easy exploration
- 🧭 **Navigation History**: Track your exploration path with breadcrumbs
- ⚙️ **Modular Architecture**: Clean, maintainable codebase

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd WordNetExplorer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Interface (Recommended)

Run the Streamlit web interface:

```bash
python run_app.py
```

This will start a local web server and open the WordNet Explorer in your default browser. The web interface provides:

- Easy word input with instant search
- Interactive depth control slider
- Relationship type filtering (toggle hypernyms, hyponyms, etc.)
- Interactive graph visualization with zoom, pan, and hover features
- Detailed word information display
- Save functionality for interactive HTML graphs
- Navigation history with breadcrumb system
- Responsive design for all devices

### Command Line Interface

For command-line usage:

```bash
# Explore the word "dog"
python main.py dog

# Alternative syntax
python main.py --word cat
```

### Advanced CLI Options

```bash
# Show detailed word information
python main.py dog --info

# Control exploration depth (default: 1)
python main.py dog --depth 3

# Save interactive graph to HTML file
python main.py dog --save dog_graph.html

# Show only word info, no graph
python main.py dog --info --no-graph

# Combine options
python main.py tree --depth 3 --info --save tree_relationships.html
```

### Command Line Options

- `word` - The word to explore (positional argument)
- `-w, --word` - Alternative way to specify the word
- `-d, --depth` - Depth of exploration (default: 1)
- `-i, --info` - Show detailed word information
- `-s, --save` - Save interactive graph to HTML file
- `--no-graph` - Don't display the graph visualization
- `-h, --help` - Show help message

## Interactive Graph Features

The visualizations are fully interactive and provide:

- **Zoom**: Mouse wheel or pinch to zoom in/out
- **Pan**: Click and drag to move around the graph
- **Node Interaction**: Hover over nodes to see definitions and relationship types
- **Double-click Navigation**: Click nodes to recenter and explore that concept
- **Physics Simulation**: Nodes automatically arrange themselves for optimal viewing
- **Color Coding**: Different colors for each relationship type
- **Responsive Layout**: Automatically adjusts to graph size and complexity

## Graph Legend

The visualization uses different colors to represent different types of relationships:

- 🔴 **Red**: Main word (your input)
- 🟣 **Purple**: Word senses (different meanings)
- 🔵 **Teal**: Hypernyms (↑) - more general concepts
- 🔵 **Blue**: Hyponyms (↓) - more specific concepts  
- 🟢 **Green**: Meronyms (⊂) - part-of relationships
- 🟡 **Yellow**: Holonyms (⊃) - whole-of relationships

## Examples

### Example 1: Basic interactive exploration
```bash
python main.py car
```
This will show an interactive graph of relationships for "car" including vehicle types, car parts, etc. Hover over nodes to see definitions.

### Example 2: Deep exploration with info
```bash
python main.py animal --depth 3 --info
```
This will:
- Show detailed information about all senses of "animal"
- Create a deep interactive graph (3 levels) of animal relationships
- Allow exploration of complex semantic networks

### Example 3: Save interactive visualization
```bash
python main.py computer --save computer_network.html
```
This will create and save an interactive HTML file that can be opened in any web browser.

## Project Structure

The project features a **clean, modular architecture** for better maintainability and organization:

```
WordNetExplorer/
├── src/
│   ├── config/               # Configuration settings
│   │   ├── __init__.py       # Package initialization
│   │   └── settings.py       # App settings, color schemes, defaults
│   ├── utils/                # Utility functions
│   │   ├── __init__.py       # Package initialization
│   │   ├── session_state.py  # Navigation and session management
│   │   └── helpers.py        # Common helper functions
│   ├── ui/                   # User interface components
│   │   ├── __init__.py       # Package initialization
│   │   ├── styles.py         # CSS styles and theming
│   │   ├── navigation.py     # Navigation history components
│   │   ├── sidebar.py        # Sidebar settings and controls
│   │   ├── word_info.py      # Word information display
│   │   ├── graph_display.py  # Graph visualization and legends
│   │   └── welcome.py        # Welcome screen component
│   ├── wordnet_explorer.py   # Core WordNet functionality
│   ├── cli.py                # Command-line interface
│   └── app.py                # Main Streamlit application
├── main.py                   # CLI entry point
├── run_app.py                # Streamlit app runner
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

### Architecture Benefits

- **🎨 Separation of Concerns**: UI, logic, and configuration are cleanly separated
- **🔧 Easy Maintenance**: Each component has a single responsibility
- **🎯 Reusable Components**: UI components can be easily reused or modified
- **⚙️ Centralized Configuration**: All settings managed in one location
- **🚀 Scalable Design**: Easy to add new features or components
- **📦 Modular Imports**: Clean import structure with proper package organization
- **🧪 Testable Code**: Separated components make unit testing easier

### Component Overview

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `config/settings.py` | Configuration management | Default settings, color schemes, layout options |
| `utils/session_state.py` | Navigation state | History tracking, breadcrumb management |
| `utils/helpers.py` | Utility functions | Output capture, file operations, validation |
| `ui/styles.py` | CSS and styling | Custom themes, responsive design |
| `ui/navigation.py` | Navigation components | History display, URL handling |
| `ui/sidebar.py` | Sidebar interface | Settings panels, input controls |
| `ui/word_info.py` | Word information | Definition display, formatting |
| `ui/graph_display.py` | Graph visualization | Interactive plots, legends, tips |
| `ui/welcome.py` | Welcome screen | Instructions, examples, help |

## Dependencies

- **nltk**: Natural Language Toolkit for WordNet access
- **networkx**: Graph creation and manipulation
- **pyvis**: Interactive network visualization
- **streamlit**: Web interface framework
- **matplotlib**: Fallback static visualization

## Requirements

- Python 3.6 or higher
- Internet connection (for initial NLTK data download)
- Web browser (for Streamlit interface)

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the tool!

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python -c "import src.app; print('All imports successful')"`
4. Start the app: `python run_app.py`

### Adding New Features

The modular architecture makes it easy to add new features:

- **New UI components**: Add to `src/ui/`
- **New settings**: Update `src/config/settings.py`
- **New utilities**: Add to `src/utils/`
- **New visualizations**: Extend `src/ui/graph_display.py`

## License

See LICENSE file for details. 