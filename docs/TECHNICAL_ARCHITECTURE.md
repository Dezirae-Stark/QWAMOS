# QWAMOS Technical Architecture
## Qubes Whonix Advanced Mobile Operating System

**Version:** 2.0.0-alpha (Base OS Architecture)
**Last Updated:** 2025-10-30
**Security Level:** Post-Quantum (Kyber-1024 + ChaCha20-Poly1305)
**License:** GPLv3

---

## Executive Summary

QWAMOS is a **ground-up mobile operating system** that replaces Android entirely. Built on a hardened Linux kernel with post-quantum cryptography, it provides Qubes OS-style VM compartmentalization where Android itself runs as just another isolated VM. The system features a custom bootloader, encrypted hypervisor layer, and military-grade security throughout the entire stack.

**Key Innovation:** Android becomes a guest OS running inside QWAMOS, not the base system.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Hardware Layer                           │
│    (ARM64 SoC, Snapdragon/MediaTek/Exynos, Unlocked Bootloader) │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Boot Sequence
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QWAMOS Bootloader (U-Boot)                    │
│         ┌───────────────────────────────────────┐               │
│         │  Secure Boot Verification             │               │
│         │  Kyber-1024 Signature Check           │               │
│         │  Anti-Rollback Protection             │               │
│         └───────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Verified Boot
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              QWAMOS Linux Kernel (Hardened 6.6 LTS)              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  PQ Crypto Modules: Kyber-1024 KEM, ChaCha20-Poly1305     │ │
│  │  KVM Hypervisor Support (ARM64 Virtualization)            │ │
│  │  Security: SELinux Enforcing, AppArmor, Seccomp-BPF       │ │
│  │  Network: Netfilter, WireGuard, Tor Integration           │ │
│  │  Storage: dm-crypt, VeraCrypt kernel driver               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Init
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  QWAMOS Init System (systemd)                    │
│         ┌───────────────────────────────────────┐               │
│         │  Encrypted Root FS Mount              │               │
│         │  Hypervisor Daemon Launch             │               │
│         │  Network Stack Initialization         │               │
│         │  Security Policy Enforcement          │               │
│         └───────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Service Start
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                QWAMOS Hypervisor Layer (KVM/QEMU)                │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐  │
│  │android-vm│whonix-vm │ kali-vm  │ vault-vm │disposable-vm │  │
│  │          │          │          │          │              │  │
│  │ Android  │ Whonix   │ Kali     │ AEGIS    │ Ephemeral    │  │
│  │ 14 AOSP  │ Gateway  │ Linux    │ Airgap   │ Temporary    │  │
│  │          │          │          │          │              │  │
│  │ [Isolated Memory, CPU, Storage, Network per VM]          │  │
│  │ [Each VM encrypted with unique ChaCha20-Poly1305 key]    │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ VM Communication
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              QWAMOS Network Isolation Layer                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Virtual Network Bridges (per-VM isolation)             │   │
│  │  Whonix Gateway (10.152.152.10) - Tor Transparent Proxy│   │
│  │  VPN Tunnel Manager (WireGuard + Kyber KEM)            │   │
│  │  Firewall Rules (iptables/nftables per VM)             │   │
│  │  Chimera Protocol (Decoy Traffic Generator)            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ User Interface
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│             QWAMOS Native UI (Wayland + React Native)            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Dashboard: Security Status, VM Manager, Quick Actions  │   │
│  │  AEGIS Vault: Crypto Wallet Management (QR Airgap)      │   │
│  │  KALI-WFH: Penetration Testing Suite                    │   │
│  │  Ghost: Self-Destruct & Emergency Controls              │   │
│  │  Settings: Encryption, Network, Theme Customization     │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Boot Sequence

### Stage 1: Bootloader (U-Boot + Kyber Verification)

```
Power On → BootROM (TrustZone) → U-Boot → Kernel
   │              │                  │        │
   │              │                  │        └─> Verify kernel signature (Kyber-1024)
   │              │                  └─> Load initramfs
   │              └─> Verify bootloader signature
   └─> Hardware initialization
```

**Security Features:**
- **Verified Boot Chain:** Each stage verifies the next using Kyber-1024 signatures
- **Anti-Rollback:** Version counters prevent downgrade attacks
- **Encrypted Boot:** Kernel and initramfs encrypted with device-unique key
- **TrustZone Integration:** Secure boot anchored in hardware

**Files:**
- `bootloader/u-boot/qwamos_defconfig` - U-Boot configuration
- `bootloader/u-boot/board/qwamos/` - Board-specific code
- `bootloader/scripts/sign_bootloader.sh` - Kyber signing script
- `bootloader/keys/` - Boot verification keys (Kyber public keys)

### Stage 2: Kernel Initialization

**Kernel Base:** Linux 6.6 LTS (hardened)

**Custom Patches:**
- KVM ARM64 hypervisor support
- Kyber-1024 crypto module
- ChaCha20-Poly1305 AEAD
- VeraCrypt kernel driver
- WireGuard with PQ crypto
- SELinux strict policy
- AppArmor profiles for VMs

**Kernel Config Highlights:**
```
CONFIG_KVM=y
CONFIG_KVM_ARM_HOST=y
CONFIG_CRYPTO_KYBER=m
CONFIG_CRYPTO_CHACHA20POLY1305=y
CONFIG_DM_CRYPT=y
CONFIG_DM_VERITY=y
CONFIG_SECURITY_SELINUX=y
CONFIG_SECURITY_APPARMOR=y
CONFIG_SECCOMP=y
CONFIG_WIREGUARD=y
```

**Files:**
- `kernel/config/qwamos_defconfig` - Kernel configuration
- `kernel/modules/crypto/kyber/` - Kyber KEM module
- `kernel/modules/crypto/chacha20/` - ChaCha20 module
- `kernel/modules/kvm/` - Hypervisor patches
- `kernel/drivers/veracrypt/` - VeraCrypt driver

