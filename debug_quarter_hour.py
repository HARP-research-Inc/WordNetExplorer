#!/usr/bin/env python3
"""
Debug quarter-hour tooltip issue
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import WordNetExplorer

def debug_quarter_hour():
    """Debug the quarter-hour tooltip issue."""
    
    print("🔍 Debugging Quarter-Hour Tooltip Issue")
    print("=" * 60)
    
    # Create explorer
    explorer = WordNetExplorer()
    
    # Test words that might connect to quarter-hour
    test_words = ['quarter', 'hour', 'time', 'quarter-hour']
    
    for word in test_words:
        print(f"\n📋 Testing '{word}':")
        print("-" * 40)
        
        try:
            G, node_labels = explorer.explore_word(word, depth=3, max_nodes=200)
            
            print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Look for any edge involving quarter or time_unit
            found_relevant = False
            for source, target, edge_data in G.edges(data=True):
                relation = edge_data.get('relation', 'unknown')
                arrow_direction = edge_data.get('arrow_direction', 'to')
                
                # Check if this edge involves quarter-hour or time_unit
                if ('quarter' in source.lower() or 'quarter' in target.lower() or 
                    'time_unit' in source or 'time_unit' in target):
                    
                    found_relevant = True
                    
                    # Extract clean names
                    source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
                    target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
                    
                    print(f"\n  📌 RELEVANT Edge: {source} → {target}")
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
                    
                    # Show current tooltip logic
                    if relation == 'hypernym':
                        current_tooltip = f"Is-a relationship: {source_name} is a type of {target_name}"
                        correct_tooltip = f"Is-a relationship: {visual_source_name} is a type of {visual_target_name}"
                    elif relation == 'hyponym':
                        current_tooltip = f"Type-includes relationship: {source_name} includes type {target_name}"
                        correct_tooltip = f"Type-includes relationship: {visual_source_name} includes type {visual_target_name}"
                    else:
                        current_tooltip = f"{relation}: {source_name} → {target_name}"
                        correct_tooltip = f"{relation}: {visual_source_name} → {visual_target_name}"
                        
                    print(f"    Current Tooltip: {current_tooltip}")
                    print(f"    Should Be: {correct_tooltip}")
                    
                    if current_tooltip == correct_tooltip:
                        print(f"    ✅ CORRECT")
                    else:
                        print(f"    ❌ INCORRECT - tooltip should match visual arrow")
            
            if not found_relevant:
                print("    No relevant edges found")
                
        except Exception as e:
            print(f"    Error testing '{word}': {e}")

if __name__ == "__main__":
    debug_quarter_hour() 