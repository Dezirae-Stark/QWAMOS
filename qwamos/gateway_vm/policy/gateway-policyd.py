#!/usr/bin/env python3
"""
Gateway VM Policy Daemon - Echo Service

Simple echo service for testing signed control bus messages from Dom0.
Verifies Ed25519 signatures and logs received policy updates.

In production, this would apply firewall rules, Tor configuration, etc.
"""
import socket
import os
import sys
import json
import base64
import logging
from pathlib import Path
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Configuration
SOCKET_PATH = "/run/qwamos/gateway-bus.sock"
DOM0_PUBLIC_KEY_PATH = Path("/etc/qwamos/dom0.pub")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [Gateway-PolicyD] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class GatewayPolicyDaemon:
    def __init__(self):
        self.verify_key = None
        self.load_verify_key()

    def load_verify_key(self):
        """Load Dom0's public verification key"""
        if not DOM0_PUBLIC_KEY_PATH.exists():
            logger.error(f"Dom0 public key not found at {DOM0_PUBLIC_KEY_PATH}")
            logger.error("Copy Dom0's public key to this VM:")
            logger.error(f"  cp ~/.qwamos/dom0/ed25519_pk {DOM0_PUBLIC_KEY_PATH}")
            sys.exit(1)

        key_bytes = DOM0_PUBLIC_KEY_PATH.read_bytes()
        self.verify_key = VerifyKey(key_bytes)
        logger.info(f"Loaded Dom0 public key from {DOM0_PUBLIC_KEY_PATH}")

    def canonical_json(self, obj):
        """Generate canonical JSON for signature verification"""
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))

    def verify_signature(self, msg, signature_b64):
        """Verify Ed25519 signature from Dom0"""
        try:
            signature = base64.b64decode(signature_b64)
            msg_canonical = self.canonical_json(msg).encode('utf-8')
            self.verify_key.verify(msg_canonical, signature)
            return True
        except BadSignatureError:
            return False
        except Exception as e:
            logger.warning(f"Signature verification error: {e}")
            return False

    def handle_policy_update(self, args):
        """Handle policy update command (echo for testing)"""
        logger.info("=== Policy Update Received ===")
        for key, value in args.items():
            logger.info(f"  {key} = {value}")

        # In production, apply actual policy changes here
        # For now, just echo back success
        return {"status": "ok", "message": "Policy update logged (echo service)"}

    def process_message(self, data):
        """Process incoming message from Dom0"""
        try:
            envelope = json.loads(data.decode('utf-8'))
            msg = envelope.get("msg")
            signature = envelope.get("signature")

            if not msg or not signature:
                logger.warning("Received message missing msg or signature")
                return {"status": "error", "reason": "Missing msg or signature"}

            # Verify signature
            if not self.verify_signature(msg, signature):
                logger.error("SIGNATURE VERIFICATION FAILED - Rejecting message")
                return {"status": "error", "reason": "Invalid signature"}

            logger.info("✓ Signature verified successfully")

            # Log message details
            command = msg.get("command")
            nonce = msg.get("nonce")
            timestamp = msg.get("timestamp")
            logger.info(f"Command: {command}, Nonce: {nonce[:16]}..., Timestamp: {timestamp}")

            # Handle command
            if command == "set_policy":
                return self.handle_policy_update(msg.get("args", {}))
            else:
                logger.warning(f"Unknown command: {command}")
                return {"status": "error", "reason": f"Unknown command: {command}"}

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return {"status": "error", "reason": f"Invalid JSON: {e}"}
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {"status": "error", "reason": f"Processing error: {e}"}

    def run(self):
        """Main daemon loop"""
        # Remove old socket if exists
        if os.path.exists(SOCKET_PATH):
            os.remove(SOCKET_PATH)

        # Create socket directory
        Path(SOCKET_PATH).parent.mkdir(parents=True, exist_ok=True)

        # Create Unix socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(SOCKET_PATH)
        sock.listen(5)

        # Set socket permissions
        os.chmod(SOCKET_PATH, 0o660)

        logger.info(f"Gateway Policy Daemon listening on {SOCKET_PATH}")
        logger.info("Echo service mode - will log received policy updates")
        logger.info("")

        try:
            while True:
                conn, addr = sock.accept()
                try:
                    # Read message
                    data = conn.recv(65536)
                    if data:
                        # Process message
                        response = self.process_message(data)

                        # Send response
                        conn.sendall(json.dumps(response).encode('utf-8'))
                finally:
                    conn.close()

        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
        finally:
            sock.close()
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)

def main():
    logger.info("=" * 70)
    logger.info("QWAMOS Gateway VM Policy Daemon (Echo Service)")
    logger.info("=" * 70)

    daemon = GatewayPolicyDaemon()
    daemon.run()

if __name__ == "__main__":
    main()
