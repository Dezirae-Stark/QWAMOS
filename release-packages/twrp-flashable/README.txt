QWAMOS v1.0.0-qbamos-gold - TWRP Flashable Package
===================================================

INSTALLATION INSTRUCTIONS
-------------------------

PREREQUISITES:
1. Unlocked bootloader
2. TWRP recovery installed
3. Full device backup (REQUIRED!)
4. At least 5GB free space on /data
5. Android 10+ (API 29+) recommended

INSTALLATION STEPS:

1. Boot into TWRP Recovery:
   - Power off device
   - Hold Power + Volume Down
   - Select "Recovery" from bootloader menu

2. Create Full Backup:
   - In TWRP, select "Backup"
   - Check: Boot, System, Data
   - Swipe to backup
   - WAIT for completion (10-20 minutes)

3. Flash QWAMOS:
   - Select "Install"
   - Navigate to QWAMOS_v1.0.0_flashable.zip
   - Swipe to confirm flash
   - WAIT for completion (5-10 minutes)

4. Reboot:
   - Select "Reboot System"
   - First boot takes 3-5 minutes

POST-INSTALLATION:

1. Install Termux (F-Droid version):
   https://f-droid.org/en/packages/com.termux/

2. Complete QWAMOS setup:
   $ cd /data/qwamos
   $ python3 setup/first_boot_setup.py

3. Generate post-quantum keys:
   $ python3 crypto/pq/pq_volume.py --generate-keys

4. Configure network routing:
   $ python3 network/network_manager.py --configure

5. Start Dom0 policy manager:
   $ systemctl start qwamosd

ROLLBACK PROCEDURE:

If QWAMOS doesn't boot or you want to revert:

1. Boot into TWRP Recovery

2. Restore from backup:
   - Select "Restore"
   - Select your backup
   - Swipe to restore

OR flash boot backup:
   - Select "Install"
   - Select "Install Image"
   - Navigate to /sdcard/qwamos_boot_backup.img
   - Select "Boot" partition
   - Swipe to flash

VERIFICATION:

SHA256 Checksum:
  (To be computed after package creation)

GPG Signature:
  Fingerprint: 18C4E89E37D5ECD392F52E85269CD0658D8BD942

  Verify:
  $ gpg --verify QWAMOS_v1.0.0_flashable.zip.asc QWAMOS_v1.0.0_flashable.zip

TROUBLESHOOTING:

- Boot loop: Restore backup or flash boot backup image
- No network: Configure Tor bridges in /etc/qwamos/tor/torrc
- VMs won't start: Check KVM module loaded (lsmod | grep kvm)
- Permission errors: Run 'restorecon -R /data/qwamos'

SUPPORT:

- GitHub: https://github.com/Dezirae-Stark/QWAMOS/issues
- Email: clockwork.halo@tutanota.de
- Documentation: See OPS_GUIDE.md and SUPPORT.md in repo

WARNING:
--------
This is an EXPERIMENTAL operating system. Use at your own risk.
Always maintain backups. Not responsible for data loss or bricked devices.

LICENSE: AGPL-3.0
© 2025 First Sterling Capital, LLC
Author: Dezirae Stark
