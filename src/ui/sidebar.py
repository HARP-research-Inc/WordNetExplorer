"""
Sidebar components for WordNet Explorer.
"""

import streamlit as st
from ..config.settings import DEFAULT_SETTINGS, LAYOUT_OPTIONS

from ..utils.session_state import add_to_search_history, clear_search_history
from ..utils.debug_logger import log_word_input_event, log_session_state
from ..wordnet_explorer import get_synsets_for_word


def get_url_default(session_manager, setting_key: str, default_value):
    """Get default value from URL parameters or fall back to default."""
    url_settings = session_manager.get_settings_from_url()
    return url_settings.get(setting_key, default_value)


def render_word_input(session_manager):
    """Render the word input field with search history."""
    log_session_state("FUNCTION_START")
    log_word_input_event("FUNCTION_ENTRY", function="render_word_input")
    
    # Check if a history word was selected
    selected_word = st.session_state.get('selected_history_word', None)
    log_word_input_event("SELECTED_WORD_CHECK", selected_word=selected_word)
    
    # Get word from URL if available
    url_word = get_url_default(session_manager, 'word', None)
    
    # Word input field - prioritize selected word, then URL word, then empty
    input_value = selected_word or url_word or ""
    log_word_input_event("INPUT_VALUE_CALCULATION", input_value=input_value, selected_word=selected_word, current_word=st.session_state.get('current_word', 'None'))
    
    word = st.text_input(
        "Enter a word to explore", 
        value=input_value,
        key="word_input",
        help="Press Enter to add the word to your search history"
    ).strip().lower()
    
    # Get sense number from URL if available
    url_sense = get_url_default(session_manager, 'sense_number', None)
    sense_input_value = str(url_sense) if url_sense is not None else ""
    
    # Sense number input field
    sense_number = st.text_input(
        "Sense number (optional)",
        value=sense_input_value,
        key="sense_number_input",
        help="Enter a specific sense number (1, 2, 3, etc.) to show only that sense. Leave blank to show all senses."
    ).strip()
    
    # Show available senses if word is provided
    if word:
        synsets = get_synsets_for_word(word)
        if synsets:
            st.info(f"💡 '{word}' has {len(synsets)} sense(s) available (1-{len(synsets)})")
        else:
            st.warning(f"⚠️ No WordNet entries found for '{word}'")
    
    # Convert sense number to integer if provided
    parsed_sense_number = None
    if sense_number:
        try:
            parsed_sense_number = int(sense_number)
            if parsed_sense_number < 1:
                st.warning("Sense number must be 1 or greater")
                parsed_sense_number = None
            elif word:  # Only validate if we have a word
                synsets = get_synsets_for_word(word)
                if synsets and parsed_sense_number > len(synsets):
                    st.warning(f"Sense number {parsed_sense_number} is too high. '{word}' only has {len(synsets)} sense(s)")
                    parsed_sense_number = None
        except ValueError:
            st.warning("Please enter a valid number for sense number")
    
    log_word_input_event("TEXT_INPUT_RESULT", word=word, input_value=input_value)
    
    # Handle selected word from history
    if selected_word:
        log_word_input_event("PROCESSING_SELECTED_WORD", selected_word=selected_word)
        # Clear the selected history word
        st.session_state.selected_history_word = None
        log_word_input_event("CLEARED_SELECTED_WORD")
        
        # Add to search history and update last searched word
        last_searched = st.session_state.get('last_searched_word', '')
        if selected_word != last_searched:
            log_word_input_event("ADDING_SELECTED_TO_HISTORY", selected_word=selected_word, last_searched=last_searched)
            add_to_search_history(selected_word)
            st.session_state.last_searched_word = selected_word
            st.session_state.previous_word_input = selected_word  # Update this too
            log_word_input_event("ADDED_SELECTED_TO_HISTORY", selected_word=selected_word)
        else:
            log_word_input_event("SKIPPED_SELECTED_DUPLICATE", selected_word=selected_word, last_searched=last_searched)
        
        # Return the selected word to ensure it's processed
        log_word_input_event("RETURNING_SELECTED_WORD", selected_word=selected_word)
        return selected_word, parsed_sense_number, True  # Word changed when selected from history
    
    # Use a more robust tracking mechanism that handles multiple function calls
    # Track the actual widget value instead of relying on previous_input
    current_widget_value = st.session_state.get('word_input', '')
    last_processed_value = st.session_state.get('last_processed_word_input', '')
    
    log_word_input_event("ROBUST_INPUT_CHECK", 
                        word=word, 
                        current_widget_value=current_widget_value,
                        last_processed_value=last_processed_value,
                        condition_met=bool(word and word != last_processed_value))
    
    # Add word to search history only when we have a new word that hasn't been processed
    if word and word != last_processed_value:
        log_word_input_event("ADDING_NORMAL_TO_HISTORY", word=word, last_processed_value=last_processed_value)
        add_to_search_history(word)
        st.session_state.last_searched_word = word
        st.session_state.previous_word_input = word
        st.session_state.last_processed_word_input = word  # Track what we've processed
        log_word_input_event("ADDED_NORMAL_TO_HISTORY", word=word)
    else:
        log_word_input_event("SKIPPED_NORMAL_INPUT", 
                            word=word, 
                            last_processed_value=last_processed_value, 
                            word_exists=bool(word), 
                            words_different=word != last_processed_value)
    
    log_session_state("FUNCTION_END")
    log_word_input_event("FUNCTION_EXIT", returning_word=word)
    
    # Determine if word changed (Enter was pressed)
    word_changed = bool(word and word != last_processed_value)
    
    return word, parsed_sense_number, word_changed


