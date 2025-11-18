# Architecture

**[← Back to Home](Home)**

---

## System Overview

QWAMOS is built on a **layered architecture** with strict isolation between components:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Panic   │  │   VM     │  │ Gateway  │  │  Crypto  │   │
│  │  System  │  │ Manager  │  │ Control  │  │  Keyring │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                   Orchestration Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   VM        │  │   Resource   │  │   Security   │     │
│  │ Scheduler   │  │  Allocator   │  │   Monitor    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                   Virtualization Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  QEMU/   │  │  Chroot  │  │  PRoot   │  │   KVM    │   │
│  │   TCG    │  │          │  │          │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                     Gateway Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Tor    │  │   I2P    │  │DNSCrypt │  │ Firewall │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                   Encryption Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Kyber-1024  │  │ ChaCha20-    │  │   BLAKE3     │     │
│  │     KEM      │  │  Poly1305    │  │   Hashing    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│                      Host OS (Android)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## VM Isolation Architecture

### Isolation Boundaries

Each VM operates in a completely isolated environment with **zero shared resources** between VMs:

```
┌──────────────────────────────────────────────────────────────┐
│                         Host System                          │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   VM 1          │  │   VM 2          │  │   VM 3      │ │
│  │  (Browser)      │  │  (Messaging)    │  │  (Dev Env)  │ │
│  │                 │  │                 │  │             │ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │ ┌─────────┐│ │
│  │  │ Isolated  │  │  │  │ Isolated  │  │  │ │Isolated ││ │
│  │  │ Filesystem│  │  │  │ Filesystem│  │  │ │Filesystm││ │
│  │  └───────────┘  │  │  └───────────┘  │  │ └─────────┘│ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │ ┌─────────┐│ │
│  │  │ Isolated  │  │  │  │ Isolated  │  │  │ │Isolated ││ │
│  │  │  Network  │  │  │  │  Network  │  │  │ │ Network ││ │
│  │  │ (10.8.0.2)│  │  │  │ (10.8.0.3)│  │  │ │(10.8.0.4│ │
│  │  └───────────┘  │  │  └───────────┘  │  │ └─────────┘│ │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │ ┌─────────┐│ │
│  │  │ Isolated  │  │  │  │ Isolated  │  │  │ │Isolated ││ │
│  │  │   GPU     │  │  │  │   GPU     │  │  │ │  GPU    ││ │
│  │  │  Context  │  │  │  │  Context  │  │  │ │ Context ││ │
│  │  └───────────┘  │  │  └───────────┘  │  │ └─────────┘│ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                              │
│             ⚠️  NO SHARED RESOURCES BETWEEN VMS              │
└──────────────────────────────────────────────────────────────┘
```

### VM Lifecycle

```
┌─────────────┐
│   Created   │  VM disk image allocated & encrypted
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Suspended  │  VM exists but not running (default state)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Booting   │  QEMU/KVM starts, loads kernel
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Running   │  VM operational, apps can execute
└──────┬──────┘
       │
       ├──► Snapshot ────► Frozen state saved to disk
       │
       ├──► Pause ───────► VM suspended (RAM persists)
       │         │
       │         └────────► Resume ──► Back to Running
       │
       ▼
┌─────────────┐
│   Shutdown  │  Clean shutdown, encrypt and save state
└──────┬──────┘
       │
       ├──► Restart ──────► Back to Booting
       │
       ▼
┌─────────────┐
│  Destroyed  │  VM deleted, disk securely wiped
└─────────────┘
```

---

## Gateway Traffic Flow

### Network Architecture

All VM network traffic flows through the **QWAMOS Gateway** which enforces anonymization:

