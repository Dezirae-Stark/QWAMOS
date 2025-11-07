#!/bin/bash
# QWAMOS Fastboot Flash Script
# Version: v1.0.0-qbamos-gold
#
# This script flashes QWAMOS to your device using fastboot.
# REQUIRED: Unlocked bootloader

set -e

echo "========================================"
echo "  QWAMOS Fastboot Flash Tool"
echo "  v1.0.0-qbamos-gold"
echo "========================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root (not recommended)
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}WARNING: Running as root is not recommended${NC}"
    echo "Press Enter to continue or Ctrl+C to abort..."
    read
fi

# Check prerequisites
echo "[1/10] Checking prerequisites..."

if ! command -v fastboot &> /dev/null; then
    echo -e "${RED}ERROR: fastboot not found${NC}"
    echo "Install Android SDK Platform Tools:"
    echo "  - Linux: sudo apt install android-tools-fastboot"
    echo "  - macOS: brew install android-platform-tools"
    echo "  - Windows: Download from developer.android.com"
    exit 1
fi

if ! command -v adb &> /dev/null; then
    echo -e "${YELLOW}WARNING: adb not found (optional but recommended)${NC}"
fi

# Check if device is connected
echo -e "${GREEN}✓${NC} fastboot found"
echo ""

# Check for image files
echo "[2/10] Verifying image files..."

REQUIRED_FILES=(
    "boot.img"
    "system.img"
    "vendor.img"
    "vbmeta.img"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}ERROR: $file not found${NC}"
        echo "Please run build_fastboot_images.sh first"
        exit 1
    fi
    echo -e "${GREEN}✓${NC} $file"
done
echo ""

# Warning about data loss
echo -e "${RED}========================================"
echo "           WARNING"
echo "========================================${NC}"
echo ""
echo "This will ERASE ALL DATA on your device!"
echo "- All apps will be removed"
echo "- All user data will be deleted"
echo "- Android OS will be replaced with QWAMOS"
echo ""
echo -e "${YELLOW}BACKUP YOUR DATA BEFORE PROCEEDING${NC}"
echo ""
echo "Type 'YES' in capital letters to continue"
read -p "> " confirmation

if [ "$confirmation" != "YES" ]; then
    echo "Flash aborted."
    exit 0
fi
echo ""

# Check device connection
echo "[3/10] Checking device connection..."
echo "Please ensure:"
echo "1. Device is powered off"
echo "2. USB cable is connected"
echo "3. Hold Volume Down + Power to enter fastboot mode"
echo ""
echo "Press Enter when device is in fastboot mode..."
read

# Verify fastboot connection
if ! fastboot devices | grep -q .; then
    echo -e "${RED}ERROR: No fastboot device detected${NC}"
    echo "Troubleshooting:"
    echo "1. Check USB cable connection"
    echo "2. Try different USB port"
    echo "3. Install device drivers (Windows)"
    echo "4. Enable USB debugging and OEM unlocking"
    exit 1
fi

DEVICE_SN=$(fastboot devices | head -1 | cut -f1)
echo -e "${GREEN}✓${NC} Device detected: $DEVICE_SN"
echo ""

# Check bootloader status
echo "[4/10] Checking bootloader status..."
BOOTLOADER_STATUS=$(fastboot getvar unlocked 2>&1 | grep "unlocked:" | cut -d' ' -f2)

if [ "$BOOTLOADER_STATUS" != "yes" ]; then
    echo -e "${RED}ERROR: Bootloader is locked${NC}"
    echo ""
    echo "You must unlock the bootloader first:"
    echo "  fastboot flashing unlock"
    echo ""
    echo "WARNING: Unlocking will WIPE ALL DATA"
    exit 1
fi

echo -e "${GREEN}✓${NC} Bootloader is unlocked"
echo ""

# Backup current boot partition (safety)
echo "[5/10] Backing up current boot partition..."
if command -v adb &> /dev/null; then
    echo "Rebooting to system to create backup..."
    fastboot reboot
    sleep 10
    adb wait-for-device
    adb shell su -c "dd if=/dev/block/by-name/boot_a of=/sdcard/qwamos_boot_backup.img bs=4M"
    adb pull /sdcard/qwamos_boot_backup.img .
    echo -e "${GREEN}✓${NC} Boot backup saved to: qwamos_boot_backup.img"
    echo "Rebooting to fastboot..."
    adb reboot bootloader
    sleep 5
else
    echo -e "${YELLOW}SKIP: adb not available, backup not created${NC}"
fi
echo ""

# Flash boot partition
echo "[6/10] Flashing boot partition (kernel + initramfs)..."
fastboot flash boot_a boot.img
fastboot flash boot_b boot.img  # A/B partition support
echo -e "${GREEN}✓${NC} Boot partition flashed"
echo ""

# Flash system partition
echo "[7/10] Flashing system partition..."
fastboot flash system_a system.img
fastboot flash system_b system.img  # A/B partition support
echo -e "${GREEN}✓${NC} System partition flashed"
echo ""

# Flash vendor partition
echo "[8/10] Flashing vendor partition..."
fastboot flash vendor_a vendor.img
fastboot flash vendor_b vendor.img  # A/B partition support
echo -e "${GREEN}✓${NC} Vendor partition flashed"
echo ""

# Flash vbmeta (disable Android Verified Boot)
echo "[9/10] Flashing vbmeta (disabling AVB)..."
fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img
fastboot --disable-verity --disable-verification flash vbmeta_a vbmeta.img
fastboot --disable-verity --disable-verification flash vbmeta_b vbmeta.img
echo -e "${GREEN}✓${NC} vbmeta flashed (AVB disabled)"
echo ""

# Wipe userdata (optional but recommended for clean install)
echo "[10/10] Wiping userdata..."
echo -e "${YELLOW}This will erase all user data${NC}"
echo "Press Enter to wipe, or Ctrl+C to skip..."
read

fastboot -w  # Wipe userdata and cache
echo -e "${GREEN}✓${NC} Userdata wiped"
echo ""

# Set active slot (A/B)
echo "Setting active slot to A..."
fastboot set_active a
echo -e "${GREEN}✓${NC} Active slot set to A"
echo ""

# Reboot
echo "========================================"
echo "  Flash Complete!"
echo "========================================"
echo ""
echo "Rebooting device..."
fastboot reboot
echo ""
echo "First boot will take 3-5 minutes."
echo "Please be patient..."
echo ""
echo -e "${GREEN}POST-INSTALLATION STEPS:${NC}"
echo "1. Install Termux (F-Droid version)"
echo "2. Run: cd /data/qwamos && python3 setup/first_boot_setup.py"
echo "3. Generate post-quantum keys"
echo "4. Configure network routing mode"
echo ""
echo "Documentation: github.com/Dezirae-Stark/QWAMOS"
echo "Support: clockwork.halo@tutanota.de"
echo ""
echo -e "${YELLOW}ROLLBACK PROCEDURE (if needed):${NC}"
echo "1. Boot to fastboot mode"
echo "2. Flash boot backup: fastboot flash boot_a qwamos_boot_backup.img"
echo "3. Factory reset: fastboot -w"
echo "4. Reboot: fastboot reboot"
echo ""
echo "Enjoy QWAMOS! 🔐"
