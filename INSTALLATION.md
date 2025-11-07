# QWAMOS Installation Guide

**Version:** v1.0.0-qbamos-gold
**Last Updated:** 2025-11-07

---

## Overview

QWAMOS offers **THREE installation methods** to suit different use cases and technical expertise levels. Choose the method that best fits your needs:

| Method | Difficulty | Requirements | Reversible | Best For |
|--------|------------|--------------|------------|----------|
| **1. Magisk Module** | Easy | Rooted device, Magisk | ✅ Yes | Testing, coexistence with Android |
| **2. TWRP Flashable ZIP** | Medium | Unlocked bootloader, TWRP | ⚠️ With backup | Full install, easier than fastboot |
| **3. Fastboot Flash** | Hard | Unlocked bootloader, fastboot tools | ⚠️ With backup | Advanced users, full control |

---

## Method 1: Magisk Module (Recommended for Testing)

### ✅ Advantages
- Easiest installation (via Magisk Manager)
- Preserves existing Android system
- Easily reversible (uninstall via Magisk)
- Coexists with other Magisk modules
- No data wipe required

### ❌ Limitations
- Less isolation than full install
- Shares Android kernel (reduced security)
- Some features limited by Android restrictions

### Prerequisites
- Rooted Android device with Magisk installed
- Android 10+ (API 29+)
- ARM64 architecture
- 2GB free space on /data

### Installation Steps

1. **Download Module**
   ```bash
   # Download QWAMOS_Magisk_v1.0.0.zip from GitHub Releases
   # https://github.com/Dezirae-Stark/QWAMOS/releases
   ```

2. **Verify Checksum** (Recommended)
   ```bash
   sha256sum QWAMOS_Magisk_v1.0.0.zip
   # Compare with SHA256SUMS.txt
   ```

3. **Install via Magisk Manager**
   - Open Magisk Manager app
   - Tap "Modules" tab
   - Tap "+" button (Install from storage)
   - Select `QWAMOS_Magisk_v1.0.0.zip`
   - Wait for installation
   - Reboot device

4. **Post-Installation Setup**
   ```bash
   # Install Termux (F-Droid version)
   # https://f-droid.org/en/packages/com.termux/

   # In Termux:
   pkg install python clang make git tor
   cd /data/qwamos
   python3 setup/first_boot_setup.py
   ```

**Full instructions:** `release-packages/magisk-module/README.txt`

---

## Method 2: TWRP Flashable ZIP (Recommended for Full Install)

### ✅ Advantages
- Full QWAMOS installation (replaces Android)
- Easier than fastboot method
- Standard TWRP procedure (familiar to many)
- Automatic backup creation

### ❌ Limitations
- Requires TWRP recovery installed
- Wipes all data (full backup required)
- Irreversible without backup

### Prerequisites
- Unlocked bootloader
- TWRP recovery installed
- Full device backup (REQUIRED!)
- 5GB free space on /data
- Android 10+ recommended

### Installation Steps

1. **Create Full Backup** (CRITICAL!)
   ```bash
   # In TWRP:
   # - Select "Backup"
   # - Check: Boot, System, Data
   # - Swipe to backup
   # - Wait 10-20 minutes
   ```

2. **Download and Verify**
   ```bash
   # Download QWAMOS_v1.0.0_flashable.zip
   # Verify SHA256:
   sha256sum QWAMOS_v1.0.0_flashable.zip
   ```

3. **Copy to Device**
   ```bash
   adb push QWAMOS_v1.0.0_flashable.zip /sdcard/
   ```

4. **Boot into TWRP**
   ```bash
   # Method 1: From Android
   adb reboot recovery

   # Method 2: Hardware buttons
   # Power off, then hold Power + Volume Down
   ```

5. **Flash QWAMOS**
   - In TWRP, select "Install"
   - Navigate to `QWAMOS_v1.0.0_flashable.zip`
   - Swipe to confirm flash
   - Wait 5-10 minutes
   - Do NOT reboot yet

6. **Wipe Cache/Dalvik** (Optional but recommended)
   - Select "Wipe"
   - Select "Advanced Wipe"
   - Check: Cache, Dalvik/ART Cache
   - Swipe to wipe

