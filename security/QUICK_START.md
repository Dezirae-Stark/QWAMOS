# QWAMOS Security Layer - Quick Start Guide

## What Is This?

A complete security architecture that transforms your Motorola Edge 2025 into a high-assurance mobile platform with:

- **Baseband Isolation**: Untrusted radio in separate VM
- **Mandatory Tor**: All traffic through Tor/I2P
- **Verified Boot**: Detect tampering at startup
- **Panic Protection**: Emergency wipe gesture
- **Duress Profiles**: Decoy user for coercion scenarios
- **Post-Quantum Crypto**: Kyber-1024 + ChaCha20-Poly1305

## Architecture (4 VMs)

```
┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌────────────┐
│   Dom0      │  │  Gateway VM  │  │ Workstation│  │ Trusted UI │
│  (Control)  │  │  (Radio)     │  │   (Apps)   │  │  (Overlay) │
│             │  │              │  │            │  │            │
│ • Policy    │  │ • Telephony  │  │ • No NIC   │  │ • Call UI  │
│ • Offline   │  │ • Tor/I2P    │  │ • Isolated │  │ • Badges   │
│ • Signs     │  │ • Firewall   │  │ • Safe     │  │ • Secure   │
└─────────────┘  └──────────────┘  └────────────┘  └────────────┘
```

## 12 Security Toggles

### Runtime-Safe (Apply Immediately)

| Toggle | Description | Values |
|--------|-------------|--------|
| `RADIO_ISOLATION` | Isolate radio in Gateway VM | on/off |
| `RADIO_HARDENING.level` | Tor-only vs basic mode | basic/strict |
| `RADIO_IDLE_TIMEOUT_MIN` | Auto power-down radio | 0-999 min |
| `TRUSTED_OVERLAY` | Secure call UI | on/off |
| `REMOTE_ATTESTATION` | Upload boot hashes | off/warn/enforce |
| `PANIC_GESTURE` | Power+Vol+FP wipe | on/off |
| `DURESS_PROFILE` | Decoy user account | on/off |
| `E2E_TUNNEL_POLICY` | Egress routing mode | tor-only/tor+vpn |
| `AUDIT_UPLOAD` | Log upload via Tor | off/tor-hidden |

### Reboot-Required

| Toggle | Description | Values |
|--------|-------------|--------|
| `VERIFIED_BOOT_ENFORCE` | Block unlock on tamper | warn/enforce |
| `KERNEL_HARDENING` | Lockdown mode + KASLR | default/strict |
| `BASEBAND_DRIVER_DISABLE` | Air-gapped mode | on/off |

## Installation (3 Minutes)

### Prerequisites
```bash
# On Motorola Edge 2025 (Termux)
pkg install python tor iptables git

# Install InviZible Pro (APK provided)
# Install signify for Ed25519 signatures
```

### Deploy
```bash
cd ~/QWAMOS/security
chmod +x deploy-to-device.sh
./deploy-to-device.sh
```

### First Boot Setup
```bash
python3 dom0/ui/first-boot-wizard.py
```

This will:
1. Guide you through security level selection
2. Configure panic gesture
3. Create duress profile (optional)
4. Generate Dom0 signing keys
5. Write initial policy

### Start Services
```bash
systemctl start qwamosd         # Policy daemon
systemctl start gateway-policyd # Gateway listener
systemctl start panicd          # Panic gesture
systemctl start attestd         # Boot attestation
```

## Usage Examples

### Change Security Level to Strict

Edit `/etc/qwamos/policy.conf`:
```ini
RADIO_HARDENING.level=strict
KERNEL_HARDENING=strict
VERIFIED_BOOT_ENFORCE=enforce
```

qwamosd will:
1. Apply `RADIO_HARDENING.level=strict` immediately (runtime)
2. Queue `KERNEL_HARDENING` and `VERIFIED_BOOT_ENFORCE` for reboot
3. Prompt: "Reboot required to apply 2 settings. Reboot now?"

### Enable Air-Gapped Mode

```bash
# Edit policy
echo "BASEBAND_DRIVER_DISABLE=on" >> /etc/qwamos/policy.conf

# Reboot required
# Radio will not initialize on next boot
```

