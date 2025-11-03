# QWAMOS Setup Guide

**Complete instructions for building QWAMOS from source**

---

## 🎯 Overview

This guide walks you through setting up the QWAMOS build environment and downloading all required dependencies. The QWAMOS repository contains **source code only** (~50-100MB). Large dependencies are downloaded separately to keep the repository lightweight.

---

## 📋 Prerequisites

### Required Hardware
- ARM64 Android device (Snapdragon 8 Gen 3 recommended)
- 32GB+ free storage
- 8GB+ RAM recommended

### Required Software
- **Termux** (latest version from F-Droid)
- **proot-distro** (for VM creation)
- **Internet connection** (for downloading dependencies)

---

## 🚀 Quick Start

### 1. Clone QWAMOS Repository

```bash
# Install git
pkg install git

# Clone repository (~50-100MB)
cd ~
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS
```

### 2. Run Automated Setup Script

```bash
# This downloads and installs ALL dependencies
./build/scripts/setup_qwamos.sh
```

The script will:
1. ✅ Install Termux packages
2. ✅ Download Linux kernel 6.6 source (~150MB compressed)
3. ✅ Download U-Boot v2024.10 source (~30MB)
4. ✅ Download Android NDK r27 (~900MB compressed)
5. ✅ Download liboqs (post-quantum crypto library)
6. ✅ Install Python dependencies
7. ✅ Create VM base images with proot-distro
8. ✅ Download Llama 3.1 8B model (optional, 4.6GB)

**Total download:** ~3-6GB (depending on options)
**Total disk usage after build:** ~15-20GB

---

## 📦 Manual Setup (Advanced)

If you prefer to set up manually or the automated script fails:

### Step 1: Install Termux Packages

```bash
pkg update && pkg upgrade -y
pkg install -y git python clang make cmake wget curl \
    binutils pkg-config which tree qemu-system-aarch64 \
    busybox proot-distro
```

### Step 2: Download Build Dependencies

#### Linux Kernel Source
```bash
cd ~/QWAMOS/kernel
wget https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-6.6.tar.xz
tar -xf linux-6.6.tar.xz
mv linux-6.6 linux-6.6-source
rm linux-6.6.tar.xz
```

#### U-Boot Bootloader Source
```bash
cd ~/QWAMOS/bootloader
git clone --depth 1 --branch v2024.10 \
    https://github.com/u-boot/u-boot.git u-boot-source
```

#### Android NDK r27
```bash
cd ~/QWAMOS/build/toolchain
wget https://dl.google.com/android/repository/android-ndk-r27-linux.zip
unzip android-ndk-r27-linux.zip
mv android-ndk-r27 android-ndk
rm android-ndk-r27-linux.zip
```

#### liboqs (Post-Quantum Crypto)
```bash
cd ~/QWAMOS/build/toolchain
git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
cd liboqs
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install pycryptodome cryptography requests \
    flask fastapi uvicorn pyyaml jinja2
```

### Step 4: Create VM Base Images

```bash
# Install Debian for VMs
proot-distro install debian

# Create QWAMOS VM directories
mkdir -p ~/QWAMOS/vms/{gateway-1,workstation-1,kali-1,android-vm,vault-vm}
```

### Step 5: Download AI Models (Optional)

#### Llama 3.1 8B for Kali GPT
```bash
cd ~/QWAMOS/ai/kali_gpt/models

# Download from Hugging Face (requires account + token)
wget https://huggingface.co/TheBloke/Llama-3.1-8B-Instruct-GGUF/resolve/main/llama-3.1-8b-instruct.Q4_K_M.gguf

# Alternative: Download via llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git /tmp/llama.cpp
cd /tmp/llama.cpp
./download-model.sh llama-3.1-8b-instruct
cp models/llama-3.1-8b-instruct.gguf ~/QWAMOS/ai/kali_gpt/models/
```

**Note:** AI models are OPTIONAL. Kali GPT will not work without the model, but Claude and ChatGPT (API-based) will work fine.

---

## 🔨 Building QWAMOS

### Build Bootloader (U-Boot)

```bash
cd ~/QWAMOS/bootloader/u-boot-source
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- qemu_arm64_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- -j$(nproc)
```

**Output:** `u-boot` binary (~5MB)

### Build Kernel

```bash
cd ~/QWAMOS/kernel/linux-6.6-source

# Apply QWAMOS configuration
bash ../qwamos_config.sh

# Build kernel (WARNING: Takes 2-4 hours on ARM64)
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- -j$(nproc)
```

**Output:** `arch/arm64/boot/Image` (~32MB)

**Note:** Due to Clang/glibc incompatibility in Termux, kernel compilation may fail. Use prebuilt Debian kernel or compile on Linux PC.

### Build Initramfs

```bash
cd ~/QWAMOS/initramfs
./build_initramfs.sh
```

**Output:** `initramfs.cpio.gz` (~1-2MB)

