"""
Footer Module

Renders the application footer with logo, copyright, and version information.
"""

import streamlit as st
import os
import base64


def render_footer():
    """Render the footer with logo, copyright and link."""
    st.markdown("---")
    
    # Display logo using HTML for full control
    _render_logo()
    
    # Get WordNet version information
    version_info = _get_version_info()
    
    # Copyright, version info, and link
    st.markdown(
        f"""
        <div style="text-align: center; padding: 10px 0; color: #666; font-size: 14px;">
            <p style="margin: 5px 0;">{version_info}</p>
            <p style="margin: 5px 0;">© 2025 HARP Research, Inc. | <a href="https://harpresearch.ai" target="_blank" style="color: #1f77b4; text-decoration: none;">https://harpresearch.ai</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )


def _render_logo():
    """Render the HARP Research logo."""
    try:
        logo_path = os.path.join(os.path.dirname(__file__), "..", "T-Shirt Logo.png")
        if os.path.exists(logo_path):
            # Read and encode the image
            with open(logo_path, "rb") as img_file:
                img_bytes = img_file.read()
                img_base64 = base64.b64encode(img_bytes).decode()
            
            # Display using HTML with full control
            st.markdown(
                f"""
                <div style="text-align: center; padding: 20px 0;">
                    <img src="data:image/png;base64,{img_base64}" 
                         style="width: 300px; 
                                border-radius: 0px !important; 
                                border: none !important;
                                box-shadow: none !important;
                                display: block;
                                margin: 0 auto;" 
                         alt="HARP Research Logo">
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception:
        # If logo fails to load, just continue without it
        st.markdown('<div style="text-align: center; padding: 20px 0;"></div>', unsafe_allow_html=True)


def _get_version_info():
    """Get WordNet and NLTK version information."""
    try:
        from nltk.corpus import wordnet as wn
        import nltk
        
        # Try to get WordNet version info
        try:
            # Check if we can access WordNet info
            wn.synsets('test')  # Test access
            wordnet_version = "WordNet 3.0"  # Default assumption for NLTK
            
            # Try to get more specific version info if available
            try:
                # Some NLTK installations have version info
                if hasattr(wn, '_LazyCorpusLoader__args'):
                    wordnet_version = "WordNet 3.0 (NLTK)"
                else:
                    wordnet_version = "WordNet 3.0 (NLTK)"
            except:
                wordnet_version = "WordNet 3.0"
                
        except:
            wordnet_version = "WordNet (version unavailable)"
            
        nltk_version = nltk.__version__
        return f"Powered by {wordnet_version} via NLTK {nltk_version}"
        
    except Exception:
        return "Powered by WordNet via NLTK" 