/**
 * QWAMOS SecureType Keyboard - React Native Package
 *
 * Registers native modules with React Native:
 * - SecureInputModule
 * - TypingAnomalyModule
 *
 * @module SecureInputPackage
 * @version 1.0.0
 */

package com.qwamos.securekeyboard;

import com.facebook.react.ReactPackage;
import com.facebook.react.bridge.NativeModule;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.uimanager.ViewManager;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class SecureInputPackage implements ReactPackage {

    @Override
    public List<NativeModule> createNativeModules(ReactApplicationContext reactContext) {
        List<NativeModule> modules = new ArrayList<>();

        // Register SecureInputModule
        modules.add(new SecureInputModule(reactContext));

        // Register TypingAnomalyModule
        modules.add(new TypingAnomalyModule(reactContext));

        return modules;
    }

    @Override
    public List<ViewManager> createViewManagers(ReactApplicationContext reactContext) {
        return Collections.emptyList();
    }
}
