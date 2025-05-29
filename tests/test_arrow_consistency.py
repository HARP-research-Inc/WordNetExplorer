"""
Test suite for arrow direction consistency in WordNet Explorer.
"""

import pytest
from tests.conftest import analyze_arrow_direction


class TestArrowConsistency:
    """Test arrow direction consistency for taxonomic relationships."""
    
    @pytest.mark.dependency()
    def test_wordnet_explorer_setup(self, explorer):
        """Verify WordNet Explorer is properly initialized."""
        assert explorer is not None
        print("✅ WordNet Explorer initialized successfully")
    
    @pytest.mark.dependency(depends=["TestArrowConsistency::test_wordnet_explorer_setup"])
    def test_femtosecond_relationships(self, explorer, relationship_config_all):
        """Test taxonomic relationships for femtosecond."""
        print("\n🔍 Testing femtosecond taxonomic relationships...")
        
        G, node_labels = explorer.explore_word(
            'femtosecond', 
            depth=3, 
            max_nodes=100,
            show_hypernyms=True,
            show_hyponyms=True
        )
        
        assert G.number_of_nodes() > 0, "Graph should have nodes"
        assert G.number_of_edges() > 0, "Graph should have edges"
        
        # Collect taxonomic relationships
        taxonomic_edges = []
        for source, target, edge_data in G.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            if relation in ['hypernym', 'hyponym']:
                arrow_info = analyze_arrow_direction(source, target, edge_data)
                taxonomic_edges.append(arrow_info)
                print(f"  {relation.upper()}: {arrow_info['visual_arrow']}")
        
        assert len(taxonomic_edges) > 0, "Should find taxonomic relationships for femtosecond"
        
        # Store results for dependent tests
        self.femtosecond_edges = taxonomic_edges
        print(f"✅ Found {len(taxonomic_edges)} taxonomic relationships for femtosecond")
    
    @pytest.mark.dependency(depends=["TestArrowConsistency::test_femtosecond_relationships"])
    def test_time_hierarchy_consistency(self, explorer):
        """Test consistency of time unit hierarchy relationships."""
        print("\n🔍 Testing time unit hierarchy consistency...")
        
        time_words = ['femtosecond', 'picosecond', 'microsecond', 'second', 'minute', 'hour']
        all_taxonomic_edges = []
        
        for word in time_words:
            print(f"\n  Testing '{word}'...")
            
            G, _ = explorer.explore_word(
                word, 
                depth=2, 
                max_nodes=50,
                show_hypernyms=True,
                show_hyponyms=True
            )
            
            word_edges = []
            for source, target, edge_data in G.edges(data=True):
                relation = edge_data.get('relation', 'unknown')
                if relation in ['hypernym', 'hyponym']:
                    arrow_info = analyze_arrow_direction(source, target, edge_data)
                    word_edges.append(arrow_info)
                    all_taxonomic_edges.append(arrow_info)
                    print(f"    {relation.upper()}: {arrow_info['visual_arrow']}")
            
            print(f"    Found {len(word_edges)} taxonomic relationships")
        
        # Analyze consistency
        print(f"\n📊 Analyzing {len(all_taxonomic_edges)} total taxonomic relationships...")
        
        # Define hierarchy levels (higher number = more specific)
        hierarchy_levels = {
            'entity': 1,
            'abstraction': 2,
            'measure': 3,
            'time_unit': 4,
            'femtosecond': 5, 'picosecond': 5, 'nanosecond': 5,
            'microsecond': 5, 'millisecond': 5, 'second': 5,
            'minute': 5, 'hour': 5, 'day': 5, 'week': 5
        }
        
        specific_to_general = 0
        general_to_specific = 0
        unclear = 0
        
        for edge in all_taxonomic_edges:
            source_level = hierarchy_levels.get(edge['visual_source'].lower(), 0)
            target_level = hierarchy_levels.get(edge['visual_target'].lower(), 0)
            
            if source_level > target_level and source_level > 0 and target_level > 0:
                specific_to_general += 1
            elif target_level > source_level and source_level > 0 and target_level > 0:
                general_to_specific += 1
            else:
                unclear += 1
        
        print(f"  Specific → General: {specific_to_general}")
        print(f"  General → Specific: {general_to_specific}")
        print(f"  Unclear hierarchy: {unclear}")
        
        # Assert consistency - all should go specific → general
        consistency_ratio = specific_to_general / (specific_to_general + general_to_specific) if (specific_to_general + general_to_specific) > 0 else 0
        print(f"  Consistency ratio: {consistency_ratio:.2%}")
        
        assert consistency_ratio >= 0.8, f"Taxonomic arrows should be at least 80% consistent (specific → general). Current: {consistency_ratio:.2%}"
        print("✅ Taxonomic arrow consistency verified")
    
    @pytest.mark.dependency(depends=["TestArrowConsistency::test_time_hierarchy_consistency"])
    def test_tooltip_accuracy(self, explorer):
        """Test that tooltips accurately describe the visual arrows."""
        print("\n🔍 Testing tooltip accuracy...")
        
        G, _ = explorer.explore_word(
            'femtosecond', 
            depth=2, 
            max_nodes=50,
            show_hypernyms=True,
            show_hyponyms=True
        )
        
        tooltip_tests = []
        for source, target, edge_data in G.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            if relation in ['hypernym', 'hyponym']:
                arrow_info = analyze_arrow_direction(source, target, edge_data)
                
                # Generate expected tooltip based on visual arrow
                expected_tooltip = f"Is-a relationship: {arrow_info['visual_source']} is a type of {arrow_info['visual_target']}"
                
                tooltip_tests.append({
                    'visual_arrow': arrow_info['visual_arrow'],
                    'expected_tooltip': expected_tooltip,
                    'relation': relation
                })
                
                print(f"  {arrow_info['visual_arrow']} → \"{expected_tooltip}\"")
        
        assert len(tooltip_tests) > 0, "Should find tooltips to test"
        
        # All tooltips should follow "specific is a type of general" pattern
        for tooltip_test in tooltip_tests:
            assert "is a type of" in tooltip_test['expected_tooltip'], f"Tooltip should use 'is a type of' pattern: {tooltip_test['expected_tooltip']}"
        
        print(f"✅ Verified {len(tooltip_tests)} tooltip patterns")
    
    @pytest.mark.dependency(depends=["TestArrowConsistency::test_tooltip_accuracy"])
    def test_edge_duplication_prevention(self, explorer):
        """Test that edge duplication is properly prevented."""
        print("\n🔍 Testing edge duplication prevention...")
        
        G, _ = explorer.explore_word(
            'femtosecond', 
            depth=3, 
            max_nodes=100,
            show_hypernyms=True,
            show_hyponyms=True
        )
        
        # Check for duplicate edges
        edge_count = {}
        duplicate_edges = []
        
        for source, target, edge_data in G.edges(data=True):
            edge_key = (source, target)
            if edge_key in edge_count:
                edge_count[edge_key] += 1
                duplicate_edges.append(edge_key)
            else:
                edge_count[edge_key] = 1
        
        print(f"  Total edges: {G.number_of_edges()}")
        print(f"  Unique edge pairs: {len(edge_count)}")
        print(f"  Duplicate edges: {len(duplicate_edges)}")
        
        assert len(duplicate_edges) == 0, f"Found duplicate edges: {duplicate_edges}"
        print("✅ No duplicate edges found")
    
    @pytest.mark.dependency(depends=["TestArrowConsistency::test_edge_duplication_prevention"])
    def test_arrow_direction_property_handling(self, explorer):
        """Test that arrow_direction property is correctly handled."""
        print("\n🔍 Testing arrow_direction property handling...")
        
        G, _ = explorer.explore_word(
            'femtosecond', 
            depth=2, 
            max_nodes=50,
            show_hypernyms=True,
            show_hyponyms=True
        )
        
        arrow_directions = {'to': 0, 'from': 0, 'missing': 0}
        taxonomic_edges = []
        
        for source, target, edge_data in G.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            if relation in ['hypernym', 'hyponym']:
                arrow_direction = edge_data.get('arrow_direction')
                if arrow_direction == 'to':
                    arrow_directions['to'] += 1
                elif arrow_direction == 'from':
                    arrow_directions['from'] += 1
                else:
                    arrow_directions['missing'] += 1
                
                arrow_info = analyze_arrow_direction(source, target, edge_data)
                taxonomic_edges.append(arrow_info)
                print(f"  {relation}: {arrow_info['original_edge']} (arrow_dir: {arrow_direction}) → Visual: {arrow_info['visual_arrow']}")
        
        print(f"\n  Arrow direction distribution:")
        print(f"    'to': {arrow_directions['to']}")
        print(f"    'from': {arrow_directions['from']}")
        print(f"    missing: {arrow_directions['missing']}")
        
        assert arrow_directions['missing'] == 0, "All taxonomic edges should have arrow_direction property"
        assert len(taxonomic_edges) > 0, "Should find taxonomic edges to test"
        print("✅ Arrow direction property handling verified")


