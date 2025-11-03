/**
 * Network Mode Card Component
 *
 * Display card for each network isolation mode
 */

import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
} from 'react-native';

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

interface Props {
  mode: NetworkMode;
  isActive: boolean;
  isDisabled: boolean;
  onPress: () => void;
}

const getSpeedColor = (speed: string): string => {
  switch (speed) {
    case 'Fast':
      return '#4CAF50';
    case 'Medium':
      return '#FFC107';
    case 'Slow':
      return '#FF5722';
    default:
      return '#888';
  }
};

const getAnonymityColor = (anonymity: string): string => {
  switch (anonymity) {
    case 'None':
      return '#F44336';
    case 'Low':
      return '#FF9800';
    case 'Medium':
      return '#FFC107';
    case 'High':
      return '#4CAF50';
    case 'Maximum':
      return '#00BCD4';
    default:
      return '#888';
  }
};

export const NetworkModeCard: React.FC<Props> = ({
  mode,
  isActive,
  isDisabled,
  onPress,
}) => {
  const cardStyle: ViewStyle[] = [
    styles.card,
    isActive && styles.cardActive,
    isDisabled && styles.cardDisabled,
  ];

  return (
    <TouchableOpacity
      style={cardStyle}
      onPress={onPress}
      disabled={isDisabled || isActive}
      activeOpacity={0.7}
    >
      {/* Mode Icon & Name */}
      <View style={styles.header}>
        <Text style={styles.icon}>{mode.icon}</Text>
        <View style={styles.headerText}>
          <Text style={styles.modeName}>{mode.name}</Text>
          {isActive && (
            <View style={styles.activeBadge}>
              <Text style={styles.activeBadgeText}>ACTIVE</Text>
            </View>
          )}
        </View>
      </View>

      {/* Description */}
      <Text style={styles.description}>{mode.description}</Text>

      {/* Metrics */}
      <View style={styles.metrics}>
        <View style={styles.metric}>
          <Text style={styles.metricLabel}>Speed</Text>
          <View style={[styles.metricBadge, { borderColor: getSpeedColor(mode.speed) }]}>
            <Text style={[styles.metricValue, { color: getSpeedColor(mode.speed) }]}>
              {mode.speed}
            </Text>
          </View>
        </View>

        <View style={styles.metric}>
          <Text style={styles.metricLabel}>Anonymity</Text>
          <View style={[styles.metricBadge, { borderColor: getAnonymityColor(mode.anonymity) }]}>
            <Text style={[styles.metricValue, { color: getAnonymityColor(mode.anonymity) }]}>
              {mode.anonymity}
            </Text>
          </View>
        </View>
      </View>

      {/* Services */}
      {mode.services.length > 0 && (
        <View style={styles.servicesContainer}>
          <Text style={styles.servicesLabel}>Services:</Text>
          <View style={styles.services}>
            {mode.services.map((service) => (
              <View key={service} style={styles.serviceTag}>
                <Text style={styles.serviceText}>{service}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Warning */}
      {mode.warning && (
        <View style={styles.warningContainer}>
          <Text style={styles.warningIcon}>⚠️</Text>
          <Text style={styles.warningText}>{mode.warning}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1a1a1a',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#333',
  },
  cardActive: {
    borderColor: '#00BCD4',
    backgroundColor: '#1a2a2a',
  },
  cardDisabled: {
    opacity: 0.5,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  icon: {
    fontSize: 32,
    marginRight: 12,
  },
  headerText: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  modeName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
  },
  activeBadge: {
    backgroundColor: '#00BCD4',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 4,
  },
  activeBadgeText: {
    color: '#000',
    fontSize: 11,
    fontWeight: '700',
  },
  description: {
    fontSize: 14,
    color: '#aaa',
    marginBottom: 12,
  },
  metrics: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 12,
  },
  metric: {
    flex: 1,
  },
  metricLabel: {
    fontSize: 12,
    color: '#888',
    marginBottom: 5,
  },
  metricBadge: {
    borderWidth: 1,
    borderRadius: 6,
    paddingVertical: 6,
    paddingHorizontal: 10,
    alignItems: 'center',
  },
  metricValue: {
    fontSize: 13,
    fontWeight: '600',
  },
  servicesContainer: {
    marginBottom: 8,
  },
  servicesLabel: {
    fontSize: 12,
    color: '#888',
    marginBottom: 6,
  },
  services: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  serviceTag: {
    backgroundColor: '#2a2a2a',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#444',
  },
  serviceText: {
    fontSize: 12,
    color: '#fff',
  },
  warningContainer: {
    flexDirection: 'row',
    backgroundColor: '#2a1a1a',
    padding: 10,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#FFA726',
    marginTop: 8,
  },
  warningIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  warningText: {
    flex: 1,
    fontSize: 12,
    color: '#FFA726',
  },
});
