#!/usr/bin/env python3
"""
Debug with all relationships enabled
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import WordNetExplorer

def debug_with_all_relationships():
    """Debug with all relationships enabled to find the hierarchy."""
    
    print("🔍 Debugging With All Relationships Enabled")
    print("=" * 60)
    
    # Create explorer
    explorer = WordNetExplorer()
    
    # Test femtosecond with ALL relationships enabled
    word = 'femtosecond'
    
    print(f"📋 Testing '{word}' with ALL relationships enabled:")
    print("-" * 50)
    
    # Enable all relationship types explicitly
    G, node_labels = explorer.explore_word(
        word, 
        depth=3, 
        max_nodes=200,
        show_hypernyms=True,
        show_hyponyms=True,
        show_meronyms=True,
        show_holonyms=True,
        show_similar=True,
        show_antonyms=True,
        show_also=True,
        show_entailments=True,
        show_causes=True
    )
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Look for ALL edge types
    relationship_types = set()
    hierarchical_edges = []
    
    for source, target, edge_data in G.edges(data=True):
        relation = edge_data.get('relation', 'unknown')
        arrow_direction = edge_data.get('arrow_direction', 'to')
        relationship_types.add(relation)
        
        # Extract clean names
        source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
        target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
        
        # Determine visual arrow direction
        if arrow_direction == 'from':
            visual_source, visual_target = target_name, source_name
        else:
            visual_source, visual_target = source_name, target_name
        
        print(f"  {relation.upper()}: {source_name} → {target_name} (visual: {visual_source} → {visual_target}, arrow_dir: {arrow_direction})")
        
        # Collect hierarchical relationships
        if relation in ['hypernym', 'hyponym']:
            hierarchical_edges.append({
                'relation': relation,
                'original': f"{source_name} → {target_name}",
                'visual': f"{visual_source} → {visual_target}",
                'arrow_direction': arrow_direction
            })
    
    print(f"\n📊 Relationship types found: {sorted(relationship_types)}")
    
    if hierarchical_edges:
        print(f"\n🎯 Hierarchical relationships found:")
        for edge in hierarchical_edges:
            print(f"  {edge['relation'].upper()}: {edge['visual']} (arrow_dir: {edge['arrow_direction']})")
    else:
        print(f"\n❌ No hierarchical relationships found!")
    
    # Test with different words that should have hierarchical relationships
    test_words = ['dog', 'animal', 'car', 'vehicle', 'hour', 'time']
    
    for test_word in test_words:
        print(f"\n" + "=" * 50)
        print(f"📋 Testing '{test_word}' for hierarchical relationships:")
        
        G_test, _ = explorer.explore_word(
            test_word, 
            depth=2, 
            max_nodes=100,
            show_hypernyms=True,
            show_hyponyms=True
        )
        
        found_hierarchy = False
        for source, target, edge_data in G_test.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            if relation in ['hypernym', 'hyponym']:
                found_hierarchy = True
                arrow_direction = edge_data.get('arrow_direction', 'to')
                source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
                target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
                
                if arrow_direction == 'from':
                    visual_source, visual_target = target_name, source_name
                else:
                    visual_source, visual_target = source_name, target_name
                
                print(f"  {relation.upper()}: {visual_source} → {visual_target} (arrow_dir: {arrow_direction})")
        
        if not found_hierarchy:
            print(f"  No hierarchical relationships found for '{test_word}'")

if __name__ == "__main__":
    debug_with_all_relationships() 