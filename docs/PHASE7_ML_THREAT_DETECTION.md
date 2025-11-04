# QWAMOS Phase 7 - AI-Powered Threat Detection & Response

**Status:** PLANNING
**Priority:** HIGH
**Estimated Timeline:** 6-8 weeks
**Dependencies:** Phase 6 (AI Assistants) ✅ Complete

---

## Executive Summary

QWAMOS Phase 7 implements an intelligent, system-wide machine learning threat detection and automated response system. This system continuously monitors all VMs, network traffic, file operations, and system calls to detect anomalies, attacks, and vulnerabilities in real-time, then coordinates with Claude and ChatGPT to generate dynamic mitigation strategies and automated patches.

**Key Features:**
- Real-time ML-based threat detection across all VMs
- Automatic threat classification and severity assessment
- AI-powered response generation (Claude + ChatGPT)
- Automated patching via Claude Code integration
- User-controlled permission system
- Zero-day attack detection via behavioral analysis
- Continuous vulnerability monitoring

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         QWAMOS Host                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          ML Threat Detection Engine (TensorFlow Lite)    │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌────────────────┐   │  │
│  │  │ Network    │  │ File System  │  │ System Call    │   │  │
│  │  │ Anomaly    │  │ Monitor      │  │ Analyzer       │   │  │
│  │  │ Detector   │  │              │  │                │   │  │
│  │  └─────┬──────┘  └──────┬───────┘  └────────┬───────┘   │  │
│  │        │                │                   │           │  │
│  │        └────────────────┴───────────────────┘           │  │
│  │                         │                               │  │
│  │                  ┌──────▼───────┐                       │  │
│  │                  │  Threat      │                       │  │
│  │                  │  Classifier  │                       │  │
│  │                  │  (ML Model)  │                       │  │
│  │                  └──────┬───────┘                       │  │
│  └─────────────────────────┼──────────────────────────────┘  │
│                            │                                  │
│  ┌─────────────────────────▼──────────────────────────────┐  │
│  │         AI Response Coordinator                        │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │  │
│  │  │ Claude       │  │ ChatGPT      │  │ Kali GPT    │  │  │
│  │  │ (Strategy)   │  │ (Mitigation) │  │ (Analysis)  │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │  │
│  │         │                 │                  │         │  │
│  │         └─────────────────┴──────────────────┘         │  │
│  │                           │                            │  │
│  │                  ┌────────▼─────────┐                  │  │
│  │                  │ Action Executor  │                  │  │
│  │                  │ (with User Auth) │                  │  │
│  │                  └────────┬─────────┘                  │  │
│  └─────────────────────────┼────────────────────────────┘  │
│                            │                                  │
│  ┌─────────────────────────▼──────────────────────────────┐  │
│  │         Automated Response Actions                     │  │
│  │  • Firewall rule updates    • Process termination      │  │
│  │  • Network isolation        • VM snapshots             │  │
│  │  • Patch deployment         • Alert notifications      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  VMs: android-vm | workstation-1 | kali-1 | vault-vm    │  │
│  │         (All monitored by sensors)                       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ML Threat Detection Engine

### 1. Network Anomaly Detector

**Purpose:** Detect suspicious network traffic patterns in real-time

**ML Model:** Autoencoder-based anomaly detection
- **Training Data:** Normal traffic patterns from all VMs
- **Input Features:**
  - Packet size distribution
  - Protocol distribution (TCP/UDP/ICMP)
  - Connection frequency/duration
  - Port access patterns
  - DNS query patterns
  - Geographic destination distribution

**Detection Capabilities:**
- ✅ Port scanning (nmap, masscan)
- ✅ DDoS attacks
- ✅ C2 (Command & Control) communications
- ✅ Data exfiltration attempts
- ✅ Lateral movement between VMs
- ✅ DNS tunneling
- ✅ Unusual protocol usage

