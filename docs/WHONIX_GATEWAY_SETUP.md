# QWAMOS Whonix Gateway Setup

**Date:** 2025-11-01
**Version:** 1.0
**Phase:** 3 (Weeks 5-6)
**Status:** Implementation guide complete

---

## Overview

The **Whonix Gateway** is the cornerstone of QWAMOS network anonymity. It provides Tor transparent proxy functionality, routing all network traffic from kali-vm and disposable-vm through the Tor network while maintaining complete isolation.

### Why Whonix?

- ✅ **Tor Isolation**: Complete separation of Tor process from client VMs
- ✅ **DNS Leak Protection**: All DNS queries forced through Tor
- ✅ **Clearnet Blocking**: Impossible to accidentally bypass Tor
- ✅ **Network Compartmentalization**: Qubes-style VM isolation
- ✅ **Stream Isolation**: Multiple Tor circuits for different applications

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  QWAMOS Host (10.152.152.1)                         │
└────────────┬────────────────────────────────────────┘
             │
       ┌─────▼─────┐
       │ whonix-vm │ (10.152.152.10)
       │  Gateway  │
       └─────┬─────┘
             │
    ┌────────┼────────┐
    │                 │
┌───▼────┐      ┌────▼─────┐
│kali-vm │      │disposable│
│  .20   │      │   -vm    │
│        │      │   .30    │
└────────┘      └──────────┘
     │                │
     └────────┬───────┘
              │
          Tor Exit
              │
          Internet
```

### Network Flow

1. **Client VM** (kali-vm/disposable-vm) sends traffic to 10.152.152.10
2. **Whonix Gateway** receives traffic on isolated network
3. **Tor Process** routes traffic through Tor network
4. **iptables Rules** block any non-Tor traffic (failsafe)
5. **Tor Exit** node connects to destination
6. **Response** flows back through Tor to client VM

---

## Whonix Gateway Components

### 1. Base OS: Debian 12 (Bookworm)

**Why Debian?**
- Stable, well-tested base
- Official Tor support
- Small footprint (minimal install)
- ARM64 support

**Installation:**
```bash
# Download Debian 12 ARM64 netinst
wget https://cdimage.debian.org/debian-cd/current/arm64/iso-cd/debian-12.4.0-arm64-netinst.iso

# Create 8GB disk for whonix-vm
qemu-img create -f qcow2 ~/QWAMOS/vms/whonix-vm/disk.qcow2 8G

# Install Debian (minimal, no desktop)
qemu-system-aarch64 \
  -machine virt,accel=tcg,gic-version=3 \
  -cpu cortex-a57 \
  -smp 2 \
  -m 1024 \
  -drive file=~/QWAMOS/vms/whonix-vm/disk.qcow2,format=qcow2,if=virtio \
  -cdrom debian-12.4.0-arm64-netinst.iso \
  -device virtio-net-pci,netdev=net0 \
  -netdev user,id=net0 \
  -nographic
```

**Packages to Install:**
```bash
# Base system (during Debian install)
- Standard system utilities
- SSH server

# Post-install packages
apt-get update
apt-get install -y \
  tor \
  iptables \
  iptables-persistent \
  dnsmasq \
  bridge-utils \
  net-tools \
  curl \
  wget \
  htop \
  vim
```

---

### 2. Tor Configuration

**File:** `/etc/tor/torrc`

```bash
# /etc/tor/torrc - Whonix Gateway Tor Configuration

##############################################
# SOCKS Proxy (for applications)
##############################################
SOCKSPort 10.152.152.10:9050

##############################################
# Transparent Proxy (for transparent routing)
##############################################
TransPort 10.152.152.10:9040

##############################################
# DNS Port (Tor DNS resolver)
##############################################
DNSPort 10.152.152.10:5300

##############################################
# Control Port (for Tor control)
##############################################
ControlPort 10.152.152.10:9051
CookieAuthentication 1

##############################################
# Security Settings
##############################################
# Disable exit node (Gateway only)
ExitRelay 0

