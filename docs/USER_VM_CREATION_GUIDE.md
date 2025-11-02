# QWAMOS User-Driven VM Creation Guide

**Date:** 2025-11-01
**Version:** 2.0 (User-Centric Approach)
**Status:** Implementation Complete

---

## Overview

QWAMOS 2.0 introduces **user-driven VM creation** - users can create, customize, and destroy VMs on-demand without pre-installing operating systems. This approach is inspired by Kali NetHunter and leverages proot-distro for fast, lightweight VM deployment.

### Key Benefits ✅

1. **No Pre-Installation** - VMs created when user needs them
2. **Fast Deployment** - 5-10 minutes from selection to ready VM
3. **Flexible** - Persistent or disposable VMs
4. **Efficient** - Uses proot-distro (200-500MB vs 2-4GB ISOs)
5. **Kali NetHunter Integration** - Full Kali tools available
6. **User Control** - Create, configure, destroy at will

---

## VM Templates

### 1. Debian 12 (Whonix Gateway)
**Purpose:** Tor gateway for anonymous networking

**Specifications:**
- RAM: 1GB
- Disk: 8GB
- Packages: tor, iptables, python3
- Network: Isolated bridge (Tor-routed)

**Features:**
- Complete Tor configuration
- DEFAULT DROP firewall
- Stream isolation
- DNS over Tor

**Use Case:** Route kali-vm, disposable-vm through Tor

---

### 2. Kali Linux (Penetration Testing)
**Purpose:** Full Kali NetHunter tools for security testing

**Specifications:**
- RAM: 2GB
- Disk: 16GB
- Packages: nmap, sqlmap, metasploit, burpsuite
- Network: Tor-routed through Whonix

**Features:**
- Full Kali Linux toolset
- NetHunter compatibility
- Kali GPT integration (AI pentesting assistant)
- Tor routing for anonymity

**Use Case:** Security testing, penetration testing, vulnerability assessment

---

### 3. Debian 12 (Minimal)
**Purpose:** Lightweight Debian for general tasks

**Specifications:**
- RAM: 512MB
- Disk: 4GB
- Packages: python3, git, vim
- Network: User-configurable

**Features:**
- Minimal footprint
- Fast boot time
- Ideal for development

**Use Case:** Quick tasks, testing, development

---

### 4. Ubuntu 22.04 (Desktop)
**Purpose:** Full Ubuntu environment

**Specifications:**
- RAM: 2GB
- Disk: 16GB
- Packages: build-essential, python3, nodejs
- Network: User-configurable

**Features:**
- Complete desktop environment
- Development tools
- Package ecosystem

**Use Case:** General computing, development work

---

### 5. Alpine (Crypto Vault)
**Purpose:** Airgapped cryptocurrency wallet

**Specifications:**
- RAM: 256MB
- Disk: 2GB
- Packages: python3, gnupg
- Network: **NONE (airgapped)**

**Features:**
- No network access
- Minimal attack surface
- Ashigaru wallet integration
- Offline transaction signing

**Use Case:** Secure cryptocurrency storage, offline signing

---

### 6. Custom VM
**Purpose:** User-configured VM

**Specifications:**
- User-defined
- Flexible configuration
- Manual setup

**Use Case:** Specialized requirements

---

## User Workflow

### Creating a VM

```bash
# List available templates
python3 ~/QWAMOS/hypervisor/scripts/vm_creator.py list

# Create Whonix Gateway (persistent, encrypted)
python3 ~/QWAMOS/hypervisor/scripts/vm_creator.py create debian-whonix my-gateway

# Create Kali VM (persistent, encrypted)
python3 ~/QWAMOS/hypervisor/scripts/vm_creator.py create kali-pentest my-kali

# Create disposable Debian VM (temporary, no encryption)
python3 ~/QWAMOS/hypervisor/scripts/vm_creator.py create debian-minimal temp-work --disposable

# Create unencrypted VM (not recommended)
python3 ~/QWAMOS/hypervisor/scripts/vm_creator.py create ubuntu-workspace my-ubuntu --no-encrypt
```

