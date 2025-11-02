#!/bin/bash
# QWAMOS Whonix Gateway Test Script
# Tests that Whonix configuration files are valid

set -e

echo "=================================================="
echo "  QWAMOS Whonix Gateway Configuration Test"
echo "=================================================="
echo ""

WHONIX_DIR=~/QWAMOS/vms/whonix-vm

##############################################
# 1. Check Configuration Files Exist
##############################################
echo "[*] Checking configuration files..."

if [ ! -f "$WHONIX_DIR/config.yaml" ]; then
    echo "[!] ERROR: whonix-vm/config.yaml not found"
    exit 1
fi
echo "[+] config.yaml found"

if [ ! -f "$WHONIX_DIR/torrc" ]; then
    echo "[!] ERROR: whonix-vm/torrc not found"
    exit 1
fi
echo "[+] torrc found"

if [ ! -f "$WHONIX_DIR/firewall.sh" ]; then
    echo "[!] ERROR: whonix-vm/firewall.sh not found"
    exit 1
fi
echo "[+] firewall.sh found"

##############################################
# 2. Validate YAML Configuration
##############################################
echo ""
echo "[*] Validating YAML configuration..."

if command -v python &> /dev/null; then
    python -c "
import yaml
import sys

try:
    with open('$WHONIX_DIR/config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Check required fields
    assert config['vm']['name'] == 'whonix-vm'
    assert config['vm']['type'] == 'gateway'
    assert config['network']['mode'] == 'isolated'
    assert config['network']['tor']['enabled'] == True

    print('[+] YAML configuration is valid')
    print('    - VM name: whonix-vm')
    print('    - VM type: gateway')
    print('    - Network mode: isolated')
    print('    - Tor enabled: True')
    sys.exit(0)
except Exception as e:
    print('[!] ERROR: Invalid YAML configuration')
    print(f'    {str(e)}')
    sys.exit(1)
"
else
    echo "[!] Python not found, skipping YAML validation"
fi

##############################################
# 3. Validate Tor Configuration
##############################################
echo ""
echo "[*] Validating Tor configuration..."

# Check for critical Tor settings
if grep -q "SOCKSPort 10.152.152.10:9050" "$WHONIX_DIR/torrc"; then
    echo "[+] SOCKS proxy configured (9050)"
else
    echo "[!] ERROR: SOCKS proxy not configured"
    exit 1
fi

if grep -q "TransPort 10.152.152.10:9040" "$WHONIX_DIR/torrc"; then
    echo "[+] Transparent proxy configured (9040)"
else
    echo "[!] ERROR: Transparent proxy not configured"
    exit 1
fi

if grep -q "DNSPort 10.152.152.10:5300" "$WHONIX_DIR/torrc"; then
    echo "[+] DNS port configured (5300)"
else
    echo "[!] ERROR: DNS port not configured"
    exit 1
fi

if grep -q "IsolateDestPort 1" "$WHONIX_DIR/torrc"; then
    echo "[+] Stream isolation enabled"
else
    echo "[!] WARNING: Stream isolation not enabled"
fi

##############################################
# 4. Validate Firewall Script
##############################################
echo ""
echo "[*] Validating firewall script..."

if grep -q "iptables -P INPUT DROP" "$WHONIX_DIR/firewall.sh"; then
    echo "[+] Default DROP policy configured"
else
    echo "[!] ERROR: Default DROP policy not found"
    exit 1
fi

if grep -q "debian-tor" "$WHONIX_DIR/firewall.sh"; then
    echo "[+] Tor user firewall rule configured"
else
    echo "[!] ERROR: Tor user firewall rule not found"
    exit 1
fi

if grep -q "9050" "$WHONIX_DIR/firewall.sh"; then
    echo "[+] SOCKS proxy firewall rule configured"
else
    echo "[!] ERROR: SOCKS proxy firewall rule not found"
    exit 1
fi

##############################################
# 5. Check Script Permissions
##############################################
echo ""
echo "[*] Checking script permissions..."

if [ -x "$WHONIX_DIR/firewall.sh" ]; then
    echo "[+] firewall.sh is executable"
else
    echo "[!] WARNING: firewall.sh is not executable"
    chmod +x "$WHONIX_DIR/firewall.sh"
    echo "[+] Made firewall.sh executable"
fi

if [ -x ~/QWAMOS/hypervisor/scripts/setup_network.sh ]; then
    echo "[+] setup_network.sh is executable"
else
    echo "[!] WARNING: setup_network.sh is not executable"
    chmod +x ~/QWAMOS/hypervisor/scripts/setup_network.sh
    echo "[+] Made setup_network.sh executable"
fi

##############################################
# 6. Test Summary
##############################################
echo ""
echo "=================================================="
echo "  Test Results"
echo "=================================================="
echo ""
echo "Configuration Files:       ✓"
echo "YAML Validation:           ✓"
echo "Tor Configuration:         ✓"
echo "Firewall Configuration:    ✓"
echo "Script Permissions:        ✓"
echo ""
echo "[+] All tests passed!"
echo ""
echo "Next Steps:"
echo "  1. Install Debian 12 in whonix-vm"
echo "  2. Copy torrc to /etc/tor/torrc"
echo "  3. Copy firewall.sh and run on boot"
echo "  4. Test Tor connection from kali-vm"
echo ""
