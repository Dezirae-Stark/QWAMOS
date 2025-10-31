# QWAMOS Self-Flashing Installer Specification

## Executive Summary

This document specifies the implementation of a **self-flashing installer** that allows QWAMOS to be installed directly from the mobile device without requiring:
- Physical connection to a PC
- SD card transfers
- Fastboot/ADB on external computer
- Manual recovery mode operations

The installer will run entirely on the device, leveraging root access and custom recovery to safely replace the Android OS with QWAMOS while maintaining bootloader integrity and providing rollback capabilities.

---

## 1. Architecture Overview

### 1.1 Installation Methods

QWAMOS will support two self-flashing installation methods:

#### Method A: Root-Based Direct Flash (Recommended)
```
Android OS (rooted with Magisk)
    ├─> QWAMOS Installer App (React Native)
    │   ├─> Pre-flash validation
    │   ├─> Automated backup creation
    │   ├─> Partition management
    │   └─> Reboot to recovery
    └─> Custom Recovery (TWRP/OrangeFox)
        ├─> Flash QWAMOS bootloader
        ├─> Flash QWAMOS kernel
        ├─> Flash QWAMOS system
        └─> Install Android as VM
```

#### Method B: Recovery-Based Flash (Alternative)
```
User boots to TWRP manually
    ├─> QWAMOS Installer ZIP (flashable)
    │   ├─> Validation script
    │   ├─> Partition backup
    │   ├─> QWAMOS installation
    │   └─> Post-install configuration
    └─> Automatic reboot to QWAMOS
```

### 1.2 Component Architecture

```
QWAMOS Self-Flasher
    ├─> Installer App (Android-based)
    │   ├─> Pre-installation checks
    │   ├─> User data backup
    │   ├─> Download manager
    │   └─> Installation orchestrator
    │
    ├─> Flashable Package (ZIP)
    │   ├─> META-INF/com/google/android/
    │   │   └─> updater-script (installation commands)
    │   ├─> boot.img (QWAMOS kernel)
    │   ├─> bootloader.img (U-Boot)
    │   ├─> system.img (QWAMOS root filesystem)
    │   ├─> vms/ (Android VM image)
    │   └─> scripts/ (post-install automation)
    │
    └─> Recovery Environment
        ├─> TWRP 3.7+ (with Kyber support)
        ├─> Partition management tools
        └─> Rollback system
```

---

## 2. Installation Prerequisites

### 2.1 Device Requirements

**Minimum Requirements:**
- ARM64 processor (ARMv8-A or newer)
- 6GB RAM minimum (8GB+ recommended)
- 128GB storage minimum (256GB+ recommended)
- Unlocked bootloader
- Root access (Magisk 26.0+)
- Custom recovery installed (TWRP 3.7+)

**Supported Devices (Initial):**
- Google Pixel 6/7/8 series
- OnePlus 9/10/11 series
- Xiaomi Mi 11/12/13 series
- Samsung Galaxy S22/S23 (Exynos/Snapdragon variants)

### 2.2 Software Prerequisites

**On Android (before installation):**
```
✓ Android 12+ (API level 31+)
✓ Magisk 26.0+ installed and working
✓ TWRP 3.7+ or OrangeFox Recovery
✓ 50GB+ free internal storage
✓ Termux or similar terminal emulator (optional for debugging)
```

**Bootloader Status:**
```bash
# Check bootloader unlock status
adb shell getprop ro.boot.flash.locked
# Should return: 0 (unlocked)
```

---

## 3. Installer App Implementation

### 3.1 React Native Installer App

