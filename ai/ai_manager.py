#!/usr/bin/env python3
"""
QWAMOS AI Manager - Central Orchestrator for AI Assistants

Manages three AI services:
1. Kali GPT (local LLM for pentesting)
2. Claude (Anthropic API for advanced reasoning)
3. ChatGPT (OpenAI API for general assistance)

All cloud API calls route through Tor for privacy.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AIManager')

class AIManager:
    """Central manager for all AI assistant services"""

    def __init__(self, config_dir: str = "/opt/qwamos/ai/config"):
        self.config_dir = Path(config_dir)
        self.services = {
            'kali-gpt': {'enabled': False, 'controller': None},
            'claude': {'enabled': False, 'controller': None},
            'chatgpt': {'enabled': False, 'controller': None}
        }
        self.usage_stats = {
            'kali-gpt': {'queries': 0, 'tokens': 0, 'cost': 0.0},
            'claude': {'queries': 0, 'tokens': 0, 'cost': 0.0},
            'chatgpt': {'queries': 0, 'tokens': 0, 'cost': 0.0}
        }
        self._load_config()

    def _load_config(self):
        """Load configuration for all services"""
        for service in ['kali-gpt', 'claude', 'chatgpt']:
            config_file = self.config_dir / f"{service.replace('-', '_')}_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Loaded config for {service}")

    # === Kali GPT (Local LLM) ===

    def enable_kali_gpt(self) -> bool:
        """
        Enable Kali GPT local LLM service

        Returns:
            bool: True if enabled successfully
        """
        try:
            logger.info("Enabling Kali GPT...")

            # Import controller
            from kali_gpt.kali_gpt_controller import KaliGPTController

            # Initialize controller
            self.services['kali-gpt']['controller'] = KaliGPTController()
            self.services['kali-gpt']['enabled'] = True

            logger.info("✅ Kali GPT enabled (local)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to enable Kali GPT: {e}")
            return False

    def disable_kali_gpt(self) -> bool:
        """Disable Kali GPT service"""
        try:
            if self.services['kali-gpt']['controller']:
                self.services['kali-gpt']['controller'].shutdown()
            self.services['kali-gpt']['enabled'] = False
            self.services['kali-gpt']['controller'] = None
            logger.info("Kali GPT disabled")
            return True
        except Exception as e:
            logger.error(f"Error disabling Kali GPT: {e}")
            return False

    # === Claude (Anthropic API) ===

    def enable_claude(self, api_key: str) -> bool:
        """
        Enable Claude AI service

        Args:
            api_key: Anthropic API key (sk-ant-...)

        Returns:
            bool: True if enabled successfully
        """
        try:
            logger.info("Enabling Claude...")

            # Import controller
            from claude.claude_controller import ClaudeController

            # Initialize controller with API key
            self.services['claude']['controller'] = ClaudeController(api_key)

            # Test connection
            if not self.services['claude']['controller'].test_connection():
                raise Exception("Failed to connect to Claude API")

            self.services['claude']['enabled'] = True
            logger.info("✅ Claude enabled (API via Tor)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to enable Claude: {e}")
            return False

    def disable_claude(self) -> bool:
        """Disable Claude service"""
        try:
            self.services['claude']['enabled'] = False
            self.services['claude']['controller'] = None
            logger.info("Claude disabled")
            return True
        except Exception as e:
            logger.error(f"Error disabling Claude: {e}")
            return False

    # === ChatGPT (OpenAI API) ===

    def enable_chatgpt(self, api_key: str) -> bool:
        """
        Enable ChatGPT service

        Args:
            api_key: OpenAI API key (sk-proj-...)

        Returns:
            bool: True if enabled successfully
        """
        try:
            logger.info("Enabling ChatGPT...")

            # Import controller
            from chatgpt.chatgpt_controller import ChatGPTController

            # Initialize controller with API key
            self.services['chatgpt']['controller'] = ChatGPTController(api_key)

            # Test connection
            if not self.services['chatgpt']['controller'].test_connection():
                raise Exception("Failed to connect to OpenAI API")

            self.services['chatgpt']['enabled'] = True
            logger.info("✅ ChatGPT enabled (API via Tor)")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to enable ChatGPT: {e}")
            return False

    def disable_chatgpt(self) -> bool:
        """Disable ChatGPT service"""
        try:
            self.services['chatgpt']['enabled'] = False
            self.services['chatgpt']['controller'] = None
            logger.info("ChatGPT disabled")
            return True
        except Exception as e:
            logger.error(f"Error disabling ChatGPT: {e}")
            return False

    # === Query Interface ===

    def query(self, service: str, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Send query to specified AI service

        Args:
            service: Service name ('kali-gpt', 'claude', 'chatgpt')
            prompt: User prompt/query
            context: Optional context dict (conversation history, etc.)

        Returns:
            str: AI response
        """
        if service not in self.services:
            raise ValueError(f"Unknown service: {service}")

        if not self.services[service]['enabled']:
            raise RuntimeError(f"Service {service} is not enabled")

        controller = self.services[service]['controller']
        if not controller:
            raise RuntimeError(f"No controller for {service}")

        # Route query to appropriate controller
        try:
            logger.info(f"Querying {service}...")

            response = controller.query(prompt, context or {})

            # Update usage stats
            self._update_stats(service, response)

            logger.info(f"Response from {service} received")
            return response

        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise

    def _update_stats(self, service: str, response: Any):
        """Update usage statistics"""
        self.usage_stats[service]['queries'] += 1

        # Extract token usage and cost from response metadata
        if hasattr(response, 'usage'):
            tokens = getattr(response.usage, 'total_tokens', 0)
            self.usage_stats[service]['tokens'] += tokens

            # Calculate cost (approximate)
            if service == 'claude':
                # Claude pricing: $0.003/1K input, $0.015/1K output
                cost = (tokens / 1000) * 0.009  # Average
            elif service == 'chatgpt':
                # GPT-4 Turbo pricing: $0.01/1K input, $0.03/1K output
                cost = (tokens / 1000) * 0.02  # Average
            else:
                cost = 0.0

            self.usage_stats[service]['cost'] += cost

    # === Status & Management ===

    def get_status(self) -> Dict[str, Any]:
        """
        Get status of all AI services

        Returns:
            dict: Status information
        """
        return {
            'kali-gpt': {
                'enabled': self.services['kali-gpt']['enabled'],
                'type': 'local',
                'privacy': '100% Local',
                'cost': 'Free'
            },
            'claude': {
                'enabled': self.services['claude']['enabled'],
                'type': 'cloud',
                'privacy': 'Cloud via Tor',
                'cost': f"${self.usage_stats['claude']['cost']:.2f}"
            },
            'chatgpt': {
                'enabled': self.services['chatgpt']['enabled'],
                'type': 'cloud',
                'privacy': 'Cloud via Tor',
                'cost': f"${self.usage_stats['chatgpt']['cost']:.2f}"
            }
        }

    def get_usage_stats(self) -> Dict[str, Dict]:
        """
        Get detailed usage statistics

        Returns:
            dict: Usage stats for all services
        """
        return self.usage_stats.copy()

    def list_services(self) -> List[str]:
        """List all available services"""
        return list(self.services.keys())

    def is_enabled(self, service: str) -> bool:
        """Check if service is enabled"""
        return self.services.get(service, {}).get('enabled', False)


