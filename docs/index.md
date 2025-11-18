---
layout: default
title: Home
nav_order: 1
description: "QWAMOS: Quantum-Resistant Workstation and Mobile Operating System for Android"
permalink: /
---

# QWAMOS Documentation
{: .fs-9 }

**Quantum-Resistant Workstation and Mobile Operating System**
{: .fs-6 .fw-300 }

Privacy-focused, VM-isolated, anonymized computing platform built on Android with post-quantum cryptography.
{: .fs-5 .fw-300 }

[Get Started](#quick-start){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[View on GitHub](https://github.com/Dezirae-Stark/QWAMOS){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## 🎯 What is QWAMOS?

QWAMOS (Quantum-Resistant Workstation and Mobile Operating System) is a security-hardened Android-based operating system that provides:

- **🔐 Post-Quantum Cryptography**: Kyber-1024, ChaCha20-Poly1305, BLAKE3
- **🖥️ VM Isolation**: QEMU, Chroot, PRoot, and KVM support
- **🌐 Network Anonymization**: Tor, I2P, and DNSCrypt integration
- **🚨 Panic/Wipe System**: Emergency data destruction
- **🛡️ Hardware Security**: TrustZone, verified boot, secure storage

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     QWAMOS Architecture                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Android 14+ (Host System)                  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         QWAMOS Control Layer (Dom0)            │  │  │
│  │  │                                                 │  │  │
│  │  │  • VM Manager                                   │  │  │
│  │  │  • Gateway Controller                           │  │  │
│  │  │  • Crypto Engine (Kyber-1024 + ChaCha20)       │  │  │
│  │  │  • Panic/Wipe System                           │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │  Gateway VM  │  │ Workstation  │  │  Vault VM   │ │  │
│  │  │              │  │     VM       │  │             │ │  │
│  │  │ Tor/I2P/DNS  │  │              │  │  Encrypted  │ │  │
│  │  │   Crypt      │  │  Isolated    │  │   Storage   │ │  │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                               │
│  Isolation: QEMU/Chroot/PRoot/KVM                           │
│  Network: Mandatory Tor/I2P egress                          │
│  Crypto: Post-Quantum (Kyber-1024)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Installation Methods

Choose your installation method based on your device and requirements:

#### 1. **Termux Installation** (No Root Required)
{: .d-inline-block }
Recommended
{: .label .label-green }

```bash
# Clone repository
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS

# Run installation script
./scripts/install.sh
```

[Detailed Termux Installation Guide →](ANDROID_VM_SETUP_GUIDE)

#### 2. **Rooted KVM Installation** (Hardware Acceleration)
{: .d-inline-block }
Advanced
{: .label .label-yellow }

For devices with root access and KVM support:

```bash
# Prerequisites: Rooted Android 14+, KVM-enabled kernel
./scripts/install-kvm.sh
```

[KVM Installation Guide →](PHASE3_HYPERVISOR_SPEC)

#### 3. **Custom ROM Installation** (Full System Integration)
{: .d-inline-block }
Expert
{: .label .label-red }

For custom ROM integration (AOSP, LineageOS, etc.):

[Custom ROM Integration Guide →](SELF_FLASHING_INSTALLER)

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Android Version** | 10+ | 14+ |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 8GB free | 32GB+ SSD |
| **CPU** | Quad-core | Octa-core, 64-bit |
| **Network** | Wi-Fi | Wi-Fi + Cellular |

---

## 📚 Documentation Sections

### 🎓 Getting Started

- [Installation & Setup Guide](ANDROID_VM_SETUP_GUIDE) - Complete installation instructions
- [User VM Creation Guide](USER_VM_CREATION_GUIDE) - Creating isolated virtual machines
- [VM Configurations](VM_CONFIGURATIONS) - VM profiles and templates
- [Setup Guide](SETUP_GUIDE) - Post-installation configuration

### 🏗️ Architecture & Design

- [Technical Architecture](TECHNICAL_ARCHITECTURE) - Complete system architecture
- [Architecture Documentation](ARCHITECTURE) - Design patterns and principles
- [Hypervisor Specification](PHASE3_HYPERVISOR_SPEC) - KVM/QEMU hypervisor details
- [Network Isolation](PHASE5_NETWORK_ISOLATION) - Gateway and firewall architecture

### 🔒 Security

- [Security Policy](../SECURITY) - Vulnerability reporting and disclosure
- [Storage Encryption](STORAGE_ENCRYPTION) - Disk encryption and key management
- [VeraCrypt Post-Quantum Crypto](VERACRYPT_POST_QUANTUM_CRYPTO) - PQC implementation
- [Secure Keyboard Spec](SECURE_KEYBOARD_SPEC) - PQ-encrypted keyboard
- [Hardware Security (Phase 10)](PHASE10_ADVANCED_HARDWARE_SECURITY) - Hardware kill switches, secure boot

### 🌐 Network & Anonymization

- [Whonix Gateway Setup](WHONIX_GATEWAY_SETUP) - Tor gateway configuration
- [InviZible Pro Integration](INVIZIBLE_PRO_INTEGRATION) - Multi-protocol anonymization
- [Network Isolation Details](PHASE5_NETWORK_ISOLATION) - Firewall and routing

### 🤖 AI & Machine Learning

- [Kali GPT Integration](KALI_GPT_INTEGRATION) - AI security assistant
- [AI Assistants (Phase 6)](PHASE6_AI_ASSISTANTS_INTEGRATION) - Claude, ChatGPT integration
- [ML Threat Detection (Phase 7)](PHASE7_ML_THREAT_DETECTION) - Real-time threat detection
- [ML Training Guide](PHASE7_ML_TRAINING_GUIDE) - Training custom models

### 🚀 Advanced Features

- [Chimera Decoy Protocol](CHIMERA_DECOY_PROTOCOL) - Plausible deniability system
- [Seamless Data Migration](SEAMLESS_DATA_MIGRATION) - VM and data migration
- [Self-Flashing Installer](SELF_FLASHING_INSTALLER) - Custom ROM installer
- [USB Kill Switch Schematic](PHASE10_USB_KILLSWITCH_SCHEMATIC) - Hardware kill switch

### 📊 Project Status

- [Project Status](PROJECT_STATUS) - Current development status
- [Phase 5 Completion Summary](PHASE5_COMPLETION_SUMMARY) - Network isolation milestone
- [Phase 7 Completion Summary](PHASE7_COMPLETION_SUMMARY) - ML threat detection milestone
- [Touchscreen and UI Status](TOUCHSCREEN_AND_UI_STATUS) - UI development progress

### 🧪 Testing & Deployment

- [Phase 5 Testing Guide](PHASE5_TESTING_GUIDE) - Testing procedures
- [No-Root Testing Plan](PHASE5_NO_ROOT_TESTING_PLAN) - Testing without root
- [Phase 6 Deployment Guide](PHASE6_DEPLOYMENT_GUIDE) - Production deployment
- [Phase 7 Deployment Guide](PHASE7_DEPLOYMENT_GUIDE) - ML deployment

### 📖 API & Development

- [Phase 7 API Documentation](PHASE7_API_DOCUMENTATION) - REST API reference
- [Contributing Guidelines](../CONTRIBUTING) - How to contribute
- [Code of Conduct](../CODE_OF_CONDUCT) - Community standards

### 🔍 Security Standards

- [QWAMOS Hardening Standard](QWAMOS_Hardening_Standard) - Security hardening guidelines
- [SLSA Roadmap](QWAMOS_SLSA_Roadmap) - Supply chain security
- [Security Audit Readiness](QWAMOS_Security_Audit_Readiness_Certificate) - Audit preparation

### 🎙️ Secure Communications

- [QWAMOS Secure Voice](QWAMOS-Secure-Voice-PQ) - Post-quantum voice encryption
- [Secure Voice Implementation](QWAMOS-SECURE-VOICE-IMPLEMENTATION) - Implementation details

---

## 🌟 Key Features

### Post-Quantum Cryptography

QWAMOS uses **NIST-approved post-quantum algorithms**:

- **Kyber-1024**: Key encapsulation mechanism (KEM)
- **ChaCha20-Poly1305**: Authenticated encryption (AEAD)
- **BLAKE3**: Cryptographic hash function
- **Argon2id**: Memory-hard key derivation

All cryptographic operations are quantum-resistant and comply with NIST PQC standards.

[Learn more about PQC →](VERACRYPT_POST_QUANTUM_CRYPTO)

### VM Isolation Modes

QWAMOS supports **four virtualization backends**:

| Mode | Description | Use Case |
|------|-------------|----------|
| **QEMU** | Software emulation | Maximum compatibility |
| **Chroot** | Namespace isolation | Lightweight, fast |
| **PRoot** | Userspace virtualization | No root required |
| **KVM** | Hardware acceleration | Maximum performance |

Each VM is **cryptographically isolated** with its own:
- Encrypted disk image (Kyber-1024 + ChaCha20)
- Network namespace (Tor/I2P only)
- Process namespace
- User namespace
- Mount namespace

[VM Configuration Guide →](VM_CONFIGURATIONS)

### Network Anonymization

**Mandatory anonymization** through:

- **Tor**: Anonymous web browsing via SOCKS5 proxy
- **I2P**: Anonymous eepsites and hidden services
- **DNSCrypt**: DNS-over-HTTPS for DNS privacy

All VMs are **network-isolated by default** with:
- Default DROP firewall policy
- Mandatory gateway VM for egress
- No direct internet access
- DNS leak prevention
- IPv6 disabled by default

[Network Setup Guide →](WHONIX_GATEWAY_SETUP)

### Emergency Protection

**Panic/Wipe System** includes:

- **Duress password**: Activates decoy profile
- **Panic gesture**: Instant data wipe
- **USB removal**: Triggers emergency shutdown
- **Time-based wipe**: Auto-wipe after timeout
- **Key destruction**: Cryptographic key shredding

[Chimera Decoy Protocol →](CHIMERA_DECOY_PROTOCOL)

---

## 📖 Wiki

Visit our [GitHub Wiki](https://github.com/Dezirae-Stark/QWAMOS/wiki) for:

- [Home](https://github.com/Dezirae-Stark/QWAMOS/wiki/Home)
- [Overview](https://github.com/Dezirae-Stark/QWAMOS/wiki/Overview)
- [Installation & Setup Guide](https://github.com/Dezirae-Stark/QWAMOS/wiki/Installation-&-Setup-Guide)
- [Architecture](https://github.com/Dezirae-Stark/QWAMOS/wiki/Architecture)
- [Security Model](https://github.com/Dezirae-Stark/QWAMOS/wiki/Security-Model)
- [Developer Guide](https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide)
- [FAQ](https://github.com/Dezirae-Stark/QWAMOS/wiki/FAQ)
- [Roadmap](https://github.com/Dezirae-Stark/QWAMOS/wiki/Roadmap)

---

## 🤝 Community

### Get Help

- **GitHub Discussions**: [Q&A Forum](https://github.com/Dezirae-Stark/QWAMOS/discussions/3)
- **Security Issues**: Email [qwamos@tutanota.com](mailto:qwamos@tutanota.com) (private disclosure)
- **Bug Reports**: [GitHub Issues](https://github.com/Dezirae-Stark/QWAMOS/issues/new?template=bug_report.md)
- **Feature Requests**: [Feature Discussion](https://github.com/Dezirae-Stark/QWAMOS/discussions/5)

### Contribute

QWAMOS is open source (AGPL-3.0) and welcomes contributions:

- [Contributing Guidelines](../CONTRIBUTING)
- [Code of Conduct](../CODE_OF_CONDUCT)
- [Security Policy](../SECURITY)
- [Developer Guide](https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide)

### Support the Project

- ⭐ Star the [GitHub repository](https://github.com/Dezirae-Stark/QWAMOS)
- 💰 [Sponsor on GitHub](https://github.com/sponsors/Dezirae-Stark)
- 🗣️ Share on social media
- 📝 Write tutorials or blog posts
- 🐛 Report bugs and security issues

---

## 📊 Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase I-IV | ✅ Complete | Core system, bootloader, kernel, PQC |
| Phase V | ✅ Complete | Network isolation and gateways |
| Phase VI | ✅ Complete | AI assistants integration |
| Phase VII | ✅ Complete | ML threat detection |
| Phase VIII | 🚧 In Progress | React Native UI |
| Phase IX | 🚧 In Progress | Android app framework |
| Phase X | ✅ Complete | Hardware security |
| Phase XI-XXI | 📅 Planned | Future enhancements |

[View Detailed Roadmap →](https://github.com/Dezirae-Stark/QWAMOS/wiki/Roadmap)

---

## 🔒 Security

**Security is our top priority.** QWAMOS implements:

- ✅ Post-quantum cryptography (NIST-approved)
- ✅ VM isolation (QEMU/Chroot/PRoot/KVM)
- ✅ Network anonymization (Tor/I2P/DNSCrypt)
- ✅ Hardware security (TrustZone, verified boot)
- ✅ Emergency panic/wipe system
- ✅ Memory-hard key derivation (Argon2id)
- ✅ Secure boot with signature verification
- ✅ ML-based threat detection

**Found a security vulnerability?** Please report responsibly:
- Email: [qwamos@tutanota.com](mailto:qwamos@tutanota.com)
- Subject: `[SECURITY] Brief description`
- **DO NOT** create public issues for security vulnerabilities

[Read our Security Policy →](../SECURITY)

---

## 📄 License

QWAMOS is licensed under **AGPL-3.0** (GNU Affero General Public License v3.0).

- ✅ Free to use, modify, and distribute
- ✅ Commercial use permitted
- ✅ Source code must be disclosed
- ✅ Same license for derivatives
- ✅ Network use triggers disclosure

[View License →](https://github.com/Dezirae-Stark/QWAMOS/blob/master/LICENSE)

---

## 📞 Contact

- **Email**: [qwamos@tutanota.com](mailto:qwamos@tutanota.com)
- **GitHub**: [@Dezirae-Stark](https://github.com/Dezirae-Stark)
- **Repository**: [QWAMOS](https://github.com/Dezirae-Stark/QWAMOS)
- **Discussions**: [GitHub Discussions](https://github.com/Dezirae-Stark/QWAMOS/discussions)

---

{: .text-center }
**Built with ❤️ for privacy, security, and freedom.**

{: .text-center }
© 2025 QWAMOS Project · Licensed under AGPL-3.0
