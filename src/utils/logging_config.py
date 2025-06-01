"""
Logging configuration for the sentence analyzer.
"""

import logging
import sys


def configure_logging(level=logging.INFO, verbose=False):
    """Configure logging for the application.
    
    Args:
        level: The logging level (default: INFO)
        verbose: If True, enables DEBUG level and detailed formatting
    """
    if verbose:
        level = logging.DEBUG
    
    # Create formatter with more detail for verbose mode
    if verbose:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    sentence_logger = logging.getLogger('src.services.sentence_analyzer_v2')
    sentence_logger.setLevel(level)
    
    return root_logger


def log_tree_structure(node, indent=0, logger=None):
    """Log the tree structure in a readable format.
    
    Args:
        node: The syntactic node to log
        indent: Current indentation level
        logger: Logger to use (default: module logger)
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    prefix = "  " * indent
    edge_label = f"[{node.edge_label}]" if node.edge_label else "[root]"
    node_info = f"{prefix}{edge_label} {node.text} (type: {node.node_type})"
    
    logger.debug(node_info)
    
    for child in node.children:
        log_tree_structure(child, indent + 1, logger) 