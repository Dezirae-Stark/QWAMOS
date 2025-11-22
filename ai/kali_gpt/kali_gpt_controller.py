#!/usr/bin/env python3
"""
QWAMOS Kali GPT Controller - Local LLM Pentesting Assistant

Manages Llama 3.1 8B model for on-device pentesting guidance.
100% private, no network required.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# CRITICAL FIX #22: Import AI sandbox for process isolation
sys.path.insert(0, str(Path(__file__).parent.parent))
from ai_sandbox import AISandbox, SandboxMode

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KaliGPT')

class KaliGPTController:
    """Controller for Kali GPT local LLM service"""

    def __init__(self, model_dir: str = "/opt/qwamos/ai/kali_gpt/models",
                 enable_sandbox: bool = True,
                 encrypt_history: bool = True):
        """
        Initialize Kali GPT controller

        Args:
            model_dir: Directory containing Llama model files
            enable_sandbox: Enable process sandboxing (Fix #22)
            encrypt_history: Encrypt conversation history (Fix #23)
        """
        self.model_dir = Path(model_dir)
        self.model_path = self.model_dir / "llama-3.1-8b-instruct.gguf"
        self.llama_cpp = None
        self.model = None
        self.context_size = 4096
        self.max_tokens = 2048
        self.temperature = 0.7

        # CRITICAL FIX #22: Enable sandbox by default
        self.enable_sandbox = enable_sandbox
        self.sandbox = None
        if self.enable_sandbox:
            # Kali GPT doesn't need network (local model)
            self.sandbox = AISandbox("kali_gpt", SandboxMode.NETWORK_ISOLATED)
            self.sandbox.setup_sandbox()
            logger.info("✓ AI sandbox enabled (network isolated)")
        else:
            logger.warning("⚠️  AI sandbox DISABLED - security risk!")

        # CRITICAL FIX #23: Enable history encryption by default
        self.encrypt_history = encrypt_history
        self.history_file = Path.home() / ".qwamos" / "ai" / "kali_gpt_history.enc"
        if self.encrypt_history:
            logger.info("✓ Conversation history encryption enabled")

        # Load system prompts
        self.system_prompt = self._load_system_prompt()

        # Load tool knowledge base
        self.tool_knowledge = self._load_tool_knowledge()

        # Conversation history
        self.history = []
        if self.encrypt_history:
            self._load_encrypted_history()

        logger.info(f"Kali GPT controller initialized (model: {self.model_path})")

    def _load_system_prompt(self) -> str:
        """Load the system prompt for Kali GPT"""
        prompt_file = Path(__file__).parent / "prompts" / "system_prompt.txt"

        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                return f.read()

        # Default system prompt
        return """You are Kali GPT, an expert penetration testing assistant running locally on QWAMOS.

Your role is to provide security testing guidance, tool recommendations, and vulnerability analysis.

Core competencies:
- Network scanning and reconnaissance (nmap, masscan)
- Web application testing (sqlmap, burp suite, nikto)
- Exploitation frameworks (metasploit, exploit-db)
- Wireless security (aircrack-ng, kismet)
- Password cracking (john, hashcat, hydra)
- Forensics and analysis
- Report generation

Guidelines:
1. Always emphasize legal and ethical hacking practices
2. Provide step-by-step command examples
3. Explain security concepts clearly
4. Suggest appropriate tools for each task
5. Warn about potential risks and side effects
6. Reference CVE databases when relevant
7. Provide mitigation strategies alongside vulnerabilities

Remember: All testing should only be performed on systems you own or have explicit permission to test."""

    def _load_tool_knowledge(self) -> Dict[str, Dict]:
        """Load pentesting tool knowledge base"""
        knowledge_file = Path(__file__).parent / "knowledge" / "tools.json"

        if knowledge_file.exists():
            with open(knowledge_file, 'r') as f:
                return json.load(f)

        # Default tool knowledge
        return {
            "nmap": {
                "description": "Network scanning and port discovery",
                "common_commands": [
                    "nmap -sV -p- <target>  # Full port scan with version detection",
                    "nmap -sS -p 80,443 <target>  # Stealth SYN scan on web ports",
                    "nmap -A <target>  # Aggressive scan with OS detection"
                ],
                "output_formats": ["-oN", "-oX", "-oG"]
            },
            "sqlmap": {
                "description": "Automated SQL injection testing",
                "common_commands": [
                    "sqlmap -u <url> --dbs  # Enumerate databases",
                    "sqlmap -u <url> -D <db> --tables  # Enumerate tables",
                    "sqlmap -u <url> --dump  # Extract data"
                ],
                "techniques": ["boolean-based", "error-based", "union", "time-based"]
            },
            "metasploit": {
                "description": "Exploitation framework",
                "common_commands": [
                    "msfconsole  # Launch console",
                    "search <keyword>  # Search exploits",
                    "use exploit/<path>  # Select exploit",
                    "set RHOST <target>  # Set target",
                    "exploit  # Run exploit"
                ],
                "components": ["exploits", "payloads", "auxiliary", "encoders"]
            },
            "burp": {
                "description": "Web application security testing platform",
                "features": ["proxy", "scanner", "repeater", "intruder", "sequencer"],
                "common_tasks": [
                    "Intercept HTTP requests",
                    "Scan for vulnerabilities",
                    "Brute force parameters",
                    "Analyze session tokens"
                ]
            },
            "john": {
                "description": "Password cracking tool",
                "common_commands": [
                    "john --wordlist=<wordlist> <hashfile>  # Dictionary attack",
                    "john --incremental <hashfile>  # Brute force",
                    "john --show <hashfile>  # Show cracked passwords"
                ],
                "modes": ["single", "wordlist", "incremental"]
            },
            "hydra": {
                "description": "Network logon cracker",
                "common_commands": [
                    "hydra -l <user> -P <passlist> <target> ssh",
                    "hydra -L <userlist> -P <passlist> <target> http-post-form"
                ],
                "protocols": ["ssh", "ftp", "http", "smb", "rdp"]
            }
        }

    def load_model(self) -> bool:
        """
        Load the Llama model into memory

        Returns:
            bool: True if loaded successfully
        """
        try:
            # Check if model file exists
            if not self.model_path.exists():
                logger.error(f"Model file not found: {self.model_path}")
                logger.info("Please download Llama 3.1 8B Instruct GGUF model")
                return False

            # Import llama-cpp-python
            try:
                from llama_cpp import Llama
                self.llama_cpp = Llama
            except ImportError:
                logger.error("llama-cpp-python not installed")
                logger.info("Install with: pip install llama-cpp-python")
                return False

            # Load model
            logger.info("Loading Llama 3.1 8B model (this may take a minute)...")

            self.model = self.llama_cpp(
                model_path=str(self.model_path),
                n_ctx=self.context_size,
                n_threads=4,  # ARM64 optimization
                n_gpu_layers=0,  # CPU only (no GPU on mobile)
                verbose=False
            )

            logger.info("✅ Kali GPT model loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def query(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Query Kali GPT with a pentesting question

        Args:
            prompt: User query/prompt
            context: Optional context (conversation history, scan results, etc.)

        Returns:
            str: Kali GPT response
        """
        try:
            # Ensure model is loaded
            if not self.model:
                if not self.load_model():
                    return "Error: Kali GPT model not loaded. Please check model installation."

            # Add context to prompt if provided
            full_prompt = self._build_prompt(prompt, context)

            # Generate response
            logger.info("Generating Kali GPT response...")

            response = self.model(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["User:", "Assistant:"]
            )

            # Extract text from response
            answer = response['choices'][0]['text'].strip()

            # Add to history
            self.history.append({
                'timestamp': datetime.now().isoformat(),
                'prompt': prompt,
                'response': answer
            })

            logger.info("Response generated successfully")
            return answer

        except Exception as e:
            logger.error(f"Query failed: {e}")
            return f"Error generating response: {e}"

    def _build_prompt(self, prompt: str, context: Optional[Dict]) -> str:
        """Build complete prompt with system prompt and context"""
        parts = [self.system_prompt, "\n\n"]

        # Add tool context if relevant
        if context and 'tool' in context:
            tool = context['tool']
            if tool in self.tool_knowledge:
                parts.append(f"Tool Context: {tool}\n")
                parts.append(json.dumps(self.tool_knowledge[tool], indent=2))
                parts.append("\n\n")

        # Add scan results if provided
        if context and 'scan_results' in context:
            parts.append("Scan Results:\n")
            parts.append(context['scan_results'])
            parts.append("\n\n")

        # Add conversation history (last 5 exchanges)
        if len(self.history) > 0:
            parts.append("Recent conversation:\n")
            for entry in self.history[-5:]:
                parts.append(f"User: {entry['prompt']}\n")
                parts.append(f"Assistant: {entry['response'][:200]}...\n\n")

        # Add current prompt
        parts.append(f"User: {prompt}\n")
        parts.append("Assistant: ")

        return "".join(parts)

    def analyze_tool_output(self, tool: str, output: str) -> str:
        """
        Analyze output from a pentesting tool

        Args:
            tool: Tool name (e.g., 'nmap', 'sqlmap')
            output: Raw output from the tool

        Returns:
            str: Analysis and recommendations
        """
        context = {
            'tool': tool,
            'scan_results': output
        }

        prompt = f"Analyze the following {tool} output and provide insights, vulnerabilities found, and next steps:"

        return self.query(prompt, context)

    def suggest_exploit(self, service: str, version: str) -> str:
        """
        Suggest exploits for a specific service and version

        Args:
            service: Service name (e.g., 'Apache', 'SSH')
            version: Version string

        Returns:
            str: Exploit suggestions
        """
        prompt = f"What are known vulnerabilities and exploits for {service} {version}? Provide CVE numbers if applicable and suggest exploitation methods."

        return self.query(prompt)

    def generate_report(self, findings: List[str]) -> str:
        """
        Generate a penetration testing report

        Args:
            findings: List of findings to include

        Returns:
            str: Formatted report
        """
        findings_text = "\n".join([f"- {f}" for f in findings])

        prompt = f"""Generate a professional penetration testing report with the following findings:

{findings_text}

Include: Executive Summary, Technical Details, Risk Ratings, and Remediation Recommendations."""

        return self.query(prompt)

    def clear_history(self):
        """Clear conversation history"""
        self.history = []
        logger.info("Conversation history cleared")

    def shutdown(self):
        """Shutdown and unload model"""
        if self.model:
            del self.model
            self.model = None
            logger.info("Kali GPT model unloaded")

    def test_connection(self) -> bool:
        """
        Test if the service is functional

        Returns:
            bool: True if working
        """
        try:
            if not self.model_path.exists():
                logger.warning("Model file not found")
                return False

            # Try to load model
            if not self.model:
                return self.load_model()

            return True

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
            'model_loaded': self.model is not None,
            'model_path': str(self.model_path),
            'model_exists': self.model_path.exists(),
            'context_size': self.context_size,
            'queries': len(self.history),
            'status': 'ready' if self.model else 'not_loaded',
            'sandbox_enabled': self.enable_sandbox,
            'history_encrypted': self.encrypt_history
        }

    def _load_encrypted_history(self):
        """
        Load encrypted conversation history.

        CRITICAL FIX #23: Encrypts AI conversation history at rest.
        """
        if not self.history_file.exists():
            return

        try:
            from Crypto.Cipher import ChaCha20_Poly1305
            from Crypto.Protocol.KDF import HKDF
            from Crypto.Hash import SHA256

            # Derive encryption key from device-specific data
            key = self._get_history_encryption_key()

            # Read encrypted file
            with open(self.history_file, 'rb') as f:
                nonce = f.read(12)  # ChaCha20-Poly1305 nonce
                tag = f.read(16)  # Authentication tag
                ciphertext = f.read()

            # Decrypt
            cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)

            # Load history
            self.history = json.loads(plaintext.decode('utf-8'))
            logger.info(f"✓ Loaded {len(self.history)} encrypted history entries")

        except Exception as e:
            logger.warning(f"Failed to load encrypted history: {e}")
            logger.info("Starting with empty history")
            self.history = []

    def _save_encrypted_history(self):
        """
        Save conversation history with encryption.

        CRITICAL FIX #23: Encrypts AI conversation history at rest.
        """
        if not self.encrypt_history:
            return

        try:
            from Crypto.Cipher import ChaCha20_Poly1305
            from Crypto.Random import get_random_bytes

            # Ensure directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            # Derive encryption key
            key = self._get_history_encryption_key()

            # Serialize history
            plaintext = json.dumps(self.history, indent=2).encode('utf-8')

            # Encrypt with ChaCha20-Poly1305
            nonce = get_random_bytes(12)
            cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext)

            # Save encrypted file
            with open(self.history_file, 'wb') as f:
                f.write(nonce)
                f.write(tag)
                f.write(ciphertext)

            # Set restrictive permissions
            os.chmod(self.history_file, 0o600)

            logger.debug(f"✓ Saved {len(self.history)} encrypted history entries")

        except Exception as e:
            logger.error(f"Failed to save encrypted history: {e}")

    def _get_history_encryption_key(self) -> bytes:
        """
        Derive encryption key for conversation history.

        Uses device-specific data to derive a unique key.

        Returns:
            32-byte encryption key
        """
        from Crypto.Protocol.KDF import HKDF
        from Crypto.Hash import SHA256
        import uuid

        # Get device-specific ID
        device_id_file = Path.home() / ".qwamos" / ".device_id"
        if device_id_file.exists():
            with open(device_id_file, 'rb') as f:
                device_id = f.read()
        else:
            # Create persistent device ID
            device_id = str(uuid.getnode()).encode('utf-8')
            device_id_file.parent.mkdir(parents=True, exist_ok=True)
            with open(device_id_file, 'wb') as f:
                f.write(device_id)
            os.chmod(device_id_file, 0o600)

        # Derive key using HKDF
        key = HKDF(
            master=device_id,
            key_len=32,
            salt=b"qwamos-ai-history-v1",
            hashmod=SHA256,
            num_keys=1,
            context=b"kali-gpt-history"
        )

        return key


