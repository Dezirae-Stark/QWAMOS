package com.qwamos.threatdetection;

import com.facebook.react.ReactPackage;
import com.facebook.react.bridge.NativeModule;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.uimanager.ViewManager;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * QWAMOS Threat Detection Package
 *
 * React Native package that registers the QWAMOSThreatBridge native module.
 *
 * Usage in MainApplication.java:
 *
 * import com.qwamos.threatdetection.QWAMOSThreatPackage;
 *
 * @Override
 * protected List<ReactPackage> getPackages() {
 *     return Arrays.<ReactPackage>asList(
 *         new MainReactPackage(),
 *         new QWAMOSThreatPackage()
 *     );
 * }
 */
public class QWAMOSThreatPackage implements ReactPackage {

    @Override
    public List<NativeModule> createNativeModules(ReactApplicationContext reactContext) {
        List<NativeModule> modules = new ArrayList<>();
        modules.add(new QWAMOSThreatBridge(reactContext));
        return modules;
    }

    @Override
    public List<ViewManager> createViewManagers(ReactApplicationContext reactContext) {
        return Collections.emptyList();
    }
}
