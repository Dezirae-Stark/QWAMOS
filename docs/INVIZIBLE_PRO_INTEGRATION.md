# InviZible Pro Integration Specification

**Feature Owner:** QWAMOS Development Team
**Priority:** HIGH
**Target Phase:** Phase 2 (Months 3-4)
**Status:** PLANNED

---

## Overview

Integrate InviZible Pro's privacy and anonymity components into QWAMOS to enhance the Whonix Gateway VM with multiple anonymity layers, encrypted DNS, and I2P routing.

**InviZible Pro** is an open-source Android application that includes:
- Tor proxy (optimized for mobile)
- DNSCrypt (encrypted DNS queries)
- Purple I2P (Invisible Internet Project router)
- Firewall and traffic routing

**Source:** https://github.com/Gedsh/InviZible

---

## Architecture

### Current QWAMOS Network Stack

```
whonix-vm
    └─> Tor (from Whonix Gateway)
        └─> Transparent proxy for all VMs
```

### Enhanced with InviZible Pro

```
whonix-vm (ENHANCED)
    ├─> Tor (InviZible Pro optimized binaries)
    │   ├─> Tor bridges support
    │   ├─> Pluggable transports (obfs4, meek, snowflake)
    │   └─> Mobile-optimized connection handling
    │
    ├─> DNSCrypt
    │   ├─> Encrypted DNS queries
    │   ├─> DNS-over-HTTPS (DoH)
    │   ├─> DNS-over-TLS (DoT)
    │   └─> Prevents DNS leaks
    │
    ├─> Purple I2P Router
    │   ├─> Parallel anonymity network
    │   ├─> Garlic routing
    │   ├─> Hidden services (eepsites)
    │   └─> BitTorrent over I2P
    │
    └─> Firewall & Routing
        ├─> iptables rules
        ├─> App-level routing
        └─> Kill switch on disconnect
```

---

## Components to Extract

### 1. Tor Module

**From InviZible Pro:**
- `app/src/main/assets/tor` - Tor binaries (ARM64)
- `app/src/main/java/pan/alexander/tordnscrypt/modules/ModulesRunner.java` - Tor controller
- `app/src/main/assets/tor-bridges.txt` - Bridge configuration

**Integration into QWAMOS:**
```
network/tor/invizible/
    ├─> tor_arm64 (optimized binary)
    ├─> torrc.invizible (mobile-optimized config)
    ├─> bridges/ (obfs4, meek, snowflake configs)
    └─> tor_controller.py (Python wrapper)
```

**Benefits:**
- Mobile-optimized Tor implementation
- Built-in bridge support for censored networks
- Pluggable transports (obfs4 for DPI bypass)

### 2. DNSCrypt Module

**From InviZible Pro:**
- `app/src/main/assets/dnscrypt-proxy` - DNSCrypt binaries
- `app/src/main/assets/dnscrypt-proxy.toml` - DNSCrypt configuration
- DNS server lists

**Integration into QWAMOS:**
```
network/dnscrypt/
    ├─> dnscrypt-proxy_arm64
    ├─> dnscrypt-proxy.toml
    ├─> resolvers/
    │   ├─> public-resolvers.md
    │   └─> relays.md
    └─> dnscrypt_controller.py
```

**Configuration:**
```toml
# network/dnscrypt/dnscrypt-proxy.toml

server_names = ['cloudflare', 'google']
listen_addresses = ['127.0.0.1:5353']

[query_log]
  file = '/var/log/dnscrypt-proxy/query.log'

[nx_log]
  file = '/var/log/dnscrypt-proxy/nx.log'

[sources]
  [sources.'public-resolvers']
    urls = ['https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v3/public-resolvers.md']
    cache_file = '/var/cache/dnscrypt-proxy/public-resolvers.md'

[blacklist]
  blacklist_file = '/etc/dnscrypt-proxy/blacklist.txt'
```

**Benefits:**
- Encrypted DNS queries (prevents ISP snooping)
- DNSSEC validation
- DNS query logging for security auditing
- Blocks ads and malware domains

### 3. Purple I2P Module

