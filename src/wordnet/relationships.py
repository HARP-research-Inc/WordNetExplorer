"""
WordNet Relationships Module

Handles extraction and management of comprehensive semantic relationships between synsets.
"""

from enum import Enum
from typing import List, Dict, Any, Tuple


class RelationshipType(Enum):
    """Enumeration of comprehensive WordNet relationship types."""
    # Basic sense connection
    SENSE = "sense"
    
    # Taxonomic Relations
    HYPERNYM = "hypernym"
    HYPONYM = "hyponym"
    INSTANCE_HYPERNYM = "instance_hypernym"
    INSTANCE_HYPONYM = "instance_hyponym"
    
    # Part-Whole Relations (Meronymy/Holonymy)
    MEMBER_HOLONYM = "member_holonym"
    SUBSTANCE_HOLONYM = "substance_holonym"
    PART_HOLONYM = "part_holonym"
    MEMBER_MERONYM = "member_meronym"
    SUBSTANCE_MERONYM = "substance_meronym"
    PART_MERONYM = "part_meronym"
    
    # Antonymy & Similarity
    ANTONYM = "antonym"
    SIMILAR_TO = "similar_to"
    
    # Entailment & Causation
    ENTAILMENT = "entailment"
    CAUSE = "cause"
    
    # Attributes & Cross-References
    ATTRIBUTE = "attribute"
    ALSO_SEE = "also_see"
    
    # Verb-Specific Links
    VERB_GROUP = "verb_group"
    PARTICIPLE_OF_VERB = "participle_of_verb"
    
    # Morphological / Derivational
    DERIVATIONALLY_RELATED_FORM = "derivationally_related_form"
    PERTAINYM = "pertainym"
    DERIVED_FROM = "derived_from"
    
    # Domain Labels
    DOMAIN_OF_SYNSET_TOPIC = "domain_of_synset_topic"
    MEMBER_OF_DOMAIN_TOPIC = "member_of_domain_topic"
    DOMAIN_OF_SYNSET_REGION = "domain_of_synset_region"
    MEMBER_OF_DOMAIN_REGION = "member_of_domain_region"
    DOMAIN_OF_SYNSET_USAGE = "domain_of_synset_usage"
    MEMBER_OF_DOMAIN_USAGE = "member_of_domain_usage"


class RelationshipConfig:
    """Configuration for comprehensive relationship extraction."""
    
    def __init__(self, **kwargs):
        # Legacy compatibility
        self.include_hypernyms = kwargs.get('show_hypernyms', False)
        self.include_hyponyms = kwargs.get('show_hyponyms', False)
        self.include_meronyms = kwargs.get('show_meronyms', False)
        self.include_holonyms = kwargs.get('show_holonyms', False)
        
        # Taxonomic Relations
        self.show_hypernym = kwargs.get('show_hypernym', False)
        self.show_hyponym = kwargs.get('show_hyponym', False)
        self.show_instance_hypernym = kwargs.get('show_instance_hypernym', False)
        self.show_instance_hyponym = kwargs.get('show_instance_hyponym', False)
        
        # Part-Whole Relations
        self.show_member_holonym = kwargs.get('show_member_holonym', False)
        self.show_substance_holonym = kwargs.get('show_substance_holonym', False)
        self.show_part_holonym = kwargs.get('show_part_holonym', False)
        self.show_member_meronym = kwargs.get('show_member_meronym', False)
        self.show_substance_meronym = kwargs.get('show_substance_meronym', False)
        self.show_part_meronym = kwargs.get('show_part_meronym', False)
        
        # Antonymy & Similarity
        self.show_antonym = kwargs.get('show_antonym', False)
        self.show_similar_to = kwargs.get('show_similar_to', False)
        
        # Entailment & Causation
        self.show_entailment = kwargs.get('show_entailment', False)
        self.show_cause = kwargs.get('show_cause', False)
        
        # Attributes & Cross-References
        self.show_attribute = kwargs.get('show_attribute', False)
        self.show_also_see = kwargs.get('show_also_see', False)
        
        # Verb-Specific Links
        self.show_verb_group = kwargs.get('show_verb_group', False)
        self.show_participle_of_verb = kwargs.get('show_participle_of_verb', False)
        
        # Morphological / Derivational
        self.show_derivationally_related_form = kwargs.get('show_derivationally_related_form', False)
        self.show_pertainym = kwargs.get('show_pertainym', False)
        self.show_derived_from = kwargs.get('show_derived_from', False)
        
        # Domain Labels
        self.show_domain_of_synset_topic = kwargs.get('show_domain_of_synset_topic', False)
        self.show_member_of_domain_topic = kwargs.get('show_member_of_domain_topic', False)
        self.show_domain_of_synset_region = kwargs.get('show_domain_of_synset_region', False)
        self.show_member_of_domain_region = kwargs.get('show_member_of_domain_region', False)
        self.show_domain_of_synset_usage = kwargs.get('show_domain_of_synset_usage', False)
        self.show_member_of_domain_usage = kwargs.get('show_member_of_domain_usage', False)


