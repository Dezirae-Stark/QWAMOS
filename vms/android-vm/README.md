# QWAMOS Android VM

**Status:** Configuration Complete, Ready for Android System Image

## Overview

The Android VM provides user-facing applications in an isolated environment routed through the Whonix Gateway for maximum privacy. This VM is designed to run Android 14 (AOSP or LineageOS) with full app compatibility.

## Architecture

```
┌────────────────────────────────────────┐
│         Android VM (Workstation)       │
│  • Android 14 AOSP/LineageOS           │
│  • User applications                   │
│  • NO direct network access            │
│  • Routes ALL traffic through Gateway  │
└────────────────────────────────────────┘
          ↓ virtio-net
┌────────────────────────────────────────┐
│       Gateway VM (Whonix/Tor)          │
│  • Tor proxy (9050/9040)               │
│  • Firewall (DEFAULT DROP)             │
│  • Only Tor egress allowed             │
└────────────────────────────────────────┘
          ↓ Physical NIC
      [Internet via Tor]
```

## Current Status

### ✅ Completed
- [x] VM configuration (config.yaml)
- [x] QEMU/KVM virtualization settings
- [x] Virtio drivers configuration
- [x] Network routing through Gateway VM
- [x] Storage encryption setup (ChaCha20-Poly1305)
- [x] Security policies defined
- [x] Boot parameters configured

### ⏳ Pending (Deployment Phase)
- [ ] Android 14 system image (8GB+, requires AOSP build or download)
- [ ] First boot setup
- [ ] App installation and testing

## VM Specifications

### Hardware
- **CPU:** 4 cores (Cortex-A57)
- **RAM:** 4096 MB
- **Disk:** 32GB QCOW2 (encrypted)
- **Graphics:** virtio-gpu-pci (hardware acceleration)
- **Audio:** ALSA backend
- **Network:** virtio-net-pci (NAT mode)

### Security
- **Isolation Level:** High
- **Seccomp:** Enabled
- **AppArmor:** Enabled
- **Storage Encryption:** ChaCha20-Poly1305 + Argon2id
- **Network:** All traffic routed through Gateway VM (mandatory Tor)

### Boot Configuration
- **Kernel:** QWAMOS Linux 6.6 LTS ARM64
- **Initramfs:** Busybox-static minimal init
- **Root Device:** /dev/vda (virtio-blk)
- **Console:** ttyAMA0 (serial)

## Android System Image Options

### Option 1: LineageOS (Recommended for Quick Deployment)
**Size:** ~1.5GB download
**Build Time:** None (prebuilt)
**Source:** https://download.lineageos.org/

```bash
cd ~/QWAMOS/vms/android-vm
wget https://download.lineageos.org/devices/generic/builds/lineage-21.0-arm64-aonly.img
qemu-img convert -f raw -O qcow2 lineage-21.0-arm64-aonly.img disk.qcow2
```

### Option 2: AOSP Build (Full Control)
**Size:** 200GB+ source, 8GB+ image
**Build Time:** 8-12 hours
**Requirements:** Linux desktop with 16GB+ RAM

```bash
# On Linux build machine
repo init -u https://android.googlesource.com/platform/manifest -b android-14.0.0_r1
repo sync -j$(nproc)
source build/envsetup.sh
lunch aosp_arm64-eng
make -j$(nproc)

# Convert system.img to QCOW2
qemu-img convert -f raw -O qcow2 out/target/product/generic_arm64/system.img \
    ~/QWAMOS/vms/android-vm/disk.qcow2
```

### Option 3: Android-x86 (Testing Only)
**Size:** ~900MB
**Build Time:** None
**Note:** x86 architecture, requires recompilation for ARM64

```bash
wget https://osdn.net/projects/android-x86/downloads/android-x86_64-9.0-r2.iso
# Convert ISO to QCOW2
qemu-img convert -f raw -O qcow2 android-x86_64-9.0-r2.iso disk.qcow2
```

## Integration with QWAMOS

### Network Routing
All Android VM network traffic is routed through the Whonix Gateway VM:

```
Android App → virtio-net → Gateway VM → Tor (9050) → Internet
```

No app can bypass Tor. DNS requests go through Tor's DNS resolver (port 5300).

### Firewall Rules
The Gateway VM firewall (configured in Phase 3) enforces:
- DEFAULT DROP on all chains
- Only Tor egress allowed
- No direct internet access
- All DNS via Tor

