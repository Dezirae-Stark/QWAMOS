# Welcome to QWAMOS

```
 ██████╗ ██╗    ██╗ █████╗ ███╗   ███╗ ██████╗ ███████╗
██╔═══██╗██║    ██║██╔══██╗████╗ ████║██╔═══██╗██╔════╝
██║   ██║██║ █╗ ██║███████║██╔████╔██║██║   ██║███████╗
██║▄▄ ██║██║███╗██║██╔══██║██║╚██╔╝██║██║   ██║╚════██║
╚██████╔╝╚███╔███╔╝██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║
 ╚══▀▀═╝  ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝

Quantum-Wrapped Android Mobile Operating System
```

**Version:** 1.2.0
**License:** AGPL-3.0
**Maintainer:** Dezirae Stark ([qwamos@tutanota.com](mailto:qwamos@tutanota.com))
**Organization:** First Sterling Capital, LLC

---

## 🎯 What is QWAMOS?

QWAMOS (Quantum-Wrapped Android Mobile Operating System) is a privacy-first, security-hardened Android environment that provides **military-grade isolation**, **post-quantum cryptography**, and **anonymous networking** for mobile devices.

Built for activists, journalists, security researchers, and privacy-conscious users, QWAMOS transforms your Android device into a fortress of compartmentalized virtual machines with zero cross-contamination.

---

## 📚 Wiki Navigation

| Section | Description |
|---------|-------------|
| **[Overview](Overview)** | Project mission, features, and capabilities |
| **[Installation & Setup Guide](Installation-&-Setup-Guide)** | Step-by-step installation and configuration |
| **[Architecture](Architecture)** | Technical architecture and system design |
| **[Security Model](Security-Model)** | Threat model, encryption, and isolation details |
| **[Developer Guide](Developer-Guide)** | Contributing, building, and development workflow |
| **[FAQ](FAQ)** | Frequently asked questions and troubleshooting |
| **[Roadmap](Roadmap)** | Development phases and future features |

---

## ⚡ Quick Start

```bash
# Clone QWAMOS
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS

# Check system compatibility
./scripts/check_compatibility.sh

# Initialize first VM
./scripts/create_vm.sh --name secure-browser --type browser

# Start gateway (Tor + I2P + DNSCrypt)
./gateway/start_gateway.sh
```

See **[Installation & Setup Guide](Installation-&-Setup-Guide)** for complete instructions.

---

## 🔒 Core Features

### VM Isolation
- **Per-app virtual machines** with hardware-backed isolation
- **Zero cross-contamination** between VMs
- **Disposable VMs** for one-time sensitive tasks
- **KVM acceleration** on supported hardware (8-15× performance boost)

### Post-Quantum Cryptography
- **Kyber-1024** key encapsulation mechanism
- **ChaCha20-Poly1305** AEAD encryption
- **BLAKE3** cryptographic hashing
- **Quantum-resistant** storage encryption

### Anonymous Networking
- **Tor** integration for .onion routing
- **I2P** darknet for eepsites
- **DNSCrypt** DNS-over-HTTPS with DNSSEC
- **Per-VM firewall rules** with automatic gateway routing

### Panic & Forensic Resistance
- **Emergency wipe triggers** (volume buttons, SMS, timer)
- **Duress passwords** (fake decoy system)
- **Anti-forensic memory scrambling**
- **Secure boot chain** with verified signatures

### GPU Isolation
- **Separate GPU contexts** per VM
- **Prevents GPU-based side channels**
- **Hardware-backed rendering isolation**

---

## 🛡️ Use Cases

### Journalists & Activists
- **Source protection** with isolated communication VMs
- **Secure document handling** with disposable VMs
- **Anonymous publishing** via Tor/I2P gateway

### Security Researchers
- **Malware analysis** in isolated sandbox VMs
- **Exploit development** without host contamination
- **Penetration testing** with compartmentalized tools