def get_relationships(synset, config: RelationshipConfig) -> Dict[RelationshipType, List]:
    """Extract all configured relationships for a synset."""
    relationships = {}
    
    # Taxonomic Relations
    if config.show_hypernym or config.include_hypernyms:
        hypernyms = synset.hypernyms()
        if hypernyms:
            relationships[RelationshipType.HYPERNYM] = hypernyms
    
    if config.show_hyponym or config.include_hyponyms:
        hyponyms = synset.hyponyms()
        if hyponyms:
            relationships[RelationshipType.HYPONYM] = hyponyms
    
    if config.show_instance_hypernym:
        relationships[RelationshipType.INSTANCE_HYPERNYM] = synset.instance_hypernyms()
    
    if config.show_instance_hyponym:
        relationships[RelationshipType.INSTANCE_HYPONYM] = synset.instance_hyponyms()
    
    # Part-Whole Relations
    if config.show_member_holonym or config.include_holonyms:
        relationships[RelationshipType.MEMBER_HOLONYM] = synset.member_holonyms()
    
    if config.show_substance_holonym or config.include_holonyms:
        relationships[RelationshipType.SUBSTANCE_HOLONYM] = synset.substance_holonyms()
    
    if config.show_part_holonym or config.include_holonyms:
        relationships[RelationshipType.PART_HOLONYM] = synset.part_holonyms()
    
    if config.show_member_meronym or config.include_meronyms:
        relationships[RelationshipType.MEMBER_MERONYM] = synset.member_meronyms()
    
    if config.show_substance_meronym or config.include_meronyms:
        relationships[RelationshipType.SUBSTANCE_MERONYM] = synset.substance_meronyms()
    
    if config.show_part_meronym or config.include_meronyms:
        relationships[RelationshipType.PART_MERONYM] = synset.part_meronyms()
    
    # Antonymy & Similarity (these work on lemmas, need special handling)
    if config.show_antonym:
        antonym_synsets = []
        for lemma in synset.lemmas():
            for antonym_lemma in lemma.antonyms():
                antonym_synsets.append(antonym_lemma.synset())
        if antonym_synsets:
            relationships[RelationshipType.ANTONYM] = antonym_synsets
    
    if config.show_similar_to:
        similar_synsets = []
        for lemma in synset.lemmas():
            for similar_lemma in lemma.similar_tos():
                similar_synsets.append(similar_lemma.synset())
        if similar_synsets:
            relationships[RelationshipType.SIMILAR_TO] = similar_synsets
    
    # Entailment & Causation
    if config.show_entailment:
        relationships[RelationshipType.ENTAILMENT] = synset.entailments()
    
    if config.show_cause:
        relationships[RelationshipType.CAUSE] = synset.causes()
    
    # Attributes & Cross-References
    if config.show_attribute:
        relationships[RelationshipType.ATTRIBUTE] = synset.attributes()
    
    if config.show_also_see:
        relationships[RelationshipType.ALSO_SEE] = synset.also_sees()
    
    # Verb-Specific Links
    if config.show_verb_group:
        relationships[RelationshipType.VERB_GROUP] = synset.verb_groups()
    
    if config.show_participle_of_verb:
        # Participle relationships work on lemmas
        participle_synsets = []
        for lemma in synset.lemmas():
            # Check if this lemma has participle relationships
            try:
                for participle_lemma in lemma.participle_of_verb():
                    participle_synsets.append(participle_lemma.synset())
            except AttributeError:
                # Some NLTK versions might not have this method
                pass
        if participle_synsets:
            relationships[RelationshipType.PARTICIPLE_OF_VERB] = participle_synsets
    
    # Morphological / Derivational (these work on lemmas, need special handling)
    if config.show_derivationally_related_form:
        derived_synsets = []
        for lemma in synset.lemmas():
            for derived_lemma in lemma.derivationally_related_forms():
                derived_synsets.append(derived_lemma.synset())
        if derived_synsets:
            relationships[RelationshipType.DERIVATIONALLY_RELATED_FORM] = derived_synsets
    
    if config.show_pertainym:
        pertainym_synsets = []
        for lemma in synset.lemmas():
            for pertainym_lemma in lemma.pertainyms():
                pertainym_synsets.append(pertainym_lemma.synset())
        if pertainym_synsets:
            relationships[RelationshipType.PERTAINYM] = pertainym_synsets
    
    if config.show_derived_from:
        # Derived-from relationships (mainly for adverbs derived from adjectives)
        derived_from_synsets = []
        for lemma in synset.lemmas():
            try:
                for derived_lemma in lemma.derived_from_adjective():
                    derived_from_synsets.append(derived_lemma.synset())
            except AttributeError:
                # Some NLTK versions might not have this method, try alternative
                try:
                    for derived_lemma in lemma.also_sees():
                        derived_from_synsets.append(derived_lemma.synset())
                except AttributeError:
                    pass
        if derived_from_synsets:
            relationships[RelationshipType.DERIVED_FROM] = derived_from_synsets
    
    # Domain Labels
    if config.show_domain_of_synset_topic:
        relationships[RelationshipType.DOMAIN_OF_SYNSET_TOPIC] = synset.topic_domains()
    
    if config.show_member_of_domain_topic:
        relationships[RelationshipType.MEMBER_OF_DOMAIN_TOPIC] = synset.in_topic_domains()
    
    if config.show_domain_of_synset_region:
        relationships[RelationshipType.DOMAIN_OF_SYNSET_REGION] = synset.region_domains()
    
    if config.show_member_of_domain_region:
        relationships[RelationshipType.MEMBER_OF_DOMAIN_REGION] = synset.in_region_domains()
    
    if config.show_domain_of_synset_usage:
        relationships[RelationshipType.DOMAIN_OF_SYNSET_USAGE] = synset.usage_domains()
    
    if config.show_member_of_domain_usage:
        relationships[RelationshipType.MEMBER_OF_DOMAIN_USAGE] = synset.in_usage_domains()
    
    return relationships


