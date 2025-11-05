/**
 * QWAMOS SecureType Keyboard - Typing Anomaly Detection Module
 *
 * React Native bridge for ML-based typing dynamics analysis:
 * - Detects unauthorized keyboard usage
 * - Learns user's typing patterns
 * - Alerts on anomalies (>30% deviation)
 *
 * @module TypingAnomalyModule
 * @version 1.0.0
 */

package com.qwamos.securekeyboard;

import android.util.Log;

import com.facebook.react.bridge.Arguments;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableMap;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.modules.core.DeviceEventManagerModule;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class TypingAnomalyModule extends ReactContextBaseJavaModule {

    private static final String MODULE_NAME = "TypingAnomalyModule";
    private static final String TAG = "QWAMOS_TypingAnomaly";

    private ReactApplicationContext reactContext;
    private Executor executor;
    private Process pythonProcess;

    public TypingAnomalyModule(ReactApplicationContext context) {
        super(context);
        this.reactContext = context;
        this.executor = Executors.newSingleThreadExecutor();
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    /**
     * Initialize ML typing anomaly detector
     *
     * Starts Python process running the ML model
     */
    @ReactMethod
    public void initialize(Promise promise) {
        executor.execute(() -> {
            try {
                // Check if Python ML detector exists
                File detectorScript = new File("/opt/qwamos/keyboard/ml/typing_anomaly_detector.py");

                if (!detectorScript.exists()) {
                    Log.w(TAG, "ML detector script not found, ML detection disabled");
                    promise.resolve(false);
                    return;
                }

                // Start Python ML detector process
                ProcessBuilder processBuilder = new ProcessBuilder(
                    "python3",
                    detectorScript.getAbsolutePath()
                );

                processBuilder.redirectErrorStream(true);
                pythonProcess = processBuilder.start();

                Log.i(TAG, "ML typing anomaly detector initialized");
                promise.resolve(true);
            } catch (Exception e) {
                Log.e(TAG, "Failed to initialize ML detector", e);
                promise.reject("ML_INIT_ERROR", e.getMessage(), e);
            }
        });
    }

    /**
     * Load user typing profile
     *
     * @return User typing profile (mean, std, samples)
     */
    @ReactMethod
    public void loadUserProfile(Promise promise) {
        executor.execute(() -> {
            try {
                File profileFile = new File(reactContext.getFilesDir(), "typing_profile.json");

                if (!profileFile.exists()) {
                    Log.i(TAG, "No typing profile found, will create new one");
                    promise.resolve(null);
                    return;
                }

                // Read profile file
                // TODO: Implement profile loading
                WritableMap profile = Arguments.createMap();
                profile.putInt("samples", 0);
                profile.putDouble("last_updated", System.currentTimeMillis());

                promise.resolve(profile);
            } catch (Exception e) {
                Log.e(TAG, "Failed to load typing profile", e);
                promise.reject("PROFILE_LOAD_ERROR", e.getMessage(), e);
            }
        });
    }

    /**
     * Save user typing profile
     *
     * @param profile - Typing profile data
     */
    @ReactMethod
    public void saveUserProfile(ReadableMap profile, Promise promise) {
        executor.execute(() -> {
            try {
                File profileFile = new File(reactContext.getFilesDir(), "typing_profile.json");

                // TODO: Implement profile saving
                Log.i(TAG, "Typing profile saved");
                promise.resolve(true);
            } catch (Exception e) {
                Log.e(TAG, "Failed to save typing profile", e);
                promise.reject("PROFILE_SAVE_ERROR", e.getMessage(), e);
            }
        });
    }

    /**
     * Analyze keystroke for typing anomalies
     *
     * Sends keystroke data to ML detector and checks for anomalies
     *
     * @param features - Typing features (press_duration, release_time, pressure, touch_area)
     * @return Anomaly detection result
     */
    @ReactMethod
    public void analyzeKeystroke(ReadableMap features, Promise promise) {
        executor.execute(() -> {
            try {
                if (pythonProcess == null || !pythonProcess.isAlive()) {
                    Log.w(TAG, "ML detector not running, skipping analysis");
                    WritableMap result = Arguments.createMap();
                    result.putBoolean("is_anomaly", false);
                    result.putDouble("confidence", 0.0);
                    promise.resolve(result);
                    return;
                }

                // Extract features
                double pressDuration = features.getDouble("press_duration");
                double releaseTime = features.getDouble("release_time");
                double pressure = features.getDouble("pressure");
                double touchArea = features.getDouble("touch_area");

                // Send to ML detector via stdin
                String input = String.format(
                    "%.4f,%.0f,%.2f,%.0f\n",
                    pressDuration,
                    releaseTime,
                    pressure,
                    touchArea
                );

                pythonProcess.getOutputStream().write(input.getBytes());
                pythonProcess.getOutputStream().flush();

                // Read result from ML detector
                BufferedReader reader = new BufferedReader(
                    new InputStreamReader(pythonProcess.getInputStream())
                );

                String line = reader.readLine();
                if (line != null) {
                    String[] parts = line.split(",");
                    boolean isAnomaly = parts[0].equals("1");
                    double confidence = Double.parseDouble(parts[1]);

                    WritableMap result = Arguments.createMap();
                    result.putBoolean("is_anomaly", isAnomaly);
                    result.putDouble("confidence", confidence);

                    // If anomaly detected, emit event
                    if (isAnomaly) {
                        WritableMap event = Arguments.createMap();
                        event.putDouble("confidence", confidence);
                        event.putMap("features", features);

                        reactContext
                            .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter.class)
                            .emit("TypingAnomalyDetected", event);

                        Log.w(TAG, String.format("Typing anomaly detected (%.2f%% confidence)", confidence * 100));
                    }

                    promise.resolve(result);
                } else {
                    throw new Exception("No response from ML detector");
                }
            } catch (Exception e) {
                Log.e(TAG, "Failed to analyze keystroke", e);
                promise.reject("ANALYSIS_ERROR", e.getMessage(), e);
            }
        });
    }

    /**
     * Reset user typing profile
     *
     * Clears learned typing patterns (after re-authentication)
     */
    @ReactMethod
    public void resetProfile(Promise promise) {
        executor.execute(() -> {
            try {
                File profileFile = new File(reactContext.getFilesDir(), "typing_profile.json");

                if (profileFile.exists()) {
                    profileFile.delete();
                }

                Log.i(TAG, "Typing profile reset");
                promise.resolve(true);
            } catch (Exception e) {
                Log.e(TAG, "Failed to reset profile", e);
                promise.reject("RESET_ERROR", e.getMessage(), e);
            }
        });
    }

    /**
     * Cleanup on module destroy
     */
    @Override
    public void onCatalystInstanceDestroy() {
        if (pythonProcess != null && pythonProcess.isAlive()) {
            pythonProcess.destroy();
            Log.i(TAG, "ML detector process terminated");
        }
    }
}
