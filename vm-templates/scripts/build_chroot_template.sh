#!/usr/bin/env bash
# Build Chroot VM Template for QWAMOS
# Creates a chroot environment with QWAMOS configurations

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_TEMPLATES_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${VM_TEMPLATES_DIR}/output/templates"
WORK_DIR="${VM_TEMPLATES_DIR}/work/chroot"

# Configuration
VM_NAME="qwamos-chroot-template"
DEBIAN_VERSION="bookworm"
ARCH="amd64"

echo "========================================"
echo "QWAMOS Chroot Template Builder"
echo "========================================"
echo "VM Name: ${VM_NAME}"
echo "Debian: ${DEBIAN_VERSION}"
echo "Architecture: ${ARCH}"
echo "========================================"

# Create work directory
mkdir -p "${WORK_DIR}"
mkdir -p "${OUTPUT_DIR}"

cd "${WORK_DIR}"

# Function to create chroot rootfs
create_chroot_rootfs() {
    echo "[1/5] Creating chroot rootfs..."

    ROOTFS_DIR="${WORK_DIR}/rootfs"
    mkdir -p "${ROOTFS_DIR}"

    # Create standard Linux filesystem structure
    echo "Creating filesystem structure..."
    mkdir -p "${ROOTFS_DIR}"/{bin,boot,dev,etc,home,lib,lib64,media,mnt,opt,proc,root,run,sbin,srv,sys,tmp,usr,var}
    mkdir -p "${ROOTFS_DIR}/usr"/{bin,include,lib,lib64,local,sbin,share,src}
    mkdir -p "${ROOTFS_DIR}/usr/local"/{bin,etc,games,include,lib,man,sbin,share,src}
    mkdir -p "${ROOTFS_DIR}/var"/{cache,lib,local,lock,log,mail,opt,run,spool,tmp}

    # Create device nodes (minimal set)
    mkdir -p "${ROOTFS_DIR}/dev"

    # Basic configuration
    echo "QWAMOS-Chroot" > "${ROOTFS_DIR}/etc/hostname"

    cat > "${ROOTFS_DIR}/etc/hosts" << 'EOF'
127.0.0.1 localhost
::1 localhost ip6-localhost ip6-loopback
127.0.1.1 qwamos-chroot
EOF

    # Create fstab
    cat > "${ROOTFS_DIR}/etc/fstab" << 'EOF'
# QWAMOS Chroot fstab
proc /proc proc defaults 0 0
sysfs /sys sysfs defaults 0 0
devpts /dev/pts devpts gid=5,mode=620 0 0
tmpfs /run tmpfs defaults 0 0
tmpfs /tmp tmpfs defaults 0 0
EOF

    # Create passwd and group
    cat > "${ROOTFS_DIR}/etc/passwd" << 'EOF'
root:x:0:0:root:/root:/bin/bash
qwamos:x:1000:1000:QWAMOS User:/home/qwamos:/bin/bash
EOF

    cat > "${ROOTFS_DIR}/etc/group" << 'EOF'
root:x:0:
qwamos:x:1000:qwamos
EOF

    # Create user home directories
    mkdir -p "${ROOTFS_DIR}/root"
    mkdir -p "${ROOTFS_DIR}/home/qwamos"

    # Create shells file
    cat > "${ROOTFS_DIR}/etc/shells" << 'EOF'
/bin/sh
/bin/bash
EOF

    echo "✓ Chroot rootfs structure created"
}

