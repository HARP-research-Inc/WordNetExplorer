#!/usr/bin/env python3
"""
Test script to demonstrate URL parameter functionality for WordNet Explorer.

This script shows example URLs with different search settings encoded as parameters.
"""

from urllib.parse import urlencode

def generate_example_urls():
    """Generate example URLs with different search settings."""
    
    base_url = "http://localhost:8501"
    
    examples = [
        {
            "description": "Basic word search",
            "params": {
                "word": "dog",
            }
        },
        {
            "description": "Word with specific sense",
            "params": {
                "word": "bank",
                "sense": "1",
            }
        },
        {
            "description": "Multiple senses exploration",
            "params": {
                "word": "run",
                "sense": "3",
                "depth": "2",
                "hypernyms": "true",
                "hyponyms": "true",
            }
        },
        {
            "description": "Detailed exploration settings",
            "params": {
                "word": "animal",
                "depth": "2",
                "hypernyms": "true",
                "hyponyms": "true",
                "meronyms": "false",
                "holonyms": "false",
                "layout": "Hierarchical",
                "color": "Vibrant",
                "physics": "false",
                "show_info": "true",
                "show_graph": "true",
            }
        },
        {
            "description": "Custom graph appearance with sense",
            "params": {
                "word": "tree",
                "sense": "2",
                "depth": "1",
                "layout": "Circular",
                "node_size": "1.5",
                "color": "Pastel",
                "physics": "true",
                "spring": "0.06",
                "gravity": "0.5",
                "labels": "true",
                "edge_width": "3",
            }
        },
        {
            "description": "Minimal relationship types",
            "params": {
                "word": "computer",
                "hypernyms": "true",
                "hyponyms": "false",
                "meronyms": "true",
                "holonyms": "false",
                "show_info": "false",
                "show_graph": "true",
            }
        },
        {
            "description": "Physics simulation showcase",
            "params": {
                "word": "emotion",
                "depth": "2",
                "physics": "true",
                "spring": "0.08",
                "gravity": "0.7",
                "layout": "Force-directed (default)",
                "color": "Monochrome",
                "labels": "false",
            }
        }
    ]
    
    print("WordNet Explorer - URL Parameter Examples")
    print("=" * 50)
    print()
    
    for i, example in enumerate(examples, 1):
        query_string = urlencode(example["params"])
        full_url = f"{base_url}?{query_string}"
        
        print(f"{i}. {example['description']}")
        print(f"   URL: {full_url}")
        print(f"   Parameters:")
        for key, value in example["params"].items():
            print(f"     - {key}: {value}")
        print()

def explain_parameters():
    """Explain what each URL parameter does."""
    
    print("URL Parameter Reference")
    print("=" * 30)
    print()
    
    parameters = {
        "word": "The word to explore (string)",
        "sense": "Specific sense number to display (integer, 1-based)",
        "depth": "Exploration depth (integer, 1-3)",
        "hypernyms": "Include hypernyms (boolean: true/false)",
        "hyponyms": "Include hyponyms (boolean: true/false)", 
        "meronyms": "Include meronyms (boolean: true/false)",
        "holonyms": "Include holonyms (boolean: true/false)",
        "layout": "Graph layout (string: 'Force-directed (default)', 'Hierarchical', 'Circular', 'Grid')",
        "node_size": "Node size multiplier (float, 0.5-2.0)",
        "color": "Color scheme (string: 'Default', 'Pastel', 'Vibrant', 'Monochrome')",
        "physics": "Enable physics simulation (boolean: true/false)",
        "spring": "Spring strength (float, 0.01-0.1)",
        "gravity": "Central gravity (float, 0.1-1.0)",
        "labels": "Show node labels (boolean: true/false)",
        "edge_width": "Edge width (integer, 1-5)",
        "show_info": "Show word information (boolean: true/false)",
        "show_graph": "Show relationship graph (boolean: true/false)",
    }
    
    for param, description in parameters.items():
        print(f"{param:12} - {description}")
    
    print()
    print("How URL Parameters Work:")
    print("=" * 25)
    print("1. URL parameters are loaded automatically when you visit a URL")
    print("2. Settings in the sidebar will reflect the URL parameters")
    print("3. URL is updated when:")
    print("   - You press Enter after typing a word")
    print("   - You click the 'Apply Settings' button")
    print("   - You select a word from search history")
    print("4. URL is NOT updated when you just change settings with sliders/checkboxes")
    print("5. This prevents the URL from changing constantly as you adjust settings")
    print()
    print("Usage:")
    print("- Copy any of the example URLs above and paste them into your browser")
    print("- The application will automatically load with the specified settings")
    print("- Modify parameters in the URL to customize the view")
    print("- Use the Apply button to update the URL with your current settings")
    print("- Share URLs with others to show specific word explorations")

if __name__ == "__main__":
    generate_example_urls()
    explain_parameters() 