# QWAMOS Android VM Setup Guide

**Date:** 2025-11-01
**Version:** 1.0
**Target:** Android 14 ARM64 on QEMU

---

## Executive Summary

This guide documents the research and setup process for running Android 14 as a guest VM in QWAMOS using QEMU ARM64 virtualization.

**Key Finding:** AOSP Cuttlefish images are the best option for QEMU ARM64 Android VMs.

---

## Research Findings

### Android Image Options for QEMU

After extensive research, three main options were identified:

| Option | Description | Viability | Recommended |
|--------|-------------|-----------|-------------|
| **Generic System Image (GSI)** | AOSP images for Treble-compliant devices | Low - requires Treble support | ❌ No |
| **Android SDK Emulator Images** | Official emulator system images | Medium - designed for Google's emulator | ⚠️ Partial |
| **AOSP Cuttlefish** | Purpose-built virtual hardware platform | **HIGH** - designed for QEMU/KVM | ✅ **YES** |

### Why Cuttlefish?

**Cuttlefish** is Google's official virtual Android device platform designed specifically for QEMU/KVM virtualization:

✅ **Pros:**
- Pre-configured for QEMU ARM64
- Includes boot images (kernel + ramdisk)
- System images optimized for virtualization
- virtio drivers built-in
- ADB over network support
- Regular updates from AOSP CI
- No GMS/Play Services (pure AOSP - aligns with QWAMOS security goals)

❌ **Cons:**
- Large downloads (~2-3 GB per build)
- Requires specific Cuttlefish tools (cvd-host-package)
- Documentation assumes Linux desktop environment

---

## Download Sources

### AOSP Continuous Integration (Recommended)

**URL:** https://ci.android.com/builds/branches/aosp-main-throttled/grid?legacy=1

**Build to Download:**
- Branch: `aosp-main-throttled` (or `aosp-main` for latest)
- Target: `aosp_cf_arm64_only_phone-trunk_staging-userdebug`
- Files needed:
  - `aosp_cf_arm64_phone-img-*.zip` (~2GB) - System images
  - `cvd-host_package.tar.gz` (~500MB) - Cuttlefish host tools

**Latest Stable Build (as of 2025-11-01):**
- Build: https://ci.android.com/builds/submitted/{BUILD_ID}/aosp_cf_arm64_only_phone-trunk_staging-userdebug/latest

### Alternative: GSI Images (Not Recommended for QWAMOS)

**URL:** https://developer.android.com/topic/generic-system-image/releases

- Requires Treble-compliant base system
- Complex setup for QEMU
- Not recommended for QWAMOS use case

---

## Architecture Overview

### QWAMOS Android VM Stack

```
┌─────────────────────────────────────────────┐
│   Android 14 AOSP (Cuttlefish)              │
│   - System UI                               │
│   - Android Framework                       │
│   - Dalvik VM (ART)                        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   Android Linux Kernel (from Cuttlefish)    │
│   - virtio drivers                          │
│   - ARM64 generic config                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   QEMU ARM64 (virt machine)                 │
│   - virtio-blk (disk)                       │
│   - virtio-net (network)                    │
│   - virtio-gpu (graphics)                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   QWAMOS Host (Linux 6.6 + KVM)             │
└─────────────────────────────────────────────┘
```

---

## Setup Process (Phase 3, Week 3-4)

### Step 1: Download Cuttlefish Images

**On a Linux PC with internet** (images too large for Termux):

```bash
# Set build ID (check AOSP CI for latest)
BUILD_ID="12345678"  # Replace with actual build ID

# Create download directory
mkdir -p ~/android_images
cd ~/android_images

# Download system images
wget https://ci.android.com/builds/submitted/${BUILD_ID}/aosp_cf_arm64_only_phone-trunk_staging-userdebug/latest/aosp_cf_arm64_phone-img-${BUILD_ID}.zip

# Download Cuttlefish host tools
wget https://ci.android.com/builds/submitted/${BUILD_ID}/aosp_cf_arm64_only_phone-trunk_staging-userdebug/latest/cvd-host_package.tar.gz

# Verify downloads
ls -lh
```

**Expected files:**
- `aosp_cf_arm64_phone-img-*.zip` (~2-3 GB)
- `cvd-host_package.tar.gz` (~500 MB)

### Step 2: Extract and Organize

