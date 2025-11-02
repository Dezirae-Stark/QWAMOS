#!/bin/bash
# QWAMOS Network Bridge Setup
# Creates isolated network bridges for VM compartmentalization

set -e

echo "=================================================="
echo "  QWAMOS Network Bridge Setup"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "[!] This script must be run as root"
    echo "    Run: sudo $0"
    exit 1
fi

##############################################
# 1. Create Isolated Network Bridge
##############################################
echo "[*] Creating isolated network bridge (qwamos-br0)..."

# Check if bridge already exists
if ip link show qwamos-br0 &> /dev/null; then
    echo "[!] Bridge qwamos-br0 already exists, deleting..."
    ip link set qwamos-br0 down
    ip link delete qwamos-br0
fi

# Create bridge
ip link add qwamos-br0 type bridge
ip addr add 10.152.152.1/24 dev qwamos-br0
ip link set qwamos-br0 up

echo "[+] Bridge qwamos-br0 created (10.152.152.1/24)"

##############################################
# 2. Create TAP Interface for whonix-vm
##############################################
echo "[*] Creating TAP interface for whonix-vm..."

if ip link show qwamos-whonix &> /dev/null; then
    echo "[!] TAP qwamos-whonix already exists, deleting..."
    ip link set qwamos-whonix down
    ip link delete qwamos-whonix
fi

ip tuntap add mode tap qwamos-whonix
ip link set qwamos-whonix master qwamos-br0
ip link set qwamos-whonix up

echo "[+] TAP qwamos-whonix created and attached to bridge"

##############################################
# 3. Create TAP Interface for kali-vm
##############################################
echo "[*] Creating TAP interface for kali-vm..."

if ip link show qwamos-kali &> /dev/null; then
    echo "[!] TAP qwamos-kali already exists, deleting..."
    ip link set qwamos-kali down
    ip link delete qwamos-kali
fi

ip tuntap add mode tap qwamos-kali
ip link set qwamos-kali master qwamos-br0
ip link set qwamos-kali up

echo "[+] TAP qwamos-kali created and attached to bridge"

##############################################
# 4. Create TAP Interface for disposable-vm
##############################################
echo "[*] Creating TAP interface for disposable-vm..."

if ip link show qwamos-disposable &> /dev/null; then
    echo "[!] TAP qwamos-disposable already exists, deleting..."
    ip link set qwamos-disposable down
    ip link delete qwamos-disposable
fi

ip tuntap add mode tap qwamos-disposable
ip link set qwamos-disposable master qwamos-br0
ip link set qwamos-disposable up

echo "[+] TAP qwamos-disposable created and attached to bridge"

##############################################
# 5. Create Separate Bridge for android-vm (NAT)
##############################################
echo "[*] Creating NAT bridge for android-vm (qwamos-nat)..."

if ip link show qwamos-nat &> /dev/null; then
    echo "[!] Bridge qwamos-nat already exists, deleting..."
    ip link set qwamos-nat down
    ip link delete qwamos-nat
fi

ip link add qwamos-nat type bridge
ip addr add 10.152.153.1/24 dev qwamos-nat
ip link set qwamos-nat up

# Create TAP for android-vm
if ip link show qwamos-android &> /dev/null; then
    echo "[!] TAP qwamos-android already exists, deleting..."
    ip link set qwamos-android down
    ip link delete qwamos-android
fi

ip tuntap add mode tap qwamos-android
ip link set qwamos-android master qwamos-nat
ip link set qwamos-android up

echo "[+] NAT bridge qwamos-nat created (10.152.153.1/24)"

##############################################
# 6. Enable NAT for android-vm
##############################################
echo "[*] Enabling NAT for android-vm..."

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# Add NAT rule (check if already exists)
if ! iptables -t nat -C POSTROUTING -s 10.152.153.0/24 -j MASQUERADE 2>/dev/null; then
    iptables -t nat -A POSTROUTING -s 10.152.153.0/24 -j MASQUERADE
    echo "[+] NAT rule added for android-vm"
else
    echo "[+] NAT rule already exists"
fi

##############################################
# 7. Block Direct Internet for Isolated Bridge
##############################################
echo "[*] Blocking direct internet for isolated network..."

# Drop forwarding from isolated bridge to external
if ! iptables -C FORWARD -i qwamos-br0 -o eth0 -j DROP 2>/dev/null; then
    iptables -A FORWARD -i qwamos-br0 -o eth0 -j DROP
fi

if ! iptables -C FORWARD -i qwamos-br0 -o wlan0 -j DROP 2>/dev/null; then
    iptables -A FORWARD -i qwamos-br0 -o wlan0 -j DROP
fi

echo "[+] Direct internet blocked for isolated network"

##############################################
# 8. Display Configuration
##############################################
echo ""
echo "=================================================="
echo "  Network Configuration Summary"
echo "=================================================="
echo ""

echo "Isolated Network (Tor-routed):"
echo "  Bridge: qwamos-br0 (10.152.152.1/24)"
echo "  - qwamos-whonix   -> whonix-vm (10.152.152.10)"
echo "  - qwamos-kali     -> kali-vm (10.152.152.20)"
echo "  - qwamos-disposable -> disposable-vm (10.152.152.30)"
echo ""

echo "NAT Network (Direct internet):"
echo "  Bridge: qwamos-nat (10.152.153.1/24)"
echo "  - qwamos-android  -> android-vm (10.152.153.10)"
echo ""

echo "Network Topology:"
echo ""
echo "  Internet"
echo "     |"
echo "  ┌──▼─────┐         ┌──────────┐"
echo "  │whonix  │         │android-vm│"
echo "  │-vm (GW)│         │(NAT)     │"
echo "  └───┬────┘         └──────────┘"
echo "      │"
echo "  ┌───┼────┐"
echo "  │        │"
echo "┌─▼──┐  ┌─▼────┐"
echo "│kali│  │dispos│"
echo "│-vm │  │-vm   │"
echo "└────┘  └──────┘"
echo ""

##############################################
# 9. Persistence (Optional)
##############################################
echo "[*] Making configuration persistent..."

# Create systemd service
cat > /etc/systemd/system/qwamos-network.service <<EOF
[Unit]
Description=QWAMOS Network Bridges
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash $(realpath $0)

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable qwamos-network.service

echo "[+] QWAMOS network bridges will be created on boot"

echo ""
echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "You can now start VMs using:"
echo "  python ~/QWAMOS/hypervisor/scripts/vm_manager.py start whonix-vm"
echo "  python ~/QWAMOS/hypervisor/scripts/vm_manager.py start kali-vm"
echo ""