### Test Panic Gesture

1. Press and hold: **Power + VolUp + Fingerprint** simultaneously
2. System will:
   - Wipe session keys
   - Disable cellular radio
   - Lock screen
   - (Optional) Send encrypted Tor ping to trusted contact

### View Boot Integrity

```bash
python3 ui_vm/overlays/boot-status.py
```

Output:
```
==================================================
  BOOT INTEGRITY STATUS
==================================================
  ✅ Status: VERIFIED
  Hash: a3b2c1d4e5f6...

  Last 5 boots: All hashes match
==================================================
```

### Unlock with Duress Profile

1. At lock screen, enter duress PIN (weak PIN like 1234)
2. System unlocks to decoy profile with benign data
3. (Optional) Silent alert sent via Tor

## File Locations

```
/etc/qwamos/policy.conf          # Active policy
/etc/qwamos/pending.conf         # Reboot-required changes
/etc/qwamos/keys/dom0.{pub,sec}  # Ed25519 signing keys
/data/qwamos/attestation.log     # Boot hash history
/data/qwamos/session-keys/       # Ephemeral keys (wiped on panic)
/var/run/qwamos/control-bus/     # VM communication channels
```

## Security Guarantees

### What QWAMOS Protects Against

✅ Baseband RCE (radio isolated in VM)
✅ IMSI catchers (Tor-only egress in strict mode)
✅ Zero-day exploits (SELinux + minimal attack surface)
✅ Evil maid (verified boot + attestation)
✅ $5-wrench attacks (duress profile + panic wipe)
✅ Network surveillance (mandatory Tor/I2P)
✅ Forensic imaging (FBE + TEE keys)
✅ Supply chain (measured boot + remote attestation)

### What QWAMOS Does NOT Protect Against

❌ Physical extraction of TEE keys (requires expensive lab)
❌ Snapdragon TrustZone 0-day (trust in hardware)
❌ Tor network-level deanonymization (timing attacks)
❌ RF side-channels (TEMPEST-level threats)
❌ Coercion with continuous monitoring (duress may be detected)

## Threat Model Examples

### Scenario 1: Border Crossing

**Threat:** Device seizure and coerced unlock

**QWAMOS Defense:**
1. `DURESS_PROFILE=on` - Weak PIN unlocks decoy profile
2. Real data encrypted with strong passphrase in TEE
3. Decoy profile has benign news/weather apps

**Result:** Attacker sees decoy data, real secrets safe

### Scenario 2: IMSI Catcher at Protest

**Threat:** Cell-site simulator tracking protesters

**QWAMOS Defense:**
1. `RADIO_HARDENING.level=strict` - Blocks IMS registration
2. `E2E_TUNNEL_POLICY=tor-only` - All data via Tor
3. `RADIO_IDLE_TIMEOUT_MIN=5` - Radio off after 5 min

**Result:** IMSI catcher cannot track device location via cellular

### Scenario 3: Targeted Malware

**Threat:** Nation-state spyware (like Pegasus)

**QWAMOS Defense:**
1. `KERNEL_HARDENING=strict` - Lockdown mode blocks many exploits
2. Radio isolated in separate VM (cannot reach workstation)
3. SELinux enforcing on all VMs
4. Minimal attack surface (no unnecessary services)

**Result:** Significantly harder to exploit; if compromised, limited to one VM

### Scenario 4: Evil Maid Attack

**Threat:** Attacker modifies bootloader while device unattended

**QWAMOS Defense:**
1. `VERIFIED_BOOT_ENFORCE=enforce` - Blocks unlock on boot hash mismatch
2. Attestation log shows boot hash history
3. Trusted UI displays warning badge

**Result:** Tamper detected, secrets not released

## Advanced Configuration

### Custom Tor Hidden Service for Attestation

Edit policy:
```ini
REMOTE_ATTESTATION=enforce
AUDIT_UPLOAD=tor-hidden
```

Edit attestation config:
```python
# attestation/attestd/attestd.py
REMOTE_VERIFIER = 'http://yourhiddenservice.onion/attest'
```

