#!/usr/bin/env python3
"""
Debug all relationships to see what's actually being generated
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import WordNetExplorer

def debug_all_relationships():
    """Debug all relationships to see what's actually being generated."""
    
    print("🔍 Debugging All Relationships Generated")
    print("=" * 60)
    
    # Create explorer
    explorer = WordNetExplorer()
    
    # Test a word that should have hierarchical relationships
    word = 'femtosecond'
    
    print(f"📋 Testing '{word}' with deeper search:")
    print("-" * 40)
    
    G, node_labels = explorer.explore_word(word, depth=3, max_nodes=200)
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Group edges by relationship type
    relationships_found = {}
    
    for source, target, edge_data in G.edges(data=True):
        relation = edge_data.get('relation', 'unknown')
        arrow_direction = edge_data.get('arrow_direction', 'to')
        
        if relation not in relationships_found:
            relationships_found[relation] = []
            
        # Extract clean names
        source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
        target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
        
        # Determine visual arrow direction
        if arrow_direction == 'from':
            visual_source, visual_target = target_name, source_name
        else:
            visual_source, visual_target = source_name, target_name
        
        relationships_found[relation].append({
            'original': f"{source_name} → {target_name}",
            'visual': f"{visual_source} → {visual_target}",
            'arrow_direction': arrow_direction,
            'source_node': source,
            'target_node': target
        })
    
    # Display relationships by type
    print(f"\n📊 Relationships found:")
    
    for relation_type, edges in relationships_found.items():
        print(f"\n🔗 {relation_type.upper()} ({len(edges)} edges):")
        
        for edge in edges:
            print(f"  • {edge['visual']} (arrow_dir: {edge['arrow_direction']})")
            if relation_type in ['hypernym', 'hyponym']:
                # For taxonomic relations, check consistency
                if 'time_unit' in edge['visual']:
                    print(f"    ⭐ TIME UNIT RELATIONSHIP: {edge['visual']}")
    
    # Also test with a different word to find more relationships
    print(f"\n" + "=" * 60)
    word2 = 'second'
    print(f"📋 Testing '{word2}' for comparison:")
    print("-" * 40)
    
    G2, node_labels2 = explorer.explore_word(word2, depth=3, max_nodes=200)
    
    print(f"Graph has {G2.number_of_nodes()} nodes and {G2.number_of_edges()} edges")
    
    # Look specifically for taxonomic relationships
    taxonomic_found = False
    for source, target, edge_data in G2.edges(data=True):
        relation = edge_data.get('relation', 'unknown')
        arrow_direction = edge_data.get('arrow_direction', 'to')
        
        if relation in ['hypernym', 'hyponym']:
            taxonomic_found = True
            source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
            target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
            
            if arrow_direction == 'from':
                visual_source, visual_target = target_name, source_name
            else:
                visual_source, visual_target = source_name, target_name
            
            print(f"  🎯 {relation.upper()}: {visual_source} → {visual_target}")
            print(f"     Original: {source_name} → {target_name}")
            print(f"     Arrow direction: {arrow_direction}")
    
    if not taxonomic_found:
        print("  No taxonomic relationships found for 'second'")

if __name__ == "__main__":
    debug_all_relationships() 