### Stage 3: Init System (systemd)

**Boot Targets:**
1. `qwamos-early.target` - Decrypt root filesystem
2. `qwamos-crypto.target` - Load crypto modules
3. `qwamos-hypervisor.target` - Start KVM/QEMU daemons
4. `qwamos-network.target` - Initialize network isolation
5. `qwamos-ui.target` - Launch Wayland compositor + UI

**Files:**
- `init/systemd/qwamos-early.service`
- `init/systemd/qwamos-hypervisor.service`
- `init/systemd/qwamos-network.service`
- `init/scripts/decrypt_root.sh`

---

## Hypervisor Architecture

### KVM/QEMU Integration

**Why KVM on ARM64:**
- Hardware-accelerated virtualization (ARMv8 Virtualization Extensions)
- Near-native performance for VMs
- Strong isolation (Stage 2 memory translation)
- Mainline Linux support

**QEMU Configuration:**
- ARM64 virt machine type
- VirtIO devices (network, block, GPU)
- PCI passthrough for hardware (optional)
- SPICE/VNC for display (or native Wayland bridge)

**Files:**
- `hypervisor/kvm/qwamos_kvm_host.c` - Host KVM controller
- `hypervisor/qemu/qwamos_qemu_wrapper.py` - QEMU VM manager
- `hypervisor/qemu/configs/android-vm.xml` - Android VM config
- `hypervisor/qemu/configs/whonix-vm.xml` - Whonix VM config

### VM Definitions

#### 1. android-vm (Android Guest)

**Purpose:** Run Android 14 AOSP as isolated VM for apps

**Specs:**
- CPU: 4 vCPUs
- RAM: 4GB
- Storage: 32GB virtual disk (encrypted)
- Network: NAT via Whonix gateway
- Display: VirtIO GPU with Wayland passthrough

**Android Image:**
- Based on AOSP 14 (no Google services)
- Custom init.rc for VM environment
- Pre-installed apps: F-Droid, Aurora Store
- VirtIO drivers compiled into kernel

**Files:**
- `vms/android/android-14-aosp.img` - System image
- `vms/android/build_android_vm.sh` - Build script
- `vms/android/kernel/` - Android VM kernel
- `vms/android/init.qwamos.rc` - Custom init

#### 2. whonix-vm (Tor Gateway)

**Purpose:** Transparent Tor proxy for all VMs

**Specs:**
- CPU: 2 vCPUs
- RAM: 1GB
- Storage: 8GB
- Network: Two interfaces (external + internal)
- Display: Headless (managed via CLI)

**Features:**
- All VM traffic routed through Tor
- Stream isolation per VM
- Connection/Active/Isolation modes
- DNS leak prevention

**Files:**
- `vms/whonix/whonix-gateway-17.img` - Whonix image
- `vms/whonix/torrc.qwamos` - Tor configuration
- `vms/whonix/iptables-gateway.rules` - Firewall rules

#### 3. kali-vm (Penetration Testing)

**Purpose:** Full Kali Linux environment for security testing

**Specs:**
- CPU: 4 vCPUs
- RAM: 4GB
- Storage: 64GB
- Network: Isolated namespace + Tor access
- Display: Wayland bridge to native UI

**Tools Included:**
- OSINT: Maltego, TheHarvester, SpiderFoot
- Network: Nmap, Wireshark, Netcat
- Web: Burp Suite, OWASP ZAP, SQLmap
- Exploit: Metasploit, BeEF, SET

**Files:**
- `vms/kali/kali-linux-2024.img` - Kali image
- `vms/kali/tool_manifest.json` - Tool list
- `tools/kali-wfh/launcher.py` - Tool launcher

#### 4. vault-vm (AEGIS Airgapped Vault)

**Purpose:** Completely airgapped cold storage for crypto wallets

**Specs:**
- CPU: 2 vCPUs
- RAM: 2GB
- Storage: 16GB (encrypted with Kyber)
- Network: **NONE** (enforced at kernel level)
- Display: QR code I/O only

**Security:**
- Network device removed at VM level
- No USB passthrough
- QR code communication only
- Encrypted memory pages

**Wallets Supported:**
- Samourai Wallet (Bitcoin + Whirlpool)
- Cake Wallet (Monero XMR)
- Sparrow Wallet
- Generic BIP39 wallets

**Files:**
- `vms/vault/aegis-vault.img` - Vault image
- `security/aegis/qr_signer.py` - Transaction signing
- `security/aegis/wallet_manager.py` - Wallet orchestration
- `security/aegis/airgap_enforcer.c` - Network blocker

#### 5. disposable-vm (Ephemeral)

**Purpose:** Temporary VM for untrusted operations

**Specs:**
- CPU: 2 vCPUs
- RAM: 2GB
- Storage: 8GB (tmpfs, auto-wiped)
- Network: Tor only
- Display: Isolated framebuffer

**Features:**
- Boots from read-only template
- All changes in RAM
- Auto-destroyed on close
- No persistent storage

**Files:**
- `vms/disposable/template.img` - Base template
- `vms/disposable/ephemeral_manager.py` - Lifecycle manager

---

## Post-Quantum Cryptography Layer

### Kyber-1024 Implementation

**Algorithm:** CRYSTALS-Kyber (NIST FIPS 203 Draft)
**Security Level:** 256-bit (Level 5)
**Key Sizes:**
- Public key: 1568 bytes
- Secret key: 3168 bytes
- Ciphertext: 1568 bytes

**Use Cases:**
1. **Boot Chain:** Bootloader → Kernel signature verification
2. **Key Encapsulation:** Wrapping ChaCha20 keys for VM storage
3. **Network:** Hybrid TLS (Kyber + X25519) for VPN
4. **VeraCrypt:** Key wrapping for volume encryption

