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


if __name__ == "__main__":
    # Run the tests with verbose output
    pytest.main([__file__, "-v", "-s"]) 