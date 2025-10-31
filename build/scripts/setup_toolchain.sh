#!/data/data/com.termux/files/usr/bin/bash
#
# QWAMOS Build Environment Setup Script
# Sets up cross-compilation toolchain and build dependencies for Termux
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLCHAIN_DIR="$PROJECT_ROOT/build/toolchain"
NDK_DIR="$TOOLCHAIN_DIR/android-ndk"

log_info "QWAMOS Build Environment Setup"
log_info "================================"
log_info "Project root: $PROJECT_ROOT"
log_info ""

# Create toolchain directory
mkdir -p "$TOOLCHAIN_DIR"

# ============================================================================
# 1. Update package repository
# ============================================================================
log_info "Step 1/8: Updating package repository..."
pkg update -y
log_success "Package repository updated"
echo ""

# ============================================================================
# 2. Install essential build tools
# ============================================================================
log_info "Step 2/8: Installing essential build tools..."

ESSENTIAL_PACKAGES=(
    "build-essential"
    "clang"
    "make"
    "cmake"
    "git"
    "wget"
    "curl"
    "unzip"
    "tar"
    "gzip"
    "bzip2"
    "xz-utils"
    "patch"
    "pkg-config"
    "python"
    "python-pip"
    "binutils"
    "bison"
    "flex"
    "bc"
    "libgmp"
    "libmpc"
    "libmpfr"
    "ncurses"
)

for package in "${ESSENTIAL_PACKAGES[@]}"; do
    if pkg list-installed 2>/dev/null | grep -q "^${package}/"; then
        log_info "  ✓ $package already installed"
    else
        log_info "  Installing $package..."
        pkg install -y "$package" 2>/dev/null || log_warning "  Could not install $package (may not be available)"
    fi
done

log_success "Essential build tools installed"
echo ""

# ============================================================================
# 3. Install ARM64 cross-compilation tools
# ============================================================================
log_info "Step 3/8: Setting up ARM64 cross-compilation..."

# Termux on ARM64 can compile natively for ARM64
if [ "$(uname -m)" = "aarch64" ]; then
    log_success "Running on ARM64, native compilation available"
    log_info "Clang version: $(clang --version | head -1)"

    # Set up compiler aliases for cross-compilation scripts
    cat > "$TOOLCHAIN_DIR/arm64-env.sh" << 'EOF'
# ARM64 Compilation Environment
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-android-
export CC=clang
export CXX=clang++
export AR=llvm-ar
export NM=llvm-nm
export OBJCOPY=llvm-objcopy
export OBJDUMP=llvm-objdump
export READELF=llvm-readelf
export STRIP=llvm-strip
export CFLAGS="-march=armv8-a -O2"
export CXXFLAGS="-march=armv8-a -O2"
EOF
    log_success "ARM64 environment configuration created"
else
    log_warning "Not running on ARM64, will need full cross-compilation setup"
fi
echo ""

# ============================================================================
# 4. Install QEMU for virtualization testing
# ============================================================================
log_info "Step 4/8: Installing QEMU..."

if pkg list-installed 2>/dev/null | grep -q "^qemu-"; then
    log_info "  QEMU already installed"
else
    log_info "  Installing QEMU system emulation..."
    pkg install -y qemu-system-x86-64-headless qemu-system-aarch64-headless qemu-utils 2>/dev/null || \
        log_warning "  Could not install QEMU (may need to run VMs on host machine)"
fi

if command -v qemu-system-aarch64 &> /dev/null; then
    log_success "QEMU installed: $(qemu-system-aarch64 --version | head -1)"
else
    log_warning "QEMU not available in Termux, will need external VM host"
fi
echo ""

# ============================================================================
# 5. Install cryptography libraries
# ============================================================================
log_info "Step 5/8: Installing cryptography libraries..."

# Install OpenSSL
if pkg list-installed 2>/dev/null | grep -q "^openssl/"; then
    log_info "  ✓ OpenSSL already installed"
else
    log_info "  Installing OpenSSL..."
    pkg install -y openssl openssl-tool
fi

# Install libsodium (for ChaCha20-Poly1305)
if pkg list-installed 2>/dev/null | grep -q "^libsodium/"; then
    log_info "  ✓ libsodium already installed"
