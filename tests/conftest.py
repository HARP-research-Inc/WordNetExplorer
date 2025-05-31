"""
Pytest configuration and common fixtures for WordNet Explorer tests.
"""

import pytest
import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import WordNetExplorer
from src.wordnet.relationships import RelationshipConfig


@pytest.fixture(scope="session")
def explorer():
    """Create a WordNet Explorer instance for testing."""
    return WordNetExplorer()


@pytest.fixture(scope="session")
def relationship_config_all():
    """Relationship config with all relationships enabled."""
    return RelationshipConfig(
        hypernyms=True,
        hyponyms=True,
        meronyms=True,
        holonyms=True,
        similar=True,
        antonyms=True,
        also=True,
        entailments=True,
        causes=True
    )


@pytest.fixture(scope="session")
def relationship_config_taxonomic():
    """Relationship config with only taxonomic relationships."""
    return RelationshipConfig(
        hypernyms=True,
        hyponyms=True,
        meronyms=False,
        holonyms=False,
        similar=False,
        antonyms=False,
        also=False,
        entailments=False,
        causes=False
    )


def extract_node_name(node_id):
    """Extract clean node name from node ID."""
    if '.' in node_id:
        return node_id.split('.')[0]
    elif '_' in node_id:
        return node_id.split('_')[-1]
    return node_id


def analyze_arrow_direction(source, target, edge_data):
    """Analyze arrow direction for taxonomic relationships."""
    relation = edge_data.get('relation', 'unknown')
    arrow_direction = edge_data.get('arrow_direction', 'to')
    
    source_name = extract_node_name(source)
    target_name = extract_node_name(target)
    
    # Determine visual arrow based on the current logic
    if relation == 'hypernym':
        # Hypernym: source → target (specific → general)
        visual_source, visual_target = source_name, target_name
    elif relation == 'hyponym':
        # Hyponym: target → source (specific → general)
        visual_source, visual_target = target_name, source_name
    else:
        # For non-taxonomic relationships
        if arrow_direction == 'from':
            visual_source, visual_target = target_name, source_name
        else:
            visual_source, visual_target = source_name, target_name
    
    return {
        'relation': relation,
        'original_edge': f"{source_name} → {target_name}",
        'visual_arrow': f"{visual_source} → {visual_target}",
        'arrow_direction': arrow_direction,
        'visual_source': visual_source,
        'visual_target': visual_target
    } 