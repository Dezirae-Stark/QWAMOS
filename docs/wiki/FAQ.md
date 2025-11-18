# Frequently Asked Questions (FAQ)

**[← Back to Home](Home)**

---

## General Questions

### 1. What is QWAMOS?

QWAMOS (Quantum-Wrapped Android Mobile Operating System) is a privacy-first, security-hardened Android environment that provides military-grade app isolation through virtual machines, post-quantum cryptography for data encryption, and anonymous networking via Tor/I2P.

Think of it as "Qubes OS for Android" - each app runs in its own isolated VM to prevent cross-contamination.

---

### 2. Do I need to root my device?

**No, rooting is optional.** QWAMOS works on non-rooted devices using:
- **PRoot mode:** Userspace isolation (no root required)
- **Chroot mode:** Requires root for better performance
- **KVM mode:** Requires root + custom kernel for hardware acceleration

**Recommendation:** Start with PRoot mode, upgrade to KVM if you need performance.

---

### 3. Which devices are supported?

**Minimum Requirements:**
- ARM64 CPU (ARMv8-A or newer)
- 4GB+ RAM
- 64GB+ storage
- Android 10+

**Best Performance (KVM Support):**
- Snapdragon 8 Gen 2/3
- Google Pixel 8/9 (with custom kernel)
- OnePlus 12 (with custom ROM)
- Samsung Galaxy S24 (with custom kernel)

See [Installation Guide](Installation-&-Setup-Guide) for device-specific instructions.

---

### 4. How is QWAMOS different from GrapheneOS?

| Feature | QWAMOS | GrapheneOS |
|---------|--------|------------|
| **Isolation** | VM per app | Android sandbox |
| **Encryption** | PQC (Kyber-1024) | Classical (AES) |
| **Anonymity** | Tor/I2P built-in | Manual VPN |
| **Platform** | Any Android 10+ | Pixel only |
| **Root** | Optional | Not recommended |

**QWAMOS** focuses on **VM isolation + PQC encryption**.
**GrapheneOS** focuses on **hardened Android OS**.

Both can be used together: GrapheneOS as base OS, QWAMOS for sensitive apps.

---

### 5. Is QWAMOS legal?

**Yes, QWAMOS is completely legal.** Using encryption and anonymization tools is legal in most countries.

**Exceptions:**
- Some countries ban/restrict Tor, VPNs, encryption (China, Russia, Iran, UAE)
- Check local laws before using QWAMOS in restricted jurisdictions

**QWAMOS is designed for legitimate privacy, not illegal activity.**

---

## Installation & Setup

### 6. Can I install QWAMOS from Google Play?

**No. QWAMOS is NOT available on Google Play.**

Install via:
1. **Termux (F-Droid):** Manual installation - [Installation Guide](Installation-&-Setup-Guide)
2. **GitHub Releases:** Pre-built images (coming soon)
3. **Custom ROM:** Full system integration (advanced)

**Never install from Google Play or APK sites** - these are fake/malware.

---

### 7. How much storage does QWAMOS need?

**Minimum:** 64GB total device storage
- QWAMOS base: 2GB
- Each VM: 5-30GB (depending on usage)
- Gateway (Tor/I2P): 500MB

**Recommended:** 128GB+ for 3-5 VMs

**Example:**
```
Device: 128GB storage
- Android OS: 20GB
- QWAMOS: 2GB
- VM 1 (Browser): 10GB
- VM 2 (Messaging): 5GB
- VM 3 (Development): 30GB
- Free space: 61GB
```

---

### 8. Can I use QWAMOS without Termux?

**Not yet.** Currently, QWAMOS requires Termux for:
- Python runtime
- QEMU emulation
- Script execution

**Future:** Native Android app (no Termux) planned for Q2 2026.

---

## Performance & Hardware

### 9. Why is my VM so slow?

**Likely using QEMU (software emulation)**, which is 10-20× slower than native.

**Solutions:**