**File:** `frontend/installer/QWAMOSInstaller.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { View, Text, Button, ProgressBar, Alert } from 'react-native';
import RNFetchBlob from 'rn-fetch-blob';
import { RootManager } from './RootManager';
import { PartitionManager } from './PartitionManager';
import { BackupManager } from './BackupManager';

interface InstallationState {
  step: string;
  progress: number;
  status: 'idle' | 'downloading' | 'validating' | 'backing_up' | 'installing' | 'complete' | 'error';
  error?: string;
}

export const QWAMOSInstaller: React.FC = () => {
  const [state, setState] = useState<InstallationState>({
    step: 'Ready to install QWAMOS',
    progress: 0,
    status: 'idle'
  });

  // Pre-installation checks
  const performChecks = async (): Promise<boolean> => {
    setState({ ...state, step: 'Performing pre-installation checks...', progress: 5 });

    // 1. Check root access
    const hasRoot = await RootManager.checkRoot();
    if (!hasRoot) {
      setState({ ...state, status: 'error', error: 'Root access required' });
      return false;
    }

    // 2. Check bootloader unlock
    const isUnlocked = await RootManager.checkBootloaderUnlock();
    if (!isUnlocked) {
      setState({ ...state, status: 'error', error: 'Bootloader must be unlocked' });
      return false;
    }

    // 3. Check storage space
    const freeSpace = await PartitionManager.getFreeSpace('/data');
    if (freeSpace < 50 * 1024 * 1024 * 1024) { // 50GB
      setState({ ...state, status: 'error', error: 'Insufficient storage (need 50GB free)' });
      return false;
    }

    // 4. Check recovery installation
    const hasRecovery = await RootManager.checkRecovery();
    if (!hasRecovery) {
      setState({ ...state, status: 'error', error: 'TWRP or compatible recovery required' });
      return false;
    }

    // 5. Check device compatibility
    const deviceModel = await RootManager.getDeviceModel();
    const isSupported = SUPPORTED_DEVICES.includes(deviceModel);
    if (!isSupported) {
      Alert.alert(
        'Device Not Officially Supported',
        `Your device (${deviceModel}) is not officially supported. Continue at your own risk?`,
        [
          { text: 'Cancel', style: 'cancel', onPress: () => {} },
          { text: 'Continue Anyway', onPress: () => {} }
        ]
      );
    }

    setState({ ...state, step: 'All checks passed', progress: 10 });
    return true;
  };

  // Download QWAMOS installation package
  const downloadQWAMOS = async (): Promise<boolean> => {
    setState({ ...state, status: 'downloading', step: 'Downloading QWAMOS...', progress: 15 });

    const QWAMOS_URL = 'https://github.com/Dezirae-Stark/QWAMOS/releases/latest/download/qwamos-installer.zip';
    const downloadPath = '/sdcard/Download/qwamos-installer.zip';

    try {
      const result = await RNFetchBlob.config({
        path: downloadPath,
        overwrite: true
      })
      .fetch('GET', QWAMOS_URL)
      .progress((received, total) => {
        const progress = 15 + (received / total) * 30; // 15% to 45%
        setState({ ...state, progress });
      });

      if (result.respInfo.status !== 200) {
        throw new Error(`Download failed: ${result.respInfo.status}`);
      }

      setState({ ...state, step: 'Download complete', progress: 45 });
      return true;
    } catch (error) {
      setState({ ...state, status: 'error', error: `Download failed: ${error.message}` });
      return false;
    }
  };

  // Validate downloaded package
  const validatePackage = async (): Promise<boolean> => {
    setState({ ...state, status: 'validating', step: 'Validating package integrity...', progress: 50 });

    const downloadPath = '/sdcard/Download/qwamos-installer.zip';
    const checksumPath = '/sdcard/Download/qwamos-installer.sha256';

    try {
      // Download checksum file
      await RNFetchBlob.config({ path: checksumPath })
        .fetch('GET', 'https://github.com/Dezirae-Stark/QWAMOS/releases/latest/download/qwamos-installer.sha256');

      // Calculate SHA256 of downloaded file
      const calculatedHash = await RNFetchBlob.fs.hash(downloadPath, 'sha256');
      const expectedHash = await RNFetchBlob.fs.readFile(checksumPath, 'utf8');

      if (calculatedHash !== expectedHash.trim()) {
        throw new Error('Checksum mismatch - package may be corrupted');
      }

      setState({ ...state, step: 'Package validated', progress: 55 });
      return true;
    } catch (error) {
      setState({ ...state, status: 'error', error: `Validation failed: ${error.message}` });
      return false;
    }
  };

  // Create backup of current Android system
  const createBackup = async (): Promise<boolean> => {
    setState({ ...state, status: 'backing_up', step: 'Backing up current system...', progress: 60 });

    try {
      // Backup critical partitions
      await BackupManager.backupPartition('boot', '/sdcard/QWAMOS-Backup/boot.img');
      await BackupManager.backupPartition('system', '/sdcard/QWAMOS-Backup/system.img');
      await BackupManager.backupUserData('/sdcard/QWAMOS-Backup/userdata/');

      setState({ ...state, step: 'Backup complete', progress: 75 });
      return true;
    } catch (error) {
      setState({ ...state, status: 'error', error: `Backup failed: ${error.message}` });
      return false;
    }
  };

  // Install QWAMOS
  const installQWAMOS = async () => {
    setState({ ...state, status: 'installing', step: 'Installing QWAMOS...', progress: 80 });

    try {
      // Copy installer package to recovery-accessible location
      await RootManager.copyToRecovery(
        '/sdcard/Download/qwamos-installer.zip',
        '/data/media/0/TWRP/qwamos-installer.zip'
      );

      // Create installation command file for recovery
      const installCommands = `
        install /data/media/0/TWRP/qwamos-installer.zip
        reboot
      `;
      await RNFetchBlob.fs.writeFile('/cache/recovery/openrecoveryscript', installCommands, 'utf8');

      setState({ ...state, step: 'Rebooting to recovery...', progress: 90 });

      // Reboot to recovery (installation will happen automatically)
      await RootManager.rebootToRecovery();

      setState({ ...state, status: 'complete', step: 'Installation initiated', progress: 100 });
    } catch (error) {
      setState({ ...state, status: 'error', error: `Installation failed: ${error.message}` });
    }
  };

  // Main installation flow
  const startInstallation = async () => {
    const checksPass = await performChecks();
    if (!checksPass) return;

    const downloaded = await downloadQWAMOS();
    if (!downloaded) return;

    const validated = await validatePackage();
    if (!validated) return;

    const backedUp = await createBackup();
    if (!backedUp) return;

    await installQWAMOS();
  };

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 20 }}>
        QWAMOS Installer
      </Text>

      <Text style={{ fontSize: 16, marginBottom: 10 }}>
        {state.step}
      </Text>

      <ProgressBar progress={state.progress / 100} color="#4CAF50" />

      {state.status === 'idle' && (
        <Button title="Install QWAMOS" onPress={startInstallation} />
      )}

      {state.status === 'error' && (
        <View>
          <Text style={{ color: 'red', marginTop: 10 }}>{state.error}</Text>
          <Button title="Retry" onPress={startInstallation} />
        </View>
      )}

      {state.status === 'complete' && (
        <Text style={{ color: 'green', marginTop: 10 }}>
          Device will reboot to recovery and complete installation automatically.
        </Text>
      )}
    </View>
  );
};

const SUPPORTED_DEVICES = [
  'Pixel 6', 'Pixel 7', 'Pixel 8',
  'OnePlus 9', 'OnePlus 10', 'OnePlus 11',
  'Mi 11', 'Mi 12', 'Mi 13'
];
```

