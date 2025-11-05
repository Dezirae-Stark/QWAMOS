/**
 * QWAMOS AI Assistants Management Screen
 *
 * React Native UI for managing AI assistants:
 * - Kali GPT (local LLM)
 * - Claude (Anthropic API)
 * - ChatGPT (OpenAI API)
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
  TextInput,
  Modal,
} from 'react-native';
import { AIManager } from '../services/AIManager';

interface AIService {
  id: string;
  name: string;
  description: string;
  type: 'local' | 'cloud';
  privacy: string;
  icon: string;
  enabled: boolean;
  requiresApiKey: boolean;
  cost: string;
}

const AI_SERVICES: AIService[] = [
  {
    id: 'kali-gpt',
    name: 'Kali GPT',
    description: 'Local LLM for penetration testing assistance',
    type: 'local',
    privacy: '🟢 100% Local',
    icon: '🤖',
    enabled: false,
    requiresApiKey: false,
    cost: 'Free',
  },
  {
    id: 'claude',
    name: 'Claude',
    description: 'Advanced reasoning via Anthropic API (via Tor)',
    type: 'cloud',
    privacy: '🟡 Cloud via Tor',
    icon: '🧠',
    enabled: false,
    requiresApiKey: true,
    cost: '$0.003-0.015/1K tokens',
  },
  {
    id: 'chatgpt',
    name: 'ChatGPT',
    description: 'General assistance via OpenAI API (via Tor)',
    type: 'cloud',
    privacy: '🟡 Cloud via Tor',
    icon: '💬',
    enabled: false,
    requiresApiKey: true,
    cost: '$0.01-0.03/1K tokens',
  },
];

export const AIAssistantsScreen = () => {
  const [services, setServices] = useState<AIService[]>(AI_SERVICES);
  const [loading, setLoading] = useState<boolean>(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState<boolean>(false);
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState<string>('');
  const [usageStats, setUsageStats] = useState<any>(null);

  useEffect(() => {
    loadStatus();
    loadUsageStats();
  }, []);

  /**
   * Load current AI services status
   */
  const loadStatus = async () => {
    try {
      setLoading(true);
      const status = await AIManager.getStatus();

      // Update services with status from backend
      const updatedServices = services.map((service) => ({
        ...service,
        enabled: status[service.id]?.enabled || false,
      }));

      setServices(updatedServices);
    } catch (error) {
      console.error('Failed to load AI status:', error);
      Alert.alert('Error', 'Failed to load AI services status');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Load usage statistics
   */
  const loadUsageStats = async () => {
    try {
      const stats = await AIManager.getUsageStats();
      setUsageStats(stats);
    } catch (error) {
      console.error('Failed to load usage stats:', error);
    }
  };

  /**
   * Toggle AI service on/off
   */
  const toggleService = async (serviceId: string, enabled: boolean) => {
    try {
      const service = services.find((s) => s.id === serviceId);
      if (!service) return;

      // If enabling and requires API key, show modal
      if (enabled && service.requiresApiKey) {
        setSelectedService(serviceId);
        setShowApiKeyModal(true);
        return;
      }

      // Enable/disable service
      setLoading(true);

      if (enabled) {
        await AIManager.enableService(serviceId);
        Alert.alert('Success', `${service.name} enabled successfully`);
      } else {
        await AIManager.disableService(serviceId);
        Alert.alert('Success', `${service.name} disabled`);
      }

      // Reload status
      await loadStatus();
      await loadUsageStats();
    } catch (error: any) {
      console.error('Failed to toggle service:', error);
      Alert.alert('Error', error.message || 'Failed to toggle service');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Enable service with API key
   */
  const enableWithApiKey = async () => {
    if (!selectedService || !apiKey.trim()) {
      Alert.alert('Error', 'Please enter a valid API key');
      return;
    }

    try {
      setLoading(true);
      await AIManager.enableService(selectedService, apiKey);

      setShowApiKeyModal(false);
      setApiKey('');
      setSelectedService(null);

      Alert.alert('Success', 'AI service enabled successfully');

      // Reload status
      await loadStatus();
      await loadUsageStats();
    } catch (error: any) {
      console.error('Failed to enable service:', error);
      Alert.alert('Error', error.message || 'Failed to enable service');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Navigate to chat screen
   */
  const openChat = (serviceId: string) => {
    // TODO: Navigate to AIChat screen
    Alert.alert('Coming Soon', 'Chat interface will be available soon');
  };

  /**
   * Test service connection
   */
  const testService = async (serviceId: string) => {
    try {
      setLoading(true);
      const result = await AIManager.testService(serviceId);

      if (result.success) {
        Alert.alert('Test Successful', `${serviceId} is working correctly`);
      } else {
        Alert.alert('Test Failed', result.error || 'Connection test failed');
      }
    } catch (error: any) {
      Alert.alert('Error', error.message || 'Failed to test service');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Render AI service card
   */
  const renderServiceCard = (service: AIService) => {
    const stats = usageStats?.[service.id] || {
      queries: 0,
      tokens: 0,
      cost: 0,
    };

    return (
      <View key={service.id} style={styles.serviceCard}>
        <View style={styles.serviceHeader}>
          <View style={styles.serviceInfo}>
            <Text style={styles.serviceIcon}>{service.icon}</Text>
            <View>
              <Text style={styles.serviceName}>{service.name}</Text>
              <Text style={styles.serviceDescription}>
                {service.description}
              </Text>
            </View>
          </View>

          <Switch
            value={service.enabled}
            onValueChange={(enabled) => toggleService(service.id, enabled)}
            disabled={loading}
          />
        </View>

        {/* Service details */}
        <View style={styles.serviceDetails}>
          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Type:</Text>
            <Text style={styles.detailValue}>
              {service.type === 'local' ? 'Local' : 'Cloud via Tor'}
            </Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Privacy:</Text>
            <Text style={styles.detailValue}>{service.privacy}</Text>
          </View>

          <View style={styles.detailRow}>
            <Text style={styles.detailLabel}>Cost:</Text>
            <Text style={styles.detailValue}>
              {service.type === 'local'
                ? service.cost
                : `$${stats.cost.toFixed(2)} spent`}
            </Text>
          </View>

          {service.enabled && (
            <View style={styles.detailRow}>
              <Text style={styles.detailLabel}>Queries:</Text>
              <Text style={styles.detailValue}>{stats.queries}</Text>
            </View>
          )}
        </View>

        {/* Action buttons */}
        {service.enabled && (
          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => openChat(service.id)}
            >
              <Text style={styles.actionButtonText}>💬 Chat</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => testService(service.id)}
            >
              <Text style={styles.actionButtonText}>🧪 Test</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>🤖 AI Assistants</Text>
        <Text style={styles.subtitle}>
          Privacy-focused AI integration for QWAMOS
        </Text>
      </View>

      {/* Loading indicator */}
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      )}

      {/* Services list */}
      <ScrollView style={styles.scrollView}>
        {services.map(renderServiceCard)}

        {/* Usage summary */}
        {usageStats && (
          <View style={styles.summaryCard}>
            <Text style={styles.summaryTitle}>📊 Total Usage</Text>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Total Queries:</Text>
              <Text style={styles.summaryValue}>
                {Object.values(usageStats).reduce(
                  (sum: number, s: any) => sum + s.queries,
                  0
                )}
              </Text>
            </View>
            <View style={styles.summaryRow}>
              <Text style={styles.summaryLabel}>Total Cost:</Text>
              <Text style={styles.summaryValue}>
                $
                {Object.values(usageStats)
                  .reduce((sum: number, s: any) => sum + s.cost, 0)
                  .toFixed(2)}
              </Text>
            </View>
          </View>
        )}

        {/* Privacy notice */}
        <View style={styles.noticeCard}>
          <Text style={styles.noticeTitle}>🔒 Privacy Notice</Text>
          <Text style={styles.noticeText}>
            • Kali GPT runs 100% locally with no network access{'\n'}
            • Cloud APIs (Claude, ChatGPT) route through Tor for anonymity{'\n'}
            • All requests are sanitized to remove PII before sending{'\n'}
            • API keys are encrypted with Kyber-1024 + ChaCha20
          </Text>
        </View>
      </ScrollView>

      {/* API Key Modal */}
      <Modal visible={showApiKeyModal} animationType="slide" transparent={true}>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Enter API Key</Text>
            <Text style={styles.modalDescription}>
              {selectedService === 'claude'
                ? 'Enter your Anthropic API key (sk-ant-...)'
                : 'Enter your OpenAI API key (sk-proj-...)'}
            </Text>

            <TextInput
              style={styles.input}
              placeholder="API Key"
              value={apiKey}
              onChangeText={setApiKey}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
            />

            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => {
                  setShowApiKeyModal(false);
                  setApiKey('');
                  setSelectedService(null);
                }}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.modalButton, styles.confirmButton]}
                onPress={enableWithApiKey}
              >
                <Text style={styles.confirmButtonText}>Enable</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
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
  serviceCard: {
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
  serviceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  serviceInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  serviceIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  serviceName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  serviceDescription: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  serviceDetails: {
    marginTop: 8,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 14,
    color: '#666',
  },
  detailValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  actionButtons: {
    flexDirection: 'row',
    marginTop: 12,
    gap: 8,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 14,
  },
  summaryCard: {
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#666',
  },
  summaryValue: {
    fontSize: 14,
    color: '#333',
    fontWeight: 'bold',
  },
  noticeCard: {
    backgroundColor: '#FFF9C4',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  noticeTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  noticeText: {
    fontSize: 13,
    color: '#555',
    lineHeight: 20,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 999,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 24,
    width: '80%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  modalDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: '#CCC',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    marginBottom: 16,
  },
  modalButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  modalButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  cancelButton: {
    backgroundColor: '#E0E0E0',
  },
  confirmButton: {
    backgroundColor: '#007AFF',
  },
  cancelButtonText: {
    color: '#333',
    fontWeight: 'bold',
  },
  confirmButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
});
