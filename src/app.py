#!/usr/bin/env python3
"""
WordNet Explorer - Streamlit UI (Refactored Modular Version)

A web-based interface for exploring WordNet semantic relationships
using Streamlit with a clean, modular architecture. 
"""

import streamlit as st

import streamlit.components.v1 as components
import sys
import os
import warnings

# Suppress specific Streamlit warnings more comprehensively
warnings.filterwarnings("ignore", message=".*was created with a default value but also had its value set via the Session State API.*")
warnings.filterwarnings("ignore", message=".*widget.*default value.*Session State API.*")
warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")

# Add parent directory to path to allow imports (works for both local and deployment)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import configuration
from config.settings import PAGE_CONFIG

# Import core modules
from core import WordNetExplorer, SessionManager

# Import UI components
from ui.styles import load_custom_css
from ui.sidebar import render_sidebar
from ui.word_info import render_word_information
from ui.graph_display import render_graph_visualization, render_graph_legend_and_controls
from ui.welcome import render_welcome_screen
from ui.footer import render_footer
from ui.comparison import render_comparison_view
from ui.path_finding import render_path_finding_view

# Import enhanced history functionality
from utils.session_state import add_query_to_history, initialize_session_state


def render_header():
    """Render the header with title."""
    # App title and description
    st.markdown('<h1 class="main-header">WordNet Explorer</h1>', unsafe_allow_html=True)
    st.markdown("Explore semantic relationships between words using WordNet")


def render_search_sidebar(session_manager):
    """Render the sidebar for the Search tab."""
    return render_sidebar(session_manager)


def render_sense_sidebar():
    """Render the sidebar for the Sense tab."""
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">🧠 Sense Explorer</h2>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Word input
        st.markdown("### 📝 Input Word")
        word = st.text_input(
            "Enter a word to analyze",
            placeholder="e.g., bank",
            key="sense_word_input",
            help="Enter the word whose senses you want to disambiguate"
        )
        
        st.markdown("---")
        
        # Definition input
        st.markdown("### 📖 Definition Matching")
        definition_sentence = st.text_area(
            "Enter a definition",
            placeholder="e.g., A financial institution that accepts deposits",
            key="sense_definition_input",
            height=100,
            help="Provide a definition to match against WordNet sense definitions"
        )
        
        st.markdown("---")
        
        # Context sentence input
        st.markdown("### 💬 Context Matching")
        context_sentence = st.text_area(
            "Enter usage in context",
            placeholder="e.g., I need to go to the bank to deposit my check",
            key="sense_context_input",
            height=100,
            help="Provide a sentence using the word in context"
        )
        
        st.markdown("---")
        
        # Scoring options
        st.markdown("### ⚙️ Scoring Options")
        use_definition = st.checkbox("Use Definition Similarity", value=True, key="use_definition_score")
        use_context = st.checkbox("Use Context Similarity", value=True, key="use_context_score")
        
        # Part of speech filtering options
        st.markdown("### 🔤 Part of Speech Filtering")
        limit_pos_to_context = st.checkbox(
            "Limit part of speech to context",
            value=False,
            key="limit_pos_to_context",
            help="Only consider senses that match the part of speech used in your context sentence"
        )
        
        pos_filter_options = ["Nouns", "Verbs", "Adjectives", "Adverbs"]
        selected_pos = st.multiselect(
            "Limit to specific parts of speech",
            options=pos_filter_options,
            default=pos_filter_options,  # All selected by default
            key="sense_pos_filter",
            help="Select which parts of speech to include in the analysis. Leave all selected to include everything."
        )
        
        # Visualization options
        st.markdown("### 🎨 Visualization Options")
        show_top_n = st.slider(
            "Show top N senses",
            min_value=1,
            max_value=10,
            value=5,
            key="sense_top_n",
            help="Number of top-scoring senses to display"
        )
        
        min_score = st.slider(
            "Minimum similarity score",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.05,
            key="sense_min_score",
            help="Hide senses with similarity below this threshold"
        )
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ How it works"):
            st.markdown("""
            **Definition Matching**: Compares your definition against WordNet definitions using semantic embeddings.
            
            **Context Matching**: Analyzes how well each sense fits in your example sentence.
            
            **Part of Speech Filtering**:
            - **Limit to context**: Automatically detects the part of speech used in your context sentence and only shows matching senses
            - **Manual selection**: Choose specific parts of speech (nouns, verbs, etc.) to include in the analysis
            
            **Similarity Scores**: Range from 0 (no similarity) to 1 (perfect match).
            
            **Visualization Types**:
            - 🟢 Green: Definition similarity
            - 🔵 Blue: Context similarity
            - 🟣 Purple: Combined score
            """)
    
    # Return settings
    return {
        'word': word.strip().lower() if word else None,
        'definition_sentence': definition_sentence.strip() if definition_sentence else None,
        'context_sentence': context_sentence.strip() if context_sentence else None,
        'use_definition': use_definition,
        'use_context': use_context,
        'limit_pos_to_context': limit_pos_to_context,
        'selected_pos': selected_pos,
        'show_top_n': show_top_n,
        'min_score': min_score
    }


