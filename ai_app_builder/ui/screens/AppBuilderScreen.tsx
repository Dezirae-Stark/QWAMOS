/**
 * QWAMOS Phase 9: AI App Builder - Main UI Screen
 *
 * User interface for building custom apps with AI:
 * - Natural language app request
 * - Real-time progress tracking
 * - Code preview with security audit
 * - Enhancement suggestions
 * - User approval workflow
 *
 * @module AppBuilderScreen
 * @version 1.0.0
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator
} from 'react-native';
import { AppBuilderService } from '../services/AppBuilderService';
import CodePreviewModal from '../components/CodePreviewModal';
import SecurityAuditReport from '../components/SecurityAuditReport';
import EnhancementsList from '../components/EnhancementsList';

interface BuildProgress {
  stage: string;
  progress: number; // 0-100
  status: string;
  details: string;
}

interface GeneratedApp {
  name: string;
  description: string;
  code: Record<string, string>;
  securityScore: number;
  qualityScore: number;
  enhancements: string[];
  manifest: string;
}

const AppBuilderScreen: React.FC = () => {
  const [request, setRequest] = useState<string>('');
  const [building, setBuilding] = useState<boolean>(false);
  const [progress, setProgress] = useState<BuildProgress | null>(null);
  const [generatedApp, setGeneratedApp] = useState<GeneratedApp | null>(null);
  const [showCodePreview, setShowCodePreview] = useState<boolean>(false);
  const [showAuditReport, setShowAuditReport] = useState<boolean>(false);

  /**
   * Start app building process
   */
  const startBuilding = async () => {
    if (!request.trim()) {
      Alert.alert('Error', 'Please describe the app you want to build');
      return;
    }

    setBuilding(true);
    setProgress({
      stage: 'Initializing...',
      progress: 0,
      status: 'in_progress',
      details: 'Starting AI coordination pipeline'
    });

    try {
      // Subscribe to progress updates
      AppBuilderService.onProgress((progressUpdate) => {
        setProgress(progressUpdate);
      });

      // Start build
      const app = await AppBuilderService.buildApp(request, 'user123');

      setGeneratedApp(app);
      setBuilding(false);

      // Show success with approval prompt
      Alert.alert(
        '✅ App Generated Successfully!',
        `${app.name} is ready for review.\n\n` +
        `Security Score: ${app.securityScore}/100\n` +
        `Quality Score: ${app.qualityScore}/100\n\n` +
        `Would you like to review the code and enhancements?`,
        [
          { text: 'Review Code', onPress: () => setShowCodePreview(true) },
          { text: 'Review Security', onPress: () => setShowAuditReport(true) },
          { text: 'Deploy Now', onPress: handleDeploy, style: 'default' }
        ]
      );

    } catch (error: any) {
      setBuilding(false);
      Alert.alert(
        'Build Failed',
        error.message || 'An error occurred during app generation'
      );
    }
  };

  /**
   * Handle app deployment
   */
  const handleDeploy = async () => {
    if (!generatedApp) return;

    Alert.alert(
      'Deploy App?',
      `This will:\n` +
      `1. Build APK in isolated VM\n` +
      `2. Run final security scans\n` +
      `3. Deploy to dedicated VM\n\n` +
      `Permissions requested: ${generatedApp.manifest.includes('INTERNET') ? 'INTERNET' : 'None'}\n\n` +
      `Continue?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Deploy',
          style: 'default',
          onPress: async () => {
            try {
              const result = await AppBuilderService.deployApp(generatedApp);
              Alert.alert(
                '✅ Deployment Complete',
                `${generatedApp.name} has been deployed!\n\n` +
                `VM: ${result.vmName}\n` +
                `Location: ${result.installPath}`
              );
            } catch (error: any) {
              Alert.alert('Deployment Failed', error.message);
            }
          }
        }
      ]
    );
  };

  /**
   * Apply selected enhancements
   */
  const applyEnhancements = async (selectedEnhancements: string[]) => {
    if (!generatedApp) return;

    Alert.alert(
      'Apply Enhancements?',
      `This will rebuild the app with ${selectedEnhancements.length} enhancements.\n\n` +
      `The app will go through security audit again.\n\n` +
      `Continue?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Apply',
          onPress: async () => {
            try {
              const enhanced = await AppBuilderService.applyEnhancements(
                generatedApp,
                selectedEnhancements
              );
              setGeneratedApp(enhanced);
              Alert.alert('✅ Enhancements Applied', 'App has been updated');
            } catch (error: any) {
              Alert.alert('Enhancement Failed', error.message);
            }
          }
        }
      ]
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>🤖 AI App Builder</Text>
        <Text style={styles.headerSubtitle}>
          Build custom apps with Kali GPT + Claude Code + ChatGPT
        </Text>
      </View>

      {/* Request Input */}
      <View style={styles.inputSection}>
        <Text style={styles.label}>Describe your app:</Text>
        <TextInput
          style={styles.textInput}
          value={request}
          onChangeText={setRequest}
          placeholder="Example: Build me a todo app with encryption and dark mode..."
          placeholderTextColor="#666"
          multiline
          numberOfLines={6}
          editable={!building}
        />

        <TouchableOpacity
          style={[styles.buildButton, building && styles.buildButtonDisabled]}
          onPress={startBuilding}
          disabled={building}
        >
          {building ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buildButtonText}>🚀 Build App</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Progress Tracker */}
      {progress && (
        <View style={styles.progressSection}>
          <Text style={styles.progressTitle}>{progress.stage}</Text>
          <View style={styles.progressBarContainer}>
            <View
              style={[styles.progressBar, { width: `${progress.progress}%` }]}
            />
          </View>
          <Text style={styles.progressDetails}>{progress.details}</Text>
          <Text style={styles.progressPercent}>{progress.progress}%</Text>
        </View>
      )}

      {/* Generated App Summary */}
      {generatedApp && !building && (
        <ScrollView style={styles.resultsSection}>
          <View style={styles.resultCard}>
            <Text style={styles.resultTitle}>✅ {generatedApp.name}</Text>
            <Text style={styles.resultDescription}>{generatedApp.description}</Text>

            {/* Scores */}
            <View style={styles.scoresRow}>
              <View style={styles.scoreCard}>
                <Text style={styles.scoreLabel}>Security</Text>
                <Text
                  style={[
                    styles.scoreValue,
                    { color: generatedApp.securityScore >= 90 ? '#00ff00' : '#ffaa00' }
                  ]}
                >
                  {generatedApp.securityScore}/100
                </Text>
              </View>

              <View style={styles.scoreCard}>
                <Text style={styles.scoreLabel}>Quality</Text>
                <Text style={styles.scoreValue}>
                  {generatedApp.qualityScore}/100
                </Text>
              </View>
            </View>

            {/* Action Buttons */}
            <View style={styles.actionsRow}>
              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => setShowCodePreview(true)}
              >
                <Text style={styles.actionButtonText}>📝 View Code</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.actionButton}
                onPress={() => setShowAuditReport(true)}
              >
                <Text style={styles.actionButtonText}>🔒 Security Report</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.actionButton, styles.deployButton]}
                onPress={handleDeploy}
              >
                <Text style={[styles.actionButtonText, styles.deployButtonText]}>
                  🚀 Deploy
                </Text>
              </TouchableOpacity>
            </View>

            {/* Enhancements */}
            {generatedApp.enhancements.length > 0 && (
              <View style={styles.enhancementsSection}>
                <Text style={styles.enhancementsTitle}>
                  💡 Suggested Enhancements ({generatedApp.enhancements.length})
                </Text>
                <EnhancementsList
                  enhancements={generatedApp.enhancements}
                  onApply={applyEnhancements}
                />
              </View>
            )}
          </View>
        </ScrollView>
      )}

      {/* Modals */}
      {generatedApp && (
        <>
          <CodePreviewModal
            visible={showCodePreview}
            code={generatedApp.code}
            onClose={() => setShowCodePreview(false)}
          />

          <SecurityAuditReport
            visible={showAuditReport}
            securityScore={generatedApp.securityScore}
            qualityScore={generatedApp.qualityScore}
            manifest={generatedApp.manifest}
            onClose={() => setShowAuditReport(false)}
          />
        </>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a'
  },
  header: {
    padding: 20,
    backgroundColor: '#1a1a1a',
    borderBottomWidth: 2,
    borderBottomColor: '#00ff00'
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#00ff00',
    marginBottom: 5
  },
  headerSubtitle: {
    fontSize: 12,
    color: '#999'
  },
  inputSection: {
    padding: 20
  },
  label: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 10,
    fontWeight: '500'
  },
  textInput: {
    backgroundColor: '#1a1a1a',
    color: '#fff',
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    fontSize: 14,
    minHeight: 150,
    textAlignVertical: 'top'
  },
  buildButton: {
    backgroundColor: '#00ff00',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 15
  },
  buildButtonDisabled: {
    backgroundColor: '#003300',
    opacity: 0.5
  },
  buildButtonText: {
    color: '#000',
    fontSize: 16,
    fontWeight: 'bold'
  },
  progressSection: {
    padding: 20,
    backgroundColor: '#1a1a1a',
    margin: 20,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#00ff00'
  },
  progressTitle: {
    color: '#00ff00',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10
  },
  progressBarContainer: {
    height: 8,
    backgroundColor: '#333',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 10
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#00ff00'
  },
  progressDetails: {
    color: '#999',
    fontSize: 12,
    marginBottom: 5
  },
  progressPercent: {
    color: '#00ff00',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'right'
  },
  resultsSection: {
    flex: 1,
    padding: 20
  },
  resultCard: {
    backgroundColor: '#1a1a1a',
    padding: 20,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#00ff00'
  },
  resultTitle: {
    color: '#00ff00',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10
  },
  resultDescription: {
    color: '#ccc',
    fontSize: 14,
    marginBottom: 20
  },
  scoresRow: {
    flexDirection: 'row',
    marginBottom: 20,
    gap: 10
  },
  scoreCard: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#333',
    alignItems: 'center'
  },
  scoreLabel: {
    color: '#999',
    fontSize: 12,
    marginBottom: 5
  },
  scoreValue: {
    color: '#00ff00',
    fontSize: 24,
    fontWeight: 'bold'
  },
  actionsRow: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 20
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#2a2a2a',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#00ff00'
  },
  actionButtonText: {
    color: '#00ff00',
    fontSize: 12,
    fontWeight: '500'
  },
  deployButton: {
    backgroundColor: '#003300'
  },
  deployButtonText: {
    fontWeight: 'bold'
  },
  enhancementsSection: {
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 1,
    borderTopColor: '#333'
  },
  enhancementsTitle: {
    color: '#ffaa00',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 10
  }
});

export default AppBuilderScreen;
