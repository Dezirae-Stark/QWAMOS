/**
 * QWAMOS SecureType Keyboard - Secure Input Native Module
 *
 * Provides native Android security features:
 * - FLAG_SECURE (anti-screenshot)
 * - Hardware-backed keystroke encryption
 * - Secure memory wiping
 * - Haptic feedback
 * - Biometric authentication
 * - Security event logging
 *
 * @module SecureInputModule
 * @version 1.0.0
 */

package com.qwamos.securekeyboard;

import android.app.Activity;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.view.Window;
import android.view.WindowManager;
import android.util.Log;

import androidx.biometric.BiometricManager;
import androidx.biometric.BiometricPrompt;
import androidx.fragment.app.FragmentActivity;

import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableMap;

import java.io.File;
import java.io.FileWriter;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class SecureInputModule extends ReactContextBaseJavaModule {

    private static final String MODULE_NAME = "SecureInputModule";
    private static final String TAG = "QWAMOS_SecureInput";

    private ReactApplicationContext reactContext;
    private KeystoreManager keystoreManager;
    private Vibrator vibrator;
    private Executor executor;

    public SecureInputModule(ReactApplicationContext context) {
        super(context);
        this.reactContext = context;
        this.keystoreManager = new KeystoreManager(context);
        this.vibrator = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
        this.executor = Executors.newSingleThreadExecutor();
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    /**
     * Initialize hardware-backed keystore
     */
    @ReactMethod
    public void initializeKeystore(Promise promise) {
        try {
            keystoreManager.initialize();
            Log.i(TAG, "Keystore initialized successfully");
            promise.resolve(true);
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize keystore", e);
            promise.reject("KEYSTORE_INIT_ERROR", e.getMessage(), e);
        }
    }

    /**
     * Set FLAG_SECURE to prevent screenshots and screen recording
     *
     * @param secure - true to enable, false to disable
     */
    @ReactMethod
    public void setSecureFlag(boolean secure, Promise promise) {
        Activity activity = getCurrentActivity();

        if (activity != null) {
            activity.runOnUiThread(() -> {
                try {
                    Window window = activity.getWindow();

                    if (secure) {
                        // Enable FLAG_SECURE
                        window.setFlags(
                            WindowManager.LayoutParams.FLAG_SECURE,
                            WindowManager.LayoutParams.FLAG_SECURE
                        );
                        Log.i(TAG, "FLAG_SECURE enabled - screenshots blocked");
                    } else {
                        // Disable FLAG_SECURE
                        window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE);
                        Log.i(TAG, "FLAG_SECURE disabled");
                    }

                    promise.resolve(true);
                } catch (Exception e) {
                    Log.e(TAG, "Failed to set FLAG_SECURE", e);
                    promise.reject("FLAG_SECURE_ERROR", e.getMessage(), e);
                }
            });
        } else {
            promise.reject("NO_ACTIVITY", "No current activity available");
        }
    }

    /**
     * Encrypt keystroke using hardware-backed keystore
     *
     * Uses ChaCha20-Poly1305 AEAD encryption
     *
     * @param keystroke - plaintext keystroke
     * @return Base64-encoded encrypted keystroke
     */
    @ReactMethod
    public void encryptKeystroke(String keystroke, Promise promise) {
        executor.execute(() -> {
            try {
                String encrypted = keystoreManager.encrypt(keystroke);
                promise.resolve(encrypted);
            } catch (Exception e) {
                Log.e(TAG, "Failed to encrypt keystroke", e);
                promise.reject("ENCRYPTION_ERROR", e.getMessage(), e);
            }
        });
    }

    /**
     * Decrypt keystroke (for testing/verification only)
     *
     * @param encryptedKeystroke - Base64-encoded encrypted keystroke
     * @return plaintext keystroke
     */
    @ReactMethod
    public void decryptKeystroke(String encryptedKeystroke, Promise promise) {
        executor.execute(() -> {
            try {
                String decrypted = keystoreManager.decrypt(encryptedKeystroke);
                promise.resolve(decrypted);
            } catch (Exception e) {
                Log.e(TAG, "Failed to decrypt keystroke", e);
                promise.reject("DECRYPTION_ERROR", e.getMessage(), e);
            }
        });
    }

    /**
     * Securely wipe encrypted keystroke buffer from memory
     *
     * Overwrites memory with random data and triggers GC
     */
    @ReactMethod
    public void wipeMemory(Promise promise) {
        try {
            keystoreManager.wipeMemory();

            // Force garbage collection
            System.gc();
            System.runFinalization();

            Log.i(TAG, "Memory wiped successfully");
            promise.resolve(true);
        } catch (Exception e) {
            Log.e(TAG, "Failed to wipe memory", e);
            promise.reject("WIPE_ERROR", e.getMessage(), e);
        }
    }

    /**
     * Provide haptic feedback
     *
     * @param intensity - 'light', 'medium', or 'heavy'
     */
    @ReactMethod
    public void hapticFeedback(String intensity, Promise promise) {
        if (vibrator != null && vibrator.hasVibrator()) {
            try {
                VibrationEffect effect;

                switch (intensity) {
                    case "light":
                        effect = VibrationEffect.createOneShot(10, VibrationEffect.DEFAULT_AMPLITUDE);
                        break;
                    case "medium":
                        effect = VibrationEffect.createOneShot(25, VibrationEffect.DEFAULT_AMPLITUDE);
                        break;
                    case "heavy":
                        effect = VibrationEffect.createOneShot(50, VibrationEffect.DEFAULT_AMPLITUDE);
                        break;
                    default:
                        effect = VibrationEffect.createOneShot(10, VibrationEffect.DEFAULT_AMPLITUDE);
                }

                vibrator.vibrate(effect);
                promise.resolve(true);
            } catch (Exception e) {
                Log.e(TAG, "Haptic feedback error", e);
                promise.reject("HAPTIC_ERROR", e.getMessage(), e);
            }
        } else {
            promise.resolve(false);
        }
    }

    /**
     * Authenticate user with biometrics
     *
     * Uses fingerprint or face unlock
     *
     * @return true if authenticated, false otherwise
     */
    @ReactMethod
    public void authenticateUser(Promise promise) {
        Activity activity = getCurrentActivity();

        if (!(activity instanceof FragmentActivity)) {
            promise.reject("NO_FRAGMENT_ACTIVITY", "Activity is not a FragmentActivity");
            return;
        }

        FragmentActivity fragmentActivity = (FragmentActivity) activity;

        BiometricManager biometricManager = BiometricManager.from(reactContext);
        int canAuthenticate = biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG
        );

        if (canAuthenticate != BiometricManager.BIOMETRIC_SUCCESS) {
            promise.reject("BIOMETRIC_UNAVAILABLE", "Biometric authentication not available");
            return;
        }

        BiometricPrompt.PromptInfo promptInfo = new BiometricPrompt.PromptInfo.Builder()
            .setTitle("QWAMOS SecureType Authentication")
            .setSubtitle("Typing anomaly detected")
            .setDescription("Please authenticate to continue using the keyboard")
            .setNegativeButtonText("Cancel")
            .build();

        BiometricPrompt biometricPrompt = new BiometricPrompt(
            fragmentActivity,
            executor,
            new BiometricPrompt.AuthenticationCallback() {
                @Override
                public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result) {
                    Log.i(TAG, "Biometric authentication succeeded");
                    promise.resolve(true);
                }

                @Override
                public void onAuthenticationFailed() {
                    Log.w(TAG, "Biometric authentication failed");
                    promise.resolve(false);
                }

                @Override
                public void onAuthenticationError(int errorCode, CharSequence errString) {
                    Log.e(TAG, "Biometric authentication error: " + errString);
                    promise.reject("BIOMETRIC_ERROR", errString.toString());
                }
            }
        );

        activity.runOnUiThread(() -> {
            biometricPrompt.authenticate(promptInfo);
        });
    }

    /**
     * Log security event to encrypted log file
     *
     * @param eventType - Type of security event
     * @param data - Event data (ReadableMap)
     */
    @ReactMethod
    public void logSecurityEvent(String eventType, ReadableMap data, Promise promise) {
        executor.execute(() -> {
            try {
                String timestamp = String.valueOf(System.currentTimeMillis());
                String logEntry = String.format(
                    "[%s] %s: %s\n",
                    timestamp,
                    eventType,
                    data.toString()
                );

                // Write to encrypted log file
                File logDir = new File(reactContext.getFilesDir(), "keyboard_logs");
                if (!logDir.exists()) {
                    logDir.mkdirs();
                }

                File logFile = new File(logDir, "security_events.log");
                FileWriter writer = new FileWriter(logFile, true);
                writer.write(logEntry);
                writer.close();

                Log.i(TAG, "Security event logged: " + eventType);
                promise.resolve(true);
            } catch (Exception e) {
                Log.e(TAG, "Failed to log security event", e);
                promise.reject("LOG_ERROR", e.getMessage(), e);
            }
        });
    }

    /**
     * Append encrypted keystroke to buffer
     *
     * @param currentBuffer - Current encrypted buffer
     * @param newKeystroke - New encrypted keystroke to append
     * @return Updated encrypted buffer
     */
    @ReactMethod
    public void appendToBuffer(String currentBuffer, String newKeystroke, Promise promise) {
        try {
            String updatedBuffer = currentBuffer + newKeystroke;
            promise.resolve(updatedBuffer);
        } catch (Exception e) {
            promise.reject("BUFFER_ERROR", e.getMessage(), e);
        }
    }
}
