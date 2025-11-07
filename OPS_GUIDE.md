# QWAMOS Operations Guide

**Version:** v1.0.0-qbamos-gold
**Last Updated:** 2025-11-07
**Audience:** System operators, advanced users, security professionals

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation Paths](#installation-paths)
   - [Rooted Install Path](#rooted-install-path)
   - [Non-Rooted Path](#non-rooted-path)
3. [Initial Configuration](#initial-configuration)
4. [Operational Modes](#operational-modes)
5. [Emergency Procedures](#emergency-procedures)
6. [Safe Updates & Rollback](#safe-updates--rollback)
7. [Monitoring & Logging](#monitoring--logging)
8. [Security Hardening](#security-hardening)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

This operations guide provides comprehensive instructions for deploying, configuring, and maintaining QWAMOS in production environments. It covers both rooted and non-rooted installation paths, emergency procedures, and operational best practices.

**Prerequisites:**
- Android device with ARM64 architecture
- Bootloader unlock capability (for rooted path)
- Termux installed (preferably F-Droid version)
- Basic Linux command-line knowledge
- Backup of existing data

---

## Installation Paths

### Rooted Install Path

**Requirements:**
- Unlocked bootloader
- Root access (Magisk recommended)
- USB debugging enabled
- ~20GB free storage

#### Step 1: Unlock Bootloader

**WARNING:** Unlocking the bootloader will WIPE ALL DATA on your device.

```bash
# On your computer (requires Android SDK Platform Tools)
adb reboot bootloader

# Unlock bootloader (varies by manufacturer)
# Pixel devices:
fastboot flashing unlock

# Motorola devices:
fastboot oem unlock <unlock_code>

# Wait for device to boot and complete setup
```

**Verify bootloader status:**
```bash
adb shell getprop ro.boot.flash.locked
# Should return: 0 (unlocked)
```

---

#### Step 2: Install Magisk (Root)

```bash
# Download Magisk APK from GitHub
# https://github.com/topjohnwu/Magisk/releases

# Extract boot.img from device firmware
adb shell su -c "dd if=/dev/block/by-name/boot_a of=/sdcard/boot.img"
adb pull /sdcard/boot.img

# Patch boot.img using Magisk Manager app
# Install > Select and Patch a File > boot.img
# This creates magisk_patched_*.img

# Flash patched boot image
adb push magisk_patched_*.img /sdcard/
adb reboot bootloader
fastboot flash boot /sdcard/magisk_patched_*.img
fastboot reboot

# Verify root access
adb shell su -c "id"
# Should show: uid=0(root)
```

---

#### Step 3: Deploy QWAMOS (Rooted)

```bash
# Clone QWAMOS repository in Termux
pkg install git python clang make
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS

# Checkout gold release
git checkout v1.0.0-qbamos-gold
git verify-tag v1.0.0-qbamos-gold

# Run rooted deployment script
chmod +x security/deploy-to-device.sh
su -c "./security/deploy-to-device.sh rooted"

# This script will:
# - Install kernel modules (KVM, usb_killswitch)
# - Configure systemd services
# - Set up VM disk images
# - Configure firewall rules
# - Enable security features
```

**Expected output:**
```
[✓] Root access verified
[✓] Kernel modules compiled and loaded
[✓] KVM hypervisor enabled
[✓] Dom0 policy manager started
[✓] VM disk images created (gateway-1, workstation-1, kali-1)
[✓] Firewall configured (DEFAULT DROP)
[✓] Tor/I2P/DNSCrypt services started
[✓] ML threat detection enabled
[✓] Hardware kill switch driver loaded

QWAMOS deployment complete!
Reboot required: yes
```

**Reboot:**
```bash
su -c "reboot"
```

---

#### Step 4: Post-Install Verification (Rooted)

```bash
# Verify KVM hypervisor
lsmod | grep kvm
# Should show: kvm kvm_arm_host

# Verify Dom0 is running
systemctl status qwamosd
# Should show: active (running)

# Verify VMs are created
ls -lh /var/lib/qwamos/vms/
# Should show: gateway-1.qcow2, workstation-1.qcow2, kali-1.qcow2

# Verify Tor is running
systemctl status qwamos-tor
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip
# Should return Tor exit node IP

# Verify encryption
cryptsetup status qwamos-volume
# Should show: active, cipher: chacha20
```

---

### Non-Rooted Path

**Requirements:**
- No root access required
- Termux (F-Droid version recommended)
- ~10GB free storage
- Android 10+ (API 29+)

**Limitations:**
- No kernel module support (no KVM acceleration)
- No hardware kill switch driver
- Limited network firewall control
- VMs run in user-mode emulation (slower)

#### Step 1: Install Termux

```bash
# Download Termux from F-Droid (NOT Google Play Store)
# https://f-droid.org/en/packages/com.termux/

# Update packages
pkg update && pkg upgrade

# Install dependencies
pkg install git python clang make qemu-system-aarch64 tor
```

---

#### Step 2: Deploy QWAMOS (Non-Rooted)

```bash
# Clone repository
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS

# Checkout gold release
git checkout v1.0.0-qbamos-gold

# Run non-rooted deployment
chmod +x security/deploy-to-device.sh
./security/deploy-to-device.sh non-rooted

# This script will:
# - Set up user-mode QEMU (no KVM)
# - Configure Tor/I2P/DNSCrypt in userspace
# - Create VM disk images in ~/QWAMOS/vms/
# - Configure iptables via VpnService API
# - Enable security features (limited)
```

**Expected output:**
```
[✓] Termux environment detected
[✓] QEMU user-mode emulation enabled
[✓] VM disk images created
[✓] Tor service started (127.0.0.1:9050)
[✓] I2P service started (127.0.0.1:4444)
[✓] DNSCrypt service started
[✓] ML threat detection enabled (limited)

QWAMOS deployment complete (non-rooted mode)
Note: Some features require root access
```

---

#### Step 3: Manual Configuration (Non-Rooted)

```bash
# Configure Android VPN for traffic routing
# (QWAMOS will prompt for VPN permission)

# Start Dom0 policy manager
python3 security/dom0/qwamosd/qwamosd.py &

# Start gateway VM (Tor routing)
cd hypervisor/scripts
./start_vm.sh gateway-1

# In another Termux session, start workstation VM
./start_vm.sh workstation-1
```

---

## Initial Configuration

### First Boot Setup

After installation, configure QWAMOS security settings:

#### 1. Generate Post-Quantum Keys

```bash
# Generate Kyber-1024 keypair for volume encryption
cd crypto/pq
python3 pq_volume.py --generate-keys

# Output:
# Kyber-1024 keypair generated
# Public key: /var/lib/qwamos/keys/kyber_public.key (1568 bytes)
# Private key: /var/lib/qwamos/keys/kyber_private.key (3168 bytes)

# Backup private key (CRITICAL - cannot recover without this)
cp /var/lib/qwamos/keys/kyber_private.key /sdcard/qwamos_backup/
```

---

#### 2. Create Encrypted Volume

```bash
# Create 10GB encrypted volume
python3 crypto/pq/pq_volume.py create \
  --size 10G \
  --output /var/lib/qwamos/volumes/workstation.vol \
  --password "your_strong_password_here"

# Mount volume
python3 crypto/pq/pq_volume.py mount \
  --volume /var/lib/qwamos/volumes/workstation.vol \
  --mountpoint /mnt/qwamos/workstation

# Verify encryption
file /var/lib/qwamos/volumes/workstation.vol
# Should show: data (encrypted)
```

---

#### 3. Configure Network Routing Mode

```bash
# Edit network configuration
nano network/config/network_mode.json

# Available modes:
# 1. direct (no anonymization - fastest)
# 2. tor-only (standard Tor anonymity)
# 3. tor-dnscrypt (Tor + encrypted DNS - recommended)
# 4. tor-i2p-parallel (access clearnet and I2P)
# 5. i2p-only (I2P network only)
# 6. maximum-anonymity (Tor → I2P chain - slowest)

# Example: Set to tor-dnscrypt (recommended)
{
  "mode": "tor-dnscrypt",
  "tor": {
    "socks_port": 9050,
    "control_port": 9051,
    "bridges": []
  },
  "dnscrypt": {
    "listen": "127.0.0.1:5300",
    "resolvers": ["cloudflare", "quad9"]
  }
}

# Apply configuration
python3 network/network_manager.py --reload
```

---

#### 4. Configure Emergency Panic Gesture

```bash
# Configure panic gesture (Power + VolUp + Fingerprint)
nano system/ui/settings/panic_gesture.json

{
  "enabled": true,
  "gesture": "power_volup_fingerprint",
  "actions": [
    "wipe_session_keys",
    "kill_radio",
    "lock_bootloader",
    "destroy_vms",
    "secure_wipe_memory"
  ],
  "timeout_ms": 2000
}

# Test panic gesture (DRY RUN - does NOT wipe)
python3 system/panic/test_panic_gesture.py --dry-run

# Output:
# [DRY RUN] Panic gesture detected
# [DRY RUN] Wiping session keys... SIMULATED
# [DRY RUN] Killing radio... SIMULATED
# [DRY RUN] Locking bootloader... SIMULATED
# [DRY RUN] Panic complete in 1.8 seconds
```

---

## Operational Modes

### Basic Mode (Default)

**Features:**
- Tor egress routing
- Basic firewall (allows IMS/VoLTE for calls)
- VM isolation enabled
- ML threat detection (monitoring only)

**Configuration:**
```bash
echo "SECURITY_MODE=basic" > /etc/qwamos/mode.conf
systemctl restart qwamosd
```

---

### Strict Mode (Maximum Security)

**Features:**
- Tor-only network (NO cellular, NO WiFi direct)
- Firewall blocks ALL except Tor (no IMS/VoLTE)
- Baseband driver disabled
- ML threat detection (auto-mitigation)
- Hardware kill switches enforced

**Configuration:**
```bash
echo "SECURITY_MODE=strict" > /etc/qwamos/mode.conf
echo "BASEBAND_DRIVER_DISABLE=on" >> /etc/qwamos/mode.conf
echo "IMS_VOLTE_BLOCK=on" >> /etc/qwamos/mode.conf
systemctl restart qwamosd

# Verify strict mode active
python3 security/dom0/qwamosd/qwamosd.py --status
# Should show: STRICT MODE ACTIVE
```

**WARNING:** Strict mode disables cellular calls/SMS. Use only when maximum anonymity is required.

---

### Development Mode (Testing Only)

**Features:**
- Direct network access (no Tor)
- Firewall disabled
- VM snapshot/restore enabled
- Logging verbosity increased

**Configuration:**
```bash
echo "SECURITY_MODE=development" > /etc/qwamos/mode.conf
echo "NETWORK_MODE=direct" >> /etc/qwamos/mode.conf
systemctl restart qwamosd
```

**WARNING:** Development mode should NEVER be used in production. For testing only.

---

## Emergency Procedures

### Panic Gesture (Instant Wipe)

**Trigger:** Press and hold: **Power + Volume Up + Fingerprint Sensor** simultaneously for 2 seconds

**Actions performed (<2 seconds):**
1. Wipe session encryption keys (RAM)
2. Disable all radios (cellular, WiFi, Bluetooth, NFC)
3. Lock bootloader (emergency ML override)
4. Snapshot VM state (for forensics)
5. Secure wipe sensitive memory regions (3-pass DoD)
6. Display decoy lock screen

**Recovery:**
```bash
# After panic, device requires:
# 1. Biometric authentication (fingerprint or face)
# 2. Master password entry
# 3. Boot into safe mode (Dom0 only, no user VMs)

# Verify wipe completed
python3 system/panic/verify_wipe.py

# Output:
# [✓] Session keys wiped from memory
# [✓] Radio interfaces disabled
# [✓] Bootloader locked
# [✓] VMs paused
# [✓] Secure wipe complete
```

---

### Duress Profile (Decoy Mode)

**Purpose:** Provide convincing fake data under coercion

**Setup:**
```bash
# Create duress profile
python3 system/duress/create_profile.py --name "decoy"

# Configure decoy data
# - Fake user account
# - Decoy VMs with fake browsing history
# - Fake encrypted volumes (unlockable with duress password)
# - Fake contacts and messages

# Set duress password (different from real password)
python3 system/duress/set_password.py --profile decoy

# Test duress login
python3 system/duress/test_login.py --password <duress_password>

# Should boot into decoy environment (fake data)
```

**WARNING:** Duress profiles only work for ONE-TIME seizure. If adversary monitors you long-term, they will detect deception.

---

### Manual Emergency Wipe

```bash
# Emergency wipe (if panic gesture fails)
su -c "python3 system/panic/manual_wipe.sh"

# Confirm wipe (type "WIPE" in uppercase)
WIPE

# This will:
# - Wipe all encryption keys
# - Destroy VMs
# - Secure wipe storage volumes
# - Factory reset device

# CANNOT BE UNDONE
```

---

## Safe Updates & Rollback

### Update Procedure

```bash
# 1. Backup current state
./scripts/backup_qwamos.sh

# Creates:
# /sdcard/qwamos_backup/qwamos_backup_20251107.tar.gz
# - Config files
# - Encryption keys (encrypted)
# - VM snapshots
# - User data

# 2. Verify new release signature
cd ~/QWAMOS
git fetch origin
git tag -v v1.0.1-qbamos-gold

# Should show:
# gpg: Good signature from "Dezirae Stark <clockwork.halo@tutanota.de>"

# 3. Checkout new version
git checkout v1.0.1-qbamos-gold

# 4. Apply update
su -c "./scripts/update_qwamos.sh"

# 5. Reboot
su -c "reboot"
```

---

### Rollback Procedure

```bash
# If update fails or causes issues, rollback:

# 1. Boot into recovery (if device won't boot)
# Hold Power + Volume Down during boot

# 2. Restore previous version
cd ~/QWAMOS
git checkout v1.0.0-qbamos-gold

# 3. Restore from backup
./scripts/restore_qwamos.sh /sdcard/qwamos_backup/qwamos_backup_20251107.tar.gz

# 4. Verify restoration
./scripts/verify_installation.sh

# 5. Reboot
su -c "reboot"
```

---

### Automatic Rollback (3 Failed Boots)

QWAMOS includes automatic rollback on failed boot:

```bash
# If device fails to boot 3 times consecutively:
# - Bootloader automatically rolls back to previous version
# - A/B partition switch (Slot A → Slot B)
# - User data preserved

# To disable auto-rollback (advanced users only):
su -c "echo 'DISABLE_AUTO_ROLLBACK=true' > /etc/qwamos/rollback.conf"
```

---

## Monitoring & Logging

### Real-Time Monitoring

```bash
# Monitor Dom0 policy manager
journalctl -u qwamosd -f

# Monitor network traffic
python3 network/scripts/network-monitor.py --live

# Monitor ML threat detection
tail -f /var/log/qwamos/threat_detection.log

# Monitor VM status
watch -n 5 'virsh list --all'
```

---

### Log Locations

```bash
# System logs
/var/log/qwamos/system.log

# Dom0 policy manager
/var/log/qwamos/qwamosd.log

# Network logs
/var/log/qwamos/network.log

# Tor logs
/var/log/qwamos/tor.log

# ML threat detection
/var/log/qwamos/threat_detection.log

# Hardware security (Phase 10)
/var/log/qwamos/ml_override.log
/var/log/qwamos/firmware_integrity.log
/var/log/qwamos/ab_isolation.log
```

---

### Log Rotation

```bash
# Logs are automatically rotated daily
# Configure rotation policy:
nano /etc/qwamos/logrotate.conf

/var/log/qwamos/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 qwamos qwamos
}
```

---

## Security Hardening

### Recommended Hardening Steps

#### 1. Disable USB Debugging (Production)

```bash
# After installation, disable USB debugging
adb shell settings put global adb_enabled 0

# Verify
adb shell settings get global adb_enabled
# Should return: 0
```

---

#### 2. Enable Hardware Kill Switches

```bash
# Configure hardware kill switches (Phase 10)
# Requires USB kill switch module (see PHASE10_USB_KILLSWITCH_SCHEMATIC.md)

# Load kernel driver
su -c "insmod /lib/modules/usb_killswitch.ko"

# Disable camera
echo 1 > /sys/kernel/usb_killswitch/camera_disable

# Disable microphone
echo 1 > /sys/kernel/usb_killswitch/mic_disable

# Disable cellular radio
echo 1 > /sys/kernel/usb_killswitch/cellular_disable

# Verify status
cat /sys/kernel/usb_killswitch/status
# Should show:
# camera: disabled (hardware)
# mic: disabled (hardware)
# cellular: disabled (hardware)
```

---

#### 3. Configure Firmware Integrity Monitoring

```bash
# Enable firmware integrity monitoring (Phase 10)
python3 security/firmware_integrity_monitor.py --enable

# Configure expected bootloader hash
BOOTLOADER_HASH=$(sha256sum /dev/block/by-name/boot_a | cut -d' ' -f1)
echo "EXPECTED_BOOTLOADER_HASH=$BOOTLOADER_HASH" > /etc/qwamos/firmware_integrity.conf

# Monitor will alert if hash changes (bootloader tampering)
```

---

#### 4. Lock Bootloader (Production)

```bash
# After QWAMOS is fully configured and tested, re-lock bootloader
# WARNING: This is irreversible without wiping data

# Enable ML bootloader override (Phase 10)
python3 security/ml_bootloader_override.py --enable

# Lock bootloader
adb reboot bootloader
fastboot flashing lock

# Verify locked
fastboot oem device-info
# Should show: Device unlocked: false
```

---

## Troubleshooting

See [SUPPORT.md](SUPPORT.md) for detailed troubleshooting procedures.

**Common issues:**
- VMs won't start → Check KVM module loaded
- Tor not connecting → Check bridges configuration
- Panic gesture not working → Verify permissions in Settings
- ML threat detection false positives → Tune thresholds in config

---

## Additional Resources

- **SECURITY.md:** Responsible disclosure policy
- **SUPPLYCHAIN.md:** Dependency verification
- **SUPPORT.md:** Troubleshooting guide
- **README.md:** Project overview and architecture

---

**Questions or issues? Email:** clockwork.halo@tutanota.de

---

© 2025 First Sterling Capital, LLC · QWAMOS Project
Licensed under AGPL-3.0
