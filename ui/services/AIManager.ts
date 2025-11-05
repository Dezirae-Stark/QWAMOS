/**
 * AI Manager Service
 *
 * React Native service layer for communicating with Python AI backend
 * Uses Native Modules to bridge to Python AI scripts
 */

import { NativeModules } from 'react-native';

const { QWAMOSAIBridge } = NativeModules;

export interface AIStatus {
  'kali-gpt': {
    enabled: boolean;
    type: string;
    privacy: string;
    cost: string;
  };
  claude: {
    enabled: boolean;
    type: string;
    privacy: string;
    cost: string;
  };
  chatgpt: {
    enabled: boolean;
    type: string;
    privacy: string;
    cost: string;
  };
}

export interface UsageStats {
  'kali-gpt': {
    queries: number;
    tokens: number;
    cost: number;
  };
  claude: {
    queries: number;
    tokens: number;
    cost: number;
  };
  chatgpt: {
    queries: number;
    tokens: number;
    cost: number;
  };
}

export interface QueryResponse {
  content: string;
  context?: any;
  usage?: {
    input_tokens?: number;
    output_tokens?: number;
    total_tokens?: number;
  };
}

export class AIManager {
  /**
   * Get status of all AI services
   */
  static async getStatus(): Promise<AIStatus> {
    try {
      // Call Python ai_manager.py status command
      const result = await QWAMOSAIBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/ai/ai_manager.py',
        'status',
      ]);

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get AI status:', error);
      throw error;
    }
  }

  /**
   * Enable AI service
   *
   * @param serviceId - Service ID ('kali-gpt', 'claude', 'chatgpt')
   * @param apiKey - API key (required for cloud services)
   */
  static async enableService(
    serviceId: string,
    apiKey?: string
  ): Promise<void> {
    try {
      const args = ['/opt/qwamos/ai/ai_manager.py', 'enable', serviceId];

      if (apiKey) {
        args.push('--api-key', apiKey);
      }

      await QWAMOSAIBridge.executeCommand('/usr/bin/python3', args);
    } catch (error) {
      console.error(`Failed to enable ${serviceId}:`, error);
      throw error;
    }
  }

  /**
   * Disable AI service
   *
   * @param serviceId - Service ID
   */
  static async disableService(serviceId: string): Promise<void> {
    try {
      await QWAMOSAIBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/ai/ai_manager.py',
        'disable',
        serviceId,
      ]);
    } catch (error) {
      console.error(`Failed to disable ${serviceId}:`, error);
      throw error;
    }
  }

  /**
   * Query AI service
   *
   * @param serviceId - Service ID
   * @param prompt - User prompt
   * @param context - Optional conversation context
   */
  static async query(
    serviceId: string,
    prompt: string,
    context?: any
  ): Promise<QueryResponse> {
    try {
      const args = [
        '/opt/qwamos/ai/ai_manager.py',
        'query',
        serviceId,
        prompt,
      ];

      if (context) {
        args.push('--context', JSON.stringify(context));
      }

      const result = await QWAMOSAIBridge.executeCommand(
        '/usr/bin/python3',
        args,
        60 // 60 second timeout for AI queries
      );

      // Parse response
      try {
        return JSON.parse(result);
      } catch {
        // If not JSON, return as plain text response
        return { content: result };
      }
    } catch (error) {
      console.error(`Failed to query ${serviceId}:`, error);
      throw error;
    }
  }

  /**
   * Get usage statistics
   *
   * @param timeRange - Time range filter ('today', 'week', 'month', 'all')
   */
  static async getUsageStats(
    timeRange: 'today' | 'week' | 'month' | 'all' = 'all'
  ): Promise<UsageStats> {
    try {
      const result = await QWAMOSAIBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/ai/ai_manager.py',
        'stats',
        '--range',
        timeRange,
      ]);

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get usage stats:', error);
      throw error;
    }
  }

  /**
   * Reset usage statistics
   */
  static async resetStats(): Promise<void> {
    try {
      await QWAMOSAIBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/ai/ai_manager.py',
        'reset-stats',
      ]);
    } catch (error) {
      console.error('Failed to reset stats:', error);
      throw error;
    }
  }

  /**
   * Test AI service connection
   *
   * @param serviceId - Service ID
   */
  static async testService(
    serviceId: string
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const result = await QWAMOSAIBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/ai/ai_manager.py',
        'test',
        serviceId,
      ]);

      return JSON.parse(result);
    } catch (error: any) {
      return {
        success: false,
        error: error.message || 'Connection test failed',
      };
    }
  }

  /**
   * Get conversation history
   *
   * @param serviceId - Service ID
   */
  static async getConversationHistory(serviceId: string): Promise<any[]> {
    try {
      // Read conversation history from file
      const historyFile = `/opt/qwamos/ai/cache/${serviceId}_history.json`;

      const exists = await QWAMOSAIBridge.fileExists(historyFile);

      if (!exists) {
        return [];
      }

      const content = await QWAMOSAIBridge.readFile(historyFile);
      return JSON.parse(content);
    } catch (error) {
      console.error('Failed to load conversation history:', error);
      return [];
    }
  }

  /**
   * Save conversation history
   *
   * @param serviceId - Service ID
   * @param messages - Messages to save
   */
  static async saveConversationHistory(
    serviceId: string,
    messages: any[]
  ): Promise<void> {
    try {
      const historyFile = `/opt/qwamos/ai/cache/${serviceId}_history.json`;
      await QWAMOSAIBridge.writeFile(historyFile, JSON.stringify(messages));
    } catch (error) {
      console.error('Failed to save conversation history:', error);
      throw error;
    }
  }

  /**
   * Clear conversation history
   *
   * @param serviceId - Service ID
   */
  static async clearConversationHistory(serviceId: string): Promise<void> {
    try {
      await this.saveConversationHistory(serviceId, []);
    } catch (error) {
      console.error('Failed to clear conversation history:', error);
      throw error;
    }
  }

  /**
   * Get AI service logs
   *
   * @param serviceId - Service ID
   * @param lines - Number of lines to retrieve (default: 50)
   */
  static async getLogs(
    serviceId: string,
    lines: number = 50
  ): Promise<string> {
    try {
      const result = await QWAMOSAIBridge.executeCommand('journalctl', [
        '-u',
        `qwamos-ai-${serviceId}.service`,
        '-n',
        lines.toString(),
        '--no-pager',
      ]);

      return result;
    } catch (error) {
      console.error(`Failed to get ${serviceId} logs:`, error);
      throw error;
    }
  }

  /**
   * Restart AI service (systemd)
   *
   * @param serviceId - Service ID
   */
  static async restartService(serviceId: string): Promise<void> {
    try {
      await QWAMOSAIBridge.executeCommand('systemctl', [
        'restart',
        `qwamos-ai-${serviceId}.service`,
      ]);
    } catch (error) {
      console.error(`Failed to restart ${serviceId}:`, error);
      throw error;
    }
  }

  /**
   * Download Kali GPT model
   *
   * @param onProgress - Progress callback (percent: number)
   */
  static async downloadKaliGPTModel(
    onProgress?: (percent: number) => void
  ): Promise<void> {
    try {
      // This would call a Python script that downloads the model
      // and reports progress

      await QWAMOSAIBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/ai/kali_gpt/scripts/download_model.py'],
        600 // 10 minute timeout for large download
      );
    } catch (error) {
      console.error('Failed to download Kali GPT model:', error);
      throw error;
    }
  }

  /**
   * Check if Kali GPT model is downloaded
   */
  static async isKaliGPTModelDownloaded(): Promise<boolean> {
    try {
      const modelPath =
        '/opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf';
      return await QWAMOSAIBridge.fileExists(modelPath);
    } catch (error) {
      return false;
    }
  }

  /**
   * Get model download status
   */
  static async getModelDownloadStatus(): Promise<{
    downloaded: boolean;
    size?: number;
    path?: string;
  }> {
    try {
      const modelPath =
        '/opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf';
      const exists = await QWAMOSAIBridge.fileExists(modelPath);

      if (exists) {
        // Get file size
        const result = await QWAMOSAIBridge.executeCommand('stat', [
          '-c',
          '%s',
          modelPath,
        ]);

        return {
          downloaded: true,
          size: parseInt(result.trim(), 10),
          path: modelPath,
        };
      }

      return { downloaded: false };
    } catch (error) {
      return { downloaded: false };
    }
  }

  /**
   * Update API key for cloud service
   *
   * @param serviceId - Service ID ('claude' or 'chatgpt')
   * @param apiKey - New API key
   */
  static async updateApiKey(
    serviceId: 'claude' | 'chatgpt',
    apiKey: string
  ): Promise<void> {
    try {
      await QWAMOSAIBridge.executeCommand('/usr/bin/python3', [
        '/opt/qwamos/ai/ai_manager.py',
        'update-api-key',
        serviceId,
        apiKey,
      ]);
    } catch (error) {
      console.error(`Failed to update API key for ${serviceId}:`, error);
      throw error;
    }
  }

  /**
   * Get AI service configuration
   *
   * @param serviceId - Service ID
   */
  static async getConfig(serviceId: string): Promise<any> {
    try {
      const configFile = `/opt/qwamos/ai/config/${serviceId.replace('-', '_')}_config.json`;

      const content = await QWAMOSAIBridge.readFile(configFile);
      return JSON.parse(content);
    } catch (error) {
      console.error(`Failed to get config for ${serviceId}:`, error);
      throw error;
    }
  }

  /**
   * Update AI service configuration
   *
   * @param serviceId - Service ID
   * @param config - Configuration object
   */
  static async updateConfig(
    serviceId: string,
    config: any
  ): Promise<void> {
    try {
      const configFile = `/opt/qwamos/ai/config/${serviceId.replace('-', '_')}_config.json`;

      await QWAMOSAIBridge.writeFile(
        configFile,
        JSON.stringify(config, null, 2)
      );
    } catch (error) {
      console.error(`Failed to update config for ${serviceId}:`, error);
      throw error;
    }
  }
}