### 3.2 Root Manager Implementation

**File:** `frontend/installer/RootManager.ts`

```typescript
import { NativeModules } from 'react-native';
import RNFetchBlob from 'rn-fetch-blob';

const { RootBridge } = NativeModules;

export class RootManager {
  /**
   * Check if device has root access
   */
  static async checkRoot(): Promise<boolean> {
    try {
      const result = await RootBridge.executeCommand('su -c "echo test"');
      return result.trim() === 'test';
    } catch (error) {
      return false;
    }
  }

  /**
   * Check if bootloader is unlocked
   */
  static async checkBootloaderUnlock(): Promise<boolean> {
    try {
      const result = await RootBridge.executeCommand('getprop ro.boot.flash.locked');
      return result.trim() === '0';
    } catch (error) {
      return false;
    }
  }

  /**
   * Check if custom recovery is installed
   */
  static async checkRecovery(): Promise<boolean> {
    try {
      // Check for TWRP or OrangeFox recovery
      const twrpExists = await RNFetchBlob.fs.exists('/cache/recovery/.twrps');
      const ofoxExists = await RNFetchBlob.fs.exists('/cache/recovery/.ofox');
      return twrpExists || ofoxExists;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get device model
   */
  static async getDeviceModel(): Promise<string> {
    try {
      const result = await RootBridge.executeCommand('getprop ro.product.model');
      return result.trim();
    } catch (error) {
      return 'Unknown';
    }
  }

  /**
   * Copy file to recovery-accessible location
   */
  static async copyToRecovery(source: string, destination: string): Promise<void> {
    await RootBridge.executeCommand(`su -c "cp ${source} ${destination}"`);
  }

  /**
   * Reboot to recovery mode
   */
  static async rebootToRecovery(): Promise<void> {
    await RootBridge.executeCommand('su -c "reboot recovery"');
  }

  /**
   * Flash image to partition
   */
  static async flashPartition(partition: string, imagePath: string): Promise<void> {
    const command = `su -c "dd if=${imagePath} of=/dev/block/by-name/${partition} bs=4M"`;
    await RootBridge.executeCommand(command);
  }
}
```

### 3.3 Partition Manager

**File:** `frontend/installer/PartitionManager.ts`

```typescript
import { NativeModules } from 'react-native';

const { RootBridge } = NativeModules;

export class PartitionManager {
  /**
   * Get free space on partition
   */
  static async getFreeSpace(mountPoint: string): Promise<number> {
    try {
      const result = await RootBridge.executeCommand(`df -k ${mountPoint} | tail -1 | awk '{print $4}'`);
      return parseInt(result.trim()) * 1024; // Convert to bytes
    } catch (error) {
      return 0;
    }
  }

  /**
   * Get partition block device path
   */
  static async getBlockDevice(partition: string): Promise<string> {
    const result = await RootBridge.executeCommand(`readlink -f /dev/block/by-name/${partition}`);
    return result.trim();
  }

  /**
   * List all partitions
   */
  static async listPartitions(): Promise<string[]> {
    const result = await RootBridge.executeCommand('ls /dev/block/by-name/');
    return result.trim().split('\n');
  }

  /**
   * Create partition layout for QWAMOS
   */
  static async createQWAMOSLayout(): Promise<void> {
    // This will resize/create partitions for QWAMOS
    // WARNING: This is destructive and requires careful implementation

    const commands = [
      // Backup current partition table
      'sgdisk -b /sdcard/QWAMOS-Backup/partition-table.bak /dev/block/sda',

      // Create QWAMOS partitions
      'sgdisk -n 0:0:+512M -t 0:8300 -c 0:"qwamos-boot" /dev/block/sda',
      'sgdisk -n 0:0:+4G -t 0:8300 -c 0:"qwamos-system" /dev/block/sda',
      'sgdisk -n 0:0:0 -t 0:8300 -c 0:"qwamos-data" /dev/block/sda',

      // Reload partition table
      'partprobe /dev/block/sda'
    ];

    for (const cmd of commands) {
      await RootBridge.executeCommand(`su -c "${cmd}"`);
    }
  }
}
```

