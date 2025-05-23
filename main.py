#!/usr/bin/env python3
"""
WordNet Explorer - Main Entry Point

This is the main entry point for the WordNet Explorer application.
It provides a simple interface to explore WordNet semantic relationships.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.cli import main

if __name__ == "__main__":
    main() 