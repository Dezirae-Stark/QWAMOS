/**
 * QWAMOS SecureType Keyboard - Main Component
 *
 * World's first mobile keyboard with:
 * - Hardware-backed per-keystroke encryption
 * - ML-based typing anomaly detection
 * - Zero telemetry guarantee (no INTERNET permission)
 *
 * @module SecureKeyboard
 * @version 1.0.0
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  NativeModules,
  NativeEventEmitter,
  Alert,
  AppState,
  AppStateStatus
} from 'react-native';
import PasswordMode from '../modes/PasswordMode';
import TerminalMode from '../modes/TerminalMode';
import StandardMode from '../modes/StandardMode';
import SecurityIndicator from './SecurityIndicator';
import { KeyboardMode, SecurityLevel, KeystrokeData } from '../types';

const { SecureInputModule, TypingAnomalyModule } = NativeModules;
const eventEmitter = new NativeEventEmitter(TypingAnomalyModule);

interface SecureKeyboardProps {
  mode?: KeyboardMode;
  securityLevel?: SecurityLevel;
  onTextChange: (text: string, encrypted: boolean) => void;
  onAnomalyDetected?: () => void;
  autoSwitchMode?: boolean;
}

const SecureKeyboard: React.FC<SecureKeyboardProps> = ({
  mode = 'STANDARD',
  securityLevel = 'STANDARD',
  onTextChange,
  onAnomalyDetected,
  autoSwitchMode = true
}) => {
  const [currentMode, setCurrentMode] = useState<KeyboardMode>(mode);
  const [currentSecurityLevel, setCurrentSecurityLevel] = useState<SecurityLevel>(securityLevel);
  const [encryptedBuffer, setEncryptedBuffer] = useState<string>('');
  const [isLocked, setIsLocked] = useState<boolean>(false);
  const [mlInitialized, setMlInitialized] = useState<boolean>(false);

  /**
   * Initialize keyboard security on mount
   */
  useEffect(() => {
    initializeSecurity();

    // Listen for typing anomaly events
    const anomalySubscription = eventEmitter.addListener(
      'TypingAnomalyDetected',
      handleTypingAnomaly
    );

    // Listen for app state changes (screen lock)
    const appStateSubscription = AppState.addEventListener(
      'change',
      handleAppStateChange
    );

    return () => {
      cleanupSecurity();
      anomalySubscription.remove();
      appStateSubscription.remove();
    };
  }, []);

  /**
   * Update mode when prop changes
   */
  useEffect(() => {
    if (mode !== currentMode) {
      switchMode(mode);
    }
  }, [mode]);

  /**
   * Initialize hardware security and ML detector
   */
  const initializeSecurity = async () => {
    try {
      // Initialize hardware-backed encryption
      await SecureInputModule.initializeKeystore();

      // Initialize ML typing anomaly detector
      const mlReady = await TypingAnomalyModule.initialize();
      setMlInitialized(mlReady);

      // Load user typing profile
      await TypingAnomalyModule.loadUserProfile();

      console.log('[SecureKeyboard] Security initialized');
    } catch (error) {
      console.error('[SecureKeyboard] Failed to initialize security:', error);
      Alert.alert(
        'Security Initialization Failed',
        'Keyboard will operate in reduced security mode.'
      );
    }
  };

  /**
   * Cleanup security on unmount
   */
  const cleanupSecurity = async () => {
    try {
      // Wipe encrypted buffer
      await SecureInputModule.wipeMemory();

      // Disable FLAG_SECURE
      if (currentMode === 'PASSWORD') {
        await SecureInputModule.setSecureFlag(false);
      }

      console.log('[SecureKeyboard] Security cleaned up');
    } catch (error) {
      console.error('[SecureKeyboard] Cleanup error:', error);
    }
  };

  /**
   * Handle app state changes (lock screen)
   */
  const handleAppStateChange = async (nextAppState: AppStateStatus) => {
    if (nextAppState === 'background' || nextAppState === 'inactive') {
      // Screen locked or app backgrounded - wipe buffer
      await SecureInputModule.wipeMemory();
      setEncryptedBuffer('');
      onTextChange('', false);
    }
  };

  /**
   * Handle typing anomaly detection
   */
  const handleTypingAnomaly = async (event: any) => {
    const { confidence, features } = event;

    console.warn('[SecureKeyboard] Typing anomaly detected:', confidence);

    // Lock keyboard
    setIsLocked(true);

    // Alert user
    Alert.alert(
      '🔒 Security Alert',
      `Unauthorized typing pattern detected (${Math.round(confidence * 100)}% confidence).\n\nKeyboard has been locked. Please authenticate to continue.`,
      [
        {
          text: 'Authenticate',
          onPress: handleAuthentication
        }
      ],
      { cancelable: false }
    );

    // Notify parent component
    if (onAnomalyDetected) {
      onAnomalyDetected();
    }

    // Log security event
    await SecureInputModule.logSecurityEvent('TYPING_ANOMALY_DETECTED', {
      confidence,
      features,
      timestamp: Date.now()
    });
  };

  /**
   * Handle re-authentication after anomaly
   */
  const handleAuthentication = async () => {
    try {
      // Request biometric authentication
      const authenticated = await SecureInputModule.authenticateUser();

      if (authenticated) {
        // Reset ML profile learning
        await TypingAnomalyModule.resetProfile();
        setIsLocked(false);

        Alert.alert('✅ Authentication Successful', 'Keyboard unlocked.');
      } else {
        Alert.alert('❌ Authentication Failed', 'Keyboard remains locked.');
      }
    } catch (error) {
      console.error('[SecureKeyboard] Authentication error:', error);
    }
  };

  /**
   * Switch keyboard mode
   */
  const switchMode = async (newMode: KeyboardMode) => {
    // Wipe buffer when switching modes
    await SecureInputModule.wipeMemory();
    setEncryptedBuffer('');

    // Update FLAG_SECURE based on mode
    if (newMode === 'PASSWORD') {
      await SecureInputModule.setSecureFlag(true);
    } else if (currentMode === 'PASSWORD') {
      await SecureInputModule.setSecureFlag(false);
    }

    setCurrentMode(newMode);
    onTextChange('', false);
  };

  /**
   * Handle keystroke input
   */
  const handleKeystroke = useCallback(async (keystrokeData: KeystrokeData) => {
    if (isLocked) {
      return; // Keyboard locked due to anomaly
    }

    const { key, pressTime, releaseTime, pressure, touchArea, touchX, touchY } = keystrokeData;

    try {
      // Analyze keystroke with ML detector (if in high security mode)
      if (mlInitialized && (currentSecurityLevel === 'HIGH' || currentSecurityLevel === 'PARANOID')) {
        await TypingAnomalyModule.analyzeKeystroke({
          key,
          press_duration: releaseTime - pressTime,
          release_time: releaseTime,
          pressure,
          touch_area: touchArea
        });
      }

      // Encrypt keystroke in hardware (if in password or paranoid mode)
      let processedKey = key;
      if (currentMode === 'PASSWORD' || currentSecurityLevel === 'PARANOID') {
        processedKey = await SecureInputModule.encryptKeystroke(key);
      }

      // Update buffer
      const newBuffer = encryptedBuffer + processedKey;
      setEncryptedBuffer(newBuffer);

      // Notify parent
      const isEncrypted = currentMode === 'PASSWORD' || currentSecurityLevel === 'PARANOID';
      onTextChange(newBuffer, isEncrypted);

      // Haptic feedback
      await SecureInputModule.hapticFeedback('light');

    } catch (error) {
      console.error('[SecureKeyboard] Keystroke processing error:', error);
    }
  }, [isLocked, mlInitialized, currentSecurityLevel, currentMode, encryptedBuffer]);

  /**
   * Handle backspace
   */
  const handleBackspace = useCallback(async () => {
    if (isLocked) {
      return;
    }

    const newBuffer = encryptedBuffer.slice(0, -1);
    setEncryptedBuffer(newBuffer);

    const isEncrypted = currentMode === 'PASSWORD' || currentSecurityLevel === 'PARANOID';
    onTextChange(newBuffer, isEncrypted);

    await SecureInputModule.hapticFeedback('medium');
  }, [isLocked, encryptedBuffer, currentMode, currentSecurityLevel]);

  /**
   * Render appropriate keyboard mode
   */
  const renderKeyboardMode = () => {
    const commonProps = {
      onKeystroke: handleKeystroke,
      onBackspace: handleBackspace,
      securityLevel: currentSecurityLevel,
      isLocked
    };

    switch (currentMode) {
      case 'PASSWORD':
        return <PasswordMode {...commonProps} />;

      case 'TERMINAL':
        return <TerminalMode {...commonProps} />;

      case 'STANDARD':
      default:
        return <StandardMode {...commonProps} />;
    }
  };

  return (
    <View style={styles.container}>
      {/* Security indicator */}
      <SecurityIndicator
        mode={currentMode}
        securityLevel={currentSecurityLevel}
        isLocked={isLocked}
        mlEnabled={mlInitialized}
      />

      {/* Keyboard mode UI */}
      <View style={styles.keyboardContainer}>
        {renderKeyboardMode()}
      </View>

      {/* Mode switcher */}
      {!isLocked && (
        <View style={styles.modeSwitcher}>
          <Text style={styles.currentMode}>
            Mode: {currentMode} | Security: {currentSecurityLevel}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    backgroundColor: '#1a1a1a',
    paddingBottom: 10
  },
  keyboardContainer: {
    minHeight: 250
  },
  modeSwitcher: {
    padding: 8,
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#333'
  },
  currentMode: {
    color: '#999',
    fontSize: 12,
    fontFamily: 'monospace'
  }
});

export default SecureKeyboard;
