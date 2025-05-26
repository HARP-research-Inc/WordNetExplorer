"""
Configuration settings for WordNet Explorer.
"""

# Default settings
DEFAULT_SETTINGS = {
    'depth': 1,
    'show_hypernyms': True,
    'show_hyponyms': True,
    'show_meronyms': True,
    'show_holonyms': True,
    'layout_type': 'Force-directed (default)',
    'node_size_multiplier': 1.0,
    'color_scheme': 'Default',
    'enable_physics': True,
    'spring_strength': 0.04,
    'central_gravity': 0.3,
    'show_labels': True,
    'show_arrows': False,
    'edge_width': 2,
    'show_info': True,
    'show_graph': True,
}

# Color schemes for graph visualization
COLOR_SCHEMES = {
    "Default": {
        "main": "#FF6B6B", 
        "synset": "#DDA0DD", 
        "hyper": "#4ECDC4", 
        "hypo": "#45B7D1", 
        "mero": "#96CEB4", 
        "holo": "#FFEAA7"
    },
    "Pastel": {
        "main": "#FFB3BA", 
        "synset": "#BFBFFF", 
        "hyper": "#BAFFCA", 
        "hypo": "#B3E5FF", 
        "mero": "#C7FFB3", 
        "holo": "#FFFFB3"
    },
    "Vibrant": {
        "main": "#FF0000", 
        "synset": "#9932CC", 
        "hyper": "#00CED1", 
        "hypo": "#1E90FF", 
        "mero": "#32CD32", 
        "holo": "#FFD700"
    },
    "Monochrome": {
        "main": "#2C2C2C", 
        "synset": "#5A5A5A", 
        "hyper": "#777777", 
        "hypo": "#949494", 
        "mero": "#B1B1B1", 
        "holo": "#CECECE"
    }
}

# Layout options
LAYOUT_OPTIONS = [
    "Force-directed (default)", 
    "Hierarchical", 
    "Circular", 
    "Grid"
]

# Page configuration
PAGE_CONFIG = {
    'page_title': "WordNet Explorer",
    'page_icon': "🔍",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
} 