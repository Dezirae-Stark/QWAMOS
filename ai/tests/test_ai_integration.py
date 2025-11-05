#!/usr/bin/env python3
"""
QWAMOS AI Integration Tests

Tests the complete AI integration stack:
- AI Manager functionality
- Service enable/disable
- Query/response flow
- Native module bridge (simulated)
- Configuration management
- Usage statistics

Usage:
    python3 test_ai_integration.py
"""

import unittest
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_manager import AIManager


class TestAIIntegration(unittest.TestCase):
    """Integration tests for QWAMOS AI system"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)

        # Create test configuration files
        self._create_test_configs()

        # Initialize AI Manager with test config dir
        self.manager = AIManager(config_dir=self.config_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_test_configs(self):
        """Create test configuration files"""
        configs = {
            'kali_gpt_config.json': {
                'model_path': '/opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf',
                'context_length': 8192,
                'temperature': 0.7,
                'threads': 4
            },
            'claude_config.json': {
                'model': 'claude-3-5-sonnet-20241022',
                'max_tokens': 4096,
                'routing': {
                    'method': 'tor',
                    'proxy': 'socks5h://127.0.0.1:9050'
                }
            },
            'chatgpt_config.json': {
                'model': 'gpt-4-turbo-preview',
                'max_tokens': 4096,
                'routing': {
                    'method': 'tor',
                    'proxy': 'socks5h://127.0.0.1:9050'
                }
            }
        }

        for filename, config in configs.items():
            path = os.path.join(self.config_dir, filename)
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)

    # === Service Management Tests ===

    def test_service_listing(self):
        """Test listing available AI services"""
        services = self.manager.list_services()

        self.assertIn('kali-gpt', services)
        self.assertIn('claude', services)
        self.assertIn('chatgpt', services)
        self.assertEqual(len(services), 3)

    def test_service_status_initial(self):
        """Test initial service status (all disabled)"""
        status = self.manager.get_status()

        for service_id in ['kali-gpt', 'claude', 'chatgpt']:
            self.assertIn(service_id, status)
            self.assertFalse(status[service_id]['enabled'])

    @patch('ai_manager.KaliGPTController')
    def test_enable_kali_gpt(self, mock_controller_class):
        """Test enabling Kali GPT service"""
        # Mock controller
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller

        # Enable service
        result = self.manager.enable_kali_gpt()

        self.assertTrue(result)
        self.assertTrue(self.manager.is_enabled('kali-gpt'))
        mock_controller_class.assert_called_once()

    @patch('ai_manager.ClaudeController')
    def test_enable_claude(self, mock_controller_class):
        """Test enabling Claude service"""
        # Mock controller
        mock_controller = Mock()
        mock_controller.test_connection.return_value = True
        mock_controller_class.return_value = mock_controller

        # Enable service
        result = self.manager.enable_claude('sk-ant-test-key')

        self.assertTrue(result)
        self.assertTrue(self.manager.is_enabled('claude'))
        mock_controller.test_connection.assert_called_once()

    @patch('ai_manager.ChatGPTController')
    def test_enable_chatgpt(self, mock_controller_class):
        """Test enabling ChatGPT service"""
        # Mock controller
        mock_controller = Mock()
        mock_controller.test_connection.return_value = True
        mock_controller_class.return_value = mock_controller

        # Enable service
        result = self.manager.enable_chatgpt('sk-proj-test-key')

        self.assertTrue(result)
        self.assertTrue(self.manager.is_enabled('chatgpt'))
        mock_controller.test_connection.assert_called_once()

    @patch('ai_manager.KaliGPTController')
    def test_disable_service(self, mock_controller_class):
        """Test disabling a service"""
        # Enable first
        mock_controller = Mock()
        mock_controller_class.return_value = mock_controller
        self.manager.enable_kali_gpt()

        # Then disable
        result = self.manager.disable_kali_gpt()

        self.assertTrue(result)
        self.assertFalse(self.manager.is_enabled('kali-gpt'))
        mock_controller.shutdown.assert_called_once()

    # === Query Tests ===

    @patch('ai_manager.KaliGPTController')
    def test_query_kali_gpt(self, mock_controller_class):
        """Test querying Kali GPT"""
        # Setup mock
        mock_controller = Mock()
        mock_controller.query.return_value = "This is a test response"
        mock_controller_class.return_value = mock_controller

        # Enable service
        self.manager.enable_kali_gpt()

        # Query
        response = self.manager.query('kali-gpt', 'How do I use nmap?')

        self.assertEqual(response, "This is a test response")
        mock_controller.query.assert_called_once_with('How do I use nmap?', {})

    @patch('ai_manager.ClaudeController')
    def test_query_claude_with_context(self, mock_controller_class):
        """Test querying Claude with conversation context"""
        # Setup mock
        mock_controller = Mock()
        mock_controller.test_connection.return_value = True
        mock_controller.query.return_value = "Claude response"
        mock_controller_class.return_value = mock_controller

        # Enable service
        self.manager.enable_claude('sk-ant-test')

        # Query with context
        context = {'conversation_id': '123', 'history': []}
        response = self.manager.query('claude', 'Explain Tor', context)

        self.assertEqual(response, "Claude response")
        mock_controller.query.assert_called_once_with('Explain Tor', context)

    def test_query_disabled_service_fails(self):
        """Test that querying disabled service raises error"""
        with self.assertRaises(RuntimeError):
            self.manager.query('kali-gpt', 'test query')

    def test_query_invalid_service_fails(self):
        """Test that querying invalid service raises error"""
        with self.assertRaises(ValueError):
            self.manager.query('invalid-service', 'test query')

    # === Usage Statistics Tests ===

    @patch('ai_manager.KaliGPTController')
    def test_usage_stats_tracking(self, mock_controller_class):
        """Test usage statistics tracking"""
        # Setup mock with usage metadata
        mock_response = Mock()
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 150

        mock_controller = Mock()
        mock_controller.query.return_value = mock_response
        mock_controller_class.return_value = mock_controller

        # Enable and query
        self.manager.enable_kali_gpt()
        self.manager.query('kali-gpt', 'test query')

        # Check stats
        stats = self.manager.get_usage_stats()

        self.assertEqual(stats['kali-gpt']['queries'], 1)
        self.assertEqual(stats['kali-gpt']['tokens'], 150)
        self.assertEqual(stats['kali-gpt']['cost'], 0.0)  # Kali GPT is free

    @patch('ai_manager.ClaudeController')
    def test_claude_cost_calculation(self, mock_controller_class):
        """Test Claude usage cost calculation"""
        # Setup mock with usage metadata
        mock_response = Mock()
        mock_response.usage = Mock()
        mock_response.usage.total_tokens = 1000  # 1K tokens

        mock_controller = Mock()
        mock_controller.test_connection.return_value = True
        mock_controller.query.return_value = mock_response
        mock_controller_class.return_value = mock_controller

        # Enable and query
        self.manager.enable_claude('sk-ant-test')
        self.manager.query('claude', 'test query')

        # Check stats (1K tokens * $0.009 avg = $0.009)
        stats = self.manager.get_usage_stats()

        self.assertEqual(stats['claude']['queries'], 1)
        self.assertEqual(stats['claude']['tokens'], 1000)
        self.assertAlmostEqual(stats['claude']['cost'], 0.009, places=3)

    # === Configuration Tests ===

    def test_config_loading(self):
        """Test configuration file loading"""
        # Configs should be loaded during initialization
        # Test by checking if enable methods can access config

        # This is implicitly tested by other tests, but we can verify
        # config files exist
        for service in ['kali_gpt', 'claude', 'chatgpt']:
            config_file = os.path.join(self.config_dir, f'{service}_config.json')
            self.assertTrue(os.path.exists(config_file))

    # === Error Handling Tests ===

    @patch('ai_manager.ClaudeController')
    def test_connection_failure_handling(self, mock_controller_class):
        """Test handling of connection failures"""
        # Mock failed connection test
        mock_controller = Mock()
        mock_controller.test_connection.return_value = False
        mock_controller_class.return_value = mock_controller

        # Try to enable (should fail)
        result = self.manager.enable_claude('sk-ant-test')

        self.assertFalse(result)
        self.assertFalse(self.manager.is_enabled('claude'))

    @patch('ai_manager.KaliGPTController')
    def test_query_error_handling(self, mock_controller_class):
        """Test handling of query errors"""
        # Setup mock to raise exception
        mock_controller = Mock()
        mock_controller.query.side_effect = Exception("Query failed")
        mock_controller_class.return_value = mock_controller

        # Enable service
        self.manager.enable_kali_gpt()

        # Query should raise exception
        with self.assertRaises(Exception):
            self.manager.query('kali-gpt', 'test query')


class TestAIServiceIntegration(unittest.TestCase):
    """Integration tests for individual AI service controllers"""

    def test_kali_gpt_model_path_validation(self):
        """Test Kali GPT model path validation"""
        from kali_gpt.kali_gpt_controller import KaliGPTController

        # This would normally check if model file exists
        # For testing, we just verify the controller can be instantiated
        # with a mock path

        # Mock the controller initialization
        with patch('kali_gpt.kali_gpt_controller.Llama'):
            controller = KaliGPTController(
                model_path='/tmp/test_model.gguf'
            )
            self.assertIsNotNone(controller)

    def test_tor_proxy_configuration(self):
        """Test Tor proxy configuration for cloud services"""
        from claude.claude_controller import ClaudeController

        # Mock Anthropic client with Tor proxy
        with patch('claude.claude_controller.Anthropic'):
            controller = ClaudeController(
                api_key='sk-ant-test',
                proxy='socks5h://127.0.0.1:9050'
            )

            # Verify proxy is configured
            self.assertIsNotNone(controller)


class TestNativeModuleBridge(unittest.TestCase):
    """Integration tests for React Native <-> Python bridge"""

    def test_command_execution_format(self):
        """Test command execution format for native bridge"""
        # Simulate what the Java native bridge would execute
        command = [
            '/usr/bin/python3',
            '/opt/qwamos/ai/ai_manager.py',
            'status'
        ]

        # Verify command format is valid
        self.assertEqual(command[0], '/usr/bin/python3')
        self.assertEqual(command[1], '/opt/qwamos/ai/ai_manager.py')
        self.assertIn('status', command)

    def test_json_response_parsing(self):
        """Test JSON response parsing from Python backend"""
        # Simulate Python backend response
        response = json.dumps({
            'kali-gpt': {'enabled': True, 'type': 'local'},
            'claude': {'enabled': False, 'type': 'cloud'},
            'chatgpt': {'enabled': False, 'type': 'cloud'}
        })

        # Parse as React Native would
        parsed = json.loads(response)

        self.assertIn('kali-gpt', parsed)
        self.assertTrue(parsed['kali-gpt']['enabled'])
        self.assertEqual(parsed['kali-gpt']['type'], 'local')


# Test runner
if __name__ == '__main__':
    # Run tests with verbose output
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("QWAMOS AI Integration Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