```
                              Internet
                                 ▲
                                 │
┌────────────────────────────────┼────────────────────────────┐
│ QWAMOS Gateway                 │                            │
│                                │                            │
│  ┌─────────────────────────────┴──────────────────────┐    │
│  │          Firewall (iptables)                       │    │
│  │  Rules: DROP all, ALLOW only Tor/I2P/DNSCrypt      │    │
│  └────────┬────────────────┬──────────────────┬───────┘    │
│           │                │                  │            │
│  ┌────────▼────────┐  ┌────▼──────┐  ┌───────▼────────┐   │
│  │  Tor Proxy      │  │ I2P Proxy │  │  DNSCrypt      │   │
│  │  127.0.0.1:9050 │  │ 127.0.0.1:│  │  127.0.0.1:5354│   │
│  │  (SOCKS5)       │  │ 4444      │  │  (DNS-over-TLS)│   │
│  └────────▲────────┘  └────▲──────┘  └───────▲────────┘   │
│           │                │                  │            │
└───────────┼────────────────┼──────────────────┼────────────┘
            │                │                  │
            │                │                  │
┌───────────┼────────────────┼──────────────────┼────────────┐
│ Virtual Bridge (10.8.0.1)  │                  │            │
│           │                │                  │            │
│  ┌────────┴────────┐  ┌────┴──────┐  ┌───────┴────────┐   │
│  │  VM 1           │  │  VM 2     │  │  VM 3          │   │
│  │  10.8.0.2       │  │  10.8.0.3 │  │  10.8.0.4      │   │
│  │  Route: Tor     │  │  Route:I2P│  │  Route: Tor    │   │
│  └─────────────────┘  └───────────┘  └────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### Routing Rules

**Per-VM Configuration:**

```ini
# ~/.qwamos/config/routing.conf

[vm:secure-browser]
network = 10.8.0.2/24
gateway = 10.8.0.1
route = tor           # All traffic via Tor
dns = dnscrypt
firewall = strict

[vm:messaging]
network = 10.8.0.3/24
gateway = 10.8.0.1
route = i2p           # All traffic via I2P
dns = dnscrypt
firewall = strict

[vm:development]
network = 10.8.0.4/24
gateway = 10.8.0.1
route = direct        # Direct internet (for development only)
dns = dnscrypt
firewall = permissive
```

### Firewall Rules (iptables)

```bash
# Default policy: DROP all
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow VM → Gateway
iptables -A FORWARD -s 10.8.0.0/24 -d 127.0.0.1 -j ACCEPT

# Allow Gateway → Tor
iptables -A OUTPUT -d 127.0.0.1 -p tcp --dport 9050 -j ACCEPT

# Allow Gateway → I2P
iptables -A OUTPUT -d 127.0.0.1 -p tcp --dport 4444 -j ACCEPT

# Allow Gateway → DNSCrypt
iptables -A OUTPUT -d 127.0.0.1 -p udp --dport 5354 -j ACCEPT

# Block direct internet from VMs
iptables -A FORWARD -s 10.8.0.0/24 ! -d 127.0.0.1 -j DROP

# Log blocked connections
iptables -A FORWARD -j LOG --log-prefix "QWAMOS-BLOCKED: "
```

---

## PQC Stack Outline

### Encryption Pipeline

```
┌───────────────────────────────────────────────────────────┐
│                  User Passphrase                          │
│               "correct-horse-battery-staple"              │
└────────────────────────┬──────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│               Argon2id Key Derivation                      │
│  Parameters: time=3, memory=256MB, parallelism=4           │
│  Output: 256-bit derived key                               │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│              Kyber-1024 Key Encapsulation                  │
│  1. Generate Kyber public/private keypair                  │
│  2. Encapsulate: ciphertext = Encaps(public_key, message)  │
│  3. Decapsulate: shared_secret = Decaps(private_key, ct)   │
│  Output: 256-bit shared secret (quantum-resistant)         │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│             ChaCha20-Poly1305 AEAD Encryption              │
│  Input: shared_secret (key), nonce, plaintext              │
│  Process:                                                   │
│    1. ChaCha20 stream cipher encrypts plaintext            │
│    2. Poly1305 MAC authenticates ciphertext                │
│  Output: ciphertext || MAC (authenticated encryption)      │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│                   Encrypted VM Disk                        │
│  File: ~/.qwamos/vms/secure-browser/disk.img.enc          │
│  Format: [Kyber CT][Nonce][ChaCha20 Ciphertext][Poly1305] │
└────────────────────────────────────────────────────────────┘
```

### Key Storage

```
~/.qwamos/
├── keys/
│   ├── master.pub              # Kyber-1024 public key
│   ├── master.key              # Kyber-1024 private key (encrypted with passphrase)
│   ├── vm-keys/
│   │   ├── secure-browser.key  # Per-VM wrapped key
│   │   ├── messaging.key
│   │   └── development.key
│   └── backup/
│       └── master-backup-2025-11-18.key  # Weekly backups
└── crypto/
    ├── nonces/                 # Unique nonce per encryption operation
    └── salts/                  # Argon2id salts (random, per-key)
