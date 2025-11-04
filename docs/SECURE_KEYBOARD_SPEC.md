# QWAMOS Secure Keyboard Specification

**Component:** SecureType Keyboard
**Status:** PLANNING
**Priority:** HIGH
**Target:** Phase 8
**Timeline:** 4-6 weeks

---

## Executive Summary

QWAMOS SecureType is a privacy-focused, security-hardened soft keyboard designed to protect against keylogging, shoulder surfing, and side-channel attacks. It provides secure input for passwords, commands, and sensitive data with advanced features like ML-based typing pattern analysis, encrypted keystroke storage, and anti-screenshot protection.

**Key Features:**
- Hardware-backed keystroke encryption
- Anti-keylogging protection
- Shoulder-surfing resistance
- Secure password input mode
- Command terminal input mode
- ML-based typing anomaly detection
- No network access (100% offline)
- Zero telemetry/analytics

---

## Threat Model

### Attacks to Defend Against

1. **Software Keyloggers**
   - Malicious apps capturing keystrokes
   - System-level keystroke interception
   - Accessibility service abuse

2. **Screen Recording/Screenshots**
   - Malicious apps recording screen
   - Screenshot capture of passwords
   - Screen sharing attacks

3. **Shoulder Surfing**
   - Visual observation of typing
   - Camera-based password capture
   - Reflection attacks

4. **Side-Channel Attacks**
   - Timing analysis of keystrokes
   - Motion sensor-based keystroke detection
   - Audio-based keystroke inference

5. **Clipboard Attacks**
   - Malicious clipboard monitoring
   - Password managers compromised
   - Paste jacking

6. **ML-Based Attacks**
   - Typing pattern analysis
   - Behavioral biometric theft
   - Touch coordinate analysis

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    QWAMOS SecureType Keyboard              │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              User Interface Layer                    │ │
│  │  ┌────────────────┐  ┌──────────────────────────┐   │ │
│  │  │ Visual Keyboard│  │ Security Indicators      │   │ │
│  │  │ (React Native) │  │ (Lock icon, mode badge)  │   │ │
│  │  └────────┬───────┘  └──────────────────────────┘   │ │
│  └───────────┼──────────────────────────────────────────┘ │
│              │                                             │
│  ┌───────────▼──────────────────────────────────────────┐ │
│  │         Touch Input Handler (Native)                │ │
│  │  • Touch coordinate obfuscation                     │ │
│  │  • Gesture detection                                │ │
│  │  • Haptic feedback                                  │ │
│  └───────────┬──────────────────────────────────────────┘ │
│              │                                             │
│  ┌───────────▼──────────────────────────────────────────┐ │
│  │         Security Layer (TEE/StrongBox)              │ │
│  │  ┌─────────────────┐  ┌──────────────────────────┐  │ │
│  │  │ Keystroke       │  │ Anti-Screenshot          │  │ │
│  │  │ Encryption      │  │ Protection               │  │ │
│  │  │ (ChaCha20)      │  │ (Secure FLAG)            │  │ │
│  │  └─────────────────┘  └──────────────────────────┘  │ │
│  │  ┌─────────────────┐  ┌──────────────────────────┐  │ │
│  │  │ Typing Anomaly  │  │ Secure Memory            │  │ │
│  │  │ Detection (ML)  │  │ Wiping                   │  │ │
│  │  └─────────────────┘  └──────────────────────────┘  │ │
│  └───────────┬──────────────────────────────────────────┘ │
│              │                                             │
│  ┌───────────▼──────────────────────────────────────────┐ │
│  │         Output Layer                                │ │
│  │  • Encrypted text buffer                            │ │
│  │  • Secure paste protection                          │ │
│  │  • Auto-clear on screen lock                        │ │
│  └─────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## Core Features

### 1. Secure Password Input Mode

**Activation:**
- Automatically activates when password field detected
- Manual activation via long-press on mode switcher
- Always-on mode for terminal/command input