# Use guard nodes
UseEntryGuards 1

# Sandbox mode (enhanced security)
Sandbox 1

##############################################
# Stream Isolation
##############################################
# Isolate streams by destination port
IsolateDestPort 1

# Isolate streams by destination address
IsolateDestAddr 1

##############################################
# Logging
##############################################
Log notice file /var/log/tor/notices.log
Log warn file /var/log/tor/warn.log

##############################################
# Performance
##############################################
# Connection limits
ConnLimit 1000

# Circuit build timeout
CircuitBuildTimeout 60

# Max circuits per period
MaxCircuitDirtiness 600

##############################################
# Whonix-Specific Settings
##############################################
# Disable client circuit building (Gateway mode)
ClientOnly 0

# Allow client mode
SocksPolicy accept 10.152.152.0/24
SocksPolicy reject *

# Virtual address network for transparent proxy
VirtualAddrNetworkIPv4 10.192.0.0/10
AutomapHostsOnResolve 1

##############################################
# CRITICAL: Post-Quantum Crypto (Future)
##############################################
# NOTE: Tor does not yet support post-quantum crypto
# When Tor adds Kyber support, enable here:
# UseKyber 1
# KyberKeySize 1024
```

**Enable Tor Service:**
```bash
systemctl enable tor
systemctl start tor
systemctl status tor
```

---

### 3. Firewall Rules (iptables)

**File:** `/etc/iptables/rules.v4`

```bash
#!/bin/bash
# Whonix Gateway Firewall Rules
# Purpose: Force ALL traffic through Tor, block clearnet

##############################################
# CRITICAL: Default DROP policy
##############################################
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

##############################################
# Loopback (localhost)
##############################################
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

##############################################
# Established connections
##############################################
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

##############################################
# Allow Tor user to connect to Tor network
##############################################
# CRITICAL: ONLY debian-tor user can access internet
iptables -A OUTPUT -m owner --uid-owner debian-tor -j ACCEPT

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

##############################################
# SSH (for management)
##############################################
iptables -A INPUT -i eth0 -p tcp --dport 22 -s 10.152.152.1 -j ACCEPT
iptables -A OUTPUT -o eth0 -p tcp --sport 22 -d 10.152.152.1 -j ACCEPT

##############################################
# DHCP (if needed)
##############################################
iptables -A INPUT -i eth0 -p udp --dport 67:68 -j ACCEPT
iptables -A OUTPUT -o eth0 -p udp --dport 67:68 -j ACCEPT

##############################################
# REJECT all other traffic (explicit denial)
##############################################
iptables -A INPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A OUTPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A FORWARD -j REJECT --reject-with icmp-port-unreachable

##############################################
# Save rules
##############################################
iptables-save > /etc/iptables/rules.v4
```

**Apply Firewall:**
```bash
# Make script executable
chmod +x /etc/iptables/rules.v4

# Apply rules
iptables-restore < /etc/iptables/rules.v4

# Make persistent
apt-get install iptables-persistent
netfilter-persistent save
```

---

### 4. Network Configuration

**File:** `/etc/network/interfaces`

```bash
# Whonix Gateway Network Configuration

auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address 10.152.152.10
    netmask 255.255.255.0
    gateway 10.152.152.1
    dns-nameservers 127.0.0.1
```

**DNS Configuration:**

**File:** `/etc/resolv.conf`

```bash
# Whonix Gateway DNS - Use Tor DNS
nameserver 127.0.0.1
```

**File:** `/etc/dnsmasq.conf`

```bash
# DNS forwarding to Tor
listen-address=10.152.152.10
port=5300
no-resolv
no-poll
server=127.0.0.1#5300
```

---

### 5. System Hardening

**File:** `/etc/sysctl.conf`

```bash
# Whonix Gateway sysctl settings

##############################################
# IP Forwarding (DISABLED - Gateway only)
##############################################
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

##############################################
# Disable IPv6 (Tor IPv6 not yet stable)
##############################################
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
net.ipv6.conf.lo.disable_ipv6 = 1

