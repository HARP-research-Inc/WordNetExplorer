#!/usr/bin/env python3
"""
Debug time unit hierarchy to show inconsistent arrow directions
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.core import WordNetExplorer

def debug_time_hierarchy():
    """Debug time unit hierarchy for inconsistent arrow directions."""
    
    print("🔍 Debugging Time Unit Hierarchy - Arrow Direction Consistency")
    print("=" * 80)
    
    # Create explorer
    explorer = WordNetExplorer()
    
    # Test specific time units that should show hierarchical relationships
    test_words = ['femtosecond', 'picosecond', 'microsecond', 'millisecond', 'second', 'minute', 'hour']
    
    all_taxonomic_edges = []
    
    for word in test_words:
        print(f"\n📋 Testing '{word}':")
        print("-" * 40)
        
        try:
            G, node_labels = explorer.explore_word(word, depth=2, max_nodes=50)
            
            print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
            
            # Look for taxonomic relationships (hypernym/hyponym)
            for source, target, edge_data in G.edges(data=True):
                relation = edge_data.get('relation', 'unknown')
                arrow_direction = edge_data.get('arrow_direction', 'to')
                
                if relation in ['hypernym', 'hyponym']:
                    # Extract clean names
                    source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
                    target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
                    
                    # Determine visual arrow direction
                    if arrow_direction == 'from':
                        visual_source, visual_target = target_name, source_name
                    else:
                        visual_source, visual_target = source_name, target_name
                    
                    edge_info = {
                        'word': word,
                        'relation': relation,
                        'original_edge': f"{source_name} → {target_name}",
                        'visual_arrow': f"{visual_source} → {visual_target}",
                        'arrow_direction': arrow_direction,
                        'source_name': source_name,
                        'target_name': target_name,
                        'visual_source': visual_source,
                        'visual_target': visual_target
                    }
                    
                    all_taxonomic_edges.append(edge_info)
                    
                    print(f"  📌 {relation.upper()}: {edge_info['original_edge']}")
                    print(f"     Arrow Dir: {arrow_direction}")
                    print(f"     Visual: {edge_info['visual_arrow']}")
                    
        except Exception as e:
            print(f"    Error testing '{word}': {e}")
    
    # Analyze consistency
    print(f"\n🔍 CONSISTENCY ANALYSIS")
    print("=" * 80)
    
    print("\nAll taxonomic relationships found:")
    
    # Group by visual arrow pattern
    abstract_to_specific = []  # e.g., time_unit → second
    specific_to_abstract = []  # e.g., second → time_unit
    
    for edge in all_taxonomic_edges:
        print(f"\n  {edge['relation'].upper()}: {edge['visual_arrow']}")
        print(f"    From word: {edge['word']}")
        print(f"    Arrow direction: {edge['arrow_direction']}")
        
        # Try to determine if this goes from abstract to specific or vice versa
        # Time units: time_unit is most abstract, femtosecond/picosecond etc are most specific
        abstract_terms = ['time_unit', 'unit', 'period', 'interval']
        specific_terms = ['femtosecond', 'picosecond', 'nanosecond', 'microsecond', 'millisecond', 
                         'second', 'minute', 'hour', 'day', 'week', 'month', 'year']
        
        source = edge['visual_source'].lower()
        target = edge['visual_target'].lower()
        
        source_is_abstract = any(term in source for term in abstract_terms)
        target_is_abstract = any(term in target for term in abstract_terms)
        source_is_specific = any(term in source for term in specific_terms)
        target_is_specific = any(term in target for term in specific_terms)
        
        if source_is_abstract and target_is_specific:
            abstract_to_specific.append(edge)
            print(f"    📊 ABSTRACT → SPECIFIC")
        elif source_is_specific and target_is_abstract:
            specific_to_abstract.append(edge)
            print(f"    📊 SPECIFIC → ABSTRACT")
        else:
            print(f"    📊 UNCLEAR HIERARCHY")
    
    print(f"\n📊 SUMMARY:")
    print(f"Abstract → Specific arrows: {len(abstract_to_specific)}")
    print(f"Specific → Abstract arrows: {len(specific_to_abstract)}")
    
    if len(abstract_to_specific) > 0 and len(specific_to_abstract) > 0:
        print(f"❌ INCONSISTENT: Arrows go both directions!")
        print(f"\nRecommendation: Choose one consistent direction:")
        print(f"  Option 1: All arrows go ABSTRACT → SPECIFIC (general to specific)")
        print(f"  Option 2: All arrows go SPECIFIC → ABSTRACT (specific to general)")
    elif len(abstract_to_specific) > 0:
        print(f"✅ CONSISTENT: All arrows go ABSTRACT → SPECIFIC")
    elif len(specific_to_abstract) > 0:
        print(f"✅ CONSISTENT: All arrows go SPECIFIC → ABSTRACT")
    else:
        print(f"⚠️  No clear hierarchical relationships found")

if __name__ == "__main__":
    debug_time_hierarchy() 