7. **Reboot**
   - Select "Reboot System"
   - First boot takes 3-5 minutes

8. **Post-Installation**
   ```bash
   # Install Termux (F-Droid)
   # Complete first-boot setup
   cd /data/qwamos
   python3 setup/first_boot_setup.py
   ```

**Full instructions:** `release-packages/twrp-flashable/README.txt`

---

## Method 3: Fastboot Flash (Advanced Users)

### ✅ Advantages
- Full control over partitions
- Most flexible method
- Doesn't require TWRP
- Can flash individual partitions

### ❌ Limitations
- Most complex method
- Requires fastboot tools installed
- Wipes all data
- Easy to brick if done incorrectly

### Prerequisites
- Unlocked bootloader (REQUIRED!)
- Android SDK Platform Tools installed
- USB drivers (Windows only)
- Full device backup
- 3GB free space for images

### Installation Steps

1. **Unlock Bootloader** (If not already unlocked)
   ```bash
   # Enable Developer Options
   # Settings → About Phone → Tap Build Number 7x

   # Enable OEM Unlocking & USB Debugging
   # Settings → Developer Options

   # Reboot to bootloader
   adb reboot bootloader

   # Unlock (WIPES ALL DATA!)
   fastboot flashing unlock

   # Confirm on device
   ```

2. **Build Fastboot Images**
   ```bash
   cd release-packages/fastboot-flash
   ./build_fastboot_images.sh

   # This creates:
   # - boot.img
   # - system.img
   # - vendor.img
   # - vbmeta.img
   ```

3. **Flash QWAMOS**
   ```bash
   # Automatic (recommended):
   ./flash-all.sh

   # Manual (advanced):
   fastboot flash boot_a boot.img
   fastboot flash boot_b boot.img
   fastboot flash system_a system.img
   fastboot flash system_b system.img
   fastboot flash vendor_a vendor.img
   fastboot flash vendor_b vendor.img
   fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img
   fastboot -w  # Wipe userdata
   fastboot set_active a
   fastboot reboot
   ```

4. **Post-Installation**
   ```bash
   # Wait for first boot (3-5 minutes)
   # Install Termux
   # Complete setup
   cd /data/qwamos
   python3 setup/first_boot_setup.py
   ```

**Full instructions:** `release-packages/fastboot-flash/README.txt`

---

## Post-Installation Configuration

After installation with any method, complete these steps:

### 1. Generate Post-Quantum Keys

```bash
cd /data/qwamos/crypto/pq
python3 pq_volume.py --generate-keys

# Backup private key (CRITICAL!)
cp /data/qwamos/keys/kyber_private.key /sdcard/qwamos_backup/
```

### 2. Create Encrypted Volume

```bash
python3 pq_volume.py create \
  --size 10G \
  --output /data/qwamos/volumes/workstation.vol \
  --password "your_strong_password"
```

### 3. Configure Network Routing

```bash
cd /data/qwamos/network
python3 network_manager.py --configure

# Choose mode:
# 1. direct - No anonymization (fastest)
# 2. tor-only - Standard Tor
# 3. tor-dnscrypt - Tor + encrypted DNS (recommended)
# 4. tor-i2p-parallel - Clearnet + I2P
# 5. i2p-only - I2P network only
# 6. maximum-anonymity - Tor → I2P chain (slowest)
```

### 4. Configure Panic Gesture

```bash
cd /data/qwamos/system/panic
nano panic_gesture.json

# Configure:
# - Gesture (Power + VolUp + Fingerprint)
# - Actions (wipe keys, kill radio, lock bootloader)
# - Timeout (2 seconds)

# Test (dry run):
python3 test_panic_gesture.py --dry-run
```

### 5. Start Services

```bash
# Start Dom0 policy manager
python3 /data/qwamos/dom0/qwamosd/qwamosd.py &

# Start network manager
python3 /data/qwamos/network/network_manager.py --daemon &

# Start ML threat detection (optional)
python3 /data/qwamos/ml/threat_detection_daemon.py &

# Start VMs (if KVM available)
cd /data/qwamos/hypervisor/scripts
./start_vm.sh gateway-1
./start_vm.sh workstation-1
```

