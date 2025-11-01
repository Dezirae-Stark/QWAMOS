# QWAMOS Phase 3: Hypervisor (KVM/QEMU) Setup

**Project**: QWAMOS - Qubes Whonix Advanced Mobile Operating System
**Phase**: 3 - Hypervisor & Virtual Machine Architecture
**Date**: November 1, 2025
**Status**: In Progress
**Version**: 1.0

---

## Executive Summary

Phase 3 implements the hypervisor layer that enables QWAMOS to run multiple isolated virtual machines. This is the core architectural component that transforms QWAMOS from a traditional mobile OS into a Qubes-style compartmentalized system where Android itself runs as a guest VM.

**Key Objectives:**
- Configure KVM (Kernel Virtual Machine) hypervisor
- Set up QEMU for ARM64 virtualization
- Create VM management infrastructure
- Build and test the first VM (android-vm)
- Implement VM-to-VM isolation

---

## 1. Architecture Overview

### 1.1 Hypervisor Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    QWAMOS Host System                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Linux Kernel 6.6 LTS (KVM-enabled)            │ │
│  │  • CONFIG_KVM=y (ARM64 virtualization)                │ │
│  │  • CONFIG_VHOST=y (virtio acceleration)               │ │
│  │  • CONFIG_TUN=y (network virtualization)              │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ▲                                  │
│                           │                                  │
│  ┌────────────────────────┴───────────────────────────────┐ │
│  │              QEMU System Emulator (ARM64)              │ │
│  │  • Version: 9.1.1                                      │ │
│  │  • Machine: virt (ARM Virtual Machine)                │ │
│  │  • CPU: cortex-a57 (4 cores)                          │ │
│  │  • Acceleration: KVM (when on real hardware)          │ │
│  └────────────────────────────────────────────────────────┘ │
│                           ▲                                  │
│                           │                                  │
│  ┌────────────────────────┴───────────────────────────────┐ │
│  │             VM Management Layer (Python)               │ │
│  │  • qwamos-vm-manager: Start/stop/monitor VMs          │ │
│  │  • Configuration: /etc/qwamos/vms/                    │ │
│  │  • Logs: /var/log/qwamos/vms/                         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
┌───────▼──────┐  ┌────────▼─────┐  ┌────────▼─────┐
│  android-vm  │  │  whonix-vm   │  │   kali-vm    │
│              │  │              │  │              │
│ Android 14   │  │ Whonix GW    │  │ Kali Linux   │
│ AOSP         │  │ Tor Gateway  │  │ Pentest      │
│              │  │              │  │              │
│ 4GB RAM      │  │ 1GB RAM      │  │ 2GB RAM      │
│ 32GB disk    │  │ 8GB disk     │  │ 16GB disk    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 1.2 VM Isolation Model

Each VM operates in complete isolation:

**Memory Isolation:**
- Dedicated RAM allocation per VM
- No shared memory between VMs
- Host memory protection enabled

**CPU Isolation:**
- vCPU pinning (optional for performance)
- CPU time limits (cgroups)
- Separate scheduling domains

**Network Isolation:**
- Each VM has isolated virtual network
- TAP/TUN devices with unique MACs
- Firewall rules between VMs
- Optional routing through Whonix Gateway

**Storage Isolation:**
- Encrypted QCOW2 disk images per VM
- ChaCha20-Poly1305 encryption (NOT AES)
- Read-only host filesystem access (if any)

---

## 2. VM Specifications

### 2.1 android-vm (Primary Android Guest)

**Purpose:** Run Android 14 AOSP as isolated guest

**Specifications:**
```yaml
name: android-vm
type: android
os: Android 14 AOSP
cpu: 4 cores (cortex-a57)
ram: 4096 MB
disk: 32 GB (qcow2, encrypted)
network: virtio-net (NAT)
display: virtio-gpu
audio: virtio-snd
usb: xhci controller
```

**Network Configuration:**
- IP: 10.0.2.15/24 (QEMU default NAT)
- Gateway: 10.0.2.2 (QEMU host)
- DNS: 10.0.2.3 (QEMU DNS proxy)
- Internet: Via host or Whonix Gateway (configurable)

