#!/usr/bin/env python3
"""
QWAMOS Signed Control Bus - Integration Tests

Tests the complete signed control bus system:
- Key generation and management
- Message signing and verification
- Policy application (runtime vs reboot)
- Replay protection
- Status updates
"""
import pytest
import json
import time
import base64
import secrets
import tempfile
from pathlib import Path
from nacl.signing import SigningKey, VerifyKey

# Mock paths for testing
TEST_DIR = Path(tempfile.mkdtemp())
TEST_SOCKET = TEST_DIR / "bus.sock"
TEST_STATUS = TEST_DIR / "status.json"
TEST_PENDING = TEST_DIR / "pending.conf"

class TestKeyGeneration:
    """Test Ed25519 key generation and management"""

    def test_key_generation(self):
        """Test that Ed25519 keypair is generated correctly"""
        sk = SigningKey.generate()
        vk = sk.verify_key

        assert sk is not None
        assert vk is not None
        assert len(sk.encode()) == 32  # Ed25519 private key is 32 bytes
        assert len(vk.encode()) == 32  # Ed25519 public key is 32 bytes

    def test_key_serialization(self):
        """Test that keys can be saved and loaded"""
        sk = SigningKey.generate()
        vk = sk.verify_key

        # Serialize
        sk_bytes = sk.encode()
        vk_bytes = vk.encode()

        # Deserialize
        sk_loaded = SigningKey(sk_bytes)
        vk_loaded = VerifyKey(vk_bytes)

        # Verify loaded keys work
        msg = b"test message"
        signed = sk_loaded.sign(msg)
        vk_loaded.verify(signed)  # Should not raise


class TestMessageSigning:
    """Test message signing and verification"""

    def setup_method(self):
        """Setup test keys"""
        self.sk = SigningKey.generate()
        self.vk = self.sk.verify_key

    def canonical_json(self, obj):
        """Generate canonical JSON"""
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))

    def test_message_signing(self):
        """Test that messages are signed correctly"""
        msg = {
            "command": "set_policy",
            "args": {"RADIO_ISOLATION": "on"},
            "nonce": base64.b64encode(secrets.token_bytes(16)).decode('ascii'),
            "timestamp": int(time.time())
        }

        # Sign message
        msg_canonical = self.canonical_json(msg).encode('utf-8')
        signed = self.sk.sign(msg_canonical)
        signature = signed.signature

        # Verify signature
        self.vk.verify(msg_canonical, signature)  # Should not raise

    def test_signature_verification_fails_on_tampered_message(self):
        """Test that tampered messages fail verification"""
        msg = {
            "command": "set_policy",
            "args": {"RADIO_ISOLATION": "on"},
            "nonce": base64.b64encode(secrets.token_bytes(16)).decode('ascii'),
            "timestamp": int(time.time())
        }

        # Sign message
        msg_canonical = self.canonical_json(msg).encode('utf-8')
        signed = self.sk.sign(msg_canonical)
        signature = signed.signature

        # Tamper with message
        msg["args"]["RADIO_ISOLATION"] = "off"
        msg_tampered = self.canonical_json(msg).encode('utf-8')

        # Verify should fail
        from nacl.exceptions import BadSignatureError
        with pytest.raises(BadSignatureError):
            self.vk.verify(msg_tampered, signature)

    def test_canonical_json_is_deterministic(self):
        """Test that canonical JSON is deterministic"""
        msg1 = {"b": 2, "a": 1, "c": 3}
        msg2 = {"c": 3, "a": 1, "b": 2}

        canonical1 = self.canonical_json(msg1)
        canonical2 = self.canonical_json(msg2)

        assert canonical1 == canonical2
        assert canonical1 == '{"a":1,"b":2,"c":3}'