**1. Enable KVM (hardware acceleration):**
```bash
# Check if KVM available
ls /dev/kvm

# If not, need custom kernel with KVM support
```

**2. Reduce VM resource allocation:**
```bash
# Edit VM config
nano ~/.qwamos/vms/your-vm/config.ini

# Reduce RAM:
ram = 1024  # Instead of 2048

# Reduce CPUs:
cpus = 2  # Instead of 4
```

**3. Close background VMs:**
```bash
# Only run one VM at a time
./vm/stop_vm.sh all
./vm/start_vm.sh your-vm
```

---

### 10. How do I enable KVM acceleration?

**Requirements:**
1. **CPU with virtualization extensions** (most modern ARM chips)
2. **Custom kernel with `CONFIG_KVM=y`**
3. **Root access** to set `/dev/kvm` permissions

**Steps:**

**Check KVM availability:**
```bash
ls -l /dev/kvm
# If exists: crw-rw---- 1 root kvm 10, 232 Nov 18 12:00 /dev/kvm
```

**Set permissions:**
```bash
su
chmod 666 /dev/kvm
```

**Create KVM-enabled VM:**
```bash
./scripts/create_vm.sh --name fast-vm --type browser --kvm
```

**Verify:**
```bash
./scripts/vm_info.sh fast-vm | grep Acceleration
# Output: Acceleration: KVM (hardware)
```

