/**
 * Network Manager Service
 *
 * React Native service layer for communicating with Python network backend
 * Uses Native Modules to bridge to Python scripts
 */

import { NativeModules } from 'react-native';

const { QWAMOSNetworkBridge } = NativeModules;

export class NetworkManager {
  /**
   * Get current network status
   */
  static async getStatus(): Promise<any> {
    try {
      // Call Python network_manager.py status command
      const result = await QWAMOSNetworkBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/network/network_manager.py', 'status']
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to get network status:', error);
      throw error;
    }
  }

  /**
   * Switch network mode
   */
  static async switchMode(mode: string, config: any = {}): Promise<void> {
    try {
      const configJson = JSON.stringify(config);

      await QWAMOSNetworkBridge.executeCommand(
        '/usr/bin/python3',
        [
          '/opt/qwamos/network/network_manager.py',
          'switch',
          '--mode',
          mode,
          '--config',
          configJson,
        ]
      );
    } catch (error) {
      console.error('Failed to switch network mode:', error);
      throw error;
    }
  }

  /**
   * Stop all network services
   */
  static async stopAll(): Promise<void> {
    try {
      await QWAMOSNetworkBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/network/network_manager.py', 'stop']
      );
    } catch (error) {
      console.error('Failed to stop network services:', error);
      throw error;
    }
  }

  /**
   * Run network connectivity test
   */
  static async testConnectivity(): Promise<any> {
    try {
      const result = await QWAMOSNetworkBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/network/network_manager.py', 'test']
      );

      return JSON.parse(result);
    } catch (error) {
      console.error('Failed to test connectivity:', error);
      throw error;
    }
  }

  /**
   * Run IP leak detection tests
   */
  static async runLeakTest(): Promise<any> {
    try {
      const result = await QWAMOSNetworkBridge.executeCommand(
        '/usr/bin/python3',
        ['/opt/qwamos/network/tests/test_ip_leak.py']
      );

      // Read results from file
      const resultsJson = await QWAMOSNetworkBridge.readFile(
        '/tmp/qwamos_leak_test_results.json'
      );

      return JSON.parse(resultsJson);
    } catch (error) {
      console.error('Failed to run leak test:', error);
      throw error;
    }
  }

  /**
   * Update Tor bridges configuration
   */
  static async updateTorBridges(enabled: boolean): Promise<void> {
    try {
      // This would call a Python script to update Tor configuration
      await QWAMOSNetworkBridge.executeCommand(
        '/usr/bin/python3',
        [
          '/opt/qwamos/network/scripts/update_tor_config.py',
          '--bridges',
          enabled ? 'enable' : 'disable',
        ]
      );

      // Restart Tor service
      await QWAMOSNetworkBridge.executeCommand(
        'systemctl',
        ['restart', 'qwamos-tor.service']
      );
    } catch (error) {
      console.error('Failed to update Tor bridges:', error);
      throw error;
    }
  }

  /**
   * Get service logs
   */
  static async getServiceLogs(service: 'tor' | 'i2p' | 'dnscrypt'): Promise<string> {
    try {
      const result = await QWAMOSNetworkBridge.executeCommand(
        'journalctl',
        ['-u', `qwamos-${service}.service`, '-n', '50', '--no-pager']
      );

      return result;
    } catch (error) {
      console.error(`Failed to get ${service} logs:`, error);
      throw error;
    }
  }

  /**
   * Get current public IP
   */
  static async getPublicIP(): Promise<string> {
    try {
      const result = await QWAMOSNetworkBridge.executeCommand(
        'curl',
        ['-s', '--max-time', '10', 'https://icanhazip.com']
      );

      return result.trim();
    } catch (error) {
      console.error('Failed to get public IP:', error);
      throw error;
    }
  }

  /**
   * Check if using Tor
   */
  static async checkTorStatus(): Promise<{ using_tor: boolean; ip: string }> {
    try {
      const result = await QWAMOSNetworkBridge.executeCommand(
        'curl',
        ['-s', '--max-time', '15', 'https://check.torproject.org/api/ip']
      );

      const response = JSON.parse(result);

      return {
        using_tor: response.IsTor || false,
        ip: response.IP || 'unknown',
      };
    } catch (error) {
      console.error('Failed to check Tor status:', error);
      throw error;
    }
  }
}

/**
 * Native Module Interface
 *
 * This is the Java/Kotlin bridge that needs to be implemented
 * in the Android native code to execute shell commands.
 *
 * Example implementation in Java:
 *
 * @ReactMethod
 * public void executeCommand(String command, ReadableArray args, Promise promise) {
 *     try {
 *         ProcessBuilder pb = new ProcessBuilder();
 *         ArrayList<String> cmdList = new ArrayList<>();
 *         cmdList.add(command);
 *         for (int i = 0; i < args.size(); i++) {
 *             cmdList.add(args.getString(i));
 *         }
 *         pb.command(cmdList);
 *
 *         Process process = pb.start();
 *         BufferedReader reader = new BufferedReader(
 *             new InputStreamReader(process.getInputStream())
 *         );
 *
 *         StringBuilder output = new StringBuilder();
 *         String line;
 *         while ((line = reader.readLine()) != null) {
 *             output.append(line).append("\n");
 *         }
 *
 *         int exitCode = process.waitFor();
 *         if (exitCode == 0) {
 *             promise.resolve(output.toString());
 *         } else {
 *             promise.reject("EXEC_ERROR", "Command failed with code " + exitCode);
 *         }
 *     } catch (Exception e) {
 *         promise.reject("EXEC_ERROR", e.getMessage());
 *     }
 * }
 *
 * @ReactMethod
 * public void readFile(String path, Promise promise) {
 *     try {
 *         String content = new String(Files.readAllBytes(Paths.get(path)));
 *         promise.resolve(content);
 *     } catch (Exception e) {
 *         promise.reject("READ_ERROR", e.getMessage());
 *     }
 * }
 */
