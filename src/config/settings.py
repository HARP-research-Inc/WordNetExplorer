"""
Configuration settings for WordNet Explorer.
"""

# Default settings
DEFAULT_SETTINGS = {
    'depth': 1,
    'show_hypernyms': False,
    'show_hyponyms': False,
    'show_meronyms': False,
    'show_holonyms': False,
    'layout_type': 'Force-directed (default)',
    'node_size_multiplier': 1.0,
    'color_scheme': 'Default',
    'enable_physics': True,
    'spring_strength': 0.04,
    'central_gravity': 0.3,
    'show_labels': True,
    'edge_width': 2,
    'show_info': False,
    'show_graph': True,
    'sense_number': None,  # Specific sense to display (None = all senses)
    'synset_search_mode': False,  # Whether to search by synset instead of word
    
    # Comprehensive WordNet relationship types
    # Taxonomic Relations
    'show_hypernym': False,
    'show_hyponym': False,
    'show_instance_hypernym': False,
    'show_instance_hyponym': False,
    
    # Part-Whole Relations
    'show_member_holonym': False,
    'show_substance_holonym': False,
    'show_part_holonym': False,
    'show_member_meronym': False,
    'show_substance_meronym': False,
    'show_part_meronym': False,
    
    # Antonymy & Similarity
    'show_antonym': False,
    'show_similar_to': False,
    
    # Entailment & Causation
    'show_entailment': False,
    'show_cause': False,
    
    # Attributes & Cross-References
    'show_attribute': False,
    'show_also_see': False,
    
    # Verb-Specific Links
    'show_verb_group': False,
    'show_participle_of_verb': False,
    
    # Morphological / Derivational
    'show_derivationally_related_form': False,
    'show_pertainym': False,
    'show_derived_from': False,
    
    # Domain Labels
    'show_domain_of_synset_topic': False,
    'show_member_of_domain_topic': False,
    'show_domain_of_synset_region': False,
    'show_member_of_domain_region': False,
    'show_domain_of_synset_usage': False,
    'show_member_of_domain_usage': False,
}

# Color schemes for graph visualization - updated for new structure
COLOR_SCHEMES = {
    "Default": {
        "main": "#FF6B6B",        # Red for main word
        "word_sense": "#FFB347",  # Orange for word senses (individual meanings)
        "word": "#4ECDC4"         # Teal for related words
    },
    "Pastel": {
        "main": "#FFB3BA",        # Light red for main word
        "word_sense": "#FFC985",  # Light orange for word senses
        "word": "#BAFFCA"         # Light teal for related words
    },
    "Vibrant": {
        "main": "#FF0000",        # Bright red for main word
        "word_sense": "#FF8C00",  # Bright orange for word senses
        "word": "#00CED1"         # Bright teal for related words
    },
    "Monochrome": {
        "main": "#2C2C2C",        # Dark grey for main word
        "word_sense": "#777777",  # Medium grey for word senses
        "word": "#777777"         # Light grey for related words
    }
}

# POS-based colors for synsets
POS_COLORS = {
    "Default": {
        "n": "#FFB6C1",  # Light pink for nouns
        "v": "#87CEEB",  # Sky blue for verbs
        "a": "#98FB98",  # Pale green for adjectives
        "s": "#98FB98",  # Pale green for adjective satellites (same as adjectives)
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