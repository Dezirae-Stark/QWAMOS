#!/usr/bin/env python3
"""
QWAMOS Policy Daemon (qwamosd)

Runs in Dom0 and listens on Unix socket /run/qwamos/bus.sock for signed
control bus messages. Validates Ed25519 signatures, enforces replay protection,
and applies policy changes either immediately (runtime-safe) or stages them
for next boot (reboot-required).

Control Bus Message Format:
{
  "msg": {
    "command": "set_policy",
    "args": {"RADIO_ISOLATION": "on"},
    "nonce": "base64-random-16-bytes",
    "timestamp": 1699876543
  },
  "signature": "base64-ed25519-signature"
}

Runtime-safe policies (apply immediately):
- RADIO_ISOLATION
- RADIO_HARDENING.level
- RADIO_IDLE_TIMEOUT_MIN
- TOR_ISOLATION
- VPN_KILL_SWITCH
- CLIPBOARD_ISOLATION
- DURESS.enabled
- DURESS.gesture
- GHOST.trigger

Reboot-required policies (staged to /etc/qwamos/pending.conf):
- BOOT_VERIFICATION
- KERNEL_HARDENING
- CRYPTO_BACKEND
"""
import socket
import os
import sys
import json
import time
import base64
from pathlib import Path
from collections import deque
import jsonschema
from jsonschema import validate
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Configuration
SOCKET_PATH = "/run/qwamos/bus.sock"
PUBLIC_KEY_PATH = Path.home() / ".qwamos" / "dom0" / "ed25519_pk"
SCHEMA_PATH = Path(__file__).parent.parent / "policy" / "policy.schema.json"
STATUS_PATH = Path("/etc/qwamos/status.json")
PENDING_PATH = Path("/etc/qwamos/pending.conf")

# Replay protection
NONCE_CACHE_SIZE = 10000
TIMESTAMP_SKEW_SEC = 300  # 5 minutes

# Policy classification
RUNTIME_SAFE_KEYS = {
    "RADIO_ISOLATION",
    "RADIO_HARDENING.level",
    "RADIO_IDLE_TIMEOUT_MIN",
    "TOR_ISOLATION",
    "VPN_KILL_SWITCH",
    "CLIPBOARD_ISOLATION",
    "DURESS.enabled",
    "DURESS.gesture",
    "GHOST.trigger"
}

REBOOT_REQUIRED_KEYS = {
    "BOOT_VERIFICATION",
    "KERNEL_HARDENING",
    "CRYPTO_BACKEND"
}