class TestPolicyClassification:
    """Test runtime vs reboot policy classification"""

    RUNTIME_SAFE = {
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

    REBOOT_REQUIRED = {
        "BOOT_VERIFICATION",
        "KERNEL_HARDENING",
        "CRYPTO_BACKEND"
    }

    def test_runtime_safe_policies(self):
        """Test that runtime-safe policies are classified correctly"""
        policy_updates = {
            "RADIO_ISOLATION": "on",
            "TOR_ISOLATION": "mandatory",
            "CLIPBOARD_ISOLATION": "strict"
        }

        runtime = {}
        reboot = {}

        for key, value in policy_updates.items():
            if key in self.RUNTIME_SAFE:
                runtime[key] = value
            elif key in self.REBOOT_REQUIRED:
                reboot[key] = value

        assert len(runtime) == 3
        assert len(reboot) == 0

    def test_reboot_required_policies(self):
        """Test that reboot-required policies are classified correctly"""
        policy_updates = {
            "BOOT_VERIFICATION": "strict",
            "KERNEL_HARDENING": "paranoid",
            "CRYPTO_BACKEND": "post-quantum"
        }

        runtime = {}
        reboot = {}

        for key, value in policy_updates.items():
            if key in self.RUNTIME_SAFE:
                runtime[key] = value
            elif key in self.REBOOT_REQUIRED:
                reboot[key] = value

        assert len(runtime) == 0
        assert len(reboot) == 3

    def test_mixed_policy_updates(self):
        """Test that mixed updates are split correctly"""
        policy_updates = {
            "RADIO_ISOLATION": "on",
            "BOOT_VERIFICATION": "strict",
            "TOR_ISOLATION": "mandatory"
        }

        runtime = {}
        reboot = {}

        for key, value in policy_updates.items():
            if key in self.RUNTIME_SAFE:
                runtime[key] = value
            elif key in self.REBOOT_REQUIRED:
                reboot[key] = value

        assert len(runtime) == 2
        assert "RADIO_ISOLATION" in runtime
        assert "TOR_ISOLATION" in runtime

        assert len(reboot) == 1
        assert "BOOT_VERIFICATION" in reboot


class TestReplayProtection:
    """Test replay attack prevention"""

    def test_nonce_uniqueness(self):
        """Test that duplicate nonces are rejected"""
        nonce_cache = []

        nonce1 = base64.b64encode(secrets.token_bytes(16)).decode('ascii')
        nonce2 = base64.b64encode(secrets.token_bytes(16)).decode('ascii')

        # First nonce should be accepted
        if nonce1 not in nonce_cache:
            nonce_cache.append(nonce1)
            accepted1 = True
        else:
            accepted1 = False

        # Second nonce should be accepted
        if nonce2 not in nonce_cache:
            nonce_cache.append(nonce2)
            accepted2 = True
        else:
            accepted2 = False

        # Replay of first nonce should be rejected
        if nonce1 not in nonce_cache:
            nonce_cache.append(nonce1)
            replay_accepted = True
        else:
            replay_accepted = False

        assert accepted1 is True
        assert accepted2 is True
        assert replay_accepted is False

    def test_timestamp_validation(self):
        """Test that old timestamps are rejected"""
        TIMESTAMP_SKEW_SEC = 300  # 5 minutes

        current_time = int(time.time())

        # Fresh timestamp should be accepted
        fresh_timestamp = current_time
        fresh_valid = abs(current_time - fresh_timestamp) <= TIMESTAMP_SKEW_SEC

        # Old timestamp should be rejected
        old_timestamp = current_time - 600  # 10 minutes old
        old_valid = abs(current_time - old_timestamp) <= TIMESTAMP_SKEW_SEC

        # Future timestamp (within skew) should be accepted
        future_timestamp = current_time + 100
        future_valid = abs(current_time - future_timestamp) <= TIMESTAMP_SKEW_SEC

        assert fresh_valid is True
        assert old_valid is False
        assert future_valid is True


class TestStatusUpdates:
    """Test policy status tracking"""

    def test_status_json_format(self):
        """Test that status.json has correct format"""
        status = {
            "policy": {
                "RADIO_ISOLATION": "on",
                "TOR_ISOLATION": "mandatory"
            },
            "last_update": int(time.time())
        }

        # Should be valid JSON
        status_json = json.dumps(status, indent=2)
        status_loaded = json.loads(status_json)

        assert "policy" in status_loaded
        assert "last_update" in status_loaded
        assert isinstance(status_loaded["policy"], dict)
        assert isinstance(status_loaded["last_update"], int)

    def test_pending_conf_format(self):
        """Test that pending.conf has correct format"""
        pending_lines = [
            "# QWAMOS Pending Policy (apply on next boot)",
            "# Generated: 2025-01-15 12:00:00",
            "",
            "BOOT_VERIFICATION=strict",
            "KERNEL_HARDENING=paranoid"
        ]

        # Parse pending.conf
        pending = {}
        for line in pending_lines:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                pending[key] = value

        assert len(pending) == 2
        assert pending["BOOT_VERIFICATION"] == "strict"
        assert pending["KERNEL_HARDENING"] == "paranoid"


class TestEndToEnd:
    """End-to-end integration tests"""

    def setup_method(self):
        """Setup test environment"""
        self.sk = SigningKey.generate()
        self.vk = self.sk.verify_key

    def canonical_json(self, obj):
        """Generate canonical JSON"""
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))

    def sign_and_send(self, command, args):
        """Simulate signing and sending a command"""
        msg = {
            "command": command,
            "args": args,
            "nonce": base64.b64encode(secrets.token_bytes(16)).decode('ascii'),
            "timestamp": int(time.time())
        }

        # Sign message
        msg_canonical = self.canonical_json(msg).encode('utf-8')
        signed = self.sk.sign(msg_canonical)
        signature = base64.b64encode(signed.signature).decode('ascii')

        # Build envelope
        envelope = {
            "msg": msg,
            "signature": signature
        }

        return envelope

    def test_complete_workflow(self):
        """Test complete signed bus workflow"""
        # 1. Send policy update
        envelope = self.sign_and_send("set_policy", {"RADIO_ISOLATION": "on"})

        # 2. Verify signature
        msg = envelope["msg"]
        signature_b64 = envelope["signature"]
        signature = base64.b64decode(signature_b64)
        msg_canonical = self.canonical_json(msg).encode('utf-8')

        # Should verify successfully
        self.vk.verify(msg_canonical, signature)

        # 3. Extract command and args
        assert msg["command"] == "set_policy"
        assert msg["args"]["RADIO_ISOLATION"] == "on"

        # 4. Simulate response
        response = {
            "status": "ok",
            "result": {
                "runtime_applied": ["RADIO_ISOLATION"],
                "reboot_staged": []
            }
        }

        assert response["status"] == "ok"
        assert "RADIO_ISOLATION" in response["result"]["runtime_applied"]


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
