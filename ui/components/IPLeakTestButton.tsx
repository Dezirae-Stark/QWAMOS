/**
 * IP Leak Test Button Component
 *
 * Triggers IP leak detection tests and displays results
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Modal,
  ScrollView,
} from 'react';
import { NetworkManager } from '../services/NetworkManager';

interface LeakTestResults {
  tests: {
    ipv4?: { status: string; ip?: string };
    ipv6?: { status: string; blocked?: boolean };
    dns?: { status: string };
    tor?: { status: string; using_tor?: boolean; ip?: string };
  };
  leaks_detected: string[];
}

export const IPLeakTestButton: React.FC = () => {
  const [testing, setTesting] = useState<boolean>(false);
  const [results, setResults] = useState<LeakTestResults | null>(null);
  const [modalVisible, setModalVisible] = useState<boolean>(false);

  const runLeakTest = async () => {
    setTesting(true);

    try {
      const testResults = await NetworkManager.runLeakTest();
      setResults(testResults);
      setModalVisible(true);
    } catch (error) {
      console.error('Leak test failed:', error);
    } finally {
      setTesting(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return '✅';
      case 'fail':
        return '❌';
      case 'warning':
        return '⚠️';
      default:
        return 'ℹ️';
    }
  };

  return (
    <View>
      <TouchableOpacity
        style={styles.button}
        onPress={runLeakTest}
        disabled={testing}
      >
        {testing ? (
          <>
            <ActivityIndicator size="small" color="#fff" />
            <Text style={styles.buttonText}>Running Tests...</Text>
          </>
        ) : (
          <>
            <Text style={styles.buttonIcon}>🔍</Text>
            <Text style={styles.buttonText}>Run IP Leak Test</Text>
          </>
        )}
      </TouchableOpacity>

      {/* Results Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <ScrollView>
              <Text style={styles.modalTitle}>IP Leak Test Results</Text>

              {results && (
                <>
                  {/* Overall Status */}
                  <View style={styles.overallStatus}>
                    {results.leaks_detected.length === 0 ? (
                      <>
                        <Text style={styles.statusIcon}>✅</Text>
                        <Text style={styles.statusText}>No Leaks Detected</Text>
                      </>
                    ) : (
                      <>
                        <Text style={styles.statusIcon}>❌</Text>
                        <Text style={styles.statusTextFail}>
                          {results.leaks_detected.length} Leak(s) Detected
                        </Text>
                      </>
                    )}
                  </View>

                  {/* Test Results */}
                  <View style={styles.testsContainer}>
                    {/* IPv4 Test */}
                    {results.tests.ipv4 && (
                      <View style={styles.testResult}>
                        <Text style={styles.testIcon}>
                          {getStatusIcon(results.tests.ipv4.status)}
                        </Text>
                        <View style={styles.testInfo}>
                          <Text style={styles.testLabel}>IPv4 Test</Text>
                          <Text style={styles.testValue}>
                            {results.tests.ipv4.ip || results.tests.ipv4.status}
                          </Text>
                        </View>
                      </View>
                    )}

                    {/* IPv6 Test */}
                    {results.tests.ipv6 && (
                      <View style={styles.testResult}>
                        <Text style={styles.testIcon}>
                          {getStatusIcon(results.tests.ipv6.status)}
                        </Text>
                        <View style={styles.testInfo}>
                          <Text style={styles.testLabel}>IPv6 Test</Text>
                          <Text style={styles.testValue}>
                            {results.tests.ipv6.blocked ? 'Properly Blocked' : 'Active'}
                          </Text>
                        </View>
                      </View>
                    )}

                    {/* DNS Test */}
                    {results.tests.dns && (
                      <View style={styles.testResult}>
                        <Text style={styles.testIcon}>
                          {getStatusIcon(results.tests.dns.status)}
                        </Text>
                        <View style={styles.testInfo}>
                          <Text style={styles.testLabel}>DNS Test</Text>
                          <Text style={styles.testValue}>{results.tests.dns.status}</Text>
                        </View>
                      </View>
                    )}

                    {/* Tor Test */}
                    {results.tests.tor && (
                      <View style={styles.testResult}>
                        <Text style={styles.testIcon}>
                          {getStatusIcon(results.tests.tor.status)}
                        </Text>
                        <View style={styles.testInfo}>
                          <Text style={styles.testLabel}>Tor Connection</Text>
                          <Text style={styles.testValue}>
                            {results.tests.tor.using_tor
                              ? `Using Tor (${results.tests.tor.ip})`
                              : 'Not using Tor'}
                          </Text>
                        </View>
                      </View>
                    )}
                  </View>

                  {/* Leak Details */}
                  {results.leaks_detected.length > 0 && (
                    <View style={styles.leaksContainer}>
                      <Text style={styles.leaksTitle}>Detected Leaks:</Text>
                      {results.leaks_detected.map((leak, index) => (
                        <Text key={index} style={styles.leakItem}>
                          • {leak}
                        </Text>
                      ))}
                    </View>
                  )}
                </>
              )}

              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.closeButtonText}>Close</Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  button: {
    backgroundColor: '#00BCD4',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 10,
    gap: 10,
  },
  buttonIcon: {
    fontSize: 20,
  },
  buttonText: {
    color: '#000',
    fontSize: 16,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: '#1a1a1a',
    borderRadius: 15,
    padding: 20,
    maxHeight: '80%',
  },
  modalTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 20,
    textAlign: 'center',
  },
  overallStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    backgroundColor: '#2a2a2a',
    borderRadius: 10,
    marginBottom: 20,
  },
  statusIcon: {
    fontSize: 28,
    marginRight: 10,
  },
  statusText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#4CAF50',
  },
  statusTextFail: {
    fontSize: 18,
    fontWeight: '600',
    color: '#F44336',
  },
  testsContainer: {
    marginBottom: 15,
  },
  testResult: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    marginBottom: 8,
  },
  testIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  testInfo: {
    flex: 1,
  },
  testLabel: {
    fontSize: 14,
    color: '#aaa',
    marginBottom: 3,
  },
  testValue: {
    fontSize: 15,
    color: '#fff',
  },
  leaksContainer: {
    backgroundColor: '#2a1a1a',
    padding: 15,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#F44336',
    marginBottom: 15,
  },
  leaksTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#F44336',
    marginBottom: 10,
  },
  leakItem: {
    fontSize: 14,
    color: '#FFA726',
    marginBottom: 5,
  },
  closeButton: {
    backgroundColor: '#333',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
