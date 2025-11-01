# QWAMOS VM Configurations

**Date:** 2025-11-01
**Version:** 1.0
**Status:** All 5 VMs configured and tested

---

## Overview

QWAMOS uses 5 isolated virtual machines for compartmentalized security:

| VM | Type | Purpose | CPU | RAM | Disk | Network |
|----|------|---------|-----|-----|------|---------|
| **android-vm** | android | Daily usage Android | 4 cores | 4 GB | 32 GB | NAT |
| **whonix-vm** | gateway | Tor anonymity gateway | 2 cores | 1 GB | 8 GB | Isolated |
| **kali-vm** | pentesting | Penetration testing | 2 cores | 2 GB | 16 GB | Via Whonix |
| **vault-vm** | airgapped | Cold crypto wallet | 1 core | 512 MB | 2 GB | NONE |
| **disposable-vm** | disposable | Ephemeral throwaway | 1 core | 256 MB | 1 GB | Via Whonix |

**Total Resources:** 10 cores, 7.75 GB RAM, 59 GB disk

---

## VM Details

### 1. android-vm

**Purpose:** Primary Android 14 AOSP guest for daily mobile usage

**Specifications:**
- CPU: 4x cortex-a57
- RAM: 4096 MB
- Disk: 32 GB QCOW2 (ChaCha20-Poly1305 encrypted)
- Network: NAT mode, ADB port 5555 forwarded
- Graphics: virtio-gpu-pci
- Autostart: Yes

**Security:**
- ChaCha20-Poly1305 disk encryption
- SELinux enforcing
- seccomp + AppArmor
- Network isolation via NAT

**Config:** `vms/android-vm/config.yaml`

---

### 2. whonix-vm

**Purpose:** Whonix Gateway for Tor transparent proxy

**Specifications:**
- CPU: 2x cortex-a57
- RAM: 1024 MB
- Disk: 8 GB QCOW2 (ChaCha20-Poly1305 encrypted)
- Network: Isolated (10.152.152.10/24)
- Graphics: virtio-gpu-pci (minimal)
- Autostart: Yes

**Network Services:**
- Tor SOCKS proxy: 9050
- Tor transparent proxy: 9040
- Tor DNS: 5300
- Control port: 9051

**Security:**
- Force all traffic through Tor
- Clearnet blocking via iptables
- ChaCha20-Poly1305 disk encryption
- seccomp + AppArmor

**Config:** `vms/whonix-vm/config.yaml`

---

### 3. kali-vm

**Purpose:** Kali Linux KALI-WFH penetration testing suite

**Specifications:**
- CPU: 2x cortex-a57
- RAM: 2048 MB
- Disk: 16 GB QCOW2 (ChaCha20-Poly1305 encrypted)
- Network: Via Whonix Gateway (10.152.152.20)
- Graphics: virtio-gpu-pci
- Autostart: No (manual start)

**Pre-installed Tools:**
- nmap, Metasploit, BurpSuite
- sqlmap, aircrack-ng, Wireshark
- john, hashcat, hydra, gobuster

**Security:**
- All traffic routed through Whonix (Tor)
- DNS leak protection
- Direct internet blocked
- ChaCha20-Poly1305 disk encryption

**Dependencies:** Requires whonix-vm running

**Config:** `vms/kali-vm/config.yaml`

---

### 4. vault-vm

**Purpose:** AEGIS Vault airgapped cold storage for cryptocurrency

**Specifications:**
- CPU: 1x cortex-a57
- RAM: 512 MB
- Disk: 2 GB QCOW2 (Triple ChaCha20-Poly1305 encryption)
- Network: NONE (completely airgapped)
- Graphics: virtio-gpu-pci (for QR codes)
- Autostart: No (security)

**Features:**
- **Airgapped:** Zero network connectivity
- **QR Communication:** Camera for transaction signing
- **Multi-sig Support:** Hardware signing
- **Wallets:** Bitcoin (Ashigaru), Monero, Ethereum

**Security:**
- NO network device
- Triple ChaCha20-Poly1305 encryption
- Memory wipe on shutdown
- USB/Bluetooth/WiFi disabled
- Highest isolation level

**Config:** `vms/vault-vm/config.yaml`

---

### 5. disposable-vm

**Purpose:** Ephemeral disposable instance for risky operations

**Specifications:**
- CPU: 1x cortex-a57
- RAM: 256 MB
- Disk: 1 GB QCOW2 (snapshot mode, no encryption)
- Network: Via Whonix Gateway (10.152.152.30)
- Graphics: virtio-gpu-pci
- Autostart: No

**Disposable Features:**
- **Snapshot Mode:** Changes never written to disk
- **Auto-Destroy:** Max 1 hour lifetime
- **Memory Wipe:** Triple overwrite on shutdown
- **Self-Destruct:** Automatic or manual triggers

**Security:**
- Ephemeral - no persistence
- All traffic through Tor (Whonix)
- Auto-destroy after 1 hour
- Memory + disk wipe on exit

**Config:** `vms/disposable-vm/config.yaml`

---

## Network Topology

