# QWAMOS Phase 7: ML Threat Detection & Response
# Deployment Checklist

**Package**: QWAMOS_Phase7_Deployment_20251105.tar.gz
**Size**: 70KB
**Date**: 2025-11-05
**Status**: Ready for deployment to rooted QWAMOS device

---

## Pre-Deployment Requirements

### Hardware Requirements
- [ ] Device rooted with full Linux environment
- [ ] Minimum 4GB RAM available
- [ ] 10GB+ free storage
- [ ] ARMv8-A 64-bit processor (8 cores recommended)

### Software Requirements
- [ ] Systemd installed and running
- [ ] Python 3.8+ installed
- [ ] pip3 package manager available
- [ ] Root access (sudo) available
- [ ] Network connectivity for dependency installation

### Phase Dependencies
- [ ] Phase 1: Secure Bootloader (100% complete)
- [ ] Phase 2: Hardened Kernel (100% complete)
- [ ] Phase 3: Hypervisor & VM Management (100% complete)
- [ ] Phase 4: Post-Quantum Cryptography (100% complete)
- [ ] Phase 6: AI Assistants (100% complete) - REQUIRED for AI Response Coordinator

---

## Package Contents Verification

### Python ML Detectors (3 files, ~1,650 LOC)
- [ ] `security/ml/network_anomaly_detector.py` (~600 lines)
- [ ] `security/ml/file_system_monitor.py` (~550 lines)
- [ ] `security/ml/system_call_analyzer.py` (~500 lines)

### AI Response System (2 files, ~950 LOC)
- [ ] `security/ai_response/ai_response_coordinator.py` (~550 lines)
- [ ] `security/actions/action_executor.py` (~400 lines)

### Systemd Services (4 files, ~210 LOC)
- [ ] `security/systemd/qwamos-ml-network-anomaly.service`
- [ ] `security/systemd/qwamos-ml-file-system.service`
- [ ] `security/systemd/qwamos-ml-system-call.service`
- [ ] `security/systemd/qwamos-ai-response.service`

### Deployment Scripts (1 file, ~395 LOC)
- [ ] `security/scripts/deploy_threat_detection.sh`

### React Native UI (1 file, ~600 LOC)
- [ ] `ui/screens/ThreatDetection/ThreatDashboard.tsx`

### TypeScript Service Layer (1 file, ~350 LOC)
- [ ] `ui/services/ThreatDetectionService.ts`

### Java Native Bridge (2 files, ~300 LOC)
- [ ] `ui/native/QWAMOSThreatBridge.java` (~280 lines)
- [ ] `ui/native/QWAMOSThreatPackage.java` (~20 lines)

### Documentation (5 files, ~3,200 LOC)
- [ ] `docs/PHASE7_DEPLOYMENT_GUIDE.md` (~1,200 lines)
- [ ] `docs/PHASE7_ML_TRAINING_GUIDE.md` (~1,300 lines)
- [ ] `docs/PHASE7_API_DOCUMENTATION.md` (~700 lines)
- [ ] `docs/PHASE7_COMPLETION_SUMMARY.md` (~900 lines)
- [ ] `docs/PHASE7_ML_THREAT_DETECTION.md` (specification, 900 lines)
- [ ] `security/README.md` (updated)

**Total**: 18 files, ~8,585 lines of code

---

## Deployment Steps

### Step 1: Transfer Package to Device

**Option A: USB Transfer**
```bash
# On development machine
adb push QWAMOS_Phase7_Deployment_20251105.tar.gz /sdcard/

# On device (via Termux or SSH)
sudo cp /sdcard/QWAMOS_Phase7_Deployment_20251105.tar.gz /opt/qwamos/
```

**Option B: Network Transfer**
```bash
# On device
cd /opt/qwamos
sudo wget http://YOUR_SERVER/QWAMOS_Phase7_Deployment_20251105.tar.gz
# or
sudo scp user@host:/path/to/QWAMOS_Phase7_Deployment_20251105.tar.gz .
```

- [ ] Package transferred to device
- [ ] Package integrity verified (SHA256 checksum)

### Step 2: Extract Package

```bash
cd /opt/qwamos
sudo tar -xzf QWAMOS_Phase7_Deployment_20251105.tar.gz
```

- [ ] Package extracted successfully
- [ ] All files present (verify with validation script below)

### Step 3: Run Automated Deployment

```bash
cd /opt/qwamos/security
sudo chmod +x scripts/deploy_threat_detection.sh
sudo ./scripts/deploy_threat_detection.sh
```

The deployment script will:
- [ ] Create directory structure (`/opt/qwamos/security/`)
- [ ] Copy ML detectors to `/opt/qwamos/security/ml/`
- [ ] Copy AI response components to `/opt/qwamos/security/ai_response/`
- [ ] Copy action executor to `/opt/qwamos/security/actions/`
- [ ] Install systemd services to `/etc/systemd/system/`
- [ ] Create qwamos user if not exists
- [ ] Set correct permissions (qwamos:qwamos)
- [ ] Install Python dependencies (TensorFlow Lite, Scapy, Watchdog, etc.)
- [ ] Create configuration files in `/opt/qwamos/security/config/`
- [ ] Create quarantine directory `/opt/qwamos/security/quarantine/`