### 3.4 Backup Manager

**File:** `frontend/installer/BackupManager.ts`

```typescript
import RNFetchBlob from 'rn-fetch-blob';
import { NativeModules } from 'react-native';

const { RootBridge } = NativeModules;

export class BackupManager {
  /**
   * Backup a partition to image file
   */
  static async backupPartition(partition: string, outputPath: string): Promise<void> {
    const blockDevice = `/dev/block/by-name/${partition}`;

    // Ensure backup directory exists
    await RNFetchBlob.fs.mkdir('/sdcard/QWAMOS-Backup');

    // Create raw image backup using dd
    const command = `su -c "dd if=${blockDevice} of=${outputPath} bs=4M status=progress"`;
    await RootBridge.executeCommand(command);
  }

  /**
   * Backup user data (selective backup of important files)
   */
  static async backupUserData(outputDir: string): Promise<void> {
    await RNFetchBlob.fs.mkdir(outputDir);

    const backupPaths = [
      '/sdcard/DCIM',           // Photos
      '/sdcard/Pictures',       // Pictures
      '/sdcard/Download',       // Downloads
      '/sdcard/Documents',      // Documents
      '/data/data',             // App data (requires root)
    ];

    for (const path of backupPaths) {
      const targetPath = `${outputDir}${path}`;
      await RootBridge.executeCommand(`su -c "cp -r ${path} ${targetPath}"`);
    }
  }

  /**
   * Create rollback package
   */
  static async createRollbackPackage(): Promise<void> {
    const rollbackDir = '/sdcard/QWAMOS-Backup/rollback';
    await RNFetchBlob.fs.mkdir(rollbackDir);

    // Backup critical partitions for rollback
    await this.backupPartition('boot', `${rollbackDir}/boot.img`);
    await this.backupPartition('system', `${rollbackDir}/system.img`);
    await this.backupPartition('vendor', `${rollbackDir}/vendor.img`);

    // Create rollback script
    const rollbackScript = `
#!/sbin/sh
# QWAMOS Rollback Script
# This script restores the original Android system

echo "Restoring original Android system..."

dd if=/sdcard/QWAMOS-Backup/rollback/boot.img of=/dev/block/by-name/boot bs=4M
dd if=/sdcard/QWAMOS-Backup/rollback/system.img of=/dev/block/by-name/system bs=4M
dd if=/sdcard/QWAMOS-Backup/rollback/vendor.img of=/dev/block/by-name/vendor bs=4M

echo "Rollback complete. Rebooting..."
reboot
    `;

    await RNFetchBlob.fs.writeFile(`${rollbackDir}/rollback.sh`, rollbackScript, 'utf8');
  }
}
```

---

## 4. Flashable ZIP Package

### 4.1 Package Structure

```
qwamos-installer.zip
├── META-INF/
│   └── com/
│       └── google/
│           └── android/
│               ├── update-binary           # Installation script interpreter
│               └── updater-script          # Installation commands
│
├── boot.img                                # QWAMOS kernel image
├── bootloader.img                          # U-Boot bootloader
├── system.img                              # QWAMOS root filesystem
├── vms/
│   └── android-base.qcow2                  # Base Android VM image
│
├── scripts/
│   ├── install.sh                          # Main installation script
│   ├── partition_setup.sh                  # Partition management
│   ├── kyber_verify.sh                     # Kyber signature verification
│   └── post_install.sh                     # Post-installation configuration
│
├── crypto/
│   ├── kyber_pubkey.pem                    # Public key for verification
│   └── signatures.sha256                   # Signed checksums
│
└── README.txt                              # Installation instructions
```

### 4.2 Updater Script

**File:** `META-INF/com/google/android/updater-script`

