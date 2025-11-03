# QWAMOS Phase 5 - Integration Checklist

## Overview

This checklist guides the final 5% of Phase 5 completion: integrating the native module into the React Native app and running full system tests on an actual device.

**Current Status:** 95% Complete (Code implementation finished)
**Remaining:** 5% (Integration + Validation)

---

## Prerequisites

### Required Hardware
- [ ] Android device with ARM64 processor
- [ ] Root access (via Magisk or equivalent)
- [ ] Minimum 2GB free storage
- [ ] Active internet connection (for Tor/I2P bootstrap)

### Required Software
- [ ] Android Studio (for React Native build)
- [ ] Node.js v16+ and npm
- [ ] React Native CLI
- [ ] ADB (Android Debug Bridge)
- [ ] Git

### Required Permissions
- [ ] Root shell access (`su`)
- [ ] Storage permissions (read/write /opt/qwamos/)
- [ ] Network permissions (full internet access)

---

## Step 1: Native Module Integration (2%)

### 1.1 Locate MainApplication.java

```bash
# In your React Native Android project
find android/app/src/main/java -name "MainApplication.java"
```

**Expected location:**
```
android/app/src/main/java/com/yourapp/MainApplication.java
```

### 1.2 Add QWAMOSNetworkPackage

Open `MainApplication.java` and modify the `getPackages()` method:

```java
import com.qwamos.network.QWAMOSNetworkPackage;  // Add this import

@Override
protected List<ReactPackage> getPackages() {
  @SuppressWarnings("UnnecessaryLocalVariable")
  List<ReactPackage> packages = new PackageList(this).getPackages();

  // Add QWAMOS Network Package
  packages.add(new QWAMOSNetworkPackage());

  return packages;
}
```

### 1.3 Copy Native Module Files

```bash
# Copy native module to Android project
cp ~/QWAMOS/ui/native/QWAMOSNetworkBridge.java \
   android/app/src/main/java/com/qwamos/network/

cp ~/QWAMOS/ui/native/QWAMOSNetworkPackage.java \
   android/app/src/main/java/com/qwamos/network/
```

### 1.4 Rebuild React Native App

```bash
cd android
./gradlew clean
cd ..

# Build debug APK
react-native run-android

# OR build release APK
cd android
./gradlew assembleRelease
```

### 1.5 Verify Native Module Loaded

In React Native app (JavaScript console):

```typescript
import { NativeModules } from 'react-native';

console.log('Native modules:', Object.keys(NativeModules));
// Should include 'QWAMOSNetworkBridge'

const { QWAMOSNetworkBridge } = NativeModules;
console.log('QWAMOSNetworkBridge:', QWAMOSNetworkBridge);

// Test basic command
QWAMOSNetworkBridge.executeCommand('/usr/bin/python3', ['--version'])
  .then(output => console.log('Python version:', output))
  .catch(err => console.error('Error:', err));
```

**Expected output:**
```
QWAMOSNetworkBridge: [object Object]
Python version: Python 3.11.x
```

**✅ Checklist:**
- [ ] MainApplication.java modified
- [ ] Native module files copied
- [ ] App rebuilt successfully
- [ ] QWAMOSNetworkBridge appears in NativeModules
- [ ] Test command execution works

---

## Step 2: Binary Extraction on Device (1%)

### 2.1 Transfer Extraction Script to Device

```bash
# Connect device via ADB
adb devices

# Push extraction script
adb push ~/QWAMOS/build/scripts/extract_invizible_binaries.sh /data/local/tmp/

# Enter ADB shell
adb shell

# Become root
su

# Make script executable
chmod +x /data/local/tmp/extract_invizible_binaries.sh
```

### 2.2 Run Binary Extraction

```bash
# Run extraction (as root)
cd /data/local/tmp
./extract_invizible_binaries.sh
```

