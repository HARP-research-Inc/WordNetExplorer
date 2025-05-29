#!/usr/bin/env python3
"""
Debug specific tooltip issues with time unit relationships
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import WordNetExplorer

def debug_specific_tooltips():
    """Debug the specific tooltip issue with time_unit relationships."""
    
    print("🔍 Debugging Specific Tooltip Issues")
    print("=" * 60)
    
    # Create explorer
    explorer = WordNetExplorer()
    
    # Test multiple time unit words to find the issue
    test_words = ['hour', 'minute', 'second', 'microsecond', 'femtosecond']
    
    for word in test_words:
        print(f"\n📋 Testing '{word}':")
        print("-" * 40)
        
        G, node_labels = explorer.explore_word(word, depth=2, max_nodes=100)
        
        print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        # Look for ALL edges and check their tooltips
        for source, target, edge_data in G.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            arrow_direction = edge_data.get('arrow_direction', 'to')
            
            # Extract clean names
            source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
            target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
            
            # Only show taxonomic relationships (hypernym/hyponym)
            if relation in ['hypernym', 'hyponym']:
                print(f"\n  Edge: {source} → {target}")
                print(f"    Clean Names: {source_name} → {target_name}")
                print(f"    Relation: {relation}")
                print(f"    Arrow Direction: {arrow_direction}")
                
                # Show what the visual arrow looks like after direction handling
                if arrow_direction == 'from':
                    visual_source, visual_target = target, source
                    visual_source_name = target_name
                    visual_target_name = source_name
                else:
                    visual_source, visual_target = source, target
                    visual_source_name = source_name
                    visual_target_name = target_name
                
                print(f"    Visual Arrow: {visual_source_name} → {visual_target_name}")
                
                # Current tooltip logic (using original names)
                if relation == 'hypernym':
                    tooltip = f"Is-a relationship: {source_name} is a type of {target_name}"
                elif relation == 'hyponym':
                    tooltip = f"Type-includes relationship: {source_name} includes type {target_name}"
                    
                print(f"    Current Tooltip: {tooltip}")
                
                # Check if this makes sense with the visual arrow
                if relation == 'hypernym':
                    # For hypernym, we want the tooltip to match the visual arrow direction
                    # Visual arrow goes from specific to general
                    expected_tooltip = f"Is-a relationship: {visual_source_name} is a type of {visual_target_name}"
                elif relation == 'hyponym':
                    # For hyponym, we want the tooltip to match the visual arrow direction  
                    # Visual arrow goes from general to specific
                    expected_tooltip = f"Type-includes relationship: {visual_source_name} includes type {visual_target_name}"
                
                print(f"    Expected Tooltip: {expected_tooltip}")
                
                if tooltip == expected_tooltip:
                    print(f"    ✅ CORRECT")
                else:
                    print(f"    ❌ INCORRECT - tooltip doesn't match visual arrow")

if __name__ == "__main__":
    debug_specific_tooltips() 