**Implementation:**
- **Kernel Module:** `kernel/modules/crypto/kyber/kyber1024.ko`
- **User-space Library:** `crypto/kyber/libqwamos_kyber.so`
- **CLI Tool:** `crypto/kyber/kyber-keygen`

**Code Structure:**
```c
// crypto/kyber/kyber_kem.c
int kyber1024_keypair(uint8_t *pk, uint8_t *sk);
int kyber1024_enc(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int kyber1024_dec(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
```

**Files:**
- `crypto/kyber/kyber1024.c` - Core implementation
- `crypto/kyber/kyber_kem.c` - KEM interface
- `crypto/kyber/kyber_test.c` - Test vectors
- `crypto/kyber/Makefile` - Build system

### ChaCha20-Poly1305 Implementation

**Algorithm:** ChaCha20 stream cipher + Poly1305 MAC (RFC 8439)
**Security Level:** 256-bit key
**Features:**
- Authenticated Encryption with Associated Data (AEAD)
- Constant-time implementation
- Resistant to timing attacks
- Fast on ARM NEON

**Use Cases:**
1. **VM Storage:** Encrypting VM disk images
2. **VeraCrypt Volumes:** Modern alternative to AES
3. **Network:** WireGuard tunnels
4. **Memory:** Encrypted swap and hibernation

**Implementation:**
- **Kernel Module:** `kernel/modules/crypto/chacha20/chacha20_poly1305.ko`
- **User-space Library:** `crypto/chacha20/libqwamos_chacha.so`

**Code Structure:**
```c
// crypto/chacha20/chacha20_poly1305.c
int chacha20_poly1305_encrypt(
    uint8_t *ciphertext,
    const uint8_t *plaintext,
    size_t plaintext_len,
    const uint8_t *key,
    const uint8_t *nonce,
    const uint8_t *ad,
    size_t ad_len
);
```

**Files:**
- `crypto/chacha20/chacha20_core.c` - ChaCha20 cipher
- `crypto/chacha20/poly1305.c` - Poly1305 MAC
- `crypto/chacha20/chacha20_poly1305.c` - AEAD combination
- `crypto/chacha20/Makefile` - Build system

### Key Derivation (Argon2id)

**Algorithm:** Argon2id (RFC 9106)
**Parameters:**
- Memory: 2 GB
- Iterations: 3
- Parallelism: 4
- Output: 32 bytes

**Use Cases:**
- Deriving encryption keys from user passphrase
- Master key derivation for VeraCrypt
- VM-specific key derivation

**Files:**
- `crypto/kdf/argon2id.c` - Argon2 implementation
- `crypto/kdf/kdf_manager.c` - Key derivation API

---

## Storage & Encryption

### VeraCrypt Integration

**Purpose:** Encrypted container volumes for sensitive data

**Features:**
- AES-256 cascaded with Twofish
- Kyber-1024 key wrapping (post-quantum)
- Hidden volumes (plausible deniability)
- PIM (Personal Iterations Multiplier)

**Volume Types:**
1. **ENCRYPT-KYESC**: Custom algorithm (ChaCha20 + Kyber)
2. **ENCRYPT-CHAA3S0**: Custom cascade (ChaCha + AES + Serpent)
3. **Standard**: AES-256 + Kyber wrapper

**Files:**
- `storage/veracrypt/veracrypt_manager.c` - Volume manager
- `storage/veracrypt/mount_helper.c` - Mounting daemon
- `storage/veracrypt/kyber_wrapper.c` - PQ key wrapping
- `kernel/drivers/veracrypt/` - Kernel driver

### Encrypted Root Filesystem

**Technology:** dm-crypt + LUKS2

**Configuration:**
- Cipher: ChaCha20-Poly1305
- Key derivation: Argon2id
- Key size: 256-bit
- Header authentication: Kyber-1024 signature

**Boot Sequence:**
1. Bootloader decrypts initramfs
2. Initramfs prompts for passphrase
3. Derive key with Argon2id
4. Unwrap LUKS master key with Kyber
5. Mount encrypted root
6. Pivot to main system

**Files:**
- `init/scripts/decrypt_root.sh` - Decryption script
- `build/scripts/create_encrypted_root.sh` - Image creation

---

## Network Architecture

### Whonix Gateway Integration

**Architecture:**
```
[Internet] ← → [Whonix GW VM] ← → [Internal Bridge] ← → [VMs]
                     ↓
              Tor Network
           (10.152.152.10)
```

**Modes:**
1. **Connection:** Tor circuit establishing
2. **Active:** Tor connection established, traffic flowing
3. **Isolation:** Tor disconnected, all VMs offline

**Stream Isolation:**
- Each VM gets unique SOCKS port
- Prevents correlation of activities
- DNS requests isolated per VM

**Files:**
- `network/tor/torrc.qwamos` - Tor configuration
- `network/tor/controller.py` - Tor control port interface
- `vms/whonix/gateway_setup.sh` - Gateway initialization

### VPN Integration (WireGuard + Kyber)

**Hybrid Cryptography:**
- Classical: X25519 (Curve25519 ECDH)
- Post-Quantum: Kyber-1024
- Symmetric: ChaCha20-Poly1305

**Configurations:**
- Tor over VPN: VPN → Tor → Internet
- VPN over Tor: Tor → VPN → Internet
- Multi-hop VPN: VPN1 → VPN2 → Tor

**Files:**
- `network/vpn/wireguard_manager.py` - VPN controller
- `network/vpn/killswitch.py` - Network kill switch
- `network/vpn/hybrid_kex.c` - Kyber+X25519 key exchange

### Chimera Protocol (Decoy Traffic)

**Purpose:** Generate realistic decoy traffic to obfuscate real activities

**Patterns:**
- Web browsing (HTTP/HTTPS)
- Video streaming (YouTube-like)
- Email checking (IMAP/SMTP)
- Social media (REST API calls)