def render_search_history():
    """Render the search history in a collapsible expander."""
    log_word_input_event("SEARCH_HISTORY_RENDER_START", history_length=len(st.session_state.get('search_history', [])))
    
    if st.session_state.search_history:
        with st.expander("🔍 Search & Navigation History", expanded=False):
            st.markdown("Click any word to explore it again:")
            
            # Create columns for history items and clear button
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Display search history as clickable buttons
                for i, hist_word in enumerate(st.session_state.search_history):
                    log_word_input_event("RENDERING_HISTORY_BUTTON", index=i, hist_word=hist_word, button_key=f"search_history_{i}")
                    if st.button(f"📝 {hist_word}", key=f"search_history_{i}", help=f"Click to explore '{hist_word}'"):
                        log_word_input_event("HISTORY_BUTTON_CLICKED", hist_word=hist_word, index=i)
                        st.session_state.selected_history_word = hist_word
                        log_word_input_event("SET_SELECTED_HISTORY_WORD", hist_word=hist_word)
                        log_session_state("BEFORE_RERUN")
                        st.rerun()
            
            with col2:
                if st.button("🗑️", help="Clear search history", key="clear_search_history"):
                    log_word_input_event("CLEAR_HISTORY_CLICKED")
                    clear_search_history()
                    st.rerun()
    else:
        log_word_input_event("NO_SEARCH_HISTORY_TO_RENDER")


def render_basic_settings(session_manager):
    """Render basic exploration settings."""
    depth = st.slider(
        "Exploration depth", 
        min_value=1, 
        max_value=3, 
        value=get_url_default(session_manager, 'depth', DEFAULT_SETTINGS['depth']), 
        help="How deep to explore relationships (higher values create larger graphs)"
    )
    return depth


def render_relationship_types(session_manager):
    """Render relationship type checkboxes."""
    with st.expander("🔗 Relationship Types", expanded=True):
        show_hypernyms = st.checkbox("Include Hypernyms (↑)", value=get_url_default(session_manager, 'show_hypernyms', DEFAULT_SETTINGS['show_hypernyms']))
        show_hyponyms = st.checkbox("Include Hyponyms (↓)", value=get_url_default(session_manager, 'show_hyponyms', DEFAULT_SETTINGS['show_hyponyms']))
        show_meronyms = st.checkbox("Include Meronyms (⊂)", value=get_url_default(session_manager, 'show_meronyms', DEFAULT_SETTINGS['show_meronyms']))
        show_holonyms = st.checkbox("Include Holonyms (⊃)", value=get_url_default(session_manager, 'show_holonyms', DEFAULT_SETTINGS['show_holonyms']))
    
    return show_hypernyms, show_hyponyms, show_meronyms, show_holonyms