# === CLI Interface ===

def main():
    """CLI entry point for Kali GPT"""
    import argparse

    parser = argparse.ArgumentParser(description='QWAMOS Kali GPT - Local Pentesting Assistant')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Query command
    query_parser = subparsers.add_parser('query', help='Ask Kali GPT a question')
    query_parser.add_argument('prompt', help='Your pentesting question')
    query_parser.add_argument('--tool', help='Tool context (nmap, sqlmap, etc.)')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze tool output')
    analyze_parser.add_argument('tool', help='Tool name')
    analyze_parser.add_argument('output_file', help='File containing tool output')

    # Status command
    subparsers.add_parser('status', help='Show Kali GPT status')

    # Test command
    subparsers.add_parser('test', help='Test Kali GPT functionality')

    args = parser.parse_args()

    # Initialize controller
    controller = KaliGPTController()

    # Execute command
    if args.command == 'query':
        context = {'tool': args.tool} if args.tool else None
        response = controller.query(args.prompt, context)
        print(f"\n{response}\n")

    elif args.command == 'analyze':
        with open(args.output_file, 'r') as f:
            output = f.read()
        analysis = controller.analyze_tool_output(args.tool, output)
        print(f"\n{analysis}\n")

    elif args.command == 'status':
        status = controller.get_status()
        print("\n=== Kali GPT Status ===\n")
        for key, value in status.items():
            print(f"{key}: {value}")
        print()

    elif args.command == 'test':
        print("Testing Kali GPT...")
        if controller.test_connection():
            print("✅ Kali GPT is working correctly")

            # Test query
            print("\nTest query: 'What ports should I scan first?'")
            response = controller.query("What ports should I scan first for a web server?")
            print(f"\nResponse: {response[:200]}...\n")
        else:
            print("❌ Kali GPT test failed")

    else:
        parser.print_help()


if __name__ == "__main__":
    sys.exit(main() or 0)
