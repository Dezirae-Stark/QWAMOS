# QWAMOS Threat Model

## Threats and Mitigations

| Threat | Mitigation |
|--------|-----------|
| **Supply chain (hardware/baseband)** | Gateway VM isolation, radio-off timer, attestation, no direct network from Dom0 |
| **$5 wrench (coercion)** | Duress login profile, panic gesture, decoy keys |
| **Zero-day kernel exploit** | SELinux/AppArmor enforcing, minimal drivers, strict egress policy |
| **Malicious hypervisor** | Signed Dom0 policy, measured boot, offline Dom0 |
| **Evil maid** | Boot hash compare, remote attestation before key release |

## Attack Surface Reduction

- Dom0 runs offline (no direct network access)
- All network traffic routed through Gateway VM (mandatory Tor)
- Baseband isolated from application processors
- Trusted UI overlay prevents malicious call/SMS prompts
- Post-quantum cryptography protects against future quantum attacks

## Assumptions

- Physical access protection (encrypted storage at rest)
- User follows operational security procedures
- Threat actors: State-level adversaries, sophisticated attackers
- Out of scope: Side-channel attacks, physical device tampering while powered on
