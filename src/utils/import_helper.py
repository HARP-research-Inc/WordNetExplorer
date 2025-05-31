"""
Import path helper for WordNet Explorer.
"""

import sys
import os


def setup_import_paths():
    """
    Set up import paths to allow imports from src directory.
    This function ensures the parent directory is in the Python path.
    """
    # Get the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get the src directory (parent of utils)
    src_dir = os.path.dirname(current_dir)
    
    # Get the project root (parent of src)
    project_root = os.path.dirname(src_dir)
    
    # Add both to path if not already there
    for path in [project_root, src_dir]:
        if path not in sys.path:
            sys.path.insert(0, path)


def get_project_root() -> str:
    """
    Get the project root directory.
    
    Returns:
        Absolute path to the project root
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    return os.path.dirname(src_dir)


def get_src_dir() -> str:
    """
    Get the src directory.
    
    Returns:
        Absolute path to the src directory
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(current_dir)


def resolve_relative_path(relative_path: str) -> str:
    """
    Resolve a relative path from the project root.
    
    Args:
        relative_path: Path relative to project root
        
    Returns:
        Absolute path
    """
    project_root = get_project_root()
    return os.path.join(project_root, relative_path) 