```edify
ui_print("===============================");
ui_print("  QWAMOS Installation v1.0");
ui_print("===============================");
ui_print("");

# Verify device compatibility
ui_print("Verifying device compatibility...");
assert(getprop("ro.product.device") == "pixel6" ||
       getprop("ro.product.device") == "pixel7" ||
       getprop("ro.product.device") == "pixel8" ||
       getprop("ro.product.device") == "OnePlus9" ||
       getprop("ro.product.device") == "OnePlus10");

# Mount partitions
ui_print("Mounting partitions...");
run_program("/sbin/mount", "/system");
run_program("/sbin/mount", "/data");
run_program("/sbin/mount", "/cache");

# Verify package integrity
ui_print("Verifying package integrity...");
package_extract_file("scripts/kyber_verify.sh", "/tmp/kyber_verify.sh");
set_metadata("/tmp/kyber_verify.sh", "uid", 0, "gid", 0, "mode", 0755);
assert(run_program("/tmp/kyber_verify.sh") == "0");

# Create backup
ui_print("Creating backup (this may take several minutes)...");
package_extract_file("scripts/partition_setup.sh", "/tmp/partition_setup.sh");
set_metadata("/tmp/partition_setup.sh", "uid", 0, "gid", 0, "mode", 0755);
run_program("/tmp/partition_setup.sh", "backup");

# Flash U-Boot bootloader
ui_print("Installing QWAMOS bootloader...");
package_extract_file("bootloader.img", "/tmp/bootloader.img");
run_program("/sbin/dd", "if=/tmp/bootloader.img", "of=/dev/block/by-name/bootloader", "bs=4M");

# Flash QWAMOS kernel
ui_print("Installing QWAMOS kernel...");
package_extract_file("boot.img", "/tmp/boot.img");
run_program("/sbin/dd", "if=/tmp/boot.img", "of=/dev/block/by-name/boot", "bs=4M");

# Flash QWAMOS system
ui_print("Installing QWAMOS system (this will take several minutes)...");
package_extract_file("system.img", "/tmp/system.img");
run_program("/sbin/dd", "if=/tmp/system.img", "of=/dev/block/by-name/system", "bs=4M");

# Setup VM storage
ui_print("Setting up VM storage...");
run_program("/sbin/mkdir", "-p", "/data/qwamos/vms");
package_extract_file("vms/android-base.qcow2", "/data/qwamos/vms/android-base.qcow2");

# Post-installation configuration
ui_print("Running post-installation setup...");
package_extract_file("scripts/post_install.sh", "/tmp/post_install.sh");
set_metadata("/tmp/post_install.sh", "uid", 0, "gid", 0, "mode", 0755);
run_program("/tmp/post_install.sh");

# Unmount partitions
ui_print("Cleaning up...");
unmount("/system");
unmount("/data");
unmount("/cache");

ui_print("");
ui_print("===============================");
ui_print("  QWAMOS Installation Complete");
ui_print("===============================");
ui_print("");
ui_print("Device will reboot in 5 seconds...");
ui_print("First boot may take 3-5 minutes.");
ui_print("");
```

### 4.3 Installation Script

**File:** `scripts/install.sh`

```bash
#!/sbin/sh
#
# QWAMOS Main Installation Script
#

set -e

OUTFD="/proc/self/fd/$2"
ZIPFILE="$3"
TMP="/tmp/qwamos"

# UI helper functions
ui_print() {
    echo "ui_print $1" > "$OUTFD"
    echo "ui_print" > "$OUTFD"
}

abort() {
    ui_print "ERROR: $1"
    exit 1
}

# Extract installation files
ui_print "Extracting installation files..."
mkdir -p "$TMP"
cd "$TMP"
unzip -o "$ZIPFILE"

# Verify Kyber signatures
ui_print "Verifying post-quantum cryptographic signatures..."
if ! ./scripts/kyber_verify.sh; then
    abort "Signature verification failed"
fi

# Check device compatibility
DEVICE=$(getprop ro.product.device)
ui_print "Device: $DEVICE"

case "$DEVICE" in
    pixel6|pixel7|pixel8|OnePlus9|OnePlus10|OnePlus11|Mi11|Mi12|Mi13)
        ui_print "Device supported"
        ;;
    *)
        ui_print "WARNING: Device not officially supported"
        ui_print "Continue at your own risk"
        sleep 3
        ;;
esac

# Check storage space
FREE_SPACE=$(df /data | tail -1 | awk '{print $4}')
REQUIRED_SPACE=$((50 * 1024 * 1024))  # 50GB in KB

if [ "$FREE_SPACE" -lt "$REQUIRED_SPACE" ]; then
    abort "Insufficient storage space (need 50GB free)"
fi

# Create partition layout
ui_print "Preparing partition layout..."
./scripts/partition_setup.sh create

# Flash components
ui_print "Flashing QWAMOS bootloader..."
dd if=bootloader.img of=/dev/block/by-name/bootloader bs=4M status=progress

ui_print "Flashing QWAMOS kernel..."
dd if=boot.img of=/dev/block/by-name/boot bs=4M status=progress

ui_print "Flashing QWAMOS system..."
dd if=system.img of=/dev/block/by-name/system bs=4M status=progress

# Setup data partition
ui_print "Setting up QWAMOS data partition..."
mkdir -p /data/qwamos/{vms,crypto,network,logs}
cp -r vms/* /data/qwamos/vms/
cp -r crypto/* /data/qwamos/crypto/

# Post-installation
ui_print "Running post-installation configuration..."
./scripts/post_install.sh

ui_print "Installation complete!"
```