### Privacy-Conscious Users
- **Banking separation** from social media apps
- **Anonymous browsing** without tracking
- **Secure messaging** with quantum-resistant encryption

### Enterprise & Government
- **BYOD compliance** with isolated work/personal VMs
- **Classified data handling** with air-gapped VMs
- **Supply chain security** with reproducible builds

---

## 📊 Project Status

**Current Version:** v1.2.0

| Phase | Component | Status | Progress |
|-------|-----------|--------|----------|
| **I-XI** | Core Foundation | ✅ Complete | 100% |
| **XII** | KVM Acceleration | ⚙️ Hardware testing pending | 80% |
| **XIII** | PQC Storage | ✅ Complete | 100% |
| **XIV** | GPU Isolation | ✅ Complete | 100% |
| **XV** | AI Governor | ✅ Complete | 100% |
| **XVI** | Secure Cluster Mode | ✅ Complete | 100% |

**Testing Status:**
- ✅ QEMU virtualization: 100% pass rate
- ✅ VM boundary tests: Passed
- ✅ PQC storage integration: Passed
- ⏳ Hardware KVM validation: Pending real ARM device

See **[Roadmap](Roadmap)** for detailed phase information.

---

## 🚀 Getting Help

- **📖 Documentation:** This wiki + [Main README](https://github.com/Dezirae-Stark/QWAMOS/blob/master/README.md)
- **🐛 Bug Reports:** [GitHub Issues](https://github.com/Dezirae-Stark/QWAMOS/issues)
- **💬 Discussions:** [GitHub Discussions](https://github.com/Dezirae-Stark/QWAMOS/discussions)
- **📧 Email:** [qwamos@tutanota.com](mailto:qwamos@tutanota.com)

---

## 🤝 Contributing

QWAMOS is open-source and community-driven. We welcome contributions!

**Priority Areas:**
1. Android VM integration (AOSP compilation)
2. Hardware testing on real devices
3. Security audits and penetration testing
4. Documentation improvements

See **[Developer Guide](Developer-Guide)** for contribution guidelines.

---

## 📜 License

QWAMOS is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

This ensures:
- ✅ Freedom to use, study, and modify
- ✅ Strong copyleft (derivatives must be open-source)
- ✅ Network use disclosure (SaaS deployments must share source)

See [LICENSE](https://github.com/Dezirae-Stark/QWAMOS/blob/master/LICENSE) for full text.

---

## 🌟 Support QWAMOS

QWAMOS is community-funded open-source software. Your donations support:
- 🔬 Security audits and penetration testing
- 📱 Hardware testing on diverse Android devices
- 🧑‍💻 Full-time development
- 📚 Documentation and educational content

[![Donate Bitcoin](https://img.shields.io/badge/Donate-Bitcoin-orange?style=for-the-badge&logo=bitcoin)](https://trocador.app/anonpay?ticker_to=btc&network_to=Mainnet&address=bc1qjm7fnrk23m4esr2nq97aqugvecw2awxvp0rd2s&ref=sqKNYGZbRl&direct=True)
[![Donate Monero](https://img.shields.io/badge/Donate-Monero-gray?style=for-the-badge&logo=monero)](https://trocador.app/anonpay?ticker_to=xmr&network_to=Mainnet&address=49CjxV4LcAMGyVe46N2hEAJJXJVQhAaSbepzistuJSKcG9ApC9RZmNNUbzpNxsmvmKHZX9N4SKBbTWk2NST7ozzVMAFsme7&ref=sqKNYGZbRl&direct=True&description=QWAMOS+Donations+)

**Why Trocador AnonPay?**
- ✅ Accept 200+ cryptocurrencies
- ✅ No KYC/registration required
- ✅ Works with Tor Browser
- ✅ Non-custodial payments

---

**Built with ❤️ for privacy, security, and freedom.**

*Last Updated: 2025-11-18*
