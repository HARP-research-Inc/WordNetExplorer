"""
Core Module

This module contains the main application logic and high-level interfaces.
"""

from .explorer import WordNetExplorer
from .session import SessionManager

__all__ = [
    'WordNetExplorer',
    'SessionManager'
] 