**Android Integration:**
- SurfaceFlinger for display
- Hardware acceleration (virgl)
- Sensor passthrough (accelerometer, GPS)
- Camera passthrough (v4l2)

### 2.2 whonix-vm (Tor Gateway)

**Purpose:** Tor anonymity gateway for network traffic

**Specifications:**
```yaml
name: whonix-vm
type: gateway
os: Debian 12 + Whonix Gateway
cpu: 2 cores
ram: 1024 MB
disk: 8 GB (qcow2, encrypted)
network: virtio-net (isolated bridge)
display: none (headless)
```

**Network Configuration:**
- External: 10.0.2.15/24 (Internet via host)
- Internal: 10.152.152.10/24 (Gateway for other VMs)
- Tor: Transparent proxy on port 9040
- DNS: Tor DNS on port 53

### 2.3 kali-vm (Penetration Testing)

**Purpose:** KALI-WFH penetration testing suite

**Specifications:**
```yaml
name: kali-vm
type: linux
os: Kali Linux 2024.3
cpu: 2 cores
ram: 2048 MB
disk: 16 GB (qcow2, encrypted)
network: virtio-net (isolated, optional Tor)
display: virtio-gpu
```

**Network Configuration:**
- IP: 10.152.152.50/24
- Gateway: 10.152.152.10 (Whonix Gateway) or direct
- Tools: nmap, sqlmap, metasploit, burp suite

### 2.4 vault-vm (AEGIS Airgapped Wallet)

**Purpose:** Airgapped cryptocurrency cold storage

**Specifications:**
```yaml
name: vault-vm
type: airgapped
os: Debian 12 minimal
cpu: 1 core
ram: 512 MB
disk: 2 GB (qcow2, triple-encrypted)
network: NONE (airgapped)
display: virtio-gpu (QR codes only)
usb: none (no passthrough)
```

**Security:**
- No network interface
- No USB passthrough
- No clipboard sharing
- Communication via QR codes only
- Triple encryption: Kyber-ChaCha20 × 3

### 2.5 disposable-vm (Ephemeral)

**Purpose:** Temporary VM for untrusted tasks

**Specifications:**
```yaml
name: disposable-vm
type: ephemeral
os: Alpine Linux (minimal)
cpu: 1 core
ram: 512 MB
disk: 4 GB (tmpfs, RAM-only)
network: virtio-net (Tor mandatory)
lifecycle: destroyed after shutdown
```

**Use Cases:**
- Opening untrusted files
- Visiting suspicious websites
- Testing malware samples
- One-time anonymous tasks

---

## 3. QEMU Configuration

### 3.1 QEMU Command Template

Basic QEMU command structure for VMs:

```bash
qemu-system-aarch64 \
  -name android-vm \
  -machine virt,accel=tcg,gic-version=3 \
  -cpu cortex-a57 \
  -smp 4 \
  -m 4096 \
  -kernel /boot/qwamos/Image \
  -initrd /boot/qwamos/initramfs.img \
  -append "console=ttyAMA0 root=/dev/vda2 rw" \
  -drive file=/var/lib/qwamos/vms/android-vm/disk.qcow2,if=virtio,format=qcow2 \
  -netdev user,id=net0,hostfwd=tcp::5555-:5555 \
  -device virtio-net-pci,netdev=net0 \
  -device virtio-gpu-pci \
  -device virtio-keyboard-pci \
  -device virtio-mouse-pci \
  -device virtio-serial-pci \
  -serial stdio \
  -nographic \
  -monitor telnet:127.0.0.1:4444,server,nowait
```

### 3.2 Acceleration Options

**On Real Hardware (ARM64 with KVM):**
```bash
-machine virt,accel=kvm,gic-version=3
-cpu host
-enable-kvm
```

**On Termux/Android (TCG Software Emulation):**
```bash
-machine virt,accel=tcg,gic-version=3
-cpu cortex-a57
```

### 3.3 Storage Configuration

**Encrypted QCOW2 Images:**