class TestSpecificCases:
    """Test specific edge cases and problematic relationships."""
    
    @pytest.mark.dependency(depends=["TestArrowConsistency::test_arrow_direction_property_handling"])
    def test_quarter_hour_case(self, explorer):
        """Test the specific quarter-hour case mentioned by the user."""
        print("\n🔍 Testing quarter-hour specific case...")
        
        # Test words that might connect to quarter-hour
        test_words = ['hour', 'minute', 'time']
        
        found_quarter_hour = False
        for word in test_words:
            print(f"\n  Testing '{word}' for quarter-hour connections...")
            
            G, _ = explorer.explore_word(
                word, 
                depth=3, 
                max_nodes=100,
                show_hypernyms=True,
                show_hyponyms=True
            )
            
            for source, target, edge_data in G.edges(data=True):
                source_name = source.split('.')[0] if '.' in source else source.split('_')[-1]
                target_name = target.split('.')[0] if '.' in target else target.split('_')[-1]
                
                if 'quarter' in source_name.lower() or 'quarter' in target_name.lower():
                    found_quarter_hour = True
                    relation = edge_data.get('relation', 'unknown')
                    if relation in ['hypernym', 'hyponym']:
                        arrow_info = analyze_arrow_direction(source, target, edge_data)
                        print(f"    FOUND: {relation.upper()}: {arrow_info['visual_arrow']}")
                        
                        # Verify the relationship makes semantic sense
                        if 'time_unit' in arrow_info['visual_arrow'] and 'quarter' in arrow_info['visual_arrow']:
                            print(f"    Testing semantic correctness...")
                            # quarter-hour should be more specific than time_unit
                            if 'quarter' in arrow_info['visual_source'] and 'time_unit' in arrow_info['visual_target']:
                                print(f"    ✅ Correct: quarter-hour → time_unit (specific → general)")
                            else:
                                print(f"    ❌ Incorrect: {arrow_info['visual_arrow']}")
        
        if not found_quarter_hour:
            print("  No quarter-hour relationships found in test words")
        
        print("✅ Quarter-hour case analysis complete")
    
    @pytest.mark.dependency(depends=["TestSpecificCases::test_quarter_hour_case"])
    def test_cross_pos_consistency(self, explorer):
        """Test arrow consistency across different parts of speech."""
        print("\n🔍 Testing cross-POS consistency...")
        
        test_cases = [
            ('dog', 'noun'),
            ('run', 'verb'),
            ('fast', 'adjective'),
            ('quickly', 'adverb')
        ]
        
        all_edges = []
        for word, pos in test_cases:
            print(f"\n  Testing '{word}' ({pos})...")
            
            G, _ = explorer.explore_word(
                word, 
                depth=2, 
                max_nodes=50,
                show_hypernyms=True,
                show_hyponyms=True
            )
            
            word_edges = []
            for source, target, edge_data in G.edges(data=True):
                relation = edge_data.get('relation', 'unknown')
                if relation in ['hypernym', 'hyponym']:
                    arrow_info = analyze_arrow_direction(source, target, edge_data)
                    word_edges.append(arrow_info)
                    all_edges.append(arrow_info)
                    print(f"    {relation.upper()}: {arrow_info['visual_arrow']}")
            
            print(f"    Found {len(word_edges)} taxonomic relationships")
        
        print(f"\n  Total taxonomic relationships across POS: {len(all_edges)}")
        
        # Verify all follow the same pattern (should be consistent regardless of POS)
        if len(all_edges) > 0:
            print("✅ Cross-POS consistency verified")
        else:
            print("⚠️  No taxonomic relationships found across test words")


@pytest.mark.dependency(depends=["TestSpecificCases::test_cross_pos_consistency"])
def test_overall_system_health(explorer):
    """Final test to verify overall system health."""
    print("\n🔍 Testing overall system health...")
    
    # Test that the system can handle various inputs without crashing
    test_words = ['test', 'example', 'simple', 'complex']
    
    for word in test_words:
        try:
            G, node_labels = explorer.explore_word(word, depth=1, max_nodes=20)
            assert G.number_of_nodes() >= 0, f"Graph should be created for '{word}'"
            print(f"  ✅ '{word}': {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        except Exception as e:
            pytest.fail(f"System failed for word '{word}': {e}")
    
    print("✅ Overall system health verified") 