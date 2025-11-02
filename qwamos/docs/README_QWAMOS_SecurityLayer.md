# QWAMOS Security Layer

## Overview

The QWAMOS Security Layer provides 12 security toggles for the Motorola Edge 2025 build, implementing a policy-driven architecture across 4 VMs:

- **Dom0**: Policy manager and control bus
- **Gateway VM**: Tor/I2P networking and firewall
- **Workstation VM**: User applications
- **Trusted UI VM**: Call/SMS prompts

## Security Toggles

### Runtime-Safe Toggles (Applied Immediately)

1. **RADIO_ISOLATION** - Disconnect baseband from application processor
2. **RADIO_HARDENING.level** - Basic vs strict firewall rules
3. **RADIO_IDLE_TIMEOUT_MIN** - Auto radio-off timer
4. **TRUSTED_OVERLAY** - Trusted UI for calls/SMS
5. **REMOTE_ATTESTATION** - Remote verification before key release
6. **PANIC_GESTURE** - Emergency wipe trigger
7. **DURESS_PROFILE** - Decoy login profile
8. **E2E_TUNNEL_POLICY** - tor-only / tor+vpn / custom
9. **AUDIT_UPLOAD** - Secure logging to Tor hidden service

### Reboot-Required Toggles

10. **VERIFIED_BOOT_ENFORCE** - Measured boot enforcement
11. **KERNEL_HARDENING** - SELinux strict mode
12. **BASEBAND_DRIVER_DISABLE** - Complete baseband isolation

## Folder Structure

- `dom0/` - Policy daemon and CLI
- `gateway_vm/` - Firewall and network isolation
- `ui_vm/` - Trusted UI overlays
- `attestation/` - Remote verification
- `crypto/` - ChaCha20-Poly1305 + Kyber-1024
- `panic/` - Emergency wipe system

## Quick Start

```bash
# View current policy
cat /etc/qwamos/policy.conf

# Update policy
qwamosctl gateway_vm policy-update --payload '{"RADIO_ISOLATION": "on"}'

# Check policy validity
python3 /opt/qwamos/dom0/policy/validate_policy.py policy.json
```

## Architecture

The security layer uses a signed control bus (Ed25519) to propagate policy changes from Dom0 to VMs. All changes are validated against policy.schema.json before application.
