#!/usr/bin/env python3
"""
QWAMOS Claude Controller - Anthropic API Integration

Manages Claude AI service with Tor routing for privacy.
Advanced reasoning and coding assistance.
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Claude')

class ClaudeController:
    """Controller for Claude AI service (Anthropic API)"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4.5"):
        """
        Initialize Claude controller

        Args:
            api_key: Anthropic API key (sk-ant-...)
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
        self.api_version = "2023-06-01"

        # Tor proxy configuration
        self.tor_socks_proxy = "socks5h://127.0.0.1:9050"
        self.use_tor = True

        # Request configuration
        self.max_tokens = 4096
        self.temperature = 1.0
        self.timeout = 60

        # Conversation history
        self.history = []

        # Usage tracking
        self.usage = {
            'requests': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0,
            'estimated_cost': 0.0
        }

        logger.info(f"Claude controller initialized (model: {self.model})")

    def query(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Query Claude AI

        Args:
            prompt: User prompt/query
            context: Optional context (conversation history, system prompt, etc.)

        Returns:
            str: Claude's response
        """
        try:
            # Build messages
            messages = self._build_messages(prompt, context)

            # Build system prompt
            system_prompt = self._get_system_prompt(context)

            # Prepare request
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "content-type": "application/json"
            }

            payload = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": messages
            }

            if system_prompt:
                payload["system"] = system_prompt

            # Configure proxy for Tor
            proxies = {}
            if self.use_tor:
                proxies = {
                    'http': self.tor_socks_proxy,
                    'https': self.tor_socks_proxy
                }

            # Make API request
            logger.info("Sending request to Claude API via Tor...")

            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                proxies=proxies,
                timeout=self.timeout
            )

            # Check response
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return f"Error: Claude API returned {response.status_code}"

            # Parse response
            data = response.json()

            # Extract answer
            answer = data['content'][0]['text']

            # Update usage tracking
            self._update_usage(data.get('usage', {}))

            # Add to history
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt,
                'response': answer,
                'model': self.model
            })

            logger.info("Response received successfully")
            return answer

        except requests.exceptions.ProxyError as e:
            logger.error(f"Tor proxy error: {e}")
            return "Error: Cannot connect to Tor proxy. Ensure Tor is running on port 9050."

        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            return "Error: Request timed out. Try again."

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return f"Error: {e}"

    def _build_messages(self, prompt: str, context: Optional[Dict]) -> List[Dict]:
        """Build messages array for API request"""
        messages = []

        # Add conversation history if provided
        if context and 'history' in context:
            for entry in context['history']:
                messages.append({'role': 'user', 'content': entry['prompt']})
                messages.append({'role': 'assistant', 'content': entry['response']})

        # Add current prompt
        messages.append({'role': 'user', 'content': prompt})

        return messages

    def _get_system_prompt(self, context: Optional[Dict]) -> Optional[str]:
        """Get system prompt from context or use default"""
        if context and 'system_prompt' in context:
            return context['system_prompt']

        # Default system prompt for QWAMOS
        return """You are Claude, an AI assistant integrated into QWAMOS (Qubes Whonix Advanced Mobile Operating System).

You provide advanced reasoning, coding assistance, and technical guidance for:
- Software development and debugging
- Security analysis and best practices
- System architecture and design
- Research and information synthesis
- Problem-solving and decision-making

You have access to knowledge up to early 2024. You are thoughtful, precise, and helpful.

Important: You are running on a privacy-focused OS. All API requests are routed through Tor for anonymity."""

    def _update_usage(self, usage_data: Dict):
        """Update token usage and cost tracking"""
        if not usage_data:
            return

        input_tokens = usage_data.get('input_tokens', 0)
        output_tokens = usage_data.get('output_tokens', 0)

        self.usage['requests'] += 1
        self.usage['input_tokens'] += input_tokens
        self.usage['output_tokens'] += output_tokens
        self.usage['total_tokens'] += (input_tokens + output_tokens)

        # Calculate cost (Claude Sonnet 4.5 pricing as of 2024)
        # Input: $0.003/1K tokens, Output: $0.015/1K tokens
        input_cost = (input_tokens / 1000) * 0.003
        output_cost = (output_tokens / 1000) * 0.015
        self.usage['estimated_cost'] += (input_cost + output_cost)

        logger.info(f"Tokens used: {input_tokens} input, {output_tokens} output")
        logger.info(f"Total cost: ${self.usage['estimated_cost']:.4f}")

    def test_connection(self) -> bool:
        """
        Test connection to Claude API (via Tor)

        Returns:
            bool: True if connection successful
        """
        try:
            # Simple test query
            test_prompt = "Respond with just 'OK' if you can read this."

            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": self.api_version,
                "content-type": "application/json"
            }

            payload = {
                "model": self.model,
                "max_tokens": 10,
                "messages": [{"role": "user", "content": test_prompt}]
            }

            proxies = {}
            if self.use_tor:
                proxies = {
                    'http': self.tor_socks_proxy,
                    'https': self.tor_socks_proxy
                }

            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                proxies=proxies,
                timeout=30
            )

            if response.status_code == 200:
                logger.info("✅ Claude API connection test passed")
                return True
            else:
                logger.error(f"API test failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get current status

        Returns:
            dict: Status information
        """
        return {
            'model': self.model,
            'tor_enabled': self.use_tor,
            'queries': len(self.history),
            'usage': self.usage.copy(),
            'api_key_set': bool(self.api_key and len(self.api_key) > 10)
        }

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get detailed usage statistics

        Returns:
            dict: Usage statistics
        """
        return self.usage.copy()

    def clear_history(self):
        """Clear conversation history"""
        self.history = []
        logger.info("Conversation history cleared")

    def set_model(self, model: str):
        """Change Claude model"""
        self.model = model
        logger.info(f"Model changed to: {model}")

    def enable_tor(self):
        """Enable Tor routing"""
        self.use_tor = True
        logger.info("Tor routing enabled")

    def disable_tor(self):
        """Disable Tor routing (NOT RECOMMENDED)"""
        self.use_tor = False
        logger.warning("⚠️  Tor routing disabled - API requests will expose your IP")

    def sanitize_request(self, prompt: str) -> str:
        """
        Sanitize request to remove sensitive information

        Args:
            prompt: Original prompt

        Returns:
            str: Sanitized prompt
        """
        # Remove common sensitive patterns
        import re

        sanitized = prompt

        # Remove IP addresses
        sanitized = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]', sanitized)

        # Remove API keys (common patterns)
        sanitized = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]', sanitized)
        sanitized = re.sub(r'ghp_[a-zA-Z0-9]{36}', '[GITHUB_TOKEN_REDACTED]', sanitized)

        # Remove email addresses
        sanitized = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', sanitized)

        # Remove potential passwords (password= or pwd= patterns)
        sanitized = re.sub(r'(password|pwd|pass)\s*[=:]\s*\S+', r'\1=[PASSWORD_REDACTED]', sanitized, flags=re.IGNORECASE)

        if sanitized != prompt:
            logger.warning("⚠️  Sensitive information detected and redacted from prompt")

        return sanitized