**Implementation:**
```python
# File: security/ml/network_anomaly_detector.py

import tensorflow as tf
import numpy as np
from scapy.all import sniff, IP, TCP, UDP

class NetworkAnomalyDetector:
    """
    Real-time network traffic anomaly detection using autoencoder
    """

    def __init__(self, model_path='/opt/qwamos/security/ml/models/network_ae.tflite'):
        # Load TensorFlow Lite model (optimized for ARM64)
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.feature_buffer = []
        self.anomaly_threshold = 0.15  # Reconstruction error threshold

    def extract_features(self, packet):
        """Extract features from network packet"""
        features = np.zeros(50)  # 50-dimensional feature vector

        if packet.haslayer(IP):
            # Basic IP features
            features[0] = len(packet)
            features[1] = packet[IP].proto
            features[2] = packet[IP].ttl

            # Port features
            if packet.haslayer(TCP):
                features[3] = packet[TCP].sport
                features[4] = packet[TCP].dport
                features[5] = packet[TCP].flags
            elif packet.haslayer(UDP):
                features[6] = packet[UDP].sport
                features[7] = packet[UDP].dport

            # Timing features (computed over window)
            features[8] = self._compute_packet_rate()
            features[9] = self._compute_connection_frequency()

            # Payload features
            features[10] = self._compute_payload_entropy(packet)

        return features

    def detect_anomaly(self, packet):
        """Detect if packet is anomalous"""
        features = self.extract_features(packet)

        # Normalize features
        features_norm = (features - self.mean) / self.std

        # Run inference
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        self.interpreter.set_tensor(input_details[0]['index'],
                                   features_norm.reshape(1, -1).astype(np.float32))
        self.interpreter.invoke()

        # Get reconstruction
        reconstruction = self.interpreter.get_tensor(output_details[0]['index'])

        # Calculate reconstruction error
        error = np.mean((features_norm - reconstruction) ** 2)

        if error > self.anomaly_threshold:
            return {
                'anomaly': True,
                'confidence': min(error / self.anomaly_threshold, 1.0),
                'error': error,
                'packet_info': self._extract_packet_info(packet),
                'features': features.tolist()
            }

        return {'anomaly': False}

    def monitor_interface(self, interface='any'):
        """Monitor network interface for anomalies"""
        def packet_handler(packet):
            result = self.detect_anomaly(packet)
            if result['anomaly']:
                self.alert_threat(result)

        sniff(iface=interface, prn=packet_handler, store=0)

    def alert_threat(self, detection):
        """Send alert to AI Response Coordinator"""
        from security.ai_response_coordinator import AIResponseCoordinator

        coordinator = AIResponseCoordinator()
        coordinator.handle_threat({
            'type': 'network_anomaly',
            'severity': self._calculate_severity(detection['confidence']),
            'details': detection,
            'timestamp': time.time()
        })
```

---

### 2. File System Monitor

**Purpose:** Detect suspicious file operations and malware

**ML Model:** Random Forest Classifier
- **Training Data:** Known malware behaviors + benign operations
- **Input Features:**
  - File access patterns
  - Permission changes
  - Rapid file creation/deletion
  - Encryption attempts (ransomware detection)
  - Executable file modifications
  - Registry/config file tampering

**Detection Capabilities:**
- ✅ Ransomware detection (file encryption patterns)
- ✅ Rootkit installation attempts
- ✅ Unauthorized file access
- ✅ Data theft (mass file copying)
- ✅ Configuration tampering
- ✅ Keylogger installation

**Implementation:**
```python
# File: security/ml/file_monitor.py

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tensorflow as tf
import numpy as np

class FileSystemMonitor(FileSystemEventHandler):
    """
    ML-based file system monitoring for threat detection
    """

    def __init__(self):
        self.model = tf.lite.Interpreter(
            model_path='/opt/qwamos/security/ml/models/file_classifier.tflite'
        )
        self.model.allocate_tensors()

        self.file_events = []
        self.window_size = 60  # 1-minute window

    def on_any_event(self, event):
        """Handle any file system event"""
        features = self.extract_features(event)

        # Add to event buffer
        self.file_events.append({
            'timestamp': time.time(),
            'event': event,
            'features': features
        })

        # Analyze window
        self.analyze_window()

    def extract_features(self, event):
        """Extract features from file event"""
        features = np.zeros(30)

        # Event type
        features[0] = 1 if event.event_type == 'created' else 0
        features[1] = 1 if event.event_type == 'deleted' else 0
        features[2] = 1 if event.event_type == 'modified' else 0
        features[3] = 1 if event.event_type == 'moved' else 0

        # File characteristics
        if os.path.exists(event.src_path):
            stat = os.stat(event.src_path)
            features[4] = stat.st_size
            features[5] = stat.st_mode
            features[6] = stat.st_mtime

            # File type indicators
            features[7] = 1 if event.src_path.endswith('.exe') else 0
            features[8] = 1 if event.src_path.endswith(('.so', '.dll')) else 0
            features[9] = 1 if event.src_path.startswith('/etc/') else 0
            features[10] = 1 if event.src_path.startswith('/root/') else 0

        # Temporal features (computed over window)
        features[11] = self._compute_event_rate()
        features[12] = self._compute_encryption_indicator()

        return features

    def analyze_window(self):
        """Analyze events in time window for threats"""
        # Remove old events
        current_time = time.time()
        self.file_events = [
            e for e in self.file_events
            if current_time - e['timestamp'] < self.window_size
        ]

        if len(self.file_events) < 10:
            return  # Not enough data

        # Aggregate features
        aggregated_features = self._aggregate_features()

        # Run ML classification
        threat_detected = self._classify_threat(aggregated_features)

        if threat_detected:
            self.alert_threat(threat_detected)

    def _detect_ransomware(self):
        """Specific ransomware detection logic"""
        # Check for rapid file encryption pattern
        recent_events = self.file_events[-100:]  # Last 100 events

        # Count file modifications
        modifications = sum(1 for e in recent_events
                          if e['event']['event_type'] == 'modified')

        # Check for suspicious extensions
        encrypted_pattern = sum(1 for e in recent_events
                               if e['event']['src_path'].endswith(('.encrypted', '.locked', '.crypt')))

        if modifications > 50 and encrypted_pattern > 10:
            return {
                'threat_type': 'ransomware',
                'confidence': 0.95,
                'affected_files': len(recent_events),
                'action': 'IMMEDIATE_ISOLATION'
            }

        return None
```