Create encrypted disk image:
```bash
qemu-img create -f qcow2 \
  -o encrypt.format=luks,encrypt.key-secret=sec0 \
  android-vm-disk.qcow2 32G
```

**IMPORTANT:** Use ChaCha20-Poly1305 encryption (NOT AES)
- QEMU currently uses LUKS which defaults to AES
- Will need to patch QEMU or use dm-crypt with ChaCha20
- Alternative: Encrypt at host filesystem level with VeraCrypt

---

## 4. VM Management System

### 4.1 Python VM Manager

Create `qwamos-vm-manager` Python script:

**Location:** `/usr/local/bin/qwamos-vm-manager`

**Features:**
- Start/stop/restart VMs
- Monitor VM status (CPU, RAM, network)
- Snapshot management
- Backup/restore VMs
- Network configuration
- Security policy enforcement

**Usage:**
```bash
# Start a VM
qwamos-vm-manager start android-vm

# Stop a VM
qwamos-vm-manager stop android-vm

# List all VMs
qwamos-vm-manager list

# VM status
qwamos-vm-manager status android-vm

# Create snapshot
qwamos-vm-manager snapshot android-vm "before-update"

# Restore snapshot
qwamos-vm-manager restore android-vm "before-update"
```

### 4.2 Configuration Files

**VM Configuration:** `/etc/qwamos/vms/<vm-name>/config.yaml`

Example for android-vm:
```yaml
name: android-vm
enabled: true
autostart: true

cpu:
  cores: 4
  model: cortex-a57

memory:
  size: 4096M

storage:
  - device: disk
    file: /var/lib/qwamos/vms/android-vm/disk.qcow2
    format: qcow2
    size: 32G
    encryption: chacha20-poly1305

network:
  - type: user
    id: net0
    ports:
      - host: 5555
        guest: 5555
        protocol: tcp

display:
  type: virtio-gpu
  resolution: 1080x2400

security:
  selinux: enforcing
  seccomp: strict
  readonly_host: true
```

### 4.3 systemd Service Integration

**Service File:** `/etc/systemd/system/qwamos-vm@.service`

```ini
[Unit]
Description=QWAMOS Virtual Machine: %i
After=network.target

[Service]
Type=forking
User=qwamos
Group=qwamos
ExecStart=/usr/local/bin/qwamos-vm-manager start %i
ExecStop=/usr/local/bin/qwamos-vm-manager stop %i
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Enable services:
```bash
systemctl enable qwamos-vm@android-vm
systemctl enable qwamos-vm@whonix-vm
systemctl start qwamos-vm@android-vm
```

---

## 5. Network Configuration

### 5.1 Virtual Network Topology

```
┌─────────────────────────────────────────────────────────┐
│                   QWAMOS Host                            │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  br-qwamos0  │         │  br-qwamos1  │             │
│  │ 10.0.2.1/24  │         │10.152.152.1  │             │
│  │  (External)  │         │  (Internal)  │             │
│  └──────┬───────┘         └──────┬───────┘             │
│         │                        │                      │
│  ┌──────┴───────┐         ┌──────┴───────┐             │
│  │ tap-android  │         │  tap-kali    │             │
│  └──────┬───────┘         └──────┬───────┘             │
└─────────┼────────────────────────┼──────────────────────┘
          │                        │
    ┌─────▼─────┐            ┌─────▼─────┐
    │android-vm │            │  kali-vm  │
    │10.0.2.15  │            │10.152.152 │
    │           │            │    .50    │
    │  Internet │            │           │
    │  Direct   │            │   via Tor │
    └───────────┘            └─────┬─────┘
                                   │
                             ┌─────▼──────┐
                             │ whonix-vm  │
                             │10.152.152  │
                             │    .10     │
                             │ Tor        │
                             │ Gateway    │
                             └────────────┘
```

### 5.2 Bridge Setup

Create network bridges:

```bash
# External bridge (Internet access)
ip link add br-qwamos0 type bridge
ip addr add 10.0.2.1/24 dev br-qwamos0
ip link set br-qwamos0 up

