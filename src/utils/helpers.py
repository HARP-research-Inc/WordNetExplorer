"""
Helper utility functions for WordNet Explorer.
"""

import sys
import tempfile
from pathlib import Path


def capture_function_output(func, *args, **kwargs):
    """
    Capture the stdout output of a function call and return it as a string.
    
    Args:
        func: The function to call
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
    
    Returns:
        str: The captured output
    """
    with tempfile.TemporaryFile(mode='w+') as temp:
        # Redirect stdout to our temporary file
        original_stdout = sys.stdout
        sys.stdout = temp
        
        try:
            # Call the function
            func(*args, **kwargs)
        finally:
            # Reset stdout
            sys.stdout = original_stdout
        
        # Get the output
        temp.seek(0)
        return temp.read()


def ensure_downloads_directory():
    """Ensure the downloads directory exists and return its path."""
    downloads_dir = Path("downloads")
    downloads_dir.mkdir(exist_ok=True)
    return downloads_dir


def validate_filename(filename, default_extension=".html"):
    """
    Validate and clean up a filename, ensuring it has the correct extension.
    
    Args:
        filename (str): The input filename
        default_extension (str): The default extension to add if missing
    
    Returns:
        str: The validated filename
    """
    if not filename:
        return f"wordnet_graph{default_extension}"
    
    if not filename.endswith(default_extension):
        filename += default_extension
    
    return filename 