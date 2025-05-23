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

- Easy word input
- Interactive depth control
- Toggle options for information and graph display
- Save functionality for graphs
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

# Save graph to file
python main.py dog --save dog_graph.png

# Show only word info, no graph
python main.py dog --info --no-graph

# Combine options
python main.py tree --depth 3 --info --save tree_relationships.png
```

### Command Line Options

- `word` - The word to explore (positional argument)
- `-w, --word` - Alternative way to specify the word
- `-d, --depth` - Depth of exploration (default: 1)
- `-i, --info` - Show detailed word information
- `-s, --save` - Save graph to PNG file
- `--no-graph` - Don't display the graph visualization
- `-h, --help` - Show help message

## Graph Legend

The visualization uses different colors to represent different types of relationships:

- 🔴 **Red**: Main word (your input)
- 🟣 **Purple**: Word senses (different meanings)
- 🔵 **Teal**: Hypernyms (↑) - more general concepts
- 🔵 **Blue**: Hyponyms (↓) - more specific concepts  
- 🟢 **Green**: Meronyms (⊂) - part-of relationships
- 🟡 **Yellow**: Holonyms (⊃) - whole-of relationships

## Examples

### Example 1: Basic word exploration
```bash
python main.py car
```
This will show a graph of relationships for "car" including vehicle types, car parts, etc.

### Example 2: Deep exploration with info
```bash
python main.py animal --depth 3 --info
```
This will:
- Show detailed information about all senses of "animal"
- Create a deep graph (3 levels) of animal relationships
- Display definitions and examples

### Example 3: Save visualization
```bash
python main.py computer --save computer_network.png
```
This will create and save a PNG file of the computer-related word network.

## Project Structure

```
WordNetExplorer/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── wordnet_explorer.py   # Core functionality
│   ├── cli.py                # Command-line interface
│   └── app.py                # Streamlit web interface
├── main.py                   # CLI entry point
├── run_app.py                # Streamlit app runner
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Dependencies

- **nltk**: Natural Language Toolkit for WordNet access
- **networkx**: Graph creation and manipulation
- **matplotlib**: Graph visualization
- **streamlit**: Web interface framework

## Requirements

- Python 3.6 or higher
- Internet connection (for initial NLTK data download)
- Web browser (for Streamlit interface)

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the tool!

## License

See LICENSE file for details.