```

### Cryptographic Operations

**VM Disk Encryption (Write):**
```python
def encrypt_vm_disk(plaintext_data, vm_name):
    # 1. Derive key from passphrase
    master_key = argon2id_derive(
        passphrase=get_user_passphrase(),
        salt=get_random_salt(),
        time_cost=3,
        memory_cost=256 * 1024,  # 256 MB
        parallelism=4
    )

    # 2. Kyber key encapsulation
    kyber_public_key = load_kyber_public_key(vm_name)
    kyber_ciphertext, shared_secret = kyber_encaps(
        public_key=kyber_public_key,
        message=master_key
    )

    # 3. ChaCha20-Poly1305 encryption
    nonce = generate_random_nonce(12 bytes)
    ciphertext, mac = chacha20_poly1305_encrypt(
        key=shared_secret,
        nonce=nonce,
        plaintext=plaintext_data,
        associated_data=vm_name
    )

    # 4. Combine components
    encrypted_disk = kyber_ciphertext + nonce + ciphertext + mac

    # 5. BLAKE3 integrity hash
    integrity_hash = blake3(encrypted_disk)

    return encrypted_disk + integrity_hash
```

**VM Disk Decryption (Read):**
```python
def decrypt_vm_disk(encrypted_disk, vm_name):
    # 1. Verify integrity
    stored_hash = encrypted_disk[-32:]  # Last 32 bytes
    computed_hash = blake3(encrypted_disk[:-32])
    if stored_hash != computed_hash:
        raise IntegrityError("Disk tampered or corrupted")

    # 2. Parse components
    kyber_ct_size = KYBER_1024_CT_SIZE  # 1568 bytes
    kyber_ciphertext = encrypted_disk[:kyber_ct_size]
    nonce = encrypted_disk[kyber_ct_size:kyber_ct_size+12]
    ciphertext_with_mac = encrypted_disk[kyber_ct_size+12:-32]

    # 3. Derive master key
    master_key = argon2id_derive(
        passphrase=get_user_passphrase(),
        salt=load_salt(vm_name),
        time_cost=3,
        memory_cost=256 * 1024,
        parallelism=4
    )

    # 4. Kyber decapsulation
    kyber_private_key = load_kyber_private_key(vm_name, master_key)
    shared_secret = kyber_decaps(
        private_key=kyber_private_key,
        ciphertext=kyber_ciphertext
    )

    # 5. ChaCha20-Poly1305 decryption
    plaintext = chacha20_poly1305_decrypt(
        key=shared_secret,
        nonce=nonce,
        ciphertext=ciphertext_with_mac[:-16],
        mac=ciphertext_with_mac[-16:],
        associated_data=vm_name
    )

    return plaintext