**From InviZible Pro:**
- `app/src/main/assets/i2pd` - I2P daemon (C++ implementation)
- `app/src/main/assets/i2pd.conf` - I2P configuration
- `app/src/main/assets/tunnels.conf` - I2P tunnel configuration

**Integration into QWAMOS:**
```
network/i2p/
    ├─> i2pd_arm64 (Purple I2P daemon)
    ├─> i2pd.conf
    ├─> tunnels.conf
    ├─> certificates/ (I2P router certificates)
    └─> i2p_controller.py
```

**Configuration:**
```ini
# network/i2p/i2pd.conf

[i2pd]
loglevel = warn
logfile = /var/log/i2p/i2pd.log

[http]
enabled = true
address = 127.0.0.1
port = 7070

[httpproxy]
enabled = true
address = 127.0.0.1
port = 4444

[socksproxy]
enabled = true
address = 127.0.0.1
port = 4447

[sam]
enabled = true
address = 127.0.0.1
port = 7656

[ntcp2]
enabled = true
published = true

[ssu2]
enabled = true
published = true

[reseed]
verify = true
urls = https://reseed.i2p-projekt.de/,https://i2p.mooo.com/netDb/,https://reseed-fr.i2pd.xyz/

[limits]
transittunnels = 2500
```

**Benefits:**
- Alternative anonymity network (not reliant on Tor)
- Access to I2P eepsites (hidden services)
- BitTorrent over I2P (anonymous file sharing)
- Garlic routing (layered encryption)

### 4. Firewall Module

**From InviZible Pro:**
- `app/src/main/java/pan/alexander/tordnscrypt/iptables/` - iptables manager
- Firewall rules for Tor/DNSCrypt/I2P routing

**Integration into QWAMOS:**
```
network/firewall/invizible/
    ├─> firewall_manager.py
    ├─> rules/
    │   ├─> tor_rules.nft
    │   ├─> dnscrypt_rules.nft
    │   └─> i2p_rules.nft
    └─> killswitch.py
```

---

## Integration Architecture

### Whonix VM Enhanced Structure

```
whonix-vm (20GB disk, 2GB RAM, 2 vCPUs)
    │
    ├─> /opt/invizible/
    │   ├─> tor/
    │   │   ├─> tor (optimized binary)
    │   │   ├─> torrc
    │   │   └─> bridges/
    │   ├─> dnscrypt/
    │   │   ├─> dnscrypt-proxy
    │   │   └─> dnscrypt-proxy.toml
    │   ├─> i2p/
    │   │   ├─> i2pd
    │   │   ├─> i2pd.conf
    │   │   └─> tunnels.conf
    │   └─> firewall/
    │       └─> rules/
    │
    ├─> /usr/local/bin/
    │   ├─> qwamos-tor (start/stop Tor)
    │   ├─> qwamos-dnscrypt (start/stop DNSCrypt)
    │   ├─> qwamos-i2p (start/stop I2P)
    │   └─> qwamos-network-mode (switch network modes)
    │
    └─> /etc/systemd/system/
        ├─> qwamos-tor.service
        ├─> qwamos-dnscrypt.service
        ├─> qwamos-i2p.service
        └─> qwamos-firewall.service
```

### Network Modes

Users can select network routing mode from QWAMOS UI:

**Mode 1: Tor Only (Default)**
```
VMs → whonix-vm (Tor) → Internet
```

**Mode 2: Tor + DNSCrypt**
```
VMs → whonix-vm (Tor + DNSCrypt for DNS) → Internet
```

**Mode 3: Tor + I2P Parallel**
```
VMs → whonix-vm → Tor (clearnet) / I2P (eepsites)
```

**Mode 4: I2P Only**
```
VMs → whonix-vm (I2P) → I2P Network
```

**Mode 5: Multi-layer (Tor over I2P)**
```
VMs → whonix-vm (Tor) → I2P → Internet
```

---

## Implementation Steps

### Phase 1: Extract InviZible Pro Components (Week 1-2)

