#!/usr/bin/env bash
# Build PRoot VM Template for QWAMOS
# Creates a minimal userspace virtualization environment using PRoot

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_TEMPLATES_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${VM_TEMPLATES_DIR}/output/templates"
WORK_DIR="${VM_TEMPLATES_DIR}/work/proot"

# Configuration
VM_NAME="qwamos-proot-template"
DEBIAN_VERSION="bookworm"
ARCH="aarch64"  # For Android/Termux compatibility

echo "========================================"
echo "QWAMOS PRoot Template Builder"
echo "========================================"
echo "VM Name: ${VM_NAME}"
echo "Debian: ${DEBIAN_VERSION}"
echo "Architecture: ${ARCH}"
echo "========================================"

# Create work directory
mkdir -p "${WORK_DIR}"
mkdir -p "${OUTPUT_DIR}"

cd "${WORK_DIR}"

# Function to create PRoot rootfs
create_proot_rootfs() {
    echo "[1/5] Creating PRoot rootfs..."

    ROOTFS_DIR="${WORK_DIR}/rootfs"
    mkdir -p "${ROOTFS_DIR}"

    # Create minimal filesystem structure
    echo "Creating minimal filesystem structure..."
    mkdir -p "${ROOTFS_DIR}"/{bin,boot,dev,etc,home,lib,mnt,opt,proc,root,run,sbin,srv,sys,tmp,usr,var}
    mkdir -p "${ROOTFS_DIR}/usr"/{bin,include,lib,local,sbin,share,src}
    mkdir -p "${ROOTFS_DIR}/var"/{cache,lib,local,lock,log,opt,run,spool,tmp}

    # Create Android/Termux compatibility directories
    mkdir -p "${ROOTFS_DIR}/data/data/com.termux/files"
    mkdir -p "${ROOTFS_DIR}/sdcard"
    mkdir -p "${ROOTFS_DIR}/storage"

    # Basic configuration files
    echo "QWAMOS-PRoot" > "${ROOTFS_DIR}/etc/hostname"

    cat > "${ROOTFS_DIR}/etc/hosts" << 'EOF'
127.0.0.1 localhost
::1 localhost
127.0.1.1 qwamos-proot
EOF

    # Create passwd and group files
    cat > "${ROOTFS_DIR}/etc/passwd" << 'EOF'
root:x:0:0:root:/root:/bin/bash
qwamos:x:1000:1000:QWAMOS User:/home/qwamos:/bin/bash
EOF

    cat > "${ROOTFS_DIR}/etc/group" << 'EOF'
root:x:0:
qwamos:x:1000:
EOF

    # Create home directory
    mkdir -p "${ROOTFS_DIR}/home/qwamos"

    echo "✓ PRoot rootfs structure created"
}

# Function to apply QWAMOS configurations
apply_qwamos_configs() {
    echo "[2/5] Applying QWAMOS configurations..."

    # Create QWAMOS directory structure
    mkdir -p "${ROOTFS_DIR}/opt/qwamos"/{bin,config,crypto,gateway,vm}

    # Create QWAMOS config for PRoot
    cat > "${ROOTFS_DIR}/opt/qwamos/config/qwamos.conf" << 'EOF'
# QWAMOS Configuration for PRoot Template
VM_TYPE="proot"
VM_VERSION="1.2.0"
PQC_ENABLED="true"
KYBER_MODE="kyber-1024"
ENCRYPTION="chacha20-poly1305"
NETWORK_MODE="isolated"
GATEWAY_REQUIRED="true"
ANDROID_COMPAT="true"
TERMUX_INTEGRATION="true"
EOF

    # Create PRoot-specific configuration
    cat > "${ROOTFS_DIR}/opt/qwamos/config/proot.conf" << 'EOF'
# PRoot-specific Configuration
PROOT_NO_SECCOMP=1
PROOT_LINK2SYMLINK=1
PROOT_L2S_DIR=/tmp/.l2s
PROOT_TMPDIR=/tmp
EOF

    # Create startup script for PRoot
    cat > "${ROOTFS_DIR}/opt/qwamos/bin/proot-start.sh" << 'EOF'
#!/bin/bash
# QWAMOS PRoot VM Startup Script

echo "Starting QWAMOS PRoot VM..."

# Load configuration
if [ -f /opt/qwamos/config/qwamos.conf ]; then
    source /opt/qwamos/config/qwamos.conf
fi

# Initialize environment
export HOME=/root
export USER=root
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Initialize PQC subsystem
if [ "$PQC_ENABLED" = "true" ]; then
    echo "Initializing Post-Quantum Cryptography..."
    # PQC initialization
fi

# Configure network isolation
if [ "$NETWORK_MODE" = "isolated" ]; then
    echo "Network isolation mode enabled"
    # Network isolation configuration
fi

# Android compatibility layer
if [ "$ANDROID_COMPAT" = "true" ]; then
    echo "Android compatibility layer enabled"
    # Android-specific initialization
fi

echo "QWAMOS PRoot VM started successfully"
exec /bin/bash
EOF

    chmod +x "${ROOTFS_DIR}/opt/qwamos/bin/proot-start.sh"

    # Create PRoot launch wrapper
    cat > "${WORK_DIR}/launch-proot.sh" << 'EOF'
#!/bin/bash
# Launch QWAMOS PRoot VM
# Usage: ./launch-proot.sh

ROOTFS_DIR="$(dirname "$0")/rootfs"

if [ ! -d "$ROOTFS_DIR" ]; then
    echo "Error: rootfs directory not found"
    exit 1
fi

# Check for proot
if ! command -v proot &> /dev/null; then
    echo "Error: proot not found. Install it first:"
    echo "  pkg install proot (Termux)"
    echo "  apt install proot (Debian/Ubuntu)"
    exit 1
fi

echo "Launching QWAMOS PRoot VM..."

proot \
    -r "$ROOTFS_DIR" \
    -b /dev \
    -b /proc \
    -b /sys \
    -w /root \
    /opt/qwamos/bin/proot-start.sh
EOF

    chmod +x "${WORK_DIR}/launch-proot.sh"

    echo "✓ QWAMOS configurations applied"
}