### 4.4 Kyber Verification Script

**File:** `scripts/kyber_verify.sh`

```bash
#!/sbin/sh
#
# Kyber-1024 Signature Verification Script
#

KYBER_VERIFY="/tmp/qwamos/crypto/kyber_verify"
PUBKEY="/tmp/qwamos/crypto/kyber_pubkey.pem"
SIGNATURES="/tmp/qwamos/crypto/signatures.sha256"

# Verify each component
verify_file() {
    local file=$1
    local expected_hash=$(grep "$file" "$SIGNATURES" | awk '{print $1}')

    if [ -z "$expected_hash" ]; then
        echo "ERROR: No signature found for $file"
        return 1
    fi

    local actual_hash=$(sha256sum "$file" | awk '{print $1}')

    if [ "$actual_hash" != "$expected_hash" ]; then
        echo "ERROR: Checksum mismatch for $file"
        return 1
    fi

    # Verify Kyber signature on hash
    if ! "$KYBER_VERIFY" "$PUBKEY" "$file" "$SIGNATURES"; then
        echo "ERROR: Kyber signature verification failed for $file"
        return 1
    fi

    return 0
}

# Verify all critical components
for file in bootloader.img boot.img system.img; do
    echo "Verifying $file..."
    if ! verify_file "$file"; then
        exit 1
    fi
done

echo "All signatures verified successfully"
exit 0
```

---

## 5. Recovery Integration

### 5.1 TWRP Modifications

To support QWAMOS installation, TWRP needs minor modifications for Kyber verification support:

**File:** `recovery/twrp/kyber_support.cpp`

```cpp
/*
 * TWRP Kyber-1024 Support Module
 */

#include <openssl/evp.h>
#include <oqs/oqs.h>

extern "C" {

int twrp_kyber_verify(const char* pubkey_path,
                      const char* data_path,
                      const char* signature_path) {
    OQS_SIG *sig = OQS_SIG_new(OQS_SIG_alg_dilithium_5);
    if (sig == NULL) {
        return -1;
    }

    // Load public key
    FILE *pk_file = fopen(pubkey_path, "rb");
    if (!pk_file) {
        OQS_SIG_free(sig);
        return -1;
    }

    uint8_t public_key[OQS_SIG_dilithium_5_length_public_key];
    fread(public_key, 1, sizeof(public_key), pk_file);
    fclose(pk_file);

    // Load data
    FILE *data_file = fopen(data_path, "rb");
    if (!data_file) {
        OQS_SIG_free(sig);
        return -1;
    }

    fseek(data_file, 0, SEEK_END);
    size_t data_len = ftell(data_file);
    fseek(data_file, 0, SEEK_SET);

    uint8_t *data = (uint8_t*)malloc(data_len);
    fread(data, 1, data_len, data_file);
    fclose(data_file);

    // Load signature
    FILE *sig_file = fopen(signature_path, "rb");
    if (!sig_file) {
        free(data);
        OQS_SIG_free(sig);
        return -1;
    }

    uint8_t signature[OQS_SIG_dilithium_5_length_signature];
    fread(signature, 1, sizeof(signature), sig_file);
    fclose(sig_file);

    // Verify signature
    OQS_STATUS status = OQS_SIG_verify(sig, data, data_len, signature,
                                       sizeof(signature), public_key);

    free(data);
    OQS_SIG_free(sig);

    return (status == OQS_SUCCESS) ? 0 : -1;
}

}  // extern "C"
```

### 5.2 OpenRecoveryScript Support

QWAMOS installer creates an OpenRecoveryScript for automated installation:

**File:** `/cache/recovery/openrecoveryscript` (created by installer app)

```bash
# QWAMOS Installation Script
# Generated by QWAMOS Installer App

# Set max brightness for visibility
cmd brightness 255

# Print header
print ===============================
print   QWAMOS Automated Installation
print ===============================
print

# Install QWAMOS package
install /data/media/0/TWRP/qwamos-installer.zip

# Wipe cache (optional, keeps user data intact)
# wipe cache

# Reboot to system
print
print Installation complete!
print Rebooting to QWAMOS in 5 seconds...
sleep 5
reboot
```

---

## 6. Rollback and Safety Mechanisms

### 6.1 Automatic Rollback

If QWAMOS fails to boot after installation, U-Boot can automatically rollback:

**File:** `bootloader/u-boot/rollback.c`