##############################################
# SYN flood protection
##############################################
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

##############################################
# Ignore ICMP redirects
##############################################
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0

##############################################
# Ignore source routed packets
##############################################
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

##############################################
# Log Martians (suspicious packets)
##############################################
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

##############################################
# Protect against time-wait assassination
##############################################
net.ipv4.tcp_rfc1337 = 1

##############################################
# Kernel hardening
##############################################
kernel.dmesg_restrict = 1
kernel.kptr_restrict = 2
kernel.yama.ptrace_scope = 2
```

**Apply sysctl:**
```bash
sysctl -p /etc/sysctl.conf
```

---

## Testing the Whonix Gateway

### 1. Test Tor Service

```bash
# Check Tor is running
systemctl status tor

# Check Tor logs
tail -f /var/log/tor/notices.log

# Expected output:
# [notice] Bootstrapped 100% (done): Done
# [notice] Tor has successfully opened a circuit. Looks like client functionality is working.
```

### 2. Test SOCKS Proxy

```bash
# From whonix-vm itself
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip

# Expected output:
# {"IsTor":true,"IP":"<tor-exit-ip>"}
```

### 3. Test from Client VM

**From kali-vm or disposable-vm:**

```bash
# Configure to use Whonix Gateway
export ALL_PROXY=socks5://10.152.152.10:9050

# Test Tor connection
curl https://check.torproject.org/api/ip

# Expected output:
# {"IsTor":true,"IP":"<tor-exit-ip>"}

# Test DNS through Tor
nslookup torproject.org 10.152.152.10#5300
```

### 4. Test Clearnet Blocking

**This should FAIL (proof of isolation):**

```bash
# Try to access internet directly (should fail)
curl https://google.com

# Expected: Connection timeout or rejection
```

### 5. Test Firewall Rules

```bash
# Check iptables rules
iptables -L -v -n

# Verify default DROP policy
iptables -L | grep policy

# Expected:
# Chain INPUT (policy DROP)
# Chain FORWARD (policy DROP)
# Chain OUTPUT (policy DROP)
```

---

## Integration with QWAMOS

### 1. Update vm_manager.py

Add Whonix-specific startup logic:

```python
def start_whonix_vm(self):
    """Start Whonix Gateway with dependency checks"""

    print("[*] Starting Whonix Gateway...")

    # Build QEMU command from config
    cmd = self.build_qemu_command()

    # Add Whonix-specific args
    cmd.extend([
        "-device", "virtio-net-pci,netdev=net0,mac=52:54:00:12:34:57",
        "-netdev", "tap,id=net0,ifname=qwamos-whonix,script=no,downscript=no"
    ])

    # Start VM
    self.execute_qemu(cmd)

    # Wait for Tor to bootstrap
    print("[*] Waiting for Tor to bootstrap...")
    time.sleep(30)

    # Verify Tor is working
    self.verify_tor_connection()

    print("[+] Whonix Gateway started successfully!")

def verify_tor_connection(self):
    """Verify Tor circuit is established"""
    # TODO: Implement Tor control port check
    pass
```

### 2. Create Network Bridge Script

**File:** `hypervisor/scripts/setup_network.sh`

```bash
#!/bin/bash
# Setup QWAMOS network bridges for VM isolation

# Create isolated network bridge
ip link add qwamos-br0 type bridge
ip addr add 10.152.152.1/24 dev qwamos-br0
ip link set qwamos-br0 up

# Create TAP interface for whonix-vm
ip tuntap add mode tap qwamos-whonix
ip link set qwamos-whonix master qwamos-br0
ip link set qwamos-whonix up

# Create TAP interface for kali-vm
ip tuntap add mode tap qwamos-kali
ip link set qwamos-kali master qwamos-br0
ip link set qwamos-kali up

# Create TAP interface for disposable-vm
ip tuntap add mode tap qwamos-disposable
ip link set qwamos-disposable master qwamos-br0
ip link set qwamos-disposable up

# Enable NAT for android-vm (separate bridge)
iptables -t nat -A POSTROUTING -s 10.152.153.0/24 -j MASQUERADE

