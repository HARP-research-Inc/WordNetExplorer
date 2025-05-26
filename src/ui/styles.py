"""
CSS styles and styling utilities for WordNet Explorer.
"""

import streamlit as st


def load_custom_css():
    """Load custom CSS styles for the application."""
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #4B8BBE;
            text-align: center;
            margin-bottom: 1rem;
        }
        .sub-header {
            font-size: 1.5rem;
            color: #306998;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .info-box {
            background-color: #f0f2f6;
            color: #222;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            font-family: monospace;
            white-space: pre-wrap;
        }
        .stButton>button {
            width: 100%;
        }
        .nav-history-container {
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        .legend-container {
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 10px;
            color: #333;
        }
        .color-dot {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            display: inline-block;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True) 