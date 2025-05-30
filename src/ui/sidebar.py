"""
Sidebar components for WordNet Explorer.
"""

import streamlit as st
from config.settings import DEFAULT_SETTINGS, LAYOUT_OPTIONS

from utils.session_state import add_to_search_history, clear_search_history
from utils.debug_logger import log_word_input_event, log_session_state
from wordnet_explorer import get_synsets_for_word


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
    
    # Get word and search mode from URL if available
    url_word = get_url_default(session_manager, 'word', None)
    synset_search_mode = get_url_default(session_manager, 'synset_search_mode', False)
    
    # Input label and help (will be updated after we have word and sense info)
    input_label = "Enter a word to explore"
    input_help = "Press Enter to add the word to your search history"
    input_placeholder = "e.g., dog"
    
    # Word input field - prioritize selected word, then URL word, then empty
    input_value = selected_word or url_word or ""
    log_word_input_event("INPUT_VALUE_CALCULATION", input_value=input_value, selected_word=selected_word, current_word=st.session_state.get('current_word', 'None'))
    
    word = st.text_input(
        input_label, 
        value=input_value,
        key="word_input",
        help=input_help,
        placeholder=input_placeholder
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

    # Show available senses if word is provided
    if word:
        synsets = get_synsets_for_word(word)
        if synsets:
            if synset_search_mode and parsed_sense_number:
                synset_name = synsets[parsed_sense_number - 1].name()
                st.success(f"🎯 Synset Mode: Will explore synset `{synset_name}` (sense {parsed_sense_number} of '{word}')")
            else:
                st.info(f"💡 '{word}' has {len(synsets)} sense(s) available (1-{len(synsets)})")
        else:
            st.warning(f"⚠️ No WordNet entries found for '{word}'")
    
    # Search mode toggle - only enabled when both word and sense number are provided
    can_enable_synset_mode = bool(parsed_sense_number and word)
    
    if not can_enable_synset_mode:
        synset_search_mode = False  # Force disable if no sense specified
    
    synset_search_mode = st.checkbox(
        "🔍 Synset Search Mode", 
        value=synset_search_mode if can_enable_synset_mode else False,
        disabled=not can_enable_synset_mode,
        help="Focus on the synset containing the specified word sense. Only available when both word and sense number are provided." if can_enable_synset_mode else "Enter both a word and sense number to enable synset search mode."
    )
    
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
    
    return word, parsed_sense_number, word_changed, synset_search_mode


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


def render_relationship_types(session_manager):
    """Render general relationship type checkboxes at top level."""
    
    st.markdown("### 🔗 Relationship Types")
    st.markdown("**Select which types of semantic relationships to display:**")
    
    # General relationship categories (vertical list)
    # Taxonomic Relations
    taxonomic_all = st.checkbox(
        "🏛️ Taxonomic Relations", 
        value=get_url_default(session_manager, 'show_hypernym', False) or get_url_default(session_manager, 'show_hyponym', False),
        help="'is-a' relationships - hierarchical connections between general and specific concepts"
    )
    
    # Part-Whole Relations  
    parthole_all = st.checkbox(
        "🧩 Part-Whole Relations", 
        value=get_url_default(session_manager, 'show_member_meronym', False) or get_url_default(session_manager, 'show_part_meronym', False),
        help="Meronymy/Holonymy - relationships between wholes and their parts"
    )

    # Similarity & Opposition
    similarity_all = st.checkbox(
        "🔄 Similarity & Opposition", 
        value=get_url_default(session_manager, 'show_antonym', False) or get_url_default(session_manager, 'show_similar_to', False),
        help="Antonyms, synonyms, and similarity relationships"
    )
    
    # Other Relations
    other_all = st.checkbox(
        "⚡ Other Relations", 
        value=get_url_default(session_manager, 'show_entailment', False) or get_url_default(session_manager, 'show_cause', False),
        help="Entailment, causation, attributes, and domain relationships"
    )
    
    # Set basic relationship flags based on general selections
    show_hypernym = taxonomic_all
    show_hyponym = taxonomic_all
    show_member_meronym = parthole_all
    show_part_meronym = parthole_all
    show_member_holonym = parthole_all
    show_part_holonym = parthole_all
    show_antonym = similarity_all
    show_similar_to = similarity_all
    show_entailment = other_all
    show_cause = other_all
    show_attribute = other_all
    show_also_see = other_all
    
    # Return basic settings for backward compatibility
    basic_relationships = {
        # Legacy compatibility
        'show_hypernyms': show_hypernym,
        'show_hyponyms': show_hyponym,
        'show_meronyms': show_member_meronym or show_part_meronym,
        'show_holonyms': show_member_holonym or show_part_holonym,
        
        # Basic new settings
        'show_hypernym': show_hypernym,
        'show_hyponym': show_hyponym,
        'show_member_meronym': show_member_meronym,
        'show_part_meronym': show_part_meronym,
        'show_member_holonym': show_member_holonym,
        'show_part_holonym': show_part_holonym,
        'show_antonym': show_antonym,
        'show_similar_to': show_similar_to,
        'show_entailment': show_entailment,
        'show_cause': show_cause,
        'show_attribute': show_attribute,
        'show_also_see': show_also_see,
        
        # Set remaining specific types to False by default (can be overridden in advanced)
        'show_instance_hypernym': False,
        'show_instance_hyponym': False,
        'show_substance_holonym': False,
        'show_substance_meronym': False,
        'show_verb_group': False,
        'show_participle_of_verb': False,
        'show_derivationally_related_form': False,
        'show_pertainym': False,
        'show_derived_from': False,
        'show_domain_of_synset_topic': False,
        'show_member_of_domain_topic': False,
        'show_domain_of_synset_region': False,
        'show_member_of_domain_region': False,
        'show_domain_of_synset_usage': False,
        'show_member_of_domain_usage': False,
    }
    
    return basic_relationships


def render_basic_settings(session_manager):
    """Render basic exploration settings."""
    depth = st.slider(
        "Exploration depth", 
        min_value=1, 
        max_value=3, 
        value=get_url_default(session_manager, 'depth', DEFAULT_SETTINGS['depth']), 
        help="How deep to explore relationships (higher values create larger graphs)"
    )
    
    # Advanced Options
    with st.expander("⚙️ Advanced Options", expanded=False):
        st.markdown("**Advanced Graph Parameters**")
        
        # Advanced depth setting (allows higher values)
        advanced_depth = st.slider(
            "Advanced Exploration Depth", 
            min_value=1, 
            max_value=10, 
            value=get_url_default(session_manager, 'advanced_depth', depth), 
            help="Higher depth values for complex exploration (warning: values above 3 may create very large graphs)"
        )
        
        # Use advanced depth if it's different from basic depth
        if advanced_depth != depth:
            depth = advanced_depth
            if advanced_depth > 3:
                st.warning(f"⚠️ Depth {advanced_depth} may create very large graphs. Consider using relationship filters to limit complexity.")
        
        # Maximum nodes limit
        max_nodes = st.number_input(
            "Maximum Nodes", 
            min_value=10, 
            max_value=1000, 
            value=get_url_default(session_manager, 'max_nodes', 100),
            step=10,
            help="Limit the total number of nodes in the graph to prevent performance issues"
        )
        
        # Branch limiting
        max_branches = st.slider(
            "Max Branches per Node",
            min_value=1,
            max_value=20,
            value=get_url_default(session_manager, 'max_branches', 5),
            help="Maximum number of related concepts to show for each node"
        )
        
        # Node filtering options
        st.markdown("**Node Filtering**")
        
        # Minimum frequency threshold
        min_frequency = st.slider(
            "Minimum Word Frequency",
            min_value=0,
            max_value=100,
            value=get_url_default(session_manager, 'min_frequency', 0),
            help="Filter out rare words (0 = no filtering). Higher values show only common words."
        )
        
        # Show only certain POS types
        pos_filter = st.multiselect(
            "Part-of-Speech Filter",
            options=["Nouns", "Verbs", "Adjectives", "Adverbs"],
            default=get_url_default(session_manager, 'pos_filter', ["Nouns", "Verbs", "Adjectives", "Adverbs"]),
            help="Show only specific parts of speech"
        )
        
        # Performance settings
        st.markdown("**Performance Settings**")
        
        # Enable/disable heavy computations
        enable_clustering = st.checkbox(
            "Enable Node Clustering",
            value=get_url_default(session_manager, 'enable_clustering', False),
            help="Group related nodes together (may slow down large graphs)"
        )
        
        # Cross-connections option
        enable_cross_connections = st.checkbox(
            "Enable Cross-Connections",
            value=get_url_default(session_manager, 'enable_cross_connections', True),
            help="Find and display relationships between existing nodes (creates richer graphs but may be slower)"
        )
        
        # Simplified mode for large graphs
        simplified_mode = st.checkbox(
            "Simplified Mode",
            value=get_url_default(session_manager, 'simplified_mode', False),
            help="Use simplified rendering for better performance with large graphs"
        )
        
        # Add detailed relationship types in advanced options
        st.markdown("---")
        st.markdown("**Detailed Relationship Types**")
        st.markdown("Fine-tune specific WordNet edge types (overrides basic relationship selections above):")
        
        # Get basic relationship settings from main section
        basic_relationships = st.session_state.get('basic_relationships', {})
        
        # Render advanced relationship controls
        advanced_relationship_settings = render_advanced_relationship_types(session_manager, basic_relationships)
        
        # Return all advanced settings as a dictionary
        advanced_settings = {
            'max_nodes': max_nodes,
            'max_branches': max_branches,
            'min_frequency': min_frequency,
            'pos_filter': pos_filter,
            'enable_clustering': enable_clustering,
            'enable_cross_connections': enable_cross_connections,
            'simplified_mode': simplified_mode
        }
        
        # Include advanced relationship settings
        advanced_settings.update(advanced_relationship_settings)
        
    return depth, advanced_settings


def render_advanced_relationship_types(session_manager, basic_relationships):
    """Render detailed relationship type controls in advanced options."""
    
    st.markdown("**Detailed Edge Types**")
    st.markdown("Fine-tune which specific WordNet relationships to include:")
    
    # Taxonomic Relations
    st.markdown("### 🏛️ Taxonomic ('is-a') Relations")
    
    # Handle "Select All Taxonomic" logic with session state
    taxonomic_all_key = "taxonomic_all_advanced"
    taxonomic_all = st.checkbox("Select All Taxonomic", key=taxonomic_all_key)
    
    # Force child checkboxes when master is toggled
    if taxonomic_all and not st.session_state.get(f"{taxonomic_all_key}_prev", False):
        # Master was just checked - set all children to True
        st.session_state["show_hypernym_forced"] = True
        st.session_state["show_hyponym_forced"] = True
        st.session_state["show_instance_hypernym_forced"] = True
        st.session_state["show_instance_hyponym_forced"] = True
    elif not taxonomic_all and st.session_state.get(f"{taxonomic_all_key}_prev", False):
        # Master was just unchecked - set all children to False
        st.session_state["show_hypernym_forced"] = False
        st.session_state["show_hyponym_forced"] = False
        st.session_state["show_instance_hypernym_forced"] = False
        st.session_state["show_instance_hyponym_forced"] = False
    
    st.session_state[f"{taxonomic_all_key}_prev"] = taxonomic_all
    
    col1, col2 = st.columns(2)
    with col1:
        show_hypernym = st.checkbox("Hypernym (@)", 
            value=st.session_state.get("show_hypernym_forced", basic_relationships.get('show_hypernym', False)),
            help="'is a type of' - more general concept")
        show_instance_hypernym = st.checkbox("Instance-Hypernym (@i)", 
            value=st.session_state.get("show_instance_hypernym_forced", get_url_default(session_manager, 'show_instance_hypernym', False)),
            help="specific instance of a concept")
    with col2:
        show_hyponym = st.checkbox("Hyponym (~)", 
            value=st.session_state.get("show_hyponym_forced", basic_relationships.get('show_hyponym', False)),
            help="'type includes' - more specific concept")
        show_instance_hyponym = st.checkbox("Instance-Hyponym (~i)", 
            value=st.session_state.get("show_instance_hyponym_forced", get_url_default(session_manager, 'show_instance_hyponym', False)),
            help="has instances")
    
    st.markdown("---")
    
    # Part-Whole Relations
    st.markdown("### 🧩 Part–Whole (Meronymy/Holonymy)")
    
    parthole_all_key = "parthole_all_advanced"
    parthole_all = st.checkbox("Select All Part-Whole", key=parthole_all_key)
    
    # Force child checkboxes when master is toggled
    if parthole_all and not st.session_state.get(f"{parthole_all_key}_prev", False):
        st.session_state["show_member_holonym_forced"] = True
        st.session_state["show_substance_holonym_forced"] = True
        st.session_state["show_part_holonym_forced"] = True
        st.session_state["show_member_meronym_forced"] = True
        st.session_state["show_substance_meronym_forced"] = True
        st.session_state["show_part_meronym_forced"] = True
    elif not parthole_all and st.session_state.get(f"{parthole_all_key}_prev", False):
        st.session_state["show_member_holonym_forced"] = False
        st.session_state["show_substance_holonym_forced"] = False
        st.session_state["show_part_holonym_forced"] = False
        st.session_state["show_member_meronym_forced"] = False
        st.session_state["show_substance_meronym_forced"] = False
        st.session_state["show_part_meronym_forced"] = False
    
    st.session_state[f"{parthole_all_key}_prev"] = parthole_all
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Holonyms (contains):**")
        show_member_holonym = st.checkbox("Member-Holonym (%m)", 
            value=st.session_state.get("show_member_holonym_forced", basic_relationships.get('show_member_holonym', False)),
            help="has members")
        show_substance_holonym = st.checkbox("Substance-Holonym (%s)", 
            value=st.session_state.get("show_substance_holonym_forced", get_url_default(session_manager, 'show_substance_holonym', False)),
            help="made of substance")
        show_part_holonym = st.checkbox("Part-Holonym (%p)", 
            value=st.session_state.get("show_part_holonym_forced", basic_relationships.get('show_part_holonym', False)),
            help="has parts")
    with col2:
        st.markdown("**Meronyms (part of):**")
        show_member_meronym = st.checkbox("Member-Meronym (#m)", 
            value=st.session_state.get("show_member_meronym_forced", basic_relationships.get('show_member_meronym', False)),
            help="member of")
        show_substance_meronym = st.checkbox("Substance-Meronym (#s)", 
            value=st.session_state.get("show_substance_meronym_forced", get_url_default(session_manager, 'show_substance_meronym', False)),
            help="substance of")
        show_part_meronym = st.checkbox("Part-Meronym (#p)", 
            value=st.session_state.get("show_part_meronym_forced", basic_relationships.get('show_part_meronym', False)),
            help="part of")
    
    st.markdown("---")
    
    # Antonymy & Similarity
    st.markdown("### 🔄 Antonymy & Similarity")
    antisim_all = st.checkbox("Select All Antonymy & Similarity", key="antisim_all_advanced")
    
    show_antonym = st.checkbox("Antonym (!)", 
        value=antisim_all or basic_relationships.get('show_antonym', False),
        help="opposite meaning")
    show_similar_to = st.checkbox("Similar-To (&)", 
        value=antisim_all or basic_relationships.get('show_similar_to', False),
        help="similar meaning")
    
    st.markdown("---")
    
    # Entailment & Causation
    st.markdown("### ⚡ Entailment & Causation")
    entail_all = st.checkbox("Select All Entailment & Causation", key="entail_all_advanced")
    
    show_entailment = st.checkbox("Entailment (*)", 
        value=entail_all or basic_relationships.get('show_entailment', False),
        help="logically entails")
    show_cause = st.checkbox("Cause (>)", 
        value=entail_all or basic_relationships.get('show_cause', False),
        help="causes")
    
    st.markdown("---")
    
    # Attributes & Cross-References
    st.markdown("### 🔗 Attributes & Cross-References")
    attr_all = st.checkbox("Select All Attributes & Cross-References", key="attr_all_advanced")
    
    show_attribute = st.checkbox("Attribute (=)", 
        value=attr_all or basic_relationships.get('show_attribute', False),
        help="attribute relationship")
    show_also_see = st.checkbox("Also-See (^)", 
        value=attr_all or basic_relationships.get('show_also_see', False),
        help="see also")
    
    st.markdown("---")
    
    # Verb-Specific Links
    st.markdown("### 🎯 Verb-Specific Links")
    verb_all = st.checkbox("Select All Verb-Specific", key="verb_all_advanced")
    
    show_verb_group = st.checkbox("Verb-Group ($)", 
        value=verb_all or get_url_default(session_manager, 'show_verb_group', False),
        help="verb group")
    show_participle_of_verb = st.checkbox("Participle-Of-Verb (<)", 
        value=verb_all or get_url_default(session_manager, 'show_participle_of_verb', False),
        help="participle form")
    
    st.markdown("---")
    
    # Morphological / Derivational
    st.markdown("### 📝 Morphological / Derivational")
    morph_all = st.checkbox("Select All Morphological", key="morph_all_advanced")
    
    show_derivationally_related_form = st.checkbox("Derivationally-Related-Form (+)", 
        value=morph_all or get_url_default(session_manager, 'show_derivationally_related_form', False),
        help="derivationally related")
    show_pertainym = st.checkbox("Pertainym (\\)", 
        value=morph_all or get_url_default(session_manager, 'show_pertainym', False),
        help="pertains to")
    show_derived_from = st.checkbox("Derived-From (\\)", 
        value=morph_all or get_url_default(session_manager, 'show_derived_from', False),
        help="derived from (adverbs)")
    
    st.markdown("---")
    
    # Domain Labels
    st.markdown("### 🏷️ Domain Labels")
    domain_all = st.checkbox("Select All Domain Labels", key="domain_all_advanced")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Domain of Synset:**")
        show_domain_of_synset_topic = st.checkbox("Topic (;c)", 
            value=domain_all or get_url_default(session_manager, 'show_domain_of_synset_topic', False),
            help="topic domain")
        show_domain_of_synset_region = st.checkbox("Region (;r)", 
            value=domain_all or get_url_default(session_manager, 'show_domain_of_synset_region', False),
            help="regional domain")
        show_domain_of_synset_usage = st.checkbox("Usage (;u)", 
            value=domain_all or get_url_default(session_manager, 'show_domain_of_synset_usage', False),
            help="usage domain")
    with col2:
        st.markdown("**Member of Domain:**")
        show_member_of_domain_topic = st.checkbox("Topic (–c)", 
            value=domain_all or get_url_default(session_manager, 'show_member_of_domain_topic', False),
            help="member of topic")
        show_member_of_domain_region = st.checkbox("Region (–r)", 
            value=domain_all or get_url_default(session_manager, 'show_member_of_domain_region', False),
            help="member of region")
        show_member_of_domain_usage = st.checkbox("Usage (–u)", 
            value=domain_all or get_url_default(session_manager, 'show_member_of_domain_usage', False),
            help="member of usage")
    
    # Return all the advanced relationship settings, overriding basic ones
    return {
        # Legacy compatibility
        'show_hypernyms': show_hypernym,
        'show_hyponyms': show_hyponym,
        'show_meronyms': show_member_meronym or show_substance_meronym or show_part_meronym,
        'show_holonyms': show_member_holonym or show_substance_holonym or show_part_holonym,
        
        # New comprehensive settings (override basic ones)
        'show_hypernym': show_hypernym,
        'show_hyponym': show_hyponym,
        'show_instance_hypernym': show_instance_hypernym,
        'show_instance_hyponym': show_instance_hyponym,
        'show_member_holonym': show_member_holonym,
        'show_substance_holonym': show_substance_holonym,
        'show_part_holonym': show_part_holonym,
        'show_member_meronym': show_member_meronym,
        'show_substance_meronym': show_substance_meronym,
        'show_part_meronym': show_part_meronym,
        'show_antonym': show_antonym,
        'show_similar_to': show_similar_to,
        'show_entailment': show_entailment,
        'show_cause': show_cause,
        'show_attribute': show_attribute,
        'show_also_see': show_also_see,
        'show_verb_group': show_verb_group,
        'show_participle_of_verb': show_participle_of_verb,
        'show_derivationally_related_form': show_derivationally_related_form,
        'show_pertainym': show_pertainym,
        'show_derived_from': show_derived_from,
        'show_domain_of_synset_topic': show_domain_of_synset_topic,
        'show_member_of_domain_topic': show_member_of_domain_topic,
        'show_domain_of_synset_region': show_domain_of_synset_region,
        'show_member_of_domain_region': show_member_of_domain_region,
        'show_domain_of_synset_usage': show_domain_of_synset_usage,
        'show_member_of_domain_usage': show_member_of_domain_usage,
    }


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
        # HTML export button
        st.markdown("#### HTML Export")
        st.markdown("*Filename will be auto-generated as: `wne-<word>-<sense>-<datetime>.html`*")
        if st.button("📥 Download HTML", help="Download the graph as an interactive HTML file", use_container_width=True):
            st.session_state.download_html_requested = True
            from utils.debug_logger import log_word_input_event
            log_word_input_event("DOWNLOAD_HTML_BUTTON_CLICKED", html_flag_set=True)
        
        # JSON export button
        st.markdown("---")
        st.markdown("#### JSON Export")
        st.markdown("*Filename will be auto-generated as: `wne-<word>-<sense>-<datetime>.json`*")
        if st.button("📥 Download JSON", help="Download the graph data as a JSON file", use_container_width=True):
            st.session_state.download_json_requested = True
            from utils.debug_logger import log_word_input_event
            log_word_input_event("DOWNLOAD_JSON_BUTTON_CLICKED", json_flag_set=True)
        
        # JSON import
        st.markdown("---")
        st.markdown("#### Import Graph")
        uploaded_file = st.file_uploader("Import JSON graph", type=['json'])
        if uploaded_file is not None:
            try:
                import json
                from src.graph import GraphSerializer
                serializer = GraphSerializer()
                json_str = uploaded_file.getvalue().decode('utf-8')
                G, node_labels, metadata = serializer.deserialize_graph(json_str)
                st.session_state.imported_graph = (G, node_labels, metadata)
                st.success("✅ Graph imported successfully!")
            except Exception as e:
                st.error(f"❌ Error importing graph: {str(e)}")
    
    # Get download request states from session state
    download_html_requested = st.session_state.get('download_html_requested', False)
    download_json_requested = st.session_state.get('download_json_requested', False)
    
    # Terminal logging for session state
    if download_html_requested or download_json_requested:
        from utils.debug_logger import log_word_input_event
        log_word_input_event("DOWNLOAD_SESSION_STATE_CHECK", 
                            html_requested=download_html_requested, 
                            json_requested=download_json_requested)
    
    return download_html_requested, download_json_requested, uploaded_file is not None


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
    - Enable "Synset Search Mode" to focus on the synset containing that specific sense
    
    **Relationship Types:**
    - **🏛️ Taxonomic Relations**: "is-a" relationships (hypernyms/hyponyms)
    - **🧩 Part-Whole Relations**: Meronymy/Holonymy relationships
    - **🔄 Similarity & Opposition**: Antonyms and similar concepts
    - **⚡ Other Relations**: Entailment, causation, attributes, and domain relationships
    
    **Advanced Options:**
    - **Advanced Depth**: Explore up to 10 levels deep (warning: large graphs above depth 3)
    - **Max Nodes**: Limit graph size to prevent performance issues (10-1000 nodes)
    - **Max Branches**: Control how many related concepts to show per node (1-20)
    - **Min Frequency**: Filter out rare words (0 = include all)
    - **POS Filter**: Choose which parts of speech to include
    - **Cross-Connections**: When enabled, finds relationships between all nodes in the graph (creates richer, more interconnected graphs but may be slower)
    - **Clustering**: Group related nodes together visually
    - **Simplified Mode**: Use simpler rendering for better performance with large graphs
    - **Detailed Edge Types**: Fine-tune specific WordNet relationships (hypernyms, meronyms, etc.)
    
    **Navigation:**
    - Double-click any node to explore that concept
    - Use search history to revisit previous words
    - All searched and navigated words appear in history
    
    **Node Types:**
    - 🔴 Root words - uppercase word forms (e.g., SHEEP, BOVINE)
    - 🔶 Word senses - specific meanings of words (diamond-shaped)
    - 🟪 Synsets - semantic groups of synonymous words (square-shaped)
    
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
        
        # If apply was clicked, ensure the word input reflects the current word
        if apply_clicked and session_manager.get_current_word():
            st.session_state.word_input = session_manager.get_current_word()
            # Also update sense number if it exists in URL
            url_settings = session_manager.get_settings_from_url()
            if 'sense_number' in url_settings:
                st.session_state.sense_number_input = str(url_settings['sense_number'])
        
        st.markdown("---")
        
        # Word input
        word, parsed_sense_number, word_changed, synset_search_mode = render_word_input(session_manager)
        
        # Search history
        render_search_history()
        
        # Relationship types (basic level)
        relationship_settings = render_relationship_types(session_manager)
        
        # Store basic relationships in session state for advanced options
        st.session_state['basic_relationships'] = relationship_settings
        
        # Basic settings (includes advanced options)
        depth, advanced_settings = render_basic_settings(session_manager)
        
        # Advanced relationship types are handled within advanced_settings now
        # No need for separate render call
        
        # Graph appearance
        layout_type, node_size_multiplier, color_scheme = render_graph_appearance(session_manager)
        
        # Physics simulation
        enable_physics, spring_strength, central_gravity = render_physics_simulation(session_manager)
        
        # Visual options
        show_labels, edge_width = render_visual_options(session_manager)
        
        # Display options
        show_info, show_graph = render_display_options(session_manager)
        
        # Save options
        download_html_requested, download_json_requested, uploaded_file = render_save_options()
        
        # About section
        render_about_section()
        
        # Collect all settings
        settings = {
            'word': word,
            'depth': depth,
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
            'download_html_requested': download_html_requested,
            'download_json_requested': download_json_requested,
            'uploaded_file': uploaded_file,
            'parsed_sense_number': parsed_sense_number,
            'synset_search_mode': synset_search_mode
        }
        
        # Add all relationship settings
        settings.update(relationship_settings)
        settings.update(advanced_settings)
        
        # Update URL with current settings only when Apply is clicked or word changed (Enter pressed)
        should_update_url = apply_clicked or word_changed
        session_manager.update_url_with_settings(settings, force_update=should_update_url)
        
        return settings 