```bash
# 1. Clone InviZible Pro
cd ~/QWAMOS/network
git clone https://github.com/Gedsh/InviZible.git invizible-source

# 2. Extract binaries
cd invizible-source
unzip app/src/main/assets/tor-arm64.zip -d ../../tor/invizible/
unzip app/src/main/assets/dnscrypt-proxy-arm64.zip -d ../../dnscrypt/
unzip app/src/main/assets/i2pd-arm64.zip -d ../../i2p/

# 3. Extract configurations
cp app/src/main/assets/torrc ../../tor/invizible/
cp app/src/main/assets/dnscrypt-proxy.toml ../../dnscrypt/
cp app/src/main/assets/i2pd.conf ../../i2p/
```

### Phase 2: Create Control Scripts (Week 3)

```python
# network/tor/invizible/tor_controller.py

import subprocess
import os

class InviZibleTorController:
    def __init__(self):
        self.tor_binary = '/opt/invizible/tor/tor'
        self.torrc = '/opt/invizible/tor/torrc'
        self.control_port = 9051
        self.socks_port = 9050
        self.process = None

    def start(self, use_bridges=False):
        """Start Tor with optional bridge mode"""
        cmd = [self.tor_binary, '-f', self.torrc]

        if use_bridges:
            cmd.extend(['--UseBridges', '1'])
            cmd.extend(['--ClientTransportPlugin', 'obfs4 exec /opt/invizible/tor/obfs4proxy'])

        self.process = subprocess.Popen(cmd)
        print(f"✅ Tor started (PID: {self.process.pid})")

    def stop(self):
        """Stop Tor gracefully"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("✅ Tor stopped")

    def get_status(self):
        """Check if Tor is running and connected"""
        # Use Tor control port to check circuit status
        pass
```

```python
# network/dnscrypt/dnscrypt_controller.py

class DNSCryptController:
    def __init__(self):
        self.dnscrypt_binary = '/opt/invizible/dnscrypt/dnscrypt-proxy'
        self.config = '/opt/invizible/dnscrypt/dnscrypt-proxy.toml'
        self.process = None

    def start(self):
        """Start DNSCrypt proxy"""
        cmd = [self.dnscrypt_binary, '-config', self.config]
        self.process = subprocess.Popen(cmd)
        print(f"✅ DNSCrypt started (listening on 127.0.0.1:5353)")

    def stop(self):
        """Stop DNSCrypt"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("✅ DNSCrypt stopped")
```

```python
# network/i2p/i2p_controller.py

class PurpleI2PController:
    def __init__(self):
        self.i2pd_binary = '/opt/invizible/i2p/i2pd'
        self.config = '/opt/invizible/i2p/i2pd.conf'
        self.process = None

    def start(self):
        """Start I2P daemon"""
        cmd = [self.i2pd_binary, '--conf', self.config, '--datadir', '/var/lib/i2p']
        self.process = subprocess.Popen(cmd)
        print(f"✅ I2P started (HTTP proxy: 4444, SOCKS: 4447)")

    def stop(self):
        """Stop I2P daemon"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("✅ I2P stopped")
```

### Phase 3: Systemd Services (Week 4)

```ini
# /etc/systemd/system/qwamos-tor.service

[Unit]
Description=QWAMOS Tor Service (InviZible Pro)
After=network.target
Wants=qwamos-dnscrypt.service

[Service]
Type=simple
ExecStart=/usr/local/bin/qwamos-tor start
ExecStop=/usr/local/bin/qwamos-tor stop
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/qwamos-dnscrypt.service

[Unit]
Description=QWAMOS DNSCrypt Service (InviZible Pro)
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/qwamos-dnscrypt start
ExecStop=/usr/local/bin/qwamos-dnscrypt stop
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/qwamos-i2p.service

[Unit]
Description=QWAMOS I2P Service (InviZible Pro)
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/qwamos-i2p start
ExecStop=/usr/local/bin/qwamos-i2p stop
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

### Phase 4: React Native UI Integration (Week 5-6)

```typescript
// frontend/screens/NetworkSettings.tsx

import React, { useState } from 'react';
import { View, Text, Switch, TouchableOpacity } from 'react-native';