**Configuration:**
- Traffic volume: Adjustable (10KB/s - 1MB/s)
- Timing: Randomized with Poisson distribution
- Destinations: Rotating list of benign sites
- Protocol distribution: 60% HTTPS, 30% HTTP, 10% DNS

**Files:**
- `security/chimera/traffic_generator.py` - Main engine
- `security/chimera/patterns/` - Traffic patterns (JSON)
- `security/chimera/scheduler.py` - Timing controller

### Firewall (nftables)

**Rules:**
- Default deny all
- Per-VM network namespaces
- Whonix gateway routing rules
- VPN tunnel enforcement
- Kill switch (drop on VPN/Tor failure)

**Files:**
- `network/firewall/nftables.conf` - Main firewall rules
- `network/firewall/vm_isolation.nft` - Per-VM rules
- `network/firewall/killswitch.nft` - Emergency rules

---

## AEGIS Vault (Airgapped Cold Storage)

### Architecture

**Security Model:**
- Complete network isolation (no NIC in VM)
- QR code-only communication
- Encrypted storage (Kyber + ChaCha20)
- Memory encryption (encrypted swap)

### Transaction Signing Flow

```
┌─────────────┐                    ┌─────────────┐
│  work-vm    │                    │  vault-vm   │
│             │                    │  (AIRGAP)   │
│ 1. Create   │                    │             │
│    unsigned │                    │             │
│    tx       │                    │             │
│             │                    │             │
│ 2. Generate ├───────────────────>│ 3. Scan QR  │
│    QR code  │  (User's camera)   │             │
│             │                    │ 4. Parse tx │
│             │                    │             │
│             │                    │ 5. Sign with│
│             │                    │    wallet   │
│             │                    │             │
│ 7. Scan QR  │<───────────────────┤ 6. Display  │
│             │  (User's camera)   │    signed tx│
│             │                    │    as QR    │
│ 8. Broadcast│                    │             │
│    to       │                    │             │
│    network  │                    │             │
└─────────────┘                    └─────────────┘
```

### Supported Wallets

**1. Samourai Wallet**
- BIP44/49/84 derivation
- Whirlpool CoinJoin integration
- STONEWALL/STOWAWAY privacy features
- PayNym support

**2. Cake Wallet (Monero)**
- Monero XMR primary support
- Polyseed format
- Subaddresses
- Integrated/standard addresses

**3. Sparrow Wallet**
- Bitcoin-only
- Full PSBT support
- Multisig coordination
- Hardware wallet integration

**Files:**
- `security/aegis/vault_vm/wallet_manager.py` - Wallet orchestrator
- `security/aegis/vault_vm/qr_signer.py` - Transaction signing
- `security/aegis/vault_vm/airgap_enforcer.c` - Network blocker
- `security/aegis/wallets/samourai/` - Samourai integration
- `security/aegis/wallets/cake/` - Cake Wallet integration
- `security/aegis/wallets/sparrow/` - Sparrow integration

### QR Code Protocol

**Format:**
- Encoding: Base64
- Encryption: ChaCha20-Poly1305 (optional)
- Signature: Kyber-1024 (for verification)
- Animation: Supported for large transactions (multi-part QR)

**Libraries:**
- `qrencode` - QR generation
- `zbar` - QR scanning
- Custom: `security/aegis/qr_bridge/encoder.py`

---

## KALI-WFH Suite

### Tool Integration

**Architecture:**
```
QWAMOS UI (React Native)
         ↓
Tool Launcher API (Python FastAPI)
         ↓
Kali VM (QEMU/KVM)
         ↓
Kali Linux Tools
```

**Tool Categories:**

#### 1. OSINT (Open Source Intelligence)

**Maltego:**
- Relationship graphing
- Entity discovery
- Infrastructure mapping

**TheHarvester:**
- Email enumeration
- Subdomain discovery
- Employee harvesting

**SpiderFoot:**
- Automated OSINT
- Target profiling
- Reputation checking

**Shodan CLI:**
- IoT device discovery
- Vulnerability search
- Banner grabbing

**Files:**
- `tools/osint/maltego_wrapper.py`
- `tools/osint/theharvester_wrapper.py`
- `tools/osint/spiderfoot_wrapper.py`

#### 2. Network Analysis

**Nmap:**
- Port scanning
- Service detection
- OS fingerprinting
- NSE scripts

**Wireshark:**
- Packet capture
- Protocol analysis
- Traffic visualization

**Gobuster:**
- Directory bruteforcing
- Subdomain enumeration
- Virtual host discovery

**Files:**
- `tools/network/nmap_wrapper.py`
- `tools/network/wireshark_wrapper.py`
- `tools/network/gobuster_wrapper.py`

#### 3. Web Application

**Burp Suite:**
- Proxy interception
- Scanner
- Intruder
- Repeater

**OWASP ZAP:**
- Automated scanning
- Fuzzing
- Spider

**SQLmap:**
- SQL injection detection
- Database extraction
- OS takeover

**Files:**
- `tools/webapp/burp_wrapper.py`
- `tools/webapp/zap_wrapper.py`
- `tools/webapp/sqlmap_wrapper.py`

#### 4. Exploitation

**Metasploit Framework:**
- Exploit database
- Payload generation
- Post-exploitation

**Social Engineer Toolkit (SET):**
- Phishing campaigns
- Credential harvesting
- HID attacks

**Files:**
- `tools/exploit/metasploit_wrapper.py`
- `tools/exploit/set_wrapper.py`

### Tool Launcher

**API Endpoints:**
```
POST /tools/osint/maltego/scan
POST /tools/network/nmap/scan
POST /tools/webapp/burp/start
GET  /tools/{category}/{tool}/status
GET  /tools/{category}/{tool}/results
```

