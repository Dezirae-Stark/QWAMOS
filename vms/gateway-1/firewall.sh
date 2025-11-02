#!/bin/bash
# Whonix Gateway Firewall Rules
# Purpose: Force ALL traffic through Tor, block clearnet
# QWAMOS Post-Quantum Security Project

set -e

echo "[*] Configuring Whonix Gateway firewall..."

##############################################
# CRITICAL: Default DROP policy
##############################################
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

echo "[+] Default DROP policy applied"

##############################################
# Flush existing rules
##############################################
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

echo "[+] Flushed existing rules"

##############################################
# Loopback (localhost)
##############################################
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

echo "[+] Loopback allowed"

##############################################
# Established connections
##############################################
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

echo "[+] Established connections allowed"

##############################################
# Allow Tor user to connect to Tor network
##############################################
# CRITICAL: ONLY debian-tor user can access internet
iptables -A OUTPUT -m owner --uid-owner debian-tor -j ACCEPT

echo "[+] Tor user allowed to connect to Tor network"

##############################################
# Allow incoming from client VMs (kali, disposable)
##############################################
# SOCKS proxy (9050)
iptables -A INPUT -i eth0 -p tcp --dport 9050 -s 10.152.152.0/24 -j ACCEPT

# Transparent proxy (9040)
iptables -A INPUT -i eth0 -p tcp --dport 9040 -s 10.152.152.0/24 -j ACCEPT

# Tor DNS (5300)
iptables -A INPUT -i eth0 -p udp --dport 5300 -s 10.152.152.0/24 -j ACCEPT

# Control port (9051) - LOCAL ONLY
iptables -A INPUT -i lo -p tcp --dport 9051 -j ACCEPT

echo "[+] Client VM connections allowed (SOCKS, TransPort, DNS)"

##############################################
# SSH (for management)
##############################################
iptables -A INPUT -i eth0 -p tcp --dport 22 -s 10.152.152.1 -j ACCEPT
iptables -A OUTPUT -o eth0 -p tcp --sport 22 -d 10.152.152.1 -j ACCEPT

echo "[+] SSH management allowed from host"

##############################################
# DHCP (if needed)
##############################################
iptables -A INPUT -i eth0 -p udp --dport 67:68 -j ACCEPT
iptables -A OUTPUT -o eth0 -p udp --dport 67:68 -j ACCEPT

echo "[+] DHCP allowed"

##############################################
# REJECT all other traffic (explicit denial)
##############################################
iptables -A INPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A OUTPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A FORWARD -j REJECT --reject-with icmp-port-unreachable

echo "[+] All other traffic rejected"

##############################################
# Save rules
##############################################
if command -v iptables-save &> /dev/null; then
    iptables-save > /etc/iptables/rules.v4
    echo "[+] Firewall rules saved to /etc/iptables/rules.v4"
else
    echo "[!] iptables-save not found, rules not persisted"
fi

echo "[+] Whonix Gateway firewall configuration complete!"

##############################################
# Display current rules
##############################################
echo ""
echo "Current iptables rules:"
iptables -L -v -n
