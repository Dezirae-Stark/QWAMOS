#!/system/bin/sh
# QWAMOS Magisk Module Installer
# Version: v1.0.0-qbamos-gold

##########################################################################################
# Configuration
##########################################################################################

SKIPUNZIP=0
PROPFILE=true
POSTFSDATA=false
LATESTARTSERVICE=true

##########################################################################################
# Functions
##########################################################################################

print_modname() {
  ui_print "=========================================="
  ui_print "  QWAMOS Security Layer"
  ui_print "  v1.0.0-qbamos-gold"
  ui_print "=========================================="
  ui_print " "
  ui_print "Post-Quantum Mobile Security OS"
  ui_print "Author: Dezirae Stark"
  ui_print "License: AGPL-3.0"
  ui_print " "
}

on_install() {
  ui_print "- Installing QWAMOS..."
  ui_print " "

  # Extract module files
  ui_print "- Extracting files..."
  unzip -o "$ZIPFILE" 'system/*' -d $MODPATH >&2

  # Set permissions
  ui_print "- Setting permissions..."
  set_perm_recursive $MODPATH/system/qwamos 0 0 0755 0644
  set_perm_recursive $MODPATH/system/qwamos/bin 0 0 0755 0755
  set_perm_recursive $MODPATH/system/qwamos/scripts 0 0 0755 0755

  # Create QWAMOS directories
  ui_print "- Creating QWAMOS directories..."
  mkdir -p /data/qwamos/{vms,keys,volumes,logs,dom0,gateway_vm,workstation_vm}
  mkdir -p /data/qwamos/network/{tor,i2p,dnscrypt,vpn}
  mkdir -p /data/qwamos/crypto/{pq,keys}
  mkdir -p /data/qwamos/ml/{models,logs}
  mkdir -p /data/qwamos/panic
  mkdir -p /etc/qwamos

  # Set data directory permissions
  chown -R 0:0 /data/qwamos
  chmod -R 755 /data/qwamos
  chmod 700 /data/qwamos/keys
  chmod 700 /data/qwamos/crypto/keys

  # Check for root
  if [ ! -f "/system/xbin/su" ] && [ ! -f "/system/bin/su" ]; then
    ui_print "⚠️ WARNING: Root not detected"
    ui_print "Some features require root access"
  else
    ui_print "✓ Root access detected"
  fi

  # Check for KVM support
  if [ -e "/dev/kvm" ]; then
    ui_print "✓ KVM support detected"
  else
    ui_print "⚠️ WARNING: KVM not available"
    ui_print "VMs will run in user-mode (slower)"
  fi

  # Check Android version
  SDK_VERSION=$(getprop ro.build.version.sdk)
  if [ "$SDK_VERSION" -lt 29 ]; then
    ui_print "⚠️ WARNING: Android 10+ recommended"
    ui_print "Current: Android $(getprop ro.build.version.release)"
  else
    ui_print "✓ Android version: $(getprop ro.build.version.release)"
  fi

  ui_print " "
  ui_print "- Installation complete!"
  ui_print " "
}

set_permissions() {
  # Set permissions for system files
  set_perm_recursive $MODPATH 0 0 0755 0644
  set_perm_recursive $MODPATH/system/qwamos/bin 0 0 0755 0755
}

##########################################################################################
# Post-Installation Instructions
##########################################################################################

ui_print "=========================================="
ui_print "  POST-INSTALLATION STEPS"
ui_print "=========================================="
ui_print " "
ui_print "1. Reboot your device"
ui_print " "
ui_print "2. Install Termux (F-Droid version):"
ui_print "   https://f-droid.org/packages/com.termux/"
ui_print " "
ui_print "3. Run first-boot setup:"
ui_print "   $ cd /data/qwamos"
ui_print "   $ python3 setup/first_boot_setup.py"
ui_print " "
ui_print "4. Generate post-quantum keys:"
ui_print "   $ python3 crypto/pq/pq_volume.py --generate-keys"
ui_print " "
ui_print "5. Configure network routing:"
ui_print "   $ python3 network/network_manager.py --configure"
ui_print " "
ui_print "6. Start Dom0 policy manager:"
ui_print "   $ systemctl start qwamosd"
ui_print " "
ui_print "=========================================="
ui_print "  FEATURES INCLUDED"
ui_print "=========================================="
ui_print " "
ui_print "✓ Post-Quantum Crypto (Kyber-1024)"
ui_print "✓ VM-based Isolation (KVM)"
ui_print "✓ ML Threat Detection"
ui_print "✓ Hardware Security (Phase 10)"
ui_print "✓ AI Assistants (Kali GPT, Claude, ChatGPT)"
ui_print "✓ SecureType Keyboard (PQ encrypted)"
ui_print "✓ AI App Builder"
ui_print "✓ Tor/I2P Network Routing"
ui_print " "
ui_print "Documentation:"
ui_print "github.com/Dezirae-Stark/QWAMOS"
ui_print " "
ui_print "Support:"
ui_print "clockwork.halo@tutanota.de"
ui_print " "
ui_print "=========================================="
ui_print "  Enjoy QWAMOS! 🔐"
ui_print "=========================================="
ui_print " "
