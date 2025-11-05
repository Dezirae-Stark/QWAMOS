#!/usr/bin/env python3
"""
QWAMOS Network Anomaly Detector

ML-based real-time network traffic anomaly detection using Autoencoder.
Detects port scanning, DDoS, C2 communications, data exfiltration, and more.

Model: Autoencoder (TensorFlow Lite optimized for ARM64)
"""

import tensorflow as tf
import numpy as np
import time
import json
import logging
from typing import Dict, List, Optional
from scapy.all import sniff, IP, TCP, UDP, ICMP, DNS
from collections import deque, defaultdict
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NetworkAnomalyDetector')


class NetworkAnomalyDetector:
    """
    Real-time network traffic anomaly detection using autoencoder
    """

    def __init__(self,
                 model_path='/opt/qwamos/security/ml/models/network_ae.tflite',
                 anomaly_threshold=0.15):
        """
        Initialize Network Anomaly Detector

        Args:
            model_path: Path to TensorFlow Lite model
            anomaly_threshold: Reconstruction error threshold for anomaly detection
        """
        self.model_path = model_path
        self.anomaly_threshold = anomaly_threshold

        # Load TensorFlow Lite model (optimized for ARM64)
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            logger.info(f"Loaded ML model from {model_path}")
        except Exception as e:
            logger.warning(f"Model not found: {e}. Running in training mode.")
            self.interpreter = None

        # Feature statistics (loaded from training)
        self.mean = np.zeros(50)
        self.std = np.ones(50)
        self._load_normalization_params()

        # Packet buffers and statistics
        self.packet_buffer = deque(maxlen=1000)
        self.connection_stats = defaultdict(lambda: {
            'packets': 0,
            'bytes': 0,
            'start_time': time.time(),
            'ports': set()
        })

        # Detection history
        self.anomaly_history = deque(maxlen=100)
        self.alert_callback = None

        # Performance tracking
        self.packets_processed = 0
        self.anomalies_detected = 0

        logger.info("Network Anomaly Detector initialized")

    def _load_normalization_params(self):
        """Load feature normalization parameters"""
        try:
            params = np.load('/opt/qwamos/security/ml/models/network_norm_params.npz')
            self.mean = params['mean']
            self.std = params['std']
            logger.info("Loaded normalization parameters")
        except:
            logger.warning("Normalization params not found, using defaults")

    def extract_features(self, packet) -> np.ndarray:
        """
        Extract 50-dimensional feature vector from network packet

        Features:
         - Packet size, protocol, TTL
         - Source/dest ports
         - TCP flags
         - Payload entropy
         - Connection statistics
         - Temporal patterns
        """
        features = np.zeros(50, dtype=np.float32)

        try:
            if not packet.haslayer(IP):
                return features

            ip_layer = packet[IP]

            # Basic IP features (0-4)
            features[0] = len(packet)  # Packet size
            features[1] = ip_layer.proto  # Protocol number
            features[2] = ip_layer.ttl  # Time to live
            features[3] = ip_layer.len  # IP packet length
            features[4] = ip_layer.flags  # IP flags

            # TCP features (5-14)
            if packet.haslayer(TCP):
                tcp_layer = packet[TCP]
                features[5] = tcp_layer.sport  # Source port
                features[6] = tcp_layer.dport  # Destination port
                features[7] = tcp_layer.flags  # TCP flags
                features[8] = tcp_layer.window  # Window size
                features[9] = tcp_layer.seq  # Sequence number
                features[10] = tcp_layer.ack  # Acknowledgment number
                features[11] = len(tcp_layer.payload) if tcp_layer.payload else 0
                features[12] = 1  # Is TCP

            # UDP features (13-16)
            elif packet.haslayer(UDP):
                udp_layer = packet[UDP]
                features[13] = udp_layer.sport
                features[14] = udp_layer.dport
                features[15] = len(udp_layer.payload) if udp_layer.payload else 0
                features[16] = 1  # Is UDP

            # ICMP features (17-19)
            elif packet.haslayer(ICMP):
                icmp_layer = packet[ICMP]
                features[17] = icmp_layer.type
                features[18] = icmp_layer.code
                features[19] = 1  # Is ICMP

            # DNS features (20-22)
            if packet.haslayer(DNS):
                features[20] = 1  # Has DNS
                features[21] = len(packet[DNS].qd) if packet[DNS].qd else 0  # Queries
                features[22] = len(packet[DNS].an) if packet[DNS].an else 0  # Answers

            # Payload features (23-26)
            if packet.payload:
                payload_bytes = bytes(packet.payload)
                features[23] = len(payload_bytes)
                features[24] = self._compute_entropy(payload_bytes)
                features[25] = self._count_printable_chars(payload_bytes)
                features[26] = self._has_suspicious_patterns(payload_bytes)

            # Connection statistics (27-35)
            conn_key = self._get_connection_key(packet)
            if conn_key:
                stats = self.connection_stats[conn_key]
                features[27] = stats['packets']
                features[28] = stats['bytes']
                features[29] = time.time() - stats['start_time']  # Connection duration
                features[30] = len(stats['ports'])  # Unique ports accessed

            # Temporal features (31-40)
            features[31] = self._compute_packet_rate()
            features[32] = self._compute_connection_frequency()
            features[33] = self._compute_port_scan_score()
            features[34] = self._compute_ddos_score()
            features[35] = self._compute_data_exfil_score()

            # Advanced features (36-49)
            features[36] = self._is_common_port(features[6])  # Is dest port common?
            features[37] = self._is_privileged_port(features[5])  # Is source port privileged?
            features[38] = self._time_of_day()  # Hour of day (0-23)
            features[39] = self._day_of_week()  # Day of week (0-6)

            # Packet direction indicators (40-44)
            features[40] = 1 if features[5] < 1024 else 0  # Outbound from privileged port
            features[41] = 1 if features[6] < 1024 else 0  # Inbound to privileged port
            features[42] = 1 if features[6] in [80, 443] else 0  # HTTP/HTTPS
            features[43] = 1 if features[6] in [22, 23, 3389] else 0  # Remote access
            features[44] = 1 if features[6] == 53 else 0  # DNS

            # Statistical features (45-49)
            recent_packets = list(self.packet_buffer)[-100:]
            if recent_packets:
                sizes = [p['size'] for p in recent_packets]
                features[45] = np.mean(sizes) if sizes else 0
                features[46] = np.std(sizes) if len(sizes) > 1 else 0
                features[47] = np.min(sizes) if sizes else 0
                features[48] = np.max(sizes) if sizes else 0
                features[49] = len(recent_packets)

        except Exception as e:
            logger.error(f"Feature extraction error: {e}")

        return features

    def _compute_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        entropy = 0.0
        for x in range(256):
            p_x = float(data.count(bytes([x]))) / len(data)
            if p_x > 0:
                entropy -= p_x * np.log2(p_x)
        return entropy

    def _count_printable_chars(self, data: bytes) -> float:
        """Count percentage of printable characters"""
        if not data:
            return 0.0
        printable = sum(1 for b in data if 32 <= b <= 126)
        return printable / len(data)

    def _has_suspicious_patterns(self, data: bytes) -> float:
        """Check for suspicious patterns in payload"""
        suspicious_patterns = [
            b'eval(', b'exec(', b'system(', b'/bin/sh', b'cmd.exe',
            b'<script', b'javascript:', b'../../', b'SELECT * FROM',
            b'UNION SELECT', b'DROP TABLE', b'../../../'
        ]
        score = sum(1 for pattern in suspicious_patterns if pattern in data)
        return min(score / len(suspicious_patterns), 1.0)

    def _get_connection_key(self, packet) -> Optional[str]:
        """Get unique key for connection tracking"""
        if not packet.haslayer(IP):
            return None

        ip = packet[IP]
        proto = 'TCP' if packet.haslayer(TCP) else 'UDP' if packet.haslayer(UDP) else 'OTHER'

        sport = packet[TCP].sport if packet.haslayer(TCP) else \
                packet[UDP].sport if packet.haslayer(UDP) else 0
        dport = packet[TCP].dport if packet.haslayer(TCP) else \
                packet[UDP].dport if packet.haslayer(UDP) else 0

        return f"{ip.src}:{sport}->{ip.dst}:{dport}/{proto}"

    def _compute_packet_rate(self) -> float:
        """Compute packets per second over last minute"""
        if not self.packet_buffer:
            return 0.0

        current_time = time.time()
        recent_packets = [p for p in self.packet_buffer
                         if current_time - p['timestamp'] < 60]
        return len(recent_packets) / 60.0

    def _compute_connection_frequency(self) -> float:
        """Compute new connections per second"""
        current_time = time.time()
        recent_conns = [conn for conn in self.connection_stats.values()
                       if current_time - conn['start_time'] < 60]
        return len(recent_conns) / 60.0

    def _compute_port_scan_score(self) -> float:
        """Detect port scanning behavior"""
        # Check for rapid access to multiple ports from same source
        recent_time = time.time() - 10  # Last 10 seconds

        src_ports = defaultdict(set)
        for conn_key, stats in self.connection_stats.items():
            if stats['start_time'] > recent_time:
                src = conn_key.split('->')[0].split(':')[0]
                port = int(conn_key.split('->')[1].split(':')[1].split('/')[0])
                src_ports[src].add(port)

        # If any source accessed >10 unique ports in 10 seconds, likely port scan
        max_ports = max([len(ports) for ports in src_ports.values()], default=0)
        return min(max_ports / 50.0, 1.0)

    def _compute_ddos_score(self) -> float:
        """Detect DDoS attack patterns"""
        # High packet rate + many unique sources
        packet_rate = self._compute_packet_rate()

        # Count unique sources in last 10 seconds
        recent_time = time.time() - 10
        unique_sources = set()
        for conn_key, stats in self.connection_stats.items():
            if stats['start_time'] > recent_time:
                src = conn_key.split('->')[0].split(':')[0]
                unique_sources.add(src)

        # DDoS indicator: >100 pps + >20 unique sources
        ddos_score = (packet_rate / 100.0) * (len(unique_sources) / 20.0)
        return min(ddos_score, 1.0)

    def _compute_data_exfil_score(self) -> float:
        """Detect data exfiltration patterns"""
        # Large outbound data transfers
        recent_time = time.time() - 60

        outbound_bytes = 0
        for conn_key, stats in self.connection_stats.items():
            if stats['start_time'] > recent_time:
                outbound_bytes += stats['bytes']

        # Suspicious if >10MB outbound in 1 minute
        return min(outbound_bytes / (10 * 1024 * 1024), 1.0)

    def _is_common_port(self, port: float) -> float:
        """Check if port is commonly used"""
        common_ports = {80, 443, 22, 21, 25, 53, 110, 143, 993, 995, 3306, 5432, 27017}
        return 1.0 if int(port) in common_ports else 0.0

    def _is_privileged_port(self, port: float) -> float:
        """Check if port is privileged (<1024)"""
        return 1.0 if int(port) < 1024 else 0.0

    def _time_of_day(self) -> float:
        """Get current hour (0-23)"""
        return float(time.localtime().tm_hour)

    def _day_of_week(self) -> float:
        """Get current day of week (0-6)"""
        return float(time.localtime().tm_wday)

    def detect_anomaly(self, packet) -> Dict:
        """
        Detect if packet is anomalous using ML model

        Returns:
            dict: Detection result with anomaly flag, confidence, and details
        """
        self.packets_processed += 1

        # Extract features
        features = self.extract_features(packet)

        # Update packet buffer
        self.packet_buffer.append({
            'timestamp': time.time(),
            'size': len(packet),
            'proto': packet[IP].proto if packet.haslayer(IP) else 0
        })

        # Update connection statistics
        conn_key = self._get_connection_key(packet)
        if conn_key:
            self.connection_stats[conn_key]['packets'] += 1
            self.connection_stats[conn_key]['bytes'] += len(packet)

            if packet.haslayer(TCP):
                port = packet[TCP].dport
                self.connection_stats[conn_key]['ports'].add(port)
            elif packet.haslayer(UDP):
                port = packet[UDP].dport
                self.connection_stats[conn_key]['ports'].add(port)

        # Skip ML inference if model not loaded
        if self.interpreter is None:
            return {'anomaly': False, 'reason': 'Model not loaded'}

        # Normalize features
        features_norm = (features - self.mean) / (self.std + 1e-8)

        # Run ML inference
        try:
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                features_norm.reshape(1, -1).astype(np.float32)
            )
            self.interpreter.invoke()

            # Get reconstruction
            reconstruction = self.interpreter.get_tensor(
                self.output_details[0]['index']
            )[0]

            # Calculate reconstruction error (MSE)
            error = np.mean((features_norm - reconstruction) ** 2)

            # Check if anomalous
            if error > self.anomaly_threshold:
                self.anomalies_detected += 1

                detection = {
                    'anomaly': True,
                    'confidence': min(error / self.anomaly_threshold, 1.0),
                    'reconstruction_error': float(error),
                    'threshold': self.anomaly_threshold,
                    'timestamp': time.time(),
                    'packet_info': self._extract_packet_info(packet),
                    'features': features.tolist(),
                    'threat_indicators': self._analyze_threat_type(features)
                }

                self.anomaly_history.append(detection)

                # Trigger alert callback
                if self.alert_callback:
                    self.alert_callback(detection)

                logger.warning(f"ANOMALY DETECTED: {detection['threat_indicators']}")

                return detection

        except Exception as e:
            logger.error(f"ML inference error: {e}")

        return {'anomaly': False}

    def _extract_packet_info(self, packet) -> Dict:
        """Extract human-readable packet information"""
        info = {'raw': str(packet.summary())}

        if packet.haslayer(IP):
            info['src_ip'] = packet[IP].src
            info['dst_ip'] = packet[IP].dst
            info['proto'] = packet[IP].proto

        if packet.haslayer(TCP):
            info['src_port'] = packet[TCP].sport
            info['dst_port'] = packet[TCP].dport
            info['flags'] = str(packet[TCP].flags)

        elif packet.haslayer(UDP):
            info['src_port'] = packet[UDP].sport
            info['dst_port'] = packet[UDP].dport

        return info

    def _analyze_threat_type(self, features: np.ndarray) -> List[str]:
        """Analyze features to determine likely threat type"""
        threats = []

        # Port scan detection
        if features[33] > 0.5:  # port_scan_score
            threats.append('PORT_SCAN')

        # DDoS detection
        if features[34] > 0.5:  # ddos_score
            threats.append('DDOS')

        # Data exfiltration detection
        if features[35] > 0.5:  # data_exfil_score
            threats.append('DATA_EXFILTRATION')

        # Suspicious payload
        if features[26] > 0.3:  # suspicious_patterns
            threats.append('SUSPICIOUS_PAYLOAD')

        # High entropy (encryption/obfuscation)
        if features[24] > 7.5:  # entropy
            threats.append('ENCRYPTED_PAYLOAD')

        # Unknown protocol behavior
        if features[12] == 0 and features[16] == 0 and features[19] == 0:
            threats.append('UNKNOWN_PROTOCOL')

        return threats if threats else ['UNKNOWN']

    def monitor_interface(self, interface='any', packet_count=0):
        """
        Monitor network interface for anomalies

        Args:
            interface: Network interface to monitor ('any' for all)
            packet_count: Number of packets to capture (0 = infinite)
        """
        logger.info(f"Starting network monitoring on interface: {interface}")

        def packet_handler(packet):
            result = self.detect_anomaly(packet)
            if result.get('anomaly'):
                logger.warning(f"Anomaly: {result}")

        try:
            sniff(iface=interface, prn=packet_handler, count=packet_count, store=0)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

    def set_alert_callback(self, callback):
        """Set callback function for anomaly alerts"""
        self.alert_callback = callback

    def get_statistics(self) -> Dict:
        """Get detector statistics"""
        return {
            'packets_processed': self.packets_processed,
            'anomalies_detected': self.anomalies_detected,
            'detection_rate': self.anomalies_detected / max(self.packets_processed, 1),
            'active_connections': len(self.connection_stats),
            'recent_anomalies': len(self.anomaly_history)
        }


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='QWAMOS Network Anomaly Detector')
    parser.add_argument('-i', '--interface', default='any', help='Network interface')
    parser.add_argument('-t', '--threshold', type=float, default=0.15, help='Anomaly threshold')
    parser.add_argument('-c', '--count', type=int, default=0, help='Packet count (0=infinite)')
    args = parser.parse_args()

    detector = NetworkAnomalyDetector(anomaly_threshold=args.threshold)
    detector.monitor_interface(interface=args.interface, packet_count=args.count)
