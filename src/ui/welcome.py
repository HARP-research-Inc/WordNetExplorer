"""
Welcome screen component for WordNet Explorer.
"""

import streamlit as st


def render_welcome_screen():
    """Render the welcome screen with instructions and examples."""
    st.markdown("""
    ## Welcome to WordNet Explorer!
    
    Enter a word in the sidebar to explore its semantic relationships in WordNet.
    
    ### Features:
    - 🔍 **Word Exploration**: Discover semantic relationships for any English word
    - 📊 **Graph Visualization**: Interactive network graphs showing word connections
    - 🎨 **Color-coded Relationships**: Different colors for hypernyms, hyponyms, meronyms, etc.
    - 📖 **Detailed Information**: View definitions, examples, and related words
    - 💾 **Save Graphs**: Export visualizations as HTML files
    - 🎯 **Configurable Depth**: Control how deep to explore relationships
    - 🧭 **Navigation History**: Track your exploration path with breadcrumbs
    - ⚙️ **Customizable Display**: Multiple color schemes, layouts, and physics options
    
    ### Example Words to Try:
    - **dog** - Explore animal classifications and relationships
    - **computer** - Discover technology and device connections
    - **tree** - Navigate plant taxonomy and parts
    - **love** - Understand emotional and abstract concepts
    - **book** - See information and literary relationships
    - **run** - Explore action verbs and their variations
    - **happiness** - Investigate emotional states and feelings
    - **ocean** - Navigate geographic and natural features
    
    ### How to Use:
    1. **Enter a word** in the sidebar text input
    2. **Adjust settings** using the collapsible sections
    3. **Explore the graph** by double-clicking nodes to navigate
    4. **Use breadcrumbs** to track your exploration path
    5. **Customize appearance** with different color schemes and layouts
    6. **Save interesting graphs** using the save options
    
    Start your semantic journey by entering a word in the sidebar! 🚀
    """) 