def get_relationship_color(relationship_type: RelationshipType) -> str:
    """Get the color code for a relationship type.
    
    Color scheme organized by relationship families:
    - Taxonomic: Red family (hypernyms/hyponyms)
    - Part-Whole: Green family (meronyms/holonyms) 
    - Opposition: Purple family (antonyms/similarity)
    - Causation: Orange family (entailment/causation)
    - Cross-Reference: Blue family (attributes/also_see)
    - Verb Relations: Dark Green family
    - Morphological: Pink family
    - Domain: Grey family
    """
    color_map = {
        # Basic connection - neutral grey
        RelationshipType.SENSE: '#666666',  # Medium grey
        
        # TAXONOMIC RELATIONS - Red family (warm, hierarchical feeling)
        RelationshipType.HYPERNYM: '#DC143C',          # Crimson (primary taxonomic)
        RelationshipType.HYPONYM: '#B22222',           # Fire brick (slightly darker red)
        RelationshipType.INSTANCE_HYPERNYM: '#FF6347', # Tomato (lighter, more orange-red)
        RelationshipType.INSTANCE_HYPONYM: '#CD5C5C',  # Indian red (muted red)
        
        # PART-WHOLE RELATIONS - Green family (natural, structural feeling)
        # Holonyms (whole → part) - darker greens
        RelationshipType.MEMBER_HOLONYM: '#228B22',     # Forest green (member holonym)
        RelationshipType.SUBSTANCE_HOLONYM: '#32CD32',  # Lime green (substance holonym)  
        RelationshipType.PART_HOLONYM: '#006400',       # Dark green (part holonym)
        # Meronyms (part → whole) - lighter greens
        RelationshipType.MEMBER_MERONYM: '#90EE90',     # Light green (member meronym)
        RelationshipType.SUBSTANCE_MERONYM: '#98FB98',  # Pale green (substance meronym)
        RelationshipType.PART_MERONYM: '#00FF7F',       # Spring green (part meronym)
        
        # OPPOSITION & SIMILARITY - Purple family (contrasting, complementary feeling)
        RelationshipType.ANTONYM: '#8A2BE2',     # Blue violet (strong opposition)
        RelationshipType.SIMILAR_TO: '#DA70D6', # Orchid (similar but distinct)
        
        # CAUSATION & ENTAILMENT - Orange family (dynamic, action-oriented)
        RelationshipType.ENTAILMENT: '#FF8C00', # Dark orange (logical entailment)
        RelationshipType.CAUSE: '#FF4500',      # Orange red (direct causation)
        
        # CROSS-REFERENCE & ATTRIBUTES - Blue family (informational, linking)
        RelationshipType.ATTRIBUTE: '#4169E1',  # Royal blue (attributes)
        RelationshipType.ALSO_SEE: '#6495ED',   # Cornflower blue (see also)
        
        # VERB-SPECIFIC RELATIONS - Dark Green family (action-oriented)
        RelationshipType.VERB_GROUP: '#2F4F4F',         # Dark slate grey (verb groups)
        RelationshipType.PARTICIPLE_OF_VERB: '#708090', # Slate grey (participles)
        
        # MORPHOLOGICAL & DERIVATIONAL - Pink family (linguistic transformation)
        RelationshipType.DERIVATIONALLY_RELATED_FORM: '#FF1493', # Deep pink (derivational)
        RelationshipType.PERTAINYM: '#FF69B4',                  # Hot pink (pertainyms)
        RelationshipType.DERIVED_FROM: '#FFB6C1',               # Light pink (derived from)
        
        # DOMAIN LABELS - Grey family (categorical, organizational)
        # Topic domains - blue-greys
        RelationshipType.DOMAIN_OF_SYNSET_TOPIC: '#708090',     # Slate grey
        RelationshipType.MEMBER_OF_DOMAIN_TOPIC: '#778899',     # Light slate grey
        # Region domains - neutral greys  
        RelationshipType.DOMAIN_OF_SYNSET_REGION: '#696969',    # Dim grey
        RelationshipType.MEMBER_OF_DOMAIN_REGION: '#808080',    # Grey
        # Usage domains - lighter greys
        RelationshipType.DOMAIN_OF_SYNSET_USAGE: '#A9A9A9',     # Dark grey
        RelationshipType.MEMBER_OF_DOMAIN_USAGE: '#C0C0C0',     # Silver
    }
    return color_map.get(relationship_type, '#000000')


