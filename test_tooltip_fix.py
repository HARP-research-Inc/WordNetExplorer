#!/usr/bin/env python3
"""
Test script to verify tooltip corrections for time unit relationships
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import WordNetExplorer

def test_tooltip_fix():
    """Test that tooltips are semantically correct after the fix."""
    
    print("🔍 Testing Tooltip Fix for Time Unit Relationships")
    print("=" * 60)
    
    # Create explorer
    explorer = WordNetExplorer()
    
    # Build graph for hour (which connects to time_unit)
    print("Building graph for 'hour'...")
    G, node_labels = explorer.explore_word('hour', depth=2, max_nodes=50)
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Look for edges involving time_unit
    print("\n🔍 Examining edges involving time_unit:")
    
    for source, target, edge_data in G.edges(data=True):
        if 'time_unit' in source or 'time_unit' in target:
            relation = edge_data.get('relation', 'unknown')
            arrow_direction = edge_data.get('arrow_direction', 'to')
            
            # Extract clean names
            source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
            target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
            
            # Show the relationship
            print(f"\n  Edge: {source} → {target}")
            print(f"    Relation: {relation}")
            print(f"    Arrow Direction: {arrow_direction}")
            print(f"    Names: {source_name} → {target_name}")
            
            # Generate tooltip (using same logic as visualizer)
            if relation == 'hypernym':
                tooltip = f"Is-a relationship: {source_name} is a type of {target_name}"
            elif relation == 'hyponym':
                tooltip = f"Type-includes relationship: {source_name} includes type {target_name}"
            else:
                tooltip = f"{relation}: {source_name} → {target_name}"
                
            print(f"    Tooltip: {tooltip}")
            
            # Check if this makes semantic sense
            if relation == 'hypernym':
                if 'time_unit' in target and 'time_unit' not in source:
                    print(f"    ✅ CORRECT: Specific time unit is a type of time_unit")
                else:
                    print(f"    ❌ INCORRECT: This doesn't make semantic sense")
            elif relation == 'hyponym':
                if 'time_unit' in source and 'time_unit' not in target:
                    print(f"    ✅ CORRECT: time_unit includes specific time units")
                else:
                    print(f"    ❌ INCORRECT: This doesn't make semantic sense")

if __name__ == "__main__":
    test_tooltip_fix() 