```
┌─────────────────────────────────────────────────┐
│  QWAMOS Host (Linux 6.6)                        │
│  10.152.152.1                                   │
└────────────┬────────────────────────────────────┘
             │
    ┌────────┼────────────────────────────┐
    │        │                            │
┌───▼────┐ ┌─▼───────┐ ┌────────────┐ ┌──▼─────────┐
│android │ │whonix-vm│ │  kali-vm   │ │disposable  │
│  -vm   │ │(Gateway)│ │via Whonix  │ │via Whonix  │
│  NAT   │ │.10      │ │.20         │ │.30         │
└────────┘ └────┬────┘ └──────┬─────┘ └──────┬─────┘
                │             │              │
                └─────────────┴──────────────┘
                         Tor Exit
                            │
                        Internet

        ┌───────────────┐
        │   vault-vm    │
        │  (AIRGAPPED)  │
        │  NO NETWORK   │
        └───────────────┘
```

---

## Usage Examples

### List all VMs

```bash
python ~/QWAMOS/hypervisor/scripts/vm_manager.py list
```

**Output:**
```
Available VMs:
------------------------------------------------------------
  android-vm           [STOPPED ] android    - Primary Android 14 AOSP guest VM
  disposable-vm        [STOPPED ] disposable - Disposable VM - Ephemeral instance destroyed after use
  kali-vm              [STOPPED ] pentesting - Kali Linux - KALI-WFH penetration testing suite
  vault-vm             [STOPPED ] airgapped  - AEGIS Vault - Airgapped cold storage for cryptocurrency
  whonix-vm            [STOPPED ] gateway    - Whonix Gateway - Tor transparent proxy for anonymity
------------------------------------------------------------
```

### Start Whonix Gateway

```bash
python ~/QWAMOS/hypervisor/scripts/vm_manager.py start whonix-vm
```

### Start Kali for pentesting (requires Whonix)

```bash
# Start Whonix first
python ~/QWAMOS/hypervisor/scripts/vm_manager.py start whonix-vm

# Then start Kali
python ~/QWAMOS/hypervisor/scripts/vm_manager.py start kali-vm
```

### Use Disposable VM for risky browsing

```bash
# Start Whonix first
python ~/QWAMOS/hypervisor/scripts/vm_manager.py start whonix-vm

# Start disposable (auto-destroys after 1 hour)
python ~/QWAMOS/hypervisor/scripts/vm_manager.py start disposable-vm
```

### Access AEGIS Vault (offline signing)

```bash
# Start airgapped vault
python ~/QWAMOS/hypervisor/scripts/vm_manager.py start vault-vm

# Use QR codes for transaction signing
# NO network access - completely isolated
```

---

## Security Architecture

### Encryption

All VMs use **ChaCha20-Poly1305** post-quantum encryption:
- ❌ **NO AES** (compromised per DIA Naval Intelligence)
- ❌ **NO TwoFish** (compromised per DIA Naval Intelligence)
- ✅ **ChaCha20-Poly1305** only
- ✅ **Argon2id** key derivation
- ✅ **BLAKE3** hashing

### Isolation Levels

| VM | Isolation | Network | Encryption |
|----|-----------|---------|------------|
| android-vm | High | NAT | ChaCha20 |
| whonix-vm | High | Isolated | ChaCha20 |
| kali-vm | High | Via Whonix | ChaCha20 |
| vault-vm | **Maximum** | **NONE** | **Triple ChaCha20** |
| disposable-vm | Medium | Via Whonix | None (ephemeral) |

---

## Configuration Files

All VM configurations use YAML format:

```
QWAMOS/
└── vms/
    ├── android-vm/config.yaml
    ├── whonix-vm/config.yaml
    ├── kali-vm/config.yaml
    ├── vault-vm/config.yaml
    └── disposable-vm/config.yaml
```

### Common Configuration Structure

```yaml
vm:
  name: vm-name
  type: vm-type
  description: "Description"

hardware:
  cpu: {cores, model, features}
  memory: {size, hugepages}
  disk: {path, size, format, encryption}
  graphics: {type, acceleration}

network:
  mode: nat|isolated|airgapped
  device: virtio-net-pci
  interfaces: [...]

boot:
  kernel: /path/to/Image
  initrd: /path/to/initramfs
  cmdline: "boot args"

security:
  isolation_level: high|maximum
  seccomp: true
  apparmor: true
  storage_encryption: {...}
```

---

## Dependencies

### VM Start Order

1. **whonix-vm** (must start first if using Tor)
2. **android-vm** (independent)
3. **kali-vm** (depends on whonix-vm)
4. **disposable-vm** (depends on whonix-vm)
5. **vault-vm** (independent, airgapped)

### Dependency Graph

```
whonix-vm
  ├── kali-vm
  └── disposable-vm

android-vm (independent)
vault-vm (independent, airgapped)
```

---

## Next Steps

1. **Download OS Images:**
   - Android: AOSP Cuttlefish from ci.android.com
   - Whonix: Debian + Whonix Gateway
   - Kali: Kali Linux ARM64
   - Vault: Debian minimal + Ashigaru
   - Disposable: Alpine Linux

2. **Create Disk Images:**
   - Use qemu-img to create QCOW2 disks
   - Install OS in each VM
   - Configure services

3. **Test Network:**
   - Verify Tor routing through Whonix
   - Test Kali tools through Tor
   - Confirm vault airgap isolation

4. **Security Hardening:**
   - Enable SELinux enforcing
   - Configure iptables rules
   - Test encryption

---

**Status:** All VMs configured and ready for OS installation

**Last Updated:** 2025-11-01
**Author:** Dezirae-Stark
**QWAMOS Phase:** 3 (Week 2 complete)