```

---

## Panic/Wipe System Overview

### Trigger Detection Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                    Trigger Sources                          │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Hardware  │  │  Software  │  │  Network   │           │
│  │  Buttons   │  │  Commands  │  │  Signals   │           │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘           │
└─────────┼────────────────┼────────────────┼─────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│              Panic Detection Daemon                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Input Monitor:                                     │   │
│  │  - /dev/input/event*  (volume buttons)              │   │
│  │  - /proc/sys/kernel/poweroff  (power button)        │   │
│  │  - SMS receiver (emergency keyword)                 │   │
│  │  - Deadman timer (last checkin timestamp)           │   │
│  │  - Geofence monitor (GPS coordinates)               │   │
│  │  - Network listener (remote wipe command)           │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼ (Trigger detected)
┌─────────────────────────────────────────────────────────────┐
│               Authentication & Verification                 │
│  - Verify trigger signature (prevent false positives)       │
│  - Check user confirmation (if enabled)                     │
│  - Log trigger event (encrypted audit log)                  │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼ (Authenticated)
┌─────────────────────────────────────────────────────────────┐
│                    Wipe Execution                           │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Step 1:      │ →  │ Step 2:      │ →  │ Step 3:      │ │
│  │ Freeze VMs   │    │ Delete Keys  │    │ Wipe Disks   │ │
│  │              │    │ (Kyber       │    │ (Overwrite   │ │
│  │ - Stop all   │    │ private keys)│    │  VM images)  │ │
│  │   VMs        │    │              │    │              │ │
│  │ - Kill       │    │ - Secure     │    │ - Quick: 1   │ │
│  │   processes  │    │   delete     │    │   pass       │ │
│  │ - Sync disks │    │   (7-pass)   │    │ - Standard:  │ │
│  │              │    │ - Scrub RAM  │    │   3-pass     │ │
│  │              │    │              │    │ - Paranoid:  │ │
│  │              │    │              │    │   7-pass     │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Post-Wipe Actions                          │
│  - Display decoy screen (if duress mode)                    │
│  - Send wipe confirmation (to trusted contact)              │
│  - Power off device (if configured)                         │
│  - Self-destruct panic daemon (prevent forensic analysis)   │
└─────────────────────────────────────────────────────────────┘
```

### Wipe Levels

| Level | Time | Operations | Security | Use Case |
|-------|------|------------|----------|----------|
| **Quick** | 1-2s | Delete encryption keys only | ⭐⭐⭐ | Border crossing |
| **Standard** | 10-30s | Keys + 1-pass overwrite | ⭐⭐⭐⭐ | Device seizure imminent |
| **Thorough** | 2-5min | Keys + 3-pass overwrite | ⭐⭐⭐⭐⭐ | Known forensic threat |
| **Paranoid** | 10-30min | Keys + 7-pass Gutmann | ⭐⭐⭐⭐⭐⭐ | Nation-state adversary |

---

## Per-VM Firewall Routing

### Routing Table Structure

```
┌────────────────────────────────────────────────────────────┐
│           QWAMOS Routing & Firewall Engine                 │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Routing Table                                        │ │
│  ├──────────┬───────────────┬──────────┬────────────────┤ │
│  │ VM Name  │ IP Address    │ Gateway  │ Route Type    │ │
│  ├──────────┼───────────────┼──────────┼────────────────┤ │
│  │ browser  │ 10.8.0.2      │10.8.0.1  │ tor           │ │
│  │ message  │ 10.8.0.3      │10.8.0.1  │ i2p           │ │
│  │ dev      │ 10.8.0.4      │10.8.0.1  │ direct        │ │
│  │ malware  │ 10.8.0.5      │10.8.0.1  │ isolated      │ │
│  └──────────┴───────────────┴──────────┴────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Firewall Rules (per-VM)                              │ │
│  ├──────────┬────────────────────────────────────────────┤ │
│  │ VM: browser                                           │ │
│  ├──────────┴────────────────────────────────────────────┤ │
│  │ ALLOW: 10.8.0.2 → 127.0.0.1:9050 (Tor)               │ │
│  │ ALLOW: 10.8.0.2 → 127.0.0.1:5354 (DNSCrypt)          │ │
│  │ DENY:  10.8.0.2 → * (all other destinations)         │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │ VM: message                                           │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │ ALLOW: 10.8.0.3 → 127.0.0.1:4444 (I2P)               │ │
│  │ ALLOW: 10.8.0.3 → 127.0.0.1:5354 (DNSCrypt)          │ │
│  │ DENY:  10.8.0.3 → * (all other destinations)         │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │ VM: malware (isolated - no network)                   │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │ DENY:  10.8.0.5 → * (complete isolation)             │ │
│  └───────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

### Network Namespaces

Each VM operates in its own **network namespace** for complete network isolation:

```bash
# Create network namespace for VM
ip netns add qwamos-browser

# Create virtual ethernet pair
ip link add veth-browser type veth peer name veth-browser-host

# Move one end to VM namespace
ip link set veth-browser netns qwamos-browser

