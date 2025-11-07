#!/bin/bash
# Build QWAMOS Magisk Module
# Version: v1.0.0-qbamos-gold

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QWAMOS_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
OUTPUT_ZIP="$SCRIPT_DIR/../QWAMOS_Magisk_v1.0.0.zip"

echo "========================================"
echo "  QWAMOS Magisk Module Builder"
echo "========================================"
echo ""

# Create system directory structure
echo "[1/6] Creating directory structure..."
mkdir -p "$SCRIPT_DIR/system/qwamos"
echo "✓ Directories created"
echo ""

# Copy QWAMOS components
echo "[2/6] Copying QWAMOS components..."

# Security layer
cp -r "$QWAMOS_ROOT/security" "$SCRIPT_DIR/system/qwamos/" 2>/dev/null || true

# Crypto
cp -r "$QWAMOS_ROOT/crypto" "$SCRIPT_DIR/system/qwamos/" 2>/dev/null || true

# Network
cp -r "$QWAMOS_ROOT/network" "$SCRIPT_DIR/system/qwamos/" 2>/dev/null || true

# AI
cp -r "$QWAMOS_ROOT/ai" "$SCRIPT_DIR/system/qwamos/" 2>/dev/null || true

# Keyboard
cp -r "$QWAMOS_ROOT/keyboard" "$SCRIPT_DIR/system/qwamos/" 2>/dev/null || true

# AI App Builder
cp -r "$QWAMOS_ROOT/ai_app_builder" "$SCRIPT_DIR/system/qwamos/" 2>/dev/null || true

# Hypervisor
cp -r "$QWAMOS_ROOT/hypervisor" "$SCRIPT_DIR/system/qwamos/" 2>/dev/null || true

echo "✓ Components copied"
echo ""

# Copy scripts
echo "[3/6] Copying scripts..."
mkdir -p "$SCRIPT_DIR/system/qwamos/scripts"
cp "$QWAMOS_ROOT"/scripts/*.sh "$SCRIPT_DIR/system/qwamos/scripts/" 2>/dev/null || true
echo "✓ Scripts copied"
echo ""

# Copy documentation
echo "[4/6] Copying documentation..."
cp "$QWAMOS_ROOT/README.md" "$SCRIPT_DIR/"
cp "$QWAMOS_ROOT/LICENSE" "$SCRIPT_DIR/"
cp "$QWAMOS_ROOT/OPS_GUIDE.md" "$SCRIPT_DIR/"
cp "$QWAMOS_ROOT/SUPPORT.md" "$SCRIPT_DIR/"
echo "✓ Documentation copied"
echo ""

# Create ZIP package
echo "[5/6] Creating Magisk module ZIP..."
cd "$SCRIPT_DIR"
zip -r "$OUTPUT_ZIP" \
  module.prop \
  install.sh \
  service.sh \
  system/ \
  README.md \
  LICENSE \
  OPS_GUIDE.md \
  SUPPORT.md \
  -x "*.git*" "*.DS_Store" "*__pycache__*" "*.pyc"

echo "✓ ZIP created: $OUTPUT_ZIP"
echo ""

# Compute checksum
echo "[6/6] Computing checksum..."
cd "$(dirname "$OUTPUT_ZIP")"
SHA256=$(sha256sum "$(basename "$OUTPUT_ZIP")" | cut -d' ' -f1)
echo "$SHA256  $(basename "$OUTPUT_ZIP")" > QWAMOS_Magisk_v1.0.0_SHA256.txt
echo "✓ SHA256: $SHA256"
echo ""

# Sign with GPG (if available)
if command -v gpg &> /dev/null; then
  echo "Signing module..."
  gpg --armor --detach-sign "$OUTPUT_ZIP"
  echo "✓ GPG signature created"
else
  echo "SKIP: GPG not available"
fi
echo ""

# Summary
echo "========================================"
echo "  Build Complete!"
echo "========================================"
echo ""
echo "Module: $OUTPUT_ZIP"
echo "Size: $(du -h "$OUTPUT_ZIP" | cut -f1)"
echo "SHA256: $SHA256"
echo ""
echo "INSTALLATION:"
echo "1. Copy to device: adb push $OUTPUT_ZIP /sdcard/"
echo "2. Open Magisk Manager"
echo "3. Tap 'Modules' → '+' → Select ZIP"
echo "4. Reboot device"
echo ""
echo "POST-INSTALLATION:"
echo "1. Install Termux (F-Droid)"
echo "2. Run: cd /data/qwamos && python3 setup/first_boot_setup.py"
echo ""
