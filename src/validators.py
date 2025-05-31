"""
Validation functions for WordNet Explorer.
"""

import re
from src.constants import MAX_DEPTH, MAX_NODES, MAX_BRANCHES, MAX_FREQUENCY


def validate_word(word):
    """
    Validate a word input.
    
    Args:
        word (str): The word to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not word:
        return False, "Word cannot be empty"
    
    if not isinstance(word, str):
        return False, "Word must be a string"
    
    # Remove extra whitespace
    word = word.strip()
    
    # Check length
    if len(word) > 100:
        return False, "Word is too long (max 100 characters)"
    
    # Check for invalid characters (allow letters, numbers, hyphens, underscores, spaces)
    if not re.match(r'^[a-zA-Z0-9\-_ ]+$', word):
        return False, "Word contains invalid characters"
    
    return True, None


def validate_synset_name(synset_name):
    """
    Validate a synset name (e.g., 'dog.n.01').
    
    Args:
        synset_name (str): The synset name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not synset_name:
        return False, "Synset name cannot be empty"
    
    if not isinstance(synset_name, str):
        return False, "Synset name must be a string"
    
    # Check format: word.pos.sense_number
    pattern = r'^[a-zA-Z_]+\.[nvasr]\.\d{2}$'
    if not re.match(pattern, synset_name):
        return False, "Invalid synset format (expected: word.pos.nn)"
    
    return True, None


def validate_depth(depth):
    """
    Validate exploration depth.
    
    Args:
        depth (int): The depth value
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        depth = int(depth)
    except (ValueError, TypeError):
        return False, "Depth must be a number"
    
    if depth < 1:
        return False, "Depth must be at least 1"
    
    if depth > MAX_DEPTH:
        return False, f"Depth cannot exceed {MAX_DEPTH}"
    
    return True, None


def validate_sense_number(sense_number, max_senses=None):
    """
    Validate a sense number.
    
    Args:
        sense_number (int): The sense number
        max_senses (int, optional): Maximum number of senses available
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if sense_number is None:
        return True, None  # Optional parameter
    
    try:
        sense_number = int(sense_number)
    except (ValueError, TypeError):
        return False, "Sense number must be a number"
    
    if sense_number < 1:
        return False, "Sense number must be at least 1"
    
    if max_senses and sense_number > max_senses:
        return False, f"Sense number exceeds available senses (max: {max_senses})"
    
    return True, None


def validate_graph_settings(settings):
    """
    Validate graph visualization settings.
    
    Args:
        settings (dict): Settings dictionary
        
    Returns:
        tuple: (is_valid, errors) where errors is a list of error messages
    """
    errors = []
    
    # Validate numeric settings
    numeric_validations = [
        ('max_nodes', 1, MAX_NODES, "Maximum nodes"),
        ('max_branches', 1, MAX_BRANCHES, "Maximum branches"),
        ('min_frequency', 0, MAX_FREQUENCY, "Minimum frequency"),
        ('node_size_multiplier', 0.1, 5.0, "Node size multiplier"),
        ('edge_width', 1, 10, "Edge width"),
        ('spring_strength', 0.001, 1.0, "Spring strength"),
        ('central_gravity', 0.0, 1.0, "Central gravity")
    ]
    
    for key, min_val, max_val, name in numeric_validations:
        if key in settings:
            try:
                value = float(settings[key])
                if value < min_val or value > max_val:
                    errors.append(f"{name} must be between {min_val} and {max_val}")
            except (ValueError, TypeError):
                errors.append(f"{name} must be a number")
    
    # Validate boolean settings
    boolean_keys = [
        'enable_physics', 'show_labels', 'enable_clustering',
        'enable_cross_connections', 'simplified_mode', 'show_graph', 'show_info'
    ]
    
    for key in boolean_keys:
        if key in settings and not isinstance(settings[key], bool):
            errors.append(f"{key} must be true or false")
    
    # Validate POS filter
    if 'pos_filter' in settings:
        valid_pos = ["Nouns", "Verbs", "Adjectives", "Adverbs"]
        if not isinstance(settings['pos_filter'], list):
            errors.append("POS filter must be a list")
        else:
            for pos in settings['pos_filter']:
                if pos not in valid_pos:
                    errors.append(f"Invalid POS filter: {pos}")
    
    return len(errors) == 0, errors


def validate_filename(filename):
    """
    Validate a filename for saving.
    
    Args:
        filename (str): The filename to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not filename:
        return False, "Filename cannot be empty"
    
    # Remove extension for validation
    name_part = filename.rsplit('.', 1)[0]
    
    # Check for invalid characters
    invalid_chars = '<>:"|?*'
    if any(char in name_part for char in invalid_chars):
        return False, f"Filename contains invalid characters: {invalid_chars}"
    
    # Check length
    if len(name_part) > 200:
        return False, "Filename is too long (max 200 characters)"
    
    return True, None


def sanitize_word(word):
    """
    Sanitize a word input for safe processing.
    
    Args:
        word (str): The word to sanitize
        
    Returns:
        str: Sanitized word
    """
    if not word:
        return ""
    
    # Convert to string if not already
    word = str(word)
    
    # Strip whitespace
    word = word.strip()
    
    # Convert to lowercase
    word = word.lower()
    
    # Replace multiple spaces with single space
    word = re.sub(r'\s+', ' ', word)
    
    # Remove any remaining invalid characters
    word = re.sub(r'[^a-zA-Z0-9\-_ ]', '', word)
    
    return word


def sanitize_filename(filename):
    """
    Sanitize a filename for saving.
    
    Args:
        filename (str): The filename to sanitize
        
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return "output"
    
    # Get name and extension
    parts = filename.rsplit('.', 1)
    name = parts[0]
    ext = parts[1] if len(parts) > 1 else ""
    
    # Remove invalid characters
    invalid_chars = '<>:"|?*\\/\n\r\t'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # Remove multiple underscores
    name = re.sub(r'_+', '_', name)
    
    # Trim to reasonable length
    name = name[:200]
    
    # Reconstruct filename
    if ext:
        return f"{name}.{ext}"
    return name 