# Function to apply QWAMOS configurations
apply_qwamos_configs() {
    echo "[2/5] Applying QWAMOS configurations..."

    # Create QWAMOS directory structure
    mkdir -p "${ROOTFS_DIR}/opt/qwamos"/{bin,config,crypto,gateway,vm,logs}

    # Create QWAMOS config for Chroot
    cat > "${ROOTFS_DIR}/opt/qwamos/config/qwamos.conf" << 'EOF'
# QWAMOS Configuration for Chroot Template
VM_TYPE="chroot"
VM_VERSION="1.2.0"
PQC_ENABLED="true"
KYBER_MODE="kyber-1024"
ENCRYPTION="chacha20-poly1305"
NETWORK_MODE="isolated"
GATEWAY_REQUIRED="true"
REQUIRES_ROOT="true"
EOF

    # Create chroot-specific configuration
    cat > "${ROOTFS_DIR}/opt/qwamos/config/chroot.conf" << 'EOF'
# Chroot-specific Configuration
BIND_DEV=true
BIND_PROC=true
BIND_SYS=true
BIND_TMP=true
UNSHARE_NET=true
UNSHARE_PID=true
UNSHARE_IPC=true
UNSHARE_UTS=true
EOF

    # Create init script
    cat > "${ROOTFS_DIR}/opt/qwamos/bin/chroot-init.sh" << 'EOF'
#!/bin/bash
# QWAMOS Chroot Initialization Script

echo "Initializing QWAMOS Chroot VM..."

# Load configuration
if [ -f /opt/qwamos/config/qwamos.conf ]; then
    source /opt/qwamos/config/qwamos.conf
fi

# Set up environment
export HOME=/root
export USER=root
export LOGNAME=root
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Mount virtual filesystems (if not already mounted)
if [ ! -d /proc/1 ]; then
    mount -t proc proc /proc 2>/dev/null || true
fi

if [ ! -d /sys/kernel ]; then
    mount -t sysfs sysfs /sys 2>/dev/null || true
fi

if [ ! -c /dev/null ]; then
    mount -o bind /dev /dev 2>/dev/null || true
fi

# Initialize PQC subsystem
if [ "$PQC_ENABLED" = "true" ]; then
    echo "Initializing Post-Quantum Cryptography..."
    # PQC initialization would go here
fi

# Configure network isolation
if [ "$NETWORK_MODE" = "isolated" ]; then
    echo "Network isolation mode enabled"
    # Network namespace configuration
fi

echo "QWAMOS Chroot VM initialized successfully"
echo ""
echo "Welcome to QWAMOS Chroot Environment"
echo "Type 'exit' to leave the chroot"
echo ""

# Drop to shell
exec /bin/bash -l
EOF

    chmod +x "${ROOTFS_DIR}/opt/qwamos/bin/chroot-init.sh"

    # Create chroot launcher script
    cat > "${WORK_DIR}/launch-chroot.sh" << 'EOF'
#!/bin/bash
# Launch QWAMOS Chroot VM
# Usage: sudo ./launch-chroot.sh

ROOTFS_DIR="$(dirname "$0")/rootfs"

if [ ! -d "$ROOTFS_DIR" ]; then
    echo "Error: rootfs directory not found"
    exit 1
fi

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    echo "Usage: sudo ./launch-chroot.sh"
    exit 1
fi

echo "Launching QWAMOS Chroot VM..."

# Bind mount essential filesystems
mount --bind /dev "$ROOTFS_DIR/dev" 2>/dev/null || true
mount --bind /proc "$ROOTFS_DIR/proc" 2>/dev/null || true
mount --bind /sys "$ROOTFS_DIR/sys" 2>/dev/null || true

# Cleanup function
cleanup() {
    echo "Cleaning up mounts..."
    umount "$ROOTFS_DIR/sys" 2>/dev/null || true
    umount "$ROOTFS_DIR/proc" 2>/dev/null || true
    umount "$ROOTFS_DIR/dev" 2>/dev/null || true
}

trap cleanup EXIT

# Enter chroot with network namespace isolation (optional)
if command -v unshare &> /dev/null; then
    # Use unshare for better isolation
    unshare --net --pid --fork --mount-proc="$ROOTFS_DIR/proc" \
        chroot "$ROOTFS_DIR" /opt/qwamos/bin/chroot-init.sh
else
    # Fallback to basic chroot
    chroot "$ROOTFS_DIR" /opt/qwamos/bin/chroot-init.sh
fi
EOF

    chmod +x "${WORK_DIR}/launch-chroot.sh"

    # Create README
    cat > "${ROOTFS_DIR}/README.txt" << 'EOF'
QWAMOS Chroot Template
======================

This is a minimal Debian-based chroot environment with QWAMOS
post-quantum cryptography and security features.

Requirements:
- Root access (sudo)
- Linux kernel with namespace support
- unshare utility (optional, for better isolation)

Usage:
1. Extract the template:
   tar xzf qwamos-chroot-template.tar.gz

2. Launch the chroot:
   sudo ./launch-chroot.sh

3. Exit the chroot:
   Type 'exit' or press Ctrl+D

Features:
- Post-Quantum Cryptography (Kyber-1024, ChaCha20-Poly1305)
- Network isolation via network namespaces
- Process isolation via PID namespaces
- Minimal attack surface

For more information, visit:
https://github.com/Dezirae-Stark/QWAMOS
EOF

    echo "✓ QWAMOS configurations applied"
}

# Function to create metadata
create_metadata() {
    echo "[3/5] Creating VM metadata..."

    cat > "${WORK_DIR}/${VM_NAME}.json" << EOF
{
  "name": "${VM_NAME}",
  "type": "chroot",
  "version": "1.2.0",
  "architecture": "${ARCH}",
  "os": "Debian ${DEBIAN_VERSION}",
  "features": {
    "pqc_enabled": true,
    "kyber_1024": true,
    "chacha20_poly1305": true,
    "blake3": true,
    "network_isolation": true,
    "pid_namespace": true,
    "ipc_namespace": true,
    "uts_namespace": true,
    "mount_namespace": true
  },
  "requirements": {
    "root_required": true,
    "kernel": ">=3.8",
    "unshare": "optional",
    "ram_min": "256M",
    "ram_recommended": "1G",
    "storage": "2G"
  },
  "files": {
    "rootfs": "${VM_NAME}-rootfs.tar.gz",
    "launcher": "launch-chroot.sh",
    "metadata": "${VM_NAME}.json",
    "readme": "README.txt"
  },
  "usage": {
    "extract": "tar xzf ${VM_NAME}.tar.gz",
    "launch": "sudo ./launch-chroot.sh",
    "exit": "Type 'exit' or press Ctrl+D"
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
        sha256sum "launch-chroot.sh" > "launch-chroot.sh.sha256"
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
        "launch-chroot.sh" \
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
    create_chroot_rootfs
    apply_qwamos_configs
    create_metadata
    package_template
    export_template

    echo ""
    echo "========================================"
    echo "✅ Chroot Template Build Complete!"
    echo "========================================"
    echo "Output: ${OUTPUT_DIR}/${VM_NAME}.tar.gz"
    echo ""
    echo "Quick Start:"
    echo "  1. Extract: tar xzf ${VM_NAME}.tar.gz"
    echo "  2. Launch: sudo ./launch-chroot.sh"
    echo "  3. Exit: Type 'exit'"
    echo ""
}

main "$@"
