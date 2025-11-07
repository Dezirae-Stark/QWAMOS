QWAMOS v1.0.0-qbamos-gold - Fastboot Flash Package
===================================================

INSTALLATION INSTRUCTIONS
-------------------------

PREREQUISITES:
1. Unlocked bootloader (REQUIRED!)
2. Android SDK Platform Tools installed
3. USB drivers installed (Windows only)
4. Full device backup (REQUIRED!)
5. At least 3GB free space for images

STEP 1: BUILD IMAGES

Run the build script to create flashable images:

  $ ./build_fastboot_images.sh

This will create:
  - boot.img (kernel + initramfs)
  - system.img (QWAMOS system files)
  - vendor.img (minimal vendor partition)
  - vbmeta.img (disabled AVB)
  - SHA256SUMS.txt (checksums)

STEP 2: UNLOCK BOOTLOADER (if not already unlocked)

WARNING: This will WIPE ALL DATA!

1. Enable Developer Options:
   Settings → About Phone → Tap Build Number 7 times

2. Enable OEM Unlocking:
   Settings → Developer Options → Enable "OEM unlocking"

3. Enable USB Debugging:
   Settings → Developer Options → Enable "USB debugging"

4. Reboot to fastboot:
   $ adb reboot bootloader

5. Unlock bootloader:
   $ fastboot flashing unlock

6. Confirm on device (Volume buttons + Power)

7. Wait for wipe and reboot

STEP 3: FLASH QWAMOS

Run the flash script:

  $ ./flash-all.sh

The script will:
1. Verify prerequisites
2. Check device connection
3. Backup current boot partition
4. Flash boot, system, vendor, vbmeta
5. Wipe userdata (optional)
6. Set active slot to A
7. Reboot device

STEP 4: FIRST BOOT SETUP

After reboot (takes 3-5 minutes):

1. Install Termux (F-Droid version):
   https://f-droid.org/en/packages/com.termux/

2. Run first boot setup:
   $ cd /data/qwamos
   $ python3 setup/first_boot_setup.py

3. Generate post-quantum keys:
   $ python3 crypto/pq/pq_volume.py --generate-keys

4. Configure network routing:
   $ python3 network/network_manager.py --configure

5. Start Dom0:
   $ systemctl start qwamosd

MANUAL FLASH (Alternative):

If flash-all.sh doesn't work, flash manually:

  $ fastboot flash boot_a boot.img
  $ fastboot flash boot_b boot.img
  $ fastboot flash system_a system.img
  $ fastboot flash system_b system.img
  $ fastboot flash vendor_a vendor.img
  $ fastboot flash vendor_b vendor.img
  $ fastboot --disable-verity --disable-verification flash vbmeta vbmeta.img
  $ fastboot -w  # Wipe userdata
  $ fastboot set_active a
  $ fastboot reboot

ROLLBACK PROCEDURE:

If QWAMOS doesn't boot:

Option 1: Restore boot backup
  $ fastboot flash boot_a qwamos_boot_backup.img
  $ fastboot reboot

Option 2: Factory reset
  $ fastboot -w
  $ fastboot reboot

Option 3: Flash stock firmware
  - Download official firmware for your device
  - Flash using manufacturer's tool

VERIFICATION:

Verify checksums before flashing:

  $ sha256sum -c SHA256SUMS.txt

Expected output:
  boot.img: OK
  system.img: OK
  vendor.img: OK
  vbmeta.img: OK

DEVICE COMPATIBILITY:

Tested on:
  - Motorola Edge 2025 (Snapdragon 8 Gen 3)
  - Google Pixel 8 (Tensor G3)

Should work on:
  - Any ARM64 Android device with unlocked bootloader
  - Android 10+ (API 29+)
  - KVM support (for full VM acceleration)

May NOT work on:
  - Devices with locked bootloader
  - Non-ARM64 devices (x86, ARM32)
  - Devices without A/B partitioning (older devices)

TROUBLESHOOTING:

Problem: fastboot not recognized
Solution:
  - Linux: sudo apt install android-tools-fastboot
  - macOS: brew install android-platform-tools
  - Windows: Download from developer.android.com

Problem: Device not detected
Solution:
  - Check USB cable (use official cable)
  - Try different USB port (USB 2.0 preferred)
  - Install device drivers (Windows)
  - Enable USB debugging

Problem: Bootloader unlock fails
Solution:
  - Enable "OEM unlocking" in Developer Options
  - Some carriers block unlocking (check with carrier)
  - Some devices require unlock code from manufacturer

Problem: Boot loop after flash
Solution:
  - Flash boot backup: fastboot flash boot_a qwamos_boot_backup.img
  - Factory reset: fastboot -w
  - Reflash stock firmware

Problem: No network/VMs won't start
Solution:
  - Check KVM support: lsmod | grep kvm
  - Configure Tor bridges if blocked
  - See SUPPORT.md for detailed troubleshooting

SUPPORT:

- GitHub Issues: https://github.com/Dezirae-Stark/QWAMOS/issues
- Email: clockwork.halo@tutanota.de
- Documentation: OPS_GUIDE.md, SUPPORT.md

WARNING:
--------
Flashing QWAMOS will:
- ERASE ALL DATA on your device
- Replace Android OS with QWAMOS
- Void warranty (on most devices)
- May brick device if interrupted

ALWAYS maintain backups. Not responsible for data loss or bricked devices.

LICENSE: AGPL-3.0
© 2025 First Sterling Capital, LLC
Author: Dezirae Stark
