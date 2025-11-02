#!/bin/bash
# QWAMOS Android VM Configuration Validation
# Validates all components required for Android VM deployment

set -e

QWAMOS_DIR="$HOME/QWAMOS"
ANDROID_VM_DIR="$QWAMOS_DIR/vms/android-vm"

echo "======================================"
echo "QWAMOS Android VM Configuration Validation"
echo "======================================"
echo ""

TESTS_PASSED=0
TESTS_TOTAL=8

# Test 1: Configuration file validation
echo "[1/$TESTS_TOTAL] Validating config.yaml..."
if [ -f "$ANDROID_VM_DIR/config.yaml" ]; then
    if python3 -c "import yaml; yaml.safe_load(open('$ANDROID_VM_DIR/config.yaml'))" 2>/dev/null; then
        echo "✅ Configuration file valid"
        ((TESTS_PASSED++))
    else
        echo "❌ Configuration file invalid (YAML parse error)"
    fi
else
    echo "❌ Configuration file missing"
fi

# Test 2: Kernel Image exists
echo ""
echo "[2/$TESTS_TOTAL] Checking kernel Image..."
if [ -f "$QWAMOS_DIR/kernel/Image" ]; then
    SIZE=$(du -h "$QWAMOS_DIR/kernel/Image" | cut -f1)
    echo "✅ Kernel Image found ($SIZE)"
    ((TESTS_PASSED++))
else
    echo "❌ Kernel Image missing"
fi

# Test 3: Initramfs exists
echo ""
echo "[3/$TESTS_TOTAL] Checking initramfs..."
if [ -d "$QWAMOS_DIR/initramfs" ]; then
    if [ -f "$QWAMOS_DIR/initramfs/init" ]; then
        echo "✅ Initramfs found with init script"
        ((TESTS_PASSED++))
    else
        echo "⚠️  Initramfs directory exists but init missing"
    fi
else
    echo "❌ Initramfs directory missing"
fi

# Test 4: Disk image exists
echo ""
echo "[4/$TESTS_TOTAL] Checking disk image..."
if [ -f "$ANDROID_VM_DIR/disk.qcow2" ]; then
    SIZE=$(du -h "$ANDROID_VM_DIR/disk.qcow2" | cut -f1)
    FORMAT=$(qemu-img info "$ANDROID_VM_DIR/disk.qcow2" 2>/dev/null | grep "file format" | awk '{print $3}')
    echo "✅ Disk image found ($SIZE, format: $FORMAT)"
    ((TESTS_PASSED++))
else
    echo "❌ Disk image missing"
fi

# Test 5: Network configuration
echo ""
echo "[5/$TESTS_TOTAL] Validating network configuration..."
if grep -q "mode: nat" "$ANDROID_VM_DIR/config.yaml"; then
    echo "✅ Network mode: NAT (correct for Gateway routing)"
    ((TESTS_PASSED++))
else
    echo "❌ Network configuration invalid"
fi

# Test 6: Security policies
echo ""
echo "[6/$TESTS_TOTAL] Checking security policies..."
if grep -q "isolation_level: high" "$ANDROID_VM_DIR/config.yaml"; then
    echo "✅ Security isolation level: high"
    ((TESTS_PASSED++))
else
    echo "❌ Security policies not configured"
fi

# Test 7: Encryption configuration
echo ""
echo "[7/$TESTS_TOTAL] Validating encryption settings..."
if grep -q "chacha20-poly1305" "$ANDROID_VM_DIR/config.yaml"; then
    echo "✅ Encryption: ChaCha20-Poly1305 configured"
    ((TESTS_PASSED++))
else
    echo "❌ Encryption not configured"
fi

# Test 8: Boot parameters
echo ""
echo "[8/$TESTS_TOTAL] Checking boot configuration..."
if grep -q "kernel:" "$ANDROID_VM_DIR/config.yaml"; then
    KERNEL_PATH=$(grep "kernel:" "$ANDROID_VM_DIR/config.yaml" | awk '{print $2}')
    if [ -f "$KERNEL_PATH" ]; then
        echo "✅ Boot parameters configured correctly"
        ((TESTS_PASSED++))
    else
        echo "⚠️  Boot parameters configured but kernel path invalid"
    fi
else
    echo "❌ Boot parameters missing"
fi

# Summary
echo ""
echo "======================================"
echo "Validation Summary"
echo "======================================"
echo "Tests passed: $TESTS_PASSED / $TESTS_TOTAL"
echo ""

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo "✅ ALL TESTS PASSED"
    echo ""
    echo "Android VM configuration is ready for deployment!"
    echo ""
    echo "Status:"
    echo "  • VM configuration: ✅ Complete"
    echo "  • Kernel + initramfs: ✅ Ready"
    echo "  • Disk image: ✅ Created"
    echo "  • Network routing: ✅ Configured (via Gateway VM)"
    echo "  • Security policies: ✅ Defined"
    echo "  • Encryption: ✅ Configured"
    echo ""
    echo "Next steps:"
    echo "  1. Obtain Android 14 system image (LineageOS or AOSP)"
    echo "  2. Convert to QCOW2 and replace disk.qcow2"
    echo "  3. Boot test with: bash ~/QWAMOS/hypervisor/scripts/test_vm_boot.sh android-1"
    echo "  4. Integrate with Gateway VM for Tor routing"
    echo ""
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    echo ""
    echo "Please fix the issues above before deployment."
    echo ""
    exit 1
fi