**Expected output:**
```
QWAMOS InviZible Pro Binary Extraction
========================================
[1/8] Checking required tools...
   ✅ All required tools present
[2/8] Creating directories...
   ✅ Directories created
[3/8] Downloading InviZible Pro APK...
   ✅ Download complete (50MB)
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

Extraction Complete!
Binaries saved to: /tmp/qwamos_invizible_extract/binaries/
```

### 2.3 Install Binaries to System

```bash
# Create system directories
mkdir -p /opt/qwamos/network/binaries/{tor,i2p,dnscrypt}
mkdir -p /opt/qwamos/network/{scripts,tests,modes}

# Copy binaries
cp /tmp/qwamos_invizible_extract/binaries/tor/tor /usr/bin/tor
cp /tmp/qwamos_invizible_extract/binaries/i2p/i2pd /usr/bin/i2pd
cp /tmp/qwamos_invizible_extract/binaries/dnscrypt/dnscrypt-proxy /usr/bin/dnscrypt-proxy

# Set permissions
chmod +x /usr/bin/{tor,i2pd,dnscrypt-proxy}

# Verify installation
tor --version
i2pd --version
dnscrypt-proxy --version
```

**Expected output:**
```
Tor version 0.4.7.13
i2pd version 2.46.0
dnscrypt-proxy 2.1.4
```

### 2.4 Copy Python Controllers

```bash
# Copy Python scripts from QWAMOS repo to device
adb push ~/QWAMOS/network/network_manager.py /opt/qwamos/network/
adb push ~/QWAMOS/network/tor/tor_controller.py /opt/qwamos/network/tor/
adb push ~/QWAMOS/network/i2p/i2p_controller.py /opt/qwamos/network/i2p/
adb push ~/QWAMOS/network/dnscrypt/dnscrypt_controller.py /opt/qwamos/network/dnscrypt/
adb push ~/QWAMOS/network/vpn/vpn_controller.py /opt/qwamos/network/vpn/
adb push ~/QWAMOS/network/scripts/network-monitor.py /opt/qwamos/network/scripts/
adb push ~/QWAMOS/network/tests/test_ip_leak.py /opt/qwamos/network/tests/

# Set executable permissions
adb shell "chmod +x /opt/qwamos/network/*.py"
adb shell "chmod +x /opt/qwamos/network/*/*.py"
```

**✅ Checklist:**
- [ ] Extraction script transferred to device
- [ ] Binaries extracted successfully
- [ ] Binaries installed to /usr/bin/
- [ ] Binary versions verified
- [ ] Python controllers copied to device

---

## Step 3: Full System Testing (2%)

### 3.1 Service Integration Tests

Follow procedures from `PHASE5_TESTING_GUIDE.md`:

```bash
# Test Tor binary
adb shell "su -c 'tor --version'"

# Test I2P binary
adb shell "su -c 'i2pd --version'"

# Test DNSCrypt binary
adb shell "su -c 'dnscrypt-proxy --version'"

# Test Python network manager
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py status'"
```

**Expected output:**
```json
{
  "current_mode": "direct",
  "services": {
    "tor": "stopped",
    "i2p": "stopped",
    "dnscrypt": "stopped",
    "vpn": "stopped"
  },
  "firewall": "inactive",
  "public_ip": "xxx.xxx.xxx.xxx"
}
```

### 3.2 Network Mode Tests

Test each of the 6 network modes:

```bash
# Mode 1: Tor Only
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py switch --mode tor-only'"

# Verify Tor IP
adb shell "su -c 'curl --socks5 127.0.0.1:9050 https://icanhazip.com'"
# Should show Tor exit IP (different from real IP)

# Mode 2: Tor + DNSCrypt (Recommended)
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py switch --mode tor-dnscrypt'"

# Mode 3: Maximum Anonymity
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py switch --mode maximum-anonymity'"

# Mode 4: Direct
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py switch --mode direct'"
```

### 3.3 IP Leak Tests

```bash
# Run comprehensive leak test
adb shell "su -c 'python3 /opt/qwamos/network/tests/test_ip_leak.py'"

# Check results
adb shell "cat /tmp/qwamos_leak_test_results.json"
```

