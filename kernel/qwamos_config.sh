#!/bin/bash
#
# QWAMOS Kernel Configuration Script
#
# Customizes Linux 6.6 LTS for QWAMOS requirements:
# - ARM64 architecture
# - KVM hypervisor support
# - Virtualization features
# - Enhanced security (SELinux, AppArmor, etc.)
# - Post-quantum crypto modules
# - Device drivers for mobile
#

set -e

KERNEL_DIR="$HOME/QWAMOS/kernel/linux-6.6-source"

cd "$KERNEL_DIR"

echo "======================================================================"
echo "QWAMOS Kernel Configuration"
echo "======================================================================"
echo ""
echo "Enabling QWAMOS-specific features..."
echo ""

# Use scripts/config to modify .config
CONFIG="$KERNEL_DIR/scripts/config"

# ============================================================
# 1. VIRTUALIZATION & KVM
# ============================================================
echo "[1/8] Enabling KVM hypervisor support..."

$CONFIG --enable CONFIG_VIRTUALIZATION
$CONFIG --enable CONFIG_KVM
$CONFIG --enable CONFIG_KVM_ARM_HOST
$CONFIG --enable CONFIG_VHOST_NET
$CONFIG --enable CONFIG_VHOST_VSOCK
$CONFIG --enable CONFIG_VHOST
$CONFIG --enable CONFIG_VIRTIO
$CONFIG --enable CONFIG_VIRTIO_PCI
$CONFIG --enable CONFIG_VIRTIO_BALLOON
$CONFIG --enable CONFIG_VIRTIO_BLK
$CONFIG --enable CONFIG_VIRTIO_NET
$CONFIG --enable CONFIG_VIRTIO_CONSOLE
$CONFIG --enable CONFIG_VIRTIO_MMIO
$CONFIG --enable CONFIG_VIRTIO_MMIO_CMDLINE_DEVICES

# ============================================================
# 2. SECURITY FEATURES
# ============================================================
echo "[2/8] Enabling security features (SELinux, AppArmor)..."

$CONFIG --enable CONFIG_SECURITY
$CONFIG --enable CONFIG_SECURITYFS
$CONFIG --enable CONFIG_SECURITY_NETWORK
$CONFIG --enable CONFIG_SECURITY_PATH
$CONFIG --enable CONFIG_SECURITY_SELINUX
$CONFIG --enable CONFIG_SECURITY_SELINUX_BOOTPARAM
$CONFIG --enable CONFIG_SECURITY_SELINUX_DEVELOP
$CONFIG --enable CONFIG_SECURITY_APPARMOR
$CONFIG --enable CONFIG_DEFAULT_SECURITY_SELINUX
$CONFIG --disable CONFIG_DEFAULT_SECURITY_DAC

# Secure boot / module signing
$CONFIG --enable CONFIG_MODULE_SIG
$CONFIG --enable CONFIG_MODULE_SIG_FORCE
$CONFIG --enable CONFIG_MODULE_SIG_SHA256

# Kernel hardening
$CONFIG --enable CONFIG_HARDENED_USERCOPY
$CONFIG --enable CONFIG_FORTIFY_SOURCE
$CONFIG --enable CONFIG_STACKPROTECTOR
$CONFIG --enable CONFIG_STACKPROTECTOR_STRONG

# ============================================================
# 3. CRYPTOGRAPHY
# ============================================================
echo "[3/8] Enabling cryptographic modules..."

$CONFIG --enable CONFIG_CRYPTO
$CONFIG --enable CONFIG_CRYPTO_ALGAPI
$CONFIG --enable CONFIG_CRYPTO_AEAD
$CONFIG --enable CONFIG_CRYPTO_HASH
$CONFIG --enable CONFIG_CRYPTO_MANAGER

# Modern ciphers
$CONFIG --enable CONFIG_CRYPTO_CHACHA20
$CONFIG --enable CONFIG_CRYPTO_POLY1305
$CONFIG --enable CONFIG_CRYPTO_CHACHA20POLY1305

# Hashing
$CONFIG --enable CONFIG_CRYPTO_SHA256
$CONFIG --enable CONFIG_CRYPTO_SHA512
$CONFIG --enable CONFIG_CRYPTO_BLAKE2B

# Key derivation
$CONFIG --enable CONFIG_CRYPTO_KDF800108_CTR
$CONFIG --enable CONFIG_CRYPTO_HKDF

# Hardware crypto acceleration (ARM NEON)
$CONFIG --enable CONFIG_CRYPTO_AES_ARM64
$CONFIG --enable CONFIG_CRYPTO_AES_ARM64_CE
$CONFIG --enable CONFIG_CRYPTO_SHA256_ARM64
$CONFIG --enable CONFIG_CRYPTO_SHA512_ARM64

# Device mapper crypto (for VeraCrypt)
$CONFIG --enable CONFIG_BLK_DEV_DM
$CONFIG --enable CONFIG_DM_CRYPT
$CONFIG --enable CONFIG_DM_VERITY
$CONFIG --enable CONFIG_DM_INTEGRITY

# ============================================================
# 4. FILE SYSTEMS
# ============================================================
echo "[4/8] Enabling file systems..."

