/**
 * QWAMOS Threat Detection Dashboard
 *
 * Real-time threat detection monitoring and response management UI
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { ThreatDetectionService } from '../../services/ThreatDetectionService';

interface ThreatSummary {
  total_threats: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  last_24h: number;
}

interface DetectorStatus {
  network_anomaly: boolean;
  file_system: boolean;
  system_call: boolean;
}

interface RecentThreat {
  id: string;
  type: string;
  severity: string;
  timestamp: number;
  status: string;
  description: string;
}

export const ThreatDashboard = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [detectorStatus, setDetectorStatus] = useState<DetectorStatus>({
    network_anomaly: false,
    file_system: false,
    system_call: false,
  });
  const [threatSummary, setThreatSummary] = useState<ThreatSummary>({
    total_threats: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    last_24h: 0,
  });
  const [recentThreats, setRecentThreats] = useState<RecentThreat[]>([]);
  const [systemHealth, setSystemHealth] = useState<number>(100);

  useEffect(() => {
    loadDashboard();

    // Refresh every 5 seconds
    const interval = setInterval(loadDashboard, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);

      // Load detector status
      const status = await ThreatDetectionService.getDetectorStatus();
      setDetectorStatus(status);

      // Load threat summary
      const summary = await ThreatDetectionService.getThreatSummary();
      setThreatSummary(summary);

      // Load recent threats
      const threats = await ThreatDetectionService.getRecentThreats(10);
      setRecentThreats(threats);

      // Calculate system health
      const health = await ThreatDetectionService.getSystemHealth();
      setSystemHealth(health);

    } catch (error) {
      console.error('Failed to load dashboard:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboard();
  };

  const toggleDetector = async (detector: keyof DetectorStatus) => {
    try {
      const newStatus = !detectorStatus[detector];

      if (newStatus) {
        await ThreatDetectionService.startDetector(detector);
      } else {
        await ThreatDetectionService.stopDetector(detector);
      }

      setDetectorStatus({
        ...detectorStatus,
        [detector]: newStatus,
      });

      Alert.alert(
        'Success',
        `${detector} detector ${newStatus ? 'started' : 'stopped'}`
      );
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to toggle detector');
    }
  };

  const viewThreatDetails = (threat: RecentThreat) => {
    // Navigate to threat details screen
    Alert.alert(
      `${threat.type}`,
      `Severity: ${threat.severity}\nStatus: ${threat.status}\n\n${threat.description}`,
      [
        { text: 'Dismiss', style: 'cancel' },
        { text: 'View Details', onPress: () => {} },
      ]
    );
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL': return '#FF3B30';
      case 'HIGH': return '#FF9500';
      case 'MEDIUM': return '#FFCC00';
      case 'LOW': return '#34C759';
      default: return '#8E8E93';
    }
  };

  const getHealthColor = (health: number): string => {
    if (health >= 90) return '#34C759';
    if (health >= 70) return '#FFCC00';
    if (health >= 50) return '#FF9500';
    return '#FF3B30';
  };

  if (loading && !refreshing) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading threat detection...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🛡️ Threat Detection</Text>
        <Text style={styles.subtitle}>Real-time ML-powered security monitoring</Text>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* System Health */}
        <View style={styles.healthCard}>
          <Text style={styles.sectionTitle}>System Health</Text>
          <View style={styles.healthMeter}>
            <View style={styles.healthBar}>
              <View
                style={[
                  styles.healthFill,
                  {
                    width: `${systemHealth}%`,
                    backgroundColor: getHealthColor(systemHealth),
                  },
                ]}
              />
            </View>
            <Text style={styles.healthText}>{systemHealth}%</Text>
          </View>
          <Text style={styles.healthStatus}>
            {systemHealth >= 90
              ? '✅ Excellent - All systems operational'
              : systemHealth >= 70
              ? '⚠️  Good - Minor threats detected'
              : systemHealth >= 50
              ? '⚠️  Fair - Active threats present'
              : '🚨 Poor - Critical threats detected'}
          </Text>
        </View>

        {/* Detector Status */}
        <View style={styles.detectorsCard}>
          <Text style={styles.sectionTitle}>ML Detectors</Text>

          {/* Network Anomaly Detector */}
          <View style={styles.detectorRow}>
            <View style={styles.detectorInfo}>
              <Text style={styles.detectorIcon}>🌐</Text>
              <View>
                <Text style={styles.detectorName}>Network Anomaly</Text>
                <Text style={styles.detectorDesc}>Monitors network traffic</Text>
              </View>
            </View>
            <TouchableOpacity
              style={[
                styles.toggleButton,
                detectorStatus.network_anomaly && styles.toggleButtonActive,
              ]}
              onPress={() => toggleDetector('network_anomaly')}
            >
              <Text
                style={[
                  styles.toggleButtonText,
                  detectorStatus.network_anomaly && styles.toggleButtonTextActive,
                ]}
              >
                {detectorStatus.network_anomaly ? 'ON' : 'OFF'}
              </Text>
            </TouchableOpacity>
          </View>

          {/* File System Monitor */}
          <View style={styles.detectorRow}>
            <View style={styles.detectorInfo}>
              <Text style={styles.detectorIcon}>📁</Text>
              <View>
                <Text style={styles.detectorName}>File System</Text>
                <Text style={styles.detectorDesc}>Monitors file operations</Text>
              </View>
            </View>
            <TouchableOpacity
              style={[
                styles.toggleButton,
                detectorStatus.file_system && styles.toggleButtonActive,
              ]}
              onPress={() => toggleDetector('file_system')}
            >
              <Text
                style={[
                  styles.toggleButtonText,
                  detectorStatus.file_system && styles.toggleButtonTextActive,
                ]}
              >
                {detectorStatus.file_system ? 'ON' : 'OFF'}
              </Text>
            </TouchableOpacity>
          </View>

          {/* System Call Analyzer */}
          <View style={styles.detectorRow}>
            <View style={styles.detectorInfo}>
              <Text style={styles.detectorIcon}>⚙️</Text>
              <View>
                <Text style={styles.detectorName}>System Calls</Text>
                <Text style={styles.detectorDesc}>Analyzes syscall sequences</Text>
              </View>
            </View>
            <TouchableOpacity
              style={[
                styles.toggleButton,
                detectorStatus.system_call && styles.toggleButtonActive,
              ]}
              onPress={() => toggleDetector('system_call')}
            >
              <Text
                style={[
                  styles.toggleButtonText,
                  detectorStatus.system_call && styles.toggleButtonTextActive,
                ]}
              >
                {detectorStatus.system_call ? 'ON' : 'OFF'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Threat Summary */}
        <View style={styles.summaryCard}>
          <Text style={styles.sectionTitle}>Threat Summary</Text>

          <View style={styles.summaryGrid}>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryValue}>{threatSummary.total_threats}</Text>
              <Text style={styles.summaryLabel}>Total</Text>
            </View>

            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, { color: '#FF3B30' }]}>
                {threatSummary.critical}
              </Text>
              <Text style={styles.summaryLabel}>Critical</Text>
            </View>

            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, { color: '#FF9500' }]}>
                {threatSummary.high}
              </Text>
              <Text style={styles.summaryLabel}>High</Text>
            </View>

            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, { color: '#FFCC00' }]}>
                {threatSummary.medium}
              </Text>
              <Text style={styles.summaryLabel}>Medium</Text>
            </View>
          </View>

          <View style={styles.summaryFooter}>
            <Text style={styles.summaryFooterText}>
              {threatSummary.last_24h} threats detected in last 24 hours
            </Text>
          </View>
        </View>

        {/* Recent Threats */}
        <View style={styles.threatsCard}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Threats</Text>
            <TouchableOpacity onPress={() => {}}>
              <Text style={styles.viewAllText}>View All →</Text>
            </TouchableOpacity>
          </View>

          {recentThreats.length === 0 ? (
            <View style={styles.emptyState}>
              <Text style={styles.emptyIcon}>✅</Text>
              <Text style={styles.emptyText}>No threats detected</Text>
              <Text style={styles.emptySubtext}>System is secure</Text>
            </View>
          ) : (
            recentThreats.map((threat) => (
              <TouchableOpacity
                key={threat.id}
                style={styles.threatItem}
                onPress={() => viewThreatDetails(threat)}
              >
                <View
                  style={[
                    styles.severityIndicator,
                    { backgroundColor: getSeverityColor(threat.severity) },
                  ]}
                />
                <View style={styles.threatContent}>
                  <View style={styles.threatHeader}>
                    <Text style={styles.threatType}>{threat.type}</Text>
                    <Text style={styles.threatTime}>
                      {new Date(threat.timestamp * 1000).toLocaleTimeString()}
                    </Text>
                  </View>
                  <Text style={styles.threatDescription} numberOfLines={2}>
                    {threat.description}
                  </Text>
                  <View style={styles.threatFooter}>
                    <Text
                      style={[
                        styles.threatSeverity,
                        { color: getSeverityColor(threat.severity) },
                      ]}
                    >
                      {threat.severity}
                    </Text>
                    <Text style={styles.threatStatus}>{threat.status}</Text>
                  </View>
                </View>
              </TouchableOpacity>
            ))
          )}
        </View>

        {/* Quick Actions */}
        <View style={styles.actionsCard}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>

          <View style={styles.actionButtons}>
            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>📊 View Analytics</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>🔍 Run Scan</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>⚙️ Settings</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.actionButton}>
              <Text style={styles.actionButtonText}>📝 View Logs</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F5F5F5',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#666',
  },
  header: {
    padding: 20,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  healthCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  healthMeter: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  healthBar: {
    flex: 1,
    height: 24,
    backgroundColor: '#E0E0E0',
    borderRadius: 12,
    overflow: 'hidden',
  },
  healthFill: {
    height: '100%',
    borderRadius: 12,
  },
  healthText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginLeft: 12,
    minWidth: 50,
  },
  healthStatus: {
    fontSize: 14,
    color: '#666',
  },
  detectorsCard: {
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
  detectorRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F0F0F0',
  },
  detectorInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  detectorIcon: {
    fontSize: 28,
    marginRight: 12,
  },
  detectorName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  detectorDesc: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  toggleButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: '#E0E0E0',
    minWidth: 60,
    alignItems: 'center',
  },
  toggleButtonActive: {
    backgroundColor: '#34C759',
  },
  toggleButtonText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#666',
  },
  toggleButtonTextActive: {
    color: '#FFFFFF',
  },
  summaryCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
  },
  summaryFooter: {
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  summaryFooterText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  threatsCard: {
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
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  viewAllText: {
    fontSize: 14,
    color: '#007AFF',
    fontWeight: '600',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  emptyText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#666',
  },
  threatItem: {
    flexDirection: 'row',
    marginBottom: 12,
    padding: 12,
    backgroundColor: '#F9F9F9',
    borderRadius: 8,
  },
  severityIndicator: {
    width: 4,
    borderRadius: 2,
    marginRight: 12,
  },
  threatContent: {
    flex: 1,
  },
  threatHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  threatType: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
  },
  threatTime: {
    fontSize: 12,
    color: '#999',
  },
  threatDescription: {
    fontSize: 13,
    color: '#666',
    marginBottom: 8,
  },
  threatFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  threatSeverity: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  threatStatus: {
    fontSize: 12,
    color: '#666',
  },
  actionsCard: {
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
  actionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  actionButton: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
});
