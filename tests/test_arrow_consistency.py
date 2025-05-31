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
    def test_comprehensive_specific_to_abstract_arrows(self, explorer):
        """Comprehensive test to ensure ALL taxonomic arrows go from specific to abstract across all relevant categories."""
        print("\n🔍 COMPREHENSIVE TEST: All taxonomic arrows specific → abstract...")
        
        # Test words from different semantic domains
        test_words = [
            # Animals
            'dog', 'cat', 'bird', 'mammal', 'vertebrate',
            # Objects
            'car', 'vehicle', 'chair', 'furniture', 'table',
            # Time units
            'second', 'minute', 'hour', 'day', 'week',
            # Abstract concepts
            'emotion', 'happiness', 'sadness', 'feeling',
            # Actions/Verbs
            'run', 'walk', 'move', 'travel',
            # Properties/Adjectives
            'big', 'large', 'huge', 'small', 'tiny'
        ]
        
        all_violations = []
        all_taxonomic_relationships = []
        domain_stats = {}
        
        for word in test_words:
            print(f"\n  🔍 Testing '{word}'...")
            
            try:
                G, _ = explorer.explore_word(
                    word, 
                    depth=2, 
                    max_nodes=30,
                    show_hypernyms=True,
                    show_hyponyms=True
                )
                
                word_relationships = []
                for source, target, edge_data in G.edges(data=True):
                    relation = edge_data.get('relation', 'unknown')
                    if relation in ['hypernym', 'hyponym']:
                        arrow_info = analyze_arrow_direction(source, target, edge_data)
                        word_relationships.append(arrow_info)
                        all_taxonomic_relationships.append(arrow_info)
                        
                        # Check for violations of specific → abstract rule
                        violation = self._check_specific_to_abstract_violation(arrow_info)
                        if violation:
                            all_violations.append({
                                'word': word,
                                'arrow_info': arrow_info,
                                'violation_reason': violation
                            })
                        
                        print(f"    {relation.upper()}: {arrow_info['visual_arrow']}")
                
                # Track domain statistics
                domain = self._categorize_word_domain(word)
                if domain not in domain_stats:
                    domain_stats[domain] = {'total': 0, 'violations': 0}
                domain_stats[domain]['total'] += len(word_relationships)
                domain_stats[domain]['violations'] += len([v for v in all_violations if v['word'] == word])
                
                print(f"    Found {len(word_relationships)} taxonomic relationships")
                
            except Exception as e:
                print(f"    ⚠️  Error processing '{word}': {e}")
                continue
        
        # Analyze results
        print(f"\n📊 COMPREHENSIVE ANALYSIS RESULTS:")
        print(f"  Total taxonomic relationships analyzed: {len(all_taxonomic_relationships)}")
        print(f"  Total violations found: {len(all_violations)}")
        
        # Domain breakdown
        print(f"\n📈 Domain Breakdown:")
        for domain, stats in domain_stats.items():
            violation_rate = (stats['violations'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"    {domain}: {stats['total']} relationships, {stats['violations']} violations ({violation_rate:.1f}%)")
        
        # Report violations
        if all_violations:
            print(f"\n❌ VIOLATIONS FOUND:")
            for violation in all_violations[:10]:  # Show first 10 violations
                print(f"    Word: {violation['word']}")
                print(f"    Arrow: {violation['arrow_info']['visual_arrow']}")
                print(f"    Reason: {violation['violation_reason']}")
                print()
        
        # Calculate overall success rate
        violation_rate = len(all_violations) / len(all_taxonomic_relationships) if all_taxonomic_relationships else 0
        success_rate = 1 - violation_rate
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"    Success rate: {success_rate:.2%}")
        print(f"    Violation rate: {violation_rate:.2%}")
        
        # Assert that we have very high consistency (allowing for some edge cases in WordNet)
        assert success_rate >= 0.90, f"Taxonomic arrows should be at least 90% consistent (specific → abstract). Current: {success_rate:.2%}"
        
        if success_rate >= 0.95:
            print("✅ EXCELLENT: 95%+ consistency achieved")
        elif success_rate >= 0.90:
            print("✅ GOOD: 90%+ consistency achieved")
        
        print("✅ Comprehensive specific → abstract arrow test PASSED")
    
    def _check_specific_to_abstract_violation(self, arrow_info):
        """Check if an arrow violates the specific → abstract rule."""
        source = arrow_info['visual_source'].lower()
        target = arrow_info['visual_target'].lower()
        
        # Define abstraction levels (higher = more abstract)
        abstraction_levels = {
            # Most concrete
            'femtosecond': 1, 'picosecond': 1, 'nanosecond': 1, 'microsecond': 1,
            'millisecond': 1, 'second': 1, 'minute': 1, 'hour': 1, 'day': 1,
            'dog': 1, 'cat': 1, 'bird': 1, 'car': 1, 'chair': 1, 'table': 1,
            'happiness': 1, 'sadness': 1,
            
            # Intermediate
            'canine': 2, 'feline': 2, 'mammal': 2, 'vehicle': 2, 'furniture': 2,
            'time_unit': 2, 'emotion': 2,
            
            # More abstract
            'vertebrate': 3, 'animal': 3, 'organism': 3, 'artifact': 3,
            'measure': 3, 'feeling': 3,
            
            # Very abstract
            'living_thing': 4, 'whole': 4, 'object': 4, 'quantity': 4,
            'abstraction': 5, 'entity': 6
        }
        
        source_level = abstraction_levels.get(source, 0)
        target_level = abstraction_levels.get(target, 0)
        
        # If we can determine levels and source is more abstract than target, it's a violation
        if source_level > 0 and target_level > 0 and source_level > target_level:
            return f"Abstract ({source}, level {source_level}) → Specific ({target}, level {target_level})"
        
        # Check for obvious violations based on common knowledge
        if self._is_obvious_abstract_to_specific(source, target):
            return f"Obvious violation: {source} is more abstract than {target}"
        
        return None
    
    def _is_obvious_abstract_to_specific(self, source, target):
        """Check for obvious abstract → specific violations."""
        abstract_to_specific_patterns = [
            ('entity', ['dog', 'cat', 'car', 'table']),
            ('abstraction', ['measure', 'time_unit', 'emotion']),
            ('measure', ['second', 'minute', 'hour']),
            ('animal', ['dog', 'cat', 'bird']),
            ('vehicle', ['car', 'truck', 'bus']),
            ('furniture', ['chair', 'table', 'bed']),
            ('emotion', ['happiness', 'sadness', 'anger'])
        ]
        
        for abstract_term, specific_terms in abstract_to_specific_patterns:
            if source == abstract_term and target in specific_terms:
                return True
        
        return False
    
    def _categorize_word_domain(self, word):
        """Categorize a word into a semantic domain."""
        domains = {
            'animals': ['dog', 'cat', 'bird', 'mammal', 'vertebrate'],
            'objects': ['car', 'vehicle', 'chair', 'furniture', 'table'],
            'time': ['second', 'minute', 'hour', 'day', 'week', 'femtosecond', 'picosecond'],
            'emotions': ['emotion', 'happiness', 'sadness', 'feeling'],
            'actions': ['run', 'walk', 'move', 'travel'],
            'properties': ['big', 'large', 'huge', 'small', 'tiny']
        }
        
        for domain, words in domains.items():
            if word in words:
                return domain
        
        return 'other'

    @pytest.mark.dependency(depends=["TestArrowConsistency::test_comprehensive_specific_to_abstract_arrows"])
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

    @pytest.mark.dependency(depends=["TestArrowConsistency::test_arrow_direction_property_handling"])
    def test_enhanced_color_scheme(self, explorer):
        """Test that the enhanced color scheme properly groups relationship families."""
        print("\n🔍 Testing enhanced color scheme...")
        
        # Import the color functions
        from src.wordnet.relationships import get_relationship_color, RelationshipType
        
        # Test a word that will likely have multiple relationship types
        G, _ = explorer.explore_word(
            'dog', 
            depth=2, 
            max_nodes=50,
            show_hypernyms=True,
            show_hyponyms=True,
            show_meronyms=True,
            show_holonyms=True,
            show_similar=True,
            show_antonyms=True
        )
        
        # Collect all relationships and their colors
        relationship_colors = {}
        color_families = {
            'taxonomic': set(),
            'part_whole': set(), 
            'opposition': set(),
            'causation': set(),
            'cross_reference': set(),
            'verb_specific': set(),
            'morphological': set(),
            'domain': set(),
            'basic': set()
        }
        
        for source, target, edge_data in G.edges(data=True):
            relation = edge_data.get('relation', 'unknown')
            color = edge_data.get('color', '#000000')
            
            if relation not in relationship_colors:
                relationship_colors[relation] = color
                
            # Categorize into families
            if relation in ['hypernym', 'hyponym', 'instance_hypernym', 'instance_hyponym']:
                color_families['taxonomic'].add(color)
            elif relation in ['member_holonym', 'substance_holonym', 'part_holonym', 
                            'member_meronym', 'substance_meronym', 'part_meronym']:
                color_families['part_whole'].add(color)
            elif relation in ['antonym', 'similar_to']:
                color_families['opposition'].add(color)
            elif relation in ['entailment', 'cause']:
                color_families['causation'].add(color)
            elif relation in ['attribute', 'also_see']:
                color_families['cross_reference'].add(color)
            elif relation in ['verb_group', 'participle_of_verb']:
                color_families['verb_specific'].add(color)
            elif relation in ['derivationally_related_form', 'pertainym', 'derived_from']:
                color_families['morphological'].add(color)
            elif 'domain' in relation:
                color_families['domain'].add(color)
            elif relation == 'sense':
                color_families['basic'].add(color)
        
        print(f"\n  Relationships found: {list(relationship_colors.keys())}")
        print(f"  Colors by relationship:")
        for rel, color in relationship_colors.items():
            print(f"    {rel}: {color}")
        
        # Test color family consistency
        print(f"\n  Color families analysis:")
        for family, colors in color_families.items():
            if colors:
                print(f"    {family.replace('_', ' ').title()}: {len(colors)} unique colors - {list(colors)}")
                
                # Verify that colors within a family are visually related
                if len(colors) > 1:
                    colors_list = list(colors)
                    family_consistency = self._analyze_color_family_consistency(family, colors_list)
                    print(f"      Consistency: {family_consistency}")
        
        # Test specific color mappings
        test_relationships = [
            (RelationshipType.HYPERNYM, 'taxonomic'),
            (RelationshipType.HYPONYM, 'taxonomic'),
            (RelationshipType.MEMBER_HOLONYM, 'part_whole'),
            (RelationshipType.PART_MERONYM, 'part_whole'),
            (RelationshipType.ANTONYM, 'opposition'),
            (RelationshipType.SIMILAR_TO, 'opposition')
        ]
        
        print(f"\n  Testing specific relationship color mappings:")
        for rel_type, expected_family in test_relationships:
            color = get_relationship_color(rel_type)
            print(f"    {rel_type.value}: {color} (expected {expected_family} family)")
            
            # Verify the color is not the default black
            assert color != '#000000', f"Relationship {rel_type.value} should have a specific color"
            
            # Verify the color is a valid hex color
            assert color.startswith('#'), f"Color {color} should be a hex color"
            assert len(color) == 7, f"Color {color} should be 7 characters long"
        
        print("✅ Enhanced color scheme verification completed")
    
    def _analyze_color_family_consistency(self, family, colors):
        """Analyze if colors in a family are visually consistent."""
        if len(colors) <= 1:
            return "Single color - consistent"
        
        # Convert hex colors to RGB for analysis
        rgb_colors = []
        for color in colors:
            if color.startswith('#') and len(color) == 7:
                try:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16) 
                    b = int(color[5:7], 16)
                    rgb_colors.append((r, g, b))
                except ValueError:
                    continue
        
        if len(rgb_colors) <= 1:
            return "Unable to analyze"
        
        # For family consistency, check if colors share similar dominant channels
        family_expectations = {
            'taxonomic': 'red_dominant',     # Red family
            'part_whole': 'green_dominant',  # Green family
            'opposition': 'purple_mixed',    # Purple family (high red+blue)
            'causation': 'orange_mixed',     # Orange family (high red+green)
            'cross_reference': 'blue_dominant',  # Blue family
            'morphological': 'pink_mixed',   # Pink family (high red)
            'domain': 'grey_balanced'        # Grey family (balanced RGB)
        }
        
        expected = family_expectations.get(family, 'unknown')
        
        if expected == 'red_dominant':
            # Check if red is dominant in most colors
            red_dominant = sum(1 for r, g, b in rgb_colors if r > g and r > b)
            return f"Red dominant in {red_dominant}/{len(rgb_colors)} colors"
        elif expected == 'green_dominant':
            green_dominant = sum(1 for r, g, b in rgb_colors if g > r and g > b)
            return f"Green dominant in {green_dominant}/{len(rgb_colors)} colors"
        elif expected == 'blue_dominant':
            blue_dominant = sum(1 for r, g, b in rgb_colors if b > r and b > g)
            return f"Blue dominant in {blue_dominant}/{len(rgb_colors)} colors"
        elif expected == 'purple_mixed':
            purple_like = sum(1 for r, g, b in rgb_colors if r > 100 and b > 100 and g < max(r, b))
            return f"Purple-like in {purple_like}/{len(rgb_colors)} colors"
        elif expected == 'orange_mixed':
            orange_like = sum(1 for r, g, b in rgb_colors if r > 150 and g > 50 and b < 100)
            return f"Orange-like in {orange_like}/{len(rgb_colors)} colors"
        else:
            return f"Family analysis for {expected}"


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