# Configure VM side
ip netns exec qwamos-browser ip addr add 10.8.0.2/24 dev veth-browser
ip netns exec qwamos-browser ip link set veth-browser up
ip netns exec qwamos-browser ip route add default via 10.8.0.1

# Configure host side
ip addr add 10.8.0.1/24 dev veth-browser-host
ip link set veth-browser-host up

# Enable NAT to gateway
iptables -t nat -A POSTROUTING -s 10.8.0.2/32 -j MASQUERADE
```

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      QWAMOS Component Map                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ UI Layer                                                   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │  React   │  │  Termux  │  │ Android  │  │   Web    │  │ │
│  │  │  Native  │  │    UI    │  │  Intents │  │Dashboard │  │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │ │
│  └───────┼─────────────┼─────────────┼─────────────┼────────┘ │
│          │             │             │             │          │
│  ┌───────┴─────────────┴─────────────┴─────────────┴────────┐ │
│  │ API Layer (REST + gRPC)                                  │ │
│  │  Endpoints: /vm/*, /crypto/*, /panic/*, /gateway/*       │ │
│  └───────┬──────────────────────────────────────────────────┘ │
│          │                                                    │
│  ┌───────┴────────────────────────────────────────────────┐  │
│  │ Core Services                                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │    VM    │  │  Crypto  │  │  Panic   │             │  │
│  │  │  Manager │  │  Engine  │  │  System  │             │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘             │  │
│  └───────┼─────────────┼─────────────┼────────────────────┘  │
│          │             │             │                       │
│  ┌───────┴─────────────┴─────────────┴────────────────────┐  │
│  │ Subsystems                                             │  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │  │
│  │  │  QEMU/  │  │ Gateway │  │   GPU   │  │   AI    │   │  │
│  │  │   KVM   │  │ (Tor/I2P│  │Isolation│  │Governor │   │  │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ Storage Layer                                          │  │
│  │  - VM Disk Images (Kyber-1024 + ChaCha20 encrypted)    │  │
│  │  - Keyring (Encrypted key storage)                     │  │
│  │  - Configuration (Routing, firewall, VM settings)      │  │
│  │  - Logs (Encrypted audit logs)                         │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## Module Structure

```
QWAMOS/
├── vm/                  # VM management
│   ├── manager.py       # VM lifecycle (create, start, stop)
│   ├── scheduler.py     # Resource allocation
│   └── qemu.py          # QEMU/KVM backend
│
├── crypto/              # Cryptographic operations
│   ├── kyber.py         # Kyber-1024 KEM
│   ├── chacha20.py      # ChaCha20-Poly1305 AEAD
│   ├── blake3.py        # BLAKE3 hashing
│   └── keyring.py       # Key management
│
├── gateway/             # Anonymous networking
│   ├── tor.py           # Tor integration
│   ├── i2p.py           # I2P integration
│   ├── dnscrypt.py      # DNSCrypt configuration
│   └── firewall.py      # iptables rules
│
├── panic/               # Emergency wipe system
│   ├── triggers.py      # Trigger detection
│   ├── wipe.py          # Secure deletion
│   └── duress.py        # Duress password handling
│
├── gpu/                 # GPU isolation (Phase XIV)
│   ├── context.py       # GPU context management
│   └── sandbox.py       # Shader sandboxing
│
├── ai/                  # AI Governor (Phase XV)
│   ├── resource.py      # Resource prediction
│   ├── threat.py        # Threat detection
│   └── models/          # On-device AI models
│
├── cluster/             # Secure Cluster Mode (Phase XVI)
│   ├── mesh.py          # Mesh networking
│   ├── consensus.py     # Byzantine fault tolerance
│   └── failover.py      # Automatic failover
│
└── tests/               # Testing framework
    ├── kvm_hardware_suite/       # Hardware validation
    └── differential_kvm_qemu/    # QEMU vs KVM comparison
```

---

## Next Steps

- **[Security Model](Security-Model):** Understand threat model and security guarantees
- **[Developer Guide](Developer-Guide):** Contribute to QWAMOS development
- **[FAQ](FAQ):** Common questions and troubleshooting

---

**[← Back to Home](Home)**
