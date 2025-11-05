# QWAMOS Phase 7: ML Threat Detection & Response - Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Service Management](#service-management)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)
10. [Performance Tuning](#performance-tuning)

---

## Overview

Phase 7 implements a comprehensive ML-powered threat detection and automated response system for QWAMOS, featuring:

- **Network Anomaly Detection**: Real-time traffic analysis using Autoencoder neural networks
- **File System Monitoring**: Ransomware and malware detection using Random Forest classifiers
- **System Call Analysis**: Exploit detection using LSTM sequence analysis
- **AI-Powered Response**: Multi-AI coordination (Kali GPT → Claude → ChatGPT) for threat mitigation
- **Automated Actions**: Permission-based security response execution
- **React Native Dashboard**: Real-time threat monitoring and management

### Key Features

✅ On-device ML inference using TensorFlow Lite (ARM64 optimized)
✅ Multi-layer threat detection (network, file system, system calls)
✅ Automated response with permission controls
✅ Multi-AI strategic planning via Tor
✅ Real-time threat dashboard
✅ Quarantine and rollback capabilities
✅ Comprehensive logging and audit trails

---

## Prerequisites

### Hardware Requirements

- **CPU**: ARMv8-A 64-bit (8 cores recommended)
- **RAM**: Minimum 4GB, 8GB+ recommended
- **Storage**: 10GB+ free space for ML models and quarantine

### Software Requirements

- **OS**: QWAMOS (Phases 1-6 completed)
- **Python**: 3.8+ with pip3
- **Systemd**: Service management
- **Root Access**: Required for deployment

### Dependencies

Python packages (automatically installed by deployment script):
```bash
tensorflow-lite     # ML inference
numpy              # Numerical computing
scapy              # Packet manipulation
watchdog           # File system monitoring
asyncio            # Async I/O
```

### Phase Dependencies

Phase 7 requires completion of:
- **Phase 1**: Secure Bootloader (Kyber PQC)
- **Phase 2**: Hardened Kernel
- **Phase 3**: Hypervisor & VM Management
- **Phase 4**: AI Assistants Integration
- **Phase 5**: Network Isolation (optional, enhances security)
- **Phase 6**: AI Assistants (required for AI Response Coordinator)

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    React Native UI                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ThreatDashboard.tsx - Real-time monitoring          │  │
│  │  ThreatDetectionService.ts - TypeScript API layer    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ ↑
┌─────────────────────────────────────────────────────────────┐
│                  ML Detection Layer                         │
│  ┌────────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │ Network        │ │ File System  │ │ System Call      │  │
│  │ Anomaly        │ │ Monitor      │ │ Analyzer         │  │
│  │ Detector       │ │              │ │                  │  │
│  │ (Autoencoder)  │ │ (Random      │ │ (LSTM)           │  │
│  │                │ │  Forest)     │ │                  │  │
│  └────────────────┘ └──────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              AI Response Coordinator                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Kali GPT (Local) - Technical Analysis            │  │
│  │  2. Claude (Tor) - Strategic Planning                │  │
│  │  3. ChatGPT (Tor) - Tactical Commands                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 Action Executor                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Firewall Rules       • VM Snapshots               │  │
│  │  • Process Termination  • File Quarantine            │  │
│  │  • Network Isolation    • Auto-Patching              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### ML Models

1. **Network Anomaly Autoencoder** (`network_ae.tflite`)
   - Input: 50-dimensional feature vector (packet metadata, entropy, temporal patterns)
   - Architecture: Encoder (50→32→16) + Decoder (16→32→50)
   - Detection: Reconstruction error threshold (default: 0.15)
   - Threats: Port scans, DDoS, C2 communications, data exfiltration

2. **File System Random Forest** (`file_classifier.tflite`)
   - Input: 30-dimensional feature vector (file attributes, modification patterns)
   - Architecture: 100 decision trees, max depth 10
   - Detection: Classification confidence threshold (default: 0.7)
   - Threats: Ransomware, malware, unauthorized modifications

3. **System Call LSTM** (`syscall_lstm.tflite`)
   - Input: Sequence of 128 system calls (one-hot encoded)
   - Architecture: LSTM (128→64→32) + Dense (32→1)
   - Detection: Anomaly score threshold (default: 0.8)
   - Threats: Privilege escalation, process injection, reverse shells

### Directory Structure

```
/opt/qwamos/security/
├── ml/
│   ├── network_anomaly_detector.py       # Network ML detector
│   ├── file_system_monitor.py            # File system ML monitor
│   ├── system_call_analyzer.py           # Syscall ML analyzer
│   ├── models/
│   │   ├── network_ae.tflite             # Network autoencoder
│   │   ├── file_classifier.tflite        # File classifier
│   │   └── syscall_lstm.tflite           # Syscall LSTM
│   ├── training/                         # Training scripts
│   └── data/                             # Training datasets
├── ai_response/
│   └── ai_response_coordinator.py        # Multi-AI coordinator
├── actions/
│   └── action_executor.py                # Security action executor
├── config/
│   ├── ai_response_config.json           # AI response settings
│   ├── action_executor_config.json       # Action executor settings
│   └── permissions.json                  # User permissions
├── quarantine/                           # Quarantined files
└── scripts/                              # Helper scripts

/var/log/qwamos/                          # System logs
/var/run/qwamos/                          # Runtime data

/etc/systemd/system/
├── qwamos-ml-network-anomaly.service     # Network detector service
├── qwamos-ml-file-system.service         # File system monitor service
├── qwamos-ml-system-call.service         # Syscall analyzer service
└── qwamos-ai-response.service            # AI response service
```

---

## Installation

### Automated Deployment (Recommended)

The deployment script automates the entire installation process.

1. **Navigate to security directory**:
```bash
cd /data/data/com.termux/files/home/QWAMOS/security
```

2. **Run deployment script as root**:
```bash
sudo ./scripts/deploy_threat_detection.sh
```

3. **Follow interactive prompts**:
   - Service enablement (start on boot)
   - Service startup (start immediately)

The script will:
- ✅ Create directory structure
- ✅ Copy ML detectors and AI components
- ✅ Install systemd services
- ✅ Set permissions (qwamos user)
- ✅ Install Python dependencies
- ✅ Create configuration files
- ✅ Check for ML models
- ✅ Enable and start services

### Manual Installation

If you prefer manual installation:

#### Step 1: Create Directories

```bash
sudo mkdir -p /opt/qwamos/security/{ml,ai_response,actions,monitors,config,quarantine}
sudo mkdir -p /opt/qwamos/security/ml/{models,training,data}
sudo mkdir -p /var/log/qwamos
sudo mkdir -p /var/run/qwamos
```

#### Step 2: Create qwamos User

```bash
sudo useradd -r -s /bin/false qwamos
```

#### Step 3: Copy Components

```bash
# ML detectors
sudo cp ml/network_anomaly_detector.py /opt/qwamos/security/ml/
sudo cp ml/file_system_monitor.py /opt/qwamos/security/ml/
sudo cp ml/system_call_analyzer.py /opt/qwamos/security/ml/
sudo chmod +x /opt/qwamos/security/ml/*.py

# AI response
sudo cp ai_response/ai_response_coordinator.py /opt/qwamos/security/ai_response/
sudo chmod +x /opt/qwamos/security/ai_response/*.py

# Action executor
sudo cp actions/action_executor.py /opt/qwamos/security/actions/
sudo chmod +x /opt/qwamos/security/actions/*.py

# Systemd services
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
```

#### Step 4: Set Permissions

```bash
sudo chown -R qwamos:qwamos /opt/qwamos/security
sudo chown -R qwamos:qwamos /var/log/qwamos
sudo chown -R qwamos:qwamos /var/run/qwamos

sudo chmod 755 /opt/qwamos/security/quarantine
sudo chmod 700 /opt/qwamos/security/config
```

#### Step 5: Install Dependencies

```bash
sudo pip3 install --upgrade \
    tensorflow-lite \
    numpy \
    scapy \
    watchdog \
    asyncio
```

#### Step 6: Create Configuration Files

See [Configuration](#configuration) section below.

---

## Configuration

### AI Response Coordinator Config

**File**: `/opt/qwamos/security/config/ai_response_config.json`

```json
{
  "auto_response_severity": "MEDIUM",
  "require_permission_above": "HIGH",
  "ai_timeout": 60,
  "max_concurrent_responses": 5,
  "alert_channels": ["log", "ui"],
  "enable_auto_patching": false,
  "enable_network_isolation": true
}
```

**Parameters**:
- `auto_response_severity`: Minimum severity for automatic response (LOW, MEDIUM, HIGH, CRITICAL)
- `require_permission_above`: Severity requiring user permission
- `ai_timeout`: Timeout for AI queries (seconds)
- `max_concurrent_responses`: Maximum parallel threat responses
- `alert_channels`: Notification channels (`log`, `ui`, `email`)
- `enable_auto_patching`: Allow automatic security patching
- `enable_network_isolation`: Allow automatic network isolation

### Action Executor Config

**File**: `/opt/qwamos/security/config/action_executor_config.json`

```json
{
  "dry_run": false,
  "log_actions": true,
  "backup_before_action": true,
  "max_concurrent_actions": 10,
  "action_timeout": 300,
  "allowed_actions": [
    "firewall",
    "kill_process",
    "network_isolation",
    "vm_snapshot",
    "quarantine_file",
    "patch"
  ]
}
```

**Parameters**:
- `dry_run`: Test mode (no actual execution)
- `log_actions`: Log all actions to audit trail
- `backup_before_action`: Create backups before destructive actions
- `max_concurrent_actions`: Maximum parallel action execution
- `action_timeout`: Timeout for action execution (seconds)
- `allowed_actions`: Whitelist of permitted actions

### User Permissions

**File**: `/opt/qwamos/security/config/permissions.json`

```json
{
  "auto_isolate_vm": true,
  "auto_block_ip": true,
  "auto_kill_process": false,
  "auto_patch": false,
  "auto_snapshot": true
}
```

**Recommended Settings**:
- **Conservative**: All `false` (require manual approval)
- **Balanced**: `auto_isolate_vm: true`, `auto_block_ip: true`, rest `false`
- **Aggressive**: All `true` (full automation)

---

## Service Management

### Systemd Services

Four systemd services manage the ML threat detection system:

1. **qwamos-ml-network-anomaly.service** - Network Anomaly Detector
2. **qwamos-ml-file-system.service** - File System Monitor
3. **qwamos-ml-system-call.service** - System Call Analyzer
4. **qwamos-ai-response.service** - AI Response Coordinator

### Service Control

#### Check Status

```bash
# All services
sudo systemctl status qwamos-ml-*.service qwamos-ai-response.service

# Individual services
sudo systemctl status qwamos-ml-network-anomaly.service
sudo systemctl status qwamos-ml-file-system.service
sudo systemctl status qwamos-ml-system-call.service
sudo systemctl status qwamos-ai-response.service
```

#### Start Services

```bash
# Start all
sudo systemctl start qwamos-ai-response.service
sudo systemctl start qwamos-ml-network-anomaly.service
sudo systemctl start qwamos-ml-file-system.service
sudo systemctl start qwamos-ml-system-call.service

# Start individual
sudo systemctl start qwamos-ml-network-anomaly.service
```

#### Stop Services

```bash
# Stop all
sudo systemctl stop qwamos-ml-*.service qwamos-ai-response.service

# Stop individual
sudo systemctl stop qwamos-ml-network-anomaly.service
```

#### Restart Services

```bash
# Restart after configuration changes
sudo systemctl restart qwamos-ai-response.service
```

#### Enable/Disable Auto-Start

```bash
# Enable on boot
sudo systemctl enable qwamos-ml-network-anomaly.service
sudo systemctl enable qwamos-ml-file-system.service
sudo systemctl enable qwamos-ml-system-call.service
sudo systemctl enable qwamos-ai-response.service

# Disable on boot
sudo systemctl disable qwamos-ml-network-anomaly.service
```

### Viewing Logs

#### Real-Time Monitoring

```bash
# All ML services
sudo journalctl -f -u 'qwamos-ml-*' -u 'qwamos-ai-response'

# Individual service
sudo journalctl -f -u qwamos-ml-network-anomaly.service
```

#### Historical Logs

```bash
# Last 100 lines
sudo journalctl -u qwamos-ml-network-anomaly.service -n 100

# Last hour
sudo journalctl -u qwamos-ai-response.service --since "1 hour ago"

# Specific date range
sudo journalctl -u qwamos-ml-file-system.service --since "2024-01-15" --until "2024-01-16"
```

#### Filtering

```bash
# Show only errors
sudo journalctl -u qwamos-ml-network-anomaly.service -p err

# Search for keyword
sudo journalctl -u qwamos-ai-response.service | grep "CRITICAL"
```

---

## Testing

### Verify Installation

```bash
# Check all services are active
sudo systemctl is-active qwamos-ml-network-anomaly.service
sudo systemctl is-active qwamos-ml-file-system.service
sudo systemctl is-active qwamos-ml-system-call.service
sudo systemctl is-active qwamos-ai-response.service

# Check logs for errors
sudo journalctl -u 'qwamos-ml-*' -u 'qwamos-ai-response' --since "10 minutes ago" -p err
```

### Test Network Anomaly Detection

Simulate port scan (from trusted network only):

```bash
# Slow scan (should trigger detection)
nmap -sS -T2 localhost

# Monitor logs
sudo journalctl -f -u qwamos-ml-network-anomaly.service
```

Expected output:
```
[THREAT] Network Anomaly: Port scan detected
  Source IP: 127.0.0.1
  Anomaly Score: 0.23 (threshold: 0.15)
  Severity: MEDIUM
  Action: Logged
```

### Test File System Monitor

Simulate ransomware behavior:

```bash
# Create test directory
mkdir -p /tmp/qwamos_test
cd /tmp/qwamos_test

# Create and encrypt multiple files rapidly
for i in {1..100}; do
  echo "Test data" > file_$i.txt
  openssl enc -aes-256-cbc -salt -in file_$i.txt -out file_$i.txt.encrypted -k testkey
  rm file_$i.txt
done

# Monitor logs
sudo journalctl -f -u qwamos-ml-file-system.service
```

Expected output:
```
[THREAT] File System Anomaly: Ransomware detected
  Pattern: Mass encryption (100 files in 30s)
  Severity: CRITICAL
  Action: Auto-quarantine enabled
```

### Test System Call Analyzer

The system call analyzer monitors running processes automatically. To verify:

```bash
# Check for privilege escalation detection
sudo journalctl -u qwamos-ml-system-call.service | grep "PRIVILEGE"

# Monitor in real-time
sudo journalctl -f -u qwamos-ml-system-call.service
```

### Test AI Response Coordinator

Trigger a threat and verify AI response:

```bash
# Watch AI response logs
sudo journalctl -f -u qwamos-ai-response.service

# In another terminal, trigger a test threat
# (use one of the tests above)
```

Expected pipeline:
```
[INFO] Threat received: network_anomaly (MEDIUM)
[INFO] Step 1: Querying Kali GPT for technical analysis...
[INFO] Kali GPT response: Port scan detected, likely reconnaissance
[INFO] Step 2: Querying Claude via Tor for strategic response...
[INFO] Claude strategy: Isolate source, monitor for escalation
[INFO] Step 3: Querying ChatGPT via Tor for tactical commands...
[INFO] Action plan created: [firewall_block, log_alert]
[INFO] Executing actions...
[SUCCESS] Response complete
```

### React Native UI Testing

1. Open QWAMOS app on Android device
2. Navigate to **Security** → **Threat Detection**
3. Verify:
   - ✅ All detectors show green status
   - ✅ System health meter shows 100%
   - ✅ Threat list is empty (or shows test threats)
   - ✅ Detector toggle switches work
   - ✅ Threat details modal opens
   - ✅ Quick actions execute

---

## Troubleshooting

### Services Won't Start

**Issue**: Service fails to start with error

**Check**:
```bash
# Detailed status
sudo systemctl status qwamos-ml-network-anomaly.service -l

# Check for port conflicts
sudo netstat -tulpn | grep python3

# Verify Python dependencies
pip3 list | grep -E "tensorflow|scapy|watchdog"
```

**Common Fixes**:
1. Missing dependencies: `sudo pip3 install tensorflow-lite scapy watchdog`
2. Permission errors: `sudo chown -R qwamos:qwamos /opt/qwamos/security`
3. ML models missing: Models will be downloaded/trained (see ML Training Guide)

### ML Models Not Found

**Issue**: Detectors run in rule-based mode

**Check**:
```bash
ls -lh /opt/qwamos/security/ml/models/
```

**Solution**: Train or download models (see PHASE7_ML_TRAINING_GUIDE.md)

### Network Detector Requires Root

**Issue**: `PermissionError: Operation not permitted`

**Fix**: Grant CAP_NET_RAW capability
```bash
sudo setcap cap_net_raw=eip /usr/bin/python3
```

Or run as root (already configured in systemd service).

### AI Response Timeout

**Issue**: `AI query timeout after 60s`

**Causes**:
1. Tor circuit not established
2. External AI API rate limiting
3. Network connectivity issues

**Check**:
```bash
# Verify Tor is running
sudo systemctl status qwamos-tor.service

# Test Tor connectivity
curl --socks5-hostname localhost:9050 https://check.torproject.org
```

**Fix**:
```bash
# Restart Tor
sudo systemctl restart qwamos-tor.service

# Increase timeout in config
sudo nano /opt/qwamos/security/config/ai_response_config.json
# Change "ai_timeout": 60 to "ai_timeout": 120
```

### High CPU Usage

**Issue**: ML detectors consuming excessive CPU

**Check Resource Usage**:
```bash
sudo systemctl status qwamos-ml-network-anomaly.service | grep CPU
```

**Tune CPU Quotas**:
```bash
sudo systemctl edit qwamos-ml-network-anomaly.service
```

Add:
```ini
[Service]
CPUQuota=30%
```

Reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart qwamos-ml-network-anomaly.service
```

### False Positives

**Issue**: Too many false threat alerts

**Solutions**:

1. **Increase Detection Thresholds**:
```bash
# Network anomaly threshold
sudo nano /opt/qwamos/security/ml/network_anomaly_detector.py
# Change: self.anomaly_threshold = 0.15 to 0.20

# System call threshold
sudo nano /opt/qwamos/security/ml/system_call_analyzer.py
# Change: self.anomaly_threshold = 0.8 to 0.9
```

2. **Retrain Models**: Use more representative training data
3. **Whitelist Trusted IPs/Processes**: Add to configuration

---

## Security Considerations

### Threat Model

Phase 7 defends against:
- ✅ Network-based attacks (port scans, DDoS, C2 communications)
- ✅ Malware and ransomware
- ✅ Privilege escalation exploits
- ✅ Process injection and memory attacks
- ✅ Data exfiltration
- ✅ Zero-day vulnerabilities (via behavioral analysis)

**Not defended**:
- ❌ Physical access attacks (requires Phase 2 kernel hardening)
- ❌ Supply chain attacks (requires Phase 1 secure boot)
- ❌ Social engineering

### Isolation & Sandboxing

All services run with systemd security hardening:
- `NoNewPrivileges=true` - Prevents privilege escalation
- `ProtectSystem=strict` - Read-only system directories
- `ProtectHome=true` - No access to user home directories
- `PrivateTmp=true` - Isolated temporary directory
- Minimal capabilities (CAP_NET_RAW, CAP_SYS_PTRACE only when needed)

### Data Privacy

- **Local ML Inference**: All ML models run on-device (no cloud)
- **Tor Routing**: External AI queries route through Tor for anonymity
- **No Telemetry**: Zero data collection or phone-home
- **Encrypted Logs**: Option to encrypt `/var/log/qwamos/` (recommended)

### Audit Trail

All security actions are logged with:
- Timestamp (nanosecond precision)
- Threat details (type, severity, source)
- Action taken (firewall, quarantine, etc.)
- AI response (Kali GPT → Claude → ChatGPT pipeline)
- User approval (if required)

**View Audit Log**:
```bash
sudo journalctl -u 'qwamos-*' | grep ACTION
```

### Permission System

Three-tier permission model:

1. **Automatic** (LOW-MEDIUM severity):
   - Logging
   - Basic firewall rules
   - VM snapshots

2. **User Approval Required** (HIGH severity):
   - Process termination
   - Network isolation
   - File quarantine

3. **Admin Approval Required** (CRITICAL severity):
   - Auto-patching
   - System configuration changes

Configure in `/opt/qwamos/security/config/permissions.json`.

---

## Performance Tuning

### Resource Allocation

Default resource limits (per service):

| Service | Memory Limit | Memory High | CPU Quota |
|---------|-------------|-------------|-----------|
| Network Anomaly | 2GB | 1.5GB | 50% |
| File System | 1GB | 800MB | 30% |
| System Call | 1.5GB | 1.2GB | 40% |
| AI Response | 2GB | 1.5GB | 60% |

**Total Peak Usage**: ~6.5GB RAM, 180% CPU (1.8 cores)

### Optimization Strategies

#### Reduce Memory Usage

1. **Limit ML model batch size**:
```python
# In network_anomaly_detector.py
self.batch_size = 32  # Reduce from 64
```

2. **Decrease detection history**:
```python
# In file_system_monitor.py
self.max_history = 5000  # Reduce from 10000
```

#### Reduce CPU Usage

1. **Increase detection intervals**:
```python
# In network_anomaly_detector.py
self.detection_interval = 5.0  # Increase from 1.0 second
```

2. **Limit concurrent AI queries**:
```json
// In ai_response_config.json
"max_concurrent_responses": 3  // Reduce from 5
```

#### Optimize for Battery Life

```bash
# Run detectors only when charging
sudo systemctl edit qwamos-ml-network-anomaly.service
```

Add:
```ini
[Unit]
ConditionACPower=true
```

### Benchmarking

**Measure Detection Latency**:
```bash
# Network anomaly detection
sudo journalctl -u qwamos-ml-network-anomaly.service | grep "Detection time"

# Average over last hour
sudo journalctl -u qwamos-ml-network-anomaly.service --since "1 hour ago" | \
  grep "Detection time" | awk '{sum+=$NF; count++} END {print sum/count " ms"}'
```

**Expected Performance**:
- Network detection: 50-150ms per packet batch
- File system detection: 10-50ms per file event
- System call detection: 5-20ms per syscall sequence
- AI response (full pipeline): 30-90s per threat

---

## Next Steps

After successful deployment:

1. **Train ML Models**: See `PHASE7_ML_TRAINING_GUIDE.md`
2. **Configure Permissions**: Adjust auto-response settings
3. **Integrate with UI**: Test React Native dashboard
4. **Run Security Audit**: Verify all threat vectors
5. **Deploy to Production**: Enable on boot

---

## Support & Documentation

- **API Documentation**: `PHASE7_API_DOCUMENTATION.md`
- **ML Training Guide**: `PHASE7_ML_TRAINING_GUIDE.md`
- **GitHub Issues**: https://github.com/Dezirae-Stark/QWAMOS/issues
- **System Logs**: `/var/log/qwamos/`

---

**Phase 7 Complete** ✅

For Phase 8 (Advanced Hardening), see `PHASE8_SPECIFICATION.md`.
