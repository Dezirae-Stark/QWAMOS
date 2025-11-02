# QWAMOS Signed Control Bus - Usage Guide

## Overview

The QWAMOS Signed Control Bus provides secure, authenticated communication between Dom0 and VMs using **Ed25519 signatures**. All policy updates are signed and verified to prevent unauthorized changes.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Dom0 (Offline)                          │
│                                                               │
│  ┌───────────────┐        ┌──────────────────┐              │
│  │  qwamosctl    │───────→│    qwamosd       │              │
│  │  (CLI Client) │        │  (Policy Daemon) │              │
│  └───────────────┘        └──────────────────┘              │
│         │                          │                          │
│         │  Signs with              │  Verifies signatures     │
│         │  Ed25519 private key     │  with Ed25519 public key │
│         ↓                          ↓                          │
│  /run/qwamos/bus.sock     /etc/qwamos/status.json           │
│                           /etc/qwamos/pending.conf           │
└───────────────────────────────────────────────────────────────┘
                              │
                              │ Unix socket (inter-VM)
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Gateway VM                              │
│                                                               │
│  ┌─────────────────────────────────────────┐                │
│  │  gateway-policyd (Echo Service)         │                │
│  │  Verifies Dom0 signatures & logs policy │                │
│  └─────────────────────────────────────────┘                │
└───────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Bootstrap Ed25519 Keys

First time setup:

```bash
cd /opt/qwamos/dom0/keys
./bootstrap_keys.py
```

Output:
```
Generating new Ed25519 keypair for Dom0...
✓ Created Dom0 Ed25519 keypair:
  Private: /home/user/.qwamos/dom0/ed25519_sk (mode 0600)
  Public:  /home/user/.qwamos/dom0/ed25519_pk (mode 0600)

WARNING: Keep the private key secure. Anyone with access
         can issue signed commands to QWAMOS VMs.
```

### 2. Start the Policy Daemon

```bash
sudo systemctl start qwamosd
# Or manually:
cd /opt/qwamos/dom0/qwamosd
sudo ./qwamosd.py
```

Output:
```
============================================================
QWAMOS Policy Daemon (qwamosd)
============================================================
✓ Loaded public key from /home/user/.qwamos/dom0/ed25519_pk
✓ Loaded policy schema from /opt/qwamos/dom0/policy/policy.schema.json
⚠ No existing policy found, starting with empty policy
✓ QWAMOS Policy Daemon listening on /run/qwamos/bus.sock
  Runtime-safe keys: 9
  Reboot-required keys: 3
```

### 3. Send Policy Updates

#### Set Single Policy Key

```bash
qwamosctl set RADIO_ISOLATION on
```

Output:
```
✓ Loaded signing key from /home/user/.qwamos/dom0/ed25519_sk
✓ Policy update successful
  Applied immediately: RADIO_ISOLATION
```

#### Apply Policy from File

```bash
# Convert INI to JSON (one-time)
cd /opt/qwamos/dom0/policy
./ini_to_json.py policy.conf.example > my_policy.json

# Apply JSON policy
qwamosctl --policy-file my_policy.json apply
```

Output:
```
✓ Loaded signing key from /home/user/.qwamos/dom0/ed25519_sk
✓ Policy file applied: my_policy.json
  Runtime updates: 5
  Reboot-required: 2
  ⚠ Reboot required: BOOT_VERIFICATION, KERNEL_HARDENING
```

#### Get Current Status

```bash
qwamosctl status
```

Output:
```
=== QWAMOS Policy Status ===

Current Policy:
  CLIPBOARD_ISOLATION = strict
  RADIO_ISOLATION = on
  TOR_ISOLATION = mandatory

Pending (reboot required):
  BOOT_VERIFICATION = strict
  KERNEL_HARDENING = paranoid
```

#### Dry-Run Mode

Test policy updates without applying:

```bash
qwamosctl set BOOT_VERIFICATION strict --dry-run
```