# Internal bridge (VM-to-VM isolated)
ip link add br-qwamos1 type bridge
ip addr add 10.152.152.1/24 dev br-qwamos1
ip link set br-qwamos1 up

# Enable IP forwarding
sysctl -w net.ipv4.ip_forward=1

# NAT for external bridge
iptables -t nat -A POSTROUTING -s 10.0.2.0/24 -j MASQUERADE
```

### 5.3 Firewall Rules

**iptables Configuration:**

```bash
# Default deny
iptables -P FORWARD DROP

# Allow android-vm to Internet (direct)
iptables -A FORWARD -i tap-android -o wlan0 -j ACCEPT
iptables -A FORWARD -i wlan0 -o tap-android -m state --state RELATED,ESTABLISHED -j ACCEPT

# Force kali-vm through Whonix Gateway
iptables -A FORWARD -i tap-kali -d 10.152.152.10 -j ACCEPT
iptables -A FORWARD -i tap-kali ! -d 10.152.152.0/24 -j REJECT

# Isolate vault-vm (no network)
iptables -A FORWARD -i tap-vault -j REJECT
```

---

## 6. Implementation Steps

### Phase 3.1: QEMU Testing (Week 1)

- [x] Verify QEMU installation
- [ ] Test basic QEMU ARM64 boot
- [ ] Create minimal test VM
- [ ] Validate virtio devices
- [ ] Test network connectivity

### Phase 3.2: VM Infrastructure (Week 2)

- [ ] Create VM storage directory structure
- [ ] Write VM configuration templates
- [ ] Implement Python VM manager (basic)
- [ ] Create systemd service files
- [ ] Test VM lifecycle (start/stop)

### Phase 3.3: android-vm Implementation (Week 3-4)

- [ ] Download Android 14 AOSP ARM64 image
- [ ] Create 32GB encrypted QCOW2 disk
- [ ] Configure Android kernel for KVM
- [ ] Set up virtio devices (GPU, net, input)
- [ ] Test Android boot in QEMU
- [ ] Optimize performance

### Phase 3.4: Network Setup (Week 5)

- [ ] Configure bridge networking
- [ ] Set up TAP/TUN devices
- [ ] Implement firewall rules
- [ ] Test VM-to-VM communication
- [ ] Test VM-to-Internet access

### Phase 3.5: Integration & Testing (Week 6)

- [ ] Integrate with QWAMOS boot process
- [ ] Auto-start VMs on system boot
- [ ] Test all VMs simultaneously
- [ ] Performance benchmarking
- [ ] Security audit

---

## 7. Testing Plan

### 7.1 Basic Functionality Tests

```bash
# Test 1: QEMU boots minimal kernel
qemu-system-aarch64 -kernel Image -initrd initramfs.img -nographic

# Test 2: Create test disk image
qemu-img create -f qcow2 test.qcow2 1G

# Test 3: Boot with disk
qemu-system-aarch64 -kernel Image -drive file=test.qcow2,if=virtio

