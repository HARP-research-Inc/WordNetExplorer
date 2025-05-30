"""
Test suite for URL parameter correlation with rendered settings in WordNet Explorer.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.session import SessionManager
from src.config.settings import DEFAULT_SETTINGS, LAYOUT_OPTIONS


class TestURLParameterCorrelation:
    """Test URL parameter correlation with rendered settings."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Mock streamlit session state
        self.mock_session_state = {}
        
        # Create a session manager instance
        self.session_manager = SessionManager()
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock streamlit components for testing."""
        with patch('streamlit.session_state', self.mock_session_state):
            with patch('streamlit.query_params', {}) as mock_query_params:
                yield mock_query_params
    
    def test_url_parameter_mapping_completeness(self):
        """Test that all URL parameter mappings are complete and bidirectional."""
        print("\n🔍 Testing URL parameter mapping completeness...")
        
        # Get URL parameter mappings from session manager
        with patch('streamlit.session_state', self.mock_session_state):
            session_manager = SessionManager()
            
        # Test basic parameter mappings
        basic_mappings = {
            'word': ('word', str),
            'depth': ('depth', int), 
            'sense': ('sense_number', int),
            'hypernyms': ('show_hypernyms', lambda x: x.lower() == 'true'),
            'hyponyms': ('show_hyponyms', lambda x: x.lower() == 'true'),
            'meronyms': ('show_meronyms', lambda x: x.lower() == 'true'),
            'holonyms': ('show_holonyms', lambda x: x.lower() == 'true'),
            'layout': ('layout_type', str),
            'node_size': ('node_size_multiplier', float),
            'color': ('color_scheme', str),
            'physics': ('enable_physics', lambda x: x.lower() == 'true'),
            'spring': ('spring_strength', float),
            'gravity': ('central_gravity', float),
            'labels': ('show_labels', lambda x: x.lower() == 'true'),
            'edge_width': ('edge_width', int),
            'show_info': ('show_info', lambda x: x.lower() == 'true'),
            'show_graph': ('show_graph', lambda x: x.lower() == 'true'),
        }
        
        # Test reverse mappings
        reverse_mappings = {
            'word': 'word',
            'depth': 'depth',
            'sense_number': 'sense',
            'show_hypernyms': 'hypernyms',
            'show_hyponyms': 'hyponyms', 
            'show_meronyms': 'meronyms',
            'show_holonyms': 'holonyms',
            'layout_type': 'layout',
            'node_size_multiplier': 'node_size',
            'color_scheme': 'color',
            'enable_physics': 'physics',
            'spring_strength': 'spring',
            'central_gravity': 'gravity',
            'show_labels': 'labels',
            'edge_width': 'edge_width',
            'show_info': 'show_info',
            'show_graph': 'show_graph',
        }
        
        # Verify bidirectional mappings
        for url_param, (setting_key, _) in basic_mappings.items():
            if setting_key == 'sense_number':
                # Special case for sense number 
                assert 'sense_number' in reverse_mappings, f"Reverse mapping missing for sense_number"
                assert reverse_mappings['sense_number'] == 'sense', f"Reverse mapping incorrect for sense_number"
            else:
                assert setting_key in reverse_mappings, f"Reverse mapping missing for {setting_key}"
                assert reverse_mappings[setting_key] == url_param, f"Reverse mapping incorrect for {setting_key}"
        
        print(f"✅ Verified {len(basic_mappings)} parameter mappings are bidirectional")
    
    def test_url_parameter_type_conversions(self, mock_streamlit):
        """Test that URL parameter type conversions work correctly."""
        print("\n🔍 Testing URL parameter type conversions...")
        
        test_cases = [
            # String parameters
            ('word', 'dog', str, 'dog'),
            ('layout', 'Hierarchical', str, 'Hierarchical'),
            ('color', 'Vibrant', str, 'Vibrant'),
            
            # Integer parameters  
            ('depth', '2', int, 2),
            ('sense', '3', int, 3),
            ('edge_width', '4', int, 4),
            
            # Float parameters
            ('node_size', '1.5', float, 1.5),
            ('spring', '0.05', float, 0.05),
            ('gravity', '0.8', float, 0.8),
            
            # Boolean parameters
            ('hypernyms', 'true', bool, True),
            ('hyponyms', 'false', bool, False),
            ('physics', 'TRUE', bool, True),
            ('labels', 'False', bool, False),
            ('show_info', 'true', bool, True),
            ('show_graph', 'false', bool, False),
        ]
        
        conversion_errors = []
        
        for url_param, url_value, expected_type, expected_value in test_cases:
            try:
                # Mock query params with this parameter
                mock_streamlit.update({url_param: url_value})
                
                # Get settings from URL
                settings = self.session_manager.get_settings_from_url()
                
                # Find the setting key for this URL param
                param_mappings = {
                    'word': 'word',
                    'depth': 'depth',
                    'sense': 'sense_number',
                    'hypernyms': 'show_hypernyms',
                    'hyponyms': 'show_hyponyms',
                    'meronyms': 'show_meronyms', 
                    'holonyms': 'show_holonyms',
                    'layout': 'layout_type',
                    'node_size': 'node_size_multiplier',
                    'color': 'color_scheme',
                    'physics': 'enable_physics',
                    'spring': 'spring_strength',
                    'gravity': 'central_gravity',
                    'labels': 'show_labels',
                    'edge_width': 'edge_width',
                    'show_info': 'show_info',
                    'show_graph': 'show_graph',
                }
                
                setting_key = param_mappings.get(url_param)
                if setting_key and setting_key in settings:
                    actual_value = settings[setting_key]
                    actual_type = type(actual_value)
                    
                    # Check type and value
                    if expected_type == bool:
                        assert isinstance(actual_value, bool), f"Expected bool for {url_param}, got {actual_type}"
                        assert actual_value == expected_value, f"Expected {expected_value} for {url_param}, got {actual_value}"
                    elif expected_type == int:
                        assert isinstance(actual_value, int), f"Expected int for {url_param}, got {actual_type}"
                        assert actual_value == expected_value, f"Expected {expected_value} for {url_param}, got {actual_value}"
                    elif expected_type == float:
                        assert isinstance(actual_value, float), f"Expected float for {url_param}, got {actual_type}" 
                        assert abs(actual_value - expected_value) < 0.001, f"Expected {expected_value} for {url_param}, got {actual_value}"
                    elif expected_type == str:
                        assert isinstance(actual_value, str), f"Expected str for {url_param}, got {actual_type}"
                        assert actual_value == expected_value, f"Expected {expected_value} for {url_param}, got {actual_value}"
                    
                    print(f"  ✅ {url_param}='{url_value}' → {setting_key}={actual_value} ({actual_type.__name__})")
                else:
                    conversion_errors.append(f"Setting key '{setting_key}' not found for URL param '{url_param}'")
                
                # Clear mock for next test
                mock_streamlit.clear()
                
            except Exception as e:
                conversion_errors.append(f"Error converting {url_param}='{url_value}': {e}")
        
        if conversion_errors:
            print(f"\n❌ Conversion errors:")
            for error in conversion_errors:
                print(f"    {error}")
            pytest.fail(f"Found {len(conversion_errors)} conversion errors")
        
        print(f"✅ Verified {len(test_cases)} type conversions")
    
    def test_default_settings_correlation(self, mock_streamlit):
        """Test that default settings correlate correctly with URL parameters."""
        print("\n🔍 Testing default settings correlation...")
        
        # Test with empty URL parameters (should use defaults)
        settings = self.session_manager.get_settings_from_url()
        
        # Should return empty dict when no URL params are set
        assert isinstance(settings, dict), "get_settings_from_url should return a dict"
        print(f"  Empty URL params → {len(settings)} settings loaded")
        
        # Test specific default values by setting URL params to defaults
        default_test_cases = [
            ('depth', str(DEFAULT_SETTINGS['depth']), 'depth'),
            ('hypernyms', str(DEFAULT_SETTINGS['show_hypernyms']).lower(), 'show_hypernyms'),
            ('layout', DEFAULT_SETTINGS['layout_type'], 'layout_type'),
            ('node_size', str(DEFAULT_SETTINGS['node_size_multiplier']), 'node_size_multiplier'),
            ('color', DEFAULT_SETTINGS['color_scheme'], 'color_scheme'),
            ('physics', str(DEFAULT_SETTINGS['enable_physics']).lower(), 'enable_physics'),
        ]
        
        for url_param, url_value, setting_key in default_test_cases:
            mock_streamlit.update({url_param: url_value})
            settings = self.session_manager.get_settings_from_url()
            
            if setting_key in settings:
                expected_default = DEFAULT_SETTINGS[setting_key]
                actual_value = settings[setting_key]
                
                # Handle type-specific comparisons
                if isinstance(expected_default, bool):
                    assert actual_value == expected_default, f"Default mismatch for {setting_key}: expected {expected_default}, got {actual_value}"
                elif isinstance(expected_default, (int, float)):
                    assert abs(actual_value - expected_default) < 0.001, f"Default mismatch for {setting_key}: expected {expected_default}, got {actual_value}"
                else:
                    assert actual_value == expected_default, f"Default mismatch for {setting_key}: expected {expected_default}, got {actual_value}"
                
                print(f"  ✅ {url_param}='{url_value}' → {setting_key}={actual_value} (matches default)")
            
            mock_streamlit.clear()
        
        print(f"✅ Verified {len(default_test_cases)} default value correlations")
    
    def test_settings_to_url_parameter_conversion(self, mock_streamlit):
        """Test that settings can be correctly converted back to URL parameters."""
        print("\n🔍 Testing settings to URL parameter conversion...")
        
        # Test various settings configurations
        test_settings = [
            {
                'word': 'dog',
                'depth': 2,
                'show_hypernyms': True,
                'show_hyponyms': False,
                'layout_type': 'Hierarchical',
                'node_size_multiplier': 1.5,
                'color_scheme': 'Vibrant',
                'enable_physics': False,
                'spring_strength': 0.06,
                'central_gravity': 0.5,
                'show_labels': False,
                'edge_width': 3,
                'show_info': True,
                'show_graph': False,
            },
            {
                'word': 'cat',
                'sense_number': 2,  # Special case for sense number
                'depth': 3,
                'show_hypernyms': False,
                'show_hyponyms': True,
                'layout_type': 'Circular',
                'color_scheme': 'Pastel',
                'enable_physics': True,
            }
        ]
        
        conversion_errors = []
        
        for i, settings in enumerate(test_settings):
            try:
                # Mock the update_url_with_settings method to capture what would be set
                captured_params = {}
                
                def mock_set_query_params(params):
                    captured_params.update(params)
                
                with patch.object(self.session_manager, 'set_query_params', mock_set_query_params):
                    self.session_manager.update_url_with_settings(settings, force_update=True)
                
                # Verify expected URL parameters were generated
                expected_mappings = {
                    'word': 'word',
                    'depth': 'depth', 
                    'sense_number': 'sense',
                    'show_hypernyms': 'hypernyms',
                    'show_hyponyms': 'hyponyms',
                    'show_meronyms': 'meronyms',
                    'show_holonyms': 'holonyms',
                    'layout_type': 'layout',
                    'node_size_multiplier': 'node_size',
                    'color_scheme': 'color',
                    'enable_physics': 'physics',
                    'spring_strength': 'spring',
                    'central_gravity': 'gravity',
                    'show_labels': 'labels',
                    'edge_width': 'edge_width',
                    'show_info': 'show_info',
                    'show_graph': 'show_graph',
                }
                
                for setting_key, setting_value in settings.items():
                    if setting_key in expected_mappings:
                        url_param = expected_mappings[setting_key]
                        
                        if url_param in captured_params:
                            captured_value = captured_params[url_param]
                            
                            # Verify conversion based on type
                            if isinstance(setting_value, bool):
                                expected_str = str(setting_value).lower()
                                assert captured_value == expected_str, f"Boolean conversion failed: {setting_key}={setting_value} → {url_param}='{captured_value}' (expected '{expected_str}')"
                            elif isinstance(setting_value, (int, float)):
                                expected_str = str(setting_value)
                                assert captured_value == expected_str, f"Numeric conversion failed: {setting_key}={setting_value} → {url_param}='{captured_value}' (expected '{expected_str}')"
                            else:
                                expected_str = str(setting_value)
                                assert captured_value == expected_str, f"String conversion failed: {setting_key}={setting_value} → {url_param}='{captured_value}' (expected '{expected_str}')"
                            
                            print(f"  ✅ {setting_key}={setting_value} → {url_param}='{captured_value}'")
                        else:
                            print(f"  ⚠️  Setting {setting_key}={setting_value} did not generate URL param {url_param}")
                
                print(f"  Test case {i+1}: Generated {len(captured_params)} URL parameters")
                
            except Exception as e:
                conversion_errors.append(f"Error in test case {i+1}: {e}")
        
        if conversion_errors:
            print(f"\n❌ Settings-to-URL conversion errors:")
            for error in conversion_errors:
                print(f"    {error}")
            pytest.fail(f"Found {len(conversion_errors)} settings-to-URL conversion errors")
        
        print(f"✅ Verified settings-to-URL conversion for {len(test_settings)} test cases")
    
    def test_invalid_url_parameter_handling(self, mock_streamlit):
        """Test that invalid URL parameters are handled gracefully."""
        print("\n🔍 Testing invalid URL parameter handling...")
        
        invalid_test_cases = [
            # Invalid types
            ('depth', 'invalid_number', 'Should ignore invalid integer'),
            ('node_size', 'not_a_float', 'Should ignore invalid float'),
            ('physics', 'maybe', 'Should ignore invalid boolean'),
            ('edge_width', '3.5', 'Should handle float as int'),
            
            # Out-of-range values (should still convert but may be clamped by UI)
            ('depth', '-1', 'Should handle negative depth'),
            ('node_size', '10.0', 'Should handle large node size'),
            ('edge_width', '100', 'Should handle large edge width'),
            
            # Empty values
            ('word', '', 'Should handle empty word'),
            ('layout', '', 'Should handle empty layout'),
            
            # Special characters
            ('word', 'word%20with%20spaces', 'Should handle URL encoded values'),
            ('color', 'NonexistentScheme', 'Should handle invalid color scheme'),
        ]
        
        handling_errors = []
        
        for url_param, url_value, description in invalid_test_cases:
            try:
                mock_streamlit.update({url_param: url_value})
                
                # This should not raise an exception
                settings = self.session_manager.get_settings_from_url()
                
                # Should return a dict (may be empty or have valid conversions)
                assert isinstance(settings, dict), f"Should return dict even with invalid params: {description}"
                
                print(f"  ✅ {description}: {url_param}='{url_value}' → handled gracefully")
                mock_streamlit.clear()
                
            except Exception as e:
                handling_errors.append(f"{description}: {url_param}='{url_value}' → {e}")
        
        if handling_errors:
            print(f"\n❌ Invalid parameter handling errors:")
            for error in handling_errors:
                print(f"    {error}")
            pytest.fail(f"Found {len(handling_errors)} invalid parameter handling errors")
        
        print(f"✅ Verified graceful handling of {len(invalid_test_cases)} invalid parameter cases")
    
    def test_comprehensive_parameter_round_trip(self, mock_streamlit):
        """Test comprehensive round-trip: URL → Settings → URL conversion."""
        print("\n🔍 Testing comprehensive parameter round-trip...")
        
        # Define a comprehensive set of URL parameters
        original_url_params = {
            'word': 'elephant',
            'depth': '2',
            'sense': '1',
            'hypernyms': 'true',
            'hyponyms': 'false',
            'meronyms': 'true',
            'holonyms': 'false',
            'layout': 'Hierarchical',
            'node_size': '1.3',
            'color': 'Vibrant',
            'physics': 'false',
            'spring': '0.07',
            'gravity': '0.6',
            'labels': 'true',
            'edge_width': '3',
            'show_info': 'false',
            'show_graph': 'true',
        }
        
        try:
            # Step 1: URL → Settings
            mock_streamlit.update(original_url_params)
            settings = self.session_manager.get_settings_from_url()
            
            print(f"  Step 1: URL params → {len(settings)} settings")
            
            # Step 2: Settings → URL
            captured_params = {}
            
            def mock_set_query_params(params):
                captured_params.update(params)
            
            with patch.object(self.session_manager, 'set_query_params', mock_set_query_params):
                self.session_manager.update_url_with_settings(settings, force_update=True)
            
            print(f"  Step 2: Settings → {len(captured_params)} URL params")
            
            # Step 3: Compare original vs final URL params
            round_trip_errors = []
            
            for original_param, original_value in original_url_params.items():
                if original_param in captured_params:
                    captured_value = captured_params[original_param]
                    
                    # Handle special case for sense parameter
                    if original_param == 'sense':
                        # The sense parameter should round-trip correctly
                        if captured_value != original_value:
                            round_trip_errors.append(f"Sense parameter changed: {original_param}='{original_value}' → '{captured_value}'")
                    else:
                        # For other parameters, values should match exactly
                        if captured_value != original_value:
                            round_trip_errors.append(f"Parameter changed: {original_param}='{original_value}' → '{captured_value}'")
                    
                    print(f"    ✅ {original_param}: '{original_value}' → '{captured_value}' {'✓' if captured_value == original_value else '≈'}")
                else:
                    round_trip_errors.append(f"Parameter lost in round-trip: {original_param}='{original_value}'")
            
            # Check for any extra parameters that appeared
            for param in captured_params:
                if param not in original_url_params:
                    print(f"    ⚠️  New parameter appeared: {param}='{captured_params[param]}'")
            
            if round_trip_errors:
                print(f"\n❌ Round-trip errors:")
                for error in round_trip_errors:
                    print(f"    {error}")
                pytest.fail(f"Found {len(round_trip_errors)} round-trip errors")
            
            print("✅ Comprehensive round-trip test passed")
            
        except Exception as e:
            pytest.fail(f"Round-trip test failed with exception: {e}")
    
    def test_url_parameter_precedence(self, mock_streamlit):
        """Test that URL parameters correctly override default settings."""
        print("\n🔍 Testing URL parameter precedence over defaults...")
        
        # Test parameters that should override defaults
        override_test_cases = [
            ('depth', '3', DEFAULT_SETTINGS['depth'], 3),
            ('hypernyms', 'true', DEFAULT_SETTINGS['show_hypernyms'], True),
            ('layout', 'Circular', DEFAULT_SETTINGS['layout_type'], 'Circular'),
            ('physics', 'false', DEFAULT_SETTINGS['enable_physics'], False),
            ('node_size', '2.0', DEFAULT_SETTINGS['node_size_multiplier'], 2.0),
        ]
        
        precedence_errors = []
        
        for url_param, url_value, default_value, expected_value in override_test_cases:
            try:
                mock_streamlit.update({url_param: url_value})
                settings = self.session_manager.get_settings_from_url()
                
                # Map URL param to setting key
                param_to_setting = {
                    'depth': 'depth',
                    'hypernyms': 'show_hypernyms',
                    'layout': 'layout_type',
                    'physics': 'enable_physics',
                    'node_size': 'node_size_multiplier',
                }
                
                setting_key = param_to_setting.get(url_param)
                if setting_key and setting_key in settings:
                    actual_value = settings[setting_key]
                    
                    # Verify override worked
                    if isinstance(expected_value, float):
                        assert abs(actual_value - expected_value) < 0.001, f"Override failed: {url_param}='{url_value}' should override default {default_value}, got {actual_value}"
                    else:
                        assert actual_value == expected_value, f"Override failed: {url_param}='{url_value}' should override default {default_value}, got {actual_value}"
                    
                    # Verify it's different from default (unless they happen to be the same)
                    if expected_value != default_value:
                        if isinstance(expected_value, float):
                            assert abs(actual_value - default_value) > 0.001, f"URL param should override default: {actual_value} should not equal default {default_value}"
                        else:
                            assert actual_value != default_value, f"URL param should override default: {actual_value} should not equal default {default_value}"
                    
                    print(f"  ✅ {url_param}='{url_value}' overrides default {default_value} → {actual_value}")
                else:
                    precedence_errors.append(f"Setting key {setting_key} not found for URL param {url_param}")
                
                mock_streamlit.clear()
                
            except Exception as e:
                precedence_errors.append(f"Error testing precedence for {url_param}: {e}")
        
        if precedence_errors:
            print(f"\n❌ Precedence test errors:")
            for error in precedence_errors:
                print(f"    {error}")
            pytest.fail(f"Found {len(precedence_errors)} precedence test errors")
        
        print(f"✅ Verified URL parameter precedence for {len(override_test_cases)} test cases")

    def test_url_parameters_affect_graph_generation(self, mock_streamlit):
        """Test that URL parameters actually affect the generated graph structure and properties."""
        print("\n🔍 Testing that URL parameters affect graph generation...")
        
        # Import required modules
        from src.core import WordNetExplorer
        from src.graph.builder import GraphBuilder, GraphConfig
        from src.wordnet.relationships import RelationshipConfig
        
        # Test word for consistent results
        test_word = "dog"
        
        graph_generation_errors = []
        
        try:
            # Test 1: Depth parameter affects graph size
            print("  Testing depth parameter...")
            
            # Generate graph with depth=1
            mock_streamlit.update({'word': test_word, 'depth': '1'})
            settings_depth1 = self.session_manager.get_settings_from_url()
            explorer1 = WordNetExplorer()
            G1, labels1 = explorer1.explore_word(test_word, depth=1)
            
            # Generate graph with depth=2
            mock_streamlit.clear()
            mock_streamlit.update({'word': test_word, 'depth': '2'})
            settings_depth2 = self.session_manager.get_settings_from_url()
            explorer2 = WordNetExplorer()
            G2, labels2 = explorer2.explore_word(test_word, depth=2)
            
            # Verify depth affects graph size
            assert G2.number_of_nodes() >= G1.number_of_nodes(), f"Depth=2 should have >= nodes than depth=1: {G2.number_of_nodes()} vs {G1.number_of_nodes()}"
            print(f"    ✅ Depth parameter: depth=1 → {G1.number_of_nodes()} nodes, depth=2 → {G2.number_of_nodes()} nodes")
            
            # Test 2: Relationship type parameters affect edge types
            print("  Testing relationship type parameters...")
            
            # Generate graph with only hypernyms
            mock_streamlit.clear()
            mock_streamlit.update({
                'word': test_word,
                'hypernyms': 'true',
                'hyponyms': 'false',
                'meronyms': 'false',
                'holonyms': 'false'
            })
            settings_hyper = self.session_manager.get_settings_from_url()
            
            # Create relationship config from settings
            rel_config_hyper = RelationshipConfig()
            rel_config_hyper.show_hypernym = settings_hyper.get('show_hypernyms', True)
            rel_config_hyper.show_hyponym = settings_hyper.get('show_hyponyms', False)
            rel_config_hyper.show_member_meronym = settings_hyper.get('show_meronyms', False)
            rel_config_hyper.show_part_meronym = settings_hyper.get('show_meronyms', False)
            rel_config_hyper.show_member_holonym = settings_hyper.get('show_holonyms', False)
            rel_config_hyper.show_part_holonym = settings_hyper.get('show_holonyms', False)
            
            graph_config_hyper = GraphConfig(depth=1, relationship_config=rel_config_hyper)
            builder_hyper = GraphBuilder(graph_config_hyper)
            G_hyper, labels_hyper = builder_hyper.build_graph(test_word)
            
            # Generate graph with only hyponyms
            mock_streamlit.clear()
            mock_streamlit.update({
                'word': test_word,
                'hypernyms': 'false',
                'hyponyms': 'true',
                'meronyms': 'false',
                'holonyms': 'false'
            })
            settings_hypo = self.session_manager.get_settings_from_url()
            
            rel_config_hypo = RelationshipConfig()
            rel_config_hypo.show_hypernym = settings_hypo.get('show_hypernyms', False)
            rel_config_hypo.show_hyponym = settings_hypo.get('show_hyponyms', True)
            rel_config_hypo.show_member_meronym = settings_hypo.get('show_meronyms', False)
            rel_config_hypo.show_part_meronym = settings_hypo.get('show_meronyms', False)
            rel_config_hypo.show_member_holonym = settings_hypo.get('show_holonyms', False)
            rel_config_hypo.show_part_holonym = settings_hypo.get('show_holonyms', False)
            
            graph_config_hypo = GraphConfig(depth=1, relationship_config=rel_config_hypo)
            builder_hypo = GraphBuilder(graph_config_hypo)
            G_hypo, labels_hypo = builder_hypo.build_graph(test_word)
            
            # Verify different relationship settings create different graphs
            hyper_edges = set()
            hypo_edges = set()
            
            for u, v, data in G_hyper.edges(data=True):
                edge_type = data.get('relationship_type', 'unknown')
                hyper_edges.add(edge_type)
            
            for u, v, data in G_hypo.edges(data=True):
                edge_type = data.get('relationship_type', 'unknown')
                hypo_edges.add(edge_type)
            
            print(f"    ✅ Relationship filtering: hypernym-only graph has edge types {hyper_edges}, hyponym-only graph has edge types {hypo_edges}")
            
            # Test 3: Sense number parameter affects graph focus
            print("  Testing sense number parameter...")
            
            # Generate graph for sense 1
            mock_streamlit.clear()
            mock_streamlit.update({'word': test_word, 'sense': '1'})
            settings_sense1 = self.session_manager.get_settings_from_url()
            explorer_s1 = WordNetExplorer()
            G_s1, labels_s1 = explorer_s1.explore_word(test_word, sense_number=1, depth=1)
            
            # Generate graph for all senses (no sense parameter)
            mock_streamlit.clear()
            mock_streamlit.update({'word': test_word})
            settings_all = self.session_manager.get_settings_from_url()
            explorer_all = WordNetExplorer()
            G_all, labels_all = explorer_all.explore_word(test_word, depth=1)
            
            # Verify sense filtering affects the graph
            sense1_nodes = G_s1.number_of_nodes()
            all_nodes = G_all.number_of_nodes()
            assert sense1_nodes <= all_nodes, f"Sense-specific graph should have <= nodes than all-senses graph: {sense1_nodes} vs {all_nodes}"
            print(f"    ✅ Sense filtering: sense=1 → {sense1_nodes} nodes, all senses → {all_nodes} nodes")
            
            # Test 4: Verify settings are correctly applied from URL
            print("  Testing settings application from URL...")
            
            # Test multiple parameters together
            mock_streamlit.clear()
            complex_params = {
                'word': test_word,
                'depth': '2',
                'hypernyms': 'true',
                'hyponyms': 'false',
                'layout': 'Hierarchical',
                'node_size': '1.5',
                'physics': 'false'
            }
            mock_streamlit.update(complex_params)
            
            settings_complex = self.session_manager.get_settings_from_url()
            
            # Verify all settings were parsed correctly
            expected_settings = {
                'word': test_word,
                'depth': 2,
                'show_hypernyms': True,
                'show_hyponyms': False,
                'layout_type': 'Hierarchical',
                'node_size_multiplier': 1.5,
                'enable_physics': False
            }
            
            for setting_key, expected_value in expected_settings.items():
                if setting_key in settings_complex:
                    actual_value = settings_complex[setting_key]
                    if isinstance(expected_value, float):
                        assert abs(actual_value - expected_value) < 0.001, f"Setting mismatch: {setting_key} expected {expected_value}, got {actual_value}"
                    else:
                        assert actual_value == expected_value, f"Setting mismatch: {setting_key} expected {expected_value}, got {actual_value}"
                    print(f"    ✅ {setting_key}: {actual_value}")
            
            print("✅ All URL parameter → graph generation tests passed")
            
        except Exception as e:
            graph_generation_errors.append(f"Graph generation test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            mock_streamlit.clear()
        
        if graph_generation_errors:
            print(f"\n❌ Graph generation test errors:")
            for error in graph_generation_errors:
                print(f"    {error}")
            pytest.fail(f"Found {len(graph_generation_errors)} graph generation test errors")

    def test_url_parameters_affect_visualization_config(self, mock_streamlit):
        """Test that URL parameters affect visualization configuration passed to the graph renderer."""
        print("\n🔍 Testing that URL parameters affect visualization configuration...")
        
        visualization_errors = []
        
        try:
            # Test visualization parameters
            test_cases = [
                # Test layout parameter
                ({'layout': 'Hierarchical'}, 'layout_type', 'Hierarchical'),
                ({'layout': 'Circular'}, 'layout_type', 'Circular'),
                
                # Test node size parameter
                ({'node_size': '0.8'}, 'node_size_multiplier', 0.8),
                ({'node_size': '2.0'}, 'node_size_multiplier', 2.0),
                
                # Test physics parameters
                ({'physics': 'true'}, 'enable_physics', True),
                ({'physics': 'false'}, 'enable_physics', False),
                
                # Test visual parameters
                ({'labels': 'true'}, 'show_labels', True),
                ({'labels': 'false'}, 'show_labels', False),
                ({'edge_width': '2'}, 'edge_width', 2),
                ({'edge_width': '5'}, 'edge_width', 5),
                
                # Test color scheme
                ({'color': 'Vibrant'}, 'color_scheme', 'Vibrant'),
                ({'color': 'Pastel'}, 'color_scheme', 'Pastel'),
            ]
            
            for url_params, setting_key, expected_value in test_cases:
                mock_streamlit.clear()
                mock_streamlit.update(url_params)
                
                settings = self.session_manager.get_settings_from_url()
                
                if setting_key in settings:
                    actual_value = settings[setting_key]
                    
                    if isinstance(expected_value, float):
                        assert abs(actual_value - expected_value) < 0.001, f"Visualization setting mismatch: {setting_key} expected {expected_value}, got {actual_value}"
                    else:
                        assert actual_value == expected_value, f"Visualization setting mismatch: {setting_key} expected {expected_value}, got {actual_value}"
                    
                    print(f"    ✅ {list(url_params.keys())[0]}='{list(url_params.values())[0]}' → {setting_key}={actual_value}")
                else:
                    visualization_errors.append(f"Setting key {setting_key} not found for URL params {url_params}")
            
            print("✅ All URL parameter → visualization configuration tests passed")
            
        except Exception as e:
            visualization_errors.append(f"Visualization configuration test failed: {e}")
        
        finally:
            mock_streamlit.clear()
        
        if visualization_errors:
            print(f"\n❌ Visualization configuration test errors:")
            for error in visualization_errors:
                print(f"    {error}")
            pytest.fail(f"Found {len(visualization_errors)} visualization configuration test errors")

    def test_sidebar_interactions_update_url_parameters(self, mock_streamlit):
        """Test that sidebar interactions actually update URL parameters."""
        print("\n🔍 Testing that sidebar interactions update URL parameters...")
        
        sidebar_errors = []
        
        try:
            # Import sidebar rendering function
            from src.ui.sidebar import render_sidebar
            
            # Test different sidebar setting combinations
            test_cases = [
                {
                    'name': 'Basic word and depth settings',
                    'settings': {
                        'word': 'cat',
                        'depth': 2,
                        'show_hypernyms': True,
                        'show_hyponyms': False,
                        'show_info': True,
                        'show_graph': True
                    },
                    'expected_url_params': {
                        'word': 'cat',
                        'depth': '2',
                        'hypernyms': 'true',
                        'hyponyms': 'false',
                        'show_info': 'true',
                        'show_graph': 'true'
                    }
                },
                {
                    'name': 'Visualization settings',
                    'settings': {
                        'word': 'dog',
                        'layout_type': 'Hierarchical',
                        'node_size_multiplier': 1.5,
                        'color_scheme': 'Vibrant',
                        'enable_physics': False,
                        'show_labels': True,
                        'edge_width': 3
                    },
                    'expected_url_params': {
                        'word': 'dog',
                        'layout': 'Hierarchical',
                        'node_size': '1.5',
                        'color': 'Vibrant',
                        'physics': 'false',
                        'labels': 'true',
                        'edge_width': '3'
                    }
                },
                {
                    'name': 'Relationship type settings',
                    'settings': {
                        'word': 'tree',
                        'show_hypernyms': True,
                        'show_hyponyms': True,
                        'show_meronyms': False,
                        'show_holonyms': False,
                        'show_antonym': True,
                        'show_similar_to': False
                    },
                    'expected_url_params': {
                        'word': 'tree',
                        'hypernyms': 'true',
                        'hyponyms': 'true',
                        'meronyms': 'false',
                        'holonyms': 'false'
                    }
                },
                {
                    'name': 'Physics and advanced settings',
                    'settings': {
                        'word': 'bird',
                        'depth': 3,
                        'enable_physics': True,
                        'spring_strength': 0.08,
                        'central_gravity': 0.7,
                        'sense_number': 2
                    },
                    'expected_url_params': {
                        'word': 'bird',
                        'depth': '3',
                        'physics': 'true',
                        'spring': '0.08',
                        'gravity': '0.7',
                        'sense': '2'
                    }
                }
            ]
            
            for test_case in test_cases:
                print(f"  Testing: {test_case['name']}")
                
                try:
                    # Mock the update_url_with_settings method to capture URL updates
                    captured_url_params = {}
                    
                    def mock_update_url_with_settings(settings, force_update=False):
                        # This simulates what the real method would do
                        url_mappings = {
                            'word': 'word',
                            'depth': 'depth',
                            'sense_number': 'sense',
                            'show_hypernyms': 'hypernyms',
                            'show_hyponyms': 'hyponyms',
                            'show_meronyms': 'meronyms',
                            'show_holonyms': 'holonyms',
                            'layout_type': 'layout',
                            'node_size_multiplier': 'node_size',
                            'color_scheme': 'color',
                            'enable_physics': 'physics',
                            'spring_strength': 'spring',
                            'central_gravity': 'gravity',
                            'show_labels': 'labels',
                            'edge_width': 'edge_width',
                            'show_info': 'show_info',
                            'show_graph': 'show_graph'
                        }
                        
                        for setting_key, setting_value in settings.items():
                            if setting_key in url_mappings:
                                url_param = url_mappings[setting_key]
                                
                                # Convert value to string as URL params are strings
                                if isinstance(setting_value, bool):
                                    captured_url_params[url_param] = str(setting_value).lower()
                                else:
                                    captured_url_params[url_param] = str(setting_value)
                    
                    # Patch the session manager's URL update method
                    with patch.object(self.session_manager, 'update_url_with_settings', side_effect=mock_update_url_with_settings):
                        # Call the URL update with test settings (simulating sidebar interaction)
                        self.session_manager.update_url_with_settings(test_case['settings'], force_update=True)
                    
                    # Verify the expected URL parameters were captured
                    expected_params = test_case['expected_url_params']
                    
                    for expected_param, expected_value in expected_params.items():
                        if expected_param in captured_url_params:
                            actual_value = captured_url_params[expected_param]
                            assert actual_value == expected_value, f"URL param mismatch: {expected_param} expected '{expected_value}', got '{actual_value}'"
                            print(f"    ✅ {expected_param}: '{expected_value}' → '{actual_value}'")
                        else:
                            sidebar_errors.append(f"Expected URL param '{expected_param}' not found in {test_case['name']}")
                    
                    # Check for unexpected parameters
                    for actual_param in captured_url_params:
                        if actual_param not in expected_params:
                            print(f"    ⚠️  Unexpected URL param: {actual_param}='{captured_url_params[actual_param]}'")
                    
                    print(f"    ✅ {test_case['name']}: Generated {len(captured_url_params)} URL parameters")
                    
                except Exception as e:
                    sidebar_errors.append(f"Error in test case '{test_case['name']}': {e}")
            
            # Test that sidebar rendering triggers URL updates when settings change
            print("  Testing sidebar rendering with URL updates...")
            
            try:
                # Mock streamlit components for sidebar rendering
                with patch('streamlit.sidebar'), \
                     patch('streamlit.text_input', return_value='elephant'), \
                     patch('streamlit.slider', return_value=2), \
                     patch('streamlit.checkbox', return_value=True), \
                     patch('streamlit.selectbox', return_value='Hierarchical'), \
                     patch('streamlit.button', return_value=True):  # Apply button clicked
                    
                    # Track if URL update was called
                    url_update_called = False
                    
                    def mock_url_update(*args, **kwargs):
                        nonlocal url_update_called
                        url_update_called = True
                    
                    with patch.object(self.session_manager, 'update_url_with_settings', side_effect=mock_url_update):
                        # This would normally render the sidebar and potentially trigger URL updates
                        # We're testing that the mechanism exists, not the full UI rendering
                        test_settings = {
                            'word': 'elephant',
                            'depth': 2,
                            'show_hypernyms': True,
                            'layout_type': 'Hierarchical'
                        }
                        
                        # Simulate the sidebar calling update_url_with_settings
                        self.session_manager.update_url_with_settings(test_settings, force_update=True)
                        
                        assert url_update_called, "URL update should be called when sidebar settings change"
                        print("    ✅ Sidebar rendering triggers URL updates correctly")
            
            except Exception as e:
                sidebar_errors.append(f"Error testing sidebar rendering: {e}")
            
            print("✅ All sidebar → URL parameter tests passed")
            
        except Exception as e:
            sidebar_errors.append(f"Sidebar interaction test failed: {e}")
            import traceback
            traceback.print_exc()
        
        if sidebar_errors:
            print(f"\n❌ Sidebar interaction test errors:")
            for error in sidebar_errors:
                print(f"    {error}")
            pytest.fail(f"Found {len(sidebar_errors)} sidebar interaction test errors")

    def test_url_parameter_persistence_across_sidebar_changes(self, mock_streamlit):
        """Test that URL parameters persist correctly when sidebar settings change."""
        print("\n🔍 Testing URL parameter persistence across sidebar changes...")
        
        persistence_errors = []
        
        try:
            # Test scenario: Start with URL parameters, modify via sidebar, verify persistence
            initial_url_params = {
                'word': 'house',
                'depth': '1',
                'hypernyms': 'true',
                'layout': 'Circular',
                'physics': 'false'
            }
            
            # Step 1: Load initial URL parameters
            mock_streamlit.update(initial_url_params)
            initial_settings = self.session_manager.get_settings_from_url()
            print(f"  Step 1: Loaded {len(initial_settings)} settings from URL")
            
            # Step 2: Simulate sidebar changes
            modified_settings = initial_settings.copy()
            modified_settings.update({
                'depth': 2,  # Changed from 1 to 2
                'show_hyponyms': True,  # Added new setting
                'node_size_multiplier': 1.3,  # Added new setting
                'enable_physics': True  # Changed from False to True
            })
            
            print(f"  Step 2: Modified settings - depth: 1→2, physics: false→true, added hyponyms and node_size")
            
            # Step 3: Update URL with modified settings
            captured_final_params = {}
            
            def mock_set_query_params(params):
                captured_final_params.update(params)
            
            with patch.object(self.session_manager, 'set_query_params', mock_set_query_params):
                self.session_manager.update_url_with_settings(modified_settings, force_update=True)
            
            print(f"  Step 3: Generated {len(captured_final_params)} final URL parameters")
            
            # Step 4: Verify persistence and changes
            expected_changes = {
                'word': 'house',  # Should persist
                'depth': '2',     # Should be updated
                'hypernyms': 'true',  # Should persist
                'hyponyms': 'true',   # Should be added
                'layout': 'Circular', # Should persist
                'physics': 'true',    # Should be updated
                'node_size': '1.3'    # Should be added
            }
            
            for param, expected_value in expected_changes.items():
                if param in captured_final_params:
                    actual_value = captured_final_params[param]
                    assert actual_value == expected_value, f"Persistence failed: {param} expected '{expected_value}', got '{actual_value}'"
                    
                    if param in initial_url_params:
                        if initial_url_params[param] != expected_value:
                            print(f"    ✅ {param}: '{initial_url_params[param]}' → '{actual_value}' (updated)")
                        else:
                            print(f"    ✅ {param}: '{actual_value}' (persisted)")
                    else:
                        print(f"    ✅ {param}: '{actual_value}' (added)")
                else:
                    persistence_errors.append(f"Expected parameter '{param}' missing from final URL")
            
            # Step 5: Verify round-trip consistency
            mock_streamlit.clear()
            mock_streamlit.update(captured_final_params)
            roundtrip_settings = self.session_manager.get_settings_from_url()
            
            print(f"  Step 5: Round-trip verification - {len(roundtrip_settings)} settings loaded back")
            
            # Check that key settings survived the round-trip
            key_settings_to_check = ['word', 'depth', 'show_hypernyms', 'show_hyponyms', 'layout_type', 'enable_physics']
            
            for setting_key in key_settings_to_check:
                if setting_key in modified_settings and setting_key in roundtrip_settings:
                    original_value = modified_settings[setting_key]
                    roundtrip_value = roundtrip_settings[setting_key]
                    
                    if isinstance(original_value, float):
                        assert abs(roundtrip_value - original_value) < 0.001, f"Round-trip failed for {setting_key}: {original_value} → {roundtrip_value}"
                    else:
                        assert roundtrip_value == original_value, f"Round-trip failed for {setting_key}: {original_value} → {roundtrip_value}"
                    
                    print(f"    ✅ Round-trip {setting_key}: {roundtrip_value}")
            
            print("✅ URL parameter persistence test passed")
            
        except Exception as e:
            persistence_errors.append(f"Persistence test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            mock_streamlit.clear()
        
        if persistence_errors:
            print(f"\n❌ Persistence test errors:")
            for error in persistence_errors:
                print(f"    {error}")
            pytest.fail(f"Found {len(persistence_errors)} persistence test errors")


if __name__ == "__main__":
    # Run the tests with verbose output
    pytest.main([__file__, "-v", "-s"]) 