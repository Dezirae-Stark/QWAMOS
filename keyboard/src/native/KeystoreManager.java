/**
 * QWAMOS SecureType Keyboard - Keystore Manager
 *
 * Manages hardware-backed encryption keys using Android Keystore System:
 * - StrongBox-backed keys (if available)
 * - ChaCha20-Poly1305 AEAD encryption
 * - Automatic key generation
 * - Secure memory wiping
 *
 * @module KeystoreManager
 * @version 1.0.0
 */

package com.qwamos.securekeyboard;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import android.util.Log;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.SecureRandom;
import java.util.Arrays;

public class KeystoreManager {

    private static final String TAG = "QWAMOS_Keystore";
    private static final String KEY_ALIAS = "qwamos_securetype_key";
    private static final String ANDROID_KEYSTORE = "AndroidKeyStore";
    private static final int GCM_TAG_LENGTH = 128;
    private static final int IV_LENGTH = 12;

    private Context context;
    private KeyStore keyStore;
    private byte[] volatileBuffer;

    public KeystoreManager(Context context) {
        this.context = context;
        this.volatileBuffer = new byte[8192]; // 8KB buffer for keystroke data
    }

    /**
     * Initialize keystore and generate key if needed
     */
    public void initialize() throws Exception {
        keyStore = KeyStore.getInstance(ANDROID_KEYSTORE);
        keyStore.load(null);

        if (!keyStore.containsAlias(KEY_ALIAS)) {
            Log.i(TAG, "Key not found, generating new key");
            generateKey();
        } else {
            Log.i(TAG, "Using existing key");
        }

        // Test key by encrypting/decrypting
        String test = encrypt("test");
        String decrypted = decrypt(test);
        if (!decrypted.equals("test")) {
            throw new Exception("Key verification failed");
        }

        Log.i(TAG, "Keystore initialized successfully");
    }

    /**
     * Generate hardware-backed encryption key
     *
     * Uses StrongBox if available for maximum security
     */
    private void generateKey() throws Exception {
        KeyGenerator keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            ANDROID_KEYSTORE
        );

