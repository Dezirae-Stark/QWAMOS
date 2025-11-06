# QWAMOS Flutter UI - Build Guide

Complete guide for building the QWAMOS Hypervisor UI APK on different platforms.

---

## 🎯 Quick Start (Automated)

### Option 1: GitHub Actions (Recommended for CI/CD)

The easiest way to build the APK is using our automated GitHub Actions workflow:

1. **Push code to GitHub:**
   ```bash
   git push origin master
   ```

2. **Workflow automatically triggers:**
   - Builds debug and release APKs
   - Runs Flutter analysis and tests
   - Uploads artifacts to GitHub Actions

3. **Download APKs:**
   - Go to: https://github.com/Dezirae-Stark/QWAMOS/actions
   - Click latest "Build Flutter UI" workflow run
   - Download artifacts:
     - `qwamos-ui-debug.apk` (debug build)
     - `qwamos-ui-release` (release builds for arm64-v8a, armeabi-v7a, x86_64)

4. **Install on device:**
   ```bash
   adb install app-arm64-v8a-release.apk
   ```

**Benefits:**
- ✅ No local setup required
- ✅ Automated builds on every commit
- ✅ Consistent build environment
- ✅ APKs available as downloadable artifacts
- ✅ Automatic release creation on tags

---

## 📦 Option 2: Build Locally

### Prerequisites

