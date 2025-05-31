#!/usr/bin/env python3
"""
Streamlit App Entry Point for Deployment
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Initialize Streamlit
import streamlit as st
from streamlit.runtime.scriptrunner import ScriptRunContext

# Import and run the main app
from app import main

if __name__ == "__main__":
    main()
else:
    # For deployment environments that import this module
    main() 