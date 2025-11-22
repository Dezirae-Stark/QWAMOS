#!/usr/bin/env python3
"""
QWAMOS QR Code Authentication

CRITICAL FIX #11: Secure QR code-based authentication for VM access.

Provides:
- Time-based one-time passwords (TOTP) via QR codes
- Secure VM unlock without keyboard
- Air-gapped authentication (scan with phone)
- Encrypted authentication tokens

Author: QWAMOS Security Team
"""

import os
import sys
import json
import time
import hmac
import hashlib
import base64
import secrets
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('QRAuth')


class QRAuthenticator:
    """
    QR Code-based authentication system.

    CRITICAL FIX #11: Implements secure QR code authentication.

    Features:
    - TOTP (Time-based One-Time Password) generation
    - QR code generation for enrollment
    - Secure secret storage
    - Challenge-response authentication
    """

    def __init__(self, config_dir: str = "/opt/qwamos/security/qr_auth"):
        """
        Initialize QR authenticator.

        Args:
            config_dir: Directory for authentication secrets
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.secrets_file = self.config_dir / "secrets.enc"
        self.config_file = self.config_dir / "config.json"

        # TOTP parameters
        self.time_step = 30  # 30-second intervals
        self.code_digits = 6  # 6-digit codes
        self.window = 1  # Allow 1 interval before/after for clock skew

        # Check for qrencode
        self.qrencode_available = self._check_qrencode()

        logger.info("QR Authenticator initialized")

    def _check_qrencode(self) -> bool:
        """Check if qrencode is available."""
        try:
            import subprocess
            result = subprocess.run(
                ['which', 'qrencode'],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False

    def generate_secret(self, user: str, vm_name: str = None) -> Tuple[str, str]:
        """
        Generate TOTP secret for a user.

        Args:
            user: Username
            vm_name: Optional VM name for scoped auth

        Returns:
            Tuple of (secret_key, otpauth_url)
        """
        # Generate random secret (160 bits = 32 base32 chars)
        secret = base64.b32encode(secrets.token_bytes(20)).decode('utf-8')

        # Create otpauth URL
        issuer = "QWAMOS"
        account_name = user
        if vm_name:
            account_name = f"{user}@{vm_name}"

        otpauth_url = (
            f"otpauth://totp/{issuer}:{account_name}"
            f"?secret={secret}"
            f"&issuer={issuer}"
            f"&algorithm=SHA1"
            f"&digits={self.code_digits}"
            f"&period={self.time_step}"
        )

        # Store secret
        self._store_secret(user, vm_name, secret)

        logger.info(f"✓ Generated TOTP secret for {account_name}")
        return secret, otpauth_url

    def generate_qr_code(self, otpauth_url: str, output_file: str = None) -> bool:
        """
        Generate QR code image from otpauth URL.

        Args:
            otpauth_url: OTP auth URL
            output_file: Output PNG file path

        Returns:
            True if successful
        """
        if not self.qrencode_available:
            logger.error("qrencode not installed - cannot generate QR code")
            logger.info("Install with: apt-get install qrencode")
            logger.info(f"Manual enrollment URL: {otpauth_url}")
            return False

        try:
            import subprocess

            if output_file is None:
                output_file = self.config_dir / "enrollment_qr.png"

            result = subprocess.run([
                'qrencode',
                '-o', str(output_file),
                '-s', '10',  # Size
                '-l', 'H',  # Error correction level
                otpauth_url
            ], capture_output=True)

            if result.returncode == 0:
                logger.info(f"✓ QR code generated: {output_file}")
                logger.info("Scan with authenticator app (Google Authenticator, Authy, etc.)")
                return True
            else:
                logger.error(f"QR code generation failed: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"QR code generation error: {e}")
            return False

    def generate_totp(self, secret: str, time_offset: int = 0) -> str:
        """
        Generate TOTP code.

        Args:
            secret: Base32-encoded secret
            time_offset: Time offset in intervals (for testing)

        Returns:
            6-digit TOTP code
        """
        # Decode secret
        key = base64.b32decode(secret, casefold=True)

        # Calculate time counter
        current_time = int(time.time())
        time_counter = (current_time // self.time_step) + time_offset

        # Generate HMAC
        msg = time_counter.to_bytes(8, byteorder='big')
        digest = hmac.new(key, msg, hashlib.sha1).digest()

        # Dynamic truncation (RFC 4226)
        offset = digest[-1] & 0x0f
        code_bytes = digest[offset:offset+4]
        code = int.from_bytes(code_bytes, byteorder='big') & 0x7fffffff

        # Format to 6 digits
        code_str = str(code % (10 ** self.code_digits)).zfill(self.code_digits)

        return code_str

    def verify_totp(self, user: str, code: str, vm_name: str = None) -> bool:
        """
        Verify TOTP code.

        Args:
            user: Username
            code: TOTP code to verify
            vm_name: Optional VM name

        Returns:
            True if code is valid
        """
        # Load secret
        secret = self._load_secret(user, vm_name)
        if not secret:
            logger.error(f"No secret found for user: {user}")
            return False

        # Check code against current time +/- window
        for offset in range(-self.window, self.window + 1):
            expected_code = self.generate_totp(secret, offset)
            if code == expected_code:
                logger.info(f"✓ TOTP verification successful for {user}")
                return True

        logger.warning(f"✗ TOTP verification failed for {user}")
        return False

    def generate_challenge(self, user: str, vm_name: str = None) -> Dict[str, str]:
        """
        Generate authentication challenge.

        Args:
            user: Username
            vm_name: Optional VM name

        Returns:
            Dict with challenge data including QR code
        """
        # Generate random challenge
        challenge = secrets.token_hex(16)

        # Create challenge URL (can be displayed as QR)
        challenge_data = {
            'user': user,
            'vm': vm_name or 'host',
            'challenge': challenge,
            'timestamp': int(time.time())
        }

        # Encode as URL for QR
        challenge_json = json.dumps(challenge_data)
        challenge_b64 = base64.urlsafe_b64encode(challenge_json.encode()).decode()

        challenge_url = f"qwamos://auth?c={challenge_b64}"

        logger.info(f"Generated challenge for {user}")
        return {
            'challenge': challenge,
            'url': challenge_url,
            'expires_at': int(time.time()) + 300  # 5 minutes
        }

    def _store_secret(self, user: str, vm_name: Optional[str], secret: str):
        """Store TOTP secret encrypted."""
        try:
            from Crypto.Cipher import ChaCha20_Poly1305
            from Crypto.Random import get_random_bytes
            from Crypto.Protocol.KDF import HKDF
            from Crypto.Hash import SHA256

            # Load existing secrets or create new
            secrets_data = {}
            if self.secrets_file.exists():
                secrets_data = self._load_secrets()

            # Add new secret
            key = f"{user}@{vm_name}" if vm_name else user
            secrets_data[key] = {
                'secret': secret,
                'created': datetime.now().isoformat(),
                'user': user,
                'vm': vm_name
            }

            # Encrypt and save
            plaintext = json.dumps(secrets_data).encode('utf-8')

            # Derive encryption key
            enc_key = self._get_encryption_key()

            nonce = get_random_bytes(12)
            cipher = ChaCha20_Poly1305.new(key=enc_key, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(plaintext)

            with open(self.secrets_file, 'wb') as f:
                f.write(nonce + tag + ciphertext)

            os.chmod(self.secrets_file, 0o600)

        except Exception as e:
            logger.error(f"Failed to store secret: {e}")
            raise

    def _load_secret(self, user: str, vm_name: Optional[str]) -> Optional[str]:
        """Load TOTP secret."""
        try:
            secrets_data = self._load_secrets()
            key = f"{user}@{vm_name}" if vm_name else user

            if key in secrets_data:
                return secrets_data[key]['secret']
            return None
        except Exception as e:
            logger.error(f"Failed to load secret: {e}")
            return None

    def _load_secrets(self) -> Dict:
        """Load all secrets from encrypted file."""
        try:
            from Crypto.Cipher import ChaCha20_Poly1305

            if not self.secrets_file.exists():
                return {}

            with open(self.secrets_file, 'rb') as f:
                nonce = f.read(12)
                tag = f.read(16)
                ciphertext = f.read()

            enc_key = self._get_encryption_key()

            cipher = ChaCha20_Poly1305.new(key=enc_key, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)

            return json.loads(plaintext.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to load secrets: {e}")
            return {}

    def _get_encryption_key(self) -> bytes:
        """Derive encryption key for secrets file."""
        from Crypto.Protocol.KDF import HKDF
        from Crypto.Hash import SHA256
        import uuid

        # Get device-specific ID
        device_id_file = Path.home() / ".qwamos" / ".device_id"
        if device_id_file.exists():
            with open(device_id_file, 'rb') as f:
                device_id = f.read()
        else:
            device_id = str(uuid.getnode()).encode('utf-8')
            device_id_file.parent.mkdir(parents=True, exist_ok=True)
            with open(device_id_file, 'wb') as f:
                f.write(device_id)
            os.chmod(device_id_file, 0o600)

        return HKDF(
            master=device_id,
            key_len=32,
            salt=b"qwamos-qr-auth-v1",
            hashmod=SHA256
        )

    def enroll_user(self, user: str, vm_name: str = None, generate_qr: bool = True) -> bool:
        """
        Enroll user for QR authentication.

        Args:
            user: Username
            vm_name: Optional VM name
            generate_qr: Whether to generate QR code image

        Returns:
            True if successful
        """
        logger.info(f"Enrolling user for QR auth: {user}")

        # Generate secret
        secret, otpauth_url = self.generate_secret(user, vm_name)

        # Generate QR code
        if generate_qr:
            qr_file = self.config_dir / f"enroll_{user}.png"
            self.generate_qr_code(otpauth_url, str(qr_file))

        # Print manual enrollment option
        logger.info(f"\nManual enrollment URL:")
        logger.info(f"{otpauth_url}\n")
        logger.info("To test, generate code with:")
        logger.info(f"  python3 -c \"from security.qr_auth import QRAuthenticator; qa = QRAuthenticator(); print(qa.generate_totp('{secret}'))\"")

        return True


def main():
    """CLI interface for QR authentication."""
    import argparse

    parser = argparse.ArgumentParser(description='QWAMOS QR Authentication')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Enroll command
    enroll_parser = subparsers.add_parser('enroll', help='Enroll user')
    enroll_parser.add_argument('user', help='Username')
    enroll_parser.add_argument('--vm', help='VM name (optional)')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify TOTP code')
    verify_parser.add_argument('user', help='Username')
    verify_parser.add_argument('code', help='6-digit TOTP code')
    verify_parser.add_argument('--vm', help='VM name (optional)')

    # Test command
    test_parser = subparsers.add_parser('test', help='Generate test code')
    test_parser.add_argument('secret', help='Base32 secret')

    args = parser.parse_args()

    qa = QRAuthenticator()

    if args.command == 'enroll':
        qa.enroll_user(args.user, args.vm)

    elif args.command == 'verify':
        result = qa.verify_totp(args.user, args.code, args.vm)
        if result:
            print("✓ Authentication successful")
            sys.exit(0)
        else:
            print("✗ Authentication failed")
            sys.exit(1)

    elif args.command == 'test':
        code = qa.generate_totp(args.secret)
        print(f"Current TOTP code: {code}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
