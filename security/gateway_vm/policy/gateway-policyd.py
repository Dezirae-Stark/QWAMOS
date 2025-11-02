#!/usr/bin/env python3
"""
QWAMOS Gateway VM Policy Daemon
Listens on control bus for policy updates from Dom0
Applies changes to Gateway VM services
"""

import os
import sys
import json
import subprocess
from pathlib import Path

CONTROL_BUS = '/var/run/qwamos/control-bus/gateway_vm.sock'
DOM0_PUBKEY = Path('/etc/qwamos/keys/dom0.pub')
FIREWALL_BASIC = Path('/data/qwamos/firewall/rules-basic.sh')
FIREWALL_STRICT = Path('/data/qwamos/firewall/rules-strict.sh')
RADIO_CTRL = Path('/data/qwamos/radio/radio-ctrl.sh')

class GatewayPolicyDaemon:
    def __init__(self):
        self.current_policy = {}

    def verify_signature(self, message, signature):
        """Verify Ed25519 signature from Dom0"""
        try:
            result = subprocess.run(
                ['signify', '-V', '-p', str(DOM0_PUBKEY), '-m', '-'],
                input=message.encode(),
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            print(f"⚠️  Signature verification error: {e}")
            return False

    def apply_policy_change(self, key, value):
        """Apply a single policy change"""
        print(f"📝 Applying: {key} = {value}")

        if key == 'RADIO_ISOLATION':
            self.apply_radio_isolation(value)

        elif key == 'RADIO_HARDENING.level':
            self.apply_radio_hardening(value)

        elif key == 'RADIO_IDLE_TIMEOUT_MIN':
            self.apply_idle_timeout(value)

        elif key == 'E2E_TUNNEL_POLICY':
            self.apply_tunnel_policy(value)

        else:
            print(f"⚠️  Unknown policy key: {key}")

    def apply_radio_isolation(self, state):
        """Start/stop Gateway VM"""
        if state == 'on':
            print("✅ Radio isolation: Gateway VM active")
            # In production: start Gateway VM services
            subprocess.run(['systemctl', 'start', 'gateway-services'])
        else:
            print("⚠️  Radio isolation disabled: Gateway VM stopped")
            subprocess.run(['systemctl', 'stop', 'gateway-services'])

    def apply_radio_hardening(self, level):
        """Apply firewall rules based on hardening level"""
        print(f"🔒 Radio hardening: {level}")

        if level == 'strict':
            subprocess.run(['/bin/bash', str(FIREWALL_STRICT)])
        else:
            subprocess.run(['/bin/bash', str(FIREWALL_BASIC)])

        print(f"✅ Firewall rules applied: {level}")

    def apply_idle_timeout(self, timeout_min):
        """Update radio idle timeout"""
        print(f"⏱️  Radio idle timeout: {timeout_min} min")

        # Update environment variable for radio-ctrl
        with open('/etc/environment', 'r') as f:
            env = f.read()

        # Replace or add timeout
        if 'RADIO_IDLE_TIMEOUT_MIN' in env:
            env = '\n'.join([
                line if not line.startswith('RADIO_IDLE_TIMEOUT_MIN')
                else f'RADIO_IDLE_TIMEOUT_MIN={timeout_min}'
                for line in env.splitlines()
            ])
        else:
            env += f'\nRADIO_IDLE_TIMEOUT_MIN={timeout_min}\n'

        with open('/etc/environment', 'w') as f:
            f.write(env)

        # Restart radio monitor
        subprocess.run(['systemctl', 'restart', 'radio-monitor'])

        print(f"✅ Idle timeout updated")

    def apply_tunnel_policy(self, policy):
        """Configure egress tunnel routing"""
        print(f"🌐 Tunnel policy: {policy}")

        if policy == 'tor-only':
            # Configure InviZible Pro for Tor-only
            subprocess.run([
                'am', 'broadcast',
                '-a', 'pan.alexander.tordnscrypt.action.SET_MODE',
                '--es', 'mode', 'tor-only'
            ])

        elif policy == 'tor+vpn':
            # Enable Tor + VPN layering
            subprocess.run([
                'am', 'broadcast',
                '-a', 'pan.alexander.tordnscrypt.action.SET_MODE',
                '--es', 'mode', 'tor+vpn'
            ])

        print(f"✅ Tunnel policy applied")

    def handle_control_message(self, message_str):
        """Process control bus message from Dom0"""
        try:
            message = json.loads(message_str)

            # Verify message structure
            required_fields = ['version', 'timestamp', 'target', 'command', 'payload', 'signature']
            if not all(field in message for field in required_fields):
                print(f"⚠️  Invalid message structure")
                return

            # Verify signature
            canonical = json.dumps({
                'version': message['version'],
                'timestamp': message['timestamp'],
                'target': message['target'],
                'command': message['command'],
                'payload': message['payload'],
                'nonce': message.get('nonce', '')
            }, sort_keys=True, separators=(',', ':'))

            if not self.verify_signature(canonical, message['signature']):
                print(f"❌ Invalid signature - rejecting message")
                return

            print(f"✅ Signature verified")

            # Apply changes
            if message['command'] == 'reload_policy':
                for key, value in message['payload'].items():
                    self.apply_policy_change(key, value)
                    self.current_policy[key] = value

        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON: {e}")
        except Exception as e:
            print(f"❌ Error handling message: {e}")

    def run(self):
        """Main daemon loop"""
        print(f"\n{'='*60}")
        print(f"  QWAMOS Gateway VM Policy Daemon")
        print(f"{'='*60}\n")
        print(f"Control bus: {CONTROL_BUS}")
        print(f"Dom0 pubkey: {DOM0_PUBKEY}")
        print()
        print(f"👁️  Listening for policy updates...\n")

        # Create control bus if needed
        CONTROL_BUS.parent.mkdir(parents=True, exist_ok=True)

        # Open control bus (FIFO)
        if not CONTROL_BUS.exists():
            os.mkfifo(CONTROL_BUS)

        # Read messages
        try:
            while True:
                with open(CONTROL_BUS, 'r') as bus:
                    for line in bus:
                        line = line.strip()
                        if line:
                            print(f"\n📨 Received message from Dom0")
                            self.handle_control_message(line)
        except KeyboardInterrupt:
            print("\n\n⏹️  Gateway policy daemon stopped")

def main():
    daemon = GatewayPolicyDaemon()
    daemon.run()

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
