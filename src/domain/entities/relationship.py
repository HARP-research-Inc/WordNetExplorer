"""Relationship entity representing semantic relationships between synsets."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class RelationshipType(Enum):
    """Enumeration of WordNet relationship types."""
    
    # Taxonomic Relations (Hypernymy/Hyponymy)
    HYPERNYM = "hypernym"  # @ - More general concept (is-a)
    HYPONYM = "hyponym"  # ~ - More specific concept
    INSTANCE_HYPERNYM = "instance_hypernym"  # @i - Instance of
    INSTANCE_HYPONYM = "instance_hyponym"  # ~i - Has instances
    
    # Part-Whole Relations (Meronymy/Holonymy)
    MEMBER_MERONYM = "member_meronym"  # #m - Member of
    SUBSTANCE_MERONYM = "substance_meronym"  # #s - Substance of
    PART_MERONYM = "part_meronym"  # #p - Part of
    MEMBER_HOLONYM = "member_holonym"  # %m - Has members
    SUBSTANCE_HOLONYM = "substance_holonym"  # %s - Made of
    PART_HOLONYM = "part_holonym"  # %p - Has parts
    
    # Antonymy & Similarity
    ANTONYM = "antonym"  # ! - Opposite
    SIMILAR_TO = "similar_to"  # & - Similar meaning
    
    # Entailment & Causation
    ENTAILMENT = "entailment"  # * - Logically entails
    CAUSE = "cause"  # > - Causes
    
    # Attributes & Cross-References
    ATTRIBUTE = "attribute"  # = - Attribute relationship
    ALSO_SEE = "also_see"  # ^ - See also
    
    # Verb-Specific
    VERB_GROUP = "verb_group"  # $ - Verb group
    PARTICIPLE_OF_VERB = "participle"  # < - Participle form
    
    # Morphological/Derivational
    DERIVATIONALLY_RELATED = "derivationally_related_form"  # + - Derivationally related
    PERTAINYM = "pertainym"  # \\ - Pertains to (adjectives)
    DERIVED_FROM = "derived"  # \\ - Derived from (adverbs)
    
    # Domain Labels
    DOMAIN_TOPIC = "domain_topic"  # ;c - Topic domain
    MEMBER_TOPIC = "member_topic"  # -c - Member of topic
    DOMAIN_REGION = "domain_region"  # ;r - Regional domain
    MEMBER_REGION = "member_region"  # -r - Member of region
    DOMAIN_USAGE = "domain_usage"  # ;u - Usage domain
    MEMBER_USAGE = "member_usage"  # -u - Member of usage
    
    # Special
    SENSE = "sense"  # Connection between word and its synset
    
    @property
    def symbol(self) -> str:
        """Get the traditional WordNet symbol for this relationship."""
        symbols = {
            self.HYPERNYM: "@",
            self.HYPONYM: "~",
            self.INSTANCE_HYPERNYM: "@i",
            self.INSTANCE_HYPONYM: "~i",
            self.MEMBER_MERONYM: "#m",
            self.SUBSTANCE_MERONYM: "#s",
            self.PART_MERONYM: "#p",
            self.MEMBER_HOLONYM: "%m",
            self.SUBSTANCE_HOLONYM: "%s",
            self.PART_HOLONYM: "%p",
            self.ANTONYM: "!",
            self.SIMILAR_TO: "&",
            self.ENTAILMENT: "*",
            self.CAUSE: ">",
            self.ATTRIBUTE: "=",
            self.ALSO_SEE: "^",
            self.VERB_GROUP: "$",
            self.PARTICIPLE_OF_VERB: "<",
            self.DERIVATIONALLY_RELATED: "+",
            self.PERTAINYM: "\\",
            self.DOMAIN_TOPIC: ";c",
            self.MEMBER_TOPIC: "-c",
            self.DOMAIN_REGION: ";r",
            self.MEMBER_REGION: "-r",
            self.DOMAIN_USAGE: ";u",
            self.MEMBER_USAGE: "-u",
        }
        return symbols.get(self, "")
    
    @property
    def is_taxonomic(self) -> bool:
        """Check if this is a taxonomic relationship."""
        return self in {
            self.HYPERNYM, self.HYPONYM,
            self.INSTANCE_HYPERNYM, self.INSTANCE_HYPONYM
        }
    
    @property
    def is_partitive(self) -> bool:
        """Check if this is a part-whole relationship."""
        return self in {
            self.MEMBER_MERONYM, self.SUBSTANCE_MERONYM, self.PART_MERONYM,
            self.MEMBER_HOLONYM, self.SUBSTANCE_HOLONYM, self.PART_HOLONYM
        }
    
    @property
    def is_similarity(self) -> bool:
        """Check if this is a similarity/opposition relationship."""
        return self in {self.ANTONYM, self.SIMILAR_TO}
    
    @property
    def is_domain(self) -> bool:
        """Check if this is a domain relationship."""
        return self in {
            self.DOMAIN_TOPIC, self.MEMBER_TOPIC,
            self.DOMAIN_REGION, self.MEMBER_REGION,
            self.DOMAIN_USAGE, self.MEMBER_USAGE
        }
    
    def get_inverse(self) -> Optional['RelationshipType']:
        """Get the inverse relationship type if it exists."""
        inverses = {
            self.HYPERNYM: self.HYPONYM,
            self.HYPONYM: self.HYPERNYM,
            self.INSTANCE_HYPERNYM: self.INSTANCE_HYPONYM,
            self.INSTANCE_HYPONYM: self.INSTANCE_HYPERNYM,
            self.MEMBER_MERONYM: self.MEMBER_HOLONYM,
            self.MEMBER_HOLONYM: self.MEMBER_MERONYM,
            self.SUBSTANCE_MERONYM: self.SUBSTANCE_HOLONYM,
            self.SUBSTANCE_HOLONYM: self.SUBSTANCE_MERONYM,
            self.PART_MERONYM: self.PART_HOLONYM,
            self.PART_HOLONYM: self.PART_MERONYM,
            self.DOMAIN_TOPIC: self.MEMBER_TOPIC,
            self.MEMBER_TOPIC: self.DOMAIN_TOPIC,
            self.DOMAIN_REGION: self.MEMBER_REGION,
            self.MEMBER_REGION: self.DOMAIN_REGION,
            self.DOMAIN_USAGE: self.MEMBER_USAGE,
            self.MEMBER_USAGE: self.DOMAIN_USAGE,
        }
        return inverses.get(self)


@dataclass(frozen=True)
class Relationship:
    """
    Immutable Relationship entity representing a semantic relationship.
    
    This represents a directed edge in the WordNet graph.
    """
    source_synset_name: str
    target_synset_name: str
    type: RelationshipType
    
    def __post_init__(self):
        """Validate relationship."""
        if not self.source_synset_name:
            raise ValueError("Source synset name cannot be empty")
        
        if not self.target_synset_name:
            raise ValueError("Target synset name cannot be empty")
        
        if not isinstance(self.type, RelationshipType):
            raise TypeError(f"Relationship type must be RelationshipType, got {type(self.type)}")
        
        if self.source_synset_name == self.target_synset_name:
            raise ValueError("Self-referential relationships are not allowed")
    
    @property
    def is_symmetric(self) -> bool:
        """Check if this relationship is symmetric."""
        return self.type in {RelationshipType.SIMILAR_TO, RelationshipType.ANTONYM}
    
    def get_inverse(self) -> Optional['Relationship']:
        """Get the inverse relationship if it exists."""
        inverse_type = self.type.get_inverse()
        if inverse_type:
            return Relationship(
                source_synset_name=self.target_synset_name,
                target_synset_name=self.source_synset_name,
                type=inverse_type
            )
        return None
    
    def __str__(self) -> str:
        """String representation of the relationship."""
        return f"{self.source_synset_name} -{self.type.symbol}-> {self.target_synset_name}"
    
    def __repr__(self) -> str:
        """Detailed representation of the relationship."""
        return (f"Relationship(source='{self.source_synset_name}', "
                f"target='{self.target_synset_name}', "
                f"type={self.type.name})") 