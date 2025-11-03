#!/usr/bin/env python3
"""
QWAMOS ChatGPT Controller - OpenAI API Integration

Manages ChatGPT service with Tor routing for privacy.
General purpose AI assistance and coding help.
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
logger = logging.getLogger('ChatGPT')

class ChatGPTController:
    """Controller for ChatGPT service (OpenAI API)"""

    def __init__(self, api_key: str, model: str = "gpt-4-turbo"):
        """
        Initialize ChatGPT controller

        Args:
            api_key: OpenAI API key (sk-proj-...)
            model: GPT model to use
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"

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
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0,
            'estimated_cost': 0.0
        }

        logger.info(f"ChatGPT controller initialized (model: {self.model})")

    def query(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Query ChatGPT

        Args:
            prompt: User prompt/query
            context: Optional context (conversation history, system prompt, etc.)

        Returns:
            str: ChatGPT's response
        """
        try:
            # Build messages
            messages = self._build_messages(prompt, context)

            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }

            # Add function calling if provided
            if context and 'functions' in context:
                payload['functions'] = context['functions']

            # Configure proxy for Tor
            proxies = {}
            if self.use_tor:
                proxies = {
                    'http': self.tor_socks_proxy,
                    'https': self.tor_socks_proxy
                }

            # Make API request
            logger.info("Sending request to OpenAI API via Tor...")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                proxies=proxies,
                timeout=self.timeout
            )

            # Check response
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return f"Error: OpenAI API returned {response.status_code}"

            # Parse response
            data = response.json()

            # Extract answer
            answer = data['choices'][0]['message']['content']

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

        # Add system prompt if provided
        system_prompt = self._get_system_prompt(context)
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})

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
        return """You are ChatGPT, an AI assistant integrated into QWAMOS (Qubes Whonix Advanced Mobile Operating System).

You provide helpful, accurate, and comprehensive assistance with:
- General knowledge and questions
- Coding and software development
- Writing and content creation
- Problem-solving and brainstorming
- Learning and education
- Creative tasks

You are running on a privacy-focused operating system. All API requests are routed through Tor for anonymity.

Be helpful, clear, and concise. Format code with markdown code blocks."""

    def _update_usage(self, usage_data: Dict):
        """Update token usage and cost tracking"""
        if not usage_data:
            return

        prompt_tokens = usage_data.get('prompt_tokens', 0)
        completion_tokens = usage_data.get('completion_tokens', 0)
        total_tokens = usage_data.get('total_tokens', 0)

        self.usage['requests'] += 1
        self.usage['prompt_tokens'] += prompt_tokens
        self.usage['completion_tokens'] += completion_tokens
        self.usage['total_tokens'] += total_tokens

        # Calculate cost (GPT-4 Turbo pricing as of 2024)
        # Input: $0.01/1K tokens, Output: $0.03/1K tokens
        input_cost = (prompt_tokens / 1000) * 0.01
        output_cost = (completion_tokens / 1000) * 0.03
        self.usage['estimated_cost'] += (input_cost + output_cost)

        logger.info(f"Tokens used: {prompt_tokens} prompt, {completion_tokens} completion")
        logger.info(f"Total cost: ${self.usage['estimated_cost']:.4f}")

    def query_with_vision(self, prompt: str, image_url: str) -> str:
        """
        Query ChatGPT with vision (image analysis)

        Args:
            prompt: Text prompt about the image
            image_url: URL or base64 data URI of image

        Returns:
            str: ChatGPT's response
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Build message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ]

            payload = {
                "model": "gpt-4-vision-preview",
                "messages": messages,
                "max_tokens": 1000
            }

            proxies = {}
            if self.use_tor:
                proxies = {
                    'http': self.tor_socks_proxy,
                    'https': self.tor_socks_proxy
                }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                proxies=proxies,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return f"Error: {response.status_code} - {response.text}"

            data = response.json()
            return data['choices'][0]['message']['content']

        except Exception as e:
            logger.error(f"Vision query failed: {e}")
            return f"Error: {e}"

    def test_connection(self) -> bool:
        """
        Test connection to OpenAI API (via Tor)

        Returns:
            bool: True if connection successful
        """
        try:
            # Simple test query
            test_prompt = "Respond with just 'OK' if you can read this."

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": test_prompt}],
                "max_tokens": 10
            }

            proxies = {}
            if self.use_tor:
                proxies = {
                    'http': self.tor_socks_proxy,
                    'https': self.tor_socks_proxy
                }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                proxies=proxies,
                timeout=30
            )

            if response.status_code == 200:
                logger.info("✅ OpenAI API connection test passed")
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
        """Change GPT model"""
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

    def generate_code(self, description: str, language: str = "python") -> str:
        """
        Generate code based on description

        Args:
            description: What the code should do
            language: Programming language

        Returns:
            str: Generated code
        """
        prompt = f"Write {language} code that {description}. Provide only the code with comments, no explanation."

        return self.query(prompt)

    def explain_code(self, code: str) -> str:
        """
        Explain what code does

        Args:
            code: Code to explain

        Returns:
            str: Explanation
        """
        prompt = f"Explain what this code does:\n\n```\n{code}\n```"

        return self.query(prompt)

    def debug_code(self, code: str, error: Optional[str] = None) -> str:
        """
        Help debug code

        Args:
            code: Code with bug
            error: Error message (if any)

        Returns:
            str: Debugging suggestions
        """
        prompt = f"Debug this code:\n\n```\n{code}\n```"

        if error:
            prompt += f"\n\nError message:\n{error}"

        return self.query(prompt)


# === CLI Interface ===

def main():
    """CLI entry point for ChatGPT controller"""
    import argparse

    parser = argparse.ArgumentParser(description='QWAMOS ChatGPT Controller')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query ChatGPT')
    query_parser.add_argument('prompt', help='Your query/question')
    query_parser.add_argument('--api-key', required=True, help='OpenAI API key')
    query_parser.add_argument('--model', default='gpt-4-turbo', help='Model to use')
    query_parser.add_argument('--no-tor', action='store_true', help='Disable Tor (not recommended)')

    # Code generation command
    code_parser = subparsers.add_parser('code', help='Generate code')
    code_parser.add_argument('description', help='What the code should do')
    code_parser.add_argument('--api-key', required=True, help='OpenAI API key')
    code_parser.add_argument('--language', default='python', help='Programming language')

    # Test command
    test_parser = subparsers.add_parser('test', help='Test OpenAI API connection')
    test_parser.add_argument('--api-key', required=True, help='OpenAI API key')
    test_parser.add_argument('--no-tor', action='store_true', help='Disable Tor')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show usage statistics')
    status_parser.add_argument('--api-key', required=True, help='OpenAI API key')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize controller
    controller = ChatGPTController(args.api_key)

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

    elif args.command == 'code':
        code = controller.generate_code(args.description, args.language)
        print(f"\n{code}\n")

    elif args.command == 'test':
        print("Testing OpenAI API connection...")
        if controller.test_connection():
            print("✅ Connection successful")
            return 0
        else:
            print("❌ Connection failed")
            return 1

    elif args.command == 'status':
        status = controller.get_status()
        print("\n=== ChatGPT Status ===\n")
        print(f"Model: {status['model']}")
        print(f"Tor Enabled: {status['tor_enabled']}")
        print(f"Queries: {status['queries']}")
        print(f"Total Tokens: {status['usage']['total_tokens']}")
        print(f"Estimated Cost: ${status['usage']['estimated_cost']:.4f}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
