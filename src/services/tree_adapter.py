"""
Adapter to make the v4 sentence analyzer compatible with existing code.

This converts between the new TreeNode structure and the expected
SyntacticNode structure.
"""

from typing import Dict, Optional
from src.services.syntactic_tree import SyntacticNode
from src.services.sentence_analyzer_v4 import TreeNode, TreeBuilder, ParsedSentence


class TreeAdapter:
    """Converts between TreeNode and SyntacticNode structures."""
    
    @staticmethod
    def convert_to_syntactic_tree(parsed: ParsedSentence) -> SyntacticNode:
        """Convert a ParsedSentence to a SyntacticNode tree."""
        tree = parsed.tree
        root_id = parsed.root_id
        
        # Build a map of converted nodes to avoid duplicates
        converted_nodes: Dict[str, SyntacticNode] = {}
        
        def convert_node(node_id: str) -> SyntacticNode:
            """Recursively convert a TreeNode to SyntacticNode."""
            if node_id in converted_nodes:
                return converted_nodes[node_id]
            
            tree_node = tree.get_node(node_id)
            if not tree_node:
                return None
            
            # Create SyntacticNode
            syn_node = SyntacticNode(
                node_id=tree_node.node_id,
                node_type=tree_node.node_type,
                text=tree_node.text,
                edge_label=tree_node.edge_label,
                token_info=tree_node.token_info
            )
            
            converted_nodes[node_id] = syn_node
            
            # Convert and add children
            for child_id in tree_node.child_ids:
                child_syn_node = convert_node(child_id)
                if child_syn_node:
                    # Properly set up parent-child relationship
                    child_syn_node.parent = syn_node
                    syn_node.children.append(child_syn_node)
            
            return syn_node
        
        # Convert from root
        root_node = convert_node(root_id)
        
        # Ensure root has no parent
        if root_node:
            root_node.parent = None
            root_node.edge_label = None
        
        return root_node


class SentenceAnalyzerAdapter:
    """Adapter for the v4 SentenceAnalyzer to match v3 interface."""
    
    def __init__(self):
        from src.services.sentence_analyzer_v4 import SentenceAnalyzer as V4Analyzer
        self.analyzer = V4Analyzer()
    
    def analyze_sentence(self, sentence: str, decompose_lemmas: bool = False):
        """Analyze sentence and return result matching v3 interface."""
        # Get v4 result
        parsed = self.analyzer.analyze_sentence(sentence, decompose_lemmas)
        
        # Convert to expected format
        syntactic_tree = TreeAdapter.convert_to_syntactic_tree(parsed)
        
        # Create result object matching expected interface
        class AnalysisResult:
            def __init__(self, tree, tokens):
                self.syntactic_tree = tree
                self.tokens = tokens
        
        return AnalysisResult(syntactic_tree, parsed.tokens) 