### Test Boot Chain (QEMU)

```bash
cd ~/QWAMOS
./build/scripts/test_boot.sh
```

This boots U-Boot → Kernel → Initramfs in QEMU.

---

## 🔐 Post-Quantum Crypto Setup

Test the Kyber-1024 implementation:

```bash
cd ~/QWAMOS/crypto/pq
python3 test_kyber_integration.py
```

**Expected:** All 6 tests pass

Create encrypted volume:

```bash
python3 qwamos_pq_crypto.py create test.qvol 100MB mypassword
```

---

## 🌐 Network Isolation Setup

### Extract InviZible Pro Binaries

```bash
cd ~/QWAMOS/build/scripts
bash extract_invizible_binaries.sh
```

This extracts:
- `tor` (ARM64 binary)
- `i2pd` (Purple I2P)
- `dnscrypt-proxy` (DNS encryption)

### Test Network Controllers

```bash
cd ~/QWAMOS/network/tests
python3 test_controllers_mock.py
```

**Expected:** 9/10 tests pass (systemd test requires root)

---

## 🤖 AI Integration Setup

### Configure AI Services

```bash
# Test AI Manager
cd ~/QWAMOS/ai
python3 ai_manager.py status

# Enable Kali GPT (requires model downloaded)
python3 ai_manager.py enable kali-gpt

# Enable Claude (requires API key)
python3 ai_manager.py enable claude --api-key sk-ant-YOUR_KEY

# Enable ChatGPT (requires API key)
python3 ai_manager.py enable chatgpt --api-key sk-proj-YOUR_KEY
```

### Test AI Controllers

```bash
# Test Kali GPT (local)
cd ~/QWAMOS/ai/kali_gpt
python3 kali_gpt_controller.py test

# Test Claude (via Tor)
cd ~/QWAMOS/ai/claude
python3 claude_controller.py test --api-key sk-ant-YOUR_KEY

# Test ChatGPT (via Tor)
cd ~/QWAMOS/ai/chatgpt
python3 chatgpt_controller.py test --api-key sk-proj-YOUR_KEY
```

---

## 📊 Disk Space Requirements

| Component | Download Size | Installed Size |
|-----------|--------------|----------------|
| QWAMOS Repository | 50-100MB | 100-200MB |
| Linux Kernel Source | 150MB | 1.5GB |
| U-Boot Source | 30MB | 200MB |
| Android NDK | 900MB | 3.5GB |
| liboqs | 5MB | 50MB |
| Python Dependencies | 50MB | 200MB |
| VM Base Images | 500MB | 2-5GB (per VM) |
| Llama 3.1 8B (optional) | 4.6GB | 4.6GB |
| **TOTAL** | **~6-7GB** | **15-25GB** |

---

## ⚠️ Common Issues

### "Permission denied" during build

**Solution:** Some operations require root. Use `su` or compile on rooted device.

### "Out of memory" during kernel build

**Solution:**
- Reduce parallel jobs: `make -j2` instead of `make -j$(nproc)`
- Close other apps to free RAM
- Enable swap: `fallocate -l 4G /swapfile && mkswap /swapfile && swapon /swapfile`

### "Cannot find clang" or "cc1: not found"

**Solution:**
```bash
pkg reinstall clang llvm binutils
export CC=clang
export CXX=clang++
```

### Git clone fails with "repository too large"

**Solution:** Repository should be ~50-100MB. If larger, use shallow clone:
```bash
git clone --depth 1 https://github.com/Dezirae-Stark/QWAMOS.git
```

### Tor/I2P/DNSCrypt binaries not working

**Solution:** Extract from InviZible Pro APK:
```bash
cd ~/QWAMOS/build/scripts
bash extract_invizible_binaries.sh
```

---

## 🎓 Next Steps

After setup is complete:

1. ✅ Read **docs/ARCHITECTURE.md** - Understand QWAMOS design
2. ✅ Read **docs/PHASE5_INTEGRATION_CHECKLIST.md** - Network setup
3. ✅ Read **docs/PHASE6_AI_ASSISTANTS_INTEGRATION.md** - AI setup
4. ✅ Test boot chain: `./build/scripts/test_boot.sh`
5. ✅ Create VMs: `./hypervisor/scripts/vm_creator.py`
6. ✅ Run integration tests: `./build/scripts/run_tests.sh`

---

## 📞 Support

- **Issues:** https://github.com/Dezirae-Stark/QWAMOS/issues
- **Documentation:** https://github.com/Dezirae-Stark/QWAMOS/tree/master/docs
- **Discussions:** https://github.com/Dezirae-Stark/QWAMOS/discussions

---

## 📝 License

QWAMOS is licensed under GPL v3. See LICENSE file for details.

---

**Last Updated:** 2025-11-03
**QWAMOS Version:** v0.6.0-alpha
**Phase Status:** Phase 6 @ 30% (AI Integration)