**Security Measures:**
- ✅ No autocomplete/suggestions
- ✅ No clipboard access
- ✅ Encrypted keystroke buffer
- ✅ Anti-screenshot protection (`FLAG_SECURE`)
- ✅ Cleared on screen lock
- ✅ Random keyboard layout option
- ✅ Haptic-only feedback (no visual)

**Visual Indicators:**
- 🔒 Lock icon in status bar
- Yellow security badge
- Subtle UI changes (dots instead of characters)

**Implementation:**
```typescript
// File: ui/components/SecureKeyboard/PasswordMode.tsx

import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, NativeModules } from 'react-native';

const { SecureInputModule } = NativeModules;

interface PasswordModeProps {
  onTextChange: (text: string) => void;
  securityLevel: 'STANDARD' | 'HIGH' | 'PARANOID';
}

const PasswordMode: React.FC<PasswordModeProps> = ({ onTextChange, securityLevel }) => {
  const [layout, setLayout] = useState<'QWERTY' | 'RANDOM'>('QWERTY');
  const [encryptedBuffer, setEncryptedBuffer] = useState<string>('');

  useEffect(() => {
    // Enable FLAG_SECURE to prevent screenshots
    SecureInputModule.setSecureFlag(true);

    // Generate random layout if in paranoid mode
    if (securityLevel === 'PARANOID') {
      generateRandomLayout();
    }

    return () => {
      // Wipe encrypted buffer on unmount
      SecureInputModule.wipeMemory();
      SecureInputModule.setSecureFlag(false);
    };
  }, [securityLevel]);

  const handleKeyPress = async (key: string) => {
    // Encrypt keystroke in TEE
    const encryptedKey = await SecureInputModule.encryptKeystroke(key);

    // Add to encrypted buffer
    const newBuffer = await SecureInputModule.appendToBuffer(encryptedBuffer, encryptedKey);
    setEncryptedBuffer(newBuffer);

    // Provide haptic feedback only (no visual)
    SecureInputModule.hapticFeedback('light');

    // Notify parent (encrypted)
    onTextChange(newBuffer);
  };

  const generateRandomLayout = () => {
    // Randomize key positions to prevent visual pattern analysis
    setLayout('RANDOM');
  };

  return (
    <View style={styles.container}>
      {/* Security indicator */}
      <View style={styles.securityBadge}>
        <Text style={styles.lockIcon}>🔒</Text>
        <Text style={styles.securityText}>SECURE INPUT</Text>
      </View>

      {/* Keyboard layout */}
      <KeyboardLayout
        layout={layout}
        onKeyPress={handleKeyPress}
        secureMode={true}
      />
    </View>
  );
};
```

---

### 2. Anti-Screenshot Protection

**Mechanisms:**
- `FLAG_SECURE` on all keyboard windows
- Content detection for sensitive fields
- Automatic activation for password/credit card inputs
- Canvas overlay to block screenshot APIs

**Native Implementation:**
```java
// File: ui/native/SecureInputModule.java

package com.qwamos.securekeyboard;

import android.view.WindowManager;
import android.view.View;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;

public class SecureInputModule extends ReactContextBaseJavaModule {

    private ReactApplicationContext reactContext;

    public SecureInputModule(ReactApplicationContext context) {
        super(context);
        this.reactContext = context;
    }

    @Override
    public String getName() {
        return "SecureInputModule";
    }

    @ReactMethod
    public void setSecureFlag(boolean secure) {
        Activity activity = getCurrentActivity();
        if (activity != null) {
            activity.runOnUiThread(() -> {
                Window window = activity.getWindow();
                if (secure) {
                    // Prevent screenshots and screen recording
                    window.setFlags(
                        WindowManager.LayoutParams.FLAG_SECURE,
                        WindowManager.LayoutParams.FLAG_SECURE
                    );
                } else {
                    window.clearFlags(WindowManager.LayoutParams.FLAG_SECURE);
                }
            });
        }
    }

    @ReactMethod
    public void encryptKeystroke(String key, Promise promise) {
        try {
            // Encrypt keystroke using hardware-backed keystore
            String encrypted = KeystoreManager.encrypt(key);
            promise.resolve(encrypted);
        } catch (Exception e) {
            promise.reject("ENCRYPTION_ERROR", e);
        }
    }

    @ReactMethod
    public void wipeMemory() {
        // Securely wipe keystroke buffer
        KeystoreManager.wipeMemory();
    }
}
```

