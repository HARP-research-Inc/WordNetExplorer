"""
Word input components for the sidebar.
"""

import streamlit as st
from utils.session_state import (
    add_to_search_history, 
    clear_search_history, 
    add_query_to_history,
    get_search_history_manager,
    restore_query_settings
)
from utils.debug_logger import log_word_input_event, log_session_state
from wordnet import get_synsets_for_word
from src.models.search_history import SearchQuery


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
    selected_query = st.session_state.get('selected_history_query', None)
    log_word_input_event("SELECTED_WORD_CHECK", selected_word=selected_word)
    
    # Get word and search mode from URL if available
    url_word = get_url_default(session_manager, 'word', None)
    synset_search_mode = get_url_default(session_manager, 'synset_search_mode', False)
    
    # If a query was selected from history, use its settings
    if selected_query:
        url_word = selected_query.word
        synset_search_mode = selected_query.synset_search_mode
    
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
    
    # Get sense number from URL or selected query
    if selected_query and selected_query.sense_number:
        sense_input_value = str(selected_query.sense_number)
    else:
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
    if selected_word or selected_query:
        log_word_input_event("PROCESSING_SELECTED_WORD", selected_word=selected_word)
        # Clear the selected history word/query
        st.session_state.selected_history_word = None
        st.session_state.selected_history_query = None
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
        return selected_word, parsed_sense_number, True, synset_search_mode  # Word changed when selected from history
    
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
    """Render the enhanced search history with query details."""
    history_manager = get_search_history_manager()
    
    # Debug logging
    log_word_input_event("SEARCH_HISTORY_RENDER_START", 
                        history_length=len(history_manager.queries),
                        manager_id=id(history_manager),
                        has_queries=bool(history_manager.queries))
    
    # Also log the first few queries for debugging
    if history_manager.queries:
        for i, query in enumerate(history_manager.queries[:3]):
            log_word_input_event(f"HISTORY_QUERY_{i}", 
                               word=query.word, 
                               hash=query.get_hash(),
                               label=query.get_display_label())
    
    if history_manager.queries:
        with st.expander("🔍 Search & Navigation History", expanded=False):
            st.markdown("Click any query to explore it again, or select multiple to compare:")
            
            # Show info about hash codes at the top
            st.info("**Hash codes** (e.g., #12345678) uniquely identify each query configuration including all parameters")
            
            # Show compare button if any items are selected
            selected_hashes = st.session_state.get('selected_queries_for_comparison', set())
            if selected_hashes:
                st.success(f"**{len(selected_hashes)} queries selected for comparison**")
                if st.button("📊 Compare Selected Graphs", key="compare_selected", type="primary"):
                    st.session_state.compare_mode = True
                    st.rerun()
                st.markdown("---")
            
            # Create container for history items
            # Group queries by word
            unique_words = history_manager.get_unique_words()
            
            for word in unique_words:
                word_queries = history_manager.get_queries_for_word(word)
                
                # If only one query for this word, show it directly
                if len(word_queries) == 1:
                    query = word_queries[0]
                    query_hash = query.get_hash()
                    
                    # Create a container for the checkbox and button
                    container = st.container()
                    with container:
                        # Checkbox for selection
                        is_selected = query_hash in selected_hashes
                        label = f"☐ {query.get_display_label()}" if not is_selected else f"☑ {query.get_display_label()}"
                        
                        if st.checkbox(
                            label,
                            key=f"select_{query_hash}", 
                            value=is_selected,
                            help=f"Select for comparison | {query.get_tooltip()}"
                        ):
                            selected_hashes.add(query_hash)
                        else:
                            selected_hashes.discard(query_hash)
                        st.session_state.selected_queries_for_comparison = selected_hashes
                        
                        # Button to load this specific query
                        if st.button(
                            f"📝 Load '{query.word}'", 
                            key=f"load_{query_hash}",
                            help=f"Load this query | {query.get_tooltip()}"
                        ):
                            log_word_input_event("QUERY_BUTTON_CLICKED", word=query.word, hash=query_hash)
                            st.session_state.selected_history_word = query.word
                            st.session_state.selected_history_query = query
                            log_word_input_event("SET_SELECTED_HISTORY_QUERY", word=query.word)
                            st.rerun()
                else:
                    # Multiple queries for this word - show them grouped
                    st.markdown(f"**📚 {word}** ({len(word_queries)} variations):")
                    for query in word_queries:
                        query_hash = query.get_hash()
                        
                        # Checkbox for selection with indent
                        is_selected = query_hash in selected_hashes
                        label = f"　☐ {query.get_display_label()}" if not is_selected else f"　☑ {query.get_display_label()}"
                        
                        if st.checkbox(
                            label,
                            key=f"select_{query_hash}", 
                            value=is_selected,
                            help=f"Select for comparison | {query.get_tooltip()}"
                        ):
                            selected_hashes.add(query_hash)
                        else:
                            selected_hashes.discard(query_hash)
                        st.session_state.selected_queries_for_comparison = selected_hashes
                        
                        # Button to load this specific query
                        if st.button(
                            f"　📝 Load", 
                            key=f"load_{query_hash}",
                            help=f"Load this query | {query.get_tooltip()}"
                        ):
                            log_word_input_event("QUERY_BUTTON_CLICKED", word=query.word, hash=query_hash)
                            st.session_state.selected_history_word = query.word
                            st.session_state.selected_history_query = query
                            log_word_input_event("SET_SELECTED_HISTORY_QUERY", word=query.word)
                            st.rerun()
            
            # Clear buttons at the bottom
            st.markdown("---")
            if st.button("🗑️ Clear History", help="Clear search history", key="clear_search_history"):
                log_word_input_event("CLEAR_HISTORY_CLICKED")
                clear_search_history()
                st.session_state.selected_queries_for_comparison = set()
                st.rerun()
                
            if selected_hashes and st.button("❌ Clear Selection", help="Clear selected items", key="clear_selection"):
                st.session_state.selected_queries_for_comparison = set()
                st.rerun()
            
            # Add legend below
            st.markdown("---")
            st.markdown("**📖 Legend:**")
            st.markdown("""
            - ☐/☑ = Checkbox to select for comparison
            - **word** = Basic word query
            - **word.XX** = Specific sense (e.g., dog.01 = first sense)
            - **[S]** = Synset search mode enabled
            - **#XXXXXXXX** = Unique 8-character hash of all parameters
            
            The hash includes: word, sense, depth, relationships, and all other settings.
            """)
    else:
        log_word_input_event("NO_SEARCH_HISTORY_TO_RENDER") 