---

### 3. System Call Analyzer

**Purpose:** Detect malicious system behaviors

**ML Model:** LSTM (Long Short-Term Memory) for sequence analysis
- **Training Data:** Normal vs malicious syscall sequences
- **Input Features:**
  - System call sequences (open, read, write, exec, etc.)
  - Call frequency and timing
  - Process relationships
  - Privilege escalation attempts

**Detection Capabilities:**
- ✅ Privilege escalation
- ✅ Backdoor installation
- ✅ Process injection
- ✅ Code execution exploits
- ✅ Kernel exploits

---

## AI Response Coordinator

### Architecture

```python
# File: security/ai_response_coordinator.py

import asyncio
from typing import Dict, List
import sys
sys.path.insert(0, '/data/data/com.termux/files/home/QWAMOS/ai')

from ai_manager import AIManager
from security.action_executor import ActionExecutor

class AIResponseCoordinator:
    """
    Coordinates AI responses to detected threats
    """

    def __init__(self):
        self.ai_manager = AIManager()
        self.action_executor = ActionExecutor()
        self.pending_actions = []
        self.user_permissions = self._load_permissions()

    async def handle_threat(self, threat: Dict):
        """
        Main threat handling pipeline

        1. Classify and assess severity
        2. Query AI assistants for response strategy
        3. Generate mitigation actions
        4. Request user permission (if required)
        5. Execute actions
        6. Monitor and adjust
        """

        print(f"[THREAT DETECTED] {threat['type']} - Severity: {threat['severity']}")

        # Step 1: Get immediate analysis from Kali GPT
        kali_analysis = await self._analyze_with_kali_gpt(threat)

        # Step 2: Get strategic response from Claude
        claude_strategy = await self._get_claude_strategy(threat, kali_analysis)

        # Step 3: Get tactical mitigation from ChatGPT
        chatgpt_mitigation = await self._get_chatgpt_mitigation(threat, claude_strategy)

        # Step 4: Combine responses into action plan
        action_plan = self._create_action_plan(
            threat, kali_analysis, claude_strategy, chatgpt_mitigation
        )

        # Step 5: Check user permissions
        if self._requires_user_permission(action_plan):
            permission_granted = await self._request_user_permission(action_plan)
            if not permission_granted:
                print("[ACTION DENIED] User denied permission")
                return

        # Step 6: Execute actions
        await self._execute_action_plan(action_plan)

        # Step 7: Monitor results
        await self._monitor_and_adjust(action_plan)

    async def _analyze_with_kali_gpt(self, threat: Dict) -> Dict:
        """Get technical analysis from Kali GPT"""
        prompt = f"""
        Analyze this security threat:

        Type: {threat['type']}
        Severity: {threat['severity']}
        Details: {threat['details']}

        Provide:
        1. Attack classification
        2. Likely attack vector
        3. Potential impact
        4. Immediate containment steps
        """

        response = self.ai_manager.query('kali-gpt', prompt)

        return {
            'analysis': response,
            'timestamp': time.time()
        }

    async def _get_claude_strategy(self, threat: Dict, analysis: Dict) -> Dict:
        """Get strategic response from Claude"""
        prompt = f"""
        Based on this threat analysis, develop a comprehensive response strategy:

        Threat: {threat['type']}
        Analysis: {analysis['analysis']}

        Consider:
        1. Short-term containment
        2. Long-term prevention
        3. System hardening recommendations
        4. Patch requirements

        Provide a detailed, actionable strategy.
        """

        response = self.ai_manager.query('claude', prompt)

        return {
            'strategy': response,
            'timestamp': time.time()
        }

    async def _get_chatgpt_mitigation(self, threat: Dict, strategy: Dict) -> Dict:
        """Get tactical mitigation steps from ChatGPT"""
        prompt = f"""
        Generate specific mitigation commands for this threat:

        Strategy: {strategy['strategy']}

        Provide:
        1. Firewall rules to add
        2. Processes to terminate
        3. Network isolation commands
        4. VM snapshot commands
        5. Log collection commands

        Format as executable shell commands.
        """

        response = self.ai_manager.query('chatgpt', prompt)

        return {
            'mitigation_steps': self._parse_commands(response),
            'timestamp': time.time()
        }

    def _create_action_plan(self, threat, analysis, strategy, mitigation) -> Dict:
        """Create consolidated action plan"""
        return {
            'threat_id': self._generate_threat_id(),
            'severity': threat['severity'],
            'immediate_actions': self._extract_immediate_actions(mitigation),
            'long_term_actions': self._extract_long_term_actions(strategy),
            'requires_user_permission': threat['severity'] in ['CRITICAL', 'HIGH'],
            'estimated_impact': self._estimate_impact(mitigation),
            'rollback_plan': self._create_rollback_plan(mitigation)
        }

    async def _request_user_permission(self, action_plan: Dict) -> bool:
        """Request user permission via UI notification"""
        # Send to React Native UI
        notification = {
            'type': 'THREAT_RESPONSE_PERMISSION',
            'title': 'Security Threat Detected',
            'message': f"QWAMOS detected a {action_plan['severity']} threat and wants to take action.",
            'actions': action_plan['immediate_actions'],
            'timeout': 60  # 60-second timeout
        }

        # Wait for user response
        response = await self.action_executor.request_user_permission(notification)

        return response['granted']

    async def _execute_action_plan(self, action_plan: Dict):
        """Execute the action plan"""
        for action in action_plan['immediate_actions']:
            try:
                result = await self.action_executor.execute(action)
                print(f"[ACTION] {action['description']}: {result['status']}")
            except Exception as e:
                print(f"[ERROR] Action failed: {e}")
                # Attempt rollback
                await self._rollback(action_plan)
                return

        # Schedule long-term actions
        for action in action_plan['long_term_actions']:
            self.action_executor.schedule(action)
```