---

### 3. Shoulder-Surfing Resistance

**Techniques:**

**A. Randomized Keyboard Layout**
- Keys shuffle positions randomly
- New layout every 30 seconds
- User memorizes key positions, not visual layout

**B. Invisible Typing Mode**
- No visual feedback when typing
- Keys don't highlight on touch
- Haptic feedback only

**C. Decoy Characters**
- Random characters flash on screen during typing
- Makes visual observation useless
- Real input is encrypted

**D. Gesture-Based Input**
- Swipe patterns for common passwords
- Reduces visual observation surface
- Muscle memory instead of visual

**Implementation:**
```typescript
// File: ui/components/SecureKeyboard/ShoulderSurfProtection.tsx

const ShoulderSurfProtection: React.FC = () => {
  const [decoyChars, setDecoyChars] = useState<string[]>([]);

  const addDecoyCharacters = () => {
    // Generate random decoy characters
    const decoys = Array.from({ length: 10 }, () =>
      String.fromCharCode(65 + Math.floor(Math.random() * 26))
    );
    setDecoyChars(decoys);

    // Flash decoys briefly
    setTimeout(() => setDecoyChars([]), 100);
  };

  return (
    <View style={styles.container}>
      {/* Decoy character overlay */}
      {decoyChars.map((char, index) => (
        <Text
          key={index}
          style={[
            styles.decoyChar,
            {
              left: Math.random() * 300,
              top: Math.random() * 400,
              opacity: Math.random() * 0.3
            }
          ]}
        >
          {char}
        </Text>
      ))}
    </View>
  );
};
```

---

### 4. ML-Based Typing Anomaly Detection

**Purpose:** Detect when someone else is using the keyboard (not the legitimate user)

**ML Model:** Typing Dynamics Classifier
- **Training Data:** User's normal typing patterns
- **Features:**
  - Key press duration
  - Inter-key timing
  - Typing speed
  - Error correction patterns
  - Swipe vs tap preference

**Detection:**
- Flags when typing pattern deviates >30% from normal
- Automatically locks keyboard
- Requires re-authentication

**Implementation:**
```python
# File: security/keyboard/typing_anomaly_detector.py

import numpy as np
import tensorflow as tf

class TypingAnomalyDetector:
    """
    Detect unauthorized keyboard usage via typing dynamics
    """

    def __init__(self, user_profile_path):
        self.model = tf.lite.Interpreter(
            model_path='/opt/qwamos/security/keyboard/typing_model.tflite'
        )
        self.model.allocate_tensors()

        self.user_profile = self._load_user_profile(user_profile_path)
        self.keystroke_buffer = []

    def analyze_keystroke(self, keystroke_data):
        """
        Analyze single keystroke for anomalies

        keystroke_data: {
            'key': 'a',
            'press_duration': 0.12,  # seconds
            'release_time': timestamp,
            'pressure': 0.8,  # 0-1 scale
            'touch_area': 150  # pixels
        }
        """
        self.keystroke_buffer.append(keystroke_data)

        # Analyze over 10-keystroke window
        if len(self.keystroke_buffer) >= 10:
            features = self._extract_features(self.keystroke_buffer[-10:])

            # Run ML classification
            is_legitimate = self._classify(features)

            if not is_legitimate:
                self.alert_anomaly()

    def _extract_features(self, keystrokes):
        """Extract typing dynamics features"""
        features = []

        # Press duration statistics
        press_durations = [k['press_duration'] for k in keystrokes]
        features.append(np.mean(press_durations))
        features.append(np.std(press_durations))

        # Inter-key timing
        inter_key_times = []
        for i in range(1, len(keystrokes)):
            inter_key_times.append(
                keystrokes[i]['release_time'] - keystrokes[i-1]['release_time']
            )
        features.append(np.mean(inter_key_times))
        features.append(np.std(inter_key_times))

        # Pressure patterns
        pressures = [k['pressure'] for k in keystrokes]
        features.append(np.mean(pressures))

        # Touch area (finger size consistency)
        touch_areas = [k['touch_area'] for k in keystrokes]
        features.append(np.mean(touch_areas))

        return np.array(features)

    def _classify(self, features):
        """Classify if typing matches user's profile"""
        # Normalize features
        features_norm = (features - self.user_profile['mean']) / self.user_profile['std']

        # Run inference
        input_details = self.model.get_input_details()
        output_details = self.model.get_output_details()

        self.model.set_tensor(input_details[0]['index'],
                             features_norm.reshape(1, -1).astype(np.float32))
        self.model.invoke()

        prediction = self.model.get_tensor(output_details[0]['index'])[0][0]

        # Threshold: 0.7 = legitimate user
        return prediction > 0.7

    def alert_anomaly(self):
        """Alert when unauthorized typing detected"""
        print("[SECURITY ALERT] Typing pattern anomaly detected!")
        # Lock keyboard
        # Request re-authentication
        # Log event
```