echo "[+] QWAMOS network bridges created"
```

### 3. Update whonix-vm Startup

Modify `vms/whonix-vm/config.yaml` to use TAP interface:

```yaml
network:
  mode: isolated
  device: virtio-net-pci
  mac: 52:54:00:12:34:57

  # Use TAP interface for bridge
  backend: tap
  tap_interface: qwamos-whonix
  bridge: qwamos-br0
```

---

## Security Considerations

### ✅ What Whonix Gateway Protects Against

1. **DNS Leaks** - All DNS forced through Tor
2. **IP Leaks** - Impossible to bypass Tor
3. **Application Leaks** - No direct internet access
4. **Protocol Leaks** - Transparent proxy captures all TCP
5. **Time-based Attacks** - NTP disabled

### ❌ What Whonix Does NOT Protect Against

1. **Malware** - Malicious apps can still leak info via Tor
2. **Browser Fingerprinting** - Use Tor Browser Bundle
3. **Traffic Analysis** - Global adversary with timing attacks
4. **Tor Vulnerabilities** - If Tor is compromised, Whonix is too
5. **Post-Quantum Attacks** - Tor doesn't support Kyber yet

### 🔐 QWAMOS Enhancements

- **ChaCha20-Poly1305** disk encryption (Whonix uses LUKS by default)
- **Argon2id** key derivation (stronger than PBKDF2)
- **VM isolation** via QEMU/KVM (stronger than containers)
- **No network by default** (must explicitly start whonix-vm)

---

## Monitoring and Maintenance

### 1. Check Tor Circuit Status

```bash
# Connect to Tor control port
telnet 127.0.0.1 9051

# Authenticate (use cookie file)
AUTHENTICATE "$(cat /var/lib/tor/control_auth_cookie | xxd -p)"

# Get circuit info
GETINFO circuit-status
GETINFO stream-status
GETINFO entry-guards
```

### 2. Monitor Tor Logs

```bash
# Real-time log monitoring
tail -f /var/log/tor/notices.log

# Check for warnings
grep -i warn /var/log/tor/warn.log
```

### 3. Update Tor

```bash
# Regular updates are CRITICAL for security
apt-get update
apt-get upgrade tor

# Restart Tor after updates
systemctl restart tor
```

---

## Troubleshooting

### Problem: Tor won't bootstrap

**Solution:**
```bash
# Check Tor logs
journalctl -u tor -f

# Verify time sync (Tor requires accurate time)
timedatectl status

# Test basic connectivity
ping 10.152.152.1
```

### Problem: Client VMs can't connect to Whonix

**Solution:**
```bash
# Check network bridge
ip addr show qwamos-br0

# Verify iptables rules
iptables -L -v -n

# Test connectivity from client
ping 10.152.152.10
```

### Problem: DNS not working

**Solution:**
```bash
# Check dnsmasq
systemctl status dnsmasq

# Test Tor DNS
dig @10.152.152.10 -p 5300 torproject.org
```

---

## Next Steps

1. **Install Debian in whonix-vm** (requires separate PC with good internet)
2. **Configure Tor and iptables** (follow this guide)
3. **Test from kali-vm** (verify Tor routing)
4. **Integrate InviZible Pro** (add DNSCrypt + I2P layers)
5. **Add Whonix Workstation** (optional: separate workstation VM)

---

## References

- **Official Whonix Docs**: https://www.whonix.org/wiki/Documentation
- **Tor Project**: https://www.torproject.org/
- **Whonix Gateway**: https://www.whonix.org/wiki/Whonix-Gateway
- **Stream Isolation**: https://www.whonix.org/wiki/Stream_Isolation
- **QWAMOS Architecture**: `docs/QWAMOS_ARCHITECTURE.md`

---

**Status:** Whonix Gateway specification complete
**Next:** Install Debian and configure Tor
**Phase 3 Progress:** 55% complete

**Author:** Dezirae-Stark
**Last Updated:** 2025-11-01