Output:
```
=== DRY RUN ===
Would send:
{
  "msg": {
    "args": {
      "BOOT_VERIFICATION": "strict"
    },
    "command": "set_policy",
    "nonce": "xK8f2pQ7vL1mN9zR4tY6wE==",
    "timestamp": 1699876543
  },
  "signature": "dGhpcyBpcyBhIGZha2Ugc2lnbmF0dXJlIGZvciB0ZXN0aW5nIHB1cnBvc2VzIG9ubHk="
}
```

## Policy Classification

### Runtime-Safe Policies (Apply Immediately)

These policies are applied immediately without requiring a reboot:

- `RADIO_ISOLATION` - Toggle radio isolation
- `RADIO_HARDENING.level` - Firewall strictness (basic/strict)
- `RADIO_IDLE_TIMEOUT_MIN` - Auto radio-off timer
- `TOR_ISOLATION` - Tor routing (off/optional/mandatory)
- `VPN_KILL_SWITCH` - VPN kill switch
- `CLIPBOARD_ISOLATION` - Clipboard isolation level
- `DURESS.enabled` - Duress profile toggle
- `DURESS.gesture` - Duress gesture type
- `GHOST.trigger` - Self-destruct trigger

### Reboot-Required Policies (Staged to pending.conf)

These policies require a reboot and are staged to `/etc/qwamos/pending.conf`:

- `BOOT_VERIFICATION` - Measured boot enforcement
- `KERNEL_HARDENING` - SELinux/AppArmor hardening level
- `CRYPTO_BACKEND` - Cryptographic backend (legacy/post-quantum)

## Security Features

### Ed25519 Signatures

- **Key Size**: 32 bytes (private and public)
- **Signature Size**: 64 bytes
- **Security Level**: ~128-bit (equivalent to RSA-3072)
- **Speed**: ~70,000 signatures/sec on modern ARM
- **Verification**: ~25,000 verifications/sec

### Replay Protection

- **Nonce**: 16 random bytes (base64-encoded) prevent replay attacks
- **Timestamp**: Unix timestamp with 5-minute skew tolerance
- **Nonce Cache**: 10,000-entry LRU cache tracks seen nonces

### Canonical JSON

Messages are signed using canonical JSON (sorted keys, no whitespace):

```json
{"args":{"RADIO_ISOLATION":"on"},"command":"set_policy","nonce":"xK8f2pQ...","timestamp":1699876543}
```

## Testing

### Run Unit Tests

```bash
cd /opt/qwamos/dom0/tests
pytest test_bus.py -v
```

Output:
```
test_bus.py::TestKeyGeneration::test_key_generation PASSED
test_bus.py::TestKeyGeneration::test_key_serialization PASSED
test_bus.py::TestMessageSigning::test_message_signing PASSED
test_bus.py::TestMessageSigning::test_signature_verification_fails_on_tampered_message PASSED
test_bus.py::TestMessageSigning::test_canonical_json_is_deterministic PASSED
test_bus.py::TestPolicyClassification::test_runtime_safe_policies PASSED
test_bus.py::TestPolicyClassification::test_reboot_required_policies PASSED
test_bus.py::TestPolicyClassification::test_mixed_policy_updates PASSED
test_bus.py::TestReplayProtection::test_nonce_uniqueness PASSED
test_bus.py::TestReplayProtection::test_timestamp_validation PASSED
test_bus.py::TestStatusUpdates::test_status_json_format PASSED
test_bus.py::TestStatusUpdates::test_pending_conf_format PASSED
test_bus.py::TestEndToEnd::test_complete_workflow PASSED

==================== 13 passed in 0.42s ====================
```

### Test Gateway VM Echo Service

```bash
# In Gateway VM:
cd /opt/qwamos/gateway_vm/policy
./gateway-policyd.py
```

