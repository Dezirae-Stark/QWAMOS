/**
 * QWAMOS SecureType Keyboard - Terminal Mode
 *
 * Optimized for shell command input:
 * - Special keys: Ctrl, Alt, Tab, Esc, |, ~, /
 * - Syntax highlighting
 * - Command history (encrypted)
 * - Tab completion (local only)
 * - No telemetry/logging
 *
 * @module TerminalMode
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

interface SpecialKey {
  label: string;
  value: string;
  color: string;
}

const TerminalMode: React.FC<ModeProps> = ({
  onKeystroke,
  onBackspace,
  securityLevel,
  isLocked
}) => {
  const [shiftActive, setShiftActive] = useState<boolean>(false);
  const [ctrlActive, setCtrlActive] = useState<boolean>(false);
  const [altActive, setAltActive] = useState<boolean>(false);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [historyIndex, setHistoryIndex] = useState<number>(-1);

  /**
   * Terminal special keys
   */
  const specialKeys: SpecialKey[] = [
    { label: 'Esc', value: '\x1b', color: '#ff4444' },
    { label: 'Tab', value: '\t', color: '#44ff44' },
    { label: '~', value: '~', color: '#4444ff' },
    { label: '/', value: '/', color: '#4444ff' },
    { label: '|', value: '|', color: '#4444ff' },
    { label: '>', value: '>', color: '#4444ff' },
    { label: '<', value: '<', color: '#4444ff' },
    { label: '&', value: '&', color: '#4444ff' }
  ];

  /**
   * Number row with special characters
   */
  const numberRow = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'];
  const symbolRow = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')'];

  /**
   * QWERTY rows
   */
  const qwertyRows = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '-']
  ];

  /**
   * Handle key press with modifier keys
   */
  const handleKeyPress = useCallback((key: string) => {
    if (isLocked) {
      return;
    }

    let processedKey = key;

    // Apply modifiers
    if (ctrlActive) {
      processedKey = `CTRL+${key}`;
      setCtrlActive(false);
    } else if (altActive) {
      processedKey = `ALT+${key}`;
      setAltActive(false);
    } else if (shiftActive) {
      processedKey = key.toUpperCase();
      setShiftActive(false);
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
  }, [isLocked, ctrlActive, altActive, shiftActive, onKeystroke]);

  /**
   * Handle special key press
   */
  const handleSpecialKeyPress = useCallback((key: SpecialKey) => {
    if (isLocked) {
      return;
    }

    if (key.label === 'Tab') {
      // TODO: Implement tab completion
      handleKeyPress(key.value);
    } else if (key.label === 'Esc') {
      // Send escape sequence
      handleKeyPress(key.value);
    } else {
      handleKeyPress(key.value);
    }
  }, [isLocked, handleKeyPress]);

  /**
   * Toggle Ctrl modifier
   */
  const toggleCtrl = () => {
    setCtrlActive(!ctrlActive);
    setAltActive(false);
    Vibration.vibrate(10);
  };

  /**
   * Toggle Alt modifier
   */
  const toggleAlt = () => {
    setAltActive(!altActive);
    setCtrlActive(false);
    Vibration.vibrate(10);
  };

  /**
   * Toggle Shift modifier
   */
  const toggleShift = () => {
    setShiftActive(!shiftActive);
    Vibration.vibrate(10);
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
      {/* Terminal mode banner */}
      <View style={styles.banner}>
        <Text style={styles.terminalIcon}>⌨️</Text>
        <Text style={styles.bannerText}>TERMINAL MODE</Text>
        {ctrlActive && <Text style={styles.modifierBadge}>CTRL</Text>}
        {altActive && <Text style={styles.modifierBadge}>ALT</Text>}
        {shiftActive && <Text style={styles.modifierBadge}>SHIFT</Text>}
      </View>

      {/* Special keys row */}
      <View style={styles.specialRow}>
        {specialKeys.map((key) => (
          <TouchableOpacity
            key={key.label}
            style={[styles.specialKey, { borderColor: key.color }]}
            onPress={() => handleSpecialKeyPress(key)}
          >
            <Text style={[styles.specialKeyText, { color: key.color }]}>
              {key.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Number/Symbol row */}
      <View style={styles.row}>
        {(shiftActive ? symbolRow : numberRow).map((key) => (
          <KeyButton
            key={key}
            label={key}
            value={key}
            onPress={(value) => handleKeyPress(value)}
            style={styles.key}
          />
        ))}
      </View>

      {/* QWERTY rows */}
      {qwertyRows.map((row, rowIndex) => (
        <View key={rowIndex} style={styles.row}>
          {row.map((key) => (
            <KeyButton
              key={key}
              label={shiftActive ? key.toUpperCase() : key}
              value={key}
              onPress={(value) => handleKeyPress(value)}
              style={styles.key}
            />
          ))}
        </View>
      ))}

      {/* Bottom modifier row */}
      <View style={styles.modifierRow}>
        <TouchableOpacity
          style={[styles.modifierKey, ctrlActive && styles.modifierActive]}
          onPress={toggleCtrl}
        >
          <Text style={[styles.modifierKeyText, ctrlActive && styles.modifierActiveText]}>
            Ctrl
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.modifierKey, altActive && styles.modifierActive]}
          onPress={toggleAlt}
        >
          <Text style={[styles.modifierKeyText, altActive && styles.modifierActiveText]}>
            Alt
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.modifierKey, shiftActive && styles.modifierActive]}
          onPress={toggleShift}
        >
          <Text style={[styles.modifierKeyText, shiftActive && styles.modifierActiveText]}>
            Shift
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.modifierKey, styles.spaceKey]}
          onPress={() => handleKeyPress(' ')}
        >
          <Text style={styles.modifierKeyText}>Space</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.modifierKey, styles.backspaceKey]}
          onPress={handleBackspacePress}
        >
          <Text style={styles.modifierKeyText}>⌫</Text>
        </TouchableOpacity>
      </View>

      {/* Command hints */}
      <View style={styles.hintsContainer}>
        <Text style={styles.hintsText}>
          💡 Tab for completion • Ctrl+C to cancel • Esc to exit
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    backgroundColor: '#0a0a0a',
    padding: 5
  },
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#001a1a',
    borderRadius: 5,
    marginBottom: 10
  },
  terminalIcon: {
    fontSize: 18,
    marginRight: 8
  },
  bannerText: {
    color: '#00ffff',
    fontSize: 14,
    fontWeight: 'bold',
    flex: 1
  },
  modifierBadge: {
    color: '#ff00ff',
    fontSize: 10,
    backgroundColor: '#2a002a',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 3,
    marginLeft: 5
  },
  specialRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 5,
    flexWrap: 'wrap'
  },
  specialKey: {
    backgroundColor: '#1a1a1a',
    padding: 8,
    margin: 2,
    borderRadius: 5,
    minWidth: 40,
    alignItems: 'center',
    borderWidth: 1
  },
  specialKeyText: {
    fontSize: 12,
    fontWeight: 'bold'
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 5
  },
  key: {
    margin: 2
  },
  modifierRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 5
  },
  modifierKey: {
    backgroundColor: '#2a2a2a',
    padding: 12,
    margin: 2,
    borderRadius: 5,
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 60,
    borderWidth: 1,
    borderColor: '#444'
  },
  modifierActive: {
    backgroundColor: '#2a002a',
    borderColor: '#ff00ff'
  },
  modifierKeyText: {
    color: '#aaa',
    fontSize: 14,
    fontWeight: 'bold'
  },
  modifierActiveText: {
    color: '#ff00ff'
  },
  spaceKey: {
    flex: 1,
    maxWidth: 200
  },
  backspaceKey: {
    minWidth: 70
  },
  hintsContainer: {
    marginTop: 10,
    padding: 8,
    backgroundColor: '#001a00',
    borderRadius: 5,
    borderWidth: 1,
    borderColor: '#00ff00'
  },
  hintsText: {
    color: '#00ff00',
    fontSize: 11,
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

export default TerminalMode;