System will upload signed boot hashes to your Tor hidden service. Enforce mode blocks unlock if upload fails.

### Multi-Layer Routing (Tor + I2P)

```ini
E2E_TUNNEL_POLICY=tor+i2p
```

Gateway VM will route:
- 50% traffic via Tor
- 50% traffic via I2P
- Parallel paths for increased anonymity

### Custom Panic Beacon

Edit panic daemon:
```python
# panic/panicd/panic-daemon.py
def send_panic_beacon():
    # Send encrypted message to trusted contact via Tor
    message = encrypt_kyber("PANIC ACTIVATED", trusted_contact_pubkey)
    torify_curl(TRUSTED_CONTACT_ONION, message)
```

## Troubleshooting

### Policy Changes Not Applying

**Check qwamosd status:**
```bash
systemctl status qwamosd
journalctl -u qwamosd -f
```

**Common issues:**
- Invalid signature on policy.conf
- Syntax error in policy file
- Control bus channel not found

### Radio Not Turning Off

**Check Gateway VM policy listener:**
```bash
systemctl status gateway-policyd
```

**Manual radio control:**
```bash
/data/qwamos/radio/radio-ctrl.sh off
```

### Panic Gesture Not Working

**Check panicd status:**
```bash
systemctl status panicd
```

**Test input devices:**
```bash
cat /dev/input/event0  # Power button
cat /dev/input/event1  # Vol up
cat /dev/input/event2  # Fingerprint
```

### Boot Attestation Failing

**Check StrongBox availability:**
```bash
keystore-cli list
```

**View attestation log:**
```bash
cat /data/qwamos/attestation.log | tail -5
```

## Performance Impact

| Component | CPU | RAM | Battery | Notes |
|-----------|-----|-----|---------|-------|
| Dom0 (qwamosd) | <1% | ~20MB | Negligible | Event-driven |
| Gateway VM | 2-5% | ~150MB | ~5% | Tor routing |
| Trusted UI VM | <1% | ~30MB | Negligible | Overlay only |
| Attestation | <1% | ~10MB | <1% | Boot-time only |
| Encryption | ~3% | ~50MB | ~2% | ChaCha20 HW accel |

**Total overhead:** ~5-10% CPU, ~250MB RAM, ~8% battery

**Acceptable for:** Daily use, normal workloads
**Not ideal for:** Gaming, heavy video processing

## FAQ

**Q: Can I still make normal phone calls?**
A: Yes! Calls work normally. Trusted UI just adds a secure overlay for Accept/Reject.

**Q: Will this break my banking apps?**
A: Most apps work. Some may detect "rooted" device (false positive). Use workstation VM for banking.

**Q: Can I disable security features temporarily?**
A: Yes, edit policy.conf. Changes apply immediately (except reboot-required toggles).

**Q: What happens if I forget my duress PIN?**
A: You can always unlock with your real PIN/passphrase. Duress is an alternate entry point.

**Q: Is this legal?**
A: Yes. You have the right to secure your own device. Check local laws regarding encryption.

**Q: Will this void my warranty?**
A: Probably. Modifying the bootloader typically voids warranties.

## Support & Development

**Documentation:** `security/README_QWAMOS_SecurityLayer.md` (60+ pages)
**Source code:** `~/QWAMOS/security/`
**Issues:** [GitHub Issues](https://github.com/yourusername/qwamos/issues)
**Community:** [QWAMOS Forum](https://forum.qwamos.org)

**Development Status:**
- ✅ Dom0 Policy Manager (complete)
- ✅ Gateway VM services (complete)
- ✅ Attestation system (complete)
- ✅ Crypto layer (complete)
- ✅ Panic & duress (complete)
- ⚙️ Trusted UI VM (compositor stub provided)
- ⚙️ Remote attestation server (API spec provided)

**Contributions welcome!** See CONTRIBUTING.md

---

**QWAMOS Security Layer v1.0**
**© 2025 QWAMOS Project**
**License: GPL-3.0**

*"Mobile privacy and security should not require a PhD in cryptography."*
