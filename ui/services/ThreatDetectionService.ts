/**
 * Threat Detection Service
 *
 * TypeScript service layer for communicating with Python ML threat detection backend
 */

import { NativeModules } from 'react-native';

const { QWAMOSThreatBridge } = NativeModules;

export interface DetectorStatus {
  network_anomaly: boolean;
  file_system: boolean;
  system_call: boolean;
}

export interface ThreatSummary {
  total_threats: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  last_24h: number;
}

export interface Threat {
  id: string;
  type: string;
  severity: string;
  timestamp: number;
  status: string;
  description: string;
  details: any;
}

export interface DetectorStats {
  network_anomaly: {
    packets_processed: number;
    anomalies_detected: number;
    detection_rate: number;
  };
  file_system: {
    events_processed: number;
    threats_detected: number;
  };
  system_call: {
    syscalls_processed: number;
    threats_detected: number;
  };
}

export class ThreatDetectionService {
  /**
   * Get status of all ML detectors
   */
  static async getDetectorStatus(): Promise<DetectorStatus> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/get_detector_status.py']
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get detector status:', error);
      throw error;
    }
  }

  /**
   * Start ML detector
   */
  static async startDetector(
    detector: 'network_anomaly' | 'file_system' | 'system_call'
  ): Promise<void> {
    try {
      await QWAMOSThreatBridge.executeCommand('systemctl', [
        'start',
        `qwamos-ml-${detector}.service`,
      ]);
    } catch (error) {
      console.error(`Failed to start ${detector} detector:`, error);
      throw error;
    }
  }

  /**
   * Stop ML detector
   */
  static async stopDetector(
    detector: 'network_anomaly' | 'file_system' | 'system_call'
  ): Promise<void> {
    try {
      await QWAMOSThreatBridge.executeCommand('systemctl', [
        'stop',
        `qwamos-ml-${detector}.service`,
      ]);
    } catch (error) {
      console.error(`Failed to stop ${detector} detector:`, error);
      throw error;
    }
  }

  /**
   * Get threat summary statistics
   */
  static async getThreatSummary(): Promise<ThreatSummary> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/get_threat_summary.py']
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get threat summary:', error);
      throw error;
    }
  }

  /**
   * Get recent threats
   */
  static async getRecentThreats(limit: number = 10): Promise<Threat[]> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        [
          '/opt/qwamos/security/scripts/get_recent_threats.py',
          '--limit',
          limit.toString(),
        ]
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get recent threats:', error);
      throw error;
    }
  }

  /**
   * Get threat by ID
   */
  static async getThreat(threatId: string): Promise<Threat> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/get_threat.py', '--id', threatId]
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get threat:', error);
      throw error;
    }
  }

  /**
   * Calculate system health score (0-100)
   */
  static async getSystemHealth(): Promise<number> {
    try {
      const summary = await this.getThreatSummary();

      // Calculate health based on threat severity
      let health = 100;

      // Critical threats have highest impact
      health -= summary.critical * 10;

      // High threats
      health -= summary.high * 5;

      // Medium threats
      health -= summary.medium * 2;

      // Low threats
      health -= summary.low * 0.5;

      // Clamp to 0-100
      return Math.max(0, Math.min(100, Math.round(health)));
    } catch (error) {
      console.error('Failed to calculate system health:', error);
      return 50; // Return neutral health on error
    }
  }

  /**
   * Get detector statistics
   */
  static async getDetectorStats(): Promise<DetectorStats> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/get_detector_stats.py']
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get detector stats:', error);
      throw error;
    }
  }

  /**
   * Acknowledge a threat (mark as reviewed)
   */
  static async acknowledgeThreat(threatId: string): Promise<void> {
    try {
      await QWAMOSThreatBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/security/scripts/acknowledge_threat.py',
        '--id',
        threatId,
      ]);
    } catch (error) {
      console.error('Failed to acknowledge threat:', error);
      throw error;
    }
  }

  /**
   * Dismiss a false positive threat
   */
  static async dismissThreat(threatId: string): Promise<void> {
    try {
      await QWAMOSThreatBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/security/scripts/dismiss_threat.py',
        '--id',
        threatId,
      ]);
    } catch (error) {
      console.error('Failed to dismiss threat:', error);
      throw error;
    }
  }

  /**
   * Get AI response for a threat
   */
  static async getAIResponse(threatId: string): Promise<any> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/get_ai_response.py', '--id', threatId]
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get AI response:', error);
      throw error;
    }
  }

  /**
   * Execute action for a threat
   */
  static async executeAction(
    threatId: string,
    actionType: string
  ): Promise<void> {
    try {
      await QWAMOSThreatBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/security/scripts/execute_action.py',
        '--threat-id',
        threatId,
        '--action',
        actionType,
      ]);
    } catch (error) {
      console.error('Failed to execute action:', error);
      throw error;
    }
  }

  /**
   * Run manual threat scan
   */
  static async runScan(scanType: 'quick' | 'full' = 'quick'): Promise<void> {
    try {
      await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/run_scan.py', '--type', scanType],
        300 // 5 minute timeout for scans
      );
    } catch (error) {
      console.error('Failed to run scan:', error);
      throw error;
    }
  }

  /**
   * Get quarantined files
   */
  static async getQuarantinedFiles(): Promise<any[]> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/list_quarantined_files.py']
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get quarantined files:', error);
      throw error;
    }
  }

  /**
   * Restore file from quarantine
   */
  static async restoreFile(quarantinePath: string): Promise<void> {
    try {
      await QWAMOSThreatBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/security/scripts/restore_file.py',
        '--path',
        quarantinePath,
      ]);
    } catch (error) {
      console.error('Failed to restore file:', error);
      throw error;
    }
  }

  /**
   * Get ML model information
   */
  static async getModelInfo(): Promise<any> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/get_model_info.py']
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get model info:', error);
      throw error;
    }
  }

  /**
   * Update ML models
   */
  static async updateModels(): Promise<void> {
    try {
      await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/security/scripts/update_models.py'],
        600 // 10 minute timeout for model updates
      );
    } catch (error) {
      console.error('Failed to update models:', error);
      throw error;
    }
  }

  /**
   * Get threat detection logs
   */
  static async getLogs(lines: number = 100): Promise<string> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand('journalctl', [
        '-u',
        'qwamos-ml-*.service',
        '-n',
        lines.toString(),
        '--no-pager',
      ]);

      return result;
    } catch (error) {
      console.error('Failed to get logs:', error);
      throw error;
    }
  }

  /**
   * Export threat report
   */
  static async exportReport(
    startDate: Date,
    endDate: Date,
    format: 'json' | 'pdf' = 'json'
  ): Promise<string> {
    try {
      const result = await QWAMOSThreatBridge.executeCommand(
        '/usr/bin/python3',
        [
          '/opt/qwamos/security/scripts/export_report.py',
          '--start',
          startDate.toISOString(),
          '--end',
          endDate.toISOString(),
          '--format',
          format,
        ],
        120 // 2 minute timeout
      );

      return result; // Returns path to generated report
    } catch (error) {
      console.error('Failed to export report:', error);
      throw error;
    }
  }
}
