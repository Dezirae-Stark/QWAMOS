#!/bin/bash
# QWAMOS Kali Setup Script

echo "[*] Updating Kali repositories..."
apt-get update

echo "[*] Installing Kali tools..."
apt-get install -y kali-linux-core

echo "[*] Installing additional tools..."
apt-get install -y nmap sqlmap metasploit-framework burpsuite

echo "[+] Kali setup complete!"
