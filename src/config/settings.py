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
    'edge_width': 2,
    'show_info': True,
    'show_graph': True,
    'sense_number': None,  # Specific sense to display (None = all senses)
    'synset_search_mode': False,  # Whether to search by synset instead of word
}

# Color schemes for graph visualization - updated for new structure
COLOR_SCHEMES = {
    "Default": {
        "main": "#FF6B6B",        # Red for main word
        "word_sense": "#FFB347",  # Orange for word senses (individual meanings)
        "synset": "#DDA0DD",      # Purple for synsets (semantic groups)
        "word": "#4ECDC4"         # Teal for related words
    },
    "Pastel": {
        "main": "#FFB3BA",        # Light red for main word
        "word_sense": "#FFC985",  # Light orange for word senses
        "synset": "#BFBFFF",      # Light purple for synsets
        "word": "#BAFFCA"         # Light teal for related words
    },
    "Vibrant": {
        "main": "#FF0000",        # Bright red for main word
        "word_sense": "#FF8C00",  # Bright orange for word senses
        "synset": "#9932CC",      # Bright purple for synsets
        "word": "#00CED1"         # Bright teal for related words
    },
    "Monochrome": {
        "main": "#2C2C2C",        # Dark grey for main word
        "word_sense": "#777777",  # Medium grey for word senses
        "synset": "#5A5A5A",      # Medium grey for synsets
        "word": "#777777"         # Light grey for related words
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