### VM Creation Process

**What Happens When You Create a VM:**

1. **Download Rootfs (2-5 minutes)**
   ```
   [*] Installing debian from proot-distro...
   [*] Downloading rootfs (200-500 MB)...
   [+] debian rootfs downloaded
   [*] Copying rootfs to VM directory...
   [+] Rootfs copied to VM directory
   ```

2. **Create Disk Image (30 seconds)**
   ```
   [*] Creating 8G disk image: /path/to/disk.qcow2
   [+] Disk image created
   [*] Encrypting disk with ChaCha20-Poly1305...
   [+] Disk encrypted
   ```

3. **Install Packages (1-3 minutes)**
   ```
   [*] Installing packages: tor, iptables, python3
   [+] Package installation script created
   [*] Packages will be installed on first boot
   ```

4. **Apply Configuration (1 minute)**
   ```
   [*] Configuring Whonix Gateway...
   [+] Tor configuration copied
   [+] Firewall script copied
   [+] VM config created
   ```

5. **VM Ready!**
   ```
   ============================================================
     VM Created Successfully: my-gateway
   ============================================================

   VM Path: /path/to/my-gateway
   Config: /path/to/my-gateway/config.yaml

   To start this VM:
     python3 ~/QWAMOS/hypervisor/scripts/vm_manager.py start my-gateway
   ```

### Starting a VM

```bash
# Start VM
python3 ~/QWAMOS/hypervisor/scripts/vm_manager.py start my-gateway

# Stop VM
python3 ~/QWAMOS/hypervisor/scripts/vm_manager.py stop my-gateway

# Restart VM
python3 ~/QWAMOS/hypervisor/scripts/vm_manager.py restart my-gateway

# VM status
python3 ~/QWAMOS/hypervisor/scripts/vm_manager.py status my-gateway
```

### Destroying a VM

```bash
# Destroy VM (with confirmation)
python3 ~/QWAMOS/hypervisor/scripts/vm_creator.py destroy my-gateway

# Output:
# [!] WARNING: This will permanently delete VM 'my-gateway'
# Type 'yes' to confirm: yes
# [*] Destroying VM: my-gateway
# [*] Securely wiping disk...
# [+] Disk wiped and deleted
# [+] VM 'my-gateway' destroyed successfully
```

**Security Note:** Disk is securely wiped with random data before deletion to prevent data recovery.

---

## Persistent vs Disposable VMs

### Persistent VMs

**Characteristics:**
- Data saved to encrypted QCOW2 disk
- Survives reboots
- User data, settings, installed packages preserved
- Can be backed up
- Encrypted by default (ChaCha20-Poly1305)

**When to Use:**
- Long-term workspaces
- Development environments
- VMs that need to retain state
- Whonix Gateway, Kali VM, Vault VM

**Example:**
```bash
python3 vm_creator.py create kali-pentest my-kali
# Creates persistent, encrypted Kali VM
```

### Disposable VMs

**Characteristics:**
- No persistent disk
- Runs entirely in RAM
- Destroyed on shutdown
- No traces left
- Perfect for sensitive work

**When to Use:**
- Sensitive browsing
- One-time tasks
- Testing untrusted software
- Temporary workspaces

**Example:**
```bash
python3 vm_creator.py create debian-minimal temp-work --disposable
# Creates temporary VM, deleted on shutdown
```

---

## Network Configuration

### Tor-Routed VMs

**VMs that route through Whonix Gateway:**
- kali-vm
- disposable-vm
- Any VM on qwamos-br0 bridge

**Configuration:**
```yaml
network:
  mode: bridge
  bridge: qwamos-br0  # Isolated, Tor-routed
  gateway: 10.152.152.10  # Whonix Gateway
```

**Benefits:**
- All traffic goes through Tor
- No clearnet leaks
- Stream isolation
- Anonymous by default

### Direct Internet (NAT)