**Expected result (Tor mode):**
```json
{
  "tests": {
    "ipv4": {"status": "pass", "ip": "185.220.xxx.xxx"},
    "ipv6": {"status": "pass", "blocked": true},
    "dns": {"status": "pass"},
    "tor": {"status": "pass", "using_tor": true}
  },
  "leaks_detected": [],
  "overall_status": "PASS"
}
```

### 3.4 UI Integration Tests

**Test 1: Network Settings Screen**
1. Open React Native app
2. Navigate to Settings → Network
3. Verify current mode displays
4. Check service status indicators (should be accurate)

**Test 2: Mode Switching**
1. Tap "Tor + DNSCrypt" mode card
2. Verify loading overlay appears
3. Wait for mode switch (~10 seconds)
4. Verify success message
5. Check status indicators update to "Active"

**Test 3: IP Leak Test Button**
1. Tap "Run IP Leak Test" button
2. Wait for test completion (~30 seconds)
3. Verify results modal displays
4. Check all tests show ✅ (pass)
5. Close modal

### 3.5 Performance Benchmarks

```bash
# Test download speed in each mode
for mode in direct tor-only tor-dnscrypt tor-i2p-parallel i2p-only maximum-anonymity; do
  echo "Testing mode: $mode"
  adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py switch --mode $mode'"
  sleep 10
  adb shell "su -c 'time curl -o /dev/null https://speed.cloudflare.com/__down?bytes=10000000'"
  echo "---"
done
```

**Record results:**
| Mode                | Speed (Mbps) | Latency (ms) |
|---------------------|--------------|--------------|
| Direct              |              |              |
| Tor Only            |              |              |
| Tor + DNSCrypt      |              |              |
| Tor + I2P Parallel  |              |              |
| I2P Only            |              |              |
| Maximum Anonymity   |              |              |

**✅ Checklist:**
- [ ] All binaries respond to --version
- [ ] Network manager status command works
- [ ] All 6 modes switch successfully
- [ ] IP changes when switching to Tor modes
- [ ] IP leak tests pass (no leaks detected)
- [ ] UI displays correct network status
- [ ] Mode switching works from UI
- [ ] Leak test button functions
- [ ] Performance benchmarks recorded

---

## Step 4: Final Validation

### 4.1 Security Validation

```bash
# Test IPv6 blocking
adb shell "su -c 'curl -6 https://icanhazip.com'"
# Expected: Connection refused or timeout

# Test kill switch
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py switch --mode tor-only'"
# Wait for Tor to start
sleep 20
# Stop Tor service
adb shell "su -c 'killall tor'"
# Try to connect
adb shell "su -c 'curl https://icanhazip.com'"
# Expected: Connection refused (kill switch active)
```

### 4.2 Long-term Stability Test

```bash
# Start monitoring daemon
adb shell "su -c 'python3 /opt/qwamos/network/scripts/network-monitor.py &'"

# Run for 1 hour in Tor mode
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py switch --mode tor-dnscrypt'"

# Check for leaks every 10 minutes
# (monitoring daemon does this automatically)
```

### 4.3 Documentation Review

- [ ] Read PHASE5_NETWORK_ISOLATION.md (architecture)
- [ ] Read PHASE5_TESTING_GUIDE.md (testing procedures)
- [ ] Read PHASE5_COMPLETION_SUMMARY.md (development history)
- [ ] Understand all 6 network modes
- [ ] Review security features (kill switch, leak detection)

---

## Step 5: Completion Verification

### 5.1 Component Checklist

**Python Backend:**
- [ ] network_manager.py functional
- [ ] tor_controller.py functional
- [ ] i2p_controller.py functional
- [ ] dnscrypt_controller.py functional
- [ ] vpn_controller.py functional
- [ ] network-monitor.py functional
- [ ] test_ip_leak.py functional

**React Native UI:**
- [ ] NetworkSettings.tsx renders
- [ ] NetworkModeCard.tsx displays correctly
- [ ] NetworkStatusIndicator.tsx shows accurate status
- [ ] IPLeakTestButton.tsx executes tests
- [ ] NetworkManager.ts communicates with backend