```bash
# Extract system images
unzip aosp_cf_arm64_phone-img-*.zip -d cuttlefish_images

# Extract host tools (optional - contains launch scripts)
tar -xzf cvd-host_package.tar.gz

# List extracted files
ls -lh cuttlefish_images/
```

**Expected contents:**
```
cuttlefish_images/
├── boot.img            # Kernel + ramdisk
├── vendor_boot.img     # Vendor ramdisk
├── super.img           # Combined system/vendor/product partitions
├── userdata.img        # User data partition
├── cache.img           # Cache partition
├── metadata.img        # Metadata partition
└── misc_info.txt       # Build information
```

### Step 3: Transfer to QWAMOS Device

**Via USB or network:**

```bash
# Option 1: USB transfer (if phone has USB OTG)
adb push cuttlefish_images/ /sdcard/Download/

# Option 2: Network transfer
scp -r cuttlefish_images/ user@phone-ip:/sdcard/Download/

# On Termux, move to QWAMOS directory
mv /sdcard/Download/cuttlefish_images ~/QWAMOS/vms/android-vm/
```

### Step 4: Extract Kernel and Ramdisk

Cuttlefish `boot.img` contains both kernel and ramdisk. We need to extract them:

```bash
cd ~/QWAMOS/vms/android-vm

# Install Android boot image tools
pkg install android-tools

# Extract boot.img
mkdir boot_extracted
cd boot_extracted

# Unpack boot image
python3 << 'EOF'
import struct
import os

# Simple boot.img parser (Android boot image format)
with open('../cuttlefish_images/boot.img', 'rb') as f:
    # Read header
    magic = f.read(8)
    kernel_size = struct.unpack('<I', f.read(4))[0]
    kernel_addr = f.read(4)
    ramdisk_size = struct.unpack('<I', f.read(4))[0]
    ramdisk_addr = f.read(4)
    second_size = struct.unpack('<I', f.read(4))[0]

    # Skip to kernel (after 2048-byte header)
    f.seek(2048)
    kernel = f.read(kernel_size)

    # Calculate ramdisk offset (page-aligned)
    ramdisk_offset = 2048 + ((kernel_size + 2047) // 2048) * 2048
    f.seek(ramdisk_offset)
    ramdisk = f.read(ramdisk_size)

    # Write extracted files
    with open('kernel', 'wb') as kf:
        kf.write(kernel)

    with open('ramdisk.img', 'wb') as rf:
        rf.write(ramdisk)

print(f"Extracted kernel ({len(kernel)} bytes) and ramdisk ({len(ramdisk)} bytes)")
EOF

# Decompress ramdisk (usually gzip or lz4)
file ramdisk.img  # Check compression format
gunzip < ramdisk.img > ramdisk.cpio || lz4 -d ramdisk.img ramdisk.cpio

# List ramdisk contents
cpio -tv < ramdisk.cpio | head -20
```

### Step 5: Create QCOW2 Disk Image

Convert Android images to QCOW2 format for QEMU:

```bash
cd ~/QWAMOS/vms/android-vm

# Create a large QCOW2 disk (32GB)
qemu-img create -f qcow2 android_disk.qcow2 32G

# Write partition table and copy Android partitions
# (This requires fdisk + dd work - see detailed guide below)
```

**Detailed Partition Setup:**

```bash
# Create GPT partition table
sgdisk -o android_disk.qcow2

# Add partitions (sizes from Cuttlefish layout)
sgdisk -n 1:2048:+512M -t 1:EF00 -c 1:"boot" android_disk.qcow2
sgdisk -n 2:0:+8G -t 2:8300 -c 2:"super" android_disk.qcow2
sgdisk -n 3:0:+4G -t 3:8300 -c 3:"userdata" android_disk.qcow2
sgdisk -n 4:0:+512M -t 4:8300 -c 4:"cache" android_disk.qcow2
sgdisk -n 5:0:+16M -t 5:8300 -c 5:"metadata" android_disk.qcow2

# Write Android images to partitions (using qemu-nbd)
sudo modprobe nbd max_part=8
sudo qemu-nbd --connect=/dev/nbd0 android_disk.qcow2

# Copy partitions
sudo dd if=cuttlefish_images/boot.img of=/dev/nbd0p1 bs=1M
sudo dd if=cuttlefish_images/super.img of=/dev/nbd0p2 bs=1M
sudo dd if=cuttlefish_images/userdata.img of=/dev/nbd0p3 bs=1M
sudo dd if=cuttlefish_images/cache.img of=/dev/nbd0p4 bs=1M
sudo dd if=cuttlefish_images/metadata.img of=/dev/nbd0p5 bs=1M

# Disconnect
sudo qemu-nbd --disconnect /dev/nbd0
```