def render_search_content(explorer, session_manager, settings):
    """Render the content for the Search tab."""
    # Check if we're in comparison mode
    compare_mode = st.session_state.get('compare_mode', False)
    path_finding_mode = st.session_state.get('path_finding_mode', False)
    
    if path_finding_mode:
        # Path finding mode
        render_path_finding_view(explorer)
    elif compare_mode:
        # Comparison mode - render merged graph
        render_comparison_view(explorer)
    else:
        # Normal mode - single graph view
        # Handle URL navigation
        session_manager.handle_url_navigation()
        
        # Determine the current word to display
        current_display_word = settings.get('word') or session_manager.get_current_word()
        
        # Debug logging
        print(f"🔍 APP: current_display_word='{current_display_word}', settings_word='{settings.get('word')}', current_word='{session_manager.get_current_word()}'")
        print(f"🔍 APP: word_changed={settings.get('word_changed', False)}, parsed_sense={settings.get('parsed_sense_number')}")
        
        # Check if this is a new query that should be added to history
        # This happens when word_changed is True OR when we have a word that's being displayed
        should_add_to_history = False
        
        # Update session state if this is a new word from input
        if settings.get('word') and settings['word'] != session_manager.get_current_word():
            # Update session state without modifying the widget
            st.session_state.current_word = settings['word']
            st.session_state.last_searched_word = settings['word']
            session_manager.add_to_history(settings['word'])
            should_add_to_history = True
            current_display_word = settings['word']
            print(f"🔍 APP: New word detected, should_add_to_history=True")
        
        # Also add to history if word_changed flag is set (user pressed Enter)
        if settings.get('word_changed', False) and settings.get('word'):
            should_add_to_history = True
            print(f"🔍 APP: word_changed flag set, should_add_to_history=True")
        
        print(f"🔍 APP: Final should_add_to_history={should_add_to_history}")
        
        # Main content area
        if current_display_word:
            try:
                # Check if we're in synset search mode
                synset_search_mode = settings.get('synset_search_mode', False)
                display_input = current_display_word
                
                # If in synset search mode, convert word+sense to synset name
                if synset_search_mode and settings.get('parsed_sense_number'):
                    from src.wordnet import get_synsets_for_word
                    synsets = get_synsets_for_word(current_display_word)
                    sense_number = settings['parsed_sense_number']
                    if synsets and 1 <= sense_number <= len(synsets):
                        # Use the synset name instead of the word
                        display_input = synsets[sense_number - 1].name()
                    else:
                        st.error(f"Invalid sense number {sense_number} for word '{current_display_word}'")
                        synset_search_mode = False  # Fall back to word mode
                
                # Add complete query to enhanced history if needed
                if should_add_to_history:
                    print(f"🔍 APP: Calling add_query_to_history with settings")
                    add_query_to_history(settings)
                else:
                    print(f"🔍 APP: NOT calling add_query_to_history")
                    # Fallback: If we're displaying a word but it's not in history, add it
                    from src.utils.session_state import get_search_history_manager
                    from src.models.search_history import SearchQuery
                    
                    history_manager = get_search_history_manager()
                    current_query = SearchQuery.from_settings(settings)
                    
                    # Check if this exact query exists in history
                    query_exists = any(q.get_hash() == current_query.get_hash() for q in history_manager.queries)
                    
                    if not query_exists and current_display_word:
                        print(f"🔍 APP: Query not in history, adding as fallback")
                        add_query_to_history(settings)
                
                # Show word information if requested (not applicable in synset mode)
                if settings.get('show_info', False) and not synset_search_mode:
                    render_word_information(current_display_word)
                
                # Build and display graph if requested
                if settings.get('show_graph', True):
                    render_graph_visualization(display_input, settings, explorer, synset_search_mode)
            
            except Exception as e:
                st.error(f"Error: {e}")
                if settings.get('synset_search_mode', False):
                    st.error("Please check that you have entered a valid synset name (e.g., 'dog.n.01').")
                else:
                    st.error("Please check that you have entered a valid English word.")
        
        else:
            # Show welcome screen
            render_welcome_screen()


