#!/usr/bin/env python3
"""
QWAMOS AI Request Sanitizer

Removes personally identifiable information (PII) and sensitive data
from prompts before sending to cloud AI services.

Protects:
- IP addresses
- Email addresses
- Phone numbers
- API keys and tokens
- Credit card numbers
- Social security numbers
- URLs with sensitive paths
- File paths
- Usernames
- Passwords
"""

import re
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger('RequestSanitizer')


class RequestSanitizer:
    """Sanitize user prompts before sending to AI services"""

    def __init__(self):
        self.patterns = self._compile_patterns()
        self.replacements_made = []

    def _compile_patterns(self) -> Dict[str, Tuple[re.Pattern, str]]:
        """Compile regex patterns for PII detection"""
        return {
            'ipv4': (
                re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
                '[IP_ADDRESS]'
            ),
            'ipv6': (
                re.compile(r'\b([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'),
                '[IPV6_ADDRESS]'
            ),
            'email': (
                re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                '[EMAIL]'
            ),
            'phone_us': (
                re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
                '[PHONE]'
            ),
            'phone_intl': (
                re.compile(r'\+\d{1,3}[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}'),
                '[PHONE]'
            ),
            'api_key_anthropic': (
                re.compile(r'sk-ant-[a-zA-Z0-9\-_]{95,}'),
                '[API_KEY]'
            ),
            'api_key_openai': (
                re.compile(r'sk-[a-zA-Z0-9]{48,}'),
                '[API_KEY]'
            ),
            'api_key_generic': (
                re.compile(r'\b[a-zA-Z0-9_-]{32,}\b(?=.*key|token|secret)', re.IGNORECASE),
                '[API_KEY]'
            ),
            'credit_card': (
                re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
                '[CREDIT_CARD]'
            ),
            'ssn': (
                re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
                '[SSN]'
            ),
            'url_with_params': (
                re.compile(r'https?://[^\s]+\?[^\s]+'),
                '[URL_WITH_PARAMS]'
            ),
            'file_path_unix': (
                re.compile(r'/(?:home|root|etc|var|opt)/[\w/.-]+'),
                '[FILE_PATH]'
            ),
            'file_path_windows': (
                re.compile(r'[A-Z]:\\[\w\\.-]+', re.IGNORECASE),
                '[FILE_PATH]'
            ),
            'username': (
                re.compile(r'(?:username|user|login)[\s:=]+([a-zA-Z0-9_-]+)', re.IGNORECASE),
                r'username: [USERNAME]'
            ),
            'password': (
                re.compile(r'(?:password|passwd|pwd)[\s:=]+\S+', re.IGNORECASE),
                'password: [REDACTED]'
            ),
            'jwt_token': (
                re.compile(r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'),
                '[JWT_TOKEN]'
            ),
            'ssh_key': (
                re.compile(r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----'),
                '[SSH_PRIVATE_KEY_REDACTED]'
            ),
            'mac_address': (
                re.compile(r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b'),
                '[MAC_ADDRESS]'
            )
        }

    def sanitize(self, text: str, aggressive: bool = False) -> Tuple[str, List[str]]:
        """
        Sanitize text by removing PII

        Args:
            text: The text to sanitize
            aggressive: If True, apply more aggressive pattern matching

        Returns:
            Tuple of (sanitized_text, list_of_replacements_made)
        """
        self.replacements_made = []
        sanitized = text

        # Apply each pattern
        for pattern_name, (pattern, replacement) in self.patterns.items():
            matches = pattern.findall(sanitized)
            if matches:
                self.replacements_made.append(f"{pattern_name}: {len(matches)} replacement(s)")
                sanitized = pattern.sub(replacement, sanitized)
                logger.debug(f"Sanitized {len(matches)} {pattern_name} match(es)")

        # Aggressive mode: additional patterns
        if aggressive:
            # Redact anything that looks like a hash
            hash_pattern = re.compile(r'\b[a-fA-F0-9]{32,}\b')
            if hash_pattern.search(sanitized):
                self.replacements_made.append("hash: multiple replacements")
                sanitized = hash_pattern.sub('[HASH]', sanitized)

            # Redact base64-like strings
            base64_pattern = re.compile(r'\b[A-Za-z0-9+/]{40,}={0,2}\b')
            if base64_pattern.search(sanitized):
                self.replacements_made.append("base64: multiple replacements")
                sanitized = base64_pattern.sub('[BASE64_DATA]', sanitized)

        return sanitized, self.replacements_made

    def sanitize_dict(self, data: Dict) -> Dict:
        """Recursively sanitize all string values in a dictionary"""
        result = {}

        for key, value in data.items():
            if isinstance(value, str):
                result[key], _ = self.sanitize(value)
            elif isinstance(value, dict):
                result[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self.sanitize_dict(item) if isinstance(item, dict)
                    else (self.sanitize(item)[0] if isinstance(item, str) else item)
                    for item in value
                ]
            else:
                result[key] = value

        return result

    def check_for_sensitive_data(self, text: str) -> List[str]:
        """
        Check if text contains sensitive data without modifying it

        Returns:
            List of detected sensitive data types
        """
        detected = []

        for pattern_name, (pattern, _) in self.patterns.items():
            if pattern.search(text):
                detected.append(pattern_name)

        return detected

    def get_report(self) -> str:
        """Get a report of what was sanitized"""
        if not self.replacements_made:
            return "No sensitive data detected"

        return "Sanitized: " + ", ".join(self.replacements_made)


def test_sanitizer():
    """Test the request sanitizer"""
    sanitizer = RequestSanitizer()

    test_cases = [
        "My IP is 192.168.1.100 and my email is user@example.com",
        "Call me at 555-123-4567 or +1-555-123-4567",
        "Here's my API key: sk-ant-api03-1234567890abcdef",
        "Credit card: 4532-1234-5678-9010",
        "SSN: 123-45-6789",
        "Visit https://example.com?token=secret123&user=admin",
        "File: /home/user/.ssh/id_rsa",
        "Username: admin, Password: secret123",
    ]

    print("QWAMOS Request Sanitizer Test")
    print("=" * 60)

    for i, test in enumerate(test_cases, 1):
        sanitized, replacements = sanitizer.sanitize(test)
        print(f"\nTest {i}:")
        print(f"  Original:  {test}")
        print(f"  Sanitized: {sanitized}")
        print(f"  Report:    {sanitizer.get_report()}")

    print("\n" + "=" * 60)
    print("All tests completed")


if __name__ == '__main__':
    test_sanitizer()
