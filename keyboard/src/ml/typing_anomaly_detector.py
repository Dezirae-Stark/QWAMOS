#!/usr/bin/env python3
"""
QWAMOS SecureType Keyboard - ML Typing Anomaly Detector

Detects unauthorized keyboard usage via typing dynamics analysis:
- Press duration patterns
- Inter-key timing
- Pressure and touch area
- Real-time anomaly detection

Uses TensorFlow Lite for ARM64 optimization

@module typing_anomaly_detector
@version 1.0.0
"""

import sys
import json
import numpy as np
import time
from pathlib import Path
from collections import deque

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    import tensorflow.lite as tflite

class TypingAnomalyDetector:
    """
    Detect unauthorized keyboard usage via typing dynamics
    """

    def __init__(self, model_path: str = None, profile_path: str = None):
        """
        Initialize typing anomaly detector

        Args:
            model_path: Path to TensorFlow Lite model
            profile_path: Path to user typing profile JSON
        """
        self.model_path = model_path or "/opt/qwamos/keyboard/ml/models/typing_model.tflite"
        self.profile_path = profile_path or "/opt/qwamos/keyboard/config/typing_profile.json"

        # Initialize ML model
        try:
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
            self.ml_enabled = True
            print(f"[ML] Model loaded: {self.model_path}", file=sys.stderr)
        except Exception as e:
            print(f"[ML] Model loading failed: {e}. Using rule-based detection.", file=sys.stderr)
            self.ml_enabled = False

        # Load user typing profile
        self.user_profile = self._load_user_profile()

        # Keystroke buffer (last 10 keystrokes for analysis)
        self.keystroke_buffer = deque(maxlen=10)

        # Feature statistics for learning
        self.feature_history = {
            'press_durations': deque(maxlen=100),
            'inter_key_times': deque(maxlen=100),
            'pressures': deque(maxlen=100),
            'touch_areas': deque(maxlen=100)
        }

        # Anomaly threshold (0-1 scale)
        self.anomaly_threshold = 0.30  # 30% deviation = anomaly

        print(f"[ML] Typing anomaly detector initialized", file=sys.stderr)
        print(f"[ML] Profile samples: {self.user_profile.get('samples', 0)}", file=sys.stderr)
        print(f"[ML] Anomaly threshold: {self.anomaly_threshold}", file=sys.stderr)

    def _load_user_profile(self) -> dict:
        """Load user typing profile from JSON"""
        try:
            profile_file = Path(self.profile_path)
            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    profile = json.load(f)
                    return profile
            else:
                # Create default profile
                return {
                    'mean': [0.12, 0.15, 0.5, 150.0],  # Default typing stats
                    'std': [0.05, 0.08, 0.2, 50.0],
                    'samples': 0,
                    'last_updated': time.time()
                }
        except Exception as e:
            print(f"[ML] Failed to load profile: {e}", file=sys.stderr)
            return {
                'mean': [0.12, 0.15, 0.5, 150.0],
                'std': [0.05, 0.08, 0.2, 50.0],
                'samples': 0,
                'last_updated': time.time()
            }

    def _save_user_profile(self):
        """Save updated user typing profile"""
        try:
            # Update profile statistics
            self.user_profile['samples'] = len(self.feature_history['press_durations'])
            self.user_profile['last_updated'] = time.time()

            # Calculate mean and std from feature history
            if self.user_profile['samples'] > 10:
                self.user_profile['mean'] = [
                    float(np.mean(self.feature_history['press_durations'])),
                    float(np.mean(self.feature_history['inter_key_times'])),
                    float(np.mean(self.feature_history['pressures'])),
                    float(np.mean(self.feature_history['touch_areas']))
                ]

                self.user_profile['std'] = [
                    float(np.std(self.feature_history['press_durations'])),
                    float(np.std(self.feature_history['inter_key_times'])),
                    float(np.std(self.feature_history['pressures'])),
                    float(np.std(self.feature_history['touch_areas']))
                ]

            # Save to file
            Path(self.profile_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.profile_path, 'w') as f:
                json.dump(self.user_profile, f, indent=2)

            print(f"[ML] Profile saved ({self.user_profile['samples']} samples)", file=sys.stderr)
        except Exception as e:
            print(f"[ML] Failed to save profile: {e}", file=sys.stderr)

    def extract_features(self, keystroke_data: dict) -> np.ndarray:
        """
        Extract typing dynamics features from keystroke

        Features:
        - Press duration (seconds)
        - Inter-key time (seconds)
        - Pressure (0-1 scale)
        - Touch area (pixels)

        Args:
            keystroke_data: Dict with press_duration, release_time, pressure, touch_area

        Returns:
            Feature vector (4 dimensions)
        """
        features = np.zeros(4, dtype=np.float32)

        # Feature 0: Press duration
        features[0] = keystroke_data.get('press_duration', 0.1)

        # Feature 1: Inter-key time (time since last keystroke)
        if len(self.keystroke_buffer) > 0:
            last_keystroke = self.keystroke_buffer[-1]
            inter_key_time = keystroke_data['release_time'] - last_keystroke['release_time']
            features[1] = inter_key_time / 1000.0  # Convert ms to seconds
        else:
            features[1] = 0.15  # Default

        # Feature 2: Pressure
        features[2] = keystroke_data.get('pressure', 0.5)

        # Feature 3: Touch area
        features[3] = keystroke_data.get('touch_area', 150.0)

        return features

    def detect_anomaly(self, keystroke_data: dict) -> tuple:
        """
        Detect typing anomaly

        Args:
            keystroke_data: Dict with typing dynamics data

        Returns:
            (is_anomaly: bool, confidence: float)
        """
        # Extract features
        features = self.extract_features(keystroke_data)

        # Add to buffer
        self.keystroke_buffer.append(keystroke_data)

        # Update feature history
        self.feature_history['press_durations'].append(features[0])
        if features[1] > 0:  # Only add valid inter-key times
            self.feature_history['inter_key_times'].append(features[1])
        self.feature_history['pressures'].append(features[2])
        self.feature_history['touch_areas'].append(features[3])

        # Need at least 10 keystrokes to analyze
        if len(self.keystroke_buffer) < 10:
            return False, 0.0

        # Use ML model if available
        if self.ml_enabled:
            is_anomaly, confidence = self._ml_classify(features)
        else:
            is_anomaly, confidence = self._rule_based_classify(features)

        # Save profile periodically (every 50 keystrokes)
        if len(self.keystroke_buffer) >= 10 and len(self.feature_history['press_durations']) % 50 == 0:
            self._save_user_profile()

        return is_anomaly, confidence

    def _ml_classify(self, features: np.ndarray) -> tuple:
        """
        ML-based anomaly classification

        Args:
            features: Feature vector

        Returns:
            (is_anomaly: bool, confidence: float)
        """
        try:
            # Normalize features
            mean = np.array(self.user_profile['mean'])
            std = np.array(self.user_profile['std'])
            features_norm = (features - mean) / (std + 1e-6)

            # Run inference
            input_details = self.interpreter.get_input_details()
            output_details = self.interpreter.get_output_details()

            self.interpreter.set_tensor(
                input_details[0]['index'],
                features_norm.reshape(1, -1).astype(np.float32)
            )

            self.interpreter.invoke()

            prediction = self.interpreter.get_tensor(output_details[0]['index'])[0][0]

            # Threshold: 0.7 = legitimate user
            is_legitimate = prediction > 0.7
            confidence = abs(prediction - 0.7) / 0.3  # 0-1 scale

            return not is_legitimate, confidence

        except Exception as e:
            print(f"[ML] Classification error: {e}", file=sys.stderr)
            return False, 0.0

    def _rule_based_classify(self, features: np.ndarray) -> tuple:
        """
        Rule-based anomaly classification (fallback)

        Detects deviations from user's normal typing patterns

        Args:
            features: Feature vector

        Returns:
            (is_anomaly: bool, confidence: float)
        """
        # Compare to user profile
        mean = np.array(self.user_profile['mean'])
        std = np.array(self.user_profile['std'])

        # Calculate z-scores (standard deviations from mean)
        z_scores = np.abs((features - mean) / (std + 1e-6))

        # Average z-score across all features
        avg_z_score = np.mean(z_scores)

        # Anomaly if deviation > 2 standard deviations (97.5% confidence)
        is_anomaly = avg_z_score > 2.0

        # Confidence based on z-score magnitude
        confidence = min(avg_z_score / 3.0, 1.0)

        if is_anomaly:
            print(f"[ML] Anomaly detected: z-score={avg_z_score:.2f}", file=sys.stderr)

        return is_anomaly, confidence

def main():
    """
    Main loop: Read keystroke data from stdin, output anomaly detection results
    """
    detector = TypingAnomalyDetector()

    print("[ML] Typing anomaly detector ready", file=sys.stderr)
    print("[ML] Waiting for keystroke data on stdin...", file=sys.stderr)

    while True:
        try:
            # Read line from stdin (CSV format)
            line = sys.stdin.readline()
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            # Parse CSV: press_duration,release_time,pressure,touch_area
            parts = line.split(',')
            if len(parts) != 4:
                print(f"[ML] Invalid input: {line}", file=sys.stderr)
                continue

            keystroke_data = {
                'press_duration': float(parts[0]),
                'release_time': float(parts[1]),
                'pressure': float(parts[2]),
                'touch_area': float(parts[3])
            }

            # Detect anomaly
            is_anomaly, confidence = detector.detect_anomaly(keystroke_data)

            # Output result (CSV): is_anomaly,confidence
            print(f"{1 if is_anomaly else 0},{confidence:.4f}")
            sys.stdout.flush()

        except Exception as e:
            print(f"[ML] Error: {e}", file=sys.stderr)
            print("0,0.0")  # No anomaly on error
            sys.stdout.flush()

if __name__ == '__main__':
    main()