class QWAMOSDaemon:
    def __init__(self):
        self.nonce_cache = deque(maxlen=NONCE_CACHE_SIZE)
        self.verify_key = None
        self.schema = None
        self.current_policy = {}
        self.load_verify_key()
        self.load_schema()
        self.load_current_policy()

    def load_verify_key(self):
        """Load Ed25519 public verification key"""
        if not PUBLIC_KEY_PATH.exists():
            print(f"ERROR: Public key not found at {PUBLIC_KEY_PATH}")
            print("Run: cd dom0/keys && ./bootstrap_keys.py")
            sys.exit(1)

        key_bytes = PUBLIC_KEY_PATH.read_bytes()
        self.verify_key = VerifyKey(key_bytes)
        print(f"✓ Loaded public key from {PUBLIC_KEY_PATH}")

    def load_schema(self):
        """Load policy JSON schema for validation"""
        if not SCHEMA_PATH.exists():
            print(f"ERROR: Schema not found at {SCHEMA_PATH}")
            sys.exit(1)

        with open(SCHEMA_PATH) as f:
            self.schema = json.load(f)
        print(f"✓ Loaded policy schema from {SCHEMA_PATH}")

    def load_current_policy(self):
        """Load current policy from status.json"""
        if STATUS_PATH.exists():
            with open(STATUS_PATH) as f:
                data = json.load(f)
                self.current_policy = data.get("policy", {})
                print(f"✓ Loaded current policy: {len(self.current_policy)} keys")
        else:
            print("⚠ No existing policy found, starting with empty policy")

    def canonical_json(self, obj):
        """Generate canonical JSON for signing (sorted keys, no whitespace)"""
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))

    def verify_signature(self, msg, signature_b64):
        """Verify Ed25519 signature on canonical JSON of msg"""
        try:
            signature = base64.b64decode(signature_b64)
            msg_canonical = self.canonical_json(msg).encode('utf-8')
            self.verify_key.verify(msg_canonical, signature)
            return True
        except BadSignatureError:
            return False
        except Exception as e:
            print(f"⚠ Signature verification error: {e}")
            return False

    def check_replay(self, nonce, timestamp):
        """Check for replay attacks using nonce cache and timestamp"""
        # Check nonce uniqueness
        if nonce in self.nonce_cache:
            return False, "Nonce already seen (replay attack)"

        # Check timestamp freshness (within 5 minutes)
        current_time = int(time.time())
        if abs(current_time - timestamp) > TIMESTAMP_SKEW_SEC:
            return False, f"Timestamp skew too large: {abs(current_time - timestamp)}s"

        # Add nonce to cache
        self.nonce_cache.append(nonce)
        return True, "OK"

    def validate_policy(self, policy_updates):
        """Validate policy updates against JSON schema"""
        try:
            # Merge with current policy for validation
            test_policy = self.current_policy.copy()
            test_policy.update(policy_updates)
            validate(instance=test_policy, schema=self.schema)
            return True, "OK"
        except jsonschema.exceptions.ValidationError as e:
            return False, str(e)

    def apply_policy(self, policy_updates):
        """Apply policy updates, splitting runtime-safe vs reboot-required"""
        runtime_updates = {}
        reboot_updates = {}

        for key, value in policy_updates.items():
            if key in RUNTIME_SAFE_KEYS:
                runtime_updates[key] = value
            elif key in REBOOT_REQUIRED_KEYS:
                reboot_updates[key] = value
            else:
                print(f"⚠ Unknown policy key: {key}")

        # Apply runtime updates immediately
        if runtime_updates:
            self.current_policy.update(runtime_updates)
            self.save_status()
            print(f"✓ Applied {len(runtime_updates)} runtime policy updates")

        # Stage reboot-required updates to pending.conf
        if reboot_updates:
            self.stage_pending(reboot_updates)
            print(f"✓ Staged {len(reboot_updates)} reboot-required policy updates")

        return {
            "runtime_applied": list(runtime_updates.keys()),
            "reboot_staged": list(reboot_updates.keys())
        }

    def save_status(self):
        """Save current policy to status.json"""
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        status = {
            "policy": self.current_policy,
            "last_update": int(time.time())
        }
        with open(STATUS_PATH, 'w') as f:
            json.dump(status, f, indent=2)
        print(f"✓ Saved status to {STATUS_PATH}")

    def stage_pending(self, reboot_updates):
        """Stage reboot-required updates to pending.conf"""
        PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Load existing pending updates
        pending = {}
        if PENDING_PATH.exists():
            with open(PENDING_PATH) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        pending[key] = value

        # Merge new updates
        for key, value in reboot_updates.items():
            pending[key] = str(value)

        # Write back to pending.conf
        with open(PENDING_PATH, 'w') as f:
            f.write("# QWAMOS Pending Policy (apply on next boot)\n")
            f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for key, value in pending.items():
                f.write(f"{key}={value}\n")

        print(f"✓ Staged to {PENDING_PATH}")

    def handle_command(self, msg):
        """Handle incoming control bus command"""
        command = msg.get("command")
        args = msg.get("args", {})

        if command == "set_policy":
            # Validate policy updates
            valid, reason = self.validate_policy(args)
            if not valid:
                return {"status": "error", "reason": f"Invalid policy: {reason}"}

            # Apply policy updates
            result = self.apply_policy(args)
            return {"status": "ok", "result": result}

        elif command == "get_status":
            return {
                "status": "ok",
                "policy": self.current_policy,
                "pending": self.get_pending()
            }

        else:
            return {"status": "error", "reason": f"Unknown command: {command}"}

    def get_pending(self):
        """Get list of pending reboot-required updates"""
        if not PENDING_PATH.exists():
            return {}

        pending = {}
        with open(PENDING_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    pending[key] = value
        return pending

    def process_message(self, data):
        """Process incoming control bus message"""
        try:
            envelope = json.loads(data.decode('utf-8'))
            msg = envelope.get("msg")
            signature = envelope.get("signature")

            if not msg or not signature:
                return {"status": "error", "reason": "Missing msg or signature"}

            # Verify signature
            if not self.verify_signature(msg, signature):
                return {"status": "error", "reason": "Invalid signature"}

            # Check replay protection
            nonce = msg.get("nonce")
            timestamp = msg.get("timestamp")
            if not nonce or not timestamp:
                return {"status": "error", "reason": "Missing nonce or timestamp"}

            replay_ok, replay_msg = self.check_replay(nonce, timestamp)
            if not replay_ok:
                return {"status": "error", "reason": replay_msg}

            # Handle command
            return self.handle_command(msg)

        except json.JSONDecodeError as e:
            return {"status": "error", "reason": f"Invalid JSON: {e}"}
        except Exception as e:
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

        # Set socket permissions (0660 - owner and group can read/write)
        os.chmod(SOCKET_PATH, 0o660)

        print(f"✓ QWAMOS Policy Daemon listening on {SOCKET_PATH}")
        print(f"  Runtime-safe keys: {len(RUNTIME_SAFE_KEYS)}")
        print(f"  Reboot-required keys: {len(REBOOT_REQUIRED_KEYS)}")
        print()

        try:
            while True:
                conn, addr = sock.accept()
                try:
                    # Read message (max 64KB)
                    data = conn.recv(65536)
                    if data:
                        # Process message
                        response = self.process_message(data)

                        # Send response
                        conn.sendall(json.dumps(response).encode('utf-8'))
                finally:
                    conn.close()

        except KeyboardInterrupt:
            print("\n✓ Shutting down gracefully...")
        finally:
            sock.close()
            if os.path.exists(SOCKET_PATH):
                os.remove(SOCKET_PATH)

def main():
    print("=" * 60)
    print("QWAMOS Policy Daemon (qwamosd)")
    print("=" * 60)

    daemon = QWAMOSDaemon()
    daemon.run()

if __name__ == "__main__":
    main()