**Files:**
- `tools/kali-wfh/launcher.py` - FastAPI server
- `tools/kali-wfh/tool_manifest.json` - Tool definitions
- `frontend/services/kaliService.ts` - React Native client

---

## Ghost Self-Destruct System

### Trigger Types

#### 1. System Status Triggers

**VPN Disconnection:**
- Monitor WireGuard interface
- Threshold: 60 seconds offline
- Action: Wipe VMs + keys

**Tor Circuit Failure:**
- Monitor Tor control port
- Threshold: 120 seconds offline
- Action: Full wipe

**Whonix Gateway Offline:**
- Monitor gateway VM status
- Threshold: 30 seconds offline
- Action: Network isolation + wipe

**Files:**
- `security/ghost/triggers/vpn_monitor.py`
- `security/ghost/triggers/tor_monitor.py`
- `security/ghost/triggers/whonix_monitor.py`

#### 2. Distribution Triggers

**Cloud Disconnection:**
- Monitor last check-in timestamp
- Threshold: Configurable (24-72 hours)
- Action: Deadman switch activation

**USB Token Removal:**
- Monitor USB device presence
- Threshold: Immediate
- Action: Lock + optional wipe

**Failed Check-in:**
- Require periodic user authentication
- Threshold: Configurable interval
- Action: Progressive (lock → wipe)

**Files:**
- `security/ghost/triggers/deadman_switch.py`
- `security/ghost/triggers/token_watcher.py`
- `security/ghost/triggers/checkin_monitor.py`

### Destruction Engine

**Wipe Methods:**
- **VMs:** 7-pass DoD 5220.22-M
- **Keys:** 3-pass + zeroing
- **Logs:** Immediate deletion
- **Swap:** Encrypted swap deletion

**Selective Wipe:**
- Configuration: `security/ghost/config/destruction_policy.yaml`
- Options: VMs only, Keys only, Full system, Custom

**Emergency Mode:**
- Duress password → Boot into decoy OS
- Hardware button combo → Immediate panic wipe
- Remote wipe command (via encrypted channel)

**Files:**
- `security/ghost/destruction_engine.c` - Secure wipe implementation
- `security/ghost/trigger_monitor.py` - Trigger coordinator
- `security/ghost/config/destruction_policy.yaml` - Policy configuration

---

## User Interface

### Technology Stack

**Display Server:** Wayland (not X11)
- Security: No network transparency exploit surface
- Performance: Better for mobile
- Isolation: Per-VM framebuffers

**Compositor:** Weston (customized)
- Touch-optimized
- Multi-VM window management
- Hardware acceleration

**UI Framework:** React Native
- Cross-platform (if needed)
- Rich ecosystem
- Fast development

**Rendering:** React Native → Native Modules → Wayland Client

### UI Components

#### Dashboard

**Security Status Panel:**
- Encryption: ACTIVE (Kyber-1024 + ChaCha20)
- KYESC: CONNECTED
- Chaa3s0: ENABLED

**VeraCrypt Volumes:**
- ENCRYPT-KYESC+CHAA3S0: Mounted
- work-deb.12: READY (128GB available)
- home.deb.12: DISCONNECTED

**Network Status:**
- VPN: CONNECTED (NordVPN Sweden)
- Tor: ACTIVE (3-hop circuit)
- Whonix: ACTIVE

**Whonix Gateway:**
- Connection Mode / Active Mode / Isolation Mode
- Current: Active Mode

**Files:**
- `frontend/screens/Dashboard.tsx`
- `frontend/components/SecurityStatus.tsx`
- `frontend/components/VeraCryptPanel.tsx`
- `frontend/components/NetworkStatus.tsx`

#### AEGIS Vault

**Components:**
- Wallet selection dropdown
- Balance display
- QR scanner (camera access)
- QR generator (transaction signing)
- Airgap status indicator (ENABLED/DISABLED)

**Files:**
- `frontend/screens/AegisVault.tsx`
- `frontend/components/WalletSelector.tsx`
- `frontend/components/QRScanner.tsx`

#### KALI-WFH

**Components:**
- Tool category tabs (OSINT/Network/WebApp/Exploit)
- Tool cards with status indicators
- Scan configuration dialogs
- Results viewer (tabular + visual)
- Automated exploitation wizard

**Files:**
- `frontend/screens/KaliWFH.tsx`
- `frontend/components/ToolCard.tsx`
- `frontend/components/ScanResults.tsx`

#### VM Manager

**Components:**
- VM list with status (Running/Stopped/Suspended)
- Start/Stop/Restart buttons
- Resource usage graphs (CPU/RAM/Network)
- Network isolation toggles
- Quick actions (Create VM, Clone, Delete)

**Files:**
- `frontend/screens/VMManager.tsx`
- `frontend/components/VMCard.tsx`
- `frontend/components/ResourceGraph.tsx`

#### Ghost Self-Destruct

**Components:**
- System status triggers (VPN/Tor/Whonix)
- Distribution triggers (Cloud/Token/Check-in)
- Wipe targets checkboxes
- Armed/Disarmed toggle
- Emergency wipe button (requires confirmation)

**Files:**
- `frontend/screens/GhostSelfDestruct.tsx`
- `frontend/components/TriggerConfig.tsx`
- `frontend/components/EmergencyWipe.tsx`

#### Settings

**Sections:**
- Theme Customization (Dark Mode, Colors, Fonts)
- Encryption Algorithms (Kyber/ChaCha/AES selection)
- Network Settings (VPN/Tor/Whonix config)
- Self-Destruct Configuration
- System Information

**Files:**
- `frontend/screens/Settings.tsx`
- `frontend/components/ThemeCustomizer.tsx`
- `frontend/components/EncryptionSettings.tsx`

### Theme System