---

## Verification

### Check QWAMOS Installation

```bash
# Check version
cat /data/qwamos/version

# Check Dom0 status
ps aux | grep qwamosd

# Check KVM (if available)
lsmod | grep kvm

# Check network routing
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip

# Check ML threat detection
tail -f /data/qwamos/logs/threat_detection.log
```

### Verify Cryptographic Signatures

```bash
# Verify package signature
gpg --verify QWAMOS_v1.0.0_flashable.zip.asc QWAMOS_v1.0.0_flashable.zip

# Expected fingerprint:
# 18C4E89E37D5ECD392F52E85269CD0658D8BD942DCF33BE4E37CC94933E4C4D2
```

---

## Rollback / Recovery

### Magisk Module Uninstall

```bash
# Via Magisk Manager:
# Modules → Trash icon → Reboot

# Via command line:
su
rm -rf /data/adb/modules/qwamos
reboot
```

### TWRP Recovery

```bash
# Boot to TWRP
# Select "Restore"
# Select your backup
# Swipe to restore
# Reboot
```

### Fastboot Recovery

```bash
# Boot to fastboot mode
adb reboot bootloader

# Flash boot backup
fastboot flash boot_a qwamos_boot_backup.img

# Factory reset
fastboot -w

# Reboot
fastboot reboot
```

---

## Troubleshooting

### Boot Loop

```bash
# TWRP method:
# Boot to TWRP → Restore backup

# Fastboot method:
fastboot flash boot_a qwamos_boot_backup.img
fastboot reboot
```

### Network Not Working

```bash
# Check Tor status
systemctl status qwamos-tor

# Restart network manager
python3 /data/qwamos/network/network_manager.py --restart

# Configure bridges (if Tor blocked)
nano /etc/qwamos/tor/torrc
# Add bridge lines
```

### VMs Won't Start

```bash
# Check KVM
lsmod | grep kvm

# If no KVM, use TCG (user-mode)
nano /data/qwamos/vms/gateway-1/config.json
# Change: "accelerator": "kvm" → "accelerator": "tcg"
```

### Permission Errors

```bash
# Fix SELinux contexts
su
restorecon -R /data/qwamos
restorecon -R /system/qwamos
```

**See SUPPORT.md for detailed troubleshooting**

---

## Comparison Matrix

| Feature | Magisk Module | TWRP ZIP | Fastboot |
|---------|---------------|----------|----------|
| **Ease of Install** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Security Level** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Reversibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Android Coexistence** | ✅ Yes | ❌ No | ❌ No |
| **VM Isolation** | ⚠️ Limited | ✅ Full | ✅ Full |
| **Bootloader Unlock** | ❌ Not required | ✅ Required | ✅ Required |
| **Data Wipe** | ❌ No | ✅ Yes | ✅ Yes |
| **Custom Kernel** | ❌ No | ✅ Yes | ✅ Yes |

---

## Build Packages from Source

If you prefer to build packages yourself:

```bash
cd ~/QWAMOS/release-packages

# Build TWRP flashable ZIP
cd twrp-flashable
./build_twrp_package.sh

# Build fastboot images
cd ../fastboot-flash
./build_fastboot_images.sh

# Build Magisk module
cd ../magisk-module
./build_magisk_module.sh
```

---

## Support

**GitHub Issues:** https://github.com/Dezirae-Stark/QWAMOS/issues
**Email:** clockwork.halo@tutanota.de
**Documentation:**
- OPS_GUIDE.md (Operational procedures)
- SUPPORT.md (Troubleshooting)
- SECURITY.md (Responsible disclosure)

---

## Recommended Installation Path by Use Case

### For Testing / Evaluation
→ **Magisk Module** (easiest, reversible)

### For Daily Use (Security-Conscious)
→ **TWRP Flashable ZIP** (good balance)

### For Maximum Security (Nation-State Threats)
→ **Fastboot Flash** (full control)

### For Development
→ **Magisk Module** or **build from source**

---

**Choose your installation method and follow the corresponding guide above.**

**Always backup your data before installation!**

---

© 2025 First Sterling Capital, LLC · Dezirae Stark
Licensed under AGPL-3.0
