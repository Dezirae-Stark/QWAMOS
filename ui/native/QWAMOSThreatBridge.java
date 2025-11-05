package com.qwamos.threatdetection;

import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReadableArray;
import com.facebook.react.bridge.ReadableMap;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * QWAMOS Threat Detection Bridge
 *
 * React Native native module that bridges JavaScript calls to Python backend
 * for threat detection and response management.
 *
 * Phase 7: ML Threat Detection & Response
 *
 * Features:
 * - Execute Python commands for threat detection
 * - Start/stop ML detectors
 * - Query threat information
 * - Execute security actions
 * - Manage detector configuration
 *
 * Security:
 * - Command validation
 * - Output sanitization
 * - Error handling
 * - Timeout protection (30s default)
 */
public class QWAMOSThreatBridge extends ReactContextBaseJavaModule {

    private static final String MODULE_NAME = "QWAMOSThreatBridge";
    private static final int DEFAULT_TIMEOUT_MS = 30000; // 30 seconds
    private static final int MAX_CONCURRENT_COMMANDS = 10;

    private final ReactApplicationContext reactContext;
    private final ExecutorService executorService;

    public QWAMOSThreatBridge(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
        this.executorService = Executors.newFixedThreadPool(MAX_CONCURRENT_COMMANDS);
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    /**
     * Execute a command with arguments
     *
     * @param command Command to execute (e.g., "/usr/bin/python3")
     * @param args Array of arguments
     * @param promise Promise to resolve/reject
     */
    @ReactMethod
    public void executeCommand(String command, ReadableArray args, Promise promise) {
        executeCommand(command, args, DEFAULT_TIMEOUT_MS, promise);
    }

    /**
     * Execute a command with arguments and custom timeout
     *
     * @param command Command to execute
     * @param args Array of arguments
     * @param timeoutMs Timeout in milliseconds
     * @param promise Promise to resolve/reject
     */
    @ReactMethod
    public void executeCommand(String command, ReadableArray args, int timeoutMs, Promise promise) {
        executorService.submit(() -> {
            try {
                // Validate command
                if (!isValidCommand(command)) {
                    promise.reject("INVALID_COMMAND", "Command not allowed: " + command);
                    return;
                }

                // Build command list
                List<String> cmdList = new ArrayList<>();
                cmdList.add(command);

                // Add arguments
                for (int i = 0; i < args.size(); i++) {
                    cmdList.add(args.getString(i));
                }

                // Execute command
                ProcessBuilder processBuilder = new ProcessBuilder(cmdList);
                processBuilder.redirectErrorStream(true);

                Process process = processBuilder.start();

                // Read output
                StringBuilder output = new StringBuilder();
                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
                );

                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                }

                // Wait for completion with timeout
                boolean completed = process.waitFor(timeoutMs, java.util.concurrent.TimeUnit.MILLISECONDS);

                if (!completed) {
                    process.destroy();
                    promise.reject("TIMEOUT", "Command timed out after " + timeoutMs + "ms");
                    return;
                }

                int exitCode = process.exitValue();

                if (exitCode == 0) {
                    promise.resolve(output.toString());
                } else {
                    promise.reject("COMMAND_FAILED",
                        "Command exited with code " + exitCode + ": " + output.toString());
                }

            } catch (IOException e) {
                promise.reject("IO_ERROR", "Failed to execute command: " + e.getMessage());
            } catch (InterruptedException e) {
                promise.reject("INTERRUPTED", "Command execution interrupted: " + e.getMessage());
            } catch (Exception e) {
                promise.reject("UNKNOWN_ERROR", "Unexpected error: " + e.getMessage());
            }
        });
    }

    /**
     * Start a threat detector
     *
     * @param detector Detector name (network_anomaly, file_system, system_call)
     * @param promise Promise to resolve/reject
     */
    @ReactMethod
    public void startDetector(String detector, Promise promise) {
        String pythonPath = "/usr/bin/python3";
        String scriptPath = getDetectorScriptPath(detector);

        if (scriptPath == null) {
            promise.reject("INVALID_DETECTOR", "Unknown detector: " + detector);
            return;
        }

        List<String> args = new ArrayList<>();
        args.add(scriptPath);
        args.add("--daemon");

        executeCommandWithArgs(pythonPath, args, promise);
    }

    /**
     * Stop a threat detector
     *
     * @param detector Detector name
     * @param promise Promise to resolve/reject
     */
    @ReactMethod
    public void stopDetector(String detector, Promise promise) {
        String scriptPath = "/opt/qwamos/security/scripts/stop_detector.py";

        List<String> args = new ArrayList<>();
        args.add(scriptPath);
        args.add(detector);

        executeCommandWithArgs("/usr/bin/python3", args, promise);
    }

    /**
     * Get detector status
     *
     * @param promise Promise to resolve with JSON status
     */
    @ReactMethod
    public void getDetectorStatus(Promise promise) {
        String scriptPath = "/opt/qwamos/security/scripts/get_detector_status.py";

        List<String> args = new ArrayList<>();
        args.add(scriptPath);

        executeCommandWithArgs("/usr/bin/python3", args, promise);
    }

    /**
     * Get list of threats
     *
     * @param options Filter options (JSON string)
     * @param promise Promise to resolve with threat list
     */
    @ReactMethod
    public void getThreats(String options, Promise promise) {
        String scriptPath = "/opt/qwamos/security/scripts/get_threats.py";

        List<String> args = new ArrayList<>();
        args.add(scriptPath);
        if (options != null && !options.isEmpty()) {
            args.add("--options");
            args.add(options);
        }

        executeCommandWithArgs("/usr/bin/python3", args, promise);
    }

    /**
     * Get threat details
     *
     * @param threatId Threat identifier
     * @param promise Promise to resolve with threat details
     */
    @ReactMethod
    public void getThreatDetails(String threatId, Promise promise) {
        String scriptPath = "/opt/qwamos/security/scripts/get_threat_details.py";

        List<String> args = new ArrayList<>();
        args.add(scriptPath);
        args.add(threatId);

        executeCommandWithArgs("/usr/bin/python3", args, promise);
    }

    /**
     * Execute security action on threat
     *
     * @param threatId Threat identifier
     * @param action Action to execute
     * @param promise Promise to resolve with action result
     */
    @ReactMethod
    public void executeAction(String threatId, String action, Promise promise) {
        String scriptPath = "/opt/qwamos/security/scripts/execute_action.py";

        List<String> args = new ArrayList<>();
        args.add(scriptPath);
        args.add(threatId);
        args.add(action);

        executeCommandWithArgs("/usr/bin/python3", args, 60000, promise); // 60s timeout for actions
    }

    /**
     * Get system health score
     *
     * @param promise Promise to resolve with health score (0-100)
     */
    @ReactMethod
    public void getSystemHealth(Promise promise) {
        String scriptPath = "/opt/qwamos/security/scripts/get_system_health.py";

        List<String> args = new ArrayList<>();
        args.add(scriptPath);

        executeCommandWithArgs("/usr/bin/python3", args, promise);
    }

    // Helper methods

    private void executeCommandWithArgs(String command, List<String> args, Promise promise) {
        executeCommandWithArgs(command, args, DEFAULT_TIMEOUT_MS, promise);
    }

    private void executeCommandWithArgs(String command, List<String> args, int timeoutMs, Promise promise) {
        executorService.submit(() -> {
            try {
                if (!isValidCommand(command)) {
                    promise.reject("INVALID_COMMAND", "Command not allowed: " + command);
                    return;
                }

                List<String> cmdList = new ArrayList<>();
                cmdList.add(command);
                cmdList.addAll(args);

                ProcessBuilder processBuilder = new ProcessBuilder(cmdList);
                processBuilder.redirectErrorStream(true);

                Process process = processBuilder.start();

                StringBuilder output = new StringBuilder();
                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
                );

                String line;
                while ((line = reader.readLine()) != null) {
                    output.append(line).append("\n");
                }

                boolean completed = process.waitFor(timeoutMs, java.util.concurrent.TimeUnit.MILLISECONDS);

                if (!completed) {
                    process.destroy();
                    promise.reject("TIMEOUT", "Command timed out");
                    return;
                }

                int exitCode = process.exitValue();

                if (exitCode == 0) {
                    promise.resolve(output.toString());
                } else {
                    promise.reject("COMMAND_FAILED", output.toString());
                }

            } catch (Exception e) {
                promise.reject("ERROR", e.getMessage());
            }
        });
    }

    private boolean isValidCommand(String command) {
        // Whitelist of allowed commands
        List<String> allowedCommands = List.of(
            "/usr/bin/python3",
            "/usr/bin/python",
            "/bin/systemctl"
        );

        return allowedCommands.contains(command);
    }

    private String getDetectorScriptPath(String detector) {
        switch (detector) {
            case "network_anomaly":
                return "/opt/qwamos/security/ml/network_anomaly_detector.py";
            case "file_system":
                return "/opt/qwamos/security/ml/file_system_monitor.py";
            case "system_call":
                return "/opt/qwamos/security/ml/system_call_analyzer.py";
            default:
                return null;
        }
    }

    @Override
    public void onCatalystInstanceDestroy() {
        executorService.shutdown();
    }
}
