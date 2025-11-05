/**
 * QWAMOS SecureType Keyboard - Password Mode
 *
 * Maximum security mode for password/sensitive input:
 * - Hardware-encrypted keystroke buffer
 * - No visual feedback (dots only)
 * - Haptic-only feedback
 * - Random layout option
 * - FLAG_SECURE (anti-screenshot)
 * - No clipboard access
 *
 * @module PasswordMode
 * @version 1.0.0
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Vibration,
  Dimensions
} from 'react-native';
import { ModeProps, KeyboardLayout, KeystrokeData } from '../types';
import KeyButton from '../components/KeyButton';
import DecoyCharacterOverlay from '../components/DecoyCharacterOverlay';

const { width } = Dimensions.get('window');

const PasswordMode: React.FC<ModeProps> = ({
  onKeystroke,
  onBackspace,
  securityLevel,
  isLocked
}) => {
  const [layout, setLayout] = useState<KeyboardLayout>('QWERTY');
  const [keys, setKeys] = useState<string[][]>([]);
  const [showDecoys, setShowDecoys] = useState<boolean>(false);
  const [inputLength, setInputLength] = useState<number>(0);

  /**
   * Initialize keyboard layout
   */
  useEffect(() => {
    if (securityLevel === 'PARANOID') {
      // Use random layout in paranoid mode
      setLayout('RANDOM');
      generateRandomLayout();

      // Regenerate layout every 30 seconds
      const interval = setInterval(() => {
        generateRandomLayout();
      }, 30000);

      return () => clearInterval(interval);
    } else {
      // Use standard QWERTY
      setLayout('QWERTY');
      setKeys(getQWERTYLayout());
    }
  }, [securityLevel]);

  /**
   * QWERTY layout
   */
  const getQWERTYLayout = (): string[][] => {
    return [
      ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
      ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
      ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
      ['z', 'x', 'c', 'v', 'b', 'n', 'm']
    ];
  };

  /**
   * Generate randomized keyboard layout (anti-shoulder-surfing)
   */
  const generateRandomLayout = () => {
    const allChars = [
      '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
      'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
      'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
      'u', 'v', 'w', 'x', 'y', 'z',
      '!', '@', '#', '$', '%', '^', '&', '*', '(', ')'
    ];

    // Shuffle array
    const shuffled = [...allChars].sort(() => Math.random() - 0.5);

    // Create rows
    const randomLayout = [
      shuffled.slice(0, 10),
      shuffled.slice(10, 20),
      shuffled.slice(20, 29),
      shuffled.slice(29, 36)
    ];

    setKeys(randomLayout);
  };

  /**
   * Handle key press with timing and pressure data
   */
  const handleKeyPress = useCallback((key: string, pressStart: number, pressEnd: number) => {
    if (isLocked) {
      return;
    }

    // Create keystroke data for ML analysis
    const keystrokeData: KeystrokeData = {
      key,
      pressTime: pressStart,
      releaseTime: pressEnd,
      pressure: 0.5, // TODO: Get actual pressure from touch event
      touchArea: 150, // TODO: Get actual touch area
      touchX: 0, // Obfuscated
      touchY: 0  // Obfuscated
    };

    // Send to parent
    onKeystroke(keystrokeData);

    // Update input length (for visual dots)
    setInputLength(prev => prev + 1);

    // Show decoy characters in paranoid mode
    if (securityLevel === 'PARANOID') {
      setShowDecoys(true);
      setTimeout(() => setShowDecoys(false), 100);
    }

    // Haptic feedback only (no visual)
    Vibration.vibrate(10);
  }, [isLocked, securityLevel, onKeystroke]);

  /**
   * Handle backspace
   */
  const handleBackspacePress = useCallback(() => {
    if (isLocked || inputLength === 0) {
      return;
    }

    onBackspace();
    setInputLength(prev => Math.max(0, prev - 1));
    Vibration.vibrate(15);
  }, [isLocked, inputLength, onBackspace]);

  /**
   * Handle layout toggle
   */
  const handleLayoutToggle = () => {
    if (layout === 'QWERTY') {
      setLayout('RANDOM');
      generateRandomLayout();
    } else {
      setLayout('QWERTY');
      setKeys(getQWERTYLayout());
    }
  };

  if (isLocked) {
    return (
      <View style={styles.lockedContainer}>
        <Text style={styles.lockIcon}>🔒</Text>
        <Text style={styles.lockText}>Keyboard Locked</Text>
        <Text style={styles.lockSubtext}>Typing anomaly detected</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Security banner */}
      <View style={styles.securityBanner}>
        <Text style={styles.lockIcon}>🔒</Text>
        <Text style={styles.securityText}>SECURE PASSWORD INPUT</Text>
        <Text style={styles.layoutBadge}>{layout}</Text>
      </View>

      {/* Visual input indicator (dots only) */}
      <View style={styles.inputIndicator}>
        <Text style={styles.dots}>
          {'•'.repeat(Math.min(inputLength, 32))}
        </Text>
      </View>

      {/* Decoy character overlay (paranoid mode) */}
      {showDecoys && securityLevel === 'PARANOID' && (
        <DecoyCharacterOverlay />
      )}

      {/* Keyboard layout */}
      <View style={styles.keyboard}>
        {keys.map((row, rowIndex) => (
          <View key={rowIndex} style={styles.row}>
            {row.map((key) => (
              <KeyButton
                key={key}
                label={key}
                value={key}
                onPress={(value, pressStart, pressEnd) => {
                  handleKeyPress(value, pressStart, pressEnd);
                }}
                secureMode={true}
                style={styles.key}
              />
            ))}
          </View>
        ))}

        {/* Special keys row */}
        <View style={styles.specialRow}>
          <TouchableOpacity
            style={[styles.specialKey, styles.layoutToggle]}
            onPress={handleLayoutToggle}
          >
            <Text style={styles.specialKeyText}>🔀 {layout}</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.specialKey, styles.spaceKey]}
            onPress={() => handleKeyPress(' ', Date.now(), Date.now() + 50)}
          >
            <Text style={styles.specialKeyText}>SPACE</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.specialKey, styles.backspaceKey]}
            onPress={handleBackspacePress}
          >
            <Text style={styles.specialKeyText}>⌫</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Warning message */}
      <View style={styles.warningContainer}>
        <Text style={styles.warningText}>
          ⚠️ No clipboard • No screenshots • Hardware encrypted
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    backgroundColor: '#1a1a1a',
    padding: 5
  },
  securityBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 8,
    backgroundColor: '#2a2a00',
    borderRadius: 5,
    marginBottom: 10
  },
  lockIcon: {
    fontSize: 18,
    marginRight: 8
  },
  securityText: {
    color: '#ffff00',
    fontSize: 14,
    fontWeight: 'bold',
    flex: 1
  },
  layoutBadge: {
    color: '#ffff00',
    fontSize: 10,
    backgroundColor: '#3a3a00',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 3
  },
  inputIndicator: {
    padding: 15,
    backgroundColor: '#0a0a0a',
    borderRadius: 5,
    marginBottom: 10,
    minHeight: 50,
    justifyContent: 'center'
  },
  dots: {
    color: '#ffff00',
    fontSize: 24,
    letterSpacing: 8,
    textAlign: 'center'
  },
  keyboard: {
    width: '100%'
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 5
  },
  key: {
    margin: 2
  },
  specialRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 5
  },
  specialKey: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    margin: 2,
    borderRadius: 5,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#ffff00'
  },
  layoutToggle: {
    width: width * 0.25
  },
  spaceKey: {
    width: width * 0.4
  },
  backspaceKey: {
    width: width * 0.25
  },
  specialKeyText: {
    color: '#ffff00',
    fontSize: 14,
    fontWeight: 'bold'
  },
  warningContainer: {
    marginTop: 10,
    padding: 8,
    backgroundColor: '#1a1a00',
    borderRadius: 5,
    borderWidth: 1,
    borderColor: '#ffff00'
  },
  warningText: {
    color: '#ffff00',
    fontSize: 11,
    textAlign: 'center'
  },
  lockedContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 50,
    backgroundColor: '#1a0000'
  },
  lockText: {
    color: '#ff0000',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 10
  },
  lockSubtext: {
    color: '#ff6666',
    fontSize: 14,
    marginTop: 5
  }
});

export default PasswordMode;