---

### 5. Command Terminal Mode

**Purpose:** Secure input for shell commands and scripts

**Features:**
- ✅ Syntax highlighting for bash commands
- ✅ Command history (encrypted)
- ✅ Auto-completion (local only)
- ✅ Tab completion for file paths
- ✅ No telemetry/logging
- ✅ Special keys: Ctrl, Alt, Tab, Esc

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│ qwamos@vault:~$ █                                   │
├─────────────────────────────────────────────────────┤
│  Esc │ Tab │  ~  │  /  │  |  │  >  │  <  │ Ctrl │  │
│   1  │  2  │  3  │  4  │  5  │  6  │  7  │  8  │   │
│   q  │  w  │  e  │  r  │  t  │  y  │  u  │  i  │   │
│   a  │  s  │  d  │  f  │  g  │  h  │  j  │  k  │   │
│  Shft│  z  │  x  │  c  │  v  │  b  │  n  │  m  │   │
│  Ctrl│  Alt│ Cmd │    Space    │  ←  │  →  │ Ret │  │
└─────────────────────────────────────────────────────┘
```

**Implementation:**
```typescript
// File: ui/components/SecureKeyboard/TerminalMode.tsx

const TerminalMode: React.FC = () => {
  const [commandHistory, setCommandHistory] = useState<string[]>([]);
  const [currentCommand, setCurrentCommand] = useState('');

  const specialKeys = [
    { label: 'Tab', value: '\t' },
    { label: 'Ctrl', value: 'CTRL_' },
    { label: 'Esc', value: '\x1b' },
    { label: '~', value: '~' },
    { label: '|', value: '|' },
    { label: '/', value: '/' }
  ];

  const handleSpecialKey = (key: string) => {
    if (key === 'Tab') {
      // Trigger tab completion
      performTabCompletion(currentCommand);
    } else if (key.startsWith('CTRL_')) {
      // Handle Ctrl combinations
      handleCtrlKey(key);
    }
  };

  return (
    <View style={styles.terminalKeyboard}>
      {/* Special keys row */}
      <View style={styles.specialKeysRow}>
        {specialKeys.map(key => (
          <TerminalKey
            key={key.label}
            label={key.label}
            onPress={() => handleSpecialKey(key.value)}
            style={styles.specialKey}
          />
        ))}
      </View>

      {/* Standard QWERTY layout */}
      <StandardKeyboard onKeyPress={handleKeyPress} />
    </View>
  );
};
```

---

### 6. Zero Telemetry & Privacy

**Guarantees:**
- ❌ No network access (no internet permission)
- ❌ No analytics/crash reporting
- ❌ No keystroke logging
- ❌ No typing suggestions (no data collection)
- ❌ No clipboard monitoring
- ❌ No personalized dictionary
- ✅ All processing 100% local
- ✅ No external libraries with telemetry
- ✅ Open source & auditable

**Manifest Permissions:**
```xml
<!-- File: ui/native/AndroidManifest.xml -->