def get_relationship_properties(relationship_type: RelationshipType) -> Dict[str, Any]:
    """Get display properties for a relationship type."""
    # Define arrow directions for different relationship types
    arrow_direction_map = {
        # Basic - no specific direction
        RelationshipType.SENSE: 'to',
        
        # Taxonomic Relations - hypernyms point up (to more general), hyponyms point down (to more specific)
        RelationshipType.HYPERNYM: 'to',  # points from specific to general
        RelationshipType.HYPONYM: 'from',  # points from general to specific (reverse direction)
        RelationshipType.INSTANCE_HYPERNYM: 'to',
        RelationshipType.INSTANCE_HYPONYM: 'from',
        
        # Part-Whole Relations - meronyms point up (to whole), holonyms point down (to parts)
        RelationshipType.MEMBER_HOLONYM: 'from',  # points from part to whole (reverse direction)
        RelationshipType.SUBSTANCE_HOLONYM: 'from',
        RelationshipType.PART_HOLONYM: 'from',
        RelationshipType.MEMBER_MERONYM: 'to',  # points from whole to part
        RelationshipType.SUBSTANCE_MERONYM: 'to',
        RelationshipType.PART_MERONYM: 'to',
        
        # Default direction for all others
        RelationshipType.ANTONYM: 'to',
        RelationshipType.SIMILAR_TO: 'to',
        RelationshipType.ENTAILMENT: 'to',
        RelationshipType.CAUSE: 'to',
        RelationshipType.ATTRIBUTE: 'to',
        RelationshipType.ALSO_SEE: 'to',
        RelationshipType.VERB_GROUP: 'to',
        RelationshipType.PARTICIPLE_OF_VERB: 'to',
        RelationshipType.DERIVATIONALLY_RELATED_FORM: 'to',
        RelationshipType.PERTAINYM: 'to',
        RelationshipType.DERIVED_FROM: 'to',
        RelationshipType.DOMAIN_OF_SYNSET_TOPIC: 'to',
        RelationshipType.MEMBER_OF_DOMAIN_TOPIC: 'to',
        RelationshipType.DOMAIN_OF_SYNSET_REGION: 'to',
        RelationshipType.MEMBER_OF_DOMAIN_REGION: 'to',
        RelationshipType.DOMAIN_OF_SYNSET_USAGE: 'to',
        RelationshipType.MEMBER_OF_DOMAIN_USAGE: 'to',
    }
    
    return {
        'color': get_relationship_color(relationship_type),
        'arrow_direction': arrow_direction_map.get(relationship_type, 'to'),
        'relation': relationship_type.value
    }