# === CLI Interface ===

def main():
    """CLI entry point for Claude controller"""
    import argparse

    parser = argparse.ArgumentParser(description='QWAMOS Claude AI Controller')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query Claude AI')
    query_parser.add_argument('prompt', help='Your query/question')
    query_parser.add_argument('--api-key', required=True, help='Anthropic API key')
    query_parser.add_argument('--model', default='claude-sonnet-4.5', help='Model to use')
    query_parser.add_argument('--no-tor', action='store_true', help='Disable Tor (not recommended)')

    # Test command
    test_parser = subparsers.add_parser('test', help='Test Claude API connection')
    test_parser.add_argument('--api-key', required=True, help='Anthropic API key')
    test_parser.add_argument('--no-tor', action='store_true', help='Disable Tor')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show usage statistics')
    status_parser.add_argument('--api-key', required=True, help='Anthropic API key')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize controller
    controller = ClaudeController(args.api_key)

    if hasattr(args, 'no_tor') and args.no_tor:
        controller.disable_tor()

    if hasattr(args, 'model') and args.model:
        controller.set_model(args.model)

    # Execute command
    if args.command == 'query':
        # Sanitize prompt
        sanitized_prompt = controller.sanitize_request(args.prompt)

        response = controller.query(sanitized_prompt)
        print(f"\n{response}\n")

    elif args.command == 'test':
        print("Testing Claude API connection...")
        if controller.test_connection():
            print("✅ Connection successful")
            return 0
        else:
            print("❌ Connection failed")
            return 1

    elif args.command == 'status':
        status = controller.get_status()
        print("\n=== Claude AI Status ===\n")
        print(f"Model: {status['model']}")
        print(f"Tor Enabled: {status['tor_enabled']}")
        print(f"Queries: {status['queries']}")
        print(f"Total Tokens: {status['usage']['total_tokens']}")
        print(f"Estimated Cost: ${status['usage']['estimated_cost']:.4f}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