**Required:**
- Flutter SDK 3.24.5+ ([Download](https://docs.flutter.dev/get-started/install))
- Java JDK 17+ (for Android builds)
- Android SDK (installed via Flutter)
- Git

**Check your setup:**
```bash
flutter doctor -v
```

All items should show ✓ (or at least SDK/JDK should be green).

---

## 🖥️ Platform-Specific Instructions

### Linux (Ubuntu/Debian)

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y curl git unzip xz-utils zip libglu1-mesa
   ```

2. **Install Flutter:**
   ```bash
   cd ~
   wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.24.5-stable.tar.xz
   tar xf flutter_linux_3.24.5-stable.tar.xz
   export PATH="$PATH:$HOME/flutter/bin"

   # Add to ~/.bashrc for persistence
   echo 'export PATH="$PATH:$HOME/flutter/bin"' >> ~/.bashrc
   ```

3. **Install Android SDK:**
   ```bash
   flutter doctor --android-licenses  # Accept licenses
   flutter doctor  # Verify setup
   ```

4. **Clone and build:**
   ```bash
   git clone https://github.com/Dezirae-Stark/QWAMOS.git
   cd QWAMOS/ui
   flutter pub get
   flutter build apk --release --split-per-abi
   ```

5. **Output:**
   ```
   ui/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk   (64-bit ARM)
   ui/build/app/outputs/flutter-apk/app-armeabi-v7a-release.apk (32-bit ARM)
   ui/build/app/outputs/flutter-apk/app-x86_64-release.apk      (64-bit x86)
   ```

---

### macOS

1. **Install Homebrew (if not installed):**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Flutter:**
   ```bash
   cd ~
   curl -O https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/flutter_macos_3.24.5-stable.zip
   unzip flutter_macos_3.24.5-stable.zip
   export PATH="$PATH:$HOME/flutter/bin"

   # Add to ~/.zshrc for persistence
   echo 'export PATH="$PATH:$HOME/flutter/bin"' >> ~/.zshrc
   ```

3. **Install Android SDK:**
   ```bash
   flutter doctor --android-licenses
   flutter doctor
   ```

4. **Clone and build:**
   ```bash
   git clone https://github.com/Dezirae-Stark/QWAMOS.git
   cd QWAMOS/ui
   flutter pub get
   flutter build apk --release --split-per-abi
   ```

---

### Windows

1. **Download Flutter:**
   - Visit: https://docs.flutter.dev/get-started/install/windows
   - Download Flutter SDK 3.24.5
   - Extract to `C:\src\flutter`

2. **Add to PATH:**
   - Search "Environment Variables" in Windows
   - Edit PATH and add: `C:\src\flutter\bin`

3. **Install Android SDK:**
   ```powershell
   flutter doctor --android-licenses
   flutter doctor
   ```

4. **Clone and build:**
   ```powershell
   git clone https://github.com/Dezirae-Stark/QWAMOS.git
   cd QWAMOS\ui
   flutter pub get
   flutter build apk --release --split-per-abi
   ```

---

## 🏗️ Build Commands Reference

### Debug Build (for testing)
```bash
flutter build apk --debug
# Output: app-debug.apk (~50MB, with debug symbols)
```

### Release Build (single APK, all architectures)
```bash
flutter build apk --release
# Output: app-release.apk (~25MB, universal)
```

### Release Build (split per ABI, recommended)
```bash
flutter build apk --release --split-per-abi
# Output:
#   app-arm64-v8a-release.apk   (~8MB, 64-bit ARM - RECOMMENDED for most phones)
#   app-armeabi-v7a-release.apk (~7MB, 32-bit ARM)
#   app-x86_64-release.apk      (~9MB, 64-bit x86 - for emulators)
```

### Profile Build (performance profiling)
```bash
flutter build apk --profile
# Output: app-profile.apk (for performance analysis)
```

---

## 📱 Installation on Device

### Via ADB (Android Debug Bridge)

1. **Enable USB Debugging:**
   - Settings → About Phone → Tap "Build Number" 7 times
   - Settings → Developer Options → Enable "USB Debugging"

2. **Connect device and install:**
   ```bash
   # Check device is connected
   adb devices

   # Install APK
   adb install build/app/outputs/flutter-apk/app-arm64-v8a-release.apk

   # Or install and grant all permissions
   adb install -g build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
   ```

3. **Launch app:**
   ```bash
   adb shell am start -n com.qwamos.ui/.MainActivity
   ```

### Via File Transfer

1. Copy APK to device:
   ```bash
   adb push build/app/outputs/flutter-apk/app-arm64-v8a-release.apk /sdcard/Download/
   ```

2. On device:
   - Open File Manager → Downloads
   - Tap APK file
   - Allow "Install from Unknown Sources" if prompted
   - Install

---

## 🧪 Testing & Validation

### Run Tests
```bash
flutter test
```

### Analyze Code
```bash
flutter analyze
```

### Check for Issues
```bash
flutter doctor -v
```

### Run on Emulator/Device
```bash
flutter devices        # List available devices
flutter run            # Run on default device
flutter run -d <id>    # Run on specific device
```

---

## 🔧 Troubleshooting

### "Flutter not found"
```bash
# Add to PATH (Linux/macOS)
export PATH="$PATH:$HOME/flutter/bin"

# Windows: Add to Environment Variables
C:\src\flutter\bin
```

### "Android licenses not accepted"
```bash
flutter doctor --android-licenses
# Press 'y' to accept all
```

### "Gradle build failed"
```bash
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter build apk
```

### "SDK version mismatch"
```bash
# Update Flutter
flutter upgrade

# Check version
flutter --version
```

### "Java version issues"
```bash
# Check Java version
java -version

# Install Java 17
sudo apt install openjdk-17-jdk  # Linux
brew install openjdk@17          # macOS
```

---

## 📊 Build Output Details

### APK Sizes (approximate)

| Build Type | Architecture | Size | Use Case |
|------------|-------------|------|----------|
| Debug | Universal | ~50MB | Development/Testing |
| Release | Universal | ~25MB | All devices (larger file) |
| Release | arm64-v8a | ~8MB | Modern 64-bit phones (RECOMMENDED) |
| Release | armeabi-v7a | ~7MB | Older 32-bit phones |
| Release | x86_64 | ~9MB | Emulators |

**Recommendation:** Use `app-arm64-v8a-release.apk` for Motorola Edge 2025 and most modern Android devices.

---

## 🚀 Production Deployment

### Signing for Production (Optional)

1. **Create keystore:**
   ```bash
   keytool -genkey -v -keystore qwamos-release.jks -keyalg RSA -keysize 2048 -validity 10000 -alias qwamos
   ```

2. **Create key.properties:**
   ```bash
   cat > android/key.properties << EOF
   storePassword=<password>
   keyPassword=<password>
   keyAlias=qwamos
   storeFile=../../qwamos-release.jks
   EOF
   ```

3. **Build signed APK:**
   ```bash
   flutter build apk --release --split-per-abi
   ```

### Automated Builds (CI/CD)

The GitHub Actions workflow automatically:
- Builds on every push to `master`
- Creates debug and release APKs
- Uploads artifacts (30-90 day retention)
- Creates GitHub releases on version tags

**Trigger manual build:**
- Go to Actions → Build Flutter UI → Run workflow

---

## 📝 Build Verification

After building, verify your APK:

```bash
# Check APK info
aapt dump badging build/app/outputs/flutter-apk/app-arm64-v8a-release.apk | head -20

# APK size
ls -lh build/app/outputs/flutter-apk/*.apk

# APK contents
unzip -l build/app/outputs/flutter-apk/app-arm64-v8a-release.apk | grep -E "lib/|assets/"
```

**Expected output:**
- Minimum SDK: 21 (Android 5.0)
- Target SDK: 34 (Android 14)
- Neon shader files in `assets/shaders/`
- ARM64 native libraries in `lib/arm64-v8a/`

---

## 🎯 Quick Reference

### Essential Commands

```bash
# Setup
flutter pub get                           # Install dependencies
flutter doctor                            # Check setup

# Build
flutter build apk --release --split-per-abi  # Production APK
flutter build apk --debug                    # Debug APK

# Test
flutter test                              # Run tests
flutter analyze                           # Code analysis
flutter run                               # Run on device

# Clean
flutter clean                             # Clear build cache
flutter pub cache repair                  # Fix package issues
```

---

## 📞 Support

**Build Issues:**
- Check Flutter docs: https://docs.flutter.dev/deployment/android
- QWAMOS GitHub Issues: https://github.com/Dezirae-Stark/QWAMOS/issues
- Flutter Discord: https://discord.gg/flutter

**QWAMOS UI Specific:**
- See `ui/README.md` for widget documentation
- See `ui/IMPLEMENTATION_GUIDE.md` for code architecture
- GitHub Actions logs for automated build errors

---

**Built for QWAMOS • Flutter 3.24.5 • Production Ready**
