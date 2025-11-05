/**
 * QWAMOS AI Usage Statistics Dashboard
 *
 * Displays detailed usage statistics and cost tracking for AI assistants
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { AIManager } from '../services/AIManager';

interface UsageStats {
  queries: number;
  tokens: number;
  cost: number;
}

interface ServiceStats {
  'kali-gpt': UsageStats;
  claude: UsageStats;
  chatgpt: UsageStats;
}

export const AIStatsScreen = () => {
  const [stats, setStats] = useState<ServiceStats | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [refreshing, setRefreshing] = useState<boolean>(false);
  const [timeRange, setTimeRange] = useState<'today' | 'week' | 'month' | 'all'>(
    'all'
  );

  useEffect(() => {
    loadStats();
  }, [timeRange]);

  /**
   * Load usage statistics
   */
  const loadStats = async () => {
    try {
      setLoading(true);
      const usageStats = await AIManager.getUsageStats(timeRange);
      setStats(usageStats);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  /**
   * Handle pull-to-refresh
   */
  const onRefresh = () => {
    setRefreshing(true);
    loadStats();
  };

  /**
   * Reset statistics
   */
  const resetStats = async () => {
    try {
      await AIManager.resetStats();
      await loadStats();
    } catch (error) {
      console.error('Failed to reset stats:', error);
    }
  };

  /**
   * Calculate totals
   */
  const getTotals = () => {
    if (!stats) return { queries: 0, tokens: 0, cost: 0 };

    return {
      queries:
        stats['kali-gpt'].queries +
        stats.claude.queries +
        stats.chatgpt.queries,
      tokens:
        stats['kali-gpt'].tokens + stats.claude.tokens + stats.chatgpt.tokens,
      cost: stats['kali-gpt'].cost + stats.claude.cost + stats.chatgpt.cost,
    };
  };

  /**
   * Render service stats card
   */
  const renderServiceCard = (
    serviceId: keyof ServiceStats,
    serviceName: string,
    icon: string,
    color: string
  ) => {
    if (!stats) return null;

    const serviceStats = stats[serviceId];
    const totals = getTotals();
    const percentage =
      totals.queries > 0
        ? ((serviceStats.queries / totals.queries) * 100).toFixed(1)
        : '0.0';

    return (
      <View style={[styles.serviceCard, { borderLeftColor: color }]}>
        <View style={styles.serviceCardHeader}>
          <View style={styles.serviceCardTitle}>
            <Text style={styles.serviceIcon}>{icon}</Text>
            <Text style={styles.serviceName}>{serviceName}</Text>
          </View>
          <Text style={styles.servicePercentage}>{percentage}%</Text>
        </View>

        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Queries</Text>
            <Text style={styles.statValue}>
              {serviceStats.queries.toLocaleString()}
            </Text>
          </View>

          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Tokens</Text>
            <Text style={styles.statValue}>
              {serviceStats.tokens.toLocaleString()}
            </Text>
          </View>

          <View style={styles.statItem}>
            <Text style={styles.statLabel}>Cost</Text>
            <Text style={[styles.statValue, { color }]}>
              ${serviceStats.cost.toFixed(2)}
            </Text>
          </View>
        </View>
      </View>
    );
  };

  if (loading && !stats) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading statistics...</Text>
      </View>
    );
  }

  const totals = getTotals();

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>📊 AI Usage Statistics</Text>
        <TouchableOpacity onPress={resetStats} style={styles.resetButton}>
          <Text style={styles.resetButtonText}>Reset</Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Time range selector */}
        <View style={styles.timeRangeContainer}>
          {(['today', 'week', 'month', 'all'] as const).map((range) => (
            <TouchableOpacity
              key={range}
              style={[
                styles.timeRangeButton,
                timeRange === range && styles.timeRangeButtonActive,
              ]}
              onPress={() => setTimeRange(range)}
            >
              <Text
                style={[
                  styles.timeRangeText,
                  timeRange === range && styles.timeRangeTextActive,
                ]}
              >
                {range.charAt(0).toUpperCase() + range.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Total summary */}
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Total Usage</Text>
          <View style={styles.summaryGrid}>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryValue}>
                {totals.queries.toLocaleString()}
              </Text>
              <Text style={styles.summaryLabel}>Total Queries</Text>
            </View>

            <View style={styles.summaryItem}>
              <Text style={styles.summaryValue}>
                {totals.tokens.toLocaleString()}
              </Text>
              <Text style={styles.summaryLabel}>Total Tokens</Text>
            </View>

            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, styles.costValue]}>
                ${totals.cost.toFixed(2)}
              </Text>
              <Text style={styles.summaryLabel}>Total Cost</Text>
            </View>
          </View>
        </View>

        {/* Service breakdown */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Service Breakdown</Text>

          {renderServiceCard('kali-gpt', 'Kali GPT', '🤖', '#4CAF50')}
          {renderServiceCard('claude', 'Claude', '🧠', '#7B2FFF')}
          {renderServiceCard('chatgpt', 'ChatGPT', '💬', '#10A37F')}
        </View>

        {/* Cost projection */}
        <View style={styles.projectionCard}>
          <Text style={styles.projectionTitle}>Monthly Cost Projection</Text>
          <View style={styles.projectionContent}>
            <Text style={styles.projectionValue}>
              ${(totals.cost * 30).toFixed(2)}
            </Text>
            <Text style={styles.projectionLabel}>
              Based on {timeRange === 'today' ? 'today' : 'current'} usage
            </Text>
          </View>
        </View>

        {/* Cost breakdown */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Cost Analysis</Text>

          <View style={styles.costCard}>
            <View style={styles.costRow}>
              <Text style={styles.costLabel}>Kali GPT (Local)</Text>
              <Text style={styles.costValue}>$0.00</Text>
            </View>
            <Text style={styles.costNote}>
              ✅ 100% free - runs entirely on-device
            </Text>
          </View>

          <View style={styles.costCard}>
            <View style={styles.costRow}>
              <Text style={styles.costLabel}>Claude (API)</Text>
              <Text style={styles.costValue}>
                ${stats?.claude.cost.toFixed(2) || '0.00'}
              </Text>
            </View>
            <Text style={styles.costNote}>
              💰 $0.003/1K input • $0.015/1K output tokens
            </Text>
          </View>

          <View style={styles.costCard}>
            <View style={styles.costRow}>
              <Text style={styles.costLabel}>ChatGPT (API)</Text>
              <Text style={styles.costValue}>
                ${stats?.chatgpt.cost.toFixed(2) || '0.00'}
              </Text>
            </View>
            <Text style={styles.costNote}>
              💰 $0.01/1K input • $0.03/1K output tokens
            </Text>
          </View>
        </View>

        {/* Savings info */}
        {stats && (
          <View style={styles.savingsCard}>
            <Text style={styles.savingsTitle}>💡 Cost Savings Tip</Text>
            <Text style={styles.savingsText}>
              Use Kali GPT for penetration testing queries to save on API costs.
              It runs 100% locally with zero costs.
              {'\n\n'}
              Kali GPT has answered {stats['kali-gpt'].queries} queries at $0
              cost, saving approximately $
              {((stats['kali-gpt'].queries * 0.02) / 1000).toFixed(2)} compared
              to cloud APIs.
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
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
  resetButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#FF3B30',
    borderRadius: 6,
  },
  resetButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: 'bold',
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  timeRangeContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 8,
  },
  timeRangeButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    alignItems: 'center',
  },
  timeRangeButtonActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  timeRangeText: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  timeRangeTextActive: {
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
  summaryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  summaryGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
  },
  costValue: {
    color: '#FF9500',
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  serviceCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  serviceCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  serviceCardTitle: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  serviceIcon: {
    fontSize: 24,
    marginRight: 8,
  },
  serviceName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  servicePercentage: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  statsGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  projectionCard: {
    backgroundColor: '#E3F2FD',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
  },
  projectionTitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  projectionContent: {
    alignItems: 'center',
  },
  projectionValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  projectionLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  costCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
  },
  costRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  costLabel: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  costNote: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  savingsCard: {
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  savingsTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  savingsText: {
    fontSize: 14,
    color: '#555',
    lineHeight: 20,
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
});
