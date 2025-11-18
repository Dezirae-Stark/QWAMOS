# Installation & Setup Guide

**[← Back to Home](Home)**

---

## Prerequisites

### Device Requirements

**Minimum Specifications:**
- **CPU:** ARM64 (ARMv8-A or newer), 4+ cores
- **RAM:** 4GB minimum, 8GB+ recommended
- **Storage:** 64GB minimum, 128GB+ recommended
- **Android Version:** 10+ (API level 29+)

**Recommended Specifications:**
- **CPU:** Snapdragon 8 Gen 2/3 or equivalent, 8+ cores
- **RAM:** 12GB+
- **Storage:** 256GB+ (for multiple VMs)
- **Android Version:** 13+ (API level 33+)

**For KVM Hardware Acceleration:**
- ARM CPU with virtualization extensions (EL2 support)
- Custom kernel with `CONFIG_KVM=y` and `CONFIG_KVM_ARM=y`
- `/dev/kvm` device accessible
- See [FAQ](FAQ) for device-specific compatibility

### Software Requirements

**Required:**
- [Termux](https://f-droid.org/en/packages/com.termux/) (from F-Droid, **not** Google Play)
- Git
- Python 3.9+
- Bash

**Optional:**
- [InviZible Pro](https://f-droid.org/en/packages/pan.alexander.tordnscrypt.stable/) (for anonymous gateway)
- Root access (for KVM, optional otherwise)
- Custom ROM with KVM support (for hardware acceleration)

---

## Installation Methods

QWAMOS supports three installation methods:

1. **[Termux (Recommended)](#method-1-termux-installation)** - Works on all devices, no root required
2. **[Rooted Device](#method-2-rooted-device-with-kvm)** - Better performance with KVM
3. **[Custom ROM](#method-3-custom-rom-integration)** - Full system integration

---

## Method 1: Termux Installation

**Best for:** Non-rooted devices, quick setup, portable installation

### Step 1: Install Termux

1. Download Termux from [F-Droid](https://f-droid.org/en/packages/com.termux/)
   - ⚠️ **DO NOT use Google Play version** (outdated, broken)

2. Grant storage permissions:
   ```bash
   termux-setup-storage
   ```

3. Update package repository:
   ```bash
   pkg update && pkg upgrade
   ```

### Step 2: Install Dependencies

```bash
# Install core packages
pkg install git python clang make binutils

# Install QEMU (for VM emulation)
pkg install qemu-system-aarch64 qemu-utils

# Install optional packages
pkg install curl wget nano vim
```

### Step 3: Clone QWAMOS

```bash
# Navigate to home directory
cd ~

# Clone QWAMOS repository
git clone https://github.com/Dezirae-Stark/QWAMOS.git

# Enter QWAMOS directory
cd QWAMOS
```

### Step 4: Run Compatibility Check

```bash
# Check system compatibility
chmod +x scripts/check_compatibility.sh
./scripts/check_compatibility.sh
```

**Expected Output:**
```
================================================================================
QWAMOS Compatibility Check
================================================================================

✅ CPU: ARM64 detected (8 cores)
✅ RAM: 8192 MB (sufficient)
✅ Storage: 128 GB available
✅ Android Version: 13 (API 33)
⚠️  KVM: Not available (using QEMU fallback)
✅ Python: 3.11.6
✅ QEMU: 8.1.0

Overall Status: COMPATIBLE ✅
Recommended mode: QEMU (software emulation)
```

### Step 5: Initialize QWAMOS

```bash
# Run initialization script
./scripts/init_qwamos.sh
```

This script will:
- Create VM storage directories
- Set up networking configuration
- Generate initial encryption keys
- Configure firewall rules
- Install Python dependencies

**Expected Output:**
```
[1/6] Creating directories...
[2/6] Configuring network...
[3/6] Generating Kyber-1024 keys...
[4/6] Setting up firewall...
[5/6] Installing Python packages...
[6/6] Finalizing configuration...

✅ QWAMOS initialized successfully!
```

### Step 6: Create Your First VM

```bash
# Create a secure browser VM
./scripts/create_vm.sh --name secure-browser --type browser --size 10G
```

**Parameters:**
- `--name`: VM identifier (alphanumeric, no spaces)
- `--type`: VM template (browser, messaging, development, generic)
- `--size`: Disk image size (e.g., 10G, 20G, 50G)

**Available Templates:**
- `browser`: Minimal browser environment (Firefox ESR)
- `messaging`: Secure messaging apps (Signal, Element)
- `development`: Development tools (Git, Python, Node.js)
- `generic`: Blank Alpine Linux installation

**VM Creation Process:**
```
Creating VM: secure-browser
  Type: browser
  Size: 10 GB

[1/5] Allocating disk image...
[2/5] Installing Alpine Linux base...
[3/5] Configuring network (10.8.0.2)...
[4/5] Installing Firefox ESR...
[5/5] Encrypting with Kyber-1024...

✅ VM created successfully!

To start: ./vm/start_vm.sh secure-browser
To connect: ./vm/connect_vm.sh secure-browser
```

### Step 7: Start the VM

```bash
# Start VM in background
./vm/start_vm.sh secure-browser

# Expected output:
Starting VM: secure-browser
  Mode: QEMU (TCG emulation)
  RAM: 2048 MB
  CPUs: 4
  Network: 10.8.0.2

✅ VM started (PID: 12345)
```

### Step 8: Connect to the VM

```bash
# Connect via SSH
./vm/connect_vm.sh secure-browser

# Or manually:
ssh root@10.8.0.2 -p 2222
# Password: (generated during VM creation, stored in ~/.qwamos/vms/secure-browser/credentials.txt)
```

**Inside the VM:**
```bash
# Check VM status
hostname
# Output: secure-browser

# Verify internet connectivity
curl -I https://check.torproject.org
# Output: 200 OK (if Tor gateway configured)

# Install additional packages
apk add firefox-esr
```

---

## Method 2: Rooted Device with KVM

**Best for:** Maximum performance, hardware-accelerated VMs

### Prerequisites

- Rooted Android device (Magisk recommended)
- Custom kernel with KVM support
- Termux with root access

### Step 1: Verify KVM Support

```bash
# Check if /dev/kvm exists
ls -l /dev/kvm

# If not found, check kernel config
zcat /proc/config.gz | grep CONFIG_KVM
# Should show: CONFIG_KVM=y, CONFIG_KVM_ARM_HOST=y

# Load KVM module (if not auto-loaded)
su
modprobe kvm
modprobe kvm-arm
```

### Step 2: Set KVM Permissions

```bash
# Grant Termux access to /dev/kvm
su
chmod 666 /dev/kvm

# Or add Termux UID to kvm group
groupadd kvm
chown root:kvm /dev/kvm
chmod 660 /dev/kvm
usermod -aG kvm $(whoami)
```

### Step 3: Install QWAMOS (Same as Method 1)

Follow Steps 2-5 from Method 1.

### Step 4: Create KVM-Accelerated VM

```bash
# Create VM with KVM flag
./scripts/create_vm.sh --name fast-browser --type browser --size 10G --kvm
```

**Performance Comparison:**
| Metric | QEMU (Software) | KVM (Hardware) |
|--------|----------------|----------------|
| VM Boot Time | 8-30 seconds | <2 seconds |
| CPU Performance | 5-15% native | 85-95% native |
| Battery Life | 2-3 hours | 6-7 hours |

### Step 5: Validate KVM Acceleration

```bash
# Check if VM is using KVM
./scripts/vm_info.sh fast-browser | grep Acceleration

# Expected output:
Acceleration: KVM (hardware)
```

---

## Method 3: Custom ROM Integration

**Best for:** Full system integration, maximum security

### Supported ROMs

- [LineageOS](https://lineageos.org/) with custom kernel
- [CalyxOS](https://calyxos.org/) (experimental)
- [GrapheneOS](https://grapheneos.org/) (experimental, limited support)

### Step 1: Flash Custom ROM with KVM Kernel

**Example: LineageOS on OnePlus 12**

1. Unlock bootloader
2. Flash LineageOS recovery
3. Flash LineageOS ROM
4. Flash KVM-enabled kernel
5. Reboot

See ROM-specific guides for your device.

### Step 2: Install QWAMOS as System App

```bash
# Clone QWAMOS to system partition
su
mount -o remount,rw /system
git clone https://github.com/Dezirae-Stark/QWAMOS.git /system/qwamos

# Create system service
cp /system/qwamos/systemd/qwamos.service /system/etc/init.d/
chmod +x /system/etc/init.d/qwamos.service

# Enable on boot
update-rc.d qwamos defaults
```

### Step 3: Configure System Integration

```bash
# Grant QWAMOS system permissions
su
setenforce 0  # Temporarily disable SELinux
chcon -R u:object_r:system_file:s0 /system/qwamos

# Add QWAMOS to PATH
echo 'export PATH=$PATH:/system/qwamos/bin' >> /system/etc/profile

# Reboot
reboot
```

---

## Anonymous Gateway Setup (InviZible Pro)

**Anonymize all VM traffic** through Tor, I2P, and DNSCrypt.

### Step 1: Install InviZible Pro

Download from [F-Droid](https://f-droid.org/en/packages/pan.alexander.tordnscrypt.stable/)

### Step 2: Configure InviZible Pro

1. Open InviZible Pro
2. Enable **Tor**, **I2P**, and **DNSCrypt**
3. Go to Settings → **VPN Mode** → Enable
4. Go to Settings → **Root Mode** → Enable (if rooted)

### Step 3: Configure QWAMOS Gateway

```bash
# Edit gateway configuration
nano ~/.qwamos/config/gateway.conf
```

**gateway.conf:**
```ini
[gateway]
mode = invizible
tor_proxy = 127.0.0.1:9050
i2p_proxy = 127.0.0.1:4444
dnscrypt = 127.0.0.1:5354

[firewall]
default_policy = DROP
allow_tor = true
allow_i2p = true
allow_direct = false

[per_vm_rules]
secure-browser = tor
messaging-vm = tor
dev-vm = direct  # Allow direct internet for development
```

### Step 4: Start Gateway

```bash
# Start QWAMOS gateway service
./gateway/start_gateway.sh
```

**Expected Output:**
```
Starting QWAMOS Gateway...
  Tor: 127.0.0.1:9050 ✅
  I2P: 127.0.0.1:4444 ✅
  DNSCrypt: 127.0.0.1:5354 ✅
  Firewall: iptables configured ✅

✅ Gateway running
```

### Step 5: Test Anonymous Connection

```bash
# Connect to VM
./vm/connect_vm.sh secure-browser

# Test Tor connection
curl https://check.torproject.org/api/ip
# Expected output: {"IsTor":true,"IP":"..."}

# Test I2P connection
curl -x http://127.0.0.1:4444 http://stats.i2p/
# Expected output: I2P Router Console
```

---

## Kyber + ChaCha20 Encryption Setup

All VM disk images are encrypted by default with **Kyber-1024 key encapsulation** and **ChaCha20-Poly1305 AEAD encryption**.

### Encryption Architecture

```
User Passphrase
       ↓
Kyber-1024 KEM (Key Encapsulation)
       ↓
Wrapped Key (Quantum-Resistant)
       ↓
ChaCha20-Poly1305 AEAD Encryption
       ↓
Encrypted VM Disk Image
```

### Step 1: Generate Master Key

```bash
# Generate Kyber-1024 master key
./crypto/generate_master_key.sh

# You will be prompted for a strong passphrase:
Enter master passphrase: ****************
Confirm passphrase: ****************

Generating Kyber-1024 keypair...
  Public key: ~/.qwamos/keys/master.pub
  Private key: ~/.qwamos/keys/master.key

✅ Master key generated
```

**Passphrase Requirements:**
- Minimum 20 characters
- Uppercase + lowercase + numbers + symbols
- No dictionary words
- Use Diceware for strong passphrases

**Example Strong Passphrase:**
```
correct-horse-battery-staple-9527-Xylophone!
```

### Step 2: Encrypt VM Disk Image

**Automatic Encryption** (during VM creation):
```bash
# VMs are encrypted by default
./scripts/create_vm.sh --name encrypted-vm --type generic --size 10G
# Automatically encrypted with master key
```

**Manual Encryption** (existing VM):
```bash
# Encrypt existing VM
./crypto/encrypt_vm.sh --vm encrypted-vm --passphrase-from-master
```

### Step 3: Decrypt and Mount VM

```bash
# Start VM (automatically decrypts)
./vm/start_vm.sh encrypted-vm
# Prompts for master passphrase if not cached

# Manual decrypt (for inspection)
./crypto/decrypt_vm.sh --vm encrypted-vm --output /tmp/encrypted-vm.img
```

### Step 4: Re-Key VM (Rotate Encryption Keys)

```bash
# Rotate keys every 90 days (recommended)
./crypto/rekey_vm.sh --vm encrypted-vm

# Generates new Kyber keypair
# Re-encrypts VM with new key
# Old keys securely deleted
```

---

## VeraCrypt Container Integration

**Optional:** Use VeraCrypt containers for additional encryption layer.

### Step 1: Install VeraCrypt

```bash
# Install VeraCrypt CLI (in Termux)
pkg install veracrypt
```

### Step 2: Create VeraCrypt Container

```bash
# Create 20GB container
veracrypt --text --create ~/QWAMOS/containers/secure-storage.vc \
  --size 20G \
  --encryption AES-256 \
  --hash SHA-512 \
  --filesystem ext4 \
  --password "your-strong-passphrase"
```

### Step 3: Mount VeraCrypt Container

```bash
# Mount container
mkdir -p ~/QWAMOS/mnt/secure-storage
veracrypt --text --mount ~/QWAMOS/containers/secure-storage.vc ~/QWAMOS/mnt/secure-storage

# Store VM disk images inside
cp ~/.qwamos/vms/*/disk.img ~/QWAMOS/mnt/secure-storage/
```

### Step 4: Auto-Mount on Boot

```bash
# Edit startup script
nano ~/.qwamos/scripts/startup.sh

# Add:
veracrypt --text --mount ~/QWAMOS/containers/secure-storage.vc ~/QWAMOS/mnt/secure-storage \
  --password-from-file ~/.qwamos/secrets/veracrypt.pass
```

---

## Troubleshooting

### Issue: VM Won't Start

**Symptom:** `./vm/start_vm.sh` fails with error

**Solutions:**

1. **Check QEMU installation:**
   ```bash
   qemu-system-aarch64 --version
   # Should output version number
   ```

2. **Check disk image exists:**
   ```bash
   ls -lh ~/.qwamos/vms/*/disk.img
   ```

3. **Check available RAM:**
   ```bash
   free -h
   # Ensure sufficient RAM (2GB+ free)
   ```

4. **Check logs:**
   ```bash
   cat ~/.qwamos/logs/qemu-*.log
   ```

### Issue: KVM Not Available

**Symptom:** `/dev/kvm` not found

**Solutions:**

1. **Verify kernel KVM support:**
   ```bash
   zcat /proc/config.gz | grep CONFIG_KVM
   # Should show CONFIG_KVM=y
   ```

2. **Load KVM module:**
   ```bash
   su
   modprobe kvm kvm-arm
   ```

3. **Check CPU virtualization support:**
   ```bash
   cat /proc/cpuinfo | grep -i virt
   # Should show virtualization flags
   ```

4. **Flash custom kernel:** See [FAQ](FAQ) for device-specific guides

### Issue: Gateway Not Working

**Symptom:** VM has no internet, or not using Tor

**Solutions:**

1. **Check InviZible Pro status:**
   - Open InviZible Pro
   - Ensure Tor, I2P, DNSCrypt are running (green indicators)

2. **Test Tor proxy:**
   ```bash
   curl -x socks5h://127.0.0.1:9050 https://check.torproject.org/api/ip
   # Should return {"IsTor":true}
   ```

3. **Check firewall rules:**
   ```bash
   su
   iptables -L -n -v | grep QWAMOS
   ```

4. **Restart gateway:**
   ```bash
   ./gateway/stop_gateway.sh
   ./gateway/start_gateway.sh
   ```

### Issue: Slow VM Performance

**Symptom:** VM is unusably slow

**Solutions:**

1. **Enable KVM** (if available): See Method 2

2. **Reduce VM RAM:**
   ```bash
   # Edit VM config
   nano ~/.qwamos/vms/*/config.ini
   # Change: ram = 1024  (instead of 2048)
   ```

3. **Close background apps:** Free up host RAM

4. **Disable graphics acceleration:**
   ```bash
   # Edit VM config
   nano ~/.qwamos/vms/*/config.ini
   # Change: graphics = none
   ```

### Issue: Encryption Key Lost

**Symptom:** Cannot decrypt VM, passphrase not working

**Solutions:**

1. **Check key backup:**
   ```bash
   ls ~/.qwamos/keys/backup/
   ```

2. **Try recovery passphrase:**
   - Check `~/.qwamos/recovery/passphrase.txt` (if backup enabled)

3. **No backup = permanent data loss**
   - ⚠️ **Kyber-1024 cannot be brute-forced**
   - VM is permanently inaccessible without key
   - Prevention: Enable key backup during setup

---

## Post-Installation Steps

### 1. Create Additional VMs

```bash
# Messaging VM
./scripts/create_vm.sh --name messaging --type messaging --size 5G

# Development VM
./scripts/create_vm.sh --name devenv --type development --size 30G

# Disposable VM (auto-deletes after use)
./scripts/create_vm.sh --name temp --type generic --size 5G --disposable
```

### 2. Configure Panic Triggers

```bash
# Enable volume button wipe
./panic/configure_triggers.sh --enable volume-buttons

# Enable SMS wipe
./panic/configure_triggers.sh --enable sms --keyword "EMERGENCY-WIPE-9527"

# Enable deadman timer (wipe if not checked-in for 48 hours)
./panic/configure_triggers.sh --enable deadman --timeout 48h
```

### 3. Enable Automatic Backups

```bash
# Backup VMs daily to external storage
./scripts/configure_backup.sh --destination /sdcard/QWAMOS-Backups --schedule daily
```

### 4. Harden Security Settings

```bash
# Enable all security features
./scripts/harden_security.sh --profile paranoid

# This enables:
# - Automatic VM snapshots before risky operations
# - Strict firewall (deny-all by default)
# - Mandatory PQC encryption for all VMs
# - Audit logging
# - Memory scrubbing on VM shutdown
```

---

## Next Steps

- **[Architecture](Architecture):** Understand how QWAMOS works internally
- **[Security Model](Security-Model):** Learn about threat model and defenses
- **[FAQ](FAQ):** Common questions and troubleshooting
- **[Developer Guide](Developer-Guide):** Contribute to QWAMOS

---

**[← Back to Home](Home)**
