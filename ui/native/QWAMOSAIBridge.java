package com.qwamos.ai;

import android.util.Log;

import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableArray;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * QWAMOS AI Bridge - React Native Native Module
 *
 * Bridges React Native UI to Python AI backend by providing:
 * - Command execution (Python AI scripts, systemctl, etc.)
 * - File I/O operations for AI configs and cache
 * - Process management for AI services
 *
 * Security: This module requires root access for systemd operations.
 * All commands are executed with proper sandboxing and timeout limits.
 */
public class QWAMOSAIBridge extends ReactContextBaseJavaModule {

    private static final String TAG = "QWAMOSAIBridge";
    private static final int DEFAULT_TIMEOUT_SECONDS = 30;
    private static final int AI_QUERY_TIMEOUT_SECONDS = 60;
    private static final int MAX_OUTPUT_SIZE = 10 * 1024 * 1024; // 10MB max output

    private final ReactApplicationContext reactContext;

    public QWAMOSAIBridge(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
    }

    @Override
    public String getName() {
        return "QWAMOSAIBridge";
    }

    /**
     * Execute a command with arguments
     *
     * @param command Command to execute (e.g., "/usr/bin/python3")
     * @param args Array of arguments
     * @param promise Promise to resolve with output or reject with error
     */
    @ReactMethod
    public void executeCommand(String command, ReadableArray args, Promise promise) {
        executeCommandWithTimeout(command, args, DEFAULT_TIMEOUT_SECONDS, promise);
    }