# Test 4: Network test
qemu-system-aarch64 -kernel Image -netdev user,id=net0 -device virtio-net,netdev=net0
```

### 7.2 VM Isolation Tests

- Memory isolation: Attempt cross-VM memory access (should fail)
- Network isolation: Test firewall rules between VMs
- Storage isolation: Verify VMs cannot access each other's disks
- CPU isolation: Monitor CPU scheduling fairness

### 7.3 Performance Benchmarks

- VM boot time: Target < 10 seconds
- Android app launch: Target < 2 seconds
- Network throughput: Target > 100 Mbps
- Disk I/O: Target > 50 MB/s sequential

---

## 8. Security Considerations

### 8.1 Hypervisor Security

**Threats:**
- VM escape attacks
- Hypervisor vulnerabilities (QEMU CVEs)
- Side-channel attacks (Spectre/Meltdown)
- Resource exhaustion (DoS)

**Mitigations:**
- Use latest QEMU version (security patches)
- Enable SELinux/AppArmor for QEMU processes
- Limit VM resources (cgroups)
- Disable unnecessary QEMU features
- Run QEMU as non-root user

### 8.2 VM-to-VM Communication

**Policy:** Deny by default, allow explicitly

**Allowed Communication:**
- android-vm → whonix-vm (optional Tor routing)
- kali-vm → whonix-vm (mandatory Tor routing)
- vault-vm → NONE (airgapped)

**Forbidden Communication:**
- android-vm ↔ kali-vm (direct)
- android-vm ↔ vault-vm
- Any VM → Host filesystem (read-only at most)

### 8.3 Encryption

**Disk Encryption:**
- Use VeraCrypt with ChaCha20-Poly1305
- NOT QEMU's built-in LUKS (uses AES)
- Encrypt VM disk images at host level
- Key derivation: Argon2id (1GB memory)

**Network Encryption:**
- VM-to-Internet: Optional VPN/Tor
- VM-to-VM: Not encrypted (isolated network)
- Host-to-VM: Local communication only

---

## 9. Resource Requirements

### 9.1 Storage

| Component | Size | Location |
|-----------|------|----------|
| android-vm disk | 32 GB | /var/lib/qwamos/vms/android-vm/ |
| whonix-vm disk | 8 GB | /var/lib/qwamos/vms/whonix-vm/ |
| kali-vm disk | 16 GB | /var/lib/qwamos/vms/kali-vm/ |
| vault-vm disk | 2 GB | /var/lib/qwamos/vms/vault-vm/ |
| Snapshots | 20 GB | /var/lib/qwamos/snapshots/ |
| **Total** | **~80 GB** | - |

### 9.2 Memory

| Component | RAM | Notes |
|-----------|-----|-------|
| Host system | 2 GB | QWAMOS base |
| android-vm | 4 GB | Primary VM |
| whonix-vm | 1 GB | Gateway |
| kali-vm | 2 GB | Optional (on-demand) |
| vault-vm | 512 MB | Rarely used |
| **Minimum** | **8 GB** | android-vm + host |
| **Recommended** | **12 GB** | All VMs running |

### 9.3 CPU

- Minimum: 4 cores (ARM Cortex-A53 or better)
- Recommended: 8 cores (ARM Cortex-A76 or better)
- KVM acceleration: Requires ARM64 with virtualization extensions

---

## 10. Deliverables

### 10.1 Code

- [ ] `/usr/local/bin/qwamos-vm-manager` - Python VM manager
- [ ] `/etc/qwamos/vms/` - VM configuration files
- [ ] `/etc/systemd/system/qwamos-vm@.service` - systemd service
- [ ] `/usr/local/bin/qwamos-network-setup.sh` - Network configuration script

### 10.2 Documentation

- [ ] `docs/PHASE3_HYPERVISOR_SPEC.md` - This specification
- [ ] `docs/VM_MANAGEMENT.md` - VM manager user guide
- [ ] `docs/ANDROID_VM_SETUP.md` - Android VM setup guide
- [ ] `docs/NETWORK_CONFIG.md` - Network configuration guide

### 10.3 Test Results

- [ ] QEMU boot test report
- [ ] VM isolation test results
- [ ] Performance benchmarks
- [ ] Security audit report

---

## 11. Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| 1 | QEMU testing, basic VM | Working test VM |
| 2 | VM infrastructure | VM manager script |
| 3-4 | android-vm setup | Bootable Android VM |
| 5 | Network configuration | Isolated network |
| 6 | Integration & testing | Phase 3 complete |

**Total Duration:** 6 weeks (1.5 months)

---

## 12. Success Criteria

Phase 3 is considered complete when:

✅ QEMU boots ARM64 kernel successfully
✅ VM manager can start/stop VMs
✅ android-vm boots to Android UI
✅ VMs are properly isolated (memory, network, storage)
✅ Network connectivity works (Internet + VM-to-VM)
✅ All security tests pass
✅ Performance meets target benchmarks
✅ Documentation is complete

---

**Document Version:** 1.0
**Last Updated:** November 1, 2025
**Status:** Specification Complete | Implementation Starting
**Next Step:** QEMU testing and basic VM setup

*QWAMOS - Hypervisor-Based Mobile Security for the Post-Quantum Era*
