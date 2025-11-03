package com.qwamos.network;

import com.facebook.react.ReactPackage;
import com.facebook.react.bridge.NativeModule;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.uimanager.ViewManager;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * QWAMOS Network Package
 *
 * React Native package that registers the QWAMOSNetworkBridge native module.
 *
 * To use, add this to your MainApplication.java:
 *
 * @Override
 * protected List<ReactPackage> getPackages() {
 *   List<ReactPackage> packages = new PackageList(this).getPackages();
 *   packages.add(new QWAMOSNetworkPackage());  // Add this line
 *   return packages;
 * }
 */
public class QWAMOSNetworkPackage implements ReactPackage {

    @Override
    public List<NativeModule> createNativeModules(ReactApplicationContext reactContext) {
        List<NativeModule> modules = new ArrayList<>();
        modules.add(new QWAMOSNetworkBridge(reactContext));
        return modules;
    }

    @Override
    public List<ViewManager> createViewManagers(ReactApplicationContext reactContext) {
        return Collections.emptyList();
    }
}