def get_relationship_description(relationship_type: RelationshipType) -> str:
    """Get human-readable description for a relationship type."""
    descriptions = {
        RelationshipType.SENSE: "Word sense connection",
        
        # Taxonomic Relations
        RelationshipType.HYPERNYM: "Is a type of (more general)",
        RelationshipType.HYPONYM: "Type includes (more specific)",
        RelationshipType.INSTANCE_HYPERNYM: "Is an instance of",
        RelationshipType.INSTANCE_HYPONYM: "Has instance",
        
        # Part-Whole Relations
        RelationshipType.MEMBER_HOLONYM: "Has members",
        RelationshipType.SUBSTANCE_HOLONYM: "Made of substance",
        RelationshipType.PART_HOLONYM: "Has parts",
        RelationshipType.MEMBER_MERONYM: "Member of",
        RelationshipType.SUBSTANCE_MERONYM: "Substance of",
        RelationshipType.PART_MERONYM: "Part of",
        
        # Antonymy & Similarity
        RelationshipType.ANTONYM: "Opposite meaning",
        RelationshipType.SIMILAR_TO: "Similar meaning",
        
        # Entailment & Causation
        RelationshipType.ENTAILMENT: "Logically entails",
        RelationshipType.CAUSE: "Causes",
        
        # Attributes & Cross-References
        RelationshipType.ATTRIBUTE: "Attribute relationship",
        RelationshipType.ALSO_SEE: "See also",
        
        # Verb-Specific Links
        RelationshipType.VERB_GROUP: "Verb group",
        RelationshipType.PARTICIPLE_OF_VERB: "Participle form",
        
        # Morphological / Derivational
        RelationshipType.DERIVATIONALLY_RELATED_FORM: "Derivationally related",
        RelationshipType.PERTAINYM: "Pertains to",
        RelationshipType.DERIVED_FROM: "Derived from",
        
        # Domain Labels
        RelationshipType.DOMAIN_OF_SYNSET_TOPIC: "Topic domain",
        RelationshipType.MEMBER_OF_DOMAIN_TOPIC: "Member of topic",
        RelationshipType.DOMAIN_OF_SYNSET_REGION: "Regional domain",
        RelationshipType.MEMBER_OF_DOMAIN_REGION: "Member of region",
        RelationshipType.DOMAIN_OF_SYNSET_USAGE: "Usage domain",
        RelationshipType.MEMBER_OF_DOMAIN_USAGE: "Member of usage",
    }
    return descriptions.get(relationship_type, relationship_type.value) 