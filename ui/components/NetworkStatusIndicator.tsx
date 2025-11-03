/**
 * Network Status Indicator Component
 *
 * Real-time status display for network services
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ServiceStatus {
  running: boolean;
  details?: any;
}

interface NetworkStatus {
  current_mode: string;
  timestamp: number;
  services: {
    tor?: ServiceStatus;
    i2p?: ServiceStatus;
    dnscrypt?: ServiceStatus;
    vpn?: ServiceStatus;
  };
}

interface Props {
  status: NetworkStatus | null;
}

const ServiceIndicator: React.FC<{ name: string; status: ServiceStatus | undefined }> = ({
  name,
  status,
}) => {
  const isRunning = status?.running || false;

  return (
    <View style={styles.serviceRow}>
      <View style={[styles.statusDot, isRunning ? styles.statusActive : styles.statusInactive]} />
      <Text style={styles.serviceName}>{name}</Text>
      <Text style={isRunning ? styles.statusTextActive : styles.statusTextInactive}>
        {isRunning ? 'Running' : 'Stopped'}
      </Text>
    </View>
  );
};

export const NetworkStatusIndicator: React.FC<Props> = ({ status }) => {
  if (!status) {
    return (
      <View style={styles.container}>
        <Text style={styles.title}>Network Status</Text>
        <Text style={styles.loading}>Loading...</Text>
      </View>
    );
  }

  const currentModeDisplay = status.current_mode
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Network Status</Text>
        <View style={styles.modeBadge}>
          <Text style={styles.modeText}>{currentModeDisplay}</Text>
        </View>
      </View>

      <View style={styles.services}>
        <ServiceIndicator name="Tor" status={status.services.tor} />
        <ServiceIndicator name="I2P" status={status.services.i2p} />
        <ServiceIndicator name="DNSCrypt" status={status.services.dnscrypt} />
        <ServiceIndicator name="VPN" status={status.services.vpn} />
      </View>

      <Text style={styles.lastUpdate}>
        Last updated: {new Date(status.timestamp * 1000).toLocaleTimeString()}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    // Container styles handled by parent
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  modeBadge: {
    backgroundColor: '#00BCD4',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  modeText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#000',
  },
  services: {
    marginBottom: 12,
  },
  serviceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#2a2a2a',
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 12,
  },
  statusActive: {
    backgroundColor: '#4CAF50',
  },
  statusInactive: {
    backgroundColor: '#666',
  },
  serviceName: {
    flex: 1,
    fontSize: 14,
    color: '#fff',
  },
  statusTextActive: {
    fontSize: 13,
    color: '#4CAF50',
  },
  statusTextInactive: {
    fontSize: 13,
    color: '#666',
  },
  lastUpdate: {
    fontSize: 11,
    color: '#666',
    marginTop: 8,
  },
  loading: {
    fontSize: 14,
    color: '#888',
    textAlign: 'center',
    paddingVertical: 20,
  },
});
