"""
Word information display components for WordNet Explorer.
"""

import streamlit as st
from ..utils.helpers import capture_function_output
from ..wordnet_explorer import print_word_info


def render_word_information(word):
    """
    Render the word information section.
    
    Args:
        word (str): The word to display information for
    """
    st.markdown('<h2 class="sub-header">Word Information</h2>', unsafe_allow_html=True)
    
    # Capture the output of print_word_info
    word_info = capture_function_output(print_word_info, word)
    
    # Display the word info with formatting
    st.markdown(f"<div class='info-box'>{word_info}</div>", unsafe_allow_html=True) 