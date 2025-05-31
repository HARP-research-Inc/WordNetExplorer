"""
Constants used throughout the WordNet Explorer application.
"""

# Application version
VERSION = "2.0.0"
VERSION_NAME = "Modular Architecture"

# Node types
NODE_TYPES = {
    'MAIN': 'main',
    'SYNSET': 'synset',
    'WORD': 'word',
    'WORD_SENSE': 'word_sense',
    'BREADCRUMB': 'breadcrumb'
}

# Relationship types
RELATIONSHIP_TYPES = {
    'SENSE': 'sense',
    'HYPERNYM': 'hypernym',
    'HYPONYM': 'hyponym',
    'MERONYM': 'meronym',
    'HOLONYM': 'holonym',
    'ANTONYM': 'antonym',
    'SIMILAR_TO': 'similar_to',
    'ENTAILMENT': 'entailment',
    'CAUSE': 'cause',
    'ATTRIBUTE': 'attribute',
    'ALSO_SEE': 'also_see',
    'VERB_GROUP': 'verb_group',
    'DERIVATION': 'derivationally_related_form',
    'PERTAINYM': 'pertainym'
}

# Relationship colors
RELATIONSHIP_COLORS = {
    'sense': '#666666',      # Dark grey for sense connections
    'hypernym': '#FF4444',   # Bright red for "is a type of"
    'hyponym': '#4488FF',    # Bright blue for "type includes"
    'meronym': '#44AA44',    # Green for "has part"
    'holonym': '#FFAA00',    # Orange for "part of"
    'antonym': '#DD00DD',    # Purple for opposites
    'similar_to': '#00AAAA', # Cyan for similar
    'default': '#888888'     # Default grey
}

# Part of speech mappings
POS_MAP = {
    'n': 'noun',
    'v': 'verb',
    'a': 'adj',
    's': 'adj',
    'r': 'adv'
}

# UI Icons
ICONS = {
    'WORD': '🔤',
    'SYNSET': '🎯',
    'SEARCH': '🔍',
    'GRAPH': '🕸️',
    'INFO': '📊',
    'SETTINGS': '⚙️',
    'ABOUT': 'ℹ️',
    'DOWNLOAD': '💾',
    'DELETE': '🗑️',
    'WARNING': '⚠️',
    'SUCCESS': '✅',
    'ERROR': '❌',
    'TIP': '💡',
    'NAVIGATION': '🧭'
}

# Default file prefixes
FILE_PREFIXES = {
    'HTML': 'wne-graph',
    'JSON': 'wne-data',
    'PNG': 'wne-image'
}

# Maximum values
MAX_DEPTH = 10
MAX_NODES = 100000
MAX_BRANCHES = 20
MAX_FREQUENCY = 100

# Default values
DEFAULT_DEPTH = 1
DEFAULT_MAX_NODES = 100
DEFAULT_MAX_BRANCHES = 5
DEFAULT_MIN_FREQUENCY = 0 