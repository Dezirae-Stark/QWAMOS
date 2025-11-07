#!/bin/bash
# Build QWAMOS Fastboot Images
# Version: v1.0.0-qbamos-gold

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QWAMOS_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "  QWAMOS Fastboot Image Builder"
echo "========================================"
echo ""

# Check prerequisites
echo "[1/6] Checking prerequisites..."
if [ ! -f "$QWAMOS_ROOT/kernel/Image" ]; then
    echo "ERROR: Kernel not found"
    exit 1
fi
echo "✓ Prerequisites OK"
echo ""

# Create boot.img
echo "[2/6] Creating boot.img..."
cd "$QWAMOS_ROOT/kernel"

if [ ! -f "initramfs_static.cpio.gz" ]; then
    echo "Building initramfs..."
    cd "$QWAMOS_ROOT/initramfs"
    find . | cpio -o -H newc | gzip > ../kernel/initramfs_static.cpio.gz
fi

cd "$QWAMOS_ROOT/kernel"

if command -v mkbootimg &> /dev/null; then
    mkbootimg \
        --kernel Image \
        --ramdisk initramfs_static.cpio.gz \
        --cmdline "console=ttyMSM0,115200n8 androidboot.hardware=qcom loglevel=7" \
        --base 0x00000000 \
        --kernel_offset 0x00008000 \
        --ramdisk_offset 0x01000000 \
        --pagesize 4096 \
        --os_version 14.0.0 \
        --header_version 2 \
        --output "$SCRIPT_DIR/boot.img"
    echo "✓ boot.img created"
else
    echo "WARNING: mkbootimg not found, using raw kernel"
    cp Image "$SCRIPT_DIR/boot.img"
fi
echo ""

# Create system.img
echo "[3/6] Creating system.img (this may take a while)..."
SYSTEM_DIR="$SCRIPT_DIR/system"
mkdir -p "$SYSTEM_DIR/qwamos"

# Copy QWAMOS components
cp -r "$QWAMOS_ROOT/security" "$SYSTEM_DIR/qwamos/"
cp -r "$QWAMOS_ROOT/crypto" "$SYSTEM_DIR/qwamos/"
cp -r "$QWAMOS_ROOT/network" "$SYSTEM_DIR/qwamos/"
cp -r "$QWAMOS_ROOT/ai" "$SYSTEM_DIR/qwamos/"
cp -r "$QWAMOS_ROOT/hypervisor" "$SYSTEM_DIR/qwamos/"

# Create sparse image
if command -v make_ext4fs &> /dev/null; then
    make_ext4fs -L system -l 2G -s "$SCRIPT_DIR/system.img" "$SYSTEM_DIR"
elif command -v mke2fs &> /dev/null; then
    # Fallback to regular ext4
    dd if=/dev/zero of="$SCRIPT_DIR/system.img" bs=1M count=2048
    mke2fs -t ext4 -L system "$SCRIPT_DIR/system.img"
    mkdir -p /tmp/qwamos_mount
    sudo mount -o loop "$SCRIPT_DIR/system.img" /tmp/qwamos_mount
    sudo cp -r "$SYSTEM_DIR/"* /tmp/qwamos_mount/
    sudo umount /tmp/qwamos_mount
else
    echo "ERROR: Neither make_ext4fs nor mke2fs found"
    exit 1
fi
echo "✓ system.img created"
echo ""

# Create vendor.img (minimal)
echo "[4/6] Creating vendor.img..."
VENDOR_DIR="$SCRIPT_DIR/vendor"
mkdir -p "$VENDOR_DIR"
echo "QWAMOS v1.0.0" > "$VENDOR_DIR/build.prop"

if command -v make_ext4fs &> /dev/null; then
    make_ext4fs -L vendor -l 256M -s "$SCRIPT_DIR/vendor.img" "$VENDOR_DIR"
else
    dd if=/dev/zero of="$SCRIPT_DIR/vendor.img" bs=1M count=256
    mke2fs -t ext4 -L vendor "$SCRIPT_DIR/vendor.img"
fi
echo "✓ vendor.img created"
echo ""

# Create vbmeta.img (empty, disables AVB)
echo "[5/6] Creating vbmeta.img..."
dd if=/dev/zero of="$SCRIPT_DIR/vbmeta.img" bs=4096 count=1
echo "✓ vbmeta.img created"
echo ""

# Compute checksums
echo "[6/6] Computing checksums..."
cd "$SCRIPT_DIR"
sha256sum boot.img system.img vendor.img vbmeta.img > SHA256SUMS.txt
echo "✓ Checksums computed"
echo ""

# Summary
echo "========================================"
echo "  Build Complete!"
echo "========================================"
echo ""
echo "Images created:"
ls -lh boot.img system.img vendor.img vbmeta.img
echo ""
echo "Total size: $(du -sh boot.img system.img vendor.img vbmeta.img | tail -1 | cut -f1)"
echo ""
echo "Next step: Run ./flash-all.sh to flash device"
echo ""