def render_sense_content(explorer, session_manager, settings):
    """Render the content for the Sense tab."""
    
    # Check if we have the required inputs
    if not settings.get('word'):
        st.markdown(
            """
            <div style="text-align: center; padding: 50px;">
                <h2>👋 Welcome to Sense Disambuation Tool!</h2>
                <p style="font-size: 18px; color: #666;">
                    Enter a word in the sidebar to begin exploring its different senses.
                </p>
                <p style="font-size: 16px; color: #888; margin-top: 20px;">
                    You can provide a definition or usage context to find the most relevant sense.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    # Check if at least one input method is selected
    if not settings['use_definition'] and not settings['use_context']:
        st.warning("Please select at least one scoring method (Definition or Context) in the sidebar.")
        return
    
    # Check if we have input for the selected methods
    if settings['use_definition'] and not settings.get('definition_sentence'):
        st.info("Please enter a definition in the sidebar to use definition matching.")
        return
    
    if settings['use_context'] and not settings.get('context_sentence'):
        st.info("Please enter a context sentence in the sidebar to use context matching.")
        return
    
    # Import required modules
    try:
        from src.wordnet import get_synsets_for_word
        from src.services.sense_similarity import get_sense_similarity_calculator
        from src.ui.sense_graph import render_sense_graph_visualization
    except ImportError as e:
        st.error(f"Error importing required modules: {e}")
        return
    
    # Get synsets for the word
    word = settings['word']
    
    with st.spinner(f"Loading senses for '{word}'..."):
        try:
            synsets = get_synsets_for_word(word)
            
            if not synsets:
                st.warning(f"No senses found for '{word}'. Please check the spelling or try a different word.")
                return
            
            st.success(f"Found {len(synsets)} senses for '{word}'")
            
        except Exception as e:
            st.error(f"Error retrieving senses: {e}")
            return
    
    # Show filtering information
    if settings.get('limit_pos_to_context') and settings.get('context_sentence'):
        st.info("🔤 **Part of Speech Filtering**: Limiting to senses that match the detected part of speech in your context sentence")
    elif settings.get('selected_pos') and len(settings.get('selected_pos', [])) < 4:
        selected_pos_str = ", ".join(settings.get('selected_pos', []))
        st.info(f"🔤 **Part of Speech Filtering**: Limiting to {selected_pos_str}")
    
    # Calculate similarities
    with st.spinner("Calculating similarities..."):
        try:
            calculator = get_sense_similarity_calculator()
            
            sense_scores = calculator.calculate_sense_similarities(
                word=word,
                synsets=synsets,
                definition_input=settings.get('definition_sentence'),
                context_input=settings.get('context_sentence'),
                limit_pos_to_context=settings.get('limit_pos_to_context', False),
                selected_pos=settings.get('selected_pos', ['Nouns', 'Verbs', 'Adjectives', 'Adverbs'])
            )
            
            # Check if filtering removed all senses
            if not sense_scores:
                if settings.get('limit_pos_to_context') and settings.get('context_sentence'):
                    st.warning("⚠️ No senses found matching the detected part of speech from your context sentence. Try disabling 'Limit part of speech to context' or check your context sentence.")
                elif settings.get('selected_pos') and len(settings.get('selected_pos', [])) < 4:
                    selected_pos_str = ", ".join(settings.get('selected_pos', []))
                    st.warning(f"⚠️ No senses found for the selected parts of speech ({selected_pos_str}). Try selecting additional parts of speech.")
                else:
                    st.warning("⚠️ No senses found after filtering.")
                return
            
        except Exception as e:
            st.error(f"Error calculating similarities: {e}")
            st.exception(e)
            return
    
    # Display input information
    st.markdown("### 📊 Analysis Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if settings.get('definition_sentence'):
            st.markdown("**Your Definition:**")
            st.info(settings['definition_sentence'])
    
    with col2:
        if settings.get('context_sentence'):
            st.markdown("**Your Context:**")
            st.info(settings['context_sentence'])
    
    st.markdown("---")
    
    # Display the sense similarity graph
    st.markdown("### 🕸️ Sense Similarity Network")
    
    render_sense_graph_visualization(word, sense_scores, settings)
    
    # Display additional insights
    st.markdown("---")
    st.markdown("### 💡 Insights")
    
    if sense_scores and sense_scores[0].max_score >= 0.7:
        st.success(f"**Best Match**: Sense {sense_scores[0].synset_name.split('.')[-1].lstrip('0')} "
                  f"with {sense_scores[0].max_score:.1%} similarity")
        st.markdown(f"*Definition*: {sense_scores[0].definition}")
    elif sense_scores and sense_scores[0].max_score >= 0.4:
        st.info(f"**Likely Match**: Sense {sense_scores[0].synset_name.split('.')[-1].lstrip('0')} "
               f"with {sense_scores[0].max_score:.1%} similarity")
        st.markdown(f"*Definition*: {sense_scores[0].definition}")
    else:
        st.warning("No strong matches found. Try providing more specific definitions or context.")


def render_sentence_sidebar():
    """Render the sidebar for the Sentence Explorer tab."""
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">🔤 Sentence Explorer</h2>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sentence input
        st.markdown("### 📝 Input Sentence")
        sentence = st.text_area(
            "Enter a sentence to analyze",
            placeholder="e.g., The quick brown fox jumps over the lazy dog.",
            key="sentence_input",
            height=100,
            help="Enter a complete sentence to analyze its grammatical structure and word senses"
        )
        
        st.markdown("---")
        
        # Visualization options
        st.markdown("### 🎨 Visualization Options")
        
        show_synsets = st.checkbox(
            "Show WordNet synsets",
            value=True,
            key="sentence_show_synsets",
            help="Display WordNet word senses for each word"
        )
        
        if show_synsets:
            synset_limit = st.slider(
                "Max synsets per word",
                min_value=1,
                max_value=5,
                value=3,
                key="sentence_synset_limit",
                help="Maximum number of synsets to show for each word"
            )
        else:
            synset_limit = 0
        
        show_synset_details = st.checkbox(
            "Show synset details",
            value=True,
            key="sentence_show_details",
            help="Show expandable details for each synset"
        )
        
        st.markdown("---")
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            enable_physics = st.checkbox(
                "Enable physics simulation",
                value=True,
                key="sentence_enable_physics",
                help="Enable interactive physics for node positioning"
            )
            
            disambiguate_senses = st.checkbox(
                "Auto-disambiguate senses",
                value=False,
                key="sentence_disambiguate",
                help="Automatically select the most likely sense for each word (experimental)"
            )
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ How it works"):
            st.markdown("""
            **Sentence Explorer** analyzes the grammatical structure of your sentence and connects it to WordNet:
            
            1. **Syntactic Analysis**: Shows how words and clauses relate hierarchically
            2. **Part-of-Speech Tagging**: Identifies the grammatical role of each word
            3. **Smart WordNet Integration**: Links content words to their best matching senses
            
            **Improved disambiguation features:**
            - Pronouns and function words are excluded from synset matching
            - Common words avoid overly technical definitions (no "iodine" for "I"!)
            - Phrasal verb particles (like "over" in "run over") are handled correctly
            - Context-aware sense selection filters out inappropriate meanings
            
            **The visualization shows:**
            - Complete sentence as the root node
            - Clauses as intermediate nodes
            - Words as leaf nodes with synset information
            - Labeled edges showing grammatical relationships
            
            **Edge labels:**
            - **sconj**: Subordinating conjunction
            - **iclause/dclause**: Independent/dependent clause
            - **tverb**: Main (tensed) verb
            - **subj/obj**: Subject/object
            - **adv/adj**: Adverb/adjective modifier
            
            **Interactive features:**
            - Hover over nodes for detailed information
            - Words with synsets show definitions in tooltips
            - Drag nodes to rearrange the layout
            - Zoom and pan to explore the graph
            """)
    
    # Return settings
    return {
        'sentence': sentence.strip() if sentence else None,
        'show_synsets': show_synsets,
        'synset_limit': synset_limit,
        'show_synset_details': show_synset_details,
        'enable_physics': enable_physics,
        'disambiguate_senses': disambiguate_senses
    }


def render_sentence_content(explorer, session_manager, settings):
    """Render the content for the Sentence Explorer tab."""
    
    # Check if we have input
    if not settings.get('sentence'):
        st.markdown(
            """
            <div style="text-align: center; padding: 50px;">
                <h2>👋 Welcome to Sentence Explorer!</h2>
                <p style="font-size: 18px; color: #666;">
                    Enter a sentence in the sidebar to begin analyzing its structure.
                </p>
                <p style="font-size: 16px; color: #888; margin-top: 20px;">
                    This tool combines grammatical analysis with WordNet to show how words relate to each other and their meanings.
                </p>
                <div style="margin-top: 30px;">
                    <h3>Example sentences to try:</h3>
                    <ul style="text-align: left; display: inline-block;">
                        <li>"The bank near the river has beautiful flowers."</li>
                        <li>"She will bank on her experience to solve the problem."</li>
                        <li>"The pilot flies planes across the ocean every week."</li>
                        <li>"Time flies when you're having fun at the party."</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    # Import required modules
    try:
        from src.services.sentence_analyzer_v2 import SentenceAnalyzerV2 as SentenceAnalyzer
        from src.ui.sentence_graph import render_sentence_graph_visualization, render_sentence_legend
    except ImportError as e:
        st.error(f"Error importing required modules: {e}")
        return
    
    # Analyze the sentence
    sentence = settings['sentence']
    
    with st.spinner(f"Analyzing sentence..."):
        try:
            analyzer = SentenceAnalyzer()
            analysis = analyzer.analyze_sentence(sentence)
            
            st.success(f"Analyzed sentence with {len(analysis.tokens)} tokens")
            
        except Exception as e:
            st.error(f"Error analyzing sentence: {e}")
            if "spacy" in str(e).lower():
                st.info("💡 **Tip**: Make sure spaCy is installed with: `pip install spacy`")
                st.info("Then download the English model: `python -m spacy download en_core_web_sm`")
            return
    
    # Display the analysis
    st.markdown("### 📊 Analysis Summary")
    
    # Show sentence with POS tags
    pos_tagged = " ".join([f"{token.text}_{token.tag}" for token in analysis.tokens])
    st.code(pos_tagged, language="text")
    
    # If auto-disambiguation is enabled, try to disambiguate
    if settings.get('disambiguate_senses', False):
        with st.spinner("Disambiguating word senses..."):
            for token in analysis.tokens:
                if token.synsets:
                    # Simple disambiguation - just use first synset for now
                    # In a real implementation, we'd use context-based disambiguation
                    token.selected_sense = analyzer.disambiguate_token(token, sentence)
    
    st.markdown("---")
    
    # Render the visualization
    render_sentence_graph_visualization(analysis, settings)
    
    # Render the legend
    st.markdown("---")
    st.markdown("### 🗝️ Graph Legend")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_sentence_legend()
    
    with col2:
        st.markdown("""
        <div class="legend-container">
            <h4>💡 Tips</h4>
            <ul>
                <li><strong>Hover</strong> over nodes to see detailed information</li>
                <li><strong>Drag</strong> nodes to rearrange the layout</li>
                <li><strong>Zoom</strong> with mouse wheel to see details</li>
                <li>The <strong>sentence root</strong> shows the complete text</li>
                <li><strong>Clauses</strong> break down complex sentences</li>
                <li><strong>Words</strong> show synset definitions on hover</li>
                <li><strong>Edge labels</strong> describe grammatical relationships</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# Tab Configuration - Add new tabs here!
TAB_CONFIG = {
    'search': {
        'label': '🔍 Network Explorer',
        'sidebar_function': render_search_sidebar,
        'content_function': render_search_content,
        'description': 'Explore word relationships and semantic networks'
    },
    'sense': {
        'label': '🧠 Sense Disambuation',
        'sidebar_function': render_sense_sidebar,
        'content_function': render_sense_content,
        'description': 'Advanced sense disambiguation and analysis'
    },
    'sentence': {
        'label': '🔤 Sentence Explorer',
        'sidebar_function': render_sentence_sidebar,
        'content_function': render_sentence_content,
        'description': 'Analyze sentence structure with WordNet integration'
    },
    # Future tabs can be added here easily:
    # 'analysis': {
    #     'label': '📊 Analysis',
    #     'sidebar_function': render_analysis_sidebar,
    #     'content_function': render_analysis_content,
    #     'description': 'Statistical analysis and insights'
    # },
    # 'export': {
    #     'label': '💾 Export',
    #     'sidebar_function': render_export_sidebar,
    #     'content_function': render_export_content,
    #     'description': 'Export data and visualizations'
    # }
}


def render_tab_buttons(active_tab):
    """Render tab buttons based on configuration."""
    tab_keys = list(TAB_CONFIG.keys())
    num_tabs = len(tab_keys)
    
    # Create columns for tab buttons
    cols = st.columns(num_tabs)
    
    for i, (tab_key, tab_info) in enumerate(TAB_CONFIG.items()):
        with cols[i]:
            button_type = "primary" if active_tab == tab_key else "secondary"
            if st.button(
                tab_info['label'], 
                type=button_type,
                use_container_width=True,
                help=tab_info['description']
            ):
                st.session_state.active_tab = tab_key
                st.rerun()


def main():
    """Main application function."""
    # Set page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize session state for enhanced history
    initialize_session_state()
    
    # Initialize active tab in session state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 'search'  # Default to first tab
    
    # Validate active tab (in case config changes)
    if st.session_state.active_tab not in TAB_CONFIG:
        st.session_state.active_tab = 'search'
    
    # Initialize core components
    session_manager = SessionManager()
    explorer = WordNetExplorer()
    
    # Load custom CSS
    load_custom_css()
    
    # Render header with logo
    render_header()
    
    # Render tab buttons
    render_tab_buttons(st.session_state.active_tab)
    
    st.markdown("---")
    
    # Get current tab configuration
    current_tab_config = TAB_CONFIG[st.session_state.active_tab]
    
    # Render appropriate sidebar based on active tab
    sidebar_function = current_tab_config['sidebar_function']
    if sidebar_function == render_search_sidebar:
        settings = sidebar_function(session_manager)
    else:
        settings = sidebar_function()
    
    # Render content based on active tab
    content_function = current_tab_config['content_function']
    content_function(explorer, session_manager, settings)
    
    # Display debug information if enabled
    session_manager.log_debug_info()
    
    # Render footer
    render_footer()


if __name__ == "__main__":
    main() 