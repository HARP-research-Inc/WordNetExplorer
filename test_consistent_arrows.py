#!/usr/bin/env python3
"""
Test consistent taxonomic arrow directions
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import WordNetExplorer

def test_consistent_arrows():
    """Test that taxonomic arrows are now consistent."""
    
    print("🔍 Testing Consistent Taxonomic Arrow Directions")
    print("=" * 70)
    
    # Create explorer
    explorer = WordNetExplorer()
    
    # Test femtosecond with ALL relationships enabled
    word = 'femtosecond'
    
    print(f"📋 Testing '{word}' with relationships enabled:")
    print("-" * 50)
    
    G, node_labels = explorer.explore_word(
        word, 
        depth=3, 
        max_nodes=100,
        show_hypernyms=True,
        show_hyponyms=True
    )
    
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Collect taxonomic relationships
    taxonomic_edges = []
    
    for source, target, edge_data in G.edges(data=True):
        relation = edge_data.get('relation', 'unknown')
        arrow_direction = edge_data.get('arrow_direction', 'to')
        
        if relation in ['hypernym', 'hyponym']:
            # Extract clean names
            source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
            target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
            
            # Determine what the visual arrow will be based on the new logic
            if relation == 'hypernym':
                # Hypernym: source → target (specific → general)
                visual_source, visual_target = source_name, target_name
            elif relation == 'hyponym':
                # Hyponym: target → source (specific → general)  
                visual_source, visual_target = target_name, source_name
            
            taxonomic_edges.append({
                'relation': relation,
                'original_edge': f"{source_name} → {target_name}",
                'visual_arrow': f"{visual_source} → {visual_target}",
                'arrow_direction': arrow_direction,
                'specific': visual_source,
                'general': visual_target
            })
    
    # Display results
    print(f"\n🎯 Taxonomic relationships found ({len(taxonomic_edges)}):")
    
    # Group by visual direction pattern
    specific_to_general = []
    general_to_specific = []
    
    # Known hierarchy: entity > abstraction > measure > time_unit > specific time units
    hierarchy = {
        'entity': 1,
        'abstraction': 2, 
        'measure': 3,
        'time_unit': 4,
        'femtosecond': 5,
        'picosecond': 5,
        'nanosecond': 5,
        'microsecond': 5,
        'millisecond': 5,
        'second': 5,
        'minute': 5,
        'hour': 5,
        'day': 5
    }
    
    for edge in taxonomic_edges:
        print(f"\n  {edge['relation'].upper()}: {edge['visual_arrow']}")
        print(f"    Original: {edge['original_edge']}")
        print(f"    Arrow direction: {edge['arrow_direction']}")
        
        # Check if this follows specific → general pattern
        specific_level = hierarchy.get(edge['specific'].lower(), 0)
        general_level = hierarchy.get(edge['general'].lower(), 0)
        
        if specific_level > general_level and specific_level > 0 and general_level > 0:
            specific_to_general.append(edge)
            print(f"    ✅ CORRECT: {edge['specific']} (level {specific_level}) → {edge['general']} (level {general_level})")
        elif general_level > specific_level and specific_level > 0 and general_level > 0:
            general_to_specific.append(edge)
            print(f"    ❌ BACKWARDS: {edge['specific']} (level {specific_level}) → {edge['general']} (level {general_level})")
        else:
            print(f"    ❓ UNCLEAR: Cannot determine hierarchy levels")
    
    # Summary
    print(f"\n📊 CONSISTENCY SUMMARY:")
    print(f"Specific → General arrows: {len(specific_to_general)}")
    print(f"General → Specific arrows: {len(general_to_specific)}")
    
    if len(general_to_specific) == 0:
        print(f"✅ CONSISTENT: All taxonomic arrows go from specific to general!")
    else:
        print(f"❌ INCONSISTENT: Found {len(general_to_specific)} backwards arrows")
    
    # Test tooltips
    print(f"\n💬 TOOLTIP EXAMPLES:")
    for edge in taxonomic_edges[:5]:  # Show first 5 examples
        tooltip = f"Is-a relationship: {edge['specific']} is a type of {edge['general']}"
        print(f"  {edge['visual_arrow']} → \"{tooltip}\"")

if __name__ == "__main__":
    test_consistent_arrows() 