**Color Palette (Cyberpunk Dark):**
- Background: #0a0e27 (dark navy)
- Surface: #1a1f3a (lighter navy)
- Primary: #00ffff (cyan)
- Secondary: #ff00ff (magenta)
- Accent: #ffff00 (yellow)
- Success: #00ff00 (green)
- Error: #ff0000 (red)
- Warning: #ff8800 (orange)

**Typography:**
- Font: System Default / Cascadia Code / Courier New
- Sizes: 12pt / 14pt / 16pt / 18pt / 20pt

**Files:**
- `frontend/theme/colors.ts`
- `frontend/theme/typography.ts`
- `frontend/theme/ThemeProvider.tsx`

---

## Build System

### Toolchain

**Cross-Compilation:**
- Host: x86_64 Linux (or ARM64 Linux)
- Target: aarch64-linux-android (ARM64)
- Toolchain: Android NDK r26 + Clang 17

**Build Tools:**
- Kernel: GNU Make + Kbuild
- Bootloader: U-Boot build system
- Crypto: CMake
- Frontend: Node.js + Metro bundler
- System: Buildroot (custom config)

**Files:**
- `build/toolchain/setup_toolchain.sh` - Toolchain installation
- `build/scripts/build_all.sh` - Full system build
- `build/configs/buildroot_qwamos.config` - Buildroot config

### Build Steps

#### 1. Bootloader
```bash
cd bootloader/u-boot
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- qwamos_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)
./scripts/sign_bootloader.sh u-boot.bin
```

**Output:** `u-boot-signed.bin`

#### 2. Kernel
```bash
cd kernel
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- qwamos_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc) Image.gz dtbs modules
```

**Output:** `arch/arm64/boot/Image.gz`, `*.dtb`, `*.ko`

#### 3. Crypto Modules
```bash
cd crypto
mkdir build && cd build
cmake -DCMAKE_TOOLCHAIN_FILE=../cmake/aarch64-toolchain.cmake ..
make -j$(nproc)
```

**Output:** `libqwamos_kyber.so`, `libqwamos_chacha.so`, `*.ko`

#### 4. Initramfs
```bash
cd init
./build_initramfs.sh
```

**Output:** `initramfs.cpio.gz`

#### 5. Root Filesystem
```bash
cd build
make buildroot-qwamos
```

**Output:** `rootfs.tar.gz`

#### 6. VM Images
```bash
cd vms
./build_android_vm.sh
./build_whonix_vm.sh
./build_kali_vm.sh
./build_vault_vm.sh
```

**Output:** `*.qcow2` images

#### 7. Frontend
```bash
cd frontend
npm install
npm run build:android
```

**Output:** `qwamos-ui.apk` (React Native app)

#### 8. Package Flash Image
```bash
cd build
./scripts/package_flash_image.sh
```

**Output:** `qwamos-v1.0.0-flashable.zip`

**Contents:**
- `boot.img` (kernel + initramfs)
- `system.img` (root filesystem)
- `vendor.img` (proprietary blobs if needed)
- `vbmeta.img` (verified boot metadata)
- `META-INF/com/google/android/update-binary` (flash script)

**Files:**
- `build/scripts/build_all.sh` - Master build script
- `build/scripts/package_flash_image.sh` - Image packaging
- `build/configs/flash_script.sh` - TWRP flash script template

---

## Installation & Flashing

### Prerequisites

**Device Requirements:**
- Unlocked bootloader
- TWRP or custom recovery installed
- ARM64 processor (ARMv8+)
- 6GB+ RAM
- 128GB+ storage

**Host Requirements:**
- ADB (Android Debug Bridge)
- Fastboot
- USB cable
- Linux/Windows/macOS host

### Flashing Steps

#### Method 1: TWRP Recovery

```bash
# 1. Reboot to recovery
adb reboot recovery

# 2. Push flash package
adb push qwamos-v1.0.0-flashable.zip /sdcard/

# 3. Install via TWRP UI
# Tap "Install" → Select qwamos-v1.0.0-flashable.zip → Swipe to confirm

# 4. Wipe data (recommended for first install)
# Tap "Wipe" → Format Data

# 5. Reboot
# Tap "Reboot System"
```

#### Method 2: Fastboot (Manual)

```bash
# 1. Reboot to bootloader
adb reboot bootloader

# 2. Flash partitions
fastboot flash boot boot.img
fastboot flash system system.img
fastboot flash vendor vendor.img
fastboot flash vbmeta --disable-verity --disable-verification vbmeta.img

# 3. Wipe userdata
fastboot -w

# 4. Reboot
fastboot reboot
```

### First Boot

**Setup Wizard:**
1. Language selection
2. Encryption passphrase (Argon2id key derivation)
3. Network configuration (WiFi + VPN)
4. Whonix Gateway setup (Tor configuration)
5. AEGIS Vault setup (wallet import/creation)
6. Theme customization

**Initial Root Decryption:**
- Prompt for passphrase
- Derive key with Argon2id (30-60 seconds)
- Unwrap LUKS master key with Kyber
- Mount encrypted root filesystem
- Boot continues

**Files:**
- `system/core/setup_wizard/` - Setup wizard implementation
- `init/scripts/first_boot.sh` - First boot initialization

---

## Development Roadmap

### Phase 1: Foundation (Months 1-2)

**Week 1-2:**
- [ ] Set up cross-compilation toolchain
- [ ] Configure U-Boot for target device
- [ ] Implement Kyber-1024 bootloader verification
- [ ] Test secure boot chain

**Week 3-4:**
- [ ] Configure Linux kernel 6.6 LTS
- [ ] Compile Kyber and ChaCha20 kernel modules
- [ ] Enable KVM hypervisor support
- [ ] Test kernel boot on device

**Week 5-6:**
- [ ] Build initramfs with encryption support
- [ ] Implement Argon2id key derivation
- [ ] Configure dm-crypt/LUKS2 with ChaCha20
- [ ] Test encrypted root filesystem

