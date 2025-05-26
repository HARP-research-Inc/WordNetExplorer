"""
WordNet Data Access Module

Handles downloading and accessing WordNet data through NLTK.
"""

import nltk


def download_nltk_data():
    """Download required NLTK data if not already present."""
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading WordNet data...")
        nltk.download('wordnet')
    
    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        print("Downloading additional WordNet data...")
        nltk.download('omw-1.4') 