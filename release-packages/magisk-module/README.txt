QWAMOS v1.0.0-qbamos-gold - Magisk Module
==========================================

WHAT IS THIS?

This is a Magisk module that overlays QWAMOS security features onto your existing Android system without replacing the OS. Perfect for users who want QWAMOS features without full system replacement.

FEATURES INCLUDED:

✓ Post-Quantum Cryptography (Kyber-1024, ChaCha20-Poly1305)
✓ VM-based Isolation (KVM hypervisor, if supported)
✓ ML Threat Detection (network, filesystem, syscall)
✓ Hardware Security (Phase 10 - ML bootloader override)
✓ AI Assistants (Kali GPT, Claude, ChatGPT)
✓ SecureType Keyboard (PQ encrypted, ML anomaly detection)
✓ AI App Builder (triple-AI validation)
✓ Tor/I2P Network Routing
✓ Emergency Protection (panic gesture, duress profiles)

PREREQUISITES:

1. Rooted Android device (Magisk installed)
2. Android 10+ (API 29+) recommended
3. ARM64 architecture
4. At least 2GB free space on /data
5. Termux (F-Droid version) for full functionality

INSTALLATION:

Method 1: Magisk Manager (Recommended)

  1. Download QWAMOS_Magisk_v1.0.0.zip to device
  2. Open Magisk Manager app
  3. Tap "Modules" tab
  4. Tap "+" button (Install from storage)
  5. Select QWAMOS_Magisk_v1.0.0.zip
  6. Wait for installation
  7. Reboot device

Method 2: ADB

  1. Copy to device:
     $ adb push QWAMOS_Magisk_v1.0.0.zip /sdcard/

  2. Install via Magisk Manager (see Method 1)

Method 3: Command Line (Advanced)

  $ adb shell
  $ su
  # magisk --install-module /sdcard/QWAMOS_Magisk_v1.0.0.zip
  # reboot

POST-INSTALLATION SETUP:

1. Reboot device (REQUIRED)

2. Install Termux (F-Droid version):
   https://f-droid.org/en/packages/com.termux/

3. Install dependencies in Termux:
   $ pkg install python clang make git tor

4. Run first-boot setup:
   $ cd /data/qwamos
   $ python3 setup/first_boot_setup.py

5. Generate post-quantum keys:
   $ python3 crypto/pq/pq_volume.py --generate-keys

6. Configure network routing (choose mode):
   $ python3 network/network_manager.py --configure

   Modes:
   - direct: No anonymization (fastest)
   - tor-only: Standard Tor
   - tor-dnscrypt: Tor + encrypted DNS (recommended)
   - maximum-anonymity: Tor → I2P chain (slowest)

7. Start Dom0 policy manager:
   $ python3 /data/qwamos/dom0/qwamosd/qwamosd.py &

8. (Optional) Start VMs:
   $ cd /data/qwamos/hypervisor/scripts
   $ ./start_vm.sh gateway-1
   $ ./start_vm.sh workstation-1

VERIFICATION:

Check if module is active:
  $ su -c "ls /data/adb/modules/"
  (Should show: qwamos)

Check logs:
  $ cat /data/qwamos/logs/magisk_service.log

Check KVM:
  $ lsmod | grep kvm
  (If available, should show: kvm)

FEATURES THAT REQUIRE ROOT:

- KVM kernel module loading
- Hardware kill switch driver
- Firmware integrity monitoring
- A/B partition isolation
- Baseband monitoring
- Full firewall control

FEATURES THAT WORK WITHOUT ROOT:

- Post-quantum encryption
- Network routing (Tor/I2P via Termux)
- AI assistants
- SecureType keyboard
- AI app builder
- ML threat detection (limited)

LIMITATIONS VS FULL QWAMOS:

This Magisk module provides QWAMOS features as an overlay:

  ✓ Preserves existing Android system
  ✓ Easier installation (no bootloader unlock required)
  ✓ Can be uninstalled via Magisk Manager
  ✓ Coexists with other Magisk modules

  ✗ Less isolation (shares Android kernel)
  ✗ Some features limited by Android restrictions
  ✗ No custom bootloader (U-Boot)
  ✗ Cannot modify boot partition

For maximum security, use full QWAMOS installation (TWRP or fastboot).

UNINSTALLATION:

Method 1: Magisk Manager

  1. Open Magisk Manager
  2. Tap "Modules" tab
  3. Tap trash icon next to "QWAMOS Security Layer"
  4. Reboot device

Method 2: Command Line

  $ su
  # rm -rf /data/adb/modules/qwamos
  # reboot

Your data in /data/qwamos will NOT be deleted. To remove:
  $ su
  # rm -rf /data/qwamos

TROUBLESHOOTING:

Problem: Module doesn't appear in Magisk
Solution:
  - Check Magisk version (requires 20.4+)
  - Reinstall module
  - Check /data/adb/modules/qwamos/install.log

Problem: VMs won't start
Solution:
  - Check KVM: lsmod | grep kvm
  - If no KVM, VMs will use user-mode (slower)
  - Check logs: /data/qwamos/logs/

Problem: Network not working
Solution:
  - Configure network mode: python3 network/network_manager.py --configure
  - Check Tor: systemctl status qwamos-tor (Termux)
  - See SUPPORT.md for detailed troubleshooting

Problem: Boot loop after installation
Solution:
  - Boot to recovery (TWRP or stock)
  - Delete /data/adb/modules/qwamos
  - Reboot

Problem: "Module is not compatible"
Solution:
  - Update Magisk to latest version
  - Check Android version (requires 10+)
  - Check architecture (requires ARM64)

VERIFICATION:

Verify SHA256 checksum before installing:

  $ sha256sum QWAMOS_Magisk_v1.0.0.zip
  (Compare with QWAMOS_Magisk_v1.0.0_SHA256.txt)

Verify GPG signature:

  $ gpg --verify QWAMOS_Magisk_v1.0.0.zip.asc QWAMOS_Magisk_v1.0.0.zip

  Expected fingerprint:
  18C4E89E37D5ECD392F52E85269CD0658D8BD942DCF33BE4E37CC94933E4C4D2

SUPPORT:

- GitHub Issues: https://github.com/Dezirae-Stark/QWAMOS/issues
- Email: clockwork.halo@tutanota.de
- Documentation: README.md, OPS_GUIDE.md, SUPPORT.md

COMPARISON: Magisk Module vs Full Install

| Feature | Magisk Module | Full Install |
|---------|---------------|--------------|
| Installation | Easy (Magisk Manager) | Complex (TWRP/fastboot) |
| Bootloader | No unlock required | Unlock required |
| Android OS | Preserved | Replaced |
| Isolation | Android kernel | Custom kernel |
| Uninstall | Reversible | Requires reflash |
| Security | Good | Maximum |
| Updates | Via Magisk | Manual flash |

RECOMMENDED USE CASES:

Magisk Module:
- Testing QWAMOS before full install
- Rooted Android user wanting QWAMOS features
- Need to preserve existing Android apps
- Want easy uninstall option

Full Install (TWRP/Fastboot):
- Maximum security required
- Nation-state threat model
- Dedicated QWAMOS device
- Don't need Android apps

LICENSE: AGPL-3.0
© 2025 First Sterling Capital, LLC
Author: Dezirae Stark