### Step 4: Verify Installation

```bash
# Check directory structure
ls -la /opt/qwamos/security/

# Check systemd services
sudo systemctl list-unit-files | grep qwamos-ml

# Check Python dependencies
pip3 list | grep -E "tensorflow|scapy|watchdog"

# Verify permissions
ls -l /opt/qwamos/security/ml/*.py
```

- [ ] All directories created
- [ ] All files in correct locations
- [ ] Systemd services installed
- [ ] Python dependencies installed
- [ ] Permissions set correctly

### Step 5: Configure Services

Edit configuration files as needed:

```bash
# AI Response configuration
sudo nano /opt/qwamos/security/config/ai_response_config.json

# Action Executor configuration
sudo nano /opt/qwamos/security/config/action_executor_config.json

# User permissions
sudo nano /opt/qwamos/security/config/permissions.json
```

**Recommended Settings for Initial Deployment:**
- `auto_response_severity`: "HIGH" (only respond to HIGH/CRITICAL automatically)
- `require_permission_above`: "MEDIUM" (require approval for MEDIUM+ actions)
- `enable_auto_patching`: false (disable auto-patching initially)
- `enable_network_isolation`: true (allow automatic network isolation)

- [ ] AI response config reviewed
- [ ] Action executor config reviewed
- [ ] User permissions configured

### Step 6: Enable and Start Services

```bash
# Enable services on boot
sudo systemctl enable qwamos-ml-network-anomaly.service
sudo systemctl enable qwamos-ml-file-system.service
sudo systemctl enable qwamos-ml-system-call.service
sudo systemctl enable qwamos-ai-response.service

# Start services
sudo systemctl start qwamos-ai-response.service
sleep 5
sudo systemctl start qwamos-ml-network-anomaly.service
sudo systemctl start qwamos-ml-file-system.service
sudo systemctl start qwamos-ml-system-call.service
```

- [ ] Services enabled on boot
- [ ] Services started successfully

### Step 7: Verify Service Status

```bash
# Check all services
sudo systemctl status qwamos-ml-*.service qwamos-ai-response.service

# Check logs for errors
sudo journalctl -u qwamos-ml-network-anomaly.service --since "5 minutes ago"
sudo journalctl -u qwamos-ml-file-system.service --since "5 minutes ago"
sudo journalctl -u qwamos-ml-system-call.service --since "5 minutes ago"
sudo journalctl -u qwamos-ai-response.service --since "5 minutes ago"
```

**Expected Status**: All services should be "active (running)"

- [ ] All services running
- [ ] No errors in logs
- [ ] Services auto-restart on failure

---

## Testing & Validation

### Test 1: Network Anomaly Detection

```bash
# Trigger port scan (safe test)
nmap -sS -T2 localhost

# Monitor detection
sudo journalctl -f -u qwamos-ml-network-anomaly.service
```

**Expected**: Port scan detected, logged as MEDIUM severity

- [ ] Network anomaly detected
- [ ] Threat logged correctly

### Test 2: File System Monitor

```bash
# Simulate suspicious file activity
mkdir -p /tmp/qwamos_test
cd /tmp/qwamos_test
for i in {1..50}; do
  echo "Test" > file_$i.txt
  openssl enc -aes-256-cbc -salt -in file_$i.txt -out file_$i.encrypted -k test
  rm file_$i.txt
done

# Monitor detection
sudo journalctl -f -u qwamos-ml-file-system.service
```

**Expected**: Mass encryption detected, potential ransomware alert

- [ ] File system anomaly detected
- [ ] Threat logged correctly

### Test 3: AI Response Coordinator

```bash
# Check AI response for detected threats
sudo journalctl -u qwamos-ai-response.service | grep -A 10 "Threat received"
```

**Expected**: Multi-AI response pipeline executed (Kali GPT → Claude → ChatGPT)

- [ ] AI response triggered
- [ ] Multi-AI pipeline executed
- [ ] Action plan created

### Test 4: React Native UI

Compile and run React Native app:

```bash
cd /opt/qwamos/ui
npx react-native run-android
```

Navigate to: **Security** → **Threat Detection**

- [ ] ThreatDashboard screen loads
- [ ] System health meter displays
- [ ] Detector toggles work
- [ ] Threat list displays recent threats
- [ ] Threat detail modal opens

---

## Post-Deployment Tasks

### ML Model Training (Required for Production)

Phase 7 includes ML model training guides:

