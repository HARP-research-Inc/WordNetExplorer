#!/usr/bin/env python3
"""
Command-line interface for WordNet Explorer
"""

import argparse
import sys
from typing import Dict, Tuple

import networkx as nx
import matplotlib.pyplot as plt

from .wordnet_explorer import (
    download_nltk_data,
    get_synsets_for_word,
    build_wordnet_graph,
    visualize_graph,
    print_word_info
)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Explore WordNet connections for a given word",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dog                    # Basic graph for 'dog'
  %(prog)s --word cat --depth 3   # Deeper exploration for 'cat'
  %(prog)s car --info             # Show detailed word information
  %(prog)s tree --save tree.png   # Save graph to file
        """
    )
    
    parser.add_argument('word', nargs='?', help='The word to explore')
    parser.add_argument('-w', '--word', help='The word to explore (alternative way)')
    parser.add_argument('-d', '--depth', type=int, default=1, 
                       help='Depth of exploration (default: 1)')
    parser.add_argument('-i', '--info', action='store_true',
                       help='Show detailed word information')
    parser.add_argument('-s', '--save', help='Save graph to file (PNG format)')
    parser.add_argument('--no-graph', action='store_true',
                       help='Don\'t display the graph visualization')
    
    return parser.parse_args()

def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Get the word from positional argument or --word flag
    word = args.word or getattr(args, 'word', None)
    if not word:
        print("Error: Please provide a word to explore")
        sys.exit(1)
    
    word = word.lower().strip()
    
    try:
        # Download NLTK data if needed
        download_nltk_data()
        
        # Show word information if requested
        if args.info:
            print_word_info(word)
        
        # Build and display graph unless --no-graph is specified
        if not args.no_graph:
            print(f"Building WordNet graph for '{word}' (depth: {args.depth})...")
            G, node_labels = build_wordnet_graph(word, args.depth)
            
            if G.number_of_nodes() > 0:
                print(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
                visualize_graph(G, node_labels, word, args.save)
            else:
                print(f"No WordNet connections found for '{word}'")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 