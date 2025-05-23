#!/usr/bin/env python3
"""
Entry point for WordNet Explorer CLI Tool
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wordnet_explorer import main

if __name__ == "__main__":
    main() 