# === CLI Interface ===

def main():
    """CLI entry point for AI Manager"""
    import argparse

    parser = argparse.ArgumentParser(description='QWAMOS AI Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable AI service')
    enable_parser.add_argument('service', choices=['kali-gpt', 'claude', 'chatgpt'])
    enable_parser.add_argument('--api-key', help='API key (for cloud services)')

    # Disable command
    disable_parser = subparsers.add_parser('disable', help='Disable AI service')
    disable_parser.add_argument('service', choices=['kali-gpt', 'claude', 'chatgpt'])

    # Status command
    subparsers.add_parser('status', help='Show status of all services')

    # Stats command
    subparsers.add_parser('stats', help='Show usage statistics')

    # Query command
    query_parser = subparsers.add_parser('query', help='Query AI service')
    query_parser.add_argument('service', choices=['kali-gpt', 'claude', 'chatgpt'])
    query_parser.add_argument('prompt', help='Query prompt')

    args = parser.parse_args()

    # Initialize manager
    manager = AIManager()

    # Execute command
    if args.command == 'enable':
        if args.service == 'kali-gpt':
            success = manager.enable_kali_gpt()
        elif args.service == 'claude':
            if not args.api_key:
                print("Error: --api-key required for Claude")
                return 1
            success = manager.enable_claude(args.api_key)
        elif args.service == 'chatgpt':
            if not args.api_key:
                print("Error: --api-key required for ChatGPT")
                return 1
            success = manager.enable_chatgpt(args.api_key)

        return 0 if success else 1

    elif args.command == 'disable':
        if args.service == 'kali-gpt':
            manager.disable_kali_gpt()
        elif args.service == 'claude':
            manager.disable_claude()
        elif args.service == 'chatgpt':
            manager.disable_chatgpt()
        return 0

    elif args.command == 'status':
        status = manager.get_status()
        print("\n=== QWAMOS AI Services Status ===\n")
        for service, info in status.items():
            enabled = "✅ Enabled" if info['enabled'] else "❌ Disabled"
            print(f"{service:12} {enabled:12} {info['privacy']:20} ${info['cost']}")
        print()
        return 0

    elif args.command == 'stats':
        stats = manager.get_usage_stats()
        print("\n=== Usage Statistics ===\n")
        for service, data in stats.items():
            print(f"{service}:")
            print(f"  Queries: {data['queries']}")
            print(f"  Tokens:  {data['tokens']}")
            print(f"  Cost:    ${data['cost']:.2f}")
        print()
        return 0

    elif args.command == 'query':
        try:
            response = manager.query(args.service, args.prompt)
            print(f"\n{response}\n")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
