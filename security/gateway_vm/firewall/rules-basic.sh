#!/bin/bash
# QWAMOS Gateway VM Firewall - Basic Mode
# Allows Tor/I2P/DNSCrypt egress
# Permits telephony (IMS/VoLTE) for calls

set -e

echo "Applying QWAMOS firewall rules: BASIC mode"

# Clear existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Default policies: DROP everything
iptables -P INPUT DROP
iptables -P OUTPUT DROP
iptables -P FORWARD DROP

# Loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Tor/I2P tunnels (tun0)
iptables -A OUTPUT -o tun0 -j ACCEPT
iptables -A INPUT -i tun0 -m state --state ESTABLISHED,RELATED -j ACCEPT

# DNS over Tor (DNSCrypt fallback)
iptables -A OUTPUT -p udp --dport 5300 -j ACCEPT
iptables -A INPUT -p udp --sport 5300 -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow telephony to baseband (for calls/SMS)
# SIP (VoLTE/IMS)
iptables -A OUTPUT -o rmnet_data+ -p udp -m multiport --dports 5060,5061 -j ACCEPT
iptables -A INPUT -i rmnet_data+ -p udp -m multiport --sports 5060,5061 -m state --state ESTABLISHED,RELATED -j ACCEPT

# IPsec (for VoLTE)
iptables -A OUTPUT -o rmnet_data+ -p udp -m multiport --dports 500,4500 -j ACCEPT
iptables -A INPUT -i rmnet_data+ -p udp -m multiport --sports 500,4500 -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow DNS to cellular (basic mode only)
iptables -A OUTPUT -o rmnet_data+ -p udp --dport 53 -j ACCEPT
iptables -A INPUT -i rmnet_data+ -p udp --sport 53 -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "GATEWAY-BASIC-IN-DROP: " --log-level 4
iptables -A OUTPUT -j LOG --log-prefix "GATEWAY-BASIC-OUT-DROP: " --log-level 4
iptables -A FORWARD -j LOG --log-prefix "GATEWAY-BASIC-FWD-DROP: " --log-level 4

# Final DROP
iptables -A INPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A OUTPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A FORWARD -j REJECT --reject-with icmp-port-unreachable

echo "✅ BASIC firewall rules applied"
echo "   - Tor/I2P/DNSCrypt egress: ALLOWED"
echo "   - IMS/VoLTE telephony: ALLOWED"
echo "   - Cellular DNS: ALLOWED"
echo "   - All other traffic: BLOCKED"
