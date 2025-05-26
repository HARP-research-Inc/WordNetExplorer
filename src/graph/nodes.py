"""
Graph Nodes Module

Handles node creation, labeling, and type management for graph structures.
"""

from enum import Enum
from typing import Dict, Any


class NodeType(Enum):
    """Enumeration of graph node types."""
    MAIN = "main"           # Root word nodes
    SYNSET = "synset"       # Synset nodes
    RELATIONSHIP = "relationship"  # Relationship nodes (if used)


def create_node_id(node_type: NodeType, identifier: str) -> str:
    """Create a standardized node ID."""
    if node_type == NodeType.MAIN:
        return f"ROOT_{identifier.upper()}"
    elif node_type == NodeType.SYNSET:
        return identifier  # Synset names are already unique
    else:
        return f"{node_type.value}_{identifier}"


def create_node_label(node_type: NodeType, data: Dict[str, Any]) -> str:
    """Create a display label for a node based on its type and data."""
    if node_type == NodeType.MAIN:
        return data.get('word', '').upper()
    elif node_type == NodeType.SYNSET:
        lemma = data.get('lemma_names', [''])[0].replace('_', ' ')
        pos_label = data.get('pos_label', '')
        sense_num = data.get('sense_number', '')
        return f"{lemma} ({pos_label}.{sense_num})"
    else:
        return data.get('label', str(data))


def create_node_attributes(node_type: NodeType, **kwargs) -> Dict[str, Any]:
    """Create standardized node attributes."""
    base_attrs = {
        'node_type': node_type.value
    }
    base_attrs.update(kwargs)
    return base_attrs 