**Note:** This step requires Linux desktop with root access. Alternative: Use prebuilt combined image if available.

### Step 6: Update android-vm Configuration

Edit `~/QWAMOS/vms/android-vm/config.yaml`:

```yaml
boot:
  kernel: /data/data/com.termux/files/home/QWAMOS/vms/android-vm/boot_extracted/kernel
  initrd: /data/data/com.termux/files/home/QWAMOS/vms/android-vm/boot_extracted/ramdisk.cpio
  cmdline: "console=ttyAMA0 androidboot.hardware=ranchu androidboot.selinux=permissive"

hardware:
  disk:
    primary:
      path: /data/data/com.termux/files/home/QWAMOS/vms/android-vm/android_disk.qcow2
      size: 32G
      format: qcow2
```

### Step 7: Boot Android VM

```bash
# Test boot
cd ~/QWAMOS
python hypervisor/scripts/vm_manager.py start android-vm

# Watch for Android boot messages
# Expected: Android logo, boot animation, System UI
```

---

## Expected Boot Sequence

1. **QEMU Initialization** (1-2 seconds)
   ```
   qemu-system-aarch64: Starting VM...
   ```

2. **Kernel Boot** (3-5 seconds)
   ```
   [    0.000000] Booting Linux on physical CPU 0x0000000000
   [    0.000000] Linux version 5.15.0-android13
   [    1.234567] Android Bootloader - Cuttlefish
   ```

3. **Android Init** (10-15 seconds)
   ```
   [    5.123456] init: Starting Android system
   [    5.234567] init: Loading SELinux policy
   [    6.345678] init: Starting servicemanager
   [    7.456789] init: Starting zygote
   ```

4. **System Services** (20-30 seconds)
   ```
   [   10.123456] system_server: Booting System Server
   [   15.234567] ActivityManager: System Ready
   [   20.345678] PackageManager: Ready
   ```

5. **Boot Complete** (30-60 seconds)
   ```
   Android Boot Complete!
   adb devices
   List of devices attached
   10.152.152.11:5555    device
   ```

---

## ADB Configuration

### Network ADB Setup

Android VM will be accessible via ADB over network:

**On QWAMOS host:**

```bash
# Install ADB on Termux
pkg install android-tools

# Connect to Android VM
adb connect 10.152.152.11:5555

# Verify connection
adb devices

# Open shell
adb shell
```

**Default ADB Port:** 5555 (configured in vm config NAT rules)

### ADB Commands for Testing

```bash
# Check Android version
adb shell getprop ro.build.version.release

# List packages
adb shell pm list packages | head -10

# Take screenshot
adb exec-out screencap -p > screenshot.png

# Install APK
adb install app.apk

# Logcat
adb logcat | head -50
```

---

## Performance Optimization

### QEMU Flags for Android

```bash
qemu-system-aarch64 \
  -machine virt,accel=tcg,gic-version=3,virtualization=on \
  -cpu cortex-a57,pmu=on \
  -smp 4 \
  -m 4096 \
  -kernel boot_extracted/kernel \
  -initrd boot_extracted/ramdisk.cpio \
  -append "console=ttyAMA0 androidboot.hardware=ranchu" \
  -drive file=android_disk.qcow2,if=virtio,format=qcow2,cache=writeback \
  -netdev user,id=net0,hostfwd=tcp::5555-:5555 \
  -device virtio-net-pci,netdev=net0 \
  -device virtio-gpu-pci,xres=1080,yres=2400 \
  -device virtio-rng-pci \
  -rtc base=utc,clock=host \
  -nographic
```

### Performance Tips

1. **CPU Cores:** Allocate 4 cores minimum for smooth UI
2. **RAM:** 4GB minimum, 6GB recommended
3. **Disk Cache:** `cache=writeback` for better I/O performance
4. **virtio Devices:** Always use virtio for disk/network (10x faster than emulated hardware)
5. **Graphics:** virtio-gpu for hardware-accelerated rendering

---

## Troubleshooting

### Issue: Kernel Panic on Boot

