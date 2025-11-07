#!/bin/bash
# Build QWAMOS TWRP Flashable Package
# Version: v1.0.0-qbamos-gold

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QWAMOS_ROOT="$(dirname "$SCRIPT_DIR")"
TWRP_DIR="$SCRIPT_DIR/twrp-flashable"
OUTPUT_ZIP="$SCRIPT_DIR/QWAMOS_v1.0.0_flashable.zip"

echo "========================================"
echo "  QWAMOS TWRP Package Builder"
echo "========================================"
echo ""

# Check prerequisites
echo "[1/8] Checking prerequisites..."
if [ ! -f "$QWAMOS_ROOT/kernel/Image" ]; then
    echo "ERROR: Kernel image not found at $QWAMOS_ROOT/kernel/Image"
    exit 1
fi

if [ ! -f "$QWAMOS_ROOT/bootloader/u-boot-source/u-boot" ]; then
    echo "ERROR: U-Boot not found"
    exit 1
fi

echo "✓ Prerequisites OK"
echo ""

# Create boot.img
echo "[2/8] Creating boot.img..."
mkdir -p "$TWRP_DIR"
cd "$QWAMOS_ROOT/kernel"

# Check if initramfs exists
if [ ! -f "initramfs_static.cpio.gz" ]; then
    echo "Building initramfs..."
    cd "$QWAMOS_ROOT/initramfs"
    find . | cpio -o -H newc | gzip > ../kernel/initramfs_static.cpio.gz
    cd "$QWAMOS_ROOT/kernel"
fi

# Create boot.img using mkbootimg (if available)
if command -v mkbootimg &> /dev/null; then
    mkbootimg \
        --kernel Image \
        --ramdisk initramfs_static.cpio.gz \
        --cmdline "console=ttyMSM0,115200n8 androidboot.console=ttyMSM0 androidboot.hardware=qcom loglevel=7" \
        --base 0x00000000 \
        --kernel_offset 0x00008000 \
        --ramdisk_offset 0x01000000 \
        --tags_offset 0x00000100 \
        --pagesize 4096 \
        --os_version 14.0.0 \
        --os_patch_level 2025-11 \
        --header_version 2 \
        --output "$TWRP_DIR/boot.img"
    echo "✓ boot.img created with mkbootimg"
else
    echo "WARNING: mkbootimg not found, copying raw kernel"
    cp Image "$TWRP_DIR/boot.img"
    echo "✓ boot.img created (raw kernel)"
fi

echo ""

# Copy system files
echo "[3/8] Copying system files..."
mkdir -p "$TWRP_DIR/system/qwamos"
mkdir -p "$TWRP_DIR/system/qwamos/bin"
mkdir -p "$TWRP_DIR/system/qwamos/lib"

# Copy security layer
cp -r "$QWAMOS_ROOT/security/"* "$TWRP_DIR/system/qwamos/" 2>/dev/null || true

# Copy crypto
cp -r "$QWAMOS_ROOT/crypto" "$TWRP_DIR/system/qwamos/" 2>/dev/null || true

# Copy network
cp -r "$QWAMOS_ROOT/network" "$TWRP_DIR/system/qwamos/" 2>/dev/null || true

# Copy AI
cp -r "$QWAMOS_ROOT/ai" "$TWRP_DIR/system/qwamos/" 2>/dev/null || true

# Copy keyboard
cp -r "$QWAMOS_ROOT/keyboard" "$TWRP_DIR/system/qwamos/" 2>/dev/null || true

# Copy ai_app_builder
cp -r "$QWAMOS_ROOT/ai_app_builder" "$TWRP_DIR/system/qwamos/" 2>/dev/null || true

echo "✓ System files copied"
echo ""

# Copy data files
echo "[4/8] Copying data files..."
mkdir -p "$TWRP_DIR/data/qwamos"

# Copy VM configurations
mkdir -p "$TWRP_DIR/data/qwamos/vms"
cp -r "$QWAMOS_ROOT/vms/"*.json "$TWRP_DIR/data/qwamos/vms/" 2>/dev/null || true

# Copy hypervisor scripts
cp -r "$QWAMOS_ROOT/hypervisor" "$TWRP_DIR/data/qwamos/" 2>/dev/null || true

echo "✓ Data files copied"
echo ""

# Copy kernel modules
echo "[5/8] Copying kernel modules..."
mkdir -p "$TWRP_DIR/modules"

# Copy Phase 10 hardware security modules (if built)
if [ -f "$QWAMOS_ROOT/hypervisor/drivers/usb_killswitch.ko" ]; then
    cp "$QWAMOS_ROOT/hypervisor/drivers/usb_killswitch.ko" "$TWRP_DIR/modules/"
    echo "✓ usb_killswitch.ko copied"
fi

echo "✓ Kernel modules copied"
echo ""

# Copy documentation
echo "[6/8] Copying documentation..."
cp "$QWAMOS_ROOT/README.md" "$TWRP_DIR/"
cp "$QWAMOS_ROOT/LICENSE" "$TWRP_DIR/"
cp "$QWAMOS_ROOT/OPS_GUIDE.md" "$TWRP_DIR/"
cp "$QWAMOS_ROOT/SUPPORT.md" "$TWRP_DIR/"
echo "✓ Documentation copied"
echo ""

# Create ZIP package
echo "[7/8] Creating flashable ZIP..."
cd "$TWRP_DIR"
zip -r "$OUTPUT_ZIP" . -x "*.git*" "*.DS_Store"
cd "$SCRIPT_DIR"
echo "✓ ZIP package created: $OUTPUT_ZIP"
echo ""

# Compute checksums
echo "[8/8] Computing checksums..."
SHA256=$(sha256sum "$OUTPUT_ZIP" | cut -d' ' -f1)
echo "$SHA256  QWAMOS_v1.0.0_flashable.zip" > "$SCRIPT_DIR/QWAMOS_v1.0.0_flashable_SHA256.txt"
echo "✓ SHA256: $SHA256"
echo ""

# Sign with GPG
if command -v gpg &> /dev/null; then
    echo "Signing package with GPG..."
    gpg --armor --detach-sign "$OUTPUT_ZIP"
    echo "✓ GPG signature created: ${OUTPUT_ZIP}.asc"
else
    echo "WARNING: GPG not found, skipping signature"
fi
echo ""

# Summary
echo "========================================"
echo "  Build Complete!"
echo "========================================"
echo ""
echo "Package: $OUTPUT_ZIP"
echo "Size: $(du -h "$OUTPUT_ZIP" | cut -f1)"
echo "SHA256: $SHA256"
echo ""
echo "Next steps:"
echo "1. Test in TWRP recovery emulator"
echo "2. Upload to GitHub Releases"
echo "3. Update installation documentation"
echo ""
echo "Installation command:"
echo "  adb push $OUTPUT_ZIP /sdcard/"
echo "  (Then flash from TWRP)"
echo ""
