#!/bin/bash
# QWAMOS Gateway VM Firewall - Strict Mode
# ONLY Tor egress allowed
# IMS/VoLTE BLOCKED (prevents IMS registration tracking)
# Maximum privacy mode

set -e

echo "Applying QWAMOS firewall rules: STRICT mode"

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

# ONLY Tor tunnel (tun0)
iptables -A OUTPUT -o tun0 -j ACCEPT
iptables -A INPUT -i tun0 -m state --state ESTABLISHED,RELATED -j ACCEPT

# Block ALL rmnet (baseband) direct egress
iptables -A OUTPUT -o rmnet_data+ -j REJECT --reject-with icmp-net-unreachable
iptables -A OUTPUT -o rmnet+ -j REJECT --reject-with icmp-net-unreachable

# Block clearnet DNS (force DNS over Tor)
iptables -A OUTPUT -p udp --dport 53 -j REJECT --reject-with icmp-port-unreachable
iptables -A OUTPUT -p tcp --dport 53 -j REJECT --reject-with tcp-reset

# Block IMS/VoLTE registration (prevents tracking via IMS APN)
iptables -A OUTPUT -p udp -m multiport --dports 5060,5061,500,4500 -j REJECT --reject-with icmp-port-unreachable
iptables -A OUTPUT -p tcp -m multiport --dports 5060,5061 -j REJECT --reject-with tcp-reset

# Block WiFi direct egress (force through Tor)
iptables -A OUTPUT -o wlan0 -j REJECT --reject-with icmp-net-unreachable

# Allow established connections (Tor only)
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Log ALL dropped packets (for audit)
iptables -A INPUT -j LOG --log-prefix "GATEWAY-STRICT-IN-DROP: " --log-level 4
iptables -A OUTPUT -j LOG --log-prefix "GATEWAY-STRICT-OUT-DROP: " --log-level 4
iptables -A FORWARD -j LOG --log-prefix "GATEWAY-STRICT-FWD-DROP: " --log-level 4

# Final DROP
iptables -A INPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A OUTPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A FORWARD -j REJECT --reject-with icmp-port-unreachable

echo "✅ STRICT firewall rules applied"
echo "   ⚠️  WARNING: MAXIMUM PRIVACY MODE"
echo "   - Tor egress: ALLOWED"
echo "   - IMS/VoLTE: BLOCKED (no calls/SMS)"
echo "   - Cellular data: BLOCKED"
echo "   - WiFi: BLOCKED"
echo "   - All other traffic: BLOCKED"
echo ""
echo "   Voice calls will NOT work in strict mode!"
echo "   Use basic mode if you need telephony."