See [Installation Guide](Installation-&-Setup-Guide#method-2-rooted-device-with-kvm) for detailed instructions.

---

### 11. Which devices have KVM support?

**Confirmed Working:**
- ✅ Google Pixel 8/9 (with custom kernel from XDA)
- ✅ OnePlus 12 (with OxygenOS custom ROM)
- ✅ Samsung Galaxy S24 (with OneUI custom kernel)
- ✅ Xiaomi 14 Pro (with MIUI custom ROM)

**Check Your Device:**
```bash
# Run hardware test suite
cd tests/kvm_hardware_suite/
chmod +x kvm_hardware_check.sh
./kvm_hardware_check.sh
```

**Custom Kernels:** Check XDA Developers forum for your device.

---

### 12. How much battery does QWAMOS use?

**QEMU Mode (software emulation):**
- Active VM: 15-25% battery/hour
- Multiple VMs: 30-50% battery/hour
- **Battery life:** 2-3 hours active use

**KVM Mode (hardware acceleration):**
- Active VM: 5-10% battery/hour
- Multiple VMs: 10-15% battery/hour
- **Battery life:** 6-8 hours active use

**Power Saving Tips:**
```bash
# Suspend VMs when not in use
./vm/pause_vm.sh your-vm

# Reduce VM CPU count
# Edit config: cpus = 2

# Use lightweight VMs (Alpine Linux instead of full Android)
```

---

## Security & Privacy

### 13. Can VMs communicate with each other?

**No, by default VMs are completely isolated.**

Inter-VM communication is blocked by:
- Separate network namespaces (different IP addresses)
- Firewall rules (iptables DROP)
- No shared filesystem

**If you need VM-to-VM communication** (e.g., development), explicitly allow:
```bash
# Edit firewall config
nano ~/.qwamos/config/firewall.conf

# Add rule:
[allow_vm_to_vm]
source = 10.8.0.2  # VM 1
destination = 10.8.0.3  # VM 2
protocol = tcp
port = 8080
```

**Security Warning:** Only allow for trusted VMs.

---

### 14. Is Kyber-1024 really quantum-resistant?

**Yes, Kyber-1024 is a NIST-standardized post-quantum algorithm** (FIPS 203).

**Security Against Quantum Computers:**
- **RSA-2048:** Broken by Shor's algorithm (~hours on quantum computer)
- **Kyber-1024:** Requires 2^254 operations (infeasible even for quantum computers)

**Assumptions:**
- Based on Learning With Errors (LWE) problem
- No known quantum algorithm solves LWE efficiently
- Conservative parameter set (1024-bit for future-proofing)

**What if Kyber is broken?**
- QWAMOS supports **algorithm agility** (easy to swap algorithms)
- Hybrid encryption (Kyber + RSA) planned for extra security

---

### 15. Does QWAMOS protect against government surveillance?

**It depends on the threat model:**

**✅ QWAMOS protects against:**
- Mass surveillance (ISP logging, corporate tracking)
- Forensic analysis (device seizure, disk imaging)
- App-level spyware (cross-contamination)
- Quantum computer attacks (future-proof encryption)

**⚠️ Limited protection against:**
- Targeted attacks with zero-days
- Baseband/cellular tracking (SIM card required)
- Evil maid attacks (physical access to powered-on device)

**❌ QWAMOS does NOT protect against:**
- Coercion/torture (rubber-hose cryptanalysis)
- Hardware implants (compromised device from factory)
- Endpoint security (keylogger, screen capture)

**Best Practice:** Use QWAMOS + operational security (OPSEC) training.

---

### 16. What happens if I forget my passphrase?

**Your data is permanently lost.** Kyber-1024 encryption cannot be brute-forced.

**Prevention:**
```bash
# Enable passphrase recovery during setup
./crypto/enable_recovery.sh

# Stores encrypted backup of master key
# Requires answering security questions
```

**Alternative: Key Splitting**
```bash
# Split master key into 3 shares (2-of-3 required)
./crypto/split_key.sh --threshold 2 --shares 3

# Store shares in separate locations:
# - Share 1: Password manager
# - Share 2: Trusted friend
# - Share 3: Bank safe deposit box
```

**Last Resort:** Factory reset (lose all VMs).

---

## Gateway & Anonymity

### 17. Can I use QWAMOS without Tor?

**Yes, Tor is optional.** You can configure VMs to use:
- **Direct internet** (no anonymization)
- **VPN only** (partial anonymization)
- **I2P only** (darknet anonymization)
- **Custom proxy** (SOCKS5/HTTP)

**Configuration:**
```bash
# Edit gateway config
nano ~/.qwamos/config/gateway.conf

# Set VM route:
[vm:development]
route = direct  # No Tor/I2P
dns = cloudflare  # Regular DNS
```

**Security Warning:** Direct internet exposes your IP address.

---

### 18. How do I access .onion sites?

**Tor hidden services (.onion) work automatically** if gateway is configured.

**Steps:**

1. **Ensure gateway running:**
```bash
./gateway/start_gateway.sh
```

2. **Connect to VM:**
```bash
./vm/connect_vm.sh browser-vm
```

3. **Use .onion address in browser:**
```bash
# Inside VM
curl https://www.torproject.org.onion
```

**Or configure Tor Browser:**
```bash
# Install Tor Browser in VM
apk add tor-browser

# Launch
tor-browser
```

---

### 19. Can I run a Tor hidden service from a VM?

**Yes, VMs can host hidden services.**

**Configuration:**

```bash
# Inside VM, install Tor
apk add tor

# Edit /etc/tor/torrc
HiddenServiceDir /var/lib/tor/hidden_service/
HiddenServicePort 80 127.0.0.1:8080

# Start Tor
rc-service tor start

# Get .onion address
cat /var/lib/tor/hidden_service/hostname
# Output: abc123def456ghi789.onion
```

**Start web server on port 8080:**
```bash
# Simple Python HTTP server
python3 -m http.server 8080
```

**Access from outside:**
```
http://abc123def456ghi789.onion/
```

---

### 20. How do I troubleshoot gateway issues?

**Problem:** VM has no internet connection

**Diagnosis:**

**1. Check gateway status:**
```bash
./gateway/status.sh

# Expected output:
# Tor: ✅ Running (127.0.0.1:9050)
# I2P: ✅ Running (127.0.0.1:4444)
# DNSCrypt: ✅ Running (127.0.0.1:5354)
```

**2. Test Tor proxy:**
```bash
curl -x socks5h://127.0.0.1:9050 https://check.torproject.org/api/ip

# Expected: {"IsTor":true}
```

**3. Check firewall rules:**
```bash
su
iptables -L -n -v | grep QWAMOS
```

**4. Check VM routing:**
```bash
# Inside VM
ip route
# Expected: default via 10.8.0.1 dev eth0

ping 10.8.0.1  # Should respond
```

**5. Check logs:**
```bash
cat ~/.qwamos/logs/gateway.log
```

**Common Fixes:**
- Restart gateway: `./gateway/restart.sh`
- Restart InviZible Pro app
- Check Android VPN settings (no conflicting VPNs)
- Verify Termux has network permissions

---

## Panic & Emergency Features

### 21. How fast is the emergency wipe?

**Wipe Speeds:**

| Level | Time | Method |
|-------|------|--------|
| **Quick** | 1-2 seconds | Delete encryption keys only |
| **Standard** | 10-30 seconds | Keys + 1-pass overwrite |
| **Thorough** | 2-5 minutes | Keys + 3-pass overwrite |
| **Paranoid** | 10-30 minutes | Keys + 7-pass Gutmann |

**Quick wipe is sufficient** for most threats (forensic recovery impossible without keys).

**Test wipe speed:**
```bash
./panic/benchmark_wipe.sh --level quick
# Output: Quick wipe: 1.2 seconds
```

---

### 22. What is a duress password?

**Duress password** unlocks a fake decoy system instead of real data.

**How it works:**
1. Set up decoy system with fake data
2. Configure duress password: `wrong-but-plausible-password`
3. If coerced, enter duress password
4. Fake system loads (real data stays encrypted)
5. Optional: Silent alert sent to trusted contact

**Setup:**
```bash
./panic/configure_duress.sh --create-decoy

# Follow prompts:
# Real passphrase: ****************
# Duress passphrase: ************
# Decoy data: ~/fake-data/
```

---

## Troubleshooting

### 23. VM won't start - "Permission denied"

**Problem:** `/dev/kvm` permission error

**Solution:**
```bash
# Option 1: Fix permissions (temporary)
su
chmod 666 /dev/kvm

# Option 2: Add user to kvm group (permanent)
su
groupadd kvm
chown root:kvm /dev/kvm
chmod 660 /dev/kvm
usermod -aG kvm $(whoami)
# Log out and back in
```

---

### 24. Encryption key error - "Failed to decrypt VM"

**Problem:** Passphrase incorrect or key corrupted

**Solutions:**

**1. Verify passphrase:**
```bash
# Try recovery passphrase
./crypto/recover_key.sh --vm your-vm
```

**2. Check key backup:**
```bash
ls ~/.qwamos/keys/backup/
# If backup exists, restore:
./crypto/restore_key.sh --vm your-vm --from-backup
```

**3. No backup = data lost permanently**

**Prevention:**
```bash
# Enable weekly backups
./crypto/enable_auto_backup.sh --frequency weekly
```

---

### 25. How do I update QWAMOS?

**Update Process:**

```bash
cd ~/QWAMOS

# Pull latest changes
git pull origin master

# Update dependencies
pip install -r requirements.txt --upgrade

# Update VM base images
./scripts/update_vms.sh

# Restart VMs
./vm/restart_all.sh
```

**Check version:**
```bash
cat VERSION
# Output: v1.2.0
```

**Release notes:** Check [Releases](https://github.com/Dezirae-Stark/QWAMOS/releases)

---

## Getting More Help

**If your question isn't answered here:**

1. **Search GitHub Issues:** https://github.com/Dezirae-Stark/QWAMOS/issues
2. **Check Wiki:** Other pages may have your answer
3. **Ask on Discussions:** https://github.com/Dezirae-Stark/QWAMOS/discussions
4. **Email:** qwamos@tutanota.com

**For security issues:** qwamos@tutanota.com (confidential)

---

**[← Back to Home](Home)**
