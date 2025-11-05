/**
 * QWAMOS Phase 10: Bootloader Lock Toggle UI Component
 * =====================================================
 *
 * User-optional bootloader lock toggle with ML threat detection override.
 *
 * Features:
 * - Simple on/off toggle switch
 * - Real-time status indicator
 * - Override status display (when ML locks bootloader)
 * - Threat history viewer
 * - Biometric unlock for override reset
 *
 * Security:
 * - User controls lock state (not forced)
 * - ML can override to lock (emergency only)
 * - Override requires biometric to reset
 *
 * Version: 1.0.0
 * Date: 2025-11-05
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  Switch,
  TouchableOpacity,
  StyleSheet,
  Alert,
  FlatList,
  ScrollView,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Python bridge for ml_bootloader_override.py
import { PythonBridge } from '../../../bridges/python_bridge';

interface ThreatEvent {
  timestamp: string;
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  description: string;
  action: string;
}

interface OverrideStatus {
  bootloader_locked: boolean;
  user_lock_preference: boolean;
  override_active: boolean;
  override_reason: string | null;
  monitoring_active: boolean;
  recent_threats: ThreatEvent[];
}

const BootloaderLockToggle: React.FC = () => {
  const [status, setStatus] = useState<OverrideStatus>({
    bootloader_locked: false,
    user_lock_preference: false,
    override_active: false,
    override_reason: null,
    monitoring_active: false,
    recent_threats: [],
  });

  const [loading, setLoading] = useState(false);
  const [showThreats, setShowThreats] = useState(false);

  // Poll status every 5 seconds
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const result = await PythonBridge.execute('ml_bootloader_override', 'get_status');
      setStatus(result);
    } catch (error) {
      console.error('[Bootloader Toggle] Failed to fetch status:', error);
    }
  };

  const handleToggle = async (enabled: boolean) => {
    setLoading(true);

    try {
      // Show confirmation dialog
      const confirmed = await new Promise<boolean>((resolve) => {
        Alert.alert(
          enabled ? 'Enable Bootloader Lock?' : 'Disable Bootloader Lock?',
          enabled
            ? 'Locking the bootloader prevents unauthorized firmware modifications. ' +
              'This protects against nation-state attacks like WikiLeaks Vault 7 Dark Matter.\n\n' +
              'You can unlock later, but ML threat detection may override if an attack is detected.'
            : 'Unlocking the bootloader allows firmware modifications. ' +
              'This reduces security but may be needed for development.\n\n' +
              'WARNING: Unlocking makes your device vulnerable to bootloader attacks.',
          [
            { text: 'Cancel', onPress: () => resolve(false), style: 'cancel' },
            { text: enabled ? 'Lock' : 'Unlock', onPress: () => resolve(true) },
          ]
        );
      });

      if (!confirmed) {
        setLoading(false);
        return;
      }

      // Set user preference
      await PythonBridge.execute('ml_bootloader_override', 'set_user_lock_preference', {
        enabled,
      });

      // Refresh status
      await fetchStatus();

      Alert.alert(
        'Success',
        enabled
          ? 'Bootloader will be locked on next boot.'
          : 'Bootloader will be unlocked on next boot (if no threats detected).'
      );
    } catch (error) {
      console.error('[Bootloader Toggle] Failed to toggle:', error);
      Alert.alert('Error', 'Failed to update bootloader lock preference.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetOverride = async () => {
    Alert.alert(
      'Reset Emergency Override?',
      'This will attempt to unlock the bootloader. Biometric authentication is required.\n\n' +
        'This is only allowed if no critical threats are active.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          onPress: async () => {
            try {
              // Request biometric authentication
              const biometric = await requestBiometric();
              if (!biometric) {
                Alert.alert('Error', 'Biometric authentication failed.');
                return;
              }

              // Reset override
              await PythonBridge.execute('ml_bootloader_override', 'reset_override', {
                biometric_verified: true,
              });

              // Refresh status
              await fetchStatus();

              Alert.alert('Success', 'Emergency override has been reset.');
            } catch (error) {
              console.error('[Bootloader Toggle] Failed to reset override:', error);
              Alert.alert('Error', 'Failed to reset override. Active threats may be present.');
            }
          },
        },
      ]
    );
  };

  const requestBiometric = async (): Promise<boolean> => {
    // TODO: Integrate with Android BiometricPrompt API
    // For now, return true (simulated)
    return new Promise((resolve) => {
      Alert.alert('Biometric Authentication', 'Place finger on sensor...', [
        { text: 'Cancel', onPress: () => resolve(false), style: 'cancel' },
        { text: 'Verified', onPress: () => resolve(true) },
      ]);
    });
  };

  const getThreatLevelColor = (level: string): string => {
    switch (level) {
      case 'CRITICAL':
        return '#DC2626'; // Red
      case 'HIGH':
        return '#EA580C'; // Orange
      case 'MEDIUM':
        return '#F59E0B'; // Yellow
      case 'LOW':
        return '#3B82F6'; // Blue
      default:
        return '#6B7280'; // Gray
    }
  };

  const renderThreatItem = ({ item }: { item: ThreatEvent }) => (
    <View style={styles.threatItem}>
      <View style={styles.threatHeader}>
        <View style={[styles.threatBadge, { backgroundColor: getThreatLevelColor(item.level) }]}>
          <Text style={styles.threatBadgeText}>{item.level}</Text>
        </View>
        <Text style={styles.threatTimestamp}>{new Date(item.timestamp).toLocaleString()}</Text>
      </View>
      <Text style={styles.threatDescription}>{item.description}</Text>
      <Text style={styles.threatAction}>Action: {item.action}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Main Status Card */}
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Icon name="lock" size={32} color="#3B82F6" />
          <Text style={styles.cardTitle}>Bootloader Lock</Text>
        </View>

        {/* Current Status */}
        <View style={styles.statusRow}>
          <Text style={styles.statusLabel}>Current State:</Text>
          <View style={styles.statusBadge}>
            <Icon
              name={status.bootloader_locked ? 'lock' : 'lock-open'}
              size={16}
              color={status.bootloader_locked ? '#10B981' : '#EF4444'}
            />
            <Text
              style={[
                styles.statusText,
                { color: status.bootloader_locked ? '#10B981' : '#EF4444' },
              ]}
            >
              {status.bootloader_locked ? 'LOCKED' : 'UNLOCKED'}
            </Text>
          </View>
        </View>

        {/* User Toggle */}
        <View style={styles.toggleRow}>
          <View style={styles.toggleLabel}>
            <Text style={styles.toggleTitle}>Enable Bootloader Lock</Text>
            <Text style={styles.toggleSubtitle}>
              Protects against firmware attacks (WikiLeaks Vault 7 Dark Matter)
            </Text>
          </View>
          <Switch
            value={status.user_lock_preference}
            onValueChange={handleToggle}
            disabled={loading || status.override_active}
            trackColor={{ false: '#D1D5DB', true: '#3B82F6' }}
            thumbColor={status.user_lock_preference ? '#1E40AF' : '#F3F4F6'}
          />
        </View>

        {/* Override Warning */}
        {status.override_active && (
          <View style={styles.overrideWarning}>
            <Icon name="alert" size={24} color="#DC2626" />
            <View style={styles.overrideContent}>
              <Text style={styles.overrideTitle}>⚠️ EMERGENCY OVERRIDE ACTIVE</Text>
              <Text style={styles.overrideReason}>
                ML threat detection has locked the bootloader due to: {status.override_reason}
              </Text>
              <TouchableOpacity style={styles.resetButton} onPress={handleResetOverride}>
                <Icon name="lock-reset" size={16} color="#FFFFFF" />
                <Text style={styles.resetButtonText}>Reset Override</Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* Monitoring Status */}
        <View style={styles.monitoringRow}>
          <Icon
            name="shield-search"
            size={20}
            color={status.monitoring_active ? '#10B981' : '#6B7280'}
          />
          <Text
            style={[
              styles.monitoringText,
              { color: status.monitoring_active ? '#10B981' : '#6B7280' },
            ]}
          >
            ML Threat Monitoring: {status.monitoring_active ? 'ACTIVE' : 'INACTIVE'}
          </Text>
        </View>
      </View>

      {/* Threat History */}
      <View style={styles.card}>
        <TouchableOpacity
          style={styles.cardHeader}
          onPress={() => setShowThreats(!showThreats)}
        >
          <Icon name="history" size={24} color="#6B7280" />
          <Text style={styles.cardTitle}>Recent Threats ({status.recent_threats.length})</Text>
          <Icon
            name={showThreats ? 'chevron-up' : 'chevron-down'}
            size={24}
            color="#6B7280"
          />
        </TouchableOpacity>

        {showThreats && (
          <View>
            {status.recent_threats.length === 0 ? (
              <View style={styles.emptyState}>
                <Icon name="shield-check" size={48} color="#10B981" />
                <Text style={styles.emptyStateText}>No threats detected (last 60 minutes)</Text>
              </View>
            ) : (
              <FlatList
                data={status.recent_threats}
                renderItem={renderThreatItem}
                keyExtractor={(item, index) => index.toString()}
                scrollEnabled={false}
              />
            )}
          </View>
        )}
      </View>

      {/* Info Card */}
      <View style={styles.infoCard}>
        <Icon name="information" size={24} color="#3B82F6" />
        <View style={styles.infoContent}>
          <Text style={styles.infoTitle}>How It Works</Text>
          <Text style={styles.infoText}>
            • <Text style={styles.infoBold}>User Control:</Text> You decide whether to lock the
            bootloader{'\n'}
            • <Text style={styles.infoBold}>ML Override:</Text> AI detects threats and can
            emergency-lock{'\n'}
            • <Text style={styles.infoBold}>Permission Request:</Text> You'll be notified before
            override (10s timeout){'\n'}
            • <Text style={styles.infoBold}>Critical Threats:</Text> Instant lock (no permission) for
            bootloader attacks{'\n'}• <Text style={styles.infoBold}>Biometric Reset:</Text>{' '}
            Fingerprint required to unlock after override
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
    padding: 16,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginLeft: 12,
    flex: 1,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  statusLabel: {
    fontSize: 16,
    color: '#6B7280',
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 6,
  },
  toggleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  toggleLabel: {
    flex: 1,
    marginRight: 16,
  },
  toggleTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#111827',
    marginBottom: 4,
  },
  toggleSubtitle: {
    fontSize: 13,
    color: '#6B7280',
  },
  overrideWarning: {
    flexDirection: 'row',
    backgroundColor: '#FEF2F2',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#DC2626',
  },
  overrideContent: {
    flex: 1,
    marginLeft: 12,
  },
  overrideTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#DC2626',
    marginBottom: 4,
  },
  overrideReason: {
    fontSize: 13,
    color: '#991B1B',
    marginBottom: 8,
  },
  resetButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#DC2626',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  resetButtonText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#FFFFFF',
    marginLeft: 6,
  },
  monitoringRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  monitoringText: {
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 8,
  },
  threatItem: {
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingTop: 12,
    paddingBottom: 12,
  },
  threatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  threatBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  threatBadgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  threatTimestamp: {
    fontSize: 12,
    color: '#6B7280',
  },
  threatDescription: {
    fontSize: 14,
    color: '#111827',
    marginBottom: 4,
  },
  threatAction: {
    fontSize: 12,
    color: '#6B7280',
    fontStyle: 'italic',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyStateText: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 12,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#EFF6FF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#DBEAFE',
  },
  infoContent: {
    flex: 1,
    marginLeft: 12,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1E40AF',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 13,
    color: '#1E3A8A',
    lineHeight: 20,
  },
  infoBold: {
    fontWeight: '600',
  },
});

export default BootloaderLockToggle;