Output:
```
======================================================================
QWAMOS Gateway VM Policy Daemon (Echo Service)
======================================================================
[2025-01-15 12:00:00] [Gateway-PolicyD] INFO: Loaded Dom0 public key from /etc/qwamos/dom0.pub
[2025-01-15 12:00:00] [Gateway-PolicyD] INFO: Gateway Policy Daemon listening on /run/qwamos/gateway-bus.sock
[2025-01-15 12:00:00] [Gateway-PolicyD] INFO: Echo service mode - will log received policy updates
```

When a policy update is sent:
```
[2025-01-15 12:01:23] [Gateway-PolicyD] INFO: ✓ Signature verified successfully
[2025-01-15 12:01:23] [Gateway-PolicyD] INFO: Command: set_policy, Nonce: xK8f2pQ7vL1mN9..., Timestamp: 1699876543
[2025-01-15 12:01:23] [Gateway-PolicyD] INFO: === Policy Update Received ===
[2025-01-15 12:01:23] [Gateway-PolicyD] INFO:   RADIO_ISOLATION = on
[2025-01-15 12:01:23] [Gateway-PolicyD] INFO:   TOR_ISOLATION = mandatory
```

## Boot-Time Policy Application

Reboot-required policies are applied at boot via systemd:

```bash
systemctl enable qwamos-policy-apply.service
```

On next boot:
```
[QWAMOS] Applying pending policy changes from /etc/qwamos/pending.conf
[QWAMOS] Backed up current status to /var/lib/qwamos/backups
[QWAMOS] Applying: BOOT_VERIFICATION = strict
[QWAMOS] Setting boot verification mode: strict
[QWAMOS] Applying: KERNEL_HARDENING = paranoid
[QWAMOS] Setting kernel hardening level: paranoid
[QWAMOS] Updated status.json with pending policy changes
[QWAMOS] Removed pending.conf (changes applied successfully)
[QWAMOS] Boot-time policy application complete ✓
```

## Troubleshooting

### Keys not found

```
ERROR: Public key not found at /home/user/.qwamos/dom0/ed25519_pk
Run: cd dom0/keys && ./bootstrap_keys.py
```

**Solution**: Run `./bootstrap_keys.py` to generate keys

### Daemon not running

```
ERROR: qwamosd not running (socket not found: /run/qwamos/bus.sock)
Start daemon: cd dom0/qwamosd && sudo ./qwamosd.py
```

**Solution**: Start qwamosd via systemd or manually

### Signature verification failed

```
[2025-01-15 12:00:00] [Gateway-PolicyD] ERROR: SIGNATURE VERIFICATION FAILED - Rejecting message
```

**Causes**:
- Wrong public key in VM (key mismatch)
- Tampered message
- Clock skew > 5 minutes

**Solution**: Ensure Dom0 public key is correctly distributed to all VMs

### Timestamp skew too large

```
✗ Policy update failed: Timestamp skew too large: 612s
```

**Solution**: Sync clocks across Dom0 and VMs (use NTP or manual sync)

## Key Rotation

To rotate Ed25519 keys:

```bash
# 1. Backup old keys
cp ~/.qwamos/dom0/ed25519_sk ~/.qwamos/dom0/ed25519_sk.backup
cp ~/.qwamos/dom0/ed25519_pk ~/.qwamos/dom0/ed25519_pk.backup

# 2. Generate new keys
rm ~/.qwamos/dom0/ed25519_*
cd /opt/qwamos/dom0/keys
./bootstrap_keys.py

# 3. Distribute new public key to all VMs
sudo cp ~/.qwamos/dom0/ed25519_pk /path/to/gateway-vm/rootfs/etc/qwamos/dom0.pub
sudo cp ~/.qwamos/dom0/ed25519_pk /path/to/ui-vm/rootfs/etc/qwamos/dom0.pub

# 4. Restart all VM policy daemons
sudo systemctl restart gateway-policyd
sudo systemctl restart ui-policyd
```

## References

- Ed25519: https://ed25519.cr.yp.to/
- PyNaCl: https://pynacl.readthedocs.io/
- Canonical JSON: RFC 8785
- QWAMOS Threat Model: `docs/THREAT_MODEL.md`
- Key Management: `dom0/keys/README.md`