**VMs with direct internet:**
- android-vm only

**Configuration:**
```yaml
network:
  mode: bridge
  bridge: qwamos-nat  # Direct internet via NAT
```

### Airgapped (No Network)

**Completely isolated VMs:**
- vault-vm (crypto wallet)

**Configuration:**
```yaml
network:
  mode: none
security:
  airgapped: true
  no_network: true
```

---

## Storage Encryption

### Default Encryption

**All persistent VMs use ChaCha20-Poly1305 encryption:**

```
Disk Structure:
┌─────────────────────────────────────┐
│  QWAMOS Encrypted Volume Header    │
│  - ChaCha20-Poly1305 cipher         │
│  - scrypt key derivation            │
│  - BLAKE2b integrity                │
└─────────────────────────────────────┘
│  Encrypted VM Data                  │
│  - 4KB block encryption             │
│  - Poly1305 authentication tags     │
└─────────────────────────────────────┘
```

**Security Features:**
- 256-bit encryption keys
- Memory-hard KDF (scrypt)
- Per-block authentication
- No compromised algorithms (NO AES!)

### Disabling Encryption (Not Recommended)

```bash
python3 vm_creator.py create debian-minimal my-vm --no-encrypt
```

**Warning:** Only use for testing. Production VMs should always be encrypted.

---

## Integration with Existing Tools

### proot-distro

**Why proot-distro?**
- ✅ Already available in Termux
- ✅ Optimized for ARM64 Android
- ✅ Small downloads (200-500MB)
- ✅ Fast extraction
- ✅ Maintained by Termux team

**Available Distros:**
- debian (Debian 12 Bookworm)
- ubuntu (Ubuntu 22.04 LTS)
- kali (Kali Linux - NetHunter compatible!)
- alpine (Alpine Linux - minimal)
- arch (Arch Linux ARM)
- fedora (Fedora ARM)

**Usage:**
```bash
# VM creator automatically uses proot-distro
# No manual installation required
```

### Kali NetHunter

**QWAMOS Kali VM is NetHunter-compatible:**

```bash
# Create Kali VM
python3 vm_creator.py create kali-pentest my-kali

# Kali VM includes:
# - All Kali core tools
# - nmap, sqlmap, metasploit
# - Burp Suite
# - NetHunter app compatibility (future)
```

**Advantages over NetHunter chroot:**
- ✅ Better isolation (VM vs chroot)
- ✅ Encrypted storage
- ✅ Tor routing through Whonix
- ✅ Full virtualization
- ✅ Snapshots/backups possible

---

## Example Workflows

### Workflow 1: Anonymous Penetration Testing

```bash
# 1. Create Whonix Gateway
python3 vm_creator.py create debian-whonix my-gateway

# 2. Create Kali VM
python3 vm_creator.py create kali-pentest my-kali

# 3. Start Whonix first
python3 vm_manager.py start my-gateway

# 4. Start Kali (routes through Whonix)
python3 vm_manager.py start my-kali

# 5. All Kali traffic now goes through Tor!
```

### Workflow 2: Disposable Browsing

```bash
# Create temporary VM
python3 vm_creator.py create debian-minimal temp-browser --disposable

# Start VM
python3 vm_manager.py start temp-browser

# Use for sensitive browsing...

# Stop VM - all data destroyed
python3 vm_manager.py stop temp-browser
```

### Workflow 3: Airgapped Crypto Wallet

```bash
# Create vault VM (no network)
python3 vm_creator.py create alpine-vault my-wallet

# Start vault
python3 vm_manager.py start my-wallet

# Install Ashigaru wallet
# Generate keys offline
# Sign transactions offline

# VM has ZERO network access - completely airgapped
```

---

## Advanced Features

### Custom VM Configuration

```bash
# Create custom VM
python3 vm_creator.py create custom my-custom

# Edit config manually
vim ~/QWAMOS/vms/my-custom/config.yaml

# Customize:
# - RAM allocation
# - CPU cores
# - Disk size
# - Network configuration
# - Security policies
```

