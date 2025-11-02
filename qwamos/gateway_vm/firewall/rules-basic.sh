#!/bin/bash
# QWAMOS Gateway Firewall - Basic Mode
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP
iptables -A OUTPUT -m owner --uid-owner debian-tor -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
echo "Gateway firewall (basic mode) applied."