```bash
# Review training guide
less /opt/qwamos/docs/PHASE7_ML_TRAINING_GUIDE.md

# Collect training data
# - Network traffic captures (PCAP files)
# - File system events (benign and malicious)
# - System call traces

# Train models (see guide for detailed instructions)
python3 /opt/qwamos/security/ml/training/train_network_autoencoder.py
python3 /opt/qwamos/security/ml/training/train_file_classifier.py
python3 /opt/qwamos/security/ml/training/train_syscall_lstm.py

# Deploy trained models
sudo cp models/*.tflite /opt/qwamos/security/ml/models/

# Restart services to load new models
sudo systemctl restart qwamos-ml-*.service
```

**Note**: Until models are trained, detectors run in rule-based mode (reduced accuracy but still functional).

- [ ] Training data collected
- [ ] Models trained and evaluated
- [ ] Models deployed to production

### Performance Monitoring

```bash
# Monitor resource usage
sudo systemctl status qwamos-ml-*.service | grep -E "Memory|CPU"

# Check detection latency
sudo journalctl -u qwamos-ml-network-anomaly.service | grep "Detection time"

# Monitor threat detection rate
sudo journalctl -u qwamos-ml-*.service | grep "\[THREAT\]" | wc -l
```

- [ ] Resource usage acceptable (< 6.5GB RAM, < 180% CPU)
- [ ] Detection latency acceptable (< 150ms)
- [ ] False positive rate acceptable (< 5%)

### Integration with Phase 6 (AI Assistants)

Verify AI assistants are running:

```bash
sudo systemctl status qwamos-ai-manager.service
sudo systemctl status qwamos-kali-gpt.service
```

- [ ] AI Manager service running
- [ ] Kali GPT service running
- [ ] AI Response Coordinator can query AI services

---

## Troubleshooting

### Services Won't Start

**Check**: Dependencies and permissions

```bash
# Verify Python dependencies
pip3 list | grep -E "tensorflow|scapy|watchdog"

# Check file permissions
ls -l /opt/qwamos/security/ml/*.py

# View detailed errors
sudo journalctl -xe -u qwamos-ml-network-anomaly.service
```

**Common Fixes**:
- Install missing dependencies: `sudo pip3 install tensorflow-lite scapy watchdog asyncio`
- Fix permissions: `sudo chown -R qwamos:qwamos /opt/qwamos/security`
- Check Python path: `which python3`

### High False Positive Rate

**Solution**: Adjust detection thresholds

```bash
# Edit detector scripts
sudo nano /opt/qwamos/security/ml/network_anomaly_detector.py
# Change: self.anomaly_threshold = 0.15 to 0.20

# Restart services
sudo systemctl restart qwamos-ml-network-anomaly.service
```

### AI Response Timeout

**Solution**: Verify Tor connectivity and increase timeout

```bash
# Check Tor
sudo systemctl status qwamos-tor.service
curl --socks5-hostname localhost:9050 https://check.torproject.org

# Increase timeout
sudo nano /opt/qwamos/security/config/ai_response_config.json
# Change: "ai_timeout": 60 to "ai_timeout": 120
```

For comprehensive troubleshooting, see: `/opt/qwamos/docs/PHASE7_DEPLOYMENT_GUIDE.md`

---

## Rollback Procedure

If deployment fails or causes issues:

```bash
# Stop all services
sudo systemctl stop qwamos-ml-*.service qwamos-ai-response.service

# Disable services
sudo systemctl disable qwamos-ml-*.service qwamos-ai-response.service

# Remove systemd services
sudo rm /etc/systemd/system/qwamos-ml-*.service /etc/systemd/system/qwamos-ai-response.service
sudo systemctl daemon-reload

# Remove Phase 7 files (optional, keeps for future retry)
sudo rm -rf /opt/qwamos/security/ml
sudo rm -rf /opt/qwamos/security/ai_response
sudo rm -rf /opt/qwamos/security/actions

# Restore system to pre-Phase 7 state
```

- [ ] Rollback completed (if needed)

---

## Sign-Off

### Deployment Completed By

**Name**: ___________________________
**Date**: ___________________________
**Signature**: ______________________

### Verification

- [ ] All 18 files deployed successfully
- [ ] All 4 systemd services running
- [ ] All tests passed
- [ ] Performance acceptable
- [ ] Documentation reviewed
- [ ] User training completed (if applicable)

### Notes

```
[Add any deployment notes, issues encountered, or special configurations here]






```

---

## Support Resources

- **Deployment Guide**: `/opt/qwamos/docs/PHASE7_DEPLOYMENT_GUIDE.md`
- **ML Training Guide**: `/opt/qwamos/docs/PHASE7_ML_TRAINING_GUIDE.md`
- **API Documentation**: `/opt/qwamos/docs/PHASE7_API_DOCUMENTATION.md`
- **GitHub Issues**: https://github.com/Dezirae-Stark/QWAMOS/issues
- **Logs**: `/var/log/qwamos/`
- **System Logs**: `sudo journalctl -u 'qwamos-*'`

---

**Phase 7: ML Threat Detection & Response**
**Status**: Ready for deployment
**Package**: QWAMOS_Phase7_Deployment_20251105.tar.gz (70KB)
**Total Implementation**: 18 files, ~8,585 lines of code