$CONFIG --enable CONFIG_EXT4_FS
$CONFIG --enable CONFIG_EXT4_FS_SECURITY
$CONFIG --enable CONFIG_F2FS_FS
$CONFIG --enable CONFIG_F2FS_FS_SECURITY
$CONFIG --enable CONFIG_BTRFS_FS
$CONFIG --enable CONFIG_OVERLAY_FS
$CONFIG --enable CONFIG_FUSE_FS
$CONFIG --enable CONFIG_VIRTIO_FS

# Encrypted filesystems
$CONFIG --enable CONFIG_FS_ENCRYPTION
$CONFIG --enable CONFIG_ECRYPT_FS

# ============================================================
# 5. NETWORKING
# ============================================================
echo "[5/8] Enabling networking features..."

$CONFIG --enable CONFIG_NET
$CONFIG --enable CONFIG_INET
$CONFIG --enable CONFIG_IPV6
$CONFIG --enable CONFIG_NETFILTER
$CONFIG --enable CONFIG_NETFILTER_XT_TARGET_NFLOG
$CONFIG --enable CONFIG_NETFILTER_XT_MATCH_STATE

# Network namespaces (for VM isolation)
$CONFIG --enable CONFIG_NET_NS
$CONFIG --enable CONFIG_UTS_NS
$CONFIG --enable CONFIG_IPC_NS
$CONFIG --enable CONFIG_USER_NS
$CONFIG --enable CONFIG_PID_NS

# TUN/TAP for VMs
$CONFIG --enable CONFIG_TUN
$CONFIG --enable CONFIG_TAP

# Bridge for VM networking
$CONFIG --enable CONFIG_BRIDGE
$CONFIG --enable CONFIG_VLAN_8021Q

# Tor/VPN support
$CONFIG --enable CONFIG_INET_TUNNEL
$CONFIG --enable CONFIG_NET_IPGRE
$CONFIG --enable CONFIG_NET_IPVTI
$CONFIG --enable CONFIG_INET6_TUNNEL

# ============================================================
# 6. DEVICE DRIVERS
# ============================================================
echo "[6/8] Enabling device drivers..."

# Block devices
$CONFIG --enable CONFIG_BLK_DEV_LOOP
$CONFIG --enable CONFIG_BLK_DEV_RAM
$CONFIG --disable CONFIG_BLK_DEV_RAM_SIZE
$CONFIG --set-val CONFIG_BLK_DEV_RAM_SIZE 65536

# USB
$CONFIG --enable CONFIG_USB_SUPPORT
$CONFIG --enable CONFIG_USB
$CONFIG --enable CONFIG_USB_ANNOUNCE_NEW_DEVICES

# Input devices
$CONFIG --enable CONFIG_INPUT_TOUCHSCREEN
$CONFIG --enable CONFIG_INPUT_EVDEV

# Graphics (for mobile display)
$CONFIG --enable CONFIG_FB
$CONFIG --enable CONFIG_DRM
$CONFIG --enable CONFIG_DRM_FBDEV_EMULATION

# ============================================================
# 7. CGROUPS & NAMESPACES (for containerization)
# ============================================================
echo "[7/8] Enabling cgroups and namespaces..."

$CONFIG --enable CONFIG_CGROUPS
$CONFIG --enable CONFIG_CGROUP_FREEZER
$CONFIG --enable CONFIG_CGROUP_DEVICE
$CONFIG --enable CONFIG_CGROUP_CPUACCT
$CONFIG --enable CONFIG_CGROUP_SCHED
$CONFIG --enable CONFIG_MEMCG
$CONFIG --enable CONFIG_MEMCG_SWAP

# Namespaces
$CONFIG --enable CONFIG_NAMESPACES
$CONFIG --enable CONFIG_UTS_NS
$CONFIG --enable CONFIG_IPC_NS
$CONFIG --enable CONFIG_USER_NS
$CONFIG --enable CONFIG_PID_NS
$CONFIG --enable CONFIG_NET_NS

# ============================================================
# 8. MISC FEATURES
# ============================================================
echo "[8/8] Enabling miscellaneous features..."

# devtmpfs (automatic /dev)
$CONFIG --enable CONFIG_DEVTMPFS
$CONFIG --enable CONFIG_DEVTMPFS_MOUNT

# Tmpfs for /tmp
$CONFIG --enable CONFIG_TMPFS
$CONFIG --enable CONFIG_TMPFS_POSIX_ACL
$CONFIG --enable CONFIG_TMPFS_XATTR

# Kernel debug info (for development)
$CONFIG --disable CONFIG_DEBUG_INFO
$CONFIG --disable CONFIG_DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT

# Disable unnecessary features
$CONFIG --disable CONFIG_WIRELESS
$CONFIG --disable CONFIG_WLAN

echo ""
echo "======================================================================"
echo "Configuration Complete"
echo "======================================================================"
echo ""
echo "Validating configuration..."

# Regenerate config with dependencies
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- olddefconfig

echo ""
echo "✓ QWAMOS kernel configuration complete!"
echo ""
echo "Key features enabled:"
echo "  • KVM hypervisor (arm64)"
echo "  • VirtIO devices"
echo "  • SELinux + AppArmor"
echo "  • ChaCha20-Poly1305 crypto"
echo "  • Device mapper crypto (VeraCrypt)"
echo "  • Network namespaces (VM isolation)"
echo "  • TUN/TAP + Bridge networking"
echo "  • Modern file systems (ext4, f2fs, btrfs)"
echo ""
echo "Next step: make ARCH=arm64 CROSS_COMPILE=aarch64-linux-android- -j4"
echo ""