def render_graph_appearance(session_manager):
    """Render graph appearance settings."""
    with st.expander("🎨 Graph Appearance"):
        # Layout options
        default_layout = get_url_default(session_manager, 'layout_type', DEFAULT_SETTINGS['layout_type'])
        try:
            layout_index = LAYOUT_OPTIONS.index(default_layout)
        except ValueError:
            layout_index = LAYOUT_OPTIONS.index(DEFAULT_SETTINGS['layout_type'])
        
        layout_type = st.selectbox(
            "Graph Layout",
            LAYOUT_OPTIONS,
            index=layout_index,
            help="Choose how nodes are arranged in the graph"
        )
        
        # Node size settings
        node_size_multiplier = st.slider(
            "Node Size", 
            min_value=0.5, 
            max_value=2.0, 
            value=get_url_default(session_manager, 'node_size_multiplier', DEFAULT_SETTINGS['node_size_multiplier']), 
            step=0.1,
            help="Adjust the size of nodes in the graph"
        )
        
        # Color scheme
        color_options = ["Default", "Pastel", "Vibrant", "Monochrome"]
        default_color = get_url_default(session_manager, 'color_scheme', DEFAULT_SETTINGS['color_scheme'])
        try:
            color_index = color_options.index(default_color)
        except ValueError:
            color_index = color_options.index(DEFAULT_SETTINGS['color_scheme'])
        
        color_scheme = st.selectbox(
            "Color Scheme",
            color_options,
            index=color_index,
            help="Choose a color scheme for the graph"
        )
    
    return layout_type, node_size_multiplier, color_scheme


def render_physics_simulation(session_manager):
    """Render physics simulation settings."""
    with st.expander("⚙️ Physics Simulation"):
        enable_physics = st.checkbox(
            "Enable Physics", 
            value=get_url_default(session_manager, 'enable_physics', DEFAULT_SETTINGS['enable_physics']), 
            help="Allow nodes to move and settle automatically"
        )
        
        if enable_physics:
            spring_strength = st.slider(
                "Spring Strength", 
                min_value=0.01, 
                max_value=0.1, 
                value=get_url_default(session_manager, 'spring_strength', DEFAULT_SETTINGS['spring_strength']), 
                step=0.01,
                help="How strongly nodes are pulled together"
            )
            
            central_gravity = st.slider(
                "Central Gravity", 
                min_value=0.1, 
                max_value=1.0, 
                value=get_url_default(session_manager, 'central_gravity', DEFAULT_SETTINGS['central_gravity']), 
                step=0.1,
                help="How strongly nodes are pulled to the center"
            )
        else:
            spring_strength = DEFAULT_SETTINGS['spring_strength']
            central_gravity = DEFAULT_SETTINGS['central_gravity']
    
    return enable_physics, spring_strength, central_gravity


def render_visual_options(session_manager):
    """Render visual options settings."""
    with st.expander("👁️ Visual Options"):
        show_labels = st.checkbox("Show Node Labels", value=get_url_default(session_manager, 'show_labels', DEFAULT_SETTINGS['show_labels']))
        edge_width = st.slider("Edge Width", min_value=1, max_value=5, value=get_url_default(session_manager, 'edge_width', DEFAULT_SETTINGS['edge_width']))
    
    return show_labels, edge_width


def render_display_options(session_manager):
    """Render display options settings."""
    with st.expander("📋 Display Options", expanded=True):
        show_info = st.checkbox("Show word information", value=get_url_default(session_manager, 'show_info', DEFAULT_SETTINGS['show_info']))
        show_graph = st.checkbox("Show relationship graph", value=get_url_default(session_manager, 'show_graph', DEFAULT_SETTINGS['show_graph']))
    
    return show_info, show_graph


