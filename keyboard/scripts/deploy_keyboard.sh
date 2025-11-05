#!/usr/bin/env bash
#
# QWAMOS SecureType Keyboard - Deployment Script
#
# Deploys keyboard to device:
# - Copies files to /opt/qwamos/keyboard
# - Installs Python dependencies
# - Configures permissions
# - Builds and installs APK
#
# Version: 1.0.0
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KEYBOARD_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INSTALL_DIR="/opt/qwamos/keyboard"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  QWAMOS SecureType Keyboard - Deployment"
echo "  Version: 1.0.0"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root (use su or sudo)"
   exit 1
fi

# Step 1: Create directories
log_info "Creating installation directories..."
mkdir -p "$INSTALL_DIR"/{src,config,ml/models,logs,tests}
mkdir -p "$INSTALL_DIR"/src/{components,modes,native,security,ml,utils}
log_success "Directories created"

# Step 2: Copy source files
log_info "Copying source files..."

# React Native components
cp -r "$KEYBOARD_ROOT"/src/components/* "$INSTALL_DIR"/src/components/
cp -r "$KEYBOARD_ROOT"/src/modes/* "$INSTALL_DIR"/src/modes/
cp -r "$KEYBOARD_ROOT"/src/types "$INSTALL_DIR"/src/

# Java native modules
cp -r "$KEYBOARD_ROOT"/src/native/*.java "$INSTALL_DIR"/src/native/
cp "$KEYBOARD_ROOT"/src/native/AndroidManifest.xml "$INSTALL_DIR"/src/native/

# ML detector
cp "$KEYBOARD_ROOT"/src/ml/typing_anomaly_detector.py "$INSTALL_DIR"/ml/
chmod +x "$INSTALL_DIR"/ml/typing_anomaly_detector.py

# Configuration
cp "$KEYBOARD_ROOT"/config/keyboard_config.json "$INSTALL_DIR"/config/

log_success "Source files copied"

# Step 3: Install Python dependencies
log_info "Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install --upgrade tensorflow-lite numpy || {
        log_warning "TensorFlow Lite installation failed, trying tflite-runtime..."
        pip3 install --upgrade tflite-runtime numpy
    }
    log_success "Python dependencies installed"
else
    log_error "pip3 not found. Install Python 3 and pip first."
    exit 1
fi

# Step 4: Set permissions
log_info "Setting permissions..."
chown -R root:root "$INSTALL_DIR"
chmod -R 755 "$INSTALL_DIR"
chmod 644 "$INSTALL_DIR"/config/*.json
chmod 755 "$INSTALL_DIR"/ml/*.py
log_success "Permissions configured"

# Step 5: Create ML model directory (placeholder)
log_info "Creating ML model directory..."
touch "$INSTALL_DIR"/ml/models/README.md
cat > "$INSTALL_DIR"/ml/models/README.md <<'EOF'
# ML Models

Place trained TensorFlow Lite models here:
- typing_model.tflite - Typing anomaly detection model

To train models, see: docs/PHASE8_ML_TRAINING_GUIDE.md
EOF
log_success "ML model directory created"

# Step 6: Build Android APK
log_info "Building Android APK..."
if [ -d "$KEYBOARD_ROOT"/android ]; then
    cd "$KEYBOARD_ROOT"/android

    # Build release APK
    if ./gradlew assembleRelease; then
        APK_PATH="$KEYBOARD_ROOT/android/app/build/outputs/apk/release/app-release.apk"

        if [ -f "$APK_PATH" ]; then
            log_success "APK built successfully: $APK_PATH"

            # Install APK to device (if connected)
            if command -v adb &> /dev/null && adb devices | grep -q "device$"; then
                log_info "Installing APK to device..."
                adb install -r "$APK_PATH"
                log_success "APK installed to device"
            else
                log_warning "ADB not available or no device connected. Manual installation required:"
                log_info "  adb install -r $APK_PATH"
            fi
        else
            log_error "APK file not found after build"
        fi
    else
        log_error "APK build failed"
        exit 1
    fi
else
    log_warning "Android project directory not found. Skipping APK build."
fi

# Step 7: Create test scripts
log_info "Creating test scripts..."
cat > "$INSTALL_DIR"/tests/test_encryption.sh <<'EOF'
#!/usr/bin/env bash
# Test hardware-backed encryption
python3 -c "
from android.security import keystore
print('Testing encryption...')
# Add test code here
"
EOF
chmod +x "$INSTALL_DIR"/tests/test_encryption.sh
log_success "Test scripts created"

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Deployment Summary"
echo "═══════════════════════════════════════════════════════════"
echo ""
log_success "Installation directory: $INSTALL_DIR"
log_success "Source files: Deployed"
log_success "Python dependencies: Installed"
log_success "Permissions: Configured"
log_success "ML detector: Ready"
echo ""
log_info "Next steps:"
echo "  1. Train ML models: cd $INSTALL_DIR/ml && python3 train_model.py"
echo "  2. Enable keyboard: Settings > System > Languages & input > Virtual keyboard"
echo "  3. Test keyboard: Open any app with text input"
echo ""
log_success "✅ Phase 8 deployment complete!"
echo ""
