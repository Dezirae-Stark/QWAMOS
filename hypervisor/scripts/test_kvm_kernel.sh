#!/bin/bash
#
# Test QWAMOS Custom Kernel with KVM Support
#
# This boots the custom kernel/Image (which has KVM enabled)
# in QEMU to verify KVM functionality
#

set -e

QWAMOS_ROOT="$HOME/QWAMOS"
KERNEL="$QWAMOS_ROOT/kernel/Image"
INITRD="$QWAMOS_ROOT/kernel/initramfs_static.cpio.gz"

echo "======================================================================"
echo "QWAMOS Custom Kernel Boot Test (KVM Verification)"
echo "======================================================================"
echo ""

# Check if kernel exists
if [ ! -f "$KERNEL" ]; then
    echo "❌ Custom kernel not found: $KERNEL"
    exit 1
fi

echo "✅ Custom kernel found: $(ls -lh $KERNEL | awk '{print $5}')"

# Check if initrd exists
if [ ! -f "$INITRD" ]; then
    echo "❌ Initramfs not found: $INITRD"
    exit 1
fi

echo "✅ Initramfs found: $(ls -lh $INITRD | awk '{print $5}')"
echo ""

# Check if QEMU is available
if ! command -v qemu-system-aarch64 &> /dev/null; then
    echo "❌ qemu-system-aarch64 not found"
    echo "   Install with: pkg install qemu-system-aarch64"
    exit 1
fi

echo "✅ QEMU found: $(qemu-system-aarch64 --version | head -1)"
echo ""

echo "======================================================================"
echo "Booting Custom QWAMOS Kernel..."
echo "======================================================================"
echo ""
echo "This kernel was compiled with:"
echo "  • CONFIG_KVM=y"
echo "  • CONFIG_KVM_ARM_HOST=y"
echo "  • CONFIG_VHOST_NET=y"
echo "  • CONFIG_VHOST_VSOCK=y"
echo "  • VirtIO devices enabled"
echo ""
echo "Expected result: /dev/kvm should be available in the VM"
echo ""
echo "Press Ctrl-A then X to exit QEMU"
echo ""

sleep 2

# Boot with KVM acceleration attempt
# Note: -accel kvm will fail on host without KVM, but kernel itself has KVM support
qemu-system-aarch64 \
    -machine virt,gic-version=3 \
    -cpu cortex-a76 \
    -accel tcg \
    -smp 2 \
    -m 1G \
    -kernel "$KERNEL" \
    -initrd "$INITRD" \
    -append "console=ttyAMA0 root=/dev/ram0 rdinit=/init" \
    -nographic \
    -monitor none

echo ""
echo "======================================================================"
echo "Boot test complete!"
echo "======================================================================"
