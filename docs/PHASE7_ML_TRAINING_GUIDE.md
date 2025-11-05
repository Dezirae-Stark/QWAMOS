# QWAMOS Phase 7: ML Model Training Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Data Collection](#data-collection)
4. [Model 1: Network Anomaly Autoencoder](#model-1-network-anomaly-autoencoder)
5. [Model 2: File System Random Forest](#model-2-file-system-random-forest)
6. [Model 3: System Call LSTM](#model-3-system-call-lstm)
7. [Model Evaluation](#model-evaluation)
8. [Deployment](#deployment)
9. [Continuous Learning](#continuous-learning)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Phase 7 uses three machine learning models for threat detection:

| Model | Type | Purpose | Training Data | Accuracy Target |
|-------|------|---------|---------------|-----------------|
| Network Anomaly | Autoencoder | Detect abnormal traffic patterns | Network packet captures | 95%+ TPR, <5% FPR |
| File System | Random Forest | Detect malware/ransomware | File system events | 98%+ TPR, <2% FPR |
| System Call | LSTM | Detect exploits via syscall sequences | System call traces | 96%+ TPR, <3% FPR |

**TPR**: True Positive Rate (sensitivity)
**FPR**: False Positive Rate

All models are converted to TensorFlow Lite (.tflite) for efficient ARM64 inference.

---

## Prerequisites

### Hardware Requirements

**For Training** (can be done on development machine):
- CPU: x86_64 or ARM64 (GPU optional but recommended)
- RAM: 16GB+ recommended
- Storage: 50GB+ for datasets
- GPU: NVIDIA CUDA-compatible (optional, speeds up training 10x)

**For Deployment** (QWAMOS device):
- CPU: ARMv8-A 64-bit
- RAM: 4GB+
- Storage: 2GB+ for models

### Software Requirements

```bash
# Python packages for training
pip3 install --upgrade \
    tensorflow \
    tensorflow-lite \
    scikit-learn \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    scapy \
    tqdm
```

### Dataset Sources

**Public Datasets**:
- **Network Traffic**:
  - [CICIDS2017](https://www.unb.ca/cic/datasets/ids-2017.html) - Intrusion detection dataset
  - [KDD Cup 99](http://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html) - Network intrusion data
  - [UNSW-NB15](https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity/ADFA-NB15-Datasets/) - Modern network attacks

- **File System**:
  - [VirusShare](https://virusshare.com/) - Malware samples (requires registration)
  - [Endgame Malware BEnchmark](https://github.com/endgameinc/ember) - Malware ML dataset
  - Custom ransomware simulation (see below)

- **System Calls**:
  - [ADFA-LD](https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity/ADFA-IDS-Datasets/) - Linux syscall intrusion detection
  - [LID-DS](https://www.hs-coburg.de/index.php?id=12405) - Linux Intrusion Detection System dataset
  - Custom syscall tracing (see below)

---

## Data Collection

### Option 1: Use Pre-Collected Datasets (Recommended)

Download and extract public datasets:

```bash
# Create datasets directory
mkdir -p /opt/qwamos/security/ml/data/{network,filesystem,syscall}

# Download CICIDS2017 (example)
cd /opt/qwamos/security/ml/data/network
wget https://www.unb.ca/cic/datasets/ids-2017.html
# Follow download instructions from website

# Download EMBER malware dataset
cd /opt/qwamos/security/ml/data/filesystem
git clone https://github.com/endgameinc/ember.git
```

### Option 2: Collect Custom Data

#### Network Traffic Collection

Capture normal and attack traffic:

```python
#!/usr/bin/env python3
# collect_network_data.py

from scapy.all import sniff, wrpcap
import sys

def collect_normal_traffic(duration=3600):
    """Collect 1 hour of normal traffic"""
    print(f"Collecting normal traffic for {duration}s...")
    packets = sniff(timeout=duration, filter="ip")
    wrpcap("/opt/qwamos/security/ml/data/network/normal_traffic.pcap", packets)
    print(f"Saved {len(packets)} packets")

def collect_attack_traffic():
    """Collect attack traffic (requires controlled environment)"""
    print("Run attacks in isolated VM, then capture traffic...")
    # Example attacks to simulate:
    # - nmap -sS target  (port scan)
    # - hping3 -S --flood target  (SYN flood)
    # - nc -l -p 4444  (reverse shell)
    packets = sniff(timeout=300, filter="ip")
    wrpcap("/opt/qwamos/security/ml/data/network/attack_traffic.pcap", packets)

if __name__ == "__main__":
    collect_normal_traffic(duration=3600)
    # collect_attack_traffic()  # Only in isolated test environment
```

**WARNING**: Only collect attack traffic in isolated, controlled environments (VMs with no internet access).

#### File System Event Collection

```python
#!/usr/bin/env python3
# collect_filesystem_data.py

import os
import json
import hashlib
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DataCollector(FileSystemEventHandler):
    def __init__(self, output_file):
        self.output_file = output_file
        self.events = []

    def on_any_event(self, event):
        data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event.event_type,
            'src_path': event.src_path,
            'is_directory': event.is_directory
        }

        # Add file metadata
        if not event.is_directory and os.path.exists(event.src_path):
            try:
                stat = os.stat(event.src_path)
                data['size'] = stat.st_size
                data['mtime'] = stat.st_mtime
                data['permissions'] = oct(stat.st_mode)[-3:]

                # File hash (first 1KB for speed)
                with open(event.src_path, 'rb') as f:
                    data['hash'] = hashlib.md5(f.read(1024)).hexdigest()
            except:
                pass

        self.events.append(data)

        # Save every 100 events
        if len(self.events) >= 100:
            self.save()

    def save(self):
        with open(self.output_file, 'a') as f:
            for event in self.events:
                f.write(json.dumps(event) + '\n')
        self.events = []

# Usage
if __name__ == "__main__":
    collector = DataCollector("/opt/qwamos/security/ml/data/filesystem/events.jsonl")
    observer = Observer()
    observer.schedule(collector, path="/home", recursive=True)
    observer.start()

    print("Collecting file system events... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        observer.stop()
        collector.save()
    observer.join()
```

#### System Call Collection

```bash
#!/bin/bash
# collect_syscall_data.sh

OUTPUT_DIR="/opt/qwamos/security/ml/data/syscall"
mkdir -p $OUTPUT_DIR

# Collect normal syscalls from common processes
echo "Collecting normal syscalls..."
for process in "bash" "python3" "npm" "gcc"; do
    echo "Tracing $process..."
    strace -f -e trace=all -o "$OUTPUT_DIR/normal_${process}.strace" \
        $process -c "sleep 10" 2>/dev/null &
done

wait

# For attack syscalls, run in isolated VM:
# - Privilege escalation exploits
# - Process injection tools
# - Reverse shell payloads

echo "Data collection complete!"
echo "Files saved to: $OUTPUT_DIR"
```

**Label your data**:
```bash
# Create labels.csv
cat > /opt/qwamos/security/ml/data/syscall/labels.csv <<EOF
filename,label
normal_bash.strace,0
normal_python3.strace,0
normal_npm.strace,0
attack_privesc.strace,1
attack_injection.strace,1
EOF
```

---

## Model 1: Network Anomaly Autoencoder

### Architecture

```
Input Layer (50 features)
    ↓
Encoder: Dense(32, relu) → Dropout(0.2) → Dense(16, relu)
    ↓
Bottleneck (16 features)
    ↓
Decoder: Dense(32, relu) → Dropout(0.2) → Dense(50, sigmoid)
    ↓
Output Layer (50 features - reconstruction)
```

### Training Script

```python
#!/usr/bin/env python3
# train_network_autoencoder.py

import numpy as np
import tensorflow as tf
from tensorflow import keras
from scapy.all import rdpcap
from sklearn.preprocessing import StandardScaler
import pickle

# Feature extraction (same as network_anomaly_detector.py)
def extract_features(packet):
    features = np.zeros(50, dtype=np.float32)

    # Basic packet info
    features[0] = len(packet)
    features[1] = packet.time if hasattr(packet, 'time') else 0

    # Protocol (one-hot encoding)
    if packet.haslayer('TCP'):
        features[2] = 1
        features[10:18] = [
            packet['TCP'].sport / 65535,
            packet['TCP'].dport / 65535,
            packet['TCP'].flags,
            packet['TCP'].seq if packet['TCP'].seq else 0,
            packet['TCP'].ack if packet['TCP'].ack else 0,
            packet['TCP'].window / 65535,
            0, 0
        ]
    elif packet.haslayer('UDP'):
        features[3] = 1
        features[10] = packet['UDP'].sport / 65535
        features[11] = packet['UDP'].dport / 65535
    elif packet.haslayer('ICMP'):
        features[4] = 1

    # IP layer
    if packet.haslayer('IP'):
        features[5] = packet['IP'].ttl / 255
        features[6] = packet['IP'].len / 65535

    # Payload analysis
    if hasattr(packet, 'payload'):
        payload = bytes(packet.payload)
        features[20] = len(payload) / 65535

        # Entropy
        if len(payload) > 0:
            prob = [payload.count(i) / len(payload) for i in range(256) if payload.count(i) > 0]
            features[21] = -sum([p * np.log2(p) for p in prob if p > 0])

    return features

# Load dataset
print("Loading network traffic data...")
normal_packets = rdpcap("/opt/qwamos/security/ml/data/network/normal_traffic.pcap")

print(f"Extracting features from {len(normal_packets)} packets...")
X_train = np.array([extract_features(pkt) for pkt in normal_packets])

# Normalize
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Save scaler for deployment
with open('/opt/qwamos/security/ml/models/network_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

# Build autoencoder
print("Building autoencoder model...")
input_dim = 50
encoding_dim = 16

encoder_input = keras.Input(shape=(input_dim,))
encoded = keras.layers.Dense(32, activation='relu')(encoder_input)
encoded = keras.layers.Dropout(0.2)(encoded)
encoded = keras.layers.Dense(encoding_dim, activation='relu')(encoded)

decoded = keras.layers.Dense(32, activation='relu')(encoded)
decoded = keras.layers.Dropout(0.2)(decoded)
decoded = keras.layers.Dense(input_dim, activation='sigmoid')(decoded)

autoencoder = keras.Model(encoder_input, decoded)
autoencoder.compile(optimizer='adam', loss='mse', metrics=['mae'])

print(autoencoder.summary())

# Train
print("Training autoencoder...")
history = autoencoder.fit(
    X_train_scaled, X_train_scaled,
    epochs=100,
    batch_size=256,
    shuffle=True,
    validation_split=0.2,
    callbacks=[
        keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=5)
    ]
)

# Convert to TensorFlow Lite
print("Converting to TensorFlow Lite...")
converter = tf.lite.TFLiteConverter.from_keras_model(autoencoder)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save
output_path = '/opt/qwamos/security/ml/models/network_ae.tflite'
with open(output_path, 'wb') as f:
    f.write(tflite_model)

print(f"Model saved to: {output_path}")
print(f"Model size: {len(tflite_model) / 1024:.2f} KB")

# Calculate anomaly threshold (95th percentile of reconstruction error)
predictions = autoencoder.predict(X_train_scaled)
mse = np.mean(np.square(X_train_scaled - predictions), axis=1)
threshold = np.percentile(mse, 95)
print(f"Recommended anomaly threshold: {threshold:.4f}")

# Save threshold
with open('/opt/qwamos/security/ml/models/network_threshold.txt', 'w') as f:
    f.write(str(threshold))
```

### Running Training

```bash
cd /opt/qwamos/security/ml/training
python3 train_network_autoencoder.py
```

**Expected Output**:
```
Loading network traffic data...
Extracting features from 125000 packets...
Building autoencoder model...
Training autoencoder...
Epoch 100/100
├─ loss: 0.0215
├─ mae: 0.1123
├─ val_loss: 0.0231
└─ val_mae: 0.1187
Converting to TensorFlow Lite...
Model saved to: /opt/qwamos/security/ml/models/network_ae.tflite
Model size: 142.37 KB
Recommended anomaly threshold: 0.1523
```

---

## Model 2: File System Random Forest

### Architecture

- **Algorithm**: Random Forest Classifier
- **Trees**: 100 estimators
- **Max Depth**: 10
- **Features**: 30 (file attributes, modification patterns)
- **Classes**: 3 (benign, malware, ransomware)

### Training Script

```python
#!/usr/bin/env python3
# train_file_classifier.py

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import tensorflow as tf
import pickle

# Feature extraction (same as file_system_monitor.py)
def extract_file_features(file_path, event_type):
    import os
    import hashlib

    features = np.zeros(30, dtype=np.float32)

    try:
        stat = os.stat(file_path)

        # File attributes
        features[0] = stat.st_size / 1e9  # Size (normalized to GB)
        features[1] = stat.st_mtime  # Modification time
        features[2] = stat.st_atime  # Access time
        features[3] = stat.st_ctime  # Creation time
        features[4] = int(oct(stat.st_mode)[-3:]) / 777  # Permissions

        # File extension
        ext = os.path.splitext(file_path)[1].lower()
        ext_map = {'.exe': 1, '.dll': 2, '.so': 3, '.py': 4, '.sh': 5, '.encrypted': 6}
        features[5] = ext_map.get(ext, 0) / 6

        # Event type (created, modified, deleted)
        event_map = {'created': 0, 'modified': 1, 'deleted': 2}
        features[6] = event_map.get(event_type, 0) / 2

        # File hash entropy (first 1KB)
        if os.path.exists(file_path) and stat.st_size > 0:
            with open(file_path, 'rb') as f:
                data = f.read(min(1024, stat.st_size))
                features[7] = len(set(data)) / 256  # Unique byte ratio

                # Calculate entropy
                if len(data) > 0:
                    prob = [data.count(i) / len(data) for i in set(data)]
                    features[8] = -sum([p * np.log2(p) for p in prob if p > 0]) / 8

        # Temporal features (calculated separately)
        # features[10:20] = modification_rate, creation_rate, etc.

    except:
        pass

    return features

# Load dataset
print("Loading file system event data...")
df = pd.read_json("/opt/qwamos/security/ml/data/filesystem/events.jsonl", lines=True)

# Load labels (you need to manually label data or use pre-labeled datasets)
labels_df = pd.read_csv("/opt/qwamos/security/ml/data/filesystem/labels.csv")
df = df.merge(labels_df, on='src_path', how='inner')

print(f"Loaded {len(df)} labeled events")
print(f"Class distribution:\n{df['label'].value_counts()}")

# Extract features
print("Extracting features...")
X = np.array([extract_file_features(row['src_path'], row['event_type'])
              for _, row in df.iterrows()])
y = df['label'].values

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train Random Forest
print("Training Random Forest classifier...")
rf = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)

# Evaluate
print("Evaluating model...")
y_pred = rf.predict(X_test)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['benign', 'malware', 'ransomware']))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Feature importance
feature_names = ['size', 'mtime', 'atime', 'ctime', 'perms', 'ext', 'event', 'unique_bytes', 'entropy']
importances = rf.feature_importances_[:len(feature_names)]
print("\nTop 5 Most Important Features:")
for name, imp in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {name}: {imp:.4f}")

# Convert to TensorFlow Lite (via tf.keras wrapper)
print("Converting to TensorFlow Lite...")

# Create Keras equivalent
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Input(shape=(30,)),
    keras.layers.Dense(100, activation='relu'),
    keras.layers.Dense(50, activation='relu'),
    keras.layers.Dense(3, activation='softmax')
])

# Train Keras model to mimic Random Forest
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=0)

# Convert
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save
output_path = '/opt/qwamos/security/ml/models/file_classifier.tflite'
with open(output_path, 'wb') as f:
    f.write(tflite_model)

print(f"Model saved to: {output_path}")
print(f"Model size: {len(tflite_model) / 1024:.2f} KB")

# Save Random Forest for comparison
with open('/opt/qwamos/security/ml/models/file_rf.pkl', 'wb') as f:
    pickle.dump(rf, f)
```

### Running Training

```bash
cd /opt/qwamos/security/ml/training
python3 train_file_classifier.py
```

---

## Model 3: System Call LSTM

### Architecture

```
Input Layer (sequence of 128 syscalls, one-hot encoded)
    ↓
Embedding Layer (128 syscalls → 64 dimensions)
    ↓
LSTM Layer (64 units, return_sequences=True)
    ↓
LSTM Layer (32 units)
    ↓
Dense Layer (16 units, relu)
    ↓
Output Layer (1 unit, sigmoid) - Anomaly score
```

### Training Script

```python
#!/usr/bin/env python3
# train_syscall_lstm.py

import numpy as np
import re
from tensorflow import keras
import tensorflow as tf
from sklearn.model_selection import train_test_split

# System call mapping (same as system_call_analyzer.py)
SYSCALL_MAP = {
    'read': 0, 'write': 1, 'open': 2, 'close': 3, 'stat': 4,
    'fstat': 5, 'lstat': 6, 'poll': 7, 'lseek': 8, 'mmap': 9,
    'mprotect': 10, 'munmap': 11, 'brk': 12, 'rt_sigaction': 13,
    'rt_sigprocmask': 14, 'rt_sigreturn': 15, 'ioctl': 16, 'pread64': 17,
    'pwrite64': 18, 'readv': 19, 'writev': 20, 'access': 21,
    'pipe': 22, 'select': 23, 'sched_yield': 24, 'mremap': 25,
    'msync': 26, 'mincore': 27, 'madvise': 28, 'shmget': 29,
    'shmat': 30, 'shmctl': 31, 'dup': 32, 'dup2': 33,
    'pause': 34, 'nanosleep': 35, 'getitimer': 36, 'alarm': 37,
    'setitimer': 38, 'getpid': 39, 'sendfile': 40, 'socket': 41,
    'connect': 42, 'accept': 43, 'sendto': 44, 'recvfrom': 45,
    'sendmsg': 46, 'recvmsg': 47, 'shutdown': 48, 'bind': 49,
    'listen': 50, 'getsockname': 51, 'getpeername': 52, 'socketpair': 53,
    'setsockopt': 54, 'getsockopt': 55, 'clone': 56, 'fork': 57,
    'vfork': 58, 'execve': 59, 'exit': 60, 'wait4': 61,
    'kill': 62, 'uname': 63, 'semget': 64, 'semop': 65,
    'semctl': 66, 'shmdt': 67, 'msgget': 68, 'msgsnd': 69,
    'msgrcv': 70, 'msgctl': 71, 'fcntl': 72, 'flock': 73,
    'fsync': 74, 'fdatasync': 75, 'truncate': 76, 'ftruncate': 77,
    'getdents': 78, 'getcwd': 79, 'chdir': 80, 'fchdir': 81,
    'rename': 82, 'mkdir': 83, 'rmdir': 84, 'creat': 85,
    'link': 86, 'unlink': 87, 'symlink': 88, 'readlink': 89,
    'chmod': 90, 'fchmod': 91, 'chown': 92, 'fchown': 93,
    'lchown': 94, 'umask': 95, 'gettimeofday': 96, 'getrlimit': 97,
    'getrusage': 98, 'sysinfo': 99, 'ptrace': 100, 'getuid': 101,
    'syslog': 102, 'getgid': 103, 'setuid': 104, 'setgid': 105,
    'geteuid': 106, 'getegid': 107, 'setpgid': 108, 'getppid': 109,
    'getpgrp': 110, 'setsid': 111, 'setreuid': 112, 'setregid': 113,
    'getgroups': 114, 'setgroups': 115, 'setresuid': 116, 'getresuid': 117,
    'setresgid': 118, 'getresgid': 119, 'getpgid': 120, 'setfsuid': 121,
    'setfsgid': 122, 'getsid': 123, 'capget': 124, 'capset': 125,
    'prctl': 126, 'unknown': 127
}

def parse_strace_file(file_path):
    """Parse strace output into syscall sequence"""
    syscalls = []

    with open(file_path, 'r') as f:
        for line in f:
            # Parse: "12345 read(3, ..." -> "read"
            match = re.match(r'^\d+\s+(\w+)\(', line)
            if match:
                syscall = match.group(1)
                syscalls.append(SYSCALL_MAP.get(syscall, SYSCALL_MAP['unknown']))

    return syscalls

def create_sequences(syscalls, seq_length=128):
    """Create overlapping sequences"""
    sequences = []
    for i in range(0, len(syscalls) - seq_length, seq_length // 2):  # 50% overlap
        sequences.append(syscalls[i:i+seq_length])
    return sequences

# Load training data
print("Loading syscall traces...")
import os
import glob

data_dir = "/opt/qwamos/security/ml/data/syscall"

normal_files = glob.glob(f"{data_dir}/normal_*.strace")
attack_files = glob.glob(f"{data_dir}/attack_*.strace")

print(f"Found {len(normal_files)} normal traces, {len(attack_files)} attack traces")

# Parse files
X_normal = []
for file in normal_files:
    syscalls = parse_strace_file(file)
    X_normal.extend(create_sequences(syscalls))

X_attack = []
for file in attack_files:
    syscalls = parse_strace_file(file)
    X_attack.extend(create_sequences(syscalls))

# Create labels
y_normal = np.zeros(len(X_normal))
y_attack = np.ones(len(X_attack))

# Combine
X = np.array(X_normal + X_attack)
y = np.concatenate([y_normal, y_attack])

print(f"Total sequences: {len(X)} (normal: {len(X_normal)}, attack: {len(X_attack)})")

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Build LSTM model
print("Building LSTM model...")
model = keras.Sequential([
    keras.layers.Embedding(input_dim=128, output_dim=64, input_length=128),
    keras.layers.LSTM(64, return_sequences=True),
    keras.layers.LSTM(32),
    keras.layers.Dense(16, activation='relu'),
    keras.layers.Dropout(0.3),
    keras.layers.Dense(1, activation='sigmoid')
])

model.compile(
    optimizer='adam',
    loss='binary_crossentropy',
    metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
)

print(model.summary())

# Train
print("Training LSTM...")
history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_split=0.2,
    callbacks=[
        keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3)
    ]
)

# Evaluate
print("Evaluating model...")
loss, accuracy, precision, recall = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy:.4f}")
print(f"Test Precision: {precision:.4f}")
print(f"Test Recall: {recall:.4f}")
print(f"F1 Score: {2 * precision * recall / (precision + recall):.4f}")

# Convert to TensorFlow Lite
print("Converting to TensorFlow Lite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save
output_path = '/opt/qwamos/security/ml/models/syscall_lstm.tflite'
with open(output_path, 'wb') as f:
    f.write(tflite_model)

print(f"Model saved to: {output_path}")
print(f"Model size: {len(tflite_model) / 1024:.2f} KB")
```

### Running Training

```bash
cd /opt/qwamos/security/ml/training
python3 train_syscall_lstm.py
```

---

## Model Evaluation

### Evaluation Metrics

For all models, evaluate using:

1. **True Positive Rate (Sensitivity)**: % of actual threats detected
2. **False Positive Rate**: % of benign events flagged as threats
3. **Precision**: % of flagged threats that are actual threats
4. **F1 Score**: Harmonic mean of precision and recall
5. **ROC-AUC**: Area under ROC curve

**Target Performance**:
- Network Anomaly: TPR ≥95%, FPR ≤5%
- File System: TPR ≥98%, FPR ≤2%
- System Call: TPR ≥96%, FPR ≤3%

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score

# For classifiers (File System, System Call)
scores = cross_val_score(model, X, y, cv=5, scoring='f1')
print(f"Cross-validation F1: {scores.mean():.4f} (+/- {scores.std():.4f})")
```

### Confusion Matrix Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.title('Confusion Matrix')
plt.savefig('/opt/qwamos/security/ml/models/confusion_matrix.png')
```

---

## Deployment

### Copy Models to Deployment Directory

```bash
# After training, copy .tflite models
sudo cp /opt/qwamos/security/ml/models/*.tflite /opt/qwamos/security/ml/models/
sudo chown qwamos:qwamos /opt/qwamos/security/ml/models/*.tflite

# Verify
ls -lh /opt/qwamos/security/ml/models/
```

### Update Detector Scripts

Ensure detectors use the new models:

```python
# In network_anomaly_detector.py
self.model_path = "/opt/qwamos/security/ml/models/network_ae.tflite"
```

### Restart Services

```bash
sudo systemctl restart qwamos-ml-network-anomaly.service
sudo systemctl restart qwamos-ml-file-system.service
sudo systemctl restart qwamos-ml-system-call.service
```

### Verify Deployment

```bash
# Check logs for model loading
sudo journalctl -u qwamos-ml-network-anomaly.service | grep "Model loaded"
```

Expected output:
```
[INFO] Model loaded successfully: network_ae.tflite (142.37 KB)
[INFO] Anomaly threshold: 0.1523
```

---

## Continuous Learning

### Model Retraining Strategy

1. **Collect New Data**: Log all detections (true positives and false positives)
2. **Label New Data**: Manually review and label
3. **Retrain Periodically**: Weekly or monthly
4. **A/B Testing**: Deploy new model alongside old, compare performance
5. **Gradual Rollout**: Replace old model if new model performs better

### Automated Retraining Pipeline

```bash
#!/bin/bash
# retrain_models.sh

# Collect recent detections
python3 /opt/qwamos/security/ml/scripts/collect_detection_logs.py

# Retrain models
python3 /opt/qwamos/security/ml/training/train_network_autoencoder.py
python3 /opt/qwamos/security/ml/training/train_file_classifier.py
python3 /opt/qwamos/security/ml/training/train_syscall_lstm.py

# Evaluate new models
python3 /opt/qwamos/security/ml/scripts/evaluate_models.py

# If evaluation passes, deploy
if [ $? -eq 0 ]; then
    echo "Deploying new models..."
    sudo systemctl restart qwamos-ml-*.service
else
    echo "Evaluation failed, keeping old models"
fi
```

Schedule retraining:
```bash
# Add to crontab
sudo crontab -e

# Run every Sunday at 2 AM
0 2 * * 0 /opt/qwamos/security/ml/training/retrain_models.sh
```

---

## Troubleshooting

### Training Fails with OOM (Out of Memory)

**Solution**: Reduce batch size or use data generators

```python
# Instead of loading all data into memory
X_train = np.load('large_dataset.npy')  # BAD

# Use generators
def data_generator(file_list, batch_size=32):
    while True:
        for i in range(0, len(file_list), batch_size):
            batch = file_list[i:i+batch_size]
            X = np.array([extract_features(f) for f in batch])
            yield X, X  # For autoencoder

model.fit(data_generator(files), steps_per_epoch=len(files)//32, epochs=100)
```

### Low Accuracy on Test Set

**Possible Causes**:
1. **Insufficient training data**: Collect more samples
2. **Class imbalance**: Use SMOTE or class weights
3. **Overfitting**: Add dropout, reduce model complexity
4. **Poor feature selection**: Analyze feature importance

**Fix for Class Imbalance**:
```python
from imblearn.over_sampling import SMOTE

smote = SMOTE()
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```

### TFLite Conversion Error

**Error**: `Some ops are not supported by the native TFLite runtime`

**Solution**: Use TF Select ops or simplify model

```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,  # TFLite ops
    tf.lite.OpsSet.SELECT_TF_OPS     # TensorFlow ops
]
tflite_model = converter.convert()
```

---

## Next Steps

After successful model training:

1. ✅ Deploy models to production
2. ✅ Monitor performance metrics
3. ✅ Set up continuous learning pipeline
4. ✅ Tune detection thresholds based on real-world FP/FN rates
5. ✅ Document model versions and performance

---

**Phase 7 ML Training Complete** ✅

For API integration, see `PHASE7_API_DOCUMENTATION.md`.