### Storage Encryption
Android VM disk is encrypted using:
- **Algorithm:** ChaCha20-Poly1305 AEAD
- **Key Derivation:** Argon2id (memory-hard)
- **Key Size:** 256 bits
- **TEE Integration:** Keys wrapped by StrongBox/Keymaster

## Testing Framework

### Validation Script
```bash
bash ~/QWAMOS/vms/android-vm/validate_config.sh
```

Checks:
1. ✅ Configuration file valid (YAML parsing)
2. ✅ Kernel Image exists (32MB ARM64)
3. ✅ Initramfs exists (busybox-static)
4. ✅ Disk image exists (QCOW2 format)
5. ✅ Network configuration valid
6. ✅ Security policies defined

### Boot Test (When Android Image Available)
```bash
bash ~/QWAMOS/vms/android-vm/boot_test.sh
```

Tests:
- Kernel boot
- Virtio drivers load
- Network connectivity via Gateway
- Storage encryption unlock
- ADB connection (port 5555)

## Performance Characteristics

### Expected Performance (Snapdragon 8 Gen 3)
- **Boot Time:** 30-45 seconds
- **App Launch:** 1-3 seconds (native apps)
- **Network Latency:** +50ms (Tor overhead)
- **Storage I/O:** 80-90% of native (ChaCha20 overhead)
- **Graphics:** 60 FPS (virtio-gpu acceleration)

### Memory Footprint
- **Base System:** ~800MB
- **Per App:** 50-200MB
- **Total (4GB RAM):** Comfortable for 10-15 concurrent apps

## App Compatibility

### ✅ Supported
- All AOSP/LineageOS compatible apps
- F-Droid apps (privacy-focused)
- APKs installable via ADB
- Most Play Store apps (if using microG)

### ❌ Not Supported
- Google Play Services (by design, privacy concern)
- Apps requiring SafetyNet attestation
- Apps with anti-VM detection
- DRM-protected content (Widevine L1)

## Deployment Workflow

### 1. Development (Current - Termux)
```bash
# VM configuration complete
# Testing framework ready
# Awaiting Android system image
```

### 2. Build Phase (Linux Desktop)
```bash
# Download LineageOS OR build AOSP
# Convert to QCOW2
# Transfer to device
```

### 3. Integration (Motorola Edge 2025)
```bash
# Copy Android VM to device
# Encrypt disk with volume_manager.py
# Start VM via vm_manager.py
# Configure network routing
# Test app installation
```

### 4. Production (Daily Use)
```bash
# Boot Android VM on device startup
# Apps route through Tor automatically
# Encrypted storage protects data at rest
# Panic gesture wipes session keys
```

## Security Considerations

### Threat Model
The Android VM protects against:
- ✅ Network surveillance (mandatory Tor)
- ✅ App tracking (no Google services)
- ✅ Data exfiltration (firewall blocks clearnet)
- ✅ Physical seizure (encrypted disk)
- ✅ Malware persistence (VM can be rolled back)

### Limitations
- ❌ Does NOT protect against malicious apps WITHIN the VM
- ❌ User must avoid installing untrusted APKs
- ❌ Tor network correlation still possible
- ❌ Apps can capture data before encryption

### Best Practices
1. **Only install apps from trusted sources** (F-Droid, direct APK from developer)
2. **Use Orbot within Android** for defense-in-depth
3. **Regularly snapshot clean VM state** for rollback
4. **Minimize app permissions** (no camera/mic unless needed)
5. **Use disposable VMs** for untrusted apps

## Next Steps

### For Phase 3 Completion (Now)
- [x] Document Android VM architecture
- [x] Create validation framework
- [x] Define integration points
- [x] Specify deployment workflow

### For Phase 4 (System Services)
- [ ] Obtain Android 14 system image
- [ ] Perform first boot test
- [ ] Configure ADB access
- [ ] Install F-Droid + essential apps
- [ ] Test Tor routing
- [ ] Benchmark performance

### For Phase 5 (UI Layer)
- [ ] Create React Native control panel
- [ ] Add VM start/stop buttons
- [ ] Show network status (Tor connected)
- [ ] Display app list
- [ ] Enable app installation UI

## Resources

- **AOSP:** https://source.android.com/
- **LineageOS:** https://lineageos.org/
- **Android-x86:** https://www.android-x86.org/
- **Waydroid:** https://waydro.id/ (alternative: Android container)
- **QEMU ARM64:** https://wiki.qemu.org/Documentation/Platforms/ARM

---

**Status:** Android VM configuration complete and validated. Ready for Android system image integration during Phase 4 deployment.

**Last Updated:** 2025-11-02