**Week 7-8:**
- [ ] Set up systemd init system
- [ ] Configure boot targets and services
- [ ] Implement hypervisor daemon
- [ ] Test VM launching

**Deliverable:** Bootable QWAMOS base system with encrypted root

### Phase 2: Hypervisor & VMs (Months 3-4)

**Week 9-10:**
- [ ] Configure KVM on ARM64
- [ ] Build QEMU with VirtIO devices
- [ ] Create VM management API
- [ ] Test basic VM creation

**Week 11-12:**
- [ ] Build Android 14 AOSP image for VM
- [ ] Compile VirtIO drivers into Android kernel
- [ ] Configure Android for VM environment
- [ ] Test Android VM boot

**Week 13-14:**
- [ ] Set up Whonix Gateway VM
- [ ] Configure Tor transparent proxy
- [ ] Implement stream isolation
- [ ] Test Tor routing for VMs

**Week 15-16:**
- [ ] Build Kali Linux VM image
- [ ] Install penetration testing tools
- [ ] Configure network isolation
- [ ] Test tool execution

**Deliverable:** Working hypervisor with Android, Whonix, and Kali VMs

### Phase 3: Storage & Crypto (Months 5-6)

**Week 17-18:**
- [ ] Integrate VeraCrypt kernel driver
- [ ] Implement volume management daemon
- [ ] Add Kyber-1024 key wrapping
- [ ] Test VeraCrypt mounting

**Week 19-20:**
- [ ] Implement AEGIS Vault VM
- [ ] Enforce network airgap at kernel level
- [ ] Build QR code transaction signing
- [ ] Test wallet integration (Samourai)

**Week 21-22:**
- [ ] Integrate Cake Wallet (Monero)
- [ ] Integrate Sparrow Wallet (Bitcoin)
- [ ] Test end-to-end transaction signing
- [ ] Verify airgap enforcement

**Week 23-24:**
- [ ] Implement disposable VM template
- [ ] Build ephemeral manager
- [ ] Configure auto-wipe on close
- [ ] Test ephemeral VM lifecycle

**Deliverable:** Full storage encryption and AEGIS Vault functional

### Phase 4: Network & Security (Months 7-8)

**Week 25-26:**
- [ ] Integrate WireGuard with Kyber KEM
- [ ] Implement hybrid key exchange
- [ ] Configure VPN kill switch
- [ ] Test multi-hop VPN scenarios

**Week 27-28:**
- [ ] Build Chimera Protocol decoy traffic
- [ ] Implement traffic patterns
- [ ] Configure timing randomization
- [ ] Test traffic generation

**Week 29-30:**
- [ ] Implement Ghost Self-Destruct triggers
- [ ] Build destruction engine (DoD 5220.22-M)
- [ ] Configure trigger monitoring
- [ ] Test emergency wipe scenarios

**Week 31-32:**
- [ ] Implement plausible deniability features
- [ ] Create decoy OS profile
- [ ] Configure duress passwords
- [ ] Test "tourist mode" transformation

**Deliverable:** Complete network isolation and self-destruct system

### Phase 5: UI & Integration (Months 9-10)

**Week 33-36:**
- [ ] Set up Wayland compositor (Weston)
- [ ] Configure touch input handling
- [ ] Implement VM window management
- [ ] Test display rendering

**Week 37-40:**
- [ ] Build React Native frontend
- [ ] Implement Dashboard screen
- [ ] Implement AEGIS Vault screen
- [ ] Implement KALI-WFH screen
- [ ] Implement VM Manager screen
- [ ] Implement Ghost Self-Destruct screen
- [ ] Implement Settings screen

**Week 41-42:**
- [ ] Build native modules for crypto
- [ ] Implement React Native bridges
- [ ] Connect UI to backend services
- [ ] Test end-to-end UI flows

**Week 43-44:**
- [ ] Implement theme customization
- [ ] Add animations and polish
- [ ] Optimize performance
- [ ] User testing

**Deliverable:** Complete user interface matching mockup designs

### Phase 6: Testing & Release (Months 11-12)

**Week 45-46:**
- [ ] Security audit (penetration testing)
- [ ] Cryptographic primitive validation
- [ ] Side-channel attack testing
- [ ] Memory forensics resistance

**Week 47-48:**
- [ ] Functional testing (all features)
- [ ] Performance testing (benchmarks)
- [ ] Compatibility testing (devices)
- [ ] Stress testing (resource limits)

**Week 49-50:**
- [ ] Write user documentation
- [ ] Write developer documentation
- [ ] Create installation guides
- [ ] Prepare community audit materials

**Week 51-52:**
- [ ] Bug fixes and refinements
- [ ] Create release candidate
- [ ] Community testing
- [ ] Final release

**Deliverable:** QWAMOS v1.0.0 Production Release

---

## Target Devices

### Initial Support

**Google Pixel Series:**
- Pixel 6/7/8 (Tensor SoC)
- Good bootloader unlock support
- Strong community

**OnePlus:**
- OnePlus 9/10/11 (Snapdragon)
- Easy bootloader unlock
- Custom ROM friendly

**Xiaomi:**
- Poco F5/F6 (Snapdragon)
- Affordable flagship specs
- Community support

### Device Tree Requirements

**Minimum:**
- ARM64 architecture (ARMv8-A)
- KVM support (Virtualization Extensions)
- 6GB+ RAM
- 128GB+ storage
- Unlockable bootloader

**Files:**
- `device/generic/qwamos/` - Generic device tree
- `device/google/pixel/` - Pixel-specific tree
- `device/oneplus/` - OnePlus-specific tree

---

## Security Considerations

### Threat Model

**Protected Against:**
- **Nation-state adversaries:** Post-quantum crypto, VM isolation
- **Network surveillance:** Tor + VPN + Chimera decoy traffic
- **Device seizure:** Full disk encryption, self-destruct
- **Cold boot attacks:** Encrypted RAM, fast wipe
- **Side-channel attacks:** Constant-time crypto implementations
- **VM escape:** KVM hardening, AppArmor profiles
- **Quantum computers:** Kyber-1024 (NIST PQC standard)

