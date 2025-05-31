"""
Color schemes for graph visualization.
"""

from typing import Dict, Any


# Node color schemes
NODE_COLOR_SCHEMES: Dict[str, Dict[str, str]] = {
    "Default": {
        "main": "#FF6B6B",        # Red for main word
        "word_sense": "#FFB347",  # Orange for word senses
        "word": "#4ECDC4",        # Teal for related words
        "breadcrumb": "#CCCCCC"   # Grey for breadcrumb
    },
    "Pastel": {
        "main": "#FFB3BA",        # Light red for main word
        "word_sense": "#FFC985",  # Light orange for word senses
        "word": "#BAFFCA",        # Light teal for related words
        "breadcrumb": "#E0E0E0"   # Light grey for breadcrumb
    },
    "Vibrant": {
        "main": "#FF0000",        # Bright red for main word
        "word_sense": "#FF8C00",  # Bright orange for word senses
        "word": "#00CED1",        # Bright teal for related words
        "breadcrumb": "#999999"   # Medium grey for breadcrumb
    },
    "Monochrome": {
        "main": "#2C2C2C",        # Dark grey for main word
        "word_sense": "#777777",  # Medium grey for word senses
        "word": "#777777",        # Light grey for related words
        "breadcrumb": "#AAAAAA"   # Light grey for breadcrumb
    }
}

# POS-based colors for synsets
POS_COLOR_SCHEMES: Dict[str, Dict[str, str]] = {
    "Default": {
        "n": "#FFB6C1",  # Light pink for nouns
        "v": "#87CEEB",  # Sky blue for verbs
        "a": "#98FB98",  # Pale green for adjectives
        "s": "#98FB98",  # Pale green for adjective satellites
        "r": "#DDA0DD"   # Plum purple for adverbs
    },
    "Pastel": {
        "n": "#FFD1DC",  # Pastel pink for nouns
        "v": "#B0E0E6",  # Powder blue for verbs
        "a": "#F0FFF0",  # Honeydew for adjectives
        "s": "#F0FFF0",  # Honeydew for adjective satellites
        "r": "#E6E6FA"   # Lavender for adverbs
    },
    "Vibrant": {
        "n": "#FF1493",  # Deep pink for nouns
        "v": "#0000FF",  # Blue for verbs
        "a": "#00FF00",  # Lime green for adjectives
        "s": "#00FF00",  # Lime green for adjective satellites
        "r": "#8A2BE2"   # Blue violet for adverbs
    },
    "Monochrome": {
        "n": "#696969",  # Dim gray for nouns
        "v": "#808080",  # Gray for verbs
        "a": "#A9A9A9",  # Dark gray for adjectives
        "s": "#A9A9A9",  # Dark gray for adjective satellites
        "r": "#C0C0C0"   # Silver for adverbs
    }
}


def get_node_color(node_type: str, color_scheme: str = "Default") -> str:
    """
    Get the color for a specific node type in the given color scheme.
    
    Args:
        node_type: Type of node (main, word_sense, word, breadcrumb)
        color_scheme: Name of the color scheme
        
    Returns:
        Hex color code
    """
    scheme = NODE_COLOR_SCHEMES.get(color_scheme, NODE_COLOR_SCHEMES["Default"])
    return scheme.get(node_type, "#CCCCCC")  # Default to light grey


def get_pos_color(pos: str, color_scheme: str = "Default") -> str:
    """
    Get the color for a specific part of speech in the given color scheme.
    
    Args:
        pos: Part of speech code (n, v, a, s, r)
        color_scheme: Name of the color scheme
        
    Returns:
        Hex color code
    """
    scheme = POS_COLOR_SCHEMES.get(color_scheme, POS_COLOR_SCHEMES["Default"])
    return scheme.get(pos, scheme.get('n', '#FFB6C1'))  # Default to noun color


def get_node_style(node_type: str) -> Dict[str, Any]:
    """
    Get the visual style for a specific node type.
    
    Args:
        node_type: Type of node
        
    Returns:
        Dictionary of style properties
    """
    styles = {
        'breadcrumb': {
            'shape': 'dot',
            'borderWidth': 3,
            'borderWidthSelected': 4,
            'borderDashes': [5, 5],
            'chosen': True
        },
        'main': {
            'shape': 'dot',
            'borderWidth': 2
        },
        'word_sense': {
            'shape': 'diamond',
            'borderWidth': 2
        },
        'synset': {
            'shape': 'square',
            'borderWidth': 2
        },
        'word': {
            'shape': 'dot',
            'borderWidth': 1
        }
    }
    
    return styles.get(node_type, {})


def get_node_size(node_type: str, size_multiplier: float = 1.0) -> int:
    """
    Get the size for a specific node type.
    
    Args:
        node_type: Type of node
        size_multiplier: Multiplier for all node sizes
        
    Returns:
        Node size in pixels
    """
    base_sizes = {
        'main': 30,
        'word_sense': 25,
        'synset': 25,
        'word': 20,
        'breadcrumb': 20,
        'default': 20
    }
    
    base_size = base_sizes.get(node_type, base_sizes['default'])
    return int(base_size * size_multiplier) 