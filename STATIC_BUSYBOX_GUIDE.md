# How to Obtain Static BusyBox for QWAMOS

**Problem:** Termux's busybox is dynamically linked against Android libraries and won't work in a standard Linux kernel environment.

**Solution:** We need a statically-linked busybox binary for ARM64.

---

## Option 1: Compile Static BusyBox (RECOMMENDED)

### On a Linux Desktop/Server with ARM64 cross-compilation:

```bash
# Install cross-compilation tools
sudo apt-get install gcc-aarch64-linux-gnu make wget

# Download BusyBox source
cd /tmp
wget https://busybox.net/downloads/busybox-1.36.1.tar.bz2
tar xjf busybox-1.36.1.tar.bz2
cd busybox-1.36.1

# Configure for static compilation
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig

# Enable static linking
sed -i 's/# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config

# Build
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)

# Result: busybox binary (statically linked, ~1MB)
file busybox
# Output: busybox: ELF 64-bit LSB executable, ARM aarch64, version 1 (GNU/Linux),
#         statically linked, stripped

# Transfer to Android device
adb push busybox /sdcard/Download/busybox_static
```

### Then on Termux:
```bash
cp /sdcard/Download/busybox_static ~/QWAMOS/initramfs/bin/busybox
chmod +x ~/QWAMOS/initramfs/bin/busybox
```

---

## Option 2: Extract from Alpine Linux Docker Image

### On a Linux system with Docker:

```bash
# Pull Alpine Linux ARM64 image
docker pull arm64v8/alpine:latest

# Create container and extract busybox
docker create --name alpine-extract arm64v8/alpine:latest
docker cp alpine-extract:/bin/busybox ./busybox_static
docker rm alpine-extract

# Verify it's static
file busybox_static
# Should show: statically linked

# Transfer to Android
adb push busybox_static /sdcard/Download/
```

---

## Option 3: Download Pre-compiled Static BusyBox

### From Reliable GitHub Repositories:

Try these repositories (check for recent releases):

1. **https://github.com/robxu9/bash-static** (includes static busybox)
2. **https://github.com/Andrew-Pynch/static-bins** (various static binaries)
3. **https://github.com/therealsaumil/static-arm-bins** (ARM static binaries)

Example:
```bash
cd ~/QWAMOS/initramfs/bin
# Try finding a working busybox-aarch64 link from above repos
wget -O busybox_static <URL>
chmod +x busybox_static
file busybox_static  # Verify it says "statically linked"
```

---

## Option 4: Use Andronix Debian (If Available)

You mentioned having Andronix Debian with busybox. Let's check if it's static:

```bash
# In Andronix Debian environment
file /bin/busybox

# If it shows "statically linked":
cp /bin/busybox ~/QWAMOS/initramfs/bin/busybox_static
```

---

## Option 5: Compile in Termux with Musl

### Install musl cross-compiler in Termux:

```bash
pkg install musl musl-dev clang

# Download busybox
cd /tmp
wget https://busybox.net/downloads/busybox-1.36.1.tar.bz2
tar xjf busybox-1.36.1.tar.bz2
cd busybox-1.36.1

# Configure
make defconfig
sed -i 's/# CONFIG_STATIC is not set/CONFIG_STATIC=y/' .config
sed -i 's/CONFIG_CROSS_COMPILER_PREFIX=""/CONFIG_CROSS_COMPILER_PREFIX="musl-"/' .config

# Build
make CC=musl-gcc -j4

# If successful, you'll have a static busybox
```

**Note:** This may fail due to Termux/Android limitations. Linux desktop compilation (Option 1) is most reliable.

---

## Verification Steps

After obtaining busybox, verify it's properly static:

```bash
cd ~/QWAMOS/initramfs/bin

# Check file type
file busybox_static
# Must show: "statically linked" (NOT "dynamically linked")

# Check for library dependencies (should show none)
readelf -d busybox_static 2>&1 | grep NEEDED
# Should return nothing or error (no dynamic libraries)

# Test it runs
./busybox_static --help
# Should show BusyBox help

# Check size (static busybox is typically 1-2MB)
ls -lh busybox_static
```

---

## Integration Steps (Once You Have Static BusyBox)

1. **Replace dynamic busybox:**
   ```bash
   cd ~/QWAMOS/initramfs
   rm bin/busybox
   cp /path/to/busybox_static bin/busybox
   chmod +x bin/busybox
   ```

2. **Reinstall symlinks:**
   ```bash
   cd ~/QWAMOS/initramfs
   bin/busybox --install -s bin/
   ```

3. **Rebuild initramfs:**
   ```bash
   cd ~/QWAMOS/initramfs
   find . | cpio -o -H newc | gzip > ../kernel/initramfs_static.cpio.gz
   ```

4. **Test in QEMU:**
   ```bash
   cd ~/QWAMOS
   qemu-system-aarch64 \
       -M virt -cpu cortex-a57 -m 2048 \
       -kernel kernel/Image \
       -initrd kernel/initramfs_static.cpio.gz \
       -append "console=ttyAMA0 rootwait" \
       -nographic
   ```

5. **Expected Result:**
   - Kernel boots
   - QWAMOS ASCII banner displays
   - Interactive shell prompt appears
   - Commands work: `ls`, `ps`, `mount`, etc.

---

## Common Issues

### Issue: "cannot execute binary file: Exec format error"
**Cause:** Wrong architecture (x86_64 instead of aarch64)
**Solution:** Ensure busybox is ARM64/aarch64

### Issue: "No such file or directory" when executing
**Cause:** Still dynamically linked, missing /system/bin/linker64
**Solution:** Get a truly static binary

### Issue: Busybox runs but commands don't work
**Cause:** Symlinks not created
**Solution:** Run `busybox --install -s bin/`

---

## Recommended Approach for You

Since you're working in Termux on Android, the **easiest approach** is:

1. **Use a Linux desktop/laptop** to compile static busybox (Option 1)
2. **Transfer via USB** or cloud storage to your Android device
3. **Copy to QWAMOS initramfs** and continue

**Estimated Time:** 15-20 minutes on Linux desktop

Alternatively, if you have access to an **x86_64 Linux server** or **cloud VM**, you can:
- SSH into it
- Compile static busybox for ARM64
- Download to your Android device
- Continue QWAMOS development

---

## Current QWAMOS Status

**What's Complete:**
- ✅ Kernel configuration (production-ready)
- ✅ Kernel boots in QEMU
- ✅ Initramfs structure (100%)
- ✅ Init script (QWAMOS banner, system info)
- ⏳ Static busybox (only blocker to Phase 2 completion)

**What's Left for Phase 2:**
1. Get static busybox binary (this guide)
2. Replace dynamic busybox (5 minutes)
3. Rebuild initramfs (1 minute)
4. Test interactive shell (5 minutes)
5. **Phase 2 COMPLETE!** 🎉

---

**Last Updated:** 2025-11-01
**Status:** Awaiting static busybox binary
**Estimated Time to Phase 2 Completion:** 15-30 minutes after obtaining static binary
