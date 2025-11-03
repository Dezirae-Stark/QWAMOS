/**
 * QWAMOS Network Settings Screen
 *
 * React Native UI for switching between network isolation modes
 * and monitoring network status.
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { NetworkModeCard } from '../components/NetworkModeCard';
import { NetworkStatusIndicator } from '../components/NetworkStatusIndicator';
import { IPLeakTestButton } from '../components/IPLeakTestButton';
import { NetworkManager } from '../services/NetworkManager';

interface NetworkMode {
  id: string;
  name: string;
  description: string;
  speed: 'Fast' | 'Medium' | 'Slow';
  anonymity: 'None' | 'Low' | 'Medium' | 'High' | 'Maximum';
  icon: string;
  services: string[];
  warning?: string;
}

const NETWORK_MODES: NetworkMode[] = [
  {
    id: 'direct',
    name: 'Direct Connection',
    description: 'No anonymization - Fastest speed',
    speed: 'Fast',
    anonymity: 'None',
    icon: '⚡',
    services: [],
    warning: 'ISP can see all traffic. Not recommended for sensitive activities.',
  },
  {
    id: 'tor-only',
    name: 'Tor Only',
    description: 'Route all traffic through Tor network',
    speed: 'Medium',
    anonymity: 'High',
    icon: '🧅',
    services: ['Tor'],
  },
  {
    id: 'tor-dnscrypt',
    name: 'Tor + DNSCrypt',
    description: 'Tor routing with encrypted DNS (Recommended)',
    speed: 'Medium',
    anonymity: 'High',
    icon: '🔐',
    services: ['Tor', 'DNSCrypt'],
  },
  {
    id: 'tor-i2p-parallel',
    name: 'Tor + I2P Parallel',
    description: 'Access both Tor and I2P networks',
    speed: 'Medium',
    anonymity: 'High',
    icon: '🌐',
    services: ['Tor', 'I2P', 'DNSCrypt'],
  },
  {
    id: 'i2p-only',
    name: 'I2P Only',
    description: 'Access I2P eepsites only (no clearnet)',
    speed: 'Slow',
    anonymity: 'High',
    icon: '👁️',
    services: ['I2P'],
  },
  {
    id: 'maximum-anonymity',
    name: 'Maximum Anonymity',
    description: 'Tor → I2P chaining for extreme privacy',
    speed: 'Slow',
    anonymity: 'Maximum',
    icon: '🛡️',
    services: ['Tor', 'I2P', 'DNSCrypt'],
  },
];

export const NetworkSettingsScreen: React.FC = () => {
  const [currentMode, setCurrentMode] = useState<string>('tor-dnscrypt');
  const [switching, setSwitching] = useState<boolean>(false);
  const [networkStatus, setNetworkStatus] = useState<any>(null);
  const [vpnEnabled, setVpnEnabled] = useState<boolean>(false);
  const [bridgesEnabled, setBridgesEnabled] = useState<boolean>(false);

  // Load current network status
  useEffect(() => {
    loadNetworkStatus();
    const interval = setInterval(loadNetworkStatus, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  const loadNetworkStatus = async () => {
    try {
      const status = await NetworkManager.getStatus();
      setNetworkStatus(status);
      setCurrentMode(status.current_mode);
    } catch (error) {
      console.error('Failed to load network status:', error);
    }
  };

  const handleModeSwitch = async (modeId: string) => {
    const mode = NETWORK_MODES.find((m) => m.id === modeId);

    if (!mode) return;

    // Show warning for direct mode
    if (modeId === 'direct') {
      Alert.alert(
        'Warning: No Anonymization',
        'Direct mode provides no privacy protection. Your ISP can see all traffic. Continue?',
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Continue',
            style: 'destructive',
            onPress: () => performModeSwitch(modeId),
          },
        ]
      );
      return;
    }

    performModeSwitch(modeId);
  };

  const performModeSwitch = async (modeId: string) => {
    setSwitching(true);

    try {
      await NetworkManager.switchMode(modeId, {
        vpn: { enabled: vpnEnabled },
        tor: { use_bridges: bridgesEnabled },
      });

      setCurrentMode(modeId);

      Alert.alert(
        'Network Mode Switched',
        `Successfully switched to ${NETWORK_MODES.find((m) => m.id === modeId)?.name}`,
        [{ text: 'OK' }]
      );

      // Reload status
      await loadNetworkStatus();
    } catch (error) {
      Alert.alert('Error', `Failed to switch network mode: ${error}`, [
        { text: 'OK' },
      ]);
    } finally {
      setSwitching(false);
    }
  };

  const handleVPNToggle = (enabled: boolean) => {
    setVpnEnabled(enabled);
    // VPN will be applied on next mode switch
  };

  const handleBridgesToggle = (enabled: boolean) => {
    setBridgesEnabled(enabled);
    if (currentMode.includes('tor')) {
      // Restart Tor with bridges
      NetworkManager.updateTorBridges(enabled);
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Network Isolation</Text>
        <Text style={styles.headerSubtitle}>
          QWAMOS Multi-Layer Anonymization
        </Text>
      </View>

      {/* Current Status */}
      <View style={styles.statusCard}>
        <NetworkStatusIndicator status={networkStatus} />
      </View>

      {/* Global Options */}
      <View style={styles.optionsCard}>
        <Text style={styles.sectionTitle}>Global Options</Text>

        <View style={styles.option}>
          <View style={styles.optionText}>
            <Text style={styles.optionLabel}>WireGuard VPN</Text>
            <Text style={styles.optionDescription}>
              Add VPN layer (Post-Quantum Kyber-1024)
            </Text>
          </View>
          <Switch value={vpnEnabled} onValueChange={handleVPNToggle} />
        </View>

        <View style={styles.option}>
          <View style={styles.optionText}>
            <Text style={styles.optionLabel}>Tor Bridges</Text>
            <Text style={styles.optionDescription}>
              Use bridges to bypass censorship (obfs4)
            </Text>
          </View>
          <Switch value={bridgesEnabled} onValueChange={handleBridgesToggle} />
        </View>
      </View>

      {/* Mode Selection */}
      <View style={styles.modesSection}>
        <Text style={styles.sectionTitle}>Network Modes</Text>

        {NETWORK_MODES.map((mode) => (
          <NetworkModeCard
            key={mode.id}
            mode={mode}
            isActive={currentMode === mode.id}
            isDisabled={switching}
            onPress={() => handleModeSwitch(mode.id)}
          />
        ))}
      </View>

      {/* Testing */}
      <View style={styles.testingSection}>
        <Text style={styles.sectionTitle}>Network Testing</Text>
        <IPLeakTestButton />
      </View>

      {/* Loading Overlay */}
      {switching && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.loadingText}>Switching network mode...</Text>
          <Text style={styles.loadingSubtext}>
            This may take 10-30 seconds
          </Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },
  header: {
    padding: 20,
    paddingTop: 40,
    borderBottomWidth: 1,
    borderBottomColor: '#222',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#888',
  },
  statusCard: {
    margin: 15,
    padding: 15,
    backgroundColor: '#1a1a1a',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#333',
  },
  optionsCard: {
    margin: 15,
    marginTop: 0,
    padding: 15,
    backgroundColor: '#1a1a1a',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#333',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 15,
  },
  option: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  optionText: {
    flex: 1,
    marginRight: 15,
  },
  optionLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#fff',
    marginBottom: 3,
  },
  optionDescription: {
    fontSize: 13,
    color: '#888',
  },
  modesSection: {
    margin: 15,
    marginTop: 0,
  },
  testingSection: {
    margin: 15,
    marginTop: 0,
    marginBottom: 30,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginTop: 15,
  },
  loadingSubtext: {
    color: '#888',
    fontSize: 14,
    marginTop: 5,
  },
});