---

## Automated Patching System

### Integration with Claude Code

```python
# File: security/auto_patcher.py

import subprocess
import json
from typing import List, Dict

class AutoPatcher:
    """
    Automated vulnerability patching using Claude Code
    """

    def __init__(self):
        self.claude_code_path = '/usr/bin/claude'  # or wherever Claude Code is installed
        self.patch_queue = []

    async def detect_vulnerabilities(self):
        """Continuously monitor for vulnerabilities"""
        while True:
            # Check for package updates
            outdated_packages = self._check_package_updates()

            # Check CVE databases
            cve_matches = self._check_cve_database()

            # Check system configs
            config_issues = self._check_configurations()

            # Consolidate findings
            vulnerabilities = outdated_packages + cve_matches + config_issues

            if vulnerabilities:
                await self._process_vulnerabilities(vulnerabilities)

            await asyncio.sleep(3600)  # Check every hour

    async def _process_vulnerabilities(self, vulnerabilities: List[Dict]):
        """Process detected vulnerabilities"""
        for vuln in vulnerabilities:
            # Ask Claude for fix strategy
            fix_strategy = await self._get_fix_strategy(vuln)

            # Request user permission
            if await self._request_patch_permission(vuln, fix_strategy):
                # Apply patch using Claude Code
                await self._apply_patch_with_claude_code(vuln, fix_strategy)

    async def _apply_patch_with_claude_code(self, vuln: Dict, strategy: Dict):
        """Use Claude Code to automatically patch vulnerability"""

        # Create a task file for Claude Code
        task_file = f"/tmp/qwamos_patch_{vuln['id']}.md"

        with open(task_file, 'w') as f:
            f.write(f"""
# QWAMOS Security Patch Task

## Vulnerability
- ID: {vuln['id']}
- Severity: {vuln['severity']}
- Affected: {vuln['affected']}
- CVE: {vuln.get('cve', 'N/A')}

## Fix Strategy
{strategy['strategy']}

## Required Actions
{strategy['actions']}

## Testing
{strategy['testing']}

## Rollback Plan
{strategy['rollback']}

Please implement this security patch following the strategy above.
Test thoroughly and provide confirmation when complete.
            """)

        # Execute Claude Code in background
        process = subprocess.Popen([
            self.claude_code_path,
            'code',
            '--task', task_file,
            '--auto-approve',  # Auto-approve low-risk changes
            '--test-after',
            '--notify-on-complete'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Monitor progress
        await self._monitor_claude_code_progress(process, vuln)
```

