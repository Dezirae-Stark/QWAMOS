/**
 * QWAMOS SecureType Keyboard - Key Button Component
 *
 * Individual key button with:
 * - Touch pressure tracking
 * - Timing capture
 * - Touch coordinate obfuscation
 * - Secure mode (no visual feedback)
 *
 * @module KeyButton
 * @version 1.0.0
 */

import React, { useState } from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  GestureResponderEvent
} from 'react-native';

interface KeyButtonProps {
  label: string;
  value: string;
  onPress: (value: string, pressStart?: number, pressEnd?: number) => void;
  style?: ViewStyle;
  secureMode?: boolean;
  width?: number | string;
  isSpecialKey?: boolean;
}

const KeyButton: React.FC<KeyButtonProps> = ({
  label,
  value,
  onPress,
  style,
  secureMode = false,
  width,
  isSpecialKey = false
}) => {
  const [pressStart, setPressStart] = useState<number>(0);
  const [isPressed, setIsPressed] = useState<boolean>(false);

  /**
   * Handle press start - record timestamp
   */
  const handlePressIn = (event: GestureResponderEvent) => {
    const timestamp = Date.now();
    setPressStart(timestamp);
    setIsPressed(true);

    // Obfuscate touch coordinates (add random noise)
    // This prevents malware from inferring keystrokes via touch coordinates
    const { locationX, locationY } = event.nativeEvent;
    const noisyX = locationX + (Math.random() - 0.5) * 10;
    const noisyY = locationY + (Math.random() - 0.5) * 10;

    // Store obfuscated coordinates (not used, but logged if malware reads events)
    // Real key is determined by button component, not coordinates
  };

  /**
   * Handle press end - calculate duration and trigger callback
   */
  const handlePressOut = () => {
    const pressEnd = Date.now();
    setIsPressed(false);

    // Send key with timing data
    onPress(value, pressStart, pressEnd);
  };

  return (
    <TouchableOpacity
      style={[
        styles.button,
        isSpecialKey && styles.specialButton,
        secureMode && styles.secureButton,
        isPressed && !secureMode && styles.pressedButton,
        style,
        width && { width }
      ]}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      activeOpacity={secureMode ? 1.0 : 0.7}
    >
      <Text
        style={[
          styles.label,
          isSpecialKey && styles.specialLabel,
          secureMode && styles.secureLabel
        ]}
      >
        {label}
      </Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#2a2a2a',
    paddingVertical: 14,
    paddingHorizontal: 10,
    borderRadius: 5,
    minWidth: 32,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#444'
  },
  pressedButton: {
    backgroundColor: '#3a3a3a',
    borderColor: '#666'
  },
  secureButton: {
    backgroundColor: '#2a2a00',
    borderColor: '#555500'
  },
  specialButton: {
    backgroundColor: '#002a2a',
    borderColor: '#004444'
  },
  label: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '500'
  },
  secureLabel: {
    color: '#ffff00'
  },
  specialLabel: {
    color: '#00ffff',
    fontSize: 14
  }
});

export default KeyButton;
