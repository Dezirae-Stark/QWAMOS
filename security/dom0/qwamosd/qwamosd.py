#!/usr/bin/env python3
"""
QWAMOS Policy Daemon (Dom0)
Watches policy file, validates, signs, and distributes updates to VMs
Handles runtime vs reboot-required logic
"""

import os
import sys
import json
import time
import hashlib
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
POLICY_FILE = Path('/etc/qwamos/policy.conf')
PENDING_FILE = Path('/etc/qwamos/pending.conf')
SCHEMA_FILE = Path('/usr/share/qwamos/policy.schema.json')
SIGNING_KEY = Path('/etc/qwamos/keys/dom0.sec')
CONTROL_BUS_DIR = Path('/var/run/qwamos/control-bus')

# Toggle classification
RUNTIME_SAFE_TOGGLES = {
    'RADIO_ISOLATION',
    'RADIO_HARDENING.level',
    'RADIO_IDLE_TIMEOUT_MIN',
    'TRUSTED_OVERLAY',
    'REMOTE_ATTESTATION',
    'PANIC_GESTURE',
    'DURESS_PROFILE',
    'E2E_TUNNEL_POLICY',
    'AUDIT_UPLOAD'
}

REBOOT_REQUIRED_TOGGLES = {
    'VERIFIED_BOOT_ENFORCE',
    'KERNEL_HARDENING',
    'BASEBAND_DRIVER_DISABLE'
}

# VM targets for each toggle
TOGGLE_TARGETS = {
    'RADIO_ISOLATION': ['gateway_vm'],
    'RADIO_HARDENING.level': ['gateway_vm'],
    'RADIO_IDLE_TIMEOUT_MIN': ['gateway_vm'],
    'TRUSTED_OVERLAY': ['ui_vm'],
    'REMOTE_ATTESTATION': ['attestation'],
    'PANIC_GESTURE': ['panic'],
    'DURESS_PROFILE': ['dom0'],
    'E2E_TUNNEL_POLICY': ['gateway_vm'],
    'AUDIT_UPLOAD': ['gateway_vm'],
    'VERIFIED_BOOT_ENFORCE': ['bootloader'],
    'KERNEL_HARDENING': ['kernel'],
    'BASEBAND_DRIVER_DISABLE': ['kernel']
}

