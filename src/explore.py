#!/usr/bin/env python3
"""
Short alias for WordNet Explorer CLI Tool
Usage: python explore.py <word>
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from wordnet_explorer import main

if __name__ == "__main__":
    main() 