"""
About section component for the sidebar.
"""

import streamlit as st
from src.constants import VERSION, VERSION_NAME


def render_about_section():
    """Render the About section in an expandable container."""
    with st.expander("ℹ️ About", expanded=False):
        st.markdown("""
        ### WordNet Explorer
        
        This tool allows you to explore semantic relationships between words using [WordNet](https://wordnet.princeton.edu/), 
        a large lexical database of English where words are grouped into sets of cognitive synonyms (synsets).
        
        #### 📖 How to use:
        1. Enter a word to explore its semantic relationships
        2. Select which types of relationships to display
        3. Adjust the exploration depth and visual settings
        4. Double-click nodes in the graph to navigate to related words
        
        #### 🔗 Relationship Types:
        - **Hypernyms**: More general concepts ("is a" relationships)
        - **Hyponyms**: More specific concepts 
        - **Meronyms**: Parts or components
        - **Holonyms**: Wholes that contain the word
        - **Antonyms**: Opposite meanings
        - **Similar-to**: Related meanings (for adjectives)
        
        #### 🎯 Navigation Tips:
        - **Double-click** any node to explore that word
        - Use the **breadcrumb** to navigate back
        - Click words in **search history** to revisit them
        - The URL updates as you navigate (shareable links!)
        
        #### 🔧 Advanced Features:
        - **Synset Search Mode**: Focus on a specific word sense (meaning)
        - **URL Parameters**: Share or bookmark specific graph configurations
        - **Node Clustering**: Group related concepts visually
        - **Cross-Connections**: Find hidden relationships between nodes
        
        #### 📊 Performance Tips:
        - Keep depth ≤ 3 for most words
        - Use relationship filters to reduce graph size
        - Enable "Simplified Mode" for large graphs
        - Disable physics simulation for static viewing
        
        ---
        Built with ❤️ using [Streamlit](https://streamlit.io/), 
        [NetworkX](https://networkx.org/), and [NLTK WordNet](https://www.nltk.org/howto/wordnet.html)
        """)
        
        # Version info
        st.markdown(f"**Version:** {VERSION} ({VERSION_NAME})")
        
        # Links
        st.markdown("""
        **Resources:**
        - [WordNet Documentation](https://wordnet.princeton.edu/documentation)
        - [NLTK WordNet Interface](https://www.nltk.org/howto/wordnet.html)
        - [Source Code](https://github.com/your-repo/wordnet-explorer)
        """)
        
        # Debug mode toggle
        if st.checkbox("Enable debug mode", value=False, key="debug_mode"):
            st.info("Debug mode enabled. Check the main area for session state information.") 