### VM Snapshots (Future)

```bash
# Take snapshot
python3 vm_manager.py snapshot my-kali backup-1

# Restore snapshot
python3 vm_manager.py restore my-kali backup-1

# List snapshots
python3 vm_manager.py snapshots my-kali
```

### VM Cloning (Future)

```bash
# Clone VM
python3 vm_creator.py clone my-kali my-kali-2

# Useful for:
# - Testing configurations
# - Creating backups
# - Distributing pre-configured VMs
```

---

## Troubleshooting

### VM Creation Fails

**Problem:** proot-distro download fails

**Solution:**
```bash
# Check internet connection
ping -c 3 8.8.8.8

# Install proot-distro manually
proot-distro install debian

# Retry VM creation
```

### VM Won't Start

**Problem:** QEMU fails to start

**Solution:**
```bash
# Check VM config
cat ~/QWAMOS/vms/my-vm/config.yaml

# Check disk exists
ls -lh ~/QWAMOS/vms/my-vm/disk.qcow2

# Check QEMU installation
which qemu-system-aarch64
```

### Slow Performance

**Problem:** VM is slow

**Solutions:**
1. Reduce RAM allocation
2. Use disposable VM (runs in RAM)
3. Disable encryption for testing (not recommended)
4. Close other VMs

---

## Security Considerations

### Encryption

**Always use encryption for persistent VMs:**
- ✅ Protects data at rest
- ✅ Prevents unauthorized access
- ✅ Complies with security requirements

**ChaCha20-Poly1305 vs AES:**
- ✅ ChaCha20 NOT compromised (AES IS compromised per DIA Intel)
- ✅ 2.7x faster on ARM
- ✅ Constant-time (timing attack resistant)

### Network Isolation

**Tor-Routed VMs:**
- All traffic goes through Whonix Gateway
- No clearnet leaks
- Stream isolation prevents correlation

**Airgapped VMs:**
- ZERO network access
- Perfect for crypto wallets
- Offline transaction signing

### Disposable VMs

**Use for:**
- Browsing untrusted sites
- Testing malware
- One-time sensitive tasks
- Avoiding forensic traces

**No data persists after shutdown**

---

## Performance Optimization

### RAM Allocation

**Guidelines:**
- Whonix Gateway: 1GB minimum
- Kali VM: 2GB recommended
- Disposable VM: 512MB-1GB
- Vault VM: 256MB sufficient

**Total:** Don't exceed 70% of host RAM

### Disk Size

**Recommendations:**
- Whonix: 8GB
- Kali: 16GB (tools require space)
- Minimal: 4GB
- Vault: 2GB

### CPU Allocation

**Default:** 2 vCPUs per VM

**Adjust for:**
- High-CPU tasks: 4 vCPUs
- Minimal VMs: 1 vCPU

---

## Future Enhancements

### Planned Features

1. **React Native UI**
   - Graphical VM creation wizard
   - One-click VM deployment
   - Visual resource monitoring

2. **VM Marketplace**
   - Pre-configured VMs
   - Community-contributed templates
   - One-click installation

3. **Automatic Updates**
   - OS updates in VMs
   - Security patches
   - Tool updates

4. **Backup/Restore**
   - Cloud backup integration
   - Encrypted backups
   - Easy restoration

---

## Summary

QWAMOS 2.0's user-driven VM creation approach provides:

✅ **Fast Deployment** - VMs ready in 5-10 minutes
✅ **Flexibility** - Persistent or disposable
✅ **Security** - ChaCha20-Poly1305 encryption, Tor routing
✅ **Efficiency** - Small downloads, minimal storage
✅ **User Control** - Create, configure, destroy at will
✅ **NetHunter Compatible** - Full Kali tools

**No pre-installation required. Users create VMs when they need them.**

---

**Document Version:** 2.0
**Last Updated:** 2025-11-01
**Author:** Dezirae-Stark / Claude Code