class PolicyDaemon:
    def __init__(self):
        self.current_policy = {}
        self.load_current_policy()

    def load_current_policy(self):
        """Load currently active policy"""
        if not POLICY_FILE.exists():
            print(f"⚠️  Policy file not found: {POLICY_FILE}")
            self.current_policy = {}
            return

        for line in POLICY_FILE.read_text().splitlines():
            if '=' in line and not line.startswith('#') and not line.startswith('SIG='):
                key, value = line.split('=', 1)
                self.current_policy[key.strip()] = value.strip()

        print(f"✅ Loaded policy: {len(self.current_policy)} settings")

    def validate_policy(self, policy_text):
        """Validate policy against schema"""
        # Parse policy
        policy = {}
        for line in policy_text.splitlines():
            if '=' in line and not line.startswith('#') and not line.startswith('SIG='):
                key, value = line.split('=', 1)
                policy[key.strip()] = value.strip()

        # Load schema
        if not SCHEMA_FILE.exists():
            print(f"⚠️  Schema not found, skipping validation")
            return True, policy

        schema = json.loads(SCHEMA_FILE.read_text())

        # Validate each key
        for key, value in policy.items():
            if key not in schema:
                return False, f"Unknown key: {key}"

            spec = schema[key]

            # Type check
            if spec['type'] == 'enum':
                if value not in spec['values']:
                    return False, f"{key}: Invalid value '{value}', must be one of {spec['values']}"

            elif spec['type'] == 'int':
                try:
                    val_int = int(value)
                    if 'min' in spec and val_int < spec['min']:
                        return False, f"{key}: Value {val_int} < min {spec['min']}"
                    if 'max' in spec and val_int > spec['max']:
                        return False, f"{key}: Value {val_int} > max {spec['max']}"
                except ValueError:
                    return False, f"{key}: Not an integer: {value}"

            elif spec['type'] == 'bool':
                if value not in ['on', 'off', 'true', 'false']:
                    return False, f"{key}: Must be on/off or true/false"

        return True, policy

    def verify_signature(self, policy_text):
        """Verify Ed25519 signature on policy"""
        lines = policy_text.splitlines()

        # Extract signature line
        sig_line = [l for l in lines if l.startswith('SIG=')]
        if not sig_line:
            return False, "No signature found"

        signature = sig_line[0].split('=', 1)[1]

        # Remove signature for verification
        unsigned_text = '\n'.join([l for l in lines if not l.startswith('SIG=')])

        # Verify with signify or similar
        try:
            result = subprocess.run(
                ['signify', '-V', '-p', '/etc/qwamos/keys/dom0.pub', '-m', '-'],
                input=unsigned_text.encode(),
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, "Signature valid"
            else:
                return False, f"Signature invalid: {result.stderr.decode()}"

        except Exception as e:
            return False, f"Signature verification error: {e}"

    def sign_policy(self, policy_text):
        """Sign policy with Dom0 Ed25519 key"""
        try:
            result = subprocess.run(
                ['signify', '-S', '-s', str(SIGNING_KEY), '-m', '-'],
                input=policy_text.encode(),
                capture_output=True,
                timeout=5
            )

            if result.returncode == 0:
                signature = result.stdout.decode().strip()
                return f"{policy_text}\nSIG={signature}"
            else:
                raise Exception(f"Signing failed: {result.stderr.decode()}")

        except Exception as e:
            raise Exception(f"Signing error: {e}")

    def detect_changes(self, new_policy):
        """Compare new policy to current, return changed toggles"""
        changes = {}

        for key, value in new_policy.items():
            if key not in self.current_policy or self.current_policy[key] != value:
                changes[key] = {
                    'old': self.current_policy.get(key),
                    'new': value
                }

        return changes

    def classify_changes(self, changes):
        """Classify changes as runtime-safe or reboot-required"""
        runtime_safe = {}
        reboot_required = {}

        for key, change in changes.items():
            if key in RUNTIME_SAFE_TOGGLES:
                runtime_safe[key] = change
            elif key in REBOOT_REQUIRED_TOGGLES:
                reboot_required[key] = change
            else:
                print(f"⚠️  Unknown toggle classification: {key}")
                runtime_safe[key] = change  # Default to runtime

        return runtime_safe, reboot_required

    def apply_runtime_changes(self, changes):
        """Apply runtime-safe changes immediately"""
        print(f"\n{'='*60}")
        print(f"  Applying Runtime Changes ({len(changes)} toggles)")
        print(f"{'='*60}\n")

        for key, change in changes.items():
            print(f"  {key}: {change['old']} → {change['new']}")

            # Get target VMs
            targets = TOGGLE_TARGETS.get(key, [])

            for target in targets:
                self.send_to_target(target, {key: change['new']})

        print(f"\n✅ Runtime changes applied\n")

    def queue_reboot_required(self, changes):
        """Queue changes that require reboot"""
        print(f"\n{'='*60}")
        print(f"  Reboot Required ({len(changes)} toggles)")
        print(f"{'='*60}\n")

        for key, change in changes.items():
            print(f"  {key}: {change['old']} → {change['new']}")

        # Write to pending file
        pending_lines = [f"{k}={v['new']}" for k, v in changes.items()]
        PENDING_FILE.write_text('\n'.join(pending_lines))

        print(f"\n⚠️  Changes staged in {PENDING_FILE}")
        print(f"   Reboot required to apply\n")

        # Prompt user
        self.prompt_reboot(changes)

    def prompt_reboot(self, changes):
        """Show reboot prompt to user"""
        change_desc = ', '.join(changes.keys())

        print(f"{'='*60}")
        print(f"  REBOOT REQUIRED")
        print(f"{'='*60}")
        print(f"\nChanges: {change_desc}")
        print(f"\nThese settings require a system reboot to apply.")
        print(f"Reboot now? (y/n): ", end='', flush=True)

        # In production: this would be a GUI dialog
        # For demo: CLI prompt
        try:
            response = input().strip().lower()

            if response == 'y':
                print("\n🔄 Rebooting system...")
                time.sleep(2)
                subprocess.run(['systemctl', 'reboot'])
            else:
                print("\n✅ Reboot postponed. Changes will apply on next boot.")

        except EOFError:
            # Non-interactive mode
            print("\nNon-interactive mode: reboot postponed")

    def send_to_target(self, target, payload):
        """Send signed update to target VM via control bus"""
        message = {
            'version': 1,
            'timestamp': int(time.time()),
            'target': target,
            'command': 'reload_policy',
            'payload': payload,
            'nonce': os.urandom(16).hex()
        }

        # Canonical JSON (sorted keys, no whitespace)
        canonical = json.dumps(message, sort_keys=True, separators=(',', ':'))

        # Sign
        signature = self.sign_message(canonical)
        message['signature'] = signature

        # Write to control bus (virtio-serial channel)
        bus_path = CONTROL_BUS_DIR / f"{target}.sock"

        if bus_path.exists():
            with open(bus_path, 'w') as bus:
                bus.write(json.dumps(message) + '\n')

            print(f"  → Sent to {target}: {payload}")
        else:
            print(f"  ⚠️  Control bus not found: {bus_path}")

    def sign_message(self, message):
        """Sign message with Dom0 key"""
        result = subprocess.run(
            ['signify', '-S', '-s', str(SIGNING_KEY), '-m', '-'],
            input=message.encode(),
            capture_output=True,
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.decode().strip()
        else:
            raise Exception(f"Message signing failed: {result.stderr.decode()}")

    def handle_policy_change(self):
        """Main handler for policy file changes"""
        print(f"\n📝 Policy file changed: {POLICY_FILE}")

        # Read new policy
        policy_text = POLICY_FILE.read_text()

        # Validate
        valid, result = self.validate_policy(policy_text)
        if not valid:
            print(f"❌ Validation failed: {result}")
            return

        new_policy = result
        print(f"✅ Policy validated: {len(new_policy)} settings")

        # Detect changes
        changes = self.detect_changes(new_policy)

        if not changes:
            print("ℹ️  No changes detected")
            return

        print(f"\n📊 Detected {len(changes)} changes:")
        for key, change in changes.items():
            print(f"   {key}: {change['old']} → {change['new']}")

        # Classify
        runtime_safe, reboot_required = self.classify_changes(changes)

        # Apply runtime changes
        if runtime_safe:
            self.apply_runtime_changes(runtime_safe)

        # Queue reboot-required changes
        if reboot_required:
            self.queue_reboot_required(reboot_required)

        # Update current policy
        self.current_policy = new_policy

    def check_pending_on_boot(self):
        """Apply pending changes on boot"""
        if not PENDING_FILE.exists():
            return

        print(f"\n🔄 Applying pending changes from previous session...")

        pending_text = PENDING_FILE.read_text()
        pending = {}

        for line in pending_text.splitlines():
            if '=' in line:
                key, value = line.split('=', 1)
                pending[key.strip()] = value.strip()

        # Apply to bootloader/kernel
        for key, value in pending.items():
            if key == 'KERNEL_HARDENING':
                self.apply_kernel_hardening(value)
            elif key == 'VERIFIED_BOOT_ENFORCE':
                self.apply_verified_boot(value)
            elif key == 'BASEBAND_DRIVER_DISABLE':
                self.apply_baseband_disable(value)

        # Merge into main policy
        current = POLICY_FILE.read_text()
        for key, value in pending.items():
            # Replace or add key
            current = self.replace_policy_key(current, key, value)

        POLICY_FILE.write_text(current)

        # Clear pending
        PENDING_FILE.unlink()

        print(f"✅ Pending changes applied and cleared")

    def replace_policy_key(self, policy_text, key, value):
        """Replace or add key in policy text"""
        lines = policy_text.splitlines()
        found = False

        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                found = True
                break

        if not found:
            # Add before signature
            sig_idx = next((i for i, l in enumerate(lines) if l.startswith('SIG=')), len(lines))
            lines.insert(sig_idx, f"{key}={value}")

        return '\n'.join(lines)

    def apply_kernel_hardening(self, level):
        """Apply kernel hardening settings"""
        print(f"  Applying kernel hardening: {level}")

        if level == 'strict':
            # Enable lockdown mode
            subprocess.run(['echo', 'integrity', '>', '/sys/kernel/security/lockdown'])

            # KASLR enforcement (via bootloader)
            subprocess.run(['fw_setenv', 'bootargs', 'kaslr'])

        print(f"  ✅ Kernel hardening applied")

    def apply_verified_boot(self, mode):
        """Configure verified boot enforcement"""
        print(f"  Configuring verified boot: {mode}")

        # Write to bootloader environment
        subprocess.run(['fw_setenv', 'qwamos_boot_enforce', mode])

        print(f"  ✅ Verified boot configured")

    def apply_baseband_disable(self, state):
        """Enable/disable baseband driver"""
        print(f"  Baseband driver: {state}")

        if state == 'on':
            # Blacklist baseband module
            Path('/etc/modprobe.d/qwamos-baseband.conf').write_text('blacklist rmnet_data\n')
        else:
            # Remove blacklist
            blacklist_file = Path('/etc/modprobe.d/qwamos-baseband.conf')
            if blacklist_file.exists():
                blacklist_file.unlink()

        print(f"  ✅ Baseband configuration updated")

    def run(self):
        """Main daemon loop"""
        print(f"\n{'='*60}")
        print(f"  QWAMOS Policy Daemon (qwamosd)")
        print(f"{'='*60}\n")
        print(f"Policy file: {POLICY_FILE}")
        print(f"Signing key: {SIGNING_KEY}")
        print(f"Control bus: {CONTROL_BUS_DIR}")
        print()

        # Check for pending changes on boot
        self.check_pending_on_boot()

        # Watch policy file
        print(f"👁️  Watching for policy changes...\n")

        class PolicyHandler(FileSystemEventHandler):
            def __init__(self, daemon):
                self.daemon = daemon

            def on_modified(self, event):
                if event.src_path == str(POLICY_FILE):
                    self.daemon.handle_policy_change()

        observer = Observer()
        observer.schedule(PolicyHandler(self), str(POLICY_FILE.parent), recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\n\n⏹️  qwamosd stopped")

        observer.join()

def main():
    # Ensure required directories exist
    POLICY_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTROL_BUS_DIR.mkdir(parents=True, exist_ok=True)

    daemon = PolicyDaemon()
    daemon.run()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
