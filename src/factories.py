"""
Factory functions for creating common objects in WordNet Explorer.
"""

import networkx as nx
from datetime import datetime
from src.constants import NODE_TYPES, RELATIONSHIP_TYPES, RELATIONSHIP_COLORS


def create_graph(directed=True):
    """
    Create a new graph instance with appropriate settings.
    
    Args:
        directed (bool): Whether to create a directed graph
        
    Returns:
        nx.Graph or nx.DiGraph: New graph instance
    """
    return nx.DiGraph() if directed else nx.Graph()


def create_node(node_id, node_type, **attributes):
    """
    Create a node dictionary with standardized attributes.
    
    Args:
        node_id (str): Unique identifier for the node
        node_type (str): Type of node (from NODE_TYPES)
        **attributes: Additional attributes for the node
        
    Returns:
        dict: Node attributes dictionary
    """
    return {
        'id': node_id,
        'node_type': node_type,
        'created_at': datetime.now().isoformat(),
        **attributes
    }


def create_edge(source, target, relationship_type, **attributes):
    """
    Create an edge dictionary with standardized attributes.
    
    Args:
        source (str): Source node ID
        target (str): Target node ID
        relationship_type (str): Type of relationship (from RELATIONSHIP_TYPES)
        **attributes: Additional attributes for the edge
        
    Returns:
        dict: Edge attributes dictionary
    """
    color = RELATIONSHIP_COLORS.get(relationship_type, RELATIONSHIP_COLORS['default'])
    
    return {
        'source': source,
        'target': target,
        'relation': relationship_type,
        'color': color,
        'arrow_direction': 'to',
        **attributes
    }


def create_main_node(word):
    """
    Create a main word node.
    
    Args:
        word (str): The word
        
    Returns:
        tuple: (node_id, node_attributes)
    """
    node_id = f"ROOT_{word.upper()}"
    attributes = create_node(
        node_id,
        NODE_TYPES['MAIN'],
        word=word.lower(),
        label=word.upper()
    )
    return node_id, attributes


def create_synset_node(synset):
    """
    Create a synset node from a WordNet synset.
    
    Args:
        synset: NLTK WordNet synset object
        
    Returns:
        tuple: (node_id, node_attributes)
    """
    from src.constants import POS_MAP
    
    node_id = synset.name()
    pos_label = POS_MAP.get(synset.pos(), synset.pos())
    sense_num = synset.name().split('.')[-1]
    
    attributes = create_node(
        node_id,
        NODE_TYPES['SYNSET'],
        synset_name=synset.name(),
        definition=synset.definition(),
        pos=synset.pos(),
        label=f"{synset.lemma_names()[0].replace('_', ' ')} ({pos_label}.{sense_num})"
    )
    return node_id, attributes


def create_word_node(word, synset_name=None):
    """
    Create a word node.
    
    Args:
        word (str): The word
        synset_name (str, optional): Associated synset name
        
    Returns:
        tuple: (node_id, node_attributes)
    """
    node_id = f"{word}_word" if not synset_name else f"{word}_{synset_name}_word"
    
    attributes = create_node(
        node_id,
        NODE_TYPES['WORD'],
        word=word,
        synset_name=synset_name,
        label=word.replace('_', ' ')
    )
    return node_id, attributes


def create_breadcrumb_node(word, original_word=None):
    """
    Create a breadcrumb navigation node.
    
    Args:
        word (str): The word to navigate back to
        original_word (str, optional): Original form of the word
        
    Returns:
        tuple: (node_id, node_attributes)
    """
    node_id = f"{word}_breadcrumb"
    
    attributes = create_node(
        node_id,
        NODE_TYPES['BREADCRUMB'],
        word=word,
        original_word=original_word or word,
        label=f"← Back to {original_word or word}"
    )
    return node_id, attributes


def create_settings_dict(**kwargs):
    """
    Create a standardized settings dictionary with defaults.
    
    Args:
        **kwargs: Setting overrides
        
    Returns:
        dict: Settings dictionary
    """
    from src.config.settings import DEFAULT_SETTINGS
    
    settings = DEFAULT_SETTINGS.copy()
    settings.update(kwargs)
    
    # Ensure required fields exist
    required_fields = ['depth', 'show_graph', 'show_info']
    for field in required_fields:
        if field not in settings:
            settings[field] = DEFAULT_SETTINGS.get(field, True)
    
    return settings 