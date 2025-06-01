"""
Token Processor Module - Handles individual token processing
"""

from dataclasses import dataclass
from typing import Optional, Set
import re
import unicodedata


@dataclass(frozen=True)
class TokenFeatures:
    """Immutable token features extracted from spaCy token."""
    index: int
    text: str
    lemma: str
    pos: str
    tag: str
    dep: str
    head: int
    is_space: bool
    is_punct: bool
    is_stop: bool
    is_alpha: bool
    shape: str
    
    def __str__(self) -> str:
        return f"{self.text}({self.pos}/{self.dep})"


# Common function words in English
FUNCTION_WORDS: Set[str] = {
    # Determiners
    'a', 'an', 'the', 'this', 'that', 'these', 'those', 'my', 'your', 'his', 
    'her', 'its', 'our', 'their', 'some', 'any', 'each', 'every', 'no',
    
    # Pronouns
    'i', 'me', 'you', 'he', 'him', 'she', 'it', 'we', 'us', 'they', 'them',
    'myself', 'yourself', 'himself', 'herself', 'itself', 'ourselves', 
    'yourselves', 'themselves', 'who', 'whom', 'whose', 'which', 'what',
    'whoever', 'whomever', 'whatever', 'whichever', 'one', 'ones',
    
    # Prepositions
    'in', 'on', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
    'from', 'up', 'down', 'out', 'off', 'over', 'under', 'of', 'as',
    
    # Conjunctions
    'and', 'or', 'but', 'nor', 'so', 'yet', 'both', 'either', 'neither',
    'because', 'since', 'unless', 'although', 'though', 'whereas', 'while',
    'if', 'whether', 'that', 'than', 'rather',
    
    # Auxiliary verbs
    'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being',
    'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
    'will', 'would', 'shall', 'should', 'may', 'might', 'must',
    'can', 'could', 'ought',
    
    # Others
    'not', 'no', 'yes', 'there', 'here', 'then', 'now'
}

# POS tags for content words
CONTENT_POS_TAGS: Set[str] = {'NOUN', 'VERB', 'ADJ', 'ADV', 'PROPN', 'NUM'}

# POS tags for function words
FUNCTION_POS_TAGS: Set[str] = {'DET', 'PRON', 'ADP', 'CCONJ', 'SCONJ', 'AUX', 'PART'}


def extract_token_features(token) -> TokenFeatures:
    """
    Extract features from a spaCy token.
    
    Args:
        token: spaCy Token object
        
    Returns:
        TokenFeatures object with extracted features
    """
    return TokenFeatures(
        index=token.i,
        text=token.text,
        lemma=token.lemma_,
        pos=token.pos_,
        tag=token.tag_,
        dep=token.dep_,
        head=token.head.i,
        is_space=token.is_space,
        is_punct=token.is_punct,
        is_stop=token.is_stop,
        is_alpha=token.is_alpha,
        shape=token.shape_
    )


