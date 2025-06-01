"""
Pytest configuration and shared fixtures for sentence parser tests.
"""

import pytest
import sys
import os

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(scope="session")
def sample_sentences():
    """Provide a collection of sample sentences for testing."""
    return {
        'simple': [
            "The cat sat.",
            "Dogs bark.",
            "I run fast.",
            "She sleeps."
        ],
        'medium': [
            "The big brown dog chases cats.",
            "She quickly ran to the store.",
            "I like coffee and tea.",
            "The book on the table is mine."
        ],
        'complex': [
            "When it rains, I stay inside and read books.",
            "The man who sold the world is coming tomorrow.",
            "I would like to go, but I can't because I'm busy.",
            "If you build it, they will come, and everyone will be happy."
        ],
        'problematic': [
            "I would like to run the world someday, but only if my 401k goes up.",
            "The dogs' toys were scattered across the children's playground.",
            "She said she'd've gone if she'd known.",
            "Time flies like an arrow; fruit flies like a banana."
        ]
    }


@pytest.fixture
def expected_tree_properties():
    """Expected properties for valid syntactic trees."""
    return {
        'required_node_types': ['sentence'],
        'valid_node_types': ['sentence', 'clause', 'phrase', 'word'],
        'valid_edge_labels': [
            'subj', 'obj', 'tverb', 'verb', 'aux', 'adv', 'adj', 'det',
            'prep', 'pobj', 'prep_phrase', 'head', 'core', 'compound',
            'poss', 'num', 'sconj', 'iclause', 'dclause', 'clause',
            'coord_clause', 'punct', 'adv_mod', 'main_clause', 'verb_head',
            'particle', 'obj_group', 'part', 'dobj', 'iobj', 'nsubj',
            # Lemma decomposition edges
            'past', 'present', 'present_3sg', 'gerund', 'past_part',
            'plural', 'singular', 'comparative', 'superlative', 'base',
            'positive', 'proper_sg', 'proper_pl', 'verb_form', 'noun_form',
            'adj_form', 'adv_form', 'form'
        ]
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    ) 