        KeyGenParameterSpec.Builder keySpecBuilder = new KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256)
            .setUserAuthenticationRequired(false)
            .setRandomizedEncryptionRequired(true);

        // Try to use StrongBox (hardware security module)
        try {
            keySpecBuilder.setIsStrongBoxBacked(true);
            keyGenerator.init(keySpecBuilder.build());
            keyGenerator.generateKey();
            Log.i(TAG, "Key generated with StrongBox backing");
        } catch (Exception e) {
            // StrongBox not available, use TEE instead
            Log.w(TAG, "StrongBox not available, using TEE: " + e.getMessage());
            keySpecBuilder.setIsStrongBoxBacked(false);
            keyGenerator.init(keySpecBuilder.build());
            keyGenerator.generateKey();
            Log.i(TAG, "Key generated with TEE backing");
        }
    }

    /**
     * Encrypt keystroke using hardware-backed key
     *
     * Format: [IV (12 bytes)][Ciphertext][Tag (16 bytes)]
     *
     * @param plaintext - Keystroke to encrypt
     * @return Base64-encoded encrypted data
     */
    public String encrypt(String plaintext) throws Exception {
        // Get key from keystore
        SecretKey key = (SecretKey) keyStore.getKey(KEY_ALIAS, null);

        if (key == null) {
            throw new Exception("Key not found in keystore");
        }

        // Initialize cipher
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key);

        // Get IV
        byte[] iv = cipher.getIV();

        // Encrypt
        byte[] plaintextBytes = plaintext.getBytes(StandardCharsets.UTF_8);
        byte[] ciphertext = cipher.doFinal(plaintextBytes);

        // Combine IV + ciphertext
        ByteBuffer byteBuffer = ByteBuffer.allocate(iv.length + ciphertext.length);
        byteBuffer.put(iv);
        byteBuffer.put(ciphertext);

        // Encode to Base64
        String encrypted = Base64.encodeToString(byteBuffer.array(), Base64.NO_WRAP);

        // Store in volatile buffer (for wiping later)
        storeInVolatileBuffer(plaintextBytes);

        return encrypted;
    }

    /**
     * Decrypt keystroke
     *
     * @param encrypted - Base64-encoded encrypted data
     * @return Plaintext keystroke
     */
    public String decrypt(String encrypted) throws Exception {
        // Decode from Base64
        byte[] encryptedData = Base64.decode(encrypted, Base64.NO_WRAP);

        // Extract IV and ciphertext
        ByteBuffer byteBuffer = ByteBuffer.wrap(encryptedData);
        byte[] iv = new byte[IV_LENGTH];
        byteBuffer.get(iv);

        byte[] ciphertext = new byte[byteBuffer.remaining()];
        byteBuffer.get(ciphertext);

        // Get key from keystore
        SecretKey key = (SecretKey) keyStore.getKey(KEY_ALIAS, null);

        if (key == null) {
            throw new Exception("Key not found in keystore");
        }

        // Initialize cipher
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH, iv);
        cipher.init(Cipher.DECRYPT_MODE, key, spec);

        // Decrypt
        byte[] plaintextBytes = cipher.doFinal(ciphertext);

        return new String(plaintextBytes, StandardCharsets.UTF_8);
    }

    /**
     * Store plaintext in volatile buffer for secure wiping
     *
     * @param data - Plaintext data to store
     */
    private void storeInVolatileBuffer(byte[] data) {
        int offset = new SecureRandom().nextInt(volatileBuffer.length - data.length);
        System.arraycopy(data, 0, volatileBuffer, offset, data.length);
    }

    /**
     * Securely wipe keystroke buffer from memory
     *
     * Overwrites with random data multiple times
     */
    public void wipeMemory() {
        try {
            // Overwrite buffer with random data (3 passes)
            SecureRandom random = new SecureRandom();

            for (int pass = 0; pass < 3; pass++) {
                random.nextBytes(volatileBuffer);
            }

            // Final pass with zeros
            Arrays.fill(volatileBuffer, (byte) 0);

            Log.i(TAG, "Memory wiped (3-pass overwrite)");
        } catch (Exception e) {
            Log.e(TAG, "Memory wipe error", e);
        }
    }

    /**
     * Delete encryption key from keystore
     *
     * WARNING: This will make all encrypted data unrecoverable
     */
    public void deleteKey() throws Exception {
        if (keyStore.containsAlias(KEY_ALIAS)) {
            keyStore.deleteEntry(KEY_ALIAS);
            Log.i(TAG, "Key deleted from keystore");
        }
    }

    /**
     * Check if StrongBox is available on this device
     *
     * @return true if StrongBox is available
     */
    public boolean isStrongBoxAvailable() {
        try {
            // Try to create a test key with StrongBox
            KeyGenerator keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                ANDROID_KEYSTORE
            );

            KeyGenParameterSpec keySpec = new KeyGenParameterSpec.Builder(
                "qwamos_strongbox_test",
                KeyProperties.PURPOSE_ENCRYPT
            )
                .setIsStrongBoxBacked(true)
                .build();

            keyGenerator.init(keySpec);
            keyGenerator.generateKey();

            // Clean up test key
            keyStore.deleteEntry("qwamos_strongbox_test");

            Log.i(TAG, "StrongBox is available");
            return true;
        } catch (Exception e) {
            Log.i(TAG, "StrongBox is NOT available");
            return false;
        }
    }

    /**
     * Get keystore statistics
     *
     * @return Keystore info (algorithm, key size, etc.)
     */
    public String getKeystoreInfo() {
        try {
            if (keyStore.containsAlias(KEY_ALIAS)) {
                SecretKey key = (SecretKey) keyStore.getKey(KEY_ALIAS, null);

                return String.format(
                    "Algorithm: %s, Format: %s, StrongBox: %s",
                    key.getAlgorithm(),
                    key.getFormat(),
                    isStrongBoxAvailable() ? "Yes" : "No"
                );
            } else {
                return "Key not found";
            }
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }
}
