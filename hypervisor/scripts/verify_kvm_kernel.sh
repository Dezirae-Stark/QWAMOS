#!/bin/bash
#
# Automated KVM Kernel Verification
# Boots custom kernel and checks for /dev/kvm
#

set -e

QWAMOS_ROOT="$HOME/QWAMOS"
KERNEL="$QWAMOS_ROOT/kernel/Image"
INITRD="$QWAMOS_ROOT/kernel/initramfs_static.cpio.gz"

echo "======================================================================"
echo "QWAMOS Custom Kernel - Automated KVM Verification"
echo "======================================================================"
echo ""

# Check files exist
if [ ! -f "$KERNEL" ]; then
    echo "❌ Kernel not found: $KERNEL"
    exit 1
fi

if [ ! -f "$INITRD" ]; then
    echo "❌ Initramfs not found: $INITRD"
    exit 1
fi

echo "✅ Kernel: $(ls -lh $KERNEL | awk '{print $5}')"
echo "✅ Initramfs: $(ls -lh $INITRD | awk '{print $5}')"
echo "✅ QEMU: $(qemu-system-aarch64 --version | head -1)"
echo ""

# Create a test script to run inside the kernel
cat > /tmp/kvm_test_init.sh << 'INITSCRIPT'
#!/bin/sh
echo ""
echo "========================================================================"
echo "QWAMOS Custom Kernel Boot - KVM Verification"
echo "========================================================================"
echo ""

# Show kernel version
echo "[*] Kernel Version:"
uname -a
echo ""

# Check for /dev/kvm
echo "[*] Checking for /dev/kvm..."
if [ -e /dev/kvm ]; then
    echo "✅ SUCCESS: /dev/kvm exists!"
    ls -l /dev/kvm
    echo ""
    echo "✅ KVM is ENABLED in this kernel"
else
    echo "❌ FAILED: /dev/kvm not found"
    echo ""
    echo "Checking /dev directory:"
    ls -la /dev/ | head -20
fi

echo ""
echo "========================================================================"
echo "Test complete! Kernel will halt in 3 seconds..."
echo "========================================================================"
sleep 3
poweroff -f
INITSCRIPT

chmod +x /tmp/kvm_test_init.sh

echo "Starting QEMU boot test (will auto-shutdown after verification)..."
echo ""

# Boot kernel with test script
timeout 30s qemu-system-aarch64 \
    -machine virt,gic-version=3 \
    -cpu cortex-a76 \
    -accel tcg \
    -smp 2 \
    -m 1G \
    -kernel "$KERNEL" \
    -initrd "$INITRD" \
    -append "console=ttyAMA0 root=/dev/ram0 rdinit=/init" \
    -nographic \
    -serial mon:stdio \
    -no-reboot \
    || true

echo ""
echo "======================================================================"
echo "Boot test complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "1. If /dev/kvm was found: ✅ KVM is ready in custom kernel"
echo "2. If not found: Check kernel config and rebuild"
echo ""
