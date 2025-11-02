#!/usr/bin/env python3
"""
QWAMOS Control CLI (qwamosctl)

Signed control bus client for sending policy updates to qwamosd.
Automatically bootstraps Ed25519 keys on first run.

Usage:
  # Set single policy key
  qwamosctl set RADIO_ISOLATION on

  # Apply policy from file
  qwamosctl --policy-file /etc/qwamos/policy.json apply

  # Get current status
  qwamosctl status

  # Dry-run policy update
  qwamosctl set RADIO_ISOLATION on --dry-run
"""
import argparse
import json
import os
import sys
import time
import socket
import base64
import secrets
from pathlib import Path
from nacl.signing import SigningKey

# Configuration
SOCKET_PATH = "/run/qwamos/bus.sock"
PRIVATE_KEY_PATH = Path.home() / ".qwamos" / "dom0" / "ed25519_sk"
BOOTSTRAP_SCRIPT = Path(__file__).parent.parent / "keys" / "bootstrap_keys.py"

class QWAMOSClient:
    def __init__(self):
        self.signing_key = None
        self.ensure_keys()

    def ensure_keys(self):
        """Ensure Ed25519 keypair exists, bootstrap if needed"""
        if not PRIVATE_KEY_PATH.exists():
            print("⚠ Ed25519 keys not found, bootstrapping...")
            if BOOTSTRAP_SCRIPT.exists():
                import subprocess
                subprocess.run([sys.executable, str(BOOTSTRAP_SCRIPT)], check=True)
            else:
                print(f"ERROR: Bootstrap script not found at {BOOTSTRAP_SCRIPT}")
                sys.exit(1)

        # Load private key
        key_bytes = PRIVATE_KEY_PATH.read_bytes()
        self.signing_key = SigningKey(key_bytes)
        print(f"✓ Loaded signing key from {PRIVATE_KEY_PATH}")

    def canonical_json(self, obj):
        """Generate canonical JSON for signing (sorted keys, no whitespace)"""
        return json.dumps(obj, sort_keys=True, separators=(',', ':'))

    def sign_message(self, msg):
        """Sign message using Ed25519 private key"""
        msg_canonical = self.canonical_json(msg).encode('utf-8')
        signed = self.signing_key.sign(msg_canonical)
        # Return just the signature (not the combined message+signature)
        return base64.b64encode(signed.signature).decode('ascii')

    def generate_nonce(self):
        """Generate 16-byte random nonce"""
        return base64.b64encode(secrets.token_bytes(16)).decode('ascii')

    def send_command(self, command, args, dry_run=False):
        """Send signed command to qwamosd over Unix socket"""
        # Build message
        msg = {
            "command": command,
            "args": args,
            "nonce": self.generate_nonce(),
            "timestamp": int(time.time())
        }

        # Sign message
        signature = self.sign_message(msg)

        # Build envelope
        envelope = {
            "msg": msg,
            "signature": signature
        }

        if dry_run:
            print("\n=== DRY RUN ===")
            print("Would send:")
            print(json.dumps(envelope, indent=2))
            return {"status": "dry_run"}

        # Connect to Unix socket
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(SOCKET_PATH)
        except FileNotFoundError:
            print(f"ERROR: qwamosd not running (socket not found: {SOCKET_PATH})")
            print("Start daemon: cd dom0/qwamosd && sudo ./qwamosd.py")
            sys.exit(1)
        except PermissionError:
            print(f"ERROR: Permission denied connecting to {SOCKET_PATH}")
            print("Run with sudo or ensure your user is in the qwamos group")
            sys.exit(1)

        try:
            # Send message
            sock.sendall(json.dumps(envelope).encode('utf-8'))

            # Receive response
            response_data = sock.recv(65536)
            response = json.loads(response_data.decode('utf-8'))
            return response

        finally:
            sock.close()

    def set_policy(self, key, value, dry_run=False):
        """Set a single policy key"""
        args = {key: value}
        response = self.send_command("set_policy", args, dry_run=dry_run)

        if dry_run:
            return

        if response.get("status") == "ok":
            result = response.get("result", {})
            runtime = result.get("runtime_applied", [])
            reboot = result.get("reboot_staged", [])

            print("✓ Policy update successful")
            if runtime:
                print(f"  Applied immediately: {', '.join(runtime)}")
            if reboot:
                print(f"  Staged for reboot: {', '.join(reboot)}")
                print("  ⚠ Reboot required to apply changes")
        else:
            print(f"✗ Policy update failed: {response.get('reason')}")
            sys.exit(1)

    def apply_policy_file(self, policy_file, dry_run=False):
        """Apply policy updates from JSON file"""
        if not Path(policy_file).exists():
            print(f"ERROR: Policy file not found: {policy_file}")
            sys.exit(1)

        with open(policy_file) as f:
            policy = json.load(f)

        response = self.send_command("set_policy", policy, dry_run=dry_run)

        if dry_run:
            return

        if response.get("status") == "ok":
            result = response.get("result", {})
            runtime = result.get("runtime_applied", [])
            reboot = result.get("reboot_staged", [])

            print(f"✓ Policy file applied: {policy_file}")
            print(f"  Runtime updates: {len(runtime)}")
            print(f"  Reboot-required: {len(reboot)}")
            if reboot:
                print(f"  ⚠ Reboot required: {', '.join(reboot)}")
        else:
            print(f"✗ Policy apply failed: {response.get('reason')}")
            sys.exit(1)

    def get_status(self):
        """Get current policy status"""
        response = self.send_command("get_status", {})

        if response.get("status") == "ok":
            policy = response.get("policy", {})
            pending = response.get("pending", {})

            print("\n=== QWAMOS Policy Status ===\n")
            print("Current Policy:")
            if policy:
                for key, value in sorted(policy.items()):
                    print(f"  {key} = {value}")
            else:
                print("  (no policy set)")

            print("\nPending (reboot required):")
            if pending:
                for key, value in sorted(pending.items()):
                    print(f"  {key} = {value}")
            else:
                print("  (none)")
            print()
        else:
            print(f"✗ Status query failed: {response.get('reason')}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="QWAMOS Control CLI - Send signed commands to qwamosd",
        epilog="""
Examples:
  qwamosctl set RADIO_ISOLATION on
  qwamosctl --policy-file /etc/qwamos/policy.json apply
  qwamosctl status
  qwamosctl set BOOT_VERIFICATION strict --dry-run
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("action",
                       choices=["set", "apply", "status"],
                       help="Action to perform")
    parser.add_argument("key", nargs="?",
                       help="Policy key (for 'set' action)")
    parser.add_argument("value", nargs="?",
                       help="Policy value (for 'set' action)")
    parser.add_argument("--policy-file",
                       help="Path to policy JSON file (for 'apply' action)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be sent without actually sending")

    args = parser.parse_args()

    # Validate arguments
    if args.action == "set":
        if not args.key or not args.value:
            parser.error("'set' requires KEY and VALUE arguments")
    elif args.action == "apply":
        if not args.policy_file:
            parser.error("'apply' requires --policy-file argument")

    # Create client
    client = QWAMOSClient()

    # Execute action
    if args.action == "set":
        client.set_policy(args.key, args.value, dry_run=args.dry_run)
    elif args.action == "apply":
        client.apply_policy_file(args.policy_file, dry_run=args.dry_run)
    elif args.action == "status":
        client.get_status()

if __name__ == "__main__":
    main()
