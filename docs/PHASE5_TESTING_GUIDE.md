# QWAMOS Phase 5 Network Isolation - Testing & Integration Guide

## Overview

This guide covers testing procedures for QWAMOS Phase 5 Network Isolation system, including binary integration, service testing, UI validation, and full integration testing.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Binary Extraction & Testing](#binary-extraction--testing)
3. [Service Integration Testing](#service-integration-testing)
4. [Network Mode Testing](#network-mode-testing)
5. [UI Integration Testing](#ui-integration-testing)
6. [Performance Testing](#performance-testing)
7. [Security Testing](#security-testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

```bash
# Install required packages
pkg install curl unzip file python

# Verify installations
python3 --version
curl --version
systemctl --version  # Requires systemd (on actual QWAMOS device)
```

### Required Permissions

- Root access (for systemd operations)
- Network access (for binary downloads and testing)
- File system access (`/opt/qwamos/`)

---

## Binary Extraction & Testing

### Step 1: Extract InviZible Pro Binaries

```bash
cd ~/QWAMOS
./build/scripts/extract_invizible_binaries.sh
```

**Expected Output:**
```
QWAMOS InviZible Pro Binary Extraction
========================================
[1/8] Checking required tools...
   ✅ All required tools present
[2/8] Creating directories...
   ✅ Directories created
[3/8] Downloading InviZible Pro APK...
   ✅ Download complete
[4/8] Extracting APK...
   ✅ APK extracted
[5/8] Locating ARM64 binaries...
   Found ARM64 library directory
[6/8] Extracting Tor binary...
   ✅ Tor extracted (5MB)
[7/8] Extracting I2P binary...
   ✅ I2P extracted (3MB)
[8/8] Extracting DNSCrypt binary...
   ✅ DNSCrypt extracted (4MB)
```

### Step 2: Test Extracted Binaries

```bash
./network/scripts/test_binaries.sh
```

**Expected Output:**
```
QWAMOS Binary Testing
=====================
[1/6] Checking binary files...
   ✅ Tor binary found and executable
   ✅ I2P binary found and executable
   ✅ DNSCrypt binary found and executable

[2/6] Verifying ARM64 architecture...
   ✅ tor: ARM64
   ✅ i2pd: ARM64
   ✅ dnscrypt-proxy: ARM64

[3/6] Testing Tor binary...
Tor version 0.4.7.13
   ✅ Tor responds to --version

[4/6] Testing I2P binary...
i2pd version 2.46.0
   ✅ I2P responds to --version

[5/6] Testing DNSCrypt binary...
dnscrypt-proxy 2.1.4
   ✅ DNSCrypt responds to --version

[6/6] Checking library dependencies...
   ✅ Binary Testing Complete
```

### Step 3: Install Binaries

```bash
# Copy binaries to system location (requires root)
sudo mkdir -p /opt/qwamos/network/binaries/{tor,i2p,dnscrypt}
sudo cp network/binaries/tor/tor /usr/bin/tor
sudo cp network/binaries/i2p/i2pd /usr/bin/i2pd
sudo cp network/binaries/dnscrypt/dnscrypt-proxy /usr/bin/dnscrypt-proxy
sudo chmod +x /usr/bin/{tor,i2pd,dnscrypt-proxy}
```

---

## Service Integration Testing

### Test 1: DNSCrypt Service

```bash
# Start DNSCrypt service
sudo systemctl start qwamos-dnscrypt.service

# Check status
sudo systemctl status qwamos-dnscrypt.service

# Expected: Active (running)

# Check logs
sudo journalctl -u qwamos-dnscrypt.service -n 50

# Test DNS resolution
dig @127.0.0.1 -p 5353 example.com

# Stop service
sudo systemctl stop qwamos-dnscrypt.service
```

### Test 2: Tor Service

```bash
# Start Tor service
sudo systemctl start qwamos-tor.service

# Check status
sudo systemctl status qwamos-tor.service

# Expected: Active (running)

# Check logs
sudo journalctl -u qwamos-tor.service -n 50

# Test Tor connection
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip

# Expected output should show "IsTor": true

# Stop service
sudo systemctl stop qwamos-tor.service
```

### Test 3: I2P Service

```bash
# Start I2P service
sudo systemctl start qwamos-i2p.service

# Check status
sudo systemctl status qwamos-i2p.service

# Expected: Active (running)

# Check logs
sudo journalctl -u qwamos-i2p.service -n 50

# Wait for I2P to integrate (5-10 minutes)
# Check I2P console
curl http://127.0.0.1:7070

# Stop service
sudo systemctl stop qwamos-i2p.service
```

### Test 4: Network Manager

```bash
# Start all network services via manager
sudo systemctl start qwamos-network-manager.service

# Check status
sudo systemctl status qwamos-network-manager.service

# Get current status
python3 /opt/qwamos/network/network_manager.py status

# Expected output: JSON with service statuses

# Test connectivity
python3 /opt/qwamos/network/network_manager.py test

# Stop all services
sudo systemctl stop qwamos-network-manager.service
```

---

## Network Mode Testing

### Test Each Mode

```bash
# Mode 1: Tor + DNSCrypt (Recommended)
python3 /opt/qwamos/network/network_manager.py switch --mode tor-dnscrypt

# Verify:
curl https://icanhazip.com  # Should show Tor exit IP
dig example.com  # Should use DNSCrypt (port 5353)

# Mode 2: Tor Only
python3 /opt/qwamos/network/network_manager.py switch --mode tor-only

# Verify:
curl https://check.torproject.org/api/ip  # Should show IsTor: true

# Mode 3: Tor + I2P Parallel
python3 /opt/qwamos/network/network_manager.py switch --mode tor-i2p-parallel

# Verify both networks accessible

# Mode 4: I2P Only
python3 /opt/qwamos/network/network_manager.py switch --mode i2p-only

# Verify I2P eepsites accessible

# Mode 5: Maximum Anonymity (Tor → I2P chaining)
python3 /opt/qwamos/network/network_manager.py switch --mode maximum-anonymity

# Verify traffic routes through Tor then I2P

# Mode 6: Direct (No anonymization)
python3 /opt/qwamos/network/network_manager.py switch --mode direct

# Verify real IP shows
curl https://icanhazip.com  # Should show your real IP
```

---

## IP Leak Testing

### Manual Leak Test

```bash
# Run comprehensive leak test
python3 /opt/qwamos/network/tests/test_ip_leak.py

# Review results
cat /tmp/qwamos_leak_test_results.json
```

**Expected Output (Tor mode):**
```json
{
  "tests": {
    "ipv4": {
      "status": "pass",
      "ip": "185.220.xxx.xxx",
      "consistent": true
    },
    "ipv6": {
      "status": "pass",
      "blocked": true
    },
    "dns": {
      "status": "pass"
    },
    "tor": {
      "status": "pass",
      "using_tor": true,
      "ip": "185.220.xxx.xxx"
    }
  },
  "leaks_detected": []
}
```

### Automated Monitoring

```bash
# Start monitoring daemon
sudo systemctl start qwamos-network-monitor.service

# Check monitoring logs
sudo journalctl -u qwamos-network-monitor.service -f

# Stop monitoring
sudo systemctl stop qwamos-network-monitor.service
```

---

## UI Integration Testing

### Test 1: Native Module Installation

1. Add QWAMOSNetworkPackage to your MainApplication.java:

```java
@Override
protected List<ReactPackage> getPackages() {
  List<ReactPackage> packages = new PackageList(this).getPackages();
  packages.add(new QWAMOSNetworkPackage());
  return packages;
}
```

2. Rebuild the React Native app

3. Test native module:

```typescript
import { NativeModules } from 'react-native';
const { QWAMOSNetworkBridge } = NativeModules;

// Test command execution
await QWAMOSNetworkBridge.executeCommand('/usr/bin/python3', ['--version']);
```

### Test 2: Network Settings Screen

1. Navigate to Network Settings
2. Verify current mode displays correctly
3. Test mode switching (Tor Only)
4. Verify loading overlay appears
5. Verify mode switch completes
6. Check service status updates

### Test 3: IP Leak Test Button

1. Tap "Run IP Leak Test" button
2. Verify loading indicator
3. Wait for test completion (~30 seconds)
4. Verify results modal displays
5. Check all 6 tests show results
6. Verify leak status (✅ or ❌)

---

## Performance Testing

### Bandwidth Testing

```bash
# Test each mode's throughput
for mode in direct tor-only tor-dnscrypt tor-i2p-parallel i2p-only maximum-anonymity; do
  echo "Testing mode: $mode"

  # Switch mode
  python3 /opt/qwamos/network/network_manager.py switch --mode $mode

  # Wait for services
  sleep 10

  # Download speed test
  time curl -o /dev/null https://speed.cloudflare.com/__down?bytes=10000000

  echo "---"
done
```

**Expected Relative Speeds:**
- Direct: 100% (baseline)
- Tor Only: 30-50%
- Tor + DNSCrypt: 30-50%
- Tor + I2P Parallel: 25-45%
- I2P Only: 20-40%
- Maximum Anonymity: 15-30%

### Latency Testing

```bash
# Ping test (via Tor)
torify ping -c 10 google.com

# Expected: 200-800ms average
```

---

## Security Testing

### Firewall Rule Verification

```bash
# Check nftables rules loaded
sudo nft list ruleset | grep qwamos

# Expected: QWAMOS filter tables present

# Verify IPv6 blocked
curl -6 https://icanhazip.com
# Expected: Connection refused

# Verify kill switch
sudo systemctl stop qwamos-tor.service
curl https://icanhazip.com
# Expected: Connection refused (kill switch active)
```

### Leak Testing

```bash
# WebRTC leak test (browser-based)
# Visit: https://browserleaks.com/webrtc

# DNS leak test
# Visit: https://dnsleaktest.com

# IPv6 leak test
# Visit: https://test-ipv6.com

# Tor check
# Visit: https://check.torproject.org
```

---

## Troubleshooting

### Issue: Binaries not extracting

**Solution:**
```bash
# Check InviZible Pro APK download
ls -lh /tmp/qwamos_invizible_extract/invizible.apk

# Manual download if needed
curl -L -o /tmp/invizible.apk \
  "https://f-droid.org/repo/pan.alexander.tordnscrypt.stable_7.4.3.apk"
```

### Issue: Services not starting

**Solution:**
```bash
# Check systemd logs
sudo journalctl -xe

# Check binary permissions
ls -l /usr/bin/{tor,i2pd,dnscrypt-proxy}

# Verify configurations
ls -l /opt/qwamos/network/tor/torrc
ls -l /opt/qwamos/network/dnscrypt/dnscrypt-proxy.toml
```

### Issue: Mode switching fails

**Solution:**
```bash
# Check NetworkManager logs
sudo journalctl -u qwamos-network-manager.service -n 100

# Manually stop all services
sudo systemctl stop qwamos-tor.service qwamos-i2p.service qwamos-dnscrypt.service

# Restart network manager
sudo systemctl restart qwamos-network-manager.service
```

### Issue: IP leaks detected

**Solution:**
```bash
# Check firewall rules
sudo nft list ruleset

# Reload firewall
sudo systemctl restart qwamos-network-manager.service

# Re-run leak test
python3 /opt/qwamos/network/tests/test_ip_leak.py
```

### Issue: Native module not found

**Solution:**
```typescript
// Check module registration
import { NativeModules } from 'react-native';
console.log(Object.keys(NativeModules));
// Should include 'QWAMOSNetworkBridge'

// If missing, rebuild app:
// cd android && ./gradlew clean && cd .. && react-native run-android
```

---

## Testing Checklist

### Phase 5 Completion Checklist

- [ ] Binaries extracted successfully
- [ ] All binary tests pass
- [ ] Binaries installed to system paths
- [ ] DNSCrypt service starts and runs
- [ ] Tor service starts and runs
- [ ] I2P service starts and runs
- [ ] Network manager starts all services
- [ ] All 6 network modes switch successfully
- [ ] IP leak tests pass (no leaks)
- [ ] IPv6 properly blocked
- [ ] Kill switch activates on failure
- [ ] Monitoring daemon runs continuously
- [ ] Native module loads in React Native
- [ ] UI displays correct network status
- [ ] Mode switching works from UI
- [ ] IP leak test button works
- [ ] Performance meets expectations
- [ ] Security tests pass

---

## Next Steps

Once all tests pass:

1. Document any issues found
2. Performance tune configurations
3. Create user documentation
4. Prepare for full system integration
5. Begin Phase 6 implementation

---

**Testing Status:** Ready for validation
**Phase 5 Completion:** 85% → 95% (pending final testing)