type NetworkMode = 'tor' | 'tor-dnscrypt' | 'tor-i2p' | 'i2p-only' | 'multilayer';

const NetworkSettings = () => {
  const [mode, setMode] = useState<NetworkMode>('tor-dnscrypt');
  const [torBridges, setTorBridges] = useState(false);
  const [dnscryptEnabled, setDnscryptEnabled] = useState(true);
  const [i2pEnabled, setI2pEnabled] = useState(false);

  const switchMode = async (newMode: NetworkMode) => {
    await NetworkService.switchMode(newMode);
    setMode(newMode);
  };

  return (
    <View>
      <Text style={{fontSize: 20, fontWeight: 'bold'}}>Network Anonymity</Text>

      <TouchableOpacity onPress={() => switchMode('tor')}>
        <Text>🔒 Tor Only</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => switchMode('tor-dnscrypt')}>
        <Text>🔒 Tor + Encrypted DNS (Recommended)</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => switchMode('tor-i2p')}>
        <Text>🔒 Tor + I2P Parallel</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => switchMode('i2p-only')}>
        <Text>👻 I2P Only (Eepsites)</Text>
      </TouchableOpacity>

      <TouchableOpacity onPress={() => switchMode('multilayer')}>
        <Text>🛡️ Maximum Anonymity (Tor over I2P)</Text>
      </TouchableOpacity>

      <View>
        <Text>Tor Bridges (for censored networks)</Text>
        <Switch value={torBridges} onValueChange={setTorBridges} />
      </View>
    </View>
  );
};
```

---

## Benefits of Integration

### 1. Enhanced Privacy
- **Encrypted DNS:** DNSCrypt prevents DNS hijacking and snooping
- **Multiple anonymity layers:** Tor + I2P for redundancy
- **Bridge support:** Bypass censorship in restrictive countries

### 2. Better Mobile Performance
- InviZible Pro's binaries are optimized for ARM mobile processors
- Lower battery consumption than desktop Tor
- Better handling of network switches (WiFi ↔ Mobile data)

### 3. Access to I2P Network
- Browse I2P eepsites (hidden services)
- Anonymous file sharing via I2P BitTorrent
- Participate in I2P email and messaging

### 4. Defense in Depth
- If Tor is compromised, I2P provides fallback
- DNS encryption prevents correlation attacks
- Multiple obfuscation layers (obfs4, meek, snowflake)

---

## Testing Strategy

### Unit Tests
```python
# tests/network/test_invizible_integration.py

def test_tor_start():
    controller = InviZibleTorController()
    controller.start()
    assert controller.process.poll() is None  # Process running

def test_dnscrypt_dns_resolution():
    controller = DNSCryptController()
    controller.start()
    # Test DNS query through encrypted proxy
    result = dns_query('example.com', server='127.0.0.1:5353')
    assert result is not None

def test_i2p_eepsite_access():
    controller = PurpleI2PController()
    controller.start()
    # Test access to I2P hidden service
    response = requests.get('http://example.i2p', proxies={
        'http': 'http://127.0.0.1:4444'
    })
    assert response.status_code == 200
```

### Integration Tests
1. Start all services (Tor + DNSCrypt + I2P)
2. Route VM traffic through whonix-vm
3. Verify anonymity (IP leak tests)
4. Test network switching (Tor ↔ I2P)
5. Test bridge fallback (if direct Tor fails)

---

## Timeline

- **Week 1-2:** Extract InviZible Pro components
- **Week 3:** Create Python control scripts
- **Week 4:** Set up systemd services
- **Week 5-6:** React Native UI integration
- **Week 7:** Testing and debugging
- **Week 8:** Documentation and user guide

**Total:** 8 weeks (2 months)

---

## Resources

- InviZible Pro GitHub: https://github.com/Gedsh/InviZible
- DNSCrypt Protocol: https://dnscrypt.info
- Purple I2P: https://i2pd.website
- Tor Bridge Configuration: https://bridges.torproject.org

---

**Status:** Ready for Implementation
**Next Steps:** Begin extraction of InviZible Pro components in Phase 2
