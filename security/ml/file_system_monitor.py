#!/usr/bin/env python3
"""
QWAMOS File System Monitor

ML-based file system monitoring for threat detection.
Detects ransomware, rootkits, unauthorized access, data theft, and configuration tampering.

Model: Random Forest Classifier (TensorFlow Lite optimized for ARM64)
"""

import os
import time
import json
import logging
import hashlib
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from collections import deque, defaultdict
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FileSystemMonitor')


class FileSystemMonitor(FileSystemEventHandler):
    """
    ML-based file system monitoring for threat detection
    """

    def __init__(self,
                 model_path='/opt/qwamos/security/ml/models/file_classifier.tflite',
                 watch_paths=None):
        """
        Initialize File System Monitor

        Args:
            model_path: Path to TensorFlow Lite model
            watch_paths: List of paths to monitor (default: critical system paths)
        """
        super().__init__()

        self.model_path = model_path

        # Load ML model
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            logger.info(f"Loaded ML model from {model_path}")
        except Exception as e:
            logger.warning(f"Model not found: {e}. Running in rule-based mode.")
            self.interpreter = None

        # Paths to monitor
        self.watch_paths = watch_paths or [
            '/etc',           # System configuration
            '/root',          # Root home directory
            '/home',          # User home directories
            '/usr/bin',       # System binaries
            '/usr/sbin',      # System admin binaries
            '/var/www',       # Web root
            '/opt/qwamos',    # QWAMOS installation
        ]

        # Event buffer
        self.file_events = deque(maxlen=10000)
        self.window_size = 60  # 1-minute window

        # Statistics tracking
        self.event_counts = defaultdict(int)
        self.file_hashes = {}  # Track file integrity
        self.recent_modifications = deque(maxlen=1000)

        # Threat detection
        self.threat_history = deque(maxlen=100)
        self.alert_callback = None

        # Performance tracking
        self.events_processed = 0
        self.threats_detected = 0

        # Ransomware-specific tracking
        self.encrypted_file_extensions = {
            '.encrypted', '.locked', '.crypt', '.cry', '.enc',
            '.crypted', '.crypto', '.cipher', '.cerber', '.locky'
        }
        self.recent_encryption_events = deque(maxlen=500)

        # Critical system files
        self.critical_files = {
            '/etc/passwd', '/etc/shadow', '/etc/sudoers',
            '/etc/ssh/sshd_config', '/etc/hosts',
            '/root/.ssh/authorized_keys'
        }

        logger.info("File System Monitor initialized")

    def on_any_event(self, event: FileSystemEvent):
        """Handle any file system event"""
        try:
            self.events_processed += 1

            # Extract features
            features = self.extract_features(event)

            # Add to event buffer
            self.file_events.append({
                'timestamp': time.time(),
                'event': event,
                'features': features
            })

            # Update statistics
            self.event_counts[event.event_type] += 1

            # Check for immediate threats (rule-based)
            immediate_threat = self._check_immediate_threats(event, features)
            if immediate_threat:
                self._alert_threat(immediate_threat)
                return

            # Analyze window for ML-based detection
            if len(self.file_events) >= 10:  # Need minimum events
                self._analyze_window()

        except Exception as e:
            logger.error(f"Error handling event: {e}")

    def extract_features(self, event: FileSystemEvent) -> np.ndarray:
        """
        Extract 30-dimensional feature vector from file event

        Features:
         - Event type (created, modified, deleted, moved)
         - File characteristics (size, permissions, type)
         - Temporal patterns
         - Path characteristics
        """
        features = np.zeros(30, dtype=np.float32)

        try:
            # Event type features (0-3)
            features[0] = 1 if event.event_type == 'created' else 0
            features[1] = 1 if event.event_type == 'deleted' else 0
            features[2] = 1 if event.event_type == 'modified' else 0
            features[3] = 1 if event.event_type == 'moved' else 0

            # File characteristics (4-10)
            if os.path.exists(event.src_path):
                try:
                    stat = os.stat(event.src_path)
                    features[4] = stat.st_size  # File size
                    features[5] = stat.st_mode  # Permissions
                    features[6] = stat.st_mtime  # Modification time
                    features[7] = stat.st_ctime  # Creation time
                    features[8] = stat.st_uid  # Owner UID
                    features[9] = stat.st_gid  # Owner GID
                    features[10] = stat.st_nlink  # Number of hard links
                except:
                    pass

            # File type indicators (11-19)
            path = event.src_path.lower()
            features[11] = 1 if path.endswith(('.exe', '.bin', '.sh')) else 0  # Executable
            features[12] = 1 if path.endswith(('.so', '.dll', '.dylib')) else 0  # Library
            features[13] = 1 if path.endswith(('.conf', '.config', '.ini', '.cfg')) else 0  # Config
            features[14] = 1 if path.endswith(('.key', '.pem', '.crt', '.p12')) else 0  # Crypto
            features[15] = 1 if path.endswith(('.db', '.sqlite', '.sql')) else 0  # Database
            features[16] = 1 if path.endswith(('.log', '.txt')) else 0  # Log/text
            features[17] = 1 if path.endswith(('.jpg', '.png', '.pdf', '.doc')) else 0  # Document
            features[18] = 1 if any(path.endswith(ext) for ext in self.encrypted_file_extensions) else 0
            features[19] = 1 if event.src_path in self.critical_files else 0  # Critical file

            # Path characteristics (20-24)
            features[20] = 1 if event.src_path.startswith('/etc/') else 0
            features[21] = 1 if event.src_path.startswith('/root/') else 0
            features[22] = 1 if event.src_path.startswith('/home/') else 0
            features[23] = 1 if event.src_path.startswith('/tmp/') else 0
            features[24] = 1 if event.src_path.startswith('/var/') else 0

            # Temporal features (25-29)
            features[25] = self._compute_event_rate()
            features[26] = self._compute_modification_burst_score()
            features[27] = self._compute_encryption_indicator()
            features[28] = self._compute_deletion_rate()
            features[29] = self._compute_permission_change_score()

        except Exception as e:
            logger.error(f"Feature extraction error: {e}")

        return features

    def _compute_event_rate(self) -> float:
        """Compute file events per second"""
        if not self.file_events:
            return 0.0

        current_time = time.time()
        recent_events = [e for e in self.file_events
                        if current_time - e['timestamp'] < 60]
        return len(recent_events) / 60.0

    def _compute_modification_burst_score(self) -> float:
        """Detect burst of file modifications (ransomware indicator)"""
        current_time = time.time()
        recent_mods = [e for e in self.recent_modifications
                      if current_time - e < 10]  # Last 10 seconds

        # Suspicious if >50 modifications in 10 seconds
        return min(len(recent_mods) / 50.0, 1.0)

    def _compute_encryption_indicator(self) -> float:
        """Detect file encryption patterns"""
        current_time = time.time()
        recent_encryption = [e for e in self.recent_encryption_events
                           if current_time - e < 60]  # Last minute

        # Suspicious if >20 encrypted files in 1 minute
        return min(len(recent_encryption) / 20.0, 1.0)

    def _compute_deletion_rate(self) -> float:
        """Compute file deletion rate"""
        if not self.file_events:
            return 0.0

        current_time = time.time()
        recent_deletions = [e for e in self.file_events
                          if (current_time - e['timestamp'] < 60 and
                              e['event'].event_type == 'deleted')]
        return len(recent_deletions) / 60.0

    def _compute_permission_change_score(self) -> float:
        """Detect suspicious permission changes"""
        # Track recent chmod events (not directly available in watchdog)
        # This would require additional monitoring
        return 0.0

    def _check_immediate_threats(self, event: FileSystemEvent, features: np.ndarray) -> Dict:
        """Check for immediate threats using rule-based detection"""

        # Critical file modification
        if event.src_path in self.critical_files and event.event_type in ['modified', 'deleted']:
            return {
                'type': 'CRITICAL_FILE_TAMPERING',
                'severity': 'CRITICAL',
                'details': {
                    'file': event.src_path,
                    'event': event.event_type
                },
                'timestamp': time.time()
            }

        # Ransomware detection
        ransomware_threat = self._detect_ransomware()
        if ransomware_threat:
            return ransomware_threat

        # Suspicious executable creation
        if (event.event_type == 'created' and
            event.src_path.endswith(('.exe', '.sh', '.bin')) and
            (event.src_path.startswith('/tmp/') or event.src_path.startswith('/var/tmp/'))):
            return {
                'type': 'SUSPICIOUS_EXECUTABLE',
                'severity': 'HIGH',
                'details': {
                    'file': event.src_path,
                    'location': 'temp_directory'
                },
                'timestamp': time.time()
            }

        # Hidden file creation in system directories
        basename = os.path.basename(event.src_path)
        if (basename.startswith('.') and event.event_type == 'created' and
            any(event.src_path.startswith(p) for p in ['/etc/', '/usr/', '/root/'])):
            return {
                'type': 'HIDDEN_FILE_CREATION',
                'severity': 'MEDIUM',
                'details': {
                    'file': event.src_path
                },
                'timestamp': time.time()
            }

        return None

    def _detect_ransomware(self) -> Dict:
        """Specific ransomware detection logic"""
        recent_events = list(self.file_events)[-100:]  # Last 100 events

        if not recent_events:
            return None

        # Count file modifications
        modifications = sum(1 for e in recent_events
                          if e['event'].event_type == 'modified')

        # Check for suspicious extensions
        encrypted_count = sum(
            1 for e in recent_events
            if any(e['event'].src_path.endswith(ext)
                  for ext in self.encrypted_file_extensions)
        )

        # Check for rapid file renaming to .encrypted/.locked
        rename_to_encrypted = sum(
            1 for e in recent_events
            if (e['event'].event_type == 'moved' and
                hasattr(e['event'], 'dest_path') and
                any(e['event'].dest_path.endswith(ext)
                   for ext in self.encrypted_file_extensions))
        )

        # Ransomware indicators:
        # 1. >50 modifications in short time
        # 2. >10 files with encrypted extensions
        # 3. >5 files renamed to .encrypted/.locked
        if modifications > 50 and (encrypted_count > 10 or rename_to_encrypted > 5):
            return {
                'type': 'RANSOMWARE_DETECTED',
                'severity': 'CRITICAL',
                'details': {
                    'modifications': modifications,
                    'encrypted_files': encrypted_count,
                    'renamed_files': rename_to_encrypted,
                    'action': 'IMMEDIATE_ISOLATION',
                    'affected_files': len(recent_events)
                },
                'timestamp': time.time()
            }

        return None

    def _analyze_window(self):
        """Analyze events in time window for threats using ML"""
        # Remove old events
        current_time = time.time()
        self.file_events = deque(
            [e for e in self.file_events
             if current_time - e['timestamp'] < self.window_size],
            maxlen=10000
        )

        if len(self.file_events) < 10:
            return  # Not enough data

        # Skip ML if model not loaded
        if self.interpreter is None:
            return

        # Aggregate features from window
        aggregated_features = self._aggregate_features()

        # Run ML classification
        threat = self._classify_threat(aggregated_features)

        if threat:
            self._alert_threat(threat)

    def _aggregate_features(self) -> np.ndarray:
        """Aggregate features from event window"""
        # Compute aggregate statistics over window
        features = np.zeros(30, dtype=np.float32)

        recent_events = list(self.file_events)[-100:]

        # Event type counts
        features[0] = sum(1 for e in recent_events
                         if e['event'].event_type == 'created')
        features[1] = sum(1 for e in recent_events
                         if e['event'].event_type == 'deleted')
        features[2] = sum(1 for e in recent_events
                         if e['event'].event_type == 'modified')
        features[3] = sum(1 for e in recent_events
                         if e['event'].event_type == 'moved')

        # Feature aggregations (mean, std, max)
        if recent_events:
            feature_matrix = np.array([e['features'] for e in recent_events])
            features[4:14] = np.mean(feature_matrix, axis=0)[:10]
            features[14:24] = np.std(feature_matrix, axis=0)[:10]
            features[24:30] = np.max(feature_matrix, axis=0)[:6]

        return features

    def _classify_threat(self, features: np.ndarray) -> Dict:
        """Classify threat using ML model"""
        try:
            # Normalize features
            features_norm = features / (np.max(features) + 1e-8)

            # Run inference
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                features_norm.reshape(1, -1).astype(np.float32)
            )
            self.interpreter.invoke()

            # Get classification
            prediction = self.interpreter.get_tensor(
                self.output_details[0]['index']
            )[0]

            # Interpret prediction
            # [0] = benign, [1] = ransomware, [2] = rootkit, [3] = data_theft
            threat_types = ['BENIGN', 'RANSOMWARE', 'ROOTKIT', 'DATA_THEFT']
            predicted_class = np.argmax(prediction)
            confidence = prediction[predicted_class]

            if predicted_class > 0 and confidence > 0.7:  # Threat detected
                self.threats_detected += 1

                return {
                    'type': f'ML_DETECTED_{threat_types[predicted_class]}',
                    'severity': 'HIGH' if confidence > 0.9 else 'MEDIUM',
                    'details': {
                        'confidence': float(confidence),
                        'predicted_class': threat_types[predicted_class],
                        'probabilities': {t: float(p) for t, p in zip(threat_types, prediction)}
                    },
                    'timestamp': time.time()
                }

        except Exception as e:
            logger.error(f"ML classification error: {e}")

        return None

    def _alert_threat(self, threat: Dict):
        """Send alert for detected threat"""
        self.threat_history.append(threat)

        logger.critical(f"THREAT DETECTED: {threat['type']} - Severity: {threat['severity']}")

        # Trigger alert callback
        if self.alert_callback:
            try:
                self.alert_callback(threat)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

    def start_monitoring(self, paths=None):
        """
        Start monitoring file system

        Args:
            paths: List of paths to monitor (uses default if None)
        """
        paths = paths or self.watch_paths

        observer = Observer()

        for path in paths:
            if os.path.exists(path):
                observer.schedule(self, path, recursive=True)
                logger.info(f"Monitoring: {path}")
            else:
                logger.warning(f"Path does not exist: {path}")

        observer.start()
        logger.info("File System Monitor started")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("Monitoring stopped by user")

        observer.join()

    def set_alert_callback(self, callback):
        """Set callback function for threat alerts"""
        self.alert_callback = callback

    def get_statistics(self) -> Dict:
        """Get monitor statistics"""
        return {
            'events_processed': self.events_processed,
            'threats_detected': self.threats_detected,
            'event_rate': self._compute_event_rate(),
            'event_counts': dict(self.event_counts),
            'recent_threats': len(self.threat_history)
        }


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='QWAMOS File System Monitor')
    parser.add_argument('-p', '--paths', nargs='+', help='Paths to monitor')
    args = parser.parse_args()

    monitor = FileSystemMonitor(watch_paths=args.paths)
    monitor.start_monitoring()
