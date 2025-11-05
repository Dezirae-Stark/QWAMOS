/**
 * QWAMOS Phase 9: AI App Builder Service
 *
 * TypeScript service layer for React Native app builder UI
 * Bridges to Python multi-AI pipeline
 *
 * @module AppBuilderService
 * @version 1.0.0
 */

import { NativeModules, NativeEventEmitter } from 'react-native';

const { QWAMOSAppBuilderBridge } = NativeModules;
const eventEmitter = new NativeEventEmitter(QWAMOSAppBuilderBridge);

export interface BuildProgress {
  stage: string;
  progress: number; // 0-100
  status: 'in_progress' | 'completed' | 'failed';
  details: string;
}

export interface GeneratedApp {
  name: string;
  description: string;
  code: Record<string, string>;
  securityScore: number;
  qualityScore: number;
  enhancements: string[];
  manifest: string;
  dependencies: string[];
  permissions: string[];
}

export interface DeploymentResult {
  vmName: string;
  installPath: string;
  status: string;
}

type ProgressCallback = (progress: BuildProgress) => void;

class AppBuilderServiceClass {
  private progressCallback: ProgressCallback | null = null;

  constructor() {
    // Listen for progress events
    eventEmitter.addListener('AppBuildProgress', (event) => {
      if (this.progressCallback) {
        this.progressCallback(event);
      }
    });
  }

  /**
   * Build app from user request
   */
  async buildApp(userRequest: string, userId: string): Promise<GeneratedApp> {
    try {
      const result = await QWAMOSAppBuilderBridge.buildApp(userRequest, userId);
      return JSON.parse(result);
    } catch (error) {
      throw new Error(`App build failed: ${error}`);
    }
  }

  /**
   * Deploy generated app to device
   */
  async deployApp(app: GeneratedApp): Promise<DeploymentResult> {
    try {
      const result = await QWAMOSAppBuilderBridge.deployApp(JSON.stringify(app));
      return JSON.parse(result);
    } catch (error) {
      throw new Error(`Deployment failed: ${error}`);
    }
  }

  /**
   * Apply enhancements to generated app
   */
  async applyEnhancements(
    app: GeneratedApp,
    selectedEnhancements: string[]
  ): Promise<GeneratedApp> {
    try {
      const result = await QWAMOSAppBuilderBridge.applyEnhancements(
        JSON.stringify(app),
        selectedEnhancements
      );
      return JSON.parse(result);
    } catch (error) {
      throw new Error(`Enhancement failed: ${error}`);
    }
  }

  /**
   * Get list of generated apps
   */
  async listGeneratedApps(): Promise<GeneratedApp[]> {
    try {
      const result = await QWAMOSAppBuilderBridge.listGeneratedApps();
      return JSON.parse(result);
    } catch (error) {
      throw new Error(`Failed to list apps: ${error}`);
    }
  }

  /**
   * Delete a generated app
   */
  async deleteApp(appName: string): Promise<void> {
    try {
      await QWAMOSAppBuilderBridge.deleteApp(appName);
    } catch (error) {
      throw new Error(`Failed to delete app: ${error}`);
    }
  }

  /**
   * Subscribe to build progress updates
   */
  onProgress(callback: ProgressCallback): void {
    this.progressCallback = callback;
  }

  /**
   * Get security audit details
   */
  async getSecurityAudit(appName: string): Promise<any> {
    try {
      const result = await QWAMOSAppBuilderBridge.getSecurityAudit(appName);
      return JSON.parse(result);
    } catch (error) {
      throw new Error(`Failed to get security audit: ${error}`);
    }
  }
}

export const AppBuilderService = new AppBuilderServiceClass();