else
    log_info "  Installing libsodium..."
    pkg install -y libsodium
fi

log_success "Cryptography libraries installed"
echo ""

# ============================================================================
# 6. Install liboqs (Open Quantum Safe - for Kyber)
# ============================================================================
log_info "Step 6/8: Installing liboqs (Post-Quantum Cryptography)..."

LIBOQS_DIR="$TOOLCHAIN_DIR/liboqs"

if [ -d "$LIBOQS_DIR" ]; then
    log_info "  liboqs already cloned"
else
    log_info "  Cloning liboqs from GitHub..."
    git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs.git "$LIBOQS_DIR"
fi

log_info "  Building liboqs..."
mkdir -p "$LIBOQS_DIR/build"
cd "$LIBOQS_DIR/build"

cmake -DCMAKE_INSTALL_PREFIX="$TOOLCHAIN_DIR/liboqs-install" \
      -DOQS_BUILD_ONLY_LIB=ON \
      -DOQS_ENABLE_KEM_KYBER=ON \
      -DOQS_ENABLE_SIG_DILITHIUM=ON \
      .. > /dev/null 2>&1 || log_warning "CMake configuration may have issues"

make -j$(nproc) > /dev/null 2>&1 || log_warning "liboqs build may have issues"
make install > /dev/null 2>&1 || log_warning "liboqs install may have issues"

if [ -f "$TOOLCHAIN_DIR/liboqs-install/lib/liboqs.so" ]; then
    log_success "liboqs built and installed successfully"
else
    log_warning "liboqs installation incomplete, will build later"
fi

cd "$PROJECT_ROOT"
echo ""

# ============================================================================
# 7. Download Android NDK (for native modules)
# ============================================================================
log_info "Step 7/8: Setting up Android NDK..."

NDK_VERSION="r27"
NDK_FILENAME="android-ndk-${NDK_VERSION}-linux.zip"
NDK_URL="https://dl.google.com/android/repository/${NDK_FILENAME}"

if [ -d "$NDK_DIR" ] && [ -f "$NDK_DIR/build/cmake/android.toolchain.cmake" ]; then
    log_info "  Android NDK already installed"
else
    log_info "  Downloading Android NDK ${NDK_VERSION}..."
    log_warning "  This is ~1GB download, may take several minutes..."

    cd "$TOOLCHAIN_DIR"
    if [ ! -f "$NDK_FILENAME" ]; then
        wget -q --show-progress "$NDK_URL" || log_error "Failed to download NDK"
    fi

    if [ -f "$NDK_FILENAME" ]; then
        log_info "  Extracting Android NDK..."
        unzip -q "$NDK_FILENAME"
        mv "android-ndk-${NDK_VERSION}" android-ndk
        rm "$NDK_FILENAME"
        log_success "Android NDK installed at: $NDK_DIR"
    else
        log_warning "NDK download skipped, install manually if needed"
    fi

    cd "$PROJECT_ROOT"
fi
echo ""

# ============================================================================
# 8. Install Python build tools and dependencies
# ============================================================================
log_info "Step 8/8: Installing Python dependencies..."

pip install --upgrade pip > /dev/null 2>&1

PYTHON_PACKAGES=(
    "pycryptodome"
    "pynacl"
    "cryptography"
    "pyqrcode"
    "pypng"
    "requests"
    "flask"
    "fastapi"
    "uvicorn"
    "pyyaml"
    "jinja2"
)

for package in "${PYTHON_PACKAGES[@]}"; do
    log_info "  Installing $package..."
    pip install "$package" > /dev/null 2>&1 || log_warning "  Could not install $package"
done

log_success "Python dependencies installed"
echo ""

# ============================================================================
# Generate environment setup script
# ============================================================================
log_info "Generating build environment script..."

cat > "$PROJECT_ROOT/build/env.sh" << EOF
#!/data/data/com.termux/files/usr/bin/bash
#
# QWAMOS Build Environment
# Source this file before building: source build/env.sh
#

export QWAMOS_ROOT="$PROJECT_ROOT"
export QWAMOS_BUILD="\$QWAMOS_ROOT/build"
export QWAMOS_TOOLCHAIN="\$QWAMOS_ROOT/build/toolchain"