def normalize_token_text(text: str) -> str:
    """
    Normalize token text for comparison.
    
    Handles:
    - Unicode normalization
    - Whitespace normalization
    - Case normalization (preserves original case info)
    
    Args:
        text: Raw token text
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    # Unicode normalization (NFC form)
    text = unicodedata.normalize('NFC', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Remove zero-width characters
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    
    return text


def get_token_lemma(token) -> str:
    """
    Get the lemma of a token with special handling.
    
    Handles:
    - Pronouns (returns lowercase form)
    - Proper nouns (preserves capitalization)
    - Special cases
    
    Args:
        token: spaCy Token object
        
    Returns:
        Lemma string
    """
    # Handle pronouns specially
    if token.pos_ == 'PRON':
        return token.text.lower()
    
    # Handle proper nouns - preserve capitalization
    if token.pos_ == 'PROPN':
        return token.text
    
    # Handle -PRON- lemma from spaCy
    if token.lemma_ == '-PRON-':
        return token.text.lower()
    
    # Default to spaCy's lemma
    return token.lemma_


def is_content_word(token) -> bool:
    """
    Check if a token is a content word (carries semantic meaning).
    
    Args:
        token: spaCy Token object or TokenFeatures
        
    Returns:
        True if content word, False otherwise
    """
    # Handle both spaCy tokens and TokenFeatures
    if hasattr(token, 'pos_'):
        pos = token.pos_
        text = token.text.lower()
    else:
        pos = token.pos
        text = token.text.lower()
    
    # Check POS tag
    if pos in CONTENT_POS_TAGS:
        # Special case: some numbers/numerals might be functional
        if pos == 'NUM' and text in {'one', 'two', 'three', 'first', 'second', 'third'}:
            # Context-dependent, but generally content words
            return True
        return True
    
    # Some verbs marked as AUX might be content words in certain contexts
    if pos == 'AUX' and text not in FUNCTION_WORDS:
        return True
    
    return False


def is_function_word(token) -> bool:
    """
    Check if a token is a function word (grammatical role).
    
    Args:
        token: spaCy Token object or TokenFeatures
        
    Returns:
        True if function word, False otherwise
    """
    # Handle both spaCy tokens and TokenFeatures
    if hasattr(token, 'pos_'):
        pos = token.pos_
        text = token.text.lower()
    else:
        pos = token.pos
        text = token.text.lower()
    
    # Check POS tag
    if pos in FUNCTION_POS_TAGS:
        return True
    
    # Check against known function words
    if text in FUNCTION_WORDS:
        return True
    
    # Punctuation is functional
    if hasattr(token, 'is_punct'):
        if token.is_punct:
            return True
    elif pos == 'PUNCT':
        return True
    
    # Spaces are functional
    if hasattr(token, 'is_space'):
        if token.is_space:
            return True
    
    return False


def get_token_shape_category(shape: str) -> str:
    """
    Categorize token shape for pattern matching.
    
    Categories:
    - 'lower': all lowercase
    - 'upper': all uppercase
    - 'title': title case
    - 'mixed': mixed case
    - 'digit': contains digits
    - 'punct': punctuation
    - 'other': everything else
    
    Args:
        shape: spaCy shape string
        
    Returns:
        Shape category
    """
    if not shape:
        return 'other'
    
    # Check for digits
    if 'd' in shape:
        return 'digit'
    
    # Check for punctuation only
    if all(c in '.,;:!?\'"()-[]{}' for c in shape):
        return 'punct'
    
    # Check case patterns
    if shape.islower() or all(c == 'x' for c in shape):
        return 'lower'
    elif shape.isupper() or all(c == 'X' for c in shape):
        return 'upper'
    elif shape[0].isupper() and shape[1:].islower():
        return 'title'
    elif any(c.isupper() for c in shape) and any(c.islower() for c in shape):
        return 'mixed'
    
    return 'other'


def is_valid_token_for_wordnet(token) -> bool:
    """
    Check if a token should be looked up in WordNet.
    
    Filters out:
    - Function words
    - Punctuation
    - Spaces
    - Numbers (unless they're word-form numbers)
    - Single characters (except 'I' and 'a')
    
    Args:
        token: spaCy Token object or TokenFeatures
        
    Returns:
        True if valid for WordNet lookup
    """
    # Must be a content word
    if not is_content_word(token):
        return False
    
    # Get text
    if hasattr(token, 'text'):
        text = token.text
    else:
        text = token.text
    
    # Filter out single characters except 'I' and 'a'
    if len(text) == 1 and text.lower() not in {'i', 'a'}:
        return False
    
    # Filter out tokens with only digits
    if text.isdigit():
        return False
    
    # Filter out tokens with special characters
    if re.match(r'^[^a-zA-Z]+$', text):
        return False
    
    return True


def get_simplified_pos(pos: str, tag: str = None) -> str:
    """
    Get simplified POS tag for WordNet lookup.
    
    Maps spaCy POS to WordNet POS:
    - NOUN, PROPN -> 'n'
    - VERB -> 'v'  
    - ADJ -> 'a'
    - ADV -> 'r'
    - Others -> None
    
    Args:
        pos: spaCy POS tag
        tag: spaCy detailed tag (optional)
        
    Returns:
        WordNet POS tag or None
    """
    pos_map = {
        'NOUN': 'n',
        'PROPN': 'n',
        'VERB': 'v',
        'ADJ': 'a',
        'ADV': 'r'
    }
    
    # Special handling for some tags
    if tag:
        # Gerunds (VBG) can be nouns or verbs depending on context
        if tag == 'VBG':
            # This is a simplification; real disambiguation needs context
            return 'v'
        
        # Past participles (VBN) can be adjectives or verbs
        if tag == 'VBN':
            # This is a simplification; real disambiguation needs context
            return 'v'
    
    return pos_map.get(pos)


def is_auxiliary_verb(token) -> bool:
    """
    Check if token is an auxiliary verb.
    
    Args:
        token: spaCy Token object or TokenFeatures
        
    Returns:
        True if auxiliary verb
    """
    # Handle both types
    if hasattr(token, 'pos_'):
        pos = token.pos_
        text = token.text.lower()
    else:
        pos = token.pos
        text = token.text.lower()
    
    if pos == 'AUX':
        return True
    
    # Check common auxiliary verbs
    aux_verbs = {
        'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being',
        'have', 'has', 'had', 'having',
        'do', 'does', 'did', 'doing',
        'will', 'would', 'shall', 'should',
        'may', 'might', 'must', 'can', 'could', 'ought'
    }
    
    return text in aux_verbs 