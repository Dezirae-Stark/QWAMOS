# QWAMOS Build System

This directory contains the build system and toolchain for compiling QWAMOS.

## Quick Start

```bash
# 1. Run toolchain setup (one-time)
cd ~/QWAMOS
./build/scripts/setup_toolchain.sh

# 2. Load build environment
source build/env.sh

# 3. Build components
./build/scripts/build_all.sh
```

## Directory Structure

- `toolchain/` - Cross-compilation toolchain, NDK, crypto libraries
- `scripts/` - Build automation scripts
- `configs/` - Build configuration files
- `tools/` - Custom build tools
- `env.sh` - Environment setup script (source this!)

## Installed Tools

After setup, you'll have:

**Compilers:**
- Clang 21.1.3 (supports ARM64 natively)
- LLVM toolchain (ar, nm, objcopy, strip, etc.)

**Build Tools:**
- Make 4.4.1
- CMake 4.1.2
- Binutils 2.44

**Virtualization:**
- QEMU 8.2.10 (aarch64 and x86-64 system emulation)

**Cryptography:**
- OpenSSL 3.x
- libsodium (ChaCha20-Poly1305)
- liboqs (Kyber-1024 post-quantum crypto)

**Android:**
- Android NDK r27 (for native modules)

## Next Steps

After successful setup, configure and build components as outlined in docs/TECHNICAL_ARCHITECTURE.md