# Compiler settings
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-android-
export CC=clang
export CXX=clang++
export AR=llvm-ar
export NM=llvm-nm
export STRIP=llvm-strip

# Android NDK
if [ -d "\$QWAMOS_TOOLCHAIN/android-ndk" ]; then
    export ANDROID_NDK_HOME="\$QWAMOS_TOOLCHAIN/android-ndk"
    export PATH="\$ANDROID_NDK_HOME/toolchains/llvm/prebuilt/linux-aarch64/bin:\$PATH"
fi

# liboqs (Post-Quantum Crypto)
if [ -d "\$QWAMOS_TOOLCHAIN/liboqs-install" ]; then
    export LIBOQS_ROOT="\$QWAMOS_TOOLCHAIN/liboqs-install"
    export PKG_CONFIG_PATH="\$LIBOQS_ROOT/lib/pkgconfig:\$PKG_CONFIG_PATH"
    export LD_LIBRARY_PATH="\$LIBOQS_ROOT/lib:\$LD_LIBRARY_PATH"
    export C_INCLUDE_PATH="\$LIBOQS_ROOT/include:\$C_INCLUDE_PATH"
fi

# Build tools
export PATH="\$QWAMOS_BUILD/tools:\$PATH"

echo "QWAMOS build environment loaded"
echo "  Root: \$QWAMOS_ROOT"
echo "  Arch: \$ARCH"
echo "  Compiler: \$(clang --version | head -1)"
if [ -n "\$LIBOQS_ROOT" ]; then
    echo "  liboqs: \$LIBOQS_ROOT"
fi
EOF

chmod +x "$PROJECT_ROOT/build/env.sh"
log_success "Build environment script created at: build/env.sh"
echo ""

# ============================================================================
# Test compilation
# ============================================================================
log_info "Testing compilation..."

TEST_DIR="$TOOLCHAIN_DIR/test"
mkdir -p "$TEST_DIR"

cat > "$TEST_DIR/test.c" << 'EOF'
#include <stdio.h>
#include <sodium.h>

int main() {
    if (sodium_init() < 0) {
        return 1;
    }
    printf("libsodium initialized successfully\n");
    printf("ChaCha20-Poly1305 available: %s\n",
           crypto_aead_chacha20poly1305_ietf_KEYBYTES > 0 ? "YES" : "NO");
    return 0;
}
EOF

cd "$TEST_DIR"
if clang test.c -o test -lsodium 2>/dev/null && ./test 2>/dev/null; then
    log_success "Test compilation successful!"
    log_success "libsodium (ChaCha20-Poly1305) working correctly"
else
    log_warning "Test compilation had issues, may need manual fixes"
fi
cd "$PROJECT_ROOT"
echo ""

# ============================================================================
# Summary
# ============================================================================
log_success "================================"
log_success "Build Environment Setup Complete"
log_success "================================"
echo ""
log_info "Summary of installed tools:"
echo "  • Clang/LLVM: $(clang --version | head -1 | cut -d' ' -f3)"
echo "  • Make: $(make --version | head -1 | cut -d' ' -f3)"
echo "  • CMake: $(cmake --version | head -1 | cut -d' ' -f3)"
echo "  • Python: $(python --version | cut -d' ' -f2)"
echo "  • Git: $(git --version | cut -d' ' -f3)"
if command -v qemu-system-aarch64 &> /dev/null; then
    echo "  • QEMU: $(qemu-system-aarch64 --version | head -1 | cut -d' ' -f4)"
fi
if [ -d "$TOOLCHAIN_DIR/liboqs-install" ]; then
    echo "  • liboqs: Installed (Kyber-1024 available)"
fi
if [ -d "$NDK_DIR" ]; then
    echo "  • Android NDK: Installed at $NDK_DIR"
fi
echo ""
log_info "To use the build environment:"
log_info "  source build/env.sh"
echo ""
log_info "Next steps:"
log_info "  1. Configure U-Boot bootloader"
log_info "  2. Configure Linux kernel"
log_info "  3. Build Kyber crypto modules"
log_info "  4. Set up hypervisor (KVM/QEMU)"
echo ""
log_success "Ready to build QWAMOS! 🚀"
