/**
 * QWAMOS SecureType Keyboard - Security Indicator
 *
 * Visual indicator showing current security status:
 * - Mode (STANDARD, PASSWORD, TERMINAL)
 * - Security level (STANDARD, HIGH, PARANOID)
 * - Lock status
 * - ML detector status
 *
 * @module SecurityIndicator
 * @version 1.0.0
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { SecurityIndicatorProps } from '../types';

const SecurityIndicator: React.FC<SecurityIndicatorProps> = ({
  mode,
  securityLevel,
  isLocked,
  mlEnabled
}) => {
  /**
   * Get mode icon and color
   */
  const getModeStyle = () => {
    switch (mode) {
      case 'PASSWORD':
        return { icon: '🔒', color: '#ffff00', bg: '#2a2a00' };
      case 'TERMINAL':
        return { icon: '⌨️', color: '#00ffff', bg: '#001a1a' };
      case 'STANDARD':
      default:
        return { icon: '📝', color: '#ffffff', bg: '#2a2a2a' };
    }
  };

  /**
   * Get security level badge
   */
  const getSecurityBadge = () => {
    switch (securityLevel) {
      case 'PARANOID':
        return { text: 'PARANOID', color: '#ff0000', bg: '#2a0000' };
      case 'HIGH':
        return { text: 'HIGH', color: '#ffaa00', bg: '#2a1a00' };
      case 'STANDARD':
      default:
        return { text: 'STANDARD', color: '#00ff00', bg: '#002200' };
    }
  };

  const modeStyle = getModeStyle();
  const securityBadge = getSecurityBadge();

  return (
    <View style={styles.container}>
      {/* Mode indicator */}
      <View style={[styles.modeIndicator, { backgroundColor: modeStyle.bg }]}>
        <Text style={styles.modeIcon}>{modeStyle.icon}</Text>
        <Text style={[styles.modeText, { color: modeStyle.color }]}>
          {mode}
        </Text>
      </View>

      {/* Security level badge */}
      <View style={[styles.securityBadge, { backgroundColor: securityBadge.bg }]}>
        <Text style={[styles.securityText, { color: securityBadge.color }]}>
          {securityBadge.text}
        </Text>
      </View>

      {/* ML detector status */}
      {mlEnabled && (
        <View style={styles.mlBadge}>
          <Text style={styles.mlText}>🧠 ML</Text>
        </View>
      )}

      {/* Lock indicator */}
      {isLocked && (
        <View style={styles.lockIndicator}>
          <Text style={styles.lockText}>🔒 LOCKED</Text>
        </View>
      )}

      {/* Zero telemetry badge */}
      <View style={styles.privacyBadge}>
        <Text style={styles.privacyText}>🚫 No Telemetry</Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#0a0a0a',
    borderBottomWidth: 1,
    borderBottomColor: '#333'
  },
  modeIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 5,
    marginRight: 8
  },
  modeIcon: {
    fontSize: 16,
    marginRight: 6
  },
  modeText: {
    fontSize: 12,
    fontWeight: 'bold'
  },
  securityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 5,
    marginRight: 8
  },
  securityText: {
    fontSize: 10,
    fontWeight: 'bold'
  },
  mlBadge: {
    backgroundColor: '#1a001a',
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 5,
    marginRight: 8
  },
  mlText: {
    color: '#ff00ff',
    fontSize: 10,
    fontWeight: 'bold'
  },
  lockIndicator: {
    backgroundColor: '#2a0000',
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 5,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#ff0000'
  },
  lockText: {
    color: '#ff0000',
    fontSize: 10,
    fontWeight: 'bold'
  },
  privacyBadge: {
    flex: 1,
    alignItems: 'flex-end'
  },
  privacyText: {
    color: '#00ff00',
    fontSize: 9
  }
});

export default SecurityIndicator;