**Native Module:**
- [ ] QWAMOSNetworkBridge.java loaded
- [ ] QWAMOSNetworkPackage.java registered
- [ ] Command execution works
- [ ] File I/O works
- [ ] No memory leaks

**Binaries:**
- [ ] Tor binary (5MB) extracted and functional
- [ ] I2P binary (3MB) extracted and functional
- [ ] DNSCrypt binary (4MB) extracted and functional

**Network Modes:**
- [ ] Mode 1: Direct works
- [ ] Mode 2: Tor Only works
- [ ] Mode 3: Tor + DNSCrypt works
- [ ] Mode 4: Tor + I2P Parallel works
- [ ] Mode 5: I2P Only works
- [ ] Mode 6: Maximum Anonymity works

**Security:**
- [ ] IPv6 properly blocked
- [ ] Kill switch activates on failure
- [ ] IP leak tests pass (0 leaks)
- [ ] DNS encryption active
- [ ] Real IP never exposed in Tor modes

**Performance:**
- [ ] Tor mode: 30-50% speed
- [ ] Maximum Anonymity: 15-30% speed
- [ ] Memory usage: <300MB total
- [ ] No crashes or freezes

### 5.2 Issue Log

Document any issues encountered:

| Issue | Severity | Status | Resolution |
|-------|----------|--------|------------|
|       |          |        |            |

---

## Step 6: Declare Phase 5 Complete

Once all items above are checked:

1. **Update README.md**
```markdown
## Phase 5: Network Isolation ✅ 100% Complete

Multi-layered anonymization system with Tor, I2P, DNSCrypt, and VPN.

- 6 network routing modes
- IP leak detection (6-test suite)
- Kill switch protection
- React Native UI integration
- Post-quantum VPN (Kyber-1024)
```

2. **Create Completion Tag**
```bash
cd ~/QWAMOS
git tag -a phase5-complete -m "Phase 5: Network Isolation - 100% Complete"
git push origin phase5-complete
```

3. **Final Commit**
```bash
git add .
git commit -m "Phase 5: 100% Complete - All tests passed"
git push
```

---

## Troubleshooting

### Issue: Native Module Not Found

**Solution:**
```bash
# Check package registration
grep "QWAMOSNetworkPackage" android/app/src/main/java/*/MainApplication.java

# Rebuild app
cd android && ./gradlew clean && cd ..
react-native run-android
```

### Issue: Binaries Not Executing

**Solution:**
```bash
# Check permissions
adb shell "su -c 'ls -l /usr/bin/{tor,i2pd,dnscrypt-proxy}'"

# Should show: -rwxr-xr-x (executable)

# Fix if needed
adb shell "su -c 'chmod +x /usr/bin/{tor,i2pd,dnscrypt-proxy}'"
```

### Issue: IP Leaks Detected

**Solution:**
```bash
# Check IPv6 blocking
adb shell "su -c 'ip6tables -L'"

# Block IPv6 manually if needed
adb shell "su -c 'ip6tables -P OUTPUT DROP'"

# Restart Tor
adb shell "su -c 'killall tor && python3 /opt/qwamos/network/tor/tor_controller.py start'"
```

### Issue: Mode Switching Fails

**Solution:**
```bash
# Check logs
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py status'"

# Stop all services
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py stop'"

# Restart in desired mode
adb shell "su -c 'python3 /opt/qwamos/network/network_manager.py switch --mode tor-dnscrypt'"
```

---

## Success Criteria

Phase 5 is 100% complete when:

✅ All checklist items above are marked complete
✅ No critical issues remain unresolved
✅ All 6 network modes work reliably
✅ IP leak tests consistently pass (0 leaks)
✅ UI correctly reflects backend status
✅ Performance meets expectations
✅ Security features function as designed
✅ Documentation is accurate and complete

---

**Document Version:** 1.0
**Last Updated:** 2025-11-03
**Phase 5 Status:** 95% → 100% (pending final integration)