def render_save_options():
    """Render save options settings."""
    with st.expander("💾 Save Options"):
        save_graph = st.checkbox("Save graph to file")
        filename = "wordnet_graph"
        if save_graph:
            filename = st.text_input("Filename (without extension)", "wordnet_graph")
            if not filename:
                filename = "wordnet_graph"
            if not filename.endswith(".html"):
                filename += ".html"
    
    return save_graph, filename


def render_about_section():
    """Render the about/help section."""
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This tool uses NLTK's WordNet to explore semantic relationships between words.
    
    **Word Input:**
    - Enter any English word to explore its meanings
    - Use the sense number field to focus on a specific meaning (1, 2, 3, etc.)
    - Leave sense number blank to see all meanings
    
    **Navigation:**
    - Double-click any node to explore that concept
    - Use search history to revisit previous words
    - All searched and navigated words appear in history
    
    **Node Types:**
    - 🔴 Root words - uppercase word forms (e.g., SHEEP, BOVINE)
    - 🟣 Word senses - specific meanings/synsets (e.g., sheep.n.01, bovine.n.01)
    
    **Edge Colors (Directed Graph):**
    - Red arrows: Hypernyms ("is a type of")
    - Blue arrows: Hyponyms ("type includes")
    - Green arrows: Meronyms ("has part")
    - Orange arrows: Holonyms ("part of")
    - Grey arrows: Sense connections (root word to its senses)
    
    **Graph Structure:**
    - Every word sense connects to its root word (e.g., sheep.n.01 → SHEEP)
    - Word senses connect directly to other word senses via relationships
    - Each related word also gets its own root node and sense connections
    - Clean sense-to-sense relationships with comprehensive root connections
    """)


def render_sidebar(session_manager):
    """Render the complete sidebar with all components."""
    with st.sidebar:
        st.markdown("### Settings")
        
        # Apply button at the top
        apply_clicked = st.button("🔄 Apply Settings", 
                                 help="Update the URL with current settings for sharing",
                                 use_container_width=True)
        
        st.markdown("---")
        
        # Word input
        word, parsed_sense_number, word_changed = render_word_input(session_manager)
        
        # Search history
        render_search_history()
        
        # Basic settings
        depth = render_basic_settings(session_manager)
        
        # Relationship types
        show_hypernyms, show_hyponyms, show_meronyms, show_holonyms = render_relationship_types(session_manager)
        
        # Graph appearance
        layout_type, node_size_multiplier, color_scheme = render_graph_appearance(session_manager)
        
        # Physics simulation
        enable_physics, spring_strength, central_gravity = render_physics_simulation(session_manager)
        
        # Visual options
        show_labels, edge_width = render_visual_options(session_manager)
        
        # Display options
        show_info, show_graph = render_display_options(session_manager)
        
        # Save options
        save_graph, filename = render_save_options()
        
        # About section
        render_about_section()
        
        # Collect all settings
        settings = {
            'word': word,
            'depth': depth,
            'show_hypernyms': show_hypernyms,
            'show_hyponyms': show_hyponyms,
            'show_meronyms': show_meronyms,
            'show_holonyms': show_holonyms,
            'layout_type': layout_type,
            'node_size_multiplier': node_size_multiplier,
            'color_scheme': color_scheme,
            'enable_physics': enable_physics,
            'spring_strength': spring_strength,
            'central_gravity': central_gravity,
            'show_labels': show_labels,
            'edge_width': edge_width,
            'show_info': show_info,
            'show_graph': show_graph,
            'save_graph': save_graph,
            'filename': filename,
            'parsed_sense_number': parsed_sense_number
        }
        
        # Update URL with current settings only when Apply is clicked or word changed (Enter pressed)
        should_update_url = apply_clicked or word_changed
        session_manager.update_url_with_settings(settings, force_update=should_update_url)
        
        return settings 