**NOT Protected Against:**
- **Supply chain attacks:** Hardware backdoors (baseband processor)
- **$5 wrench attacks:** Physical coercion for passphrase
- **Zero-day kernel exploits:** (Until patched)
- **Malicious hypervisor:** Root compromise = full compromise
- **Evil maid attacks:** (Requires hardware security module)

### Cryptographic Guarantees

**Post-Quantum Security:**
- Kyber-1024: IND-CCA2 secure against quantum adversaries
- Security level: NIST Level 5 (256-bit equivalent)
- Resistant to Shor's algorithm and Grover's algorithm

**Classical Security:**
- ChaCha20-Poly1305: 256-bit key, IND-CPA + INT-CTXT secure
- Argon2id: Memory-hard, resistant to GPU/ASIC attacks
- Constant-time: All implementations resistant to timing attacks

### Key Hierarchy

```
Device Root Key (TrustZone, hardware-backed)
    ├─> Bootloader Verification Key (Kyber-1024 public)
    │       └─> U-Boot Signature
    │
    ├─> Kernel Signing Key (Kyber-1024 public)
    │       └─> Kernel Image Signature
    │
    └─> Master Encryption Key (256-bit, derived from passphrase)
            ├─> LUKS Root FS Key (ChaCha20)
            │
            ├─> VM Encryption Keys (per-VM ChaCha20)
            │   ├─> android-vm.qcow2
            │   ├─> whonix-vm.qcow2
            │   ├─> kali-vm.qcow2
            │   ├─> vault-vm.qcow2 (Kyber-wrapped)
            │   └─> disposable-vm.qcow2
            │
            └─> VeraCrypt Volume Keys (Kyber-wrapped)
                ├─> ENCRYPT-KYESC.vol
                ├─> ENCRYPT-CHAA3S0.vol
                └─> standard-aes.vol
```

---

## Performance Targets

### Boot Time
- Cold boot to UI: < 60 seconds
- VM startup (Android): < 15 seconds
- VM startup (Linux): < 5 seconds

### VM Performance
- CPU overhead: < 5% (KVM hardware acceleration)
- Memory overhead: ~200MB per VM (QEMU)
- Storage I/O: ~80% of native (VirtIO)
- Network latency: +50-100ms (Tor routing)

### Encryption Overhead
- ChaCha20-Poly1305: < 5% CPU (ARM NEON optimized)
- Kyber-1024 keygen: ~10ms
- Kyber-1024 encaps/decaps: ~5ms
- Argon2id (2GB, 3 iter): ~30-60 seconds (acceptable for boot)

### UI Responsiveness
- Touch latency: < 50ms
- Frame rate: 60 FPS (Wayland vsync)
- App launch: < 2 seconds

---

## Dependencies & Licensing

### Core Components

**Linux Kernel 6.6 LTS** (GPL-2.0)
**U-Boot Bootloader** (GPL-2.0)
**QEMU/KVM** (GPL-2.0)
**systemd** (LGPL-2.1)
**Wayland/Weston** (MIT)
**React Native** (MIT)

### Cryptography

**liboqs** (MIT) - Kyber-1024 implementation
**libsodium** (ISC) - ChaCha20-Poly1305
**Argon2** (CC0) - Key derivation
**OpenSSL 3.x** (Apache 2.0) - Supporting crypto

### Privacy & Anonymity

**Tor** (BSD-3-Clause)
**Whonix** (GPL-3.0)
**WireGuard** (GPL-2.0)

### Storage

**VeraCrypt** (Apache 2.0)
**dm-crypt/LUKS** (GPL-2.0)

### Tools

**Kali Linux Tools** (Various, mostly GPL)
**Metasploit Framework** (BSD-3-Clause)
**Nmap** (NPSL - Nmap Public Source License)

**QWAMOS License:** GPLv3

---

## Next Immediate Steps

### 1. Extract Ashigaru Components
- Analyze existing codebase from Mega folder
- Identify reusable components
- Map to QWAMOS architecture

### 2. Set Up Development Environment
```bash
# Install cross-compilation toolchain
sudo apt install -y build-essential gcc-aarch64-linux-gnu \
    binutils-aarch64-linux-gnu git bc bison flex libssl-dev \
    libncurses-dev device-tree-compiler python3

# Install Android NDK
wget https://dl.google.com/android/repository/android-ndk-r26-linux.zip
unzip android-ndk-r26-linux.zip
export ANDROID_NDK_HOME=$PWD/android-ndk-r26

# Install QEMU/KVM
sudo apt install -y qemu-system-arm qemu-kvm libvirt-daemon-system

# Install React Native dependencies
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
npm install -g react-native-cli expo-cli
```

### 3. Build Proof-of-Concept
- Compile minimal kernel with Kyber module
- Boot test kernel on device
- Verify KVM functionality
- Launch basic QEMU VM

### 4. Commit to GitHub
```bash
git add .
git commit -m "Initial QWAMOS architecture and project structure

- Complete technical architecture document
- Project directory structure for base OS
- Bootloader, kernel, hypervisor, crypto, UI components
- Documentation and build system setup"

git push -u origin master
```

---

**Status:** Architecture Complete - Ready for Implementation
**Next Milestone:** Extract Ashigaru components and set up development environment
**ETA to Alpha:** 2 months (with full-time development)
**ETA to Production:** 12 months

---

**Document Metadata:**
- **Created:** 2025-10-30
- **Author:** QWAMOS Development Team (Dezirae Stark)
- **Version:** 2.0.0-alpha
- **Classification:** INTERNAL (Technical Architecture)
- **Repository:** https://github.com/Dezirae-Stark/QWAMOS