---

## User Permission System

### Permission Levels

```python
# File: security/permission_manager.py

class PermissionManager:
    """
    Manage user permissions for automated security actions
    """

    PERMISSION_LEVELS = {
        'AUTOMATIC': {
            'description': 'Fully automatic responses (user notified after)',
            'allowed_severities': ['LOW', 'MEDIUM'],
            'allowed_actions': [
                'firewall_rule_add',
                'process_terminate_non_critical',
                'log_collection',
                'snapshot_create'
            ]
        },
        'SEMI_AUTOMATIC': {
            'description': 'Automatic for low/medium, ask for high/critical',
            'allowed_severities': ['LOW', 'MEDIUM'],
            'requires_approval': ['HIGH', 'CRITICAL'],
            'timeout_seconds': 60  # Auto-deny after 60s
        },
        'MANUAL': {
            'description': 'Always ask user permission',
            'allowed_severities': [],
            'requires_approval': ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        }
    }

    def __init__(self):
        self.current_level = self._load_user_preference()

    def check_permission(self, action: Dict) -> bool:
        """Check if action is allowed under current permission level"""
        level_config = self.PERMISSION_LEVELS[self.current_level]

        if action['severity'] in level_config.get('allowed_severities', []):
            if action['type'] in level_config.get('allowed_actions', []):
                return True

        # Requires user approval
        if action['severity'] in level_config.get('requires_approval', []):
            return self._request_user_approval(action)

        return False
```

---

## React Native UI Components

### Threat Dashboard

```typescript
// File: ui/screens/ThreatDashboard.tsx

import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';

interface Threat {
  id: string;
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  timestamp: number;
  status: 'DETECTED' | 'ANALYZING' | 'MITIGATING' | 'RESOLVED';
  description: string;
}

const ThreatDashboard: React.FC = () => {
  const [threats, setThreats] = useState<Threat[]>([]);
  const [systemStatus, setSystemStatus] = useState('MONITORING');

  useEffect(() => {
    // Subscribe to threat feed
    const ws = new WebSocket('ws://localhost:8080/threats');

    ws.onmessage = (event) => {
      const threat = JSON.parse(event.data);
      setThreats(prev => [threat, ...prev].slice(0, 50));
    };

    return () => ws.close();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>🛡️ QWAMOS Threat Detection</Text>

      <View style={styles.statusCard}>
        <Text style={styles.statusLabel}>System Status:</Text>
        <Text style={styles.statusValue}>{systemStatus}</Text>
      </View>

      <ScrollView style={styles.threatList}>
        {threats.map(threat => (
          <ThreatCard key={threat.id} threat={threat} />
        ))}
      </ScrollView>
    </View>
  );
};
```

---

## Implementation Timeline

### Week 1-2: ML Model Development
- Day 1-3: Collect training data (normal + malicious)
- Day 4-7: Train network anomaly detector
- Day 8-10: Train file system monitor
- Day 11-14: Train syscall analyzer

### Week 3-4: Integration
- Day 15-17: Implement AI Response Coordinator
- Day 18-21: Integrate with Claude/ChatGPT
- Day 22-25: Build permission system
- Day 26-28: React Native UI

### Week 5-6: Automated Patching
- Day 29-33: Claude Code integration
- Day 34-38: Vulnerability scanner
- Day 39-42: Testing framework

### Week 7-8: Testing & Deployment
- Day 43-49: Comprehensive testing
- Day 50-56: Production deployment

---

## Performance Requirements

**ML Inference:**
- Network anomaly detection: <10ms per packet
- File operation analysis: <5ms per event
- Syscall analysis: <1ms per syscall

**Resource Usage:**
- ML models total size: <100MB
- RAM usage: <500MB
- CPU usage: <10% baseline

**Response Time:**
- Threat detection: Real-time (<100ms)
- AI analysis: <5 seconds
- Mitigation execution: <30 seconds

---

## Next Steps

1. Create `security/ml/` directory structure
2. Download TensorFlow Lite for ARM64
3. Collect training data for ML models
4. Implement NetworkAnomalyDetector
5. Build AI Response Coordinator
6. Create React Native threat dashboard

**Status:** Specification complete, ready for implementation
**Priority:** HIGH - Critical security feature
**Dependencies:** Phase 6 AI Assistants (60% complete)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-04
**Author:** QWAMOS Development Team