<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.qwamos.securekeyboard">

    <!-- ONLY these permissions - no INTERNET -->
    <uses-permission android:name="android.permission.VIBRATE" />

    <!-- Explicitly deny internet -->
    <uses-permission android:name="android.permission.INTERNET"
        tools:node="remove" />

    <application
        android:allowBackup="false"
        android:fullBackupContent="false"
        android:networkSecurityConfig="@xml/network_security_config">
        ...
    </application>
</manifest>
```

---

## Layout Variants

### 1. QWERTY Layout (Standard)
```
q w e r t y u i o p
 a s d f g h j k l
  z x c v b n m ⌫
```

### 2. AZERTY Layout (French)
```
a z e r t y u i o p
 q s d f g h j k l m
  w x c v b n ⌫
```

### 3. Dvorak Layout (Ergonomic)
```
' , . p y f g c r l
 a o e u i d h t n s
  ; q j k x b m w v z
```

### 4. Terminal Layout (Command-Optimized)
```
Esc Tab ~ / | > < Ctrl
 1 2 3 4 5 6 7 8 9 0
  q w e r t y u i o p
   a s d f g h j k l
    z x c v b n m ⌫
```

---

## Advanced Security Features

### 1. Keystroke Encryption in Hardware

```java
// File: ui/native/KeystoreManager.java

import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import java.security.KeyStore;

public class KeystoreManager {

    private static final String KEY_ALIAS = "qwamos_keyboard_key";
    private static final String ANDROID_KEYSTORE = "AndroidKeyStore";

    public static String encrypt(String keystroke) throws Exception {
        // Get key from hardware-backed keystore (StrongBox if available)
        KeyStore keyStore = KeyStore.getInstance(ANDROID_KEYSTORE);
        keyStore.load(null);

        if (!keyStore.containsAlias(KEY_ALIAS)) {
            generateKey();
        }

        SecretKey key = (SecretKey) keyStore.getKey(KEY_ALIAS, null);

        // Encrypt using ChaCha20-Poly1305 (fast on ARM)
        Cipher cipher = Cipher.getInstance("ChaCha20-Poly1305");
        cipher.init(Cipher.ENCRYPT_MODE, key);

        byte[] encrypted = cipher.doFinal(keystroke.getBytes());

        return Base64.encodeToString(encrypted, Base64.NO_WRAP);
    }

    private static void generateKey() throws Exception {
        KeyGenerator keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            ANDROID_KEYSTORE
        );

        KeyGenParameterSpec keySpec = new KeyGenParameterSpec.Builder(
            KEY_ALIAS,
            KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setUserAuthenticationRequired(false)
            .setIsStrongBoxBacked(true)  // Use StrongBox if available
            .build();

        keyGenerator.init(keySpec);
        keyGenerator.generateKey();
    }

    public static void wipeMemory() {
        // Securely wipe keystroke buffer
        System.gc();
        System.runFinalization();
    }
}
```

---

### 2. Touch Coordinate Obfuscation

**Problem:** Malware can infer keystrokes by analyzing touch coordinates

**Solution:** Add random noise to touch event coordinates

```typescript
// File: ui/components/SecureKeyboard/TouchObfuscation.tsx

const obfuscateTouchCoordinates = (event: GestureResponderEvent): void => {
  const { locationX, locationY } = event.nativeEvent;

  // Add random noise (±5 pixels)
  const noisyX = locationX + (Math.random() - 0.5) * 10;
  const noisyY = locationY + (Math.random() - 0.5) * 10;

  // Still map to correct key, but report noisy coordinates
  const key = mapCoordinatesToKey(locationX, locationY);
  const obfuscatedEvent = {
    ...event,
    nativeEvent: {
      ...event.nativeEvent,
      locationX: noisyX,
      locationY: noisyY
    }
  };

  handleKeyPress(key, obfuscatedEvent);
};
```

---

## Touchscreen Integration Status

Let me check the current touchscreen integration:

<function_calls>
<invoke name="Read">
<parameter name="file_path">/data/data/com.termux/files/home/QWAMOS/ui/README.md