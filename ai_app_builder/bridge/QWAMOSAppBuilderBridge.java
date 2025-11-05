package com.qwamos.appbuilder.bridge;

import android.util.Log;

import com.facebook.react.bridge.Arguments;
import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableArray;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.modules.core.DeviceEventManagerModule;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

import javax.annotation.Nonnull;

/**
 * QWAMOS Phase 9: React Native Bridge
 *
 * Native bridge between React Native UI and Python backend.
 * Handles communication for app building, deployment, and management.
 *
 * @version 1.0.0
 */
public class QWAMOSAppBuilderBridge extends ReactContextBaseJavaModule {

    private static final String MODULE_NAME = "QWAMOSAppBuilderBridge";
    private static final String TAG = "QWAMOSAppBuilderBridge";

    // Backend service URLs
    private static final String BACKEND_HOST = "localhost";
    private static final int BACKEND_PORT = 8888;
    private static final String BACKEND_URL = "http://" + BACKEND_HOST + ":" + BACKEND_PORT;

    private final ReactApplicationContext reactContext;

    public QWAMOSAppBuilderBridge(@Nonnull ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
    }

    @Nonnull
    @Override
    public String getName() {
        return MODULE_NAME;
    }

    /**
     * Build app from user request
     *
     * @param userRequest User's natural language app description
     * @param userId      User ID
     * @param promise     Promise to resolve with generated app JSON
     */
    @ReactMethod
    public void buildApp(String userRequest, String userId, Promise promise) {
        Log.d(TAG, "buildApp called: " + userRequest);

        new Thread(() -> {
            try {
                // Create request JSON
                JSONObject requestJson = new JSONObject();
                requestJson.put("user_request", userRequest);
                requestJson.put("user_id", userId);

                // Send to backend
                JSONObject response = sendPostRequest("/api/build", requestJson);

                // Return result
                promise.resolve(response.toString());

            } catch (Exception e) {
                Log.e(TAG, "Error building app", e);
                promise.reject("BUILD_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * Deploy generated app to device
     *
     * @param appJson JSON string of GeneratedApp
     * @param promise Promise to resolve with deployment result
     */
    @ReactMethod
    public void deployApp(String appJson, Promise promise) {
        Log.d(TAG, "deployApp called");

        new Thread(() -> {
            try {
                // Parse app JSON
                JSONObject app = new JSONObject(appJson);

                // Create request
                JSONObject requestJson = new JSONObject();
                requestJson.put("app", app);

                // Send to backend
                JSONObject response = sendPostRequest("/api/deploy", requestJson);

                // Return result
                promise.resolve(response.toString());

            } catch (Exception e) {
                Log.e(TAG, "Error deploying app", e);
                promise.reject("DEPLOY_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * Apply enhancements to generated app
     *
     * @param appJson               JSON string of GeneratedApp
     * @param selectedEnhancements  Array of enhancement IDs to apply
     * @param promise               Promise to resolve with updated app
     */
    @ReactMethod
    public void applyEnhancements(
        String appJson,
        ReadableArray selectedEnhancements,
        Promise promise
    ) {
        Log.d(TAG, "applyEnhancements called");

        new Thread(() -> {
            try {
                // Parse app JSON
                JSONObject app = new JSONObject(appJson);

                // Convert ReadableArray to JSONArray
                JSONArray enhancementsArray = new JSONArray();
                for (int i = 0; i < selectedEnhancements.size(); i++) {
                    enhancementsArray.put(selectedEnhancements.getString(i));
                }

                // Create request
                JSONObject requestJson = new JSONObject();
                requestJson.put("app", app);
                requestJson.put("selected_enhancements", enhancementsArray);

                // Send to backend
                JSONObject response = sendPostRequest("/api/apply-enhancements", requestJson);

                // Return result
                promise.resolve(response.toString());

            } catch (Exception e) {
                Log.e(TAG, "Error applying enhancements", e);
                promise.reject("ENHANCEMENT_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * List all generated apps
     *
     * @param promise Promise to resolve with array of apps
     */
    @ReactMethod
    public void listGeneratedApps(Promise promise) {
        Log.d(TAG, "listGeneratedApps called");

        new Thread(() -> {
            try {
                // Send to backend
                JSONObject response = sendGetRequest("/api/apps");

                // Return result
                promise.resolve(response.toString());

            } catch (Exception e) {
                Log.e(TAG, "Error listing apps", e);
                promise.reject("LIST_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * Delete a generated app
     *
     * @param appName App name to delete
     * @param promise Promise to resolve when complete
     */
    @ReactMethod
    public void deleteApp(String appName, Promise promise) {
        Log.d(TAG, "deleteApp called: " + appName);

        new Thread(() -> {
            try {
                // Create request
                JSONObject requestJson = new JSONObject();
                requestJson.put("app_name", appName);

                // Send to backend
                sendPostRequest("/api/delete", requestJson);

                // Return success
                promise.resolve(null);

            } catch (Exception e) {
                Log.e(TAG, "Error deleting app", e);
                promise.reject("DELETE_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * Get security audit details for app
     *
     * @param appName App name
     * @param promise Promise to resolve with audit JSON
     */
    @ReactMethod
    public void getSecurityAudit(String appName, Promise promise) {
        Log.d(TAG, "getSecurityAudit called: " + appName);

        new Thread(() -> {
            try {
                // Send to backend
                JSONObject response = sendGetRequest("/api/audit/" + appName);

                // Return result
                promise.resolve(response.toString());

            } catch (Exception e) {
                Log.e(TAG, "Error getting security audit", e);
                promise.reject("AUDIT_ERROR", e.getMessage());
            }
        }).start();
    }

    /**
     * Send progress event to React Native
     *
     * @param stage    Current stage name
     * @param progress Progress percentage (0-100)
     * @param status   Status (in_progress, completed, failed)
     * @param details  Details message
     */
    public void sendProgressEvent(
        String stage,
        int progress,
        String status,
        String details
    ) {
        WritableMap params = Arguments.createMap();
        params.putString("stage", stage);
        params.putInt("progress", progress);
        params.putString("status", status);
        params.putString("details", details);

        sendEvent(reactContext, "AppBuildProgress", params);
    }

    /**
     * Send event to React Native
     */
    private void sendEvent(
        ReactContext reactContext,
        String eventName,
        WritableMap params
    ) {
        reactContext
            .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter.class)
            .emit(eventName, params);
    }

    /**
     * Send POST request to backend
     */
    private JSONObject sendPostRequest(String endpoint, JSONObject requestBody) throws Exception {
        URL url = new URL(BACKEND_URL + endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        try {
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);

            // Write request body
            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = requestBody.toString().getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            // Read response
            int responseCode = conn.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_OK) {
                BufferedReader br = new BufferedReader(
                    new InputStreamReader(conn.getInputStream(), "utf-8")
                );

                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = br.readLine()) != null) {
                    response.append(responseLine.trim());
                }

                return new JSONObject(response.toString());

            } else {
                throw new Exception("HTTP error: " + responseCode);
            }

        } finally {
            conn.disconnect();
        }
    }

    /**
     * Send GET request to backend
     */
    private JSONObject sendGetRequest(String endpoint) throws Exception {
        URL url = new URL(BACKEND_URL + endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        try {
            conn.setRequestMethod("GET");

            // Read response
            int responseCode = conn.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_OK) {
                BufferedReader br = new BufferedReader(
                    new InputStreamReader(conn.getInputStream(), "utf-8")
                );

                StringBuilder response = new StringBuilder();
                String responseLine;
                while ((responseLine = br.readLine()) != null) {
                    response.append(responseLine.trim());
                }

                return new JSONObject(response.toString());

            } else {
                throw new Exception("HTTP error: " + responseCode);
            }

        } finally {
            conn.disconnect();
        }
    }

    /**
     * Get constants to export to React Native
     */
    @Override
    public Map<String, Object> getConstants() {
        final Map<String, Object> constants = new HashMap<>();
        constants.put("BACKEND_URL", BACKEND_URL);
        return constants;
    }
}
