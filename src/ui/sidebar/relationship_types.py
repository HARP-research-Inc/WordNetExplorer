"""
Relationship type selection components for the sidebar.
"""

import streamlit as st
from config.settings import DEFAULT_SETTINGS


def get_url_default(session_manager, setting_key: str, default_value):
    """Get default value from URL parameters or fall back to default."""
    url_settings = session_manager.get_settings_from_url()
    return url_settings.get(setting_key, default_value)


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
    
    # Similarity & Opposition Relations
    st.markdown("### 🔄 Similarity & Opposition")
    
    similarity_all_key = "similarity_all_advanced"
    similarity_all = st.checkbox("Select All Similarity", key=similarity_all_key)
    
    if similarity_all and not st.session_state.get(f"{similarity_all_key}_prev", False):
        st.session_state["show_antonym_forced"] = True
        st.session_state["show_similar_to_forced"] = True
        st.session_state["show_also_see_forced"] = True
        st.session_state["show_verb_group_forced"] = True
        st.session_state["show_derivationally_related_form_forced"] = True
        st.session_state["show_pertainym_forced"] = True
    elif not similarity_all and st.session_state.get(f"{similarity_all_key}_prev", False):
        st.session_state["show_antonym_forced"] = False
        st.session_state["show_similar_to_forced"] = False
        st.session_state["show_also_see_forced"] = False
        st.session_state["show_verb_group_forced"] = False
        st.session_state["show_derivationally_related_form_forced"] = False
        st.session_state["show_pertainym_forced"] = False
    
    st.session_state[f"{similarity_all_key}_prev"] = similarity_all
    
    col1, col2 = st.columns(2)
    with col1:
        show_antonym = st.checkbox("Antonym (!)", 
            value=st.session_state.get("show_antonym_forced", basic_relationships.get('show_antonym', False)),
            help="opposite meaning")
        show_similar_to = st.checkbox("Similar-to (&)", 
            value=st.session_state.get("show_similar_to_forced", basic_relationships.get('show_similar_to', False)),
            help="similar meaning (adjectives)")
        show_also_see = st.checkbox("Also-see (^)", 
            value=st.session_state.get("show_also_see_forced", get_url_default(session_manager, 'show_also_see', False)),
            help="related concepts worth seeing")
    with col2:
        show_verb_group = st.checkbox("Verb-group ($)", 
            value=st.session_state.get("show_verb_group_forced", get_url_default(session_manager, 'show_verb_group', False)),
            help="related verbs")
        show_derivationally_related_form = st.checkbox("Derivation (+)", 
            value=st.session_state.get("show_derivationally_related_form_forced", get_url_default(session_manager, 'show_derivationally_related_form', False)),
            help="morphologically related")
        show_pertainym = st.checkbox("Pertainym (\\)", 
            value=st.session_state.get("show_pertainym_forced", get_url_default(session_manager, 'show_pertainym', False)),
            help="pertains to")
    
    st.markdown("---")
    
    # Other Relations
    st.markdown("### ⚡ Other Relations")
    
    other_all_key = "other_all_advanced"
    other_all = st.checkbox("Select All Other", key=other_all_key)
    
    if other_all and not st.session_state.get(f"{other_all_key}_prev", False):
        st.session_state["show_entailment_forced"] = True
        st.session_state["show_cause_forced"] = True
        st.session_state["show_attribute_forced"] = True
        st.session_state["show_domain_of_synset_topic_forced"] = True
        st.session_state["show_member_of_domain_topic_forced"] = True
    elif not other_all and st.session_state.get(f"{other_all_key}_prev", False):
        st.session_state["show_entailment_forced"] = False
        st.session_state["show_cause_forced"] = False
        st.session_state["show_attribute_forced"] = False
        st.session_state["show_domain_of_synset_topic_forced"] = False
        st.session_state["show_member_of_domain_topic_forced"] = False
    
    st.session_state[f"{other_all_key}_prev"] = other_all
    
    col1, col2 = st.columns(2)
    with col1:
        show_entailment = st.checkbox("Entailment (*)", 
            value=st.session_state.get("show_entailment_forced", basic_relationships.get('show_entailment', False)),
            help="logically entails")
        show_cause = st.checkbox("Cause (>)", 
            value=st.session_state.get("show_cause_forced", basic_relationships.get('show_cause', False)),
            help="causes")
        show_attribute = st.checkbox("Attribute (=)", 
            value=st.session_state.get("show_attribute_forced", basic_relationships.get('show_attribute', False)),
            help="attribute relationship")
    with col2:
        show_domain_of_synset_topic = st.checkbox("Domain-topic (-t)", 
            value=st.session_state.get("show_domain_of_synset_topic_forced", get_url_default(session_manager, 'show_domain_of_synset_topic', False)),
            help="domain of synset - TOPIC")
        show_member_of_domain_topic = st.checkbox("Member-domain-topic (+t)", 
            value=st.session_state.get("show_member_of_domain_topic_forced", get_url_default(session_manager, 'show_member_of_domain_topic', False)),
            help="member of this domain - TOPIC")
    
    # Collect all relationship settings
    relationship_settings = {
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
        'show_also_see': show_also_see,
        'show_verb_group': show_verb_group,
        'show_derivationally_related_form': show_derivationally_related_form,
        'show_pertainym': show_pertainym,
        
        'show_entailment': show_entailment,
        'show_cause': show_cause,
        'show_attribute': show_attribute,
        'show_domain_of_synset_topic': show_domain_of_synset_topic,
        'show_member_of_domain_topic': show_member_of_domain_topic,
        
        # Additional relationships not shown in UI but available
        'show_derived_from': get_url_default(session_manager, 'show_derived_from', False),
        'show_participle_of_verb': get_url_default(session_manager, 'show_participle_of_verb', False),
        'show_domain_of_synset_region': get_url_default(session_manager, 'show_domain_of_synset_region', False),
        'show_member_of_domain_region': get_url_default(session_manager, 'show_member_of_domain_region', False),
        'show_domain_of_synset_usage': get_url_default(session_manager, 'show_domain_of_synset_usage', False),
        'show_member_of_domain_usage': get_url_default(session_manager, 'show_member_of_domain_usage', False),
    }
    
    return relationship_settings 