```c
/*
 * U-Boot QWAMOS Rollback Mechanism
 */

#define MAX_BOOT_ATTEMPTS 3
#define ROLLBACK_PARTITION "/dev/block/by-name/rollback_boot"

int check_boot_success(void) {
    // Check if QWAMOS successfully booted
    // This is set by QWAMOS init system on successful boot
    char *success_flag = env_get("qwamos_boot_success");
    return (success_flag && strcmp(success_flag, "1") == 0);
}

int get_boot_attempts(void) {
    char *attempts = env_get("boot_attempts");
    return attempts ? atoi(attempts) : 0;
}

void increment_boot_attempts(void) {
    int attempts = get_boot_attempts() + 1;
    char buf[16];
    snprintf(buf, sizeof(buf), "%d", attempts);
    env_set("boot_attempts", buf);
    env_save();
}

void reset_boot_attempts(void) {
    env_set("boot_attempts", "0");
    env_set("qwamos_boot_success", "0");
    env_save();
}

void perform_rollback(void) {
    printf("Boot failed %d times. Initiating rollback...\n", MAX_BOOT_ATTEMPTS);

    // Restore backup boot partition
    run_command("ext4load mmc 0:1 ${loadaddr} /backup/boot.img", 0);
    run_command("mmc write ${loadaddr} boot 0x100000", 0);

    // Restore backup system partition
    run_command("ext4load mmc 0:1 ${loadaddr} /backup/system.img", 0);
    run_command("mmc write ${loadaddr} system 0x1000000", 0);

    printf("Rollback complete. Rebooting to original system...\n");
    reset_boot_attempts();
    run_command("reset", 0);
}

int qwamos_boot_check(void) {
    if (!check_boot_success()) {
        increment_boot_attempts();

        if (get_boot_attempts() >= MAX_BOOT_ATTEMPTS) {
            perform_rollback();
            return -1;
        }
    } else {
        reset_boot_attempts();
    }

    return 0;
}
```

### 6.2 Manual Rollback via Recovery

Users can manually rollback to Android from TWRP:

**File:** `scripts/manual_rollback.sh`

```bash
#!/sbin/sh
#
# Manual QWAMOS Rollback Script
# Place in /sdcard/QWAMOS-Backup/rollback.sh
# Flash from TWRP: Install -> Install ZIP -> rollback.sh
#

ui_print "===============================";
ui_print "  QWAMOS Rollback to Android";
ui_print "===============================";
ui_print "";

# Check if backup exists
if [ ! -f "/sdcard/QWAMOS-Backup/boot.img" ]; then
    ui_print "ERROR: Backup not found!";
    exit 1;
fi

# Restore bootloader
ui_print "Restoring original bootloader...";
dd if=/sdcard/QWAMOS-Backup/bootloader.img of=/dev/block/by-name/bootloader bs=4M

# Restore boot partition
ui_print "Restoring boot partition...";
dd if=/sdcard/QWAMOS-Backup/boot.img of=/dev/block/by-name/boot bs=4M

# Restore system partition
ui_print "Restoring system partition...";
dd if=/sdcard/QWAMOS-Backup/system.img of=/dev/block/by-name/system bs=4M

# Restore vendor partition
ui_print "Restoring vendor partition...";
dd if=/sdcard/QWAMOS-Backup/vendor.img of=/dev/block/by-name/vendor bs=4M

ui_print "";
ui_print "Rollback complete!";
ui_print "Rebooting to Android...";
reboot;
```

---

## 7. Implementation Timeline

### Week 1-2: React Native Installer App Development
- [ ] Create React Native project structure
- [ ] Implement RootManager for root operations
- [ ] Implement PartitionManager for storage management
- [ ] Implement BackupManager for system backup
- [ ] Create UI for installation wizard
- [ ] Test on supported devices

### Week 3-4: Flashable ZIP Package Creation
- [ ] Create updater-script for TWRP installation
- [ ] Implement partition setup scripts
- [ ] Implement Kyber verification scripts
- [ ] Create post-installation configuration scripts
- [ ] Package all components into ZIP
- [ ] Sign ZIP with Kyber-1024

### Week 5-6: TWRP Modifications
- [ ] Add liboqs support to TWRP
- [ ] Implement Kyber verification in recovery
- [ ] Test recovery installation process
- [ ] Create custom TWRP build for QWAMOS

### Week 7-8: Rollback System
- [ ] Implement U-Boot rollback mechanism
- [ ] Create manual rollback scripts
- [ ] Test automatic rollback on boot failure
- [ ] Test manual rollback from recovery

### Week 9-10: Testing and Refinement
- [ ] Test on all supported devices
- [ ] Verify backup and restore functionality
- [ ] Test rollback mechanisms
- [ ] Optimize installation speed
- [ ] Create user documentation

---

## 8. Safety Considerations

### 8.1 Pre-Installation Warnings

The installer app must display clear warnings:

```
⚠️  WARNING ⚠️

This installation will:
• Replace your Android OS completely with QWAMOS
• Require a factory reset (user data will be backed up)
• Take 30-60 minutes to complete
• Require 50GB+ free storage
• Potentially void your device warranty

Before proceeding:
✓ Ensure device is charged to at least 70%
✓ Back up any data not stored in /sdcard
✓ Verify you have the rollback instructions saved
✓ Understand this is experimental software

Do you want to continue?
[Cancel] [I Understand, Continue]
```