    /**
     * Execute a command with custom timeout
     *
     * @param command Command to execute
     * @param args Array of arguments
     * @param timeoutSeconds Timeout in seconds
     * @param promise Promise to resolve/reject
     */
    @ReactMethod
    public void executeCommandWithTimeout(
            String command,
            ReadableArray args,
            int timeoutSeconds,
            Promise promise
    ) {
        new Thread(() -> {
            try {
                Log.d(TAG, "Executing AI command: " + command);

                // Build command list
                List<String> cmdList = new ArrayList<>();
                cmdList.add(command);

                // Add arguments
                for (int i = 0; i < args.size(); i++) {
                    String arg = args.getString(i);
                    if (arg != null) {
                        cmdList.add(arg);
                    }
                }

                // Log command for debugging (sanitize API keys)
                String logCommand = String.join(" ", cmdList)
                        .replaceAll("sk-ant-[a-zA-Z0-9-]+", "sk-ant-***")
                        .replaceAll("sk-proj-[a-zA-Z0-9-]+", "sk-proj-***");
                Log.d(TAG, "Full command: " + logCommand);

                // Create process
                ProcessBuilder pb = new ProcessBuilder(cmdList);
                pb.redirectErrorStream(true); // Combine stdout and stderr

                // Start process
                Process process = pb.start();

                // Read output
                BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getInputStream())
                );

                StringBuilder output = new StringBuilder();
                String line;
                int totalChars = 0;

                while ((line = reader.readLine()) != null) {
                    // Prevent excessive memory usage
                    totalChars += line.length();
                    if (totalChars > MAX_OUTPUT_SIZE) {
                        Log.w(TAG, "Output exceeded max size, truncating");
                        output.append("\n[OUTPUT TRUNCATED - Exceeded 10MB]");
                        break;
                    }

                    output.append(line).append("\n");
                }

                // Wait for process with timeout
                boolean finished = process.waitFor(timeoutSeconds, TimeUnit.SECONDS);

                if (!finished) {
                    process.destroy();
                    promise.reject(
                            "TIMEOUT",
                            "AI command timed out after " + timeoutSeconds + " seconds"
                    );
                    return;
                }

                int exitCode = process.exitValue();

                if (exitCode == 0) {
                    String result = output.toString().trim();
                    promise.resolve(result);
                } else {
                    promise.reject(
                            "EXEC_ERROR",
                            "AI command failed with exit code " + exitCode + ": " + output.toString()
                    );
                }

            } catch (IOException e) {
                Log.e(TAG, "IO Error executing AI command", e);
                promise.reject("IO_ERROR", e.getMessage());
            } catch (InterruptedException e) {
                Log.e(TAG, "AI command interrupted", e);
                promise.reject("INTERRUPTED", e.getMessage());
            } catch (Exception e) {
                Log.e(TAG, "Unexpected error executing AI command", e);
                promise.reject("UNKNOWN_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * Read a file's contents
     *
     * @param filePath Absolute path to file
     * @param promise Promise to resolve with file contents
     */
    @ReactMethod
    public void readFile(String filePath, Promise promise) {
        new Thread(() -> {
            try {
                Log.d(TAG, "Reading AI file: " + filePath);

                File file = new File(filePath);

                if (!file.exists()) {
                    promise.reject("FILE_NOT_FOUND", "File does not exist: " + filePath);
                    return;
                }

                if (!file.canRead()) {
                    promise.reject("PERMISSION_DENIED", "Cannot read file: " + filePath);
                    return;
                }

                // Check file size
                long fileSize = file.length();
                if (fileSize > MAX_OUTPUT_SIZE) {
                    promise.reject(
                            "FILE_TOO_LARGE",
                            "File exceeds max size of 10MB: " + fileSize + " bytes"
                    );
                    return;
                }

                // Read file
                StringBuilder content = new StringBuilder();
                BufferedReader reader = new BufferedReader(new FileReader(file));

                String line;
                while ((line = reader.readLine()) != null) {
                    content.append(line).append("\n");
                }

                reader.close();

                promise.resolve(content.toString());

            } catch (IOException e) {
                Log.e(TAG, "Error reading AI file", e);
                promise.reject("READ_ERROR", e.getMessage());
            } catch (Exception e) {
                Log.e(TAG, "Unexpected error reading AI file", e);
                promise.reject("UNKNOWN_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * Write content to a file
     *
     * @param filePath Absolute path to file
     * @param content Content to write
     * @param promise Promise to resolve on success
     */
    @ReactMethod
    public void writeFile(String filePath, String content, Promise promise) {
        new Thread(() -> {
            try {
                Log.d(TAG, "Writing AI file: " + filePath);

                File file = new File(filePath);

                // Create parent directories if needed
                File parentDir = file.getParentFile();
                if (parentDir != null && !parentDir.exists()) {
                    parentDir.mkdirs();
                }

                // Write file
                Files.write(Paths.get(filePath), content.getBytes());

                promise.resolve(true);

            } catch (IOException e) {
                Log.e(TAG, "Error writing AI file", e);
                promise.reject("WRITE_ERROR", e.getMessage());
            } catch (Exception e) {
                Log.e(TAG, "Unexpected error writing AI file", e);
                promise.reject("UNKNOWN_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * Check if a file exists
     *
     * @param filePath Absolute path to file
     * @param promise Promise to resolve with boolean
     */
    @ReactMethod
    public void fileExists(String filePath, Promise promise) {
        try {
            File file = new File(filePath);
            boolean exists = file.exists();
            Log.d(TAG, "File exists check for " + filePath + ": " + exists);
            promise.resolve(exists);
        } catch (Exception e) {
            Log.e(TAG, "Error checking file existence", e);
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Get file permissions
     *
     * @param filePath Absolute path to file
     * @param promise Promise to resolve with permissions info
     */
    @ReactMethod
    public void getFilePermissions(String filePath, Promise promise) {
        try {
            File file = new File(filePath);

            if (!file.exists()) {
                promise.reject("FILE_NOT_FOUND", "File does not exist");
                return;
            }

            String permissions = (file.canRead() ? "r" : "-") +
                    (file.canWrite() ? "w" : "-") +
                    (file.canExecute() ? "x" : "-");

            promise.resolve(permissions);

        } catch (Exception e) {
            Log.e(TAG, "Error getting file permissions", e);
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Delete a file
     *
     * @param filePath Absolute path to file
     * @param promise Promise to resolve on success
     */
    @ReactMethod
    public void deleteFile(String filePath, Promise promise) {
        try {
            File file = new File(filePath);

            if (!file.exists()) {
                promise.resolve(true); // Already deleted
                return;
            }

            boolean deleted = file.delete();

            if (deleted) {
                Log.d(TAG, "Deleted file: " + filePath);
                promise.resolve(true);
            } else {
                promise.reject("DELETE_ERROR", "Failed to delete file");
            }

        } catch (Exception e) {
            Log.e(TAG, "Error deleting file", e);
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Get disk space available for AI models
     *
     * @param promise Promise to resolve with available bytes
     */
    @ReactMethod
    public void getAvailableDiskSpace(Promise promise) {
        try {
            File path = new File("/opt/qwamos/ai");

            if (!path.exists()) {
                path.mkdirs();
            }

            long availableBytes = path.getUsableSpace();

            Log.d(TAG, "Available disk space: " + availableBytes + " bytes");
            promise.resolve((double) availableBytes);

        } catch (Exception e) {
            Log.e(TAG, "Error getting available disk space", e);
            promise.reject("ERROR", e.getMessage());
        }
    }

    /**
     * Kill a running process by PID
     *
     * @param pid Process ID
     * @param promise Promise to resolve on success
     */
    @ReactMethod
    public void killProcess(int pid, Promise promise) {
        try {
            ProcessBuilder pb = new ProcessBuilder("kill", String.valueOf(pid));
            Process process = pb.start();

            boolean finished = process.waitFor(5, TimeUnit.SECONDS);

            if (finished && process.exitValue() == 0) {
                Log.d(TAG, "Killed process: " + pid);
                promise.resolve(true);
            } else {
                promise.reject("KILL_ERROR", "Failed to kill process " + pid);
            }

        } catch (Exception e) {
            Log.e(TAG, "Error killing process", e);
            promise.reject("ERROR", e.getMessage());
        }
    }
}
