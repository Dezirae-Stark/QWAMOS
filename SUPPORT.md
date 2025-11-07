# QWAMOS Support & Troubleshooting Guide

**Version:** v1.0.0-qbamos-gold
**Last Updated:** 2025-11-07

---

## Table of Contents

1. [Getting Help](#getting-help)
2. [Common Issues](#common-issues)
3. [System Logs](#system-logs)
4. [Recovery Procedures](#recovery-procedures)
5. [Performance Optimization](#performance-optimization)
6. [FAQ](#frequently-asked-questions)
7. [Reporting Bugs](#reporting-bugs)

---

## Getting Help

### Official Support Channels

**GitHub Issues (Recommended):**
- URL: https://github.com/Dezirae-Stark/QWAMOS/issues
- Use for: Bug reports, feature requests, general questions
- Response time: 1-3 business days

**Email Support:**
- Email: clockwork.halo@tutanota.de
- Use for: Private issues, security concerns
- Response time: 3-7 business days

**Community (Coming Soon):**
- Matrix: (To be established)
- Forum: (To be established)

---

### Before Requesting Help

Please gather the following information:

1. **QWAMOS version:**
   ```bash
   git describe --tags
   cat /etc/qwamos/version
   ```

2. **Device information:**
   ```bash
   uname -a
   getprop ro.product.model
   getprop ro.build.version.release
   ```

3. **Installation method:**
   - Rooted or non-rooted?
   - Installation date
   - Deployment script used

4. **Error messages:**
   - Copy full error output
   - Check logs (see [System Logs](#system-logs))

5. **Steps to reproduce:**
   - What were you trying to do?
   - What happened instead?
   - Can you reproduce the issue?

---

## Common Issues

### Issue 1: VMs Won't Start

**Symptoms:**
- `virsh list --all` shows VMs as "shut off"
- Error: "KVM not available"
- QEMU fails to start

**Diagnosis:**
```bash
# Check if KVM module is loaded
lsmod | grep kvm
# Should show: kvm kvm_arm_host

# Check KVM device permissions
ls -l /dev/kvm
# Should show: crw-rw---- 1 root kvm

# Check if user is in kvm group
groups
# Should include: kvm
```

**Solutions:**

1. **Load KVM module (root required):**
   ```bash
   su -c "modprobe kvm"
   su -c "modprobe kvm-arm-host"
   ```

2. **Add user to kvm group:**
   ```bash
   su -c "usermod -aG kvm $(whoami)"
   # Logout and login again
   ```

3. **Fall back to user-mode emulation (non-rooted):**
   ```bash
   # Edit VM config to use TCG instead of KVM
   nano ~/QWAMOS/vms/gateway-1/config.json
   # Change: "accelerator": "kvm" → "accelerator": "tcg"
   ```

4. **Check VM disk image exists:**
   ```bash
   ls -lh /var/lib/qwamos/vms/gateway-1.qcow2
   # Should exist and be >1GB
   ```

---

### Issue 2: Tor Not Connecting

**Symptoms:**
- `systemctl status qwamos-tor` shows "failed"
- Error: "Tor can't connect to the network"
- `curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip` times out

**Diagnosis:**
```bash
# Check Tor service status
systemctl status qwamos-tor

# Check Tor logs
journalctl -u qwamos-tor -n 50

# Common errors:
# - "Failed to establish circuit"
# - "No route to network"
# - "Connection refused"
```

**Solutions:**

1. **Restart Tor service:**
   ```bash
   systemctl restart qwamos-tor
   sleep 30  # Wait for bootstrap
   curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip
   ```

2. **Configure Tor bridges (if Tor is blocked):**
   ```bash
   # Edit Tor config
   nano /etc/qwamos/tor/torrc

   # Add bridge lines (get from https://bridges.torproject.org/)
   UseBridges 1
   Bridge obfs4 [bridge_address]
   ClientTransportPlugin obfs4 exec /usr/bin/obfs4proxy

   # Restart Tor
   systemctl restart qwamos-tor
   ```

3. **Check firewall rules:**
   ```bash
   # Verify Tor ports not blocked
   su -c "iptables -L OUTPUT -n | grep 9050"
   # Should allow outbound on port 9050

   # If blocked, add rule:
   su -c "iptables -A OUTPUT -p tcp --dport 9050 -j ACCEPT"
   ```

4. **Verify system time (Tor requires accurate time):**
   ```bash
   date
   # If incorrect:
   su -c "ntpd -q -g"
   ```

---

### Issue 3: Panic Gesture Not Working

**Symptoms:**
- Pressing Power + VolUp + Fingerprint does nothing
- No wipe confirmation screen

**Diagnosis:**
```bash
# Check if panic gesture is enabled
cat /etc/qwamos/panic_gesture.json | jq '.enabled'
# Should return: true

# Check permissions
ls -l /usr/bin/panic_wipe.sh
# Should be executable: -rwxr-xr-x

# Test gesture detection
python3 system/panic/test_panic_gesture.py --dry-run
```

**Solutions:**

1. **Enable panic gesture:**
   ```bash
   nano /etc/qwamos/panic_gesture.json
   # Set: "enabled": true

   systemctl restart qwamos-panic-monitor
   ```

2. **Grant permissions (Android):**
   ```bash
   # QWAMOS needs permission to:
   # - Fingerprint sensor (BODY_SENSORS)
   # - Lock screen (DEVICE_ADMIN)

   # Grant via Settings > Apps > QWAMOS > Permissions
   ```

3. **Calibrate gesture timing:**
   ```bash
   # Edit timeout (default: 2000ms)
   nano /etc/qwamos/panic_gesture.json
   # Increase: "timeout_ms": 3000
   ```

4. **Manual test:**
   ```bash
   # Trigger panic manually
   python3 system/panic/manual_wipe.sh --dry-run
   # Should simulate wipe
   ```

---

### Issue 4: High CPU Usage / Performance Issues

**Symptoms:**
- Device running hot
- Battery draining quickly
- UI lag/stuttering

**Diagnosis:**
```bash
# Check CPU usage
top -b -n 1 | head -20

# Check which process is using CPU
ps aux --sort=-%cpu | head -10

# Common culprits:
# - qemu-system-aarch64 (VMs)
# - python3 (ML threat detection)
# - tor
```

**Solutions:**

1. **Reduce VM count:**
   ```bash
   # Stop unused VMs
   virsh shutdown workstation-1
   virsh shutdown kali-1

   # Only run gateway-1 (Tor routing)
   ```

2. **Disable ML threat detection (temporary):**
   ```bash
   systemctl stop qwamos-network-anomaly
   systemctl stop qwamos-filesystem-monitor
   systemctl stop qwamos-syscall-analyzer
   ```

3. **Lower ML model frequency:**
   ```bash
   # Edit threat detection config
   nano /etc/qwamos/ml_threat_detection.json

   # Reduce frequency:
   "network_anomaly": { "check_interval": 60 }  # 60s instead of 10s
   ```

4. **Use TCG instead of KVM (if on non-rooted):**
   ```bash
   # KVM is faster but TCG uses less power
   # Edit VM config
   nano ~/QWAMOS/vms/gateway-1/config.json
   # Change: "accelerator": "kvm" → "accelerator": "tcg"
   ```

---

### Issue 5: Encryption Volume Won't Mount

**Symptoms:**
- Error: "Failed to unlock volume"
- Wrong password message (but password is correct)
- Volume corrupted

**Diagnosis:**
```bash
# Check if volume file exists
ls -lh /var/lib/qwamos/volumes/workstation.vol

# Check volume header
python3 crypto/pq/pq_volume.py info --volume /var/lib/qwamos/volumes/workstation.vol

# Output should show:
# - Volume header version
# - Kyber-1024 public key hash
# - Argon2id KDF parameters
```

**Solutions:**

1. **Retry with correct password:**
   ```bash
   python3 crypto/pq/pq_volume.py mount \
     --volume /var/lib/qwamos/volumes/workstation.vol \
     --mountpoint /mnt/qwamos/workstation
   # Enter password carefully
   ```

2. **Restore from backup (if available):**
   ```bash
   cp /sdcard/qwamos_backup/workstation.vol.backup \
      /var/lib/qwamos/volumes/workstation.vol
   ```

3. **Check disk space:**
   ```bash
   df -h
   # Ensure /var/lib/qwamos has free space
   ```

4. **Verify Kyber keys:**
   ```bash
   ls -l /var/lib/qwamos/keys/kyber_private.key
   # Should exist (3168 bytes)

   # If missing, restore from backup:
   cp /sdcard/qwamos_backup/kyber_private.key \
      /var/lib/qwamos/keys/
   ```

---

### Issue 6: Network Routing Not Working

**Symptoms:**
- No internet connection
- Apps cannot connect
- Tor/I2P shows connected but no traffic

**Diagnosis:**
```bash
# Check network mode
cat /etc/qwamos/network_mode.json | jq '.mode'

# Test Tor connectivity
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip

# Check DNS
nslookup google.com 127.0.0.1:5300

# Check firewall rules
su -c "iptables -L -n -v"
```

**Solutions:**

1. **Restart network services:**
   ```bash
   systemctl restart qwamos-tor
   systemctl restart qwamos-dnscrypt
   systemctl restart qwamos-network-manager
   ```

2. **Switch network mode:**
   ```bash
   # Try direct mode (temporary, for testing)
   python3 network/network_manager.py --mode direct

   # If direct works, issue is with Tor/I2P
   ```

3. **Check iptables:**
   ```bash
   # Flush and reload firewall
   su -c "/etc/qwamos/firewall/reload.sh"
   ```

4. **Verify DNS:**
   ```bash
   # Test DNSCrypt
   dig @127.0.0.1 -p 5300 google.com

   # If fails, restart DNSCrypt
   systemctl restart qwamos-dnscrypt
   ```

---

## System Logs

### Log Locations

```bash
# System logs
/var/log/qwamos/system.log          # General system events
/var/log/qwamos/qwamosd.log         # Dom0 policy manager
/var/log/qwamos/network.log         # Network routing
/var/log/qwamos/tor.log             # Tor service
/var/log/qwamos/i2p.log             # I2P service
/var/log/qwamos/threat_detection.log # ML threat detection

# Hardware security (Phase 10)
/var/log/qwamos/ml_override.log     # ML bootloader override
/var/log/qwamos/firmware_integrity.log # Firmware monitoring
/var/log/qwamos/ab_isolation.log    # A/B partition isolation

# Android logs
logcat | grep QWAMOS
```

---

### Viewing Logs

```bash
# Real-time monitoring
tail -f /var/log/qwamos/system.log

# View recent errors
grep -i error /var/log/qwamos/*.log | tail -50

# View specific service
journalctl -u qwamos-tor -f

# Export logs for bug report
tar czf /sdcard/qwamos_logs.tar.gz /var/log/qwamos/
```

---

## Recovery Procedures

### Recovery Mode

If QWAMOS fails to boot:

```bash
# 1. Boot into Termux recovery
# (Device-specific - usually Power + Volume Down)

# 2. Mount QWAMOS partition
su -c "mount /dev/block/by-name/userdata /mnt"

# 3. Check logs
cat /mnt/data/qwamos/logs/boot.log

# 4. Repair broken services
su -c "systemctl reset-failed"
su -c "systemctl restart qwamosd"

# 5. If unrecoverable, rollback (see OPS_GUIDE.md)
```

---

### Factory Reset (Last Resort)

**WARNING:** This will DELETE ALL DATA.

```bash
# Backup critical files first
cp -r /var/lib/qwamos/keys /sdcard/qwamos_backup/
cp -r /var/lib/qwamos/volumes /sdcard/qwamos_backup/

# Factory reset
su -c "./scripts/factory_reset.sh"

# Confirm (type "RESET" in uppercase)
RESET

# This will:
# - Wipe all QWAMOS data
# - Restore default configuration
# - Remove VMs
# - Reset firewall rules
```

---

## Performance Optimization

### Reduce Resource Usage

1. **Disable unused features:**
   ```bash
   # Disable AI assistants
   systemctl stop qwamos-kali-gpt
   systemctl stop qwamos-claude
   systemctl stop qwamos-chatgpt

   # Disable ML threat detection
   systemctl stop qwamos-threat-detection

   # Disable I2P (if not used)
   systemctl stop qwamos-i2p
   ```

2. **Optimize VM resources:**
   ```bash
   # Reduce VM memory allocation
   nano ~/QWAMOS/vms/gateway-1/config.json
   # Change: "memory": "2048" → "memory": "1024"
   ```

3. **Lower ML model precision:**
   ```bash
   # Use INT8 quantization instead of FP32
   nano /etc/qwamos/ml_threat_detection.json
   # Change: "precision": "fp32" → "precision": "int8"
   ```

---

## Frequently Asked Questions

### General Questions

**Q: Is QWAMOS production-ready?**
A: QWAMOS v1.0.0 is production-ready for most features (Phases 1-11 complete). Phase 5 network isolation is 95% complete (device testing pending). See PROJECT_STATUS.md.

**Q: What devices are supported?**
A: Currently tested on ARM64 Android devices. Target device: Motorola Edge 2025 (Snapdragon 8 Gen 3). May work on other ARM64 devices with bootloader unlock support.

**Q: Do I need root access?**
A: Root is recommended for full features (KVM, hardware kill switches, kernel modules). Non-rooted mode works but with limitations (user-mode QEMU, no kill switches).

**Q: Can I use QWAMOS without Tor?**
A: Yes, network mode can be set to "direct" (no anonymization), but this defeats one of QWAMOS's core security features. Not recommended for privacy-sensitive use.

**Q: Does QWAMOS work with Magisk modules?**
A: Yes, QWAMOS is compatible with Magisk. Some Magisk modules may conflict (e.g., network modules). Test carefully.

---

### Security Questions

**Q: Is QWAMOS quantum-safe?**
A: Yes, QWAMOS uses post-quantum cryptography (Kyber-1024, ChaCha20-Poly1305) for volume encryption and keyboard encryption. Legacy crypto (AES, RSA, ECDH) is forbidden in SecureType keyboard.

**Q: Can QWAMOS protect against Pegasus/NSO Group?**
A: QWAMOS provides defense-in-depth (VM isolation, Tor routing, hardware kill switches, ML threat detection). Pegasus-level attacks require chaining multiple 0-days. QWAMOS raises the bar significantly but cannot guarantee protection against nation-state attackers with unlimited resources.

**Q: Does QWAMOS phone home?**
A: No. QWAMOS has ZERO telemetry. SecureType keyboard has NO INTERNET permission (OS-enforced). AI queries are routed through Tor (user-controlled). ML models run locally.

**Q: Can law enforcement recover data after panic gesture?**
A: After panic gesture, session keys are wiped (3-pass DoD secure wipe). Without keys, encrypted data is computationally infeasible to decrypt. However, if adversary has live memory dump BEFORE wipe, keys may be recoverable.

---

### Technical Questions

**Q: Why does QWAMOS use ChaCha20 instead of AES?**
A: ChaCha20-Poly1305 is 2.7x faster than AES-256-GCM on ARM64 (NEON acceleration). Also quantum-resistant (256-bit key).

**Q: Can I run Android apps in QWAMOS?**
A: Yes, Android apps run in the Android VM (android-vm). This is currently in configuration stage (Phase 3, 100% complete). Requires Android 14 system image.

**Q: How much storage does QWAMOS require?**
A: ~20GB for full installation (rooted). Breakdown: Kernel (32MB), VMs (5GB), encrypted volumes (10GB), binaries (2GB), logs (1GB), buffer (2GB).

**Q: What's the performance overhead of VMs?**
A: With KVM acceleration, overhead is ~5-10%. With TCG (user-mode emulation), overhead is ~50-70%. Rooted installation strongly recommended.

---

## Reporting Bugs

### Bug Report Template

Please use this template when filing GitHub issues:

```markdown
**QWAMOS Version:**
[Run: git describe --tags]

**Device Information:**
- Model: [e.g., Pixel 8, Motorola Edge 2025]
- Android Version: [e.g., Android 14]
- Root Status: [Rooted / Non-rooted]

**Installation Method:**
- [ ] Rooted deployment script
- [ ] Non-rooted deployment script
- [ ] Manual installation

**Issue Description:**
[Clear description of the problem]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [...]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Error Messages:**
```
[Paste full error output here]
```

**Logs:**
[Attach relevant logs from /var/log/qwamos/]

**Screenshots (if applicable):**
[Attach screenshots]

**Additional Context:**
[Any other relevant information]
```

---

### GitHub Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `security`: Security vulnerability (use email for private disclosure)
- `performance`: Performance optimization
- `help wanted`: Community assistance needed
- `good first issue`: Beginner-friendly issues

---

### Feature Requests

We welcome feature requests! Please use the GitHub issue template and include:

1. **Use case:** Why is this feature needed?
2. **Proposed solution:** How should it work?
3. **Alternatives considered:** Other approaches?
4. **Security implications:** Any security concerns?

---

## Contact Support

**GitHub Issues:** https://github.com/Dezirae-Stark/QWAMOS/issues
**Email:** clockwork.halo@tutanota.de
**Security Issues:** See [SECURITY.md](SECURITY.md)

---

**We're here to help!**

---

© 2025 First Sterling Capital, LLC · QWAMOS Project
Licensed under AGPL-3.0
