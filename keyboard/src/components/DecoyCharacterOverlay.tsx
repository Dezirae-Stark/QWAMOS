/**
 * QWAMOS SecureType Keyboard - Decoy Character Overlay
 *
 * Anti-shoulder-surfing protection:
 * - Flashes random characters on screen while typing
 * - Makes visual observation useless
 * - Real input is encrypted and hidden
 *
 * Used in PARANOID security mode
 *
 * @module DecoyCharacterOverlay
 * @version 1.0.0
 */

import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Dimensions } from 'react-native';

const { width, height } = Dimensions.get('window');

interface DecoyChar {
  char: string;
  x: number;
  y: number;
  opacity: number;
  fontSize: number;
}

const DecoyCharacterOverlay: React.FC = () => {
  const [decoys, setDecoys] = useState<DecoyChar[]>([]);

  /**
   * Generate random decoy characters
   */
  useEffect(() => {
    const chars = [];
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()';

    // Generate 15-20 random decoy characters
    const count = 15 + Math.floor(Math.random() * 6);

    for (let i = 0; i < count; i++) {
      chars.push({
        char: characters[Math.floor(Math.random() * characters.length)],
        x: Math.random() * (width - 50),
        y: Math.random() * 250, // Keep within keyboard area
        opacity: 0.1 + Math.random() * 0.3,
        fontSize: 16 + Math.random() * 24
      });
    }

    setDecoys(chars);

    // Clear decoys after 100ms
    const timeout = setTimeout(() => {
      setDecoys([]);
    }, 100);

    return () => clearTimeout(timeout);
  }, []);

  return (
    <View style={styles.container} pointerEvents="none">
      {decoys.map((decoy, index) => (
        <Text
          key={index}
          style={[
            styles.decoyChar,
            {
              left: decoy.x,
              top: decoy.y,
              opacity: decoy.opacity,
              fontSize: decoy.fontSize
            }
          ]}
        >
          {decoy.char}
        </Text>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    zIndex: 999
  },
  decoyChar: {
    position: 'absolute',
    color: '#ffff00',
    fontWeight: 'bold'
  }
});

export default DecoyCharacterOverlay;