**Symptoms:**
```
Kernel panic - not syncing: VFS: Unable to mount root fs
```

**Solution:**
- Verify ramdisk extraction: `file ramdisk.cpio`
- Check kernel command line includes `androidboot.hardware=ranchu`
- Ensure disk partitions are correctly written

### Issue: Android Stuck at Boot Logo

**Symptoms:**
- Android logo appears but no progress

**Solution:**
```bash
# Enable verbose boot
-append "console=ttyAMA0 androidboot.hardware=ranchu loglevel=7 debug"

# Check logs for errors
adb logcat
```

### Issue: No Network / ADB Not Working

**Symptoms:**
```
adb connect 10.152.152.11:5555
cannot connect to 10.152.152.11:5555
```

**Solution:**
- Verify NAT port forwarding in QEMU command
- Check Android network settings: `adb shell ifconfig`
- Ensure `adbd` service is running: `adb shell getprop init.svc.adbd`

### Issue: Slow Performance

**Symptoms:**
- Laggy UI, slow app launches

**Solutions:**
1. Increase CPU cores: `-smp 6` or `-smp 8`
2. Increase RAM: `-m 6144` (6GB)
3. Use KVM if available (requires real ARM hardware with KVM support)
4. Disable SELinux: `androidboot.selinux=permissive`

---

## Security Considerations

### Post-Quantum Encryption

Android VM disk must be encrypted with ChaCha20-Poly1305 (NOT AES):

```bash
# Create encrypted container
veracrypt --create \
  --volume-type=normal \
  --encryption=chacha20 \
  --hash=blake3 \
  --filesystem=none \
  --size=32G \
  android_encrypted.vc

# Mount encrypted container
veracrypt android_encrypted.vc /mnt/android_encrypted

# Create QCOW2 inside encrypted volume
qemu-img create -f qcow2 /mnt/android_encrypted/android_disk.qcow2 32G
```

### Network Isolation

Android VM should be isolated from host network:

- **NAT Mode:** VM cannot directly access host network
- **Firewall Rules:** Block all outbound except Whonix Gateway
- **ADB over NAT:** Port 5555 forwarded only from localhost

### SELinux Enforcing

For production use, ensure SELinux is enforcing:

```bash
# Remove 'selinux=permissive' from boot args
-append "console=ttyAMA0 androidboot.hardware=ranchu androidboot.selinux=enforcing"
```

---

## Alternative: Simpler Approach with Android x86

**If ARM64 proves too complex**, consider Android-x86 project:

**Pros:**
- Easier to set up
- Better QEMU compatibility
- ISO images available

**Cons:**
- x86_64 architecture (not native ARM)
- Translation overhead on ARM devices
- Not ideal for QWAMOS security model

**Download:** https://www.android-x86.org/download.html

---

## Next Steps

1. **Download Cuttlefish images** on Linux PC
2. **Extract kernel and ramdisk** from boot.img
3. **Transfer to QWAMOS device** via USB/network
4. **Test Android boot** in QEMU
5. **Configure ADB access** over network
6. **Document success/failures** for iteration

---

## Resources

### Official Documentation

- **AOSP CI:** https://ci.android.com
- **Cuttlefish Overview:** https://source.android.com/docs/setup/create/cuttlefish
- **Android Boot Image Format:** https://source.android.com/docs/core/architecture/bootloader/boot-image-header

### Community Guides

- **Android QEMU on ARM64:** https://gist.github.com/Abyss-W4tcher/f1833623c975193446315d48c106750e
- **Cuttlefish Setup:** https://github.com/google/android-cuttlefish

### QWAMOS Internal

- `docs/PHASE3_HYPERVISOR_SPEC.md` - Hypervisor architecture
- `vms/android-vm/config.yaml` - VM configuration
- `hypervisor/scripts/vm_manager.py` - VM management tool

---

## Conclusion

This guide provides the foundation for setting up Android 14 as a guest VM in QWAMOS. The Cuttlefish approach is recommended due to its QEMU-native design and regular AOSP updates.

**Status:** Research complete, ready for implementation in Phase 3 Week 3-4.

**Estimated Time:** 4-6 hours for complete setup and testing.

**Confidence Level:** HIGH - Cuttlefish is purpose-built for this use case.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-01
**Author:** Dezirae-Stark
**QWAMOS Phase:** 3 (Week 3-4)