### 8.2 Brick Prevention

To prevent device bricking:

1. **Bootloader Verification**: Always verify bootloader unlock status before flashing
2. **Battery Check**: Require minimum 70% battery before installation
3. **Backup Creation**: Mandatory backup of boot, system, and vendor partitions
4. **Signature Verification**: All images must pass Kyber-1024 signature verification
5. **Automatic Rollback**: U-Boot automatically reverts to backup after 3 failed boots
6. **Recovery Access**: Ensure TWRP remains accessible even if QWAMOS fails to boot

### 8.3 Emergency Recovery

In case of boot failure:

```
EMERGENCY RECOVERY PROCEDURE:

1. Power off device completely
2. Boot into recovery mode:
   - Most devices: Hold Volume Down + Power
   - Pixel devices: Hold Volume Down + Power, select "Recovery mode"

3. In TWRP:
   - Install -> Install ZIP
   - Navigate to /sdcard/QWAMOS-Backup/rollback.sh
   - Flash rollback script
   - Reboot

4. If TWRP is inaccessible:
   - Boot into fastboot mode (Volume Down + Power)
   - Connect to PC
   - Run: fastboot flash boot /path/to/backup/boot.img
   - Run: fastboot flash system /path/to/backup/system.img
   - Run: fastboot reboot
```

---

## 9. Testing Checklist

Before releasing the self-flashing installer:

### Device Compatibility Testing
- [ ] Google Pixel 6/7/8 installation success
- [ ] OnePlus 9/10/11 installation success
- [ ] Xiaomi Mi 11/12/13 installation success
- [ ] Samsung Galaxy S22/S23 installation success

### Installation Process Testing
- [ ] Installer app installs and runs correctly
- [ ] Root detection works on Magisk 26.0+
- [ ] Bootloader unlock detection works
- [ ] Storage space check works correctly
- [ ] Download completes successfully
- [ ] SHA256 verification works
- [ ] Backup creation succeeds
- [ ] Recovery reboot works
- [ ] TWRP installation completes
- [ ] QWAMOS boots successfully

### Rollback Testing
- [ ] Automatic rollback triggers after 3 boot failures
- [ ] Manual rollback from TWRP succeeds
- [ ] User data is preserved during rollback
- [ ] Device returns to working Android state

### Safety Testing
- [ ] Battery check prevents installation at low battery
- [ ] Installer aborts if backup fails
- [ ] Installer aborts if signature verification fails
- [ ] Device does not brick if power loss occurs mid-install
- [ ] TWRP remains accessible after failed QWAMOS boot

---

## 10. User Documentation

### 10.1 Installation Guide

**QWAMOS Self-Flashing Installation Guide**

**Prerequisites:**
1. Unlocked bootloader (see manufacturer instructions)
2. Root access via Magisk 26.0+
3. TWRP 3.7+ or OrangeFox Recovery installed
4. 70%+ battery charge
5. 50GB+ free storage

**Installation Steps:**

1. **Download QWAMOS Installer**
   - Download from: https://github.com/Dezirae-Stark/QWAMOS/releases
   - Install APK: `QWAMOSInstaller.apk`

2. **Launch Installer**
   - Open QWAMOS Installer app
   - Grant root permissions when prompted
   - Read and accept warnings

3. **Pre-Installation Checks**
   - App will verify device compatibility
   - App will check bootloader unlock status
   - App will verify storage space
   - App will check battery level

4. **Automatic Installation**
   - Tap "Install QWAMOS"
   - Installer will:
     - Download QWAMOS package (~3GB)
     - Verify package integrity
     - Create backup of current system
     - Copy installer to recovery
     - Reboot to recovery mode

5. **Recovery Installation**
   - Device will automatically boot to TWRP
   - Installation will proceed automatically
   - This takes 15-30 minutes
   - Device will reboot when complete

6. **First Boot**
   - First boot takes 3-5 minutes
   - QWAMOS will initialize
   - Android VM will be configured
   - Setup wizard will guide you through initial configuration

**If Something Goes Wrong:**
- Device automatically rolls back to Android after 3 failed boots
- Manual rollback available from TWRP (see Emergency Recovery section)
- Your data backup is stored in /sdcard/QWAMOS-Backup/

---

## 11. Conclusion

This self-flashing installer specification provides a comprehensive, safe, and user-friendly method for installing QWAMOS directly from the mobile device without requiring PC connectivity. The implementation includes:

✓ **Root-based installer app** with automated download, verification, and backup
✓ **TWRP-compatible flashable ZIP** with Kyber-1024 signature verification
✓ **Automatic rollback mechanisms** to prevent bricking
✓ **Manual rollback procedures** for emergency recovery
✓ **Comprehensive safety checks** at every step
✓ **Device compatibility verification** for supported hardware

This approach enables seamless QWAMOS installation while maintaining maximum safety and providing robust recovery options in case of any issues.
