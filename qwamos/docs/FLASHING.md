# QWAMOS Flashing Guide

## Prerequisites

- Motorola Edge 2025 with unlocked bootloader
- TWRP recovery installed
- Backup of all data

## Installation Steps

1. **Boot to TWRP**:
   ```bash
   adb reboot recovery
   ```

2. **Flash QWAMOS**:
   - Transfer qwamos-flashable.zip to /sdcard
   - In TWRP: Install → Select ZIP → qwamos-flashable.zip
   - Verify signature (Kyber-1024)
   - Swipe to confirm flash

3. **First Boot**:
   - Set password (16+ characters recommended)
   - Configure network (all traffic routes through Tor)
   - Enable security toggles as needed

## Rollback

If QWAMOS fails to boot:
- Boot to TWRP
- Restore TWRP backup from /sdcard/TWRP/

## Verification

After boot, verify:
```bash
qwamosctl gateway_vm policy-update
cat /proc/version  # Should show QWAMOS kernel
```
