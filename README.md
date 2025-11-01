# QWAMOS

**Qubes+Whonix Advanced Mobile Operating System**

A ground-up mobile operating system that replaces Android, featuring post-quantum cryptography, Qubes OS-style VM compartmentalization, and military-grade security.

<p align="center">
  <img src="assets/QWAMOS_logo.png" width="300" alt="QWAMOS Logo">
</p>

## 🔒 Key Features

- **Post-Quantum Cryptography:** Kyber-1024 + ChaCha20-Poly1305 throughout entire stack
- **VM-Based Isolation:** Android runs as a guest VM alongside Whonix, Kali, and AEGIS Vault
- **Verified Boot:** Secure boot chain from bootloader to kernel with Kyber signatures
- **Network Anonymity:** Whonix Gateway with Tor routing and Chimera decoy traffic
- **AEGIS Vault:** Airgapped cold storage for cryptocurrency wallets
- **KALI-WFH Suite:** Full penetration testing toolkit integrated
- **Ghost Self-Destruct:** Emergency destruction triggers with configurable policies
- **Custom UI:** Beautiful React Native interface with cyberpunk aesthetic

## 🏗️ Architecture

QWAMOS is a complete mobile OS built from the ground up:

```
Hardware
    └─> U-Boot Bootloader (Kyber-verified)
        └─> Linux Kernel 6.6 LTS (Hardened, KVM-enabled)
            └─> systemd Init
                └─> KVM/QEMU Hypervisor
                    ├─> android-vm (Android 14 AOSP)
                    ├─> whonix-vm (Tor Gateway)
                    ├─> kali-vm (Penetration Testing)
                    ├─> vault-vm (AEGIS Airgap)
                    └─> disposable-vm (Ephemeral)
```

See [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md) for complete details.

## 📱 Screenshots

<p align="center">
  <img src="assets/screenshots/screenshot1.png" width="300">
  <br><em>QWAMOS Core Interface</em>
</p>

<p align="center">
  <img src="assets/screenshots/screenshot2.png" width="300">
  <br><em>Hypervisor Layer View</em>
</p>

## 🚀 Quick Start

### Prerequisites

- ARM64 device (Snapdragon/MediaTek/Exynos)
- Unlocked bootloader
- TWRP or custom recovery
- 6GB+ RAM, 128GB+ storage
- Linux build environment

### Building QWAMOS

```bash
# Clone repository
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS

# Set up toolchain
./build/scripts/setup_toolchain.sh

# Build everything (takes 2-4 hours)
./build/scripts/build_all.sh

# Package flashable image
./build/scripts/package_flash_image.sh
```

Output: `qwamos-v1.0.0-flashable.zip`

### Installing

#### Method 1: TWRP Recovery
```bash
adb reboot recovery
adb push qwamos-v1.0.0-flashable.zip /sdcard/
# Install via TWRP UI
```

#### Method 2: Fastboot
```bash
adb reboot bootloader
fastboot flash boot boot.img
fastboot flash system system.img
fastboot flash vendor vendor.img
fastboot -w
fastboot reboot
```

See [Installation Guide](docs/INSTALLATION.md) for detailed instructions.

## 🛠️ Development

### Project Structure

```
QWAMOS/
├── bootloader/          # U-Boot with Kyber verification
├── kernel/              # Linux 6.6 LTS with crypto modules
├── init/                # systemd init system
├── hypervisor/          # KVM/QEMU management
├── crypto/              # Kyber + ChaCha20 implementations
├── vms/                 # VM images and configs
├── network/             # Tor, VPN, firewall
├── storage/             # VeraCrypt integration
├── security/            # AEGIS, Ghost, Chimera
├── frontend/            # React Native UI
├── tools/               # KALI-WFH suite
├── build/               # Build system and scripts
├── device/              # Device-specific configs
└── docs/                # Documentation
```

### Development Roadmap

- [x] **Phase 0:** Project setup and architecture (Month 0)
- [ ] **Phase 1:** Foundation - Bootloader + Kernel (Months 1-2)
- [ ] **Phase 2:** Hypervisor & VMs (Months 3-4)
- [ ] **Phase 3:** Storage & Crypto (Months 5-6)
- [ ] **Phase 4:** Network & Security (Months 7-8)
- [ ] **Phase 5:** UI & Integration (Months 9-10)
- [ ] **Phase 6:** Testing & Release (Months 11-12)

See [Development Roadmap](docs/ROADMAP.md) for details.

## 🔐 Security

### Threat Model

QWAMOS is designed to protect against:

- Nation-state adversaries (NSA/GCHQ level)
- Post-quantum attacks (Shor's algorithm)
- Network surveillance
- Device seizure
- Cold boot attacks
- Side-channel attacks
- VM escape attempts

### Cryptographic Guarantees

- **Kyber-1024:** NIST Level 5 post-quantum security
- **ChaCha20-Poly1305:** 256-bit authenticated encryption
- **Argon2id:** Memory-hard key derivation
- **Constant-time:** All implementations resistant to timing attacks

See [Security Model](docs/SECURITY.md) for complete threat analysis.

## 🤝 Contributing

QWAMOS is open source (GPLv3). Contributions are welcome!

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for coding standards.

## 📄 License

QWAMOS is licensed under **GNU General Public License v3.0 (GPLv3)**

Key components:
- Linux Kernel: GPL-2.0
- U-Boot: GPL-2.0
- QEMU/KVM: GPL-2.0
- liboqs (Kyber): MIT
- libsodium (ChaCha20): ISC
- React Native: MIT
- Tor: BSD-3-Clause
- VeraCrypt: Apache 2.0

See [LICENSE](LICENSE) for full text.

## 🙏 Acknowledgments

QWAMOS builds upon the excellent work of:

- **Qubes OS Team** - VM isolation architecture
- **Whonix Project** - Tor anonymity framework
- **Open Quantum Safe (liboqs)** - Post-quantum cryptography
- **Android Open Source Project (AOSP)** - Android base
- **Kali Linux Team** - Penetration testing tools
- **VeraCrypt Team** - Disk encryption
- **WireGuard Team** - VPN implementation

## 📞 Support & Contact

- **Issues:** [GitHub Issues](https://github.com/Dezirae-Stark/QWAMOS/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Dezirae-Stark/QWAMOS/discussions)
- **Matrix:** #qwamos:matrix.org
- **Email:** dev@qwamos.org (coming soon)

## ⚠️ Disclaimer

QWAMOS is experimental software in active development. Use at your own risk. The authors are not responsible for any data loss, device damage, or security breaches.

**This software is intended for:**
- Security researchers
- Privacy enthusiasts
- Penetration testers
- Cryptocurrency users
- Advanced users comfortable with custom ROMs

**NOT recommended for:**
- Daily driver (yet - wait for v1.0 stable)
- Critical production systems
- Users unfamiliar with Android flashing

---

**Status:** Alpha Development
**Version:** 0.1.0-dev
**ETA to Production:** 12 months

**Made with ❤️ by Dezirae Stark and contributors**
