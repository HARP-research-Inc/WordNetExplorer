#!/usr/bin/env python3
"""
Run the WordNet Explorer Streamlit app
"""

import os
import sys
import subprocess

def main():
    """Run the Streamlit app."""
    # Add src directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Get the path to the app.py file
    app_path = os.path.join(os.path.dirname(__file__), 'src', 'app.py')
    
    # Run the Streamlit app
    subprocess.run(['streamlit', 'run', app_path])

if __name__ == "__main__":
    main() 