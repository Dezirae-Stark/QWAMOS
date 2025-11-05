#!/usr/bin/env python3
"""
QWAMOS System Call Analyzer

ML-based system call sequence analysis for threat detection.
Detects privilege escalation, backdoors, process injection, and code execution exploits.

Model: LSTM (Long Short-Term Memory) for sequence analysis (TensorFlow Lite)
"""

import os
import time
import json
import logging
import subprocess
import numpy as np
import tensorflow as tf
from typing import Dict, List, Deque
from collections import deque, defaultdict
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SystemCallAnalyzer')


class SystemCallAnalyzer:
    """
    ML-based system call sequence analysis for threat detection
    """

    # System call mapping (common Linux syscalls)
    SYSCALL_MAP = {
        'read': 0, 'write': 1, 'open': 2, 'close': 3, 'stat': 4,
        'fstat': 5, 'lstat': 6, 'poll': 7, 'lseek': 8, 'mmap': 9,
        'mprotect': 10, 'munmap': 11, 'brk': 12, 'rt_sigaction': 13,
        'rt_sigprocmask': 14, 'ioctl': 15, 'pread64': 16, 'pwrite64': 17,
        'readv': 18, 'writev': 19, 'access': 20, 'pipe': 21, 'select': 22,
        'sched_yield': 23, 'mremap': 24, 'msync': 25, 'mincore': 26,
        'madvise': 27, 'shmget': 28, 'shmat': 29, 'shmctl': 30,
        'dup': 31, 'dup2': 32, 'pause': 33, 'nanosleep': 34, 'getitimer': 35,
        'alarm': 36, 'setitimer': 37, 'getpid': 38, 'sendfile': 39,
        'socket': 40, 'connect': 41, 'accept': 42, 'sendto': 43,
        'recvfrom': 44, 'sendmsg': 45, 'recvmsg': 46, 'shutdown': 47,
        'bind': 48, 'listen': 49, 'getsockname': 50, 'getpeername': 51,
        'socketpair': 52, 'setsockopt': 53, 'getsockopt': 54, 'clone': 55,
        'fork': 56, 'vfork': 57, 'execve': 58, 'exit': 59, 'wait4': 60,
        'kill': 61, 'uname': 62, 'semget': 63, 'semop': 64, 'semctl': 65,
        'shmdt': 66, 'msgget': 67, 'msgsnd': 68, 'msgrcv': 69,
        'msgctl': 70, 'fcntl': 71, 'flock': 72, 'fsync': 73, 'fdatasync': 74,
        'truncate': 75, 'ftruncate': 76, 'getdents': 77, 'getcwd': 78,
        'chdir': 79, 'fchdir': 80, 'rename': 81, 'mkdir': 82, 'rmdir': 83,
        'creat': 84, 'link': 85, 'unlink': 86, 'symlink': 87, 'readlink': 88,
        'chmod': 89, 'fchmod': 90, 'chown': 91, 'fchown': 92, 'lchown': 93,
        'umask': 94, 'gettimeofday': 95, 'getrlimit': 96, 'getrusage': 97,
        'sysinfo': 98, 'times': 99, 'ptrace': 100, 'getuid': 101,
        'syslog': 102, 'getgid': 103, 'setuid': 104, 'setgid': 105,
        'geteuid': 106, 'getegid': 107, 'setpgid': 108, 'getppid': 109,
        'getpgrp': 110, 'setsid': 111, 'setreuid': 112, 'setregid': 113,
        'getgroups': 114, 'setgroups': 115, 'setresuid': 116, 'getresuid': 117,
        'setresgid': 118, 'getresgid': 119, 'getpgid': 120, 'setfsuid': 121,
        'setfsgid': 122, 'getsid': 123, 'capget': 124, 'capset': 125,
        'prctl': 126, 'unknown': 127
    }

    def __init__(self,
                 model_path='/opt/qwamos/security/ml/models/syscall_lstm.tflite',
                 sequence_length=50):
        """
        Initialize System Call Analyzer

        Args:
            model_path: Path to TensorFlow Lite LSTM model
            sequence_length: Length of syscall sequences to analyze
        """
        self.model_path = model_path
        self.sequence_length = sequence_length

        # Load ML model
        try:
            self.interpreter = tf.lite.Interpreter(model_path=model_path)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            logger.info(f"Loaded LSTM model from {model_path}")
        except Exception as e:
            logger.warning(f"Model not found: {e}. Running in rule-based mode.")
            self.interpreter = None

        # Process monitoring
        self.process_syscalls = defaultdict(lambda: deque(maxlen=sequence_length))
        self.process_info = {}

        # Threat tracking
        self.threat_history = deque(maxlen=100)
        self.alert_callback = None

        # Statistics
        self.syscalls_processed = 0
        self.threats_detected = 0

        # Monitoring thread
        self.monitoring = False
        self.monitor_thread = None

        logger.info("System Call Analyzer initialized")

    def start_monitoring(self, target_pids=None):
        """
        Start monitoring system calls

        Args:
            target_pids: List of PIDs to monitor (None = all processes)
        """
        if self.monitoring:
            logger.warning("Already monitoring")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_syscalls,
            args=(target_pids,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Started system call monitoring")

    def stop_monitoring(self):
        """Stop monitoring system calls"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Stopped system call monitoring")

    def _monitor_syscalls(self, target_pids=None):
        """
        Monitor system calls using strace

        Note: This is a simplified implementation. In production, would use:
        - eBPF/bpftrace for efficient kernel-level tracing
        - perf events
        - SystemTap
        - auditd
        """
        # For demonstration, we'll use a simulated approach
        # In production, this would use eBPF or kernel modules

        logger.info("Monitoring system calls (simulation mode)...")

        while self.monitoring:
            try:
                # Simulate syscall monitoring
                # In real implementation, this would capture actual syscalls
                self._simulate_syscall_capture()
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(1)

    def _simulate_syscall_capture(self):
        """Simulate syscall capture (for demonstration)"""
        # This would be replaced with actual syscall capture in production
        pass

    def capture_syscall(self, pid: int, syscall: str, args: List = None, retval: int = 0):
        """
        Capture and analyze a system call

        Args:
            pid: Process ID
            syscall: System call name
            args: System call arguments
            retval: Return value
        """
        self.syscalls_processed += 1

        # Map syscall to ID
        syscall_id = self.SYSCALL_MAP.get(syscall, self.SYSCALL_MAP['unknown'])

        # Add to process sequence
        self.process_syscalls[pid].append({
            'syscall_id': syscall_id,
            'syscall_name': syscall,
            'args': args or [],
            'retval': retval,
            'timestamp': time.time()
        })

        # Update process info
        if pid not in self.process_info:
            self.process_info[pid] = {
                'first_seen': time.time(),
                'syscall_count': 0,
                'threat_score': 0.0
            }
        self.process_info[pid]['syscall_count'] += 1

        # Check for suspicious patterns (rule-based)
        immediate_threat = self._check_suspicious_patterns(pid, syscall, args)
        if immediate_threat:
            self._alert_threat(immediate_threat)

        # Analyze sequence with ML if we have enough data
        if len(self.process_syscalls[pid]) >= self.sequence_length:
            self._analyze_sequence(pid)

    def _check_suspicious_patterns(self, pid: int, syscall: str, args: List) -> Dict:
        """Check for immediately suspicious syscall patterns"""

        # Privilege escalation attempts
        if syscall in ['setuid', 'setgid', 'setreuid', 'setregid']:
            # Check if trying to escalate to root (uid/gid 0)
            if args and 0 in args[:2]:
                return {
                    'type': 'PRIVILEGE_ESCALATION_ATTEMPT',
                    'severity': 'CRITICAL',
                    'details': {
                        'pid': pid,
                        'syscall': syscall,
                        'args': args,
                        'description': f'Process {pid} attempting to gain root privileges'
                    },
                    'timestamp': time.time()
                }

        # Process injection (ptrace)
        if syscall == 'ptrace':
            return {
                'type': 'PROCESS_INJECTION_ATTEMPT',
                'severity': 'HIGH',
                'details': {
                    'pid': pid,
                    'syscall': syscall,
                    'args': args,
                    'description': f'Process {pid} using ptrace (possible injection)'
                },
                'timestamp': time.time()
            }

        # Suspicious execve patterns
        if syscall == 'execve':
            if args and len(args) > 0:
                executable = str(args[0])
                # Check for shell execution
                if any(shell in executable for shell in ['/bin/sh', '/bin/bash', 'python', 'perl', 'ruby']):
                    # Check if from unusual location
                    recent_syscalls = list(self.process_syscalls[pid])[-10:]
                    has_network = any(s['syscall_name'] in ['socket', 'connect', 'accept']
                                    for s in recent_syscalls)

                    if has_network:
                        return {
                            'type': 'REVERSE_SHELL_ATTEMPT',
                            'severity': 'CRITICAL',
                            'details': {
                                'pid': pid,
                                'executable': executable,
                                'description': f'Possible reverse shell: network + shell execution'
                            },
                            'timestamp': time.time()
                        }

        # Kernel module loading
        if syscall in ['init_module', 'finit_module']:
            return {
                'type': 'KERNEL_MODULE_LOAD',
                'severity': 'HIGH',
                'details': {
                    'pid': pid,
                    'syscall': syscall,
                    'description': f'Process {pid} loading kernel module (possible rootkit)'
                },
                'timestamp': time.time()
            }

        return None

    def _analyze_sequence(self, pid: int):
        """Analyze syscall sequence using LSTM model"""
        if not self.interpreter:
            return

        try:
            # Get syscall sequence
            sequence = list(self.process_syscalls[pid])[-self.sequence_length:]

            # Extract syscall IDs
            syscall_ids = [s['syscall_id'] for s in sequence]

            # Pad if needed
            while len(syscall_ids) < self.sequence_length:
                syscall_ids.insert(0, 0)  # Pad with zeros at beginning

            # Convert to numpy array
            sequence_array = np.array(syscall_ids, dtype=np.float32).reshape(1, self.sequence_length, 1)

            # Run LSTM inference
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                sequence_array
            )
            self.interpreter.invoke()

            # Get prediction
            prediction = self.interpreter.get_tensor(
                self.output_details[0]['index']
            )[0]

            # Interpret prediction
            # [0] = benign, [1] = privilege_escalation, [2] = backdoor, [3] = exploit
            threat_types = ['BENIGN', 'PRIVILEGE_ESCALATION', 'BACKDOOR', 'EXPLOIT']
            predicted_class = np.argmax(prediction)
            confidence = prediction[predicted_class]

            if predicted_class > 0 and confidence > 0.75:  # Threat detected
                self.threats_detected += 1
                self.process_info[pid]['threat_score'] = float(confidence)

                threat = {
                    'type': f'ML_DETECTED_{threat_types[predicted_class]}',
                    'severity': 'CRITICAL' if confidence > 0.9 else 'HIGH',
                    'details': {
                        'pid': pid,
                        'confidence': float(confidence),
                        'predicted_class': threat_types[predicted_class],
                        'probabilities': {t: float(p) for t, p in zip(threat_types, prediction)},
                        'recent_syscalls': [s['syscall_name'] for s in sequence[-10:]]
                    },
                    'timestamp': time.time()
                }

                self._alert_threat(threat)

        except Exception as e:
            logger.error(f"Sequence analysis error: {e}")

    def analyze_process(self, pid: int) -> Dict:
        """
        Analyze a specific process

        Args:
            pid: Process ID

        Returns:
            dict: Analysis results
        """
        if pid not in self.process_syscalls:
            return {
                'pid': pid,
                'monitored': False,
                'message': 'Process not being monitored'
            }

        syscalls = list(self.process_syscalls[pid])
        info = self.process_info[pid]

        # Compute statistics
        syscall_counts = defaultdict(int)
        for s in syscalls:
            syscall_counts[s['syscall_name']] += 1

        return {
            'pid': pid,
            'monitored': True,
            'syscall_count': len(syscalls),
            'unique_syscalls': len(syscall_counts),
            'top_syscalls': sorted(syscall_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'threat_score': info.get('threat_score', 0.0),
            'monitoring_duration': time.time() - info.get('first_seen', time.time())
        }

    def _alert_threat(self, threat: Dict):
        """Send alert for detected threat"""
        self.threat_history.append(threat)

        logger.critical(f"SYSCALL THREAT DETECTED: {threat['type']} - Severity: {threat['severity']}")

        # Trigger alert callback
        if self.alert_callback:
            try:
                self.alert_callback(threat)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

    def set_alert_callback(self, callback):
        """Set callback function for threat alerts"""
        self.alert_callback = callback

    def get_statistics(self) -> Dict:
        """Get analyzer statistics"""
        return {
            'syscalls_processed': self.syscalls_processed,
            'threats_detected': self.threats_detected,
            'monitored_processes': len(self.process_syscalls),
            'recent_threats': len(self.threat_history),
            'monitoring': self.monitoring
        }

    def get_process_list(self) -> List[Dict]:
        """Get list of monitored processes"""
        processes = []
        for pid, info in self.process_info.items():
            processes.append({
                'pid': pid,
                'syscall_count': info['syscall_count'],
                'threat_score': info['threat_score'],
                'monitoring_duration': time.time() - info['first_seen']
            })

        # Sort by threat score (descending)
        processes.sort(key=lambda x: x['threat_score'], reverse=True)
        return processes


# Demo/Test Interface
def demo_syscall_sequences():
    """Demonstrate syscall analysis with example sequences"""
    analyzer = SystemCallAnalyzer()

    logger.info("=== Demonstrating System Call Analysis ===")

    # Example 1: Normal process
    logger.info("\n1. Normal process behavior:")
    normal_pid = 1234
    normal_syscalls = ['open', 'read', 'write', 'close', 'open', 'read', 'write', 'close']
    for syscall in normal_syscalls:
        analyzer.capture_syscall(normal_pid, syscall)
    result = analyzer.analyze_process(normal_pid)
    logger.info(f"Analysis: {json.dumps(result, indent=2)}")

    # Example 2: Privilege escalation
    logger.info("\n2. Privilege escalation attempt:")
    priv_esc_pid = 5678
    priv_esc_syscalls = ['open', 'read', 'setuid', 'execve']
    for i, syscall in enumerate(priv_esc_syscalls):
        args = [0] if syscall == 'setuid' else ['/bin/sh'] if syscall == 'execve' else []
        analyzer.capture_syscall(priv_esc_pid, syscall, args)

    # Example 3: Reverse shell
    logger.info("\n3. Reverse shell attempt:")
    revshell_pid = 9012
    revshell_syscalls = ['socket', 'connect', 'dup2', 'dup2', 'dup2', 'execve']
    for syscall in revshell_syscalls:
        args = ['/bin/bash'] if syscall == 'execve' else []
        analyzer.capture_syscall(revshell_pid, syscall, args)

    # Show statistics
    logger.info("\n=== Statistics ===")
    stats = analyzer.get_statistics()
    logger.info(json.dumps(stats, indent=2))

    # Show process list
    logger.info("\n=== Monitored Processes ===")
    processes = analyzer.get_process_list()
    for proc in processes:
        logger.info(f"PID {proc['pid']}: Threat Score: {proc['threat_score']:.2f}, "
                   f"Syscalls: {proc['syscall_count']}")


if __name__ == "__main__":
    demo_syscall_sequences()