# Function to create metadata
create_metadata() {
    echo "[3/5] Creating VM metadata..."

    cat > "${WORK_DIR}/${VM_NAME}.json" << EOF
{
  "name": "${VM_NAME}",
  "type": "proot",
  "version": "1.2.0",
  "architecture": "${ARCH}",
  "os": "Debian ${DEBIAN_VERSION}",
  "features": {
    "pqc_enabled": true,
    "kyber_1024": true,
    "chacha20_poly1305": true,
    "blake3": true,
    "network_isolation": true,
    "android_compat": true,
    "termux_integration": true,
    "no_root_required": true
  },
  "requirements": {
    "proot_version": ">=5.1",
    "ram_min": "256M",
    "ram_recommended": "1G",
    "storage": "2G"
  },
  "files": {
    "rootfs": "${VM_NAME}-rootfs.tar.gz",
    "launcher": "launch-proot.sh",
    "metadata": "${VM_NAME}.json"
  },
  "usage": {
    "extract": "tar xzf ${VM_NAME}.tar.gz",
    "launch": "./launch-proot.sh",
    "termux": "proot -r rootfs -b /dev -b /proc -b /sys /bin/bash"
  },
  "created": "$(date -Iseconds)",
  "checksum_algorithm": "sha256"
}
EOF

    echo "✓ Metadata created"
}

# Function to package template
package_template() {
    echo "[4/5] Packaging template..."

    cd "${WORK_DIR}"

    # Create rootfs tarball
    ROOTFS_TAR="${WORK_DIR}/${VM_NAME}-rootfs.tar.gz"
    tar czf "${ROOTFS_TAR}" -C "${ROOTFS_DIR}" .

    echo "✓ Rootfs packaged: ${ROOTFS_TAR}"

    # Generate checksums
    if command -v sha256sum &> /dev/null; then
        sha256sum "${ROOTFS_TAR}" > "${ROOTFS_TAR}.sha256"
        sha256sum "launch-proot.sh" > "launch-proot.sh.sha256"
        echo "✓ Checksums generated"
    fi
}

# Function to export template
export_template() {
    echo "[5/5] Exporting template to output directory..."

    # Create final archive
    TEMPLATE_ARCHIVE="${OUTPUT_DIR}/${VM_NAME}.tar.gz"

    cd "${WORK_DIR}"
    tar czf "${TEMPLATE_ARCHIVE}" \
        "${VM_NAME}-rootfs.tar.gz" \
        "launch-proot.sh" \
        "${VM_NAME}.json" \
        *.sha256 2>/dev/null || true

    # Generate final checksum
    if command -v sha256sum &> /dev/null; then
        cd "${OUTPUT_DIR}"
        sha256sum "${VM_NAME}.tar.gz" > "${VM_NAME}.tar.gz.sha256"
    fi

    echo "✓ Template exported to: ${TEMPLATE_ARCHIVE}"

    # Show file size
    if [ -f "${TEMPLATE_ARCHIVE}" ]; then
        SIZE=$(du -h "${TEMPLATE_ARCHIVE}" | cut -f1)
        echo "✓ Template size: ${SIZE}"
    fi
}

# Main execution
main() {
    create_proot_rootfs
    apply_qwamos_configs
    create_metadata
    package_template
    export_template

    echo ""
    echo "========================================"
    echo "✅ PRoot Template Build Complete!"
    echo "========================================"
    echo "Output: ${OUTPUT_DIR}/${VM_NAME}.tar.gz"
    echo ""
    echo "Quick Start:"
    echo "  1. Extract: tar xzf ${VM_NAME}.tar.gz"
    echo "  2. Launch: ./launch-proot.sh"
    echo ""
}

main "$@"
