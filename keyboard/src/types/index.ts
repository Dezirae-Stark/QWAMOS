/**
 * QWAMOS SecureType Keyboard - Type Definitions
 *
 * @module types
 * @version 1.0.0
 */

/**
 * Keyboard operating modes
 */
export type KeyboardMode = 'STANDARD' | 'PASSWORD' | 'TERMINAL' | 'GESTURE';

/**
 * Security levels
 */
export type SecurityLevel = 'STANDARD' | 'HIGH' | 'PARANOID';

/**
 * Layout types
 */
export type KeyboardLayout = 'QWERTY' | 'AZERTY' | 'DVORAK' | 'TERMINAL' | 'RANDOM';

/**
 * Keystroke data for ML analysis
 */
export interface KeystrokeData {
  key: string;
  pressTime: number;
  releaseTime: number;
  pressure: number;
  touchArea: number;
  touchX: number;
  touchY: number;
}

/**
 * Typing dynamics features for ML
 */
export interface TypingFeatures {
  press_duration: number;
  release_time: number;
  pressure: number;
  touch_area: number;
  inter_key_time?: number;
}

/**
 * ML anomaly detection result
 */
export interface AnomalyDetectionResult {
  is_anomaly: boolean;
  confidence: number;
  features: TypingFeatures;
  timestamp: number;
}

/**
 * User typing profile
 */
export interface TypingProfile {
  mean: number[];
  std: number[];
  samples: number;
  last_updated: number;
}

/**
 * Security event log entry
 */
export interface SecurityEvent {
  event_type: 'TYPING_ANOMALY_DETECTED' | 'BUFFER_WIPED' | 'MODE_SWITCHED' | 'AUTHENTICATION_FAILED';
  data: any;
  timestamp: number;
}

/**
 * Keyboard configuration
 */
export interface KeyboardConfig {
  mode: KeyboardMode;
  security_level: SecurityLevel;
  layout: KeyboardLayout;
  enable_ml_detection: boolean;
  enable_haptic: boolean;
  enable_decoy_chars: boolean;
  random_layout_interval: number; // seconds
  anomaly_threshold: number; // 0-1
}

/**
 * Key button properties
 */
export interface KeyButtonProps {
  label: string;
  value: string;
  onPress: (value: string) => void;
  onPressStart?: (timestamp: number) => void;
  onPressEnd?: (timestamp: number) => void;
  style?: any;
  secureMode?: boolean;
  width?: number | string;
  isSpecialKey?: boolean;
}

/**
 * Mode-specific props
 */
export interface ModeProps {
  onKeystroke: (data: KeystrokeData) => void;
  onBackspace: () => void;
  securityLevel: SecurityLevel;
  isLocked: boolean;
}

/**
 * Security indicator props
 */
export interface SecurityIndicatorProps {
  mode: KeyboardMode;
  securityLevel: SecurityLevel;
  isLocked: boolean;
  mlEnabled: boolean;
}

/**
 * Native module interfaces
 */
export interface SecureInputModuleInterface {
  initializeKeystore(): Promise<void>;
  setSecureFlag(secure: boolean): Promise<void>;
  encryptKeystroke(key: string): Promise<string>;
  wipeMemory(): Promise<void>;
  hapticFeedback(intensity: 'light' | 'medium' | 'heavy'): Promise<void>;
  authenticateUser(): Promise<boolean>;
  logSecurityEvent(event_type: string, data: any): Promise<void>;
}

export interface TypingAnomalyModuleInterface {
  initialize(): Promise<boolean>;
  loadUserProfile(): Promise<TypingProfile | null>;
  saveUserProfile(profile: TypingProfile): Promise<void>;
  analyzeKeystroke(features: TypingFeatures): Promise<AnomalyDetectionResult>;
  resetProfile(): Promise<void>;
}

/**
 * Decoy character configuration
 */
export interface DecoyCharConfig {
  enabled: boolean;
  count: number;
  duration: number; // ms
  opacity: number; // 0-1
}

/**
 * Touch obfuscation settings
 */
export interface TouchObfuscation {
  enabled: boolean;
  noise_level: number; // pixels
}

/**
 * Keyboard statistics
 */
export interface KeyboardStats {
  total_keystrokes: number;
  anomalies_detected: number;
  mode_switches: number;
  buffer_wipes: number;
  uptime: number; // seconds
}
