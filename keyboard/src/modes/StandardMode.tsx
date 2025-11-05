/**
 * QWAMOS SecureType Keyboard - Standard Mode
 *
 * Regular typing with hardware encryption:
 * - QWERTY layout
 * - Visual feedback
 * - Hardware-encrypted buffer
 * - ML typing analysis (optional)
 *
 * @module StandardMode
 * @version 1.0.0
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Vibration,
  Dimensions
} from 'react-native';
import { ModeProps, KeystrokeData } from '../types';
import KeyButton from '../components/KeyButton';

const { width } = Dimensions.get('window');

const StandardMode: React.FC<ModeProps> = ({
  onKeystroke,
  onBackspace,
  securityLevel,
  isLocked
}) => {
  const [shiftActive, setShiftActive] = useState<boolean>(false);
  const [capsLock, setCapsLock] = useState<boolean>(false);

  /**
   * QWERTY layout
   */
  const numberRow = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'];
  const topRow = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'];
  const middleRow = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'];
  const bottomRow = ['z', 'x', 'c', 'v', 'b', 'n', 'm'];

  /**
   * Handle key press
   */
  const handleKeyPress = useCallback((key: string) => {
    if (isLocked) {
      return;
    }

    let processedKey = key;

    // Apply shift/caps lock
    if (shiftActive || capsLock) {
      processedKey = key.toUpperCase();
      if (shiftActive) {
        setShiftActive(false);
      }
    }

    // Create keystroke data
    const keystrokeData: KeystrokeData = {
      key: processedKey,
      pressTime: Date.now(),
      releaseTime: Date.now() + 50,
      pressure: 0.5,
      touchArea: 150,
      touchX: 0,
      touchY: 0
    };

    onKeystroke(keystrokeData);
    Vibration.vibrate(5);
  }, [isLocked, shiftActive, capsLock, onKeystroke]);

  /**
   * Toggle shift
   */
  const toggleShift = () => {
    setShiftActive(!shiftActive);
    Vibration.vibrate(10);
  };

  /**
   * Handle double-tap for caps lock
   */
  const handleShiftDoubleTap = () => {
    setCapsLock(!capsLock);
    setShiftActive(false);
    Vibration.vibrate(15);
  };

  /**
   * Handle backspace
   */
  const handleBackspacePress = useCallback(() => {
    if (isLocked) {
      return;
    }

    onBackspace();
    Vibration.vibrate(15);
  }, [isLocked, onBackspace]);

  if (isLocked) {
    return (
      <View style={styles.lockedContainer}>
        <Text style={styles.lockIcon}>🔒</Text>
        <Text style={styles.lockText}>Keyboard Locked</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Mode banner */}
      <View style={styles.banner}>
        <Text style={styles.bannerText}>Standard Mode</Text>
        {securityLevel !== 'STANDARD' && (
          <Text style={styles.securityBadge}>
            🔐 {securityLevel}
          </Text>
        )}
        {capsLock && <Text style={styles.capsLockBadge}>CAPS</Text>}
      </View>

      {/* Number row */}
      <View style={styles.row}>
        {numberRow.map((key) => (
          <KeyButton
            key={key}
            label={key}
            value={key}
            onPress={(value) => handleKeyPress(value)}
            style={styles.key}
          />
        ))}
      </View>

      {/* Top row */}
      <View style={styles.row}>
        {topRow.map((key) => (
          <KeyButton
            key={key}
            label={shiftActive || capsLock ? key.toUpperCase() : key}
            value={key}
            onPress={(value) => handleKeyPress(value)}
            style={styles.key}
          />
        ))}
      </View>

      {/* Middle row */}
      <View style={styles.row}>
        {middleRow.map((key) => (
          <KeyButton
            key={key}
            label={shiftActive || capsLock ? key.toUpperCase() : key}
            value={key}
            onPress={(value) => handleKeyPress(value)}
            style={styles.key}
          />
        ))}
      </View>

      {/* Bottom row */}
      <View style={styles.row}>
        <TouchableOpacity
          style={[styles.shiftKey, (shiftActive || capsLock) && styles.shiftActive]}
          onPress={toggleShift}
          onLongPress={handleShiftDoubleTap}
        >
          <Text style={[styles.shiftText, (shiftActive || capsLock) && styles.shiftActiveText]}>
            ⇧
          </Text>
        </TouchableOpacity>

        {bottomRow.map((key) => (
          <KeyButton
            key={key}
            label={shiftActive || capsLock ? key.toUpperCase() : key}
            value={key}
            onPress={(value) => handleKeyPress(value)}
            style={styles.key}
          />
        ))}

        <TouchableOpacity
          style={styles.backspaceKey}
          onPress={handleBackspacePress}
        >
          <Text style={styles.backspaceText}>⌫</Text>
        </TouchableOpacity>
      </View>

      {/* Space row */}
      <View style={styles.spaceRow}>
        <TouchableOpacity
          style={styles.commaKey}
          onPress={() => handleKeyPress(',')}
        >
          <Text style={styles.commaText}>,</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.spaceKey}
          onPress={() => handleKeyPress(' ')}
        >
          <Text style={styles.spaceText}>SPACE</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.periodKey}
          onPress={() => handleKeyPress('.')}
        >
          <Text style={styles.periodText}>.</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.returnKey}
          onPress={() => handleKeyPress('\n')}
        >
          <Text style={styles.returnText}>↵</Text>
        </TouchableOpacity>
      </View>

      {/* Privacy indicator */}
      {securityLevel !== 'STANDARD' && (
        <View style={styles.privacyIndicator}>
          <Text style={styles.privacyText}>
            🔐 Hardware encrypted • ML monitoring active
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
    padding: 5
  },
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#2a2a2a',
    borderRadius: 5,
    marginBottom: 10
  },
  bannerText: {
    color: '#ffffff',
    fontSize: 14,
    flex: 1
  },
  securityBadge: {
    color: '#00ff00',
    fontSize: 10,
    backgroundColor: '#002200',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 3,
    marginLeft: 5
  },
  capsLockBadge: {
    color: '#ff9900',
    fontSize: 10,
    backgroundColor: '#2a1a00',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 3,
    marginLeft: 5
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 5
  },
  key: {
    margin: 2
  },
  shiftKey: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    margin: 2,
    borderRadius: 5,
    width: 50,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#444'
  },
  shiftActive: {
    backgroundColor: '#2a4a2a',
    borderColor: '#00ff00'
  },
  shiftText: {
    color: '#aaa',
    fontSize: 18,
    fontWeight: 'bold'
  },
  shiftActiveText: {
    color: '#00ff00'
  },
  backspaceKey: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    margin: 2,
    borderRadius: 5,
    width: 50,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#444'
  },
  backspaceText: {
    color: '#ff6666',
    fontSize: 18,
    fontWeight: 'bold'
  },
  spaceRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 5
  },
  commaKey: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    margin: 2,
    borderRadius: 5,
    width: 50,
    alignItems: 'center',
    justifyContent: 'center'
  },
  commaText: {
    color: '#ffffff',
    fontSize: 18
  },
  spaceKey: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    margin: 2,
    borderRadius: 5,
    flex: 1,
    maxWidth: 200,
    alignItems: 'center',
    justifyContent: 'center'
  },
  spaceText: {
    color: '#ffffff',
    fontSize: 14
  },
  periodKey: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    margin: 2,
    borderRadius: 5,
    width: 50,
    alignItems: 'center',
    justifyContent: 'center'
  },
  periodText: {
    color: '#ffffff',
    fontSize: 18
  },
  returnKey: {
    backgroundColor: '#2a4a2a',
    padding: 12,
    margin: 2,
    borderRadius: 5,
    width: 60,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#00ff00'
  },
  returnText: {
    color: '#00ff00',
    fontSize: 18,
    fontWeight: 'bold'
  },
  privacyIndicator: {
    marginTop: 10,
    padding: 6,
    backgroundColor: '#001a00',
    borderRadius: 5
  },
  privacyText: {
    color: '#00ff00',
    fontSize: 10,
    textAlign: 'center'
  },
  lockedContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 50,
    backgroundColor: '#1a0000'
  },
  lockIcon: {
    fontSize: 48
  },
  lockText: {
    color: '#ff0000',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 10
  }
});

export default StandardMode;
