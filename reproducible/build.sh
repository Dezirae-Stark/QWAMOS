#!/bin/bash
#
# QWAMOS Reproducible Build Script
# Builds QWAMOS APK with reproducible build settings
#

set -e
set -o pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output/apk"
LOG_DIR="$SCRIPT_DIR/output/logs"
BUILD_NUMBER="${1:-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_DIR/build-${BUILD_NUMBER}.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_DIR/build-${BUILD_NUMBER}.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_DIR/build-${BUILD_NUMBER}.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/build-${BUILD_NUMBER}.log"
}

# Create output directories
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

log_info "=== QWAMOS Reproducible Build #${BUILD_NUMBER} ==="
log_info "Project root: $PROJECT_ROOT"
log_info "Output directory: $OUTPUT_DIR"
log_info "Build started: $(date -u)"

# Check for Android project
if [ ! -d "$PROJECT_ROOT/android" ]; then
    log_error "Android project not found at $PROJECT_ROOT/android"
    exit 1
fi

cd "$PROJECT_ROOT/android"

# Clean previous builds
log_info "Cleaning previous builds..."
./gradlew clean || {
    log_warning "Gradle clean failed, continuing anyway"
}

# Remove build artifacts
rm -rf app/build
rm -rf .gradle
rm -rf build

log_success "Clean completed"

# Set reproducible build environment variables
log_info "Setting reproducible build environment..."

# Fixed timestamp for reproducibility (use SOURCE_DATE_EPOCH)
# Default to project start date if not set
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-1704067200}" # 2024-01-01 00:00:00 UTC

# Normalize locale
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
export TZ=UTC

# JVM settings for reproducibility
export JAVA_TOOL_OPTIONS="-Duser.timezone=UTC -Duser.language=en -Duser.country=US -Dfile.encoding=UTF-8"

# Gradle settings for reproducibility
export GRADLE_OPTS="-Dorg.gradle.jvmargs=-Xmx2g -Dfile.encoding=UTF-8"

log_info "Environment configured:"
log_info "  SOURCE_DATE_EPOCH: $SOURCE_DATE_EPOCH"
log_info "  Date: $(date -u -d @$SOURCE_DATE_EPOCH)"
log_info "  LANG: $LANG"
log_info "  TZ: $TZ"

# Create gradle.properties for reproducible builds
cat > gradle.properties <<EOF
# Reproducible build settings
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
org.gradle.parallel=false
org.gradle.caching=false
org.gradle.configuration-cache=false

# Android build settings
android.useAndroidX=true
android.enableJetifier=true

# Reproducibility settings
android.injected.build.abi=
android.injected.build.density=

# Build timestamp (for reproducibility)
buildTimestamp=$SOURCE_DATE_EPOCH
EOF

log_success "gradle.properties configured"

# Ensure deterministic Gradle wrapper
log_info "Validating Gradle wrapper..."
if [ -f "gradle/wrapper/gradle-wrapper.properties" ]; then
    log_info "Gradle wrapper version:"
    grep "distributionUrl" gradle/wrapper/gradle-wrapper.properties | tee -a "$LOG_DIR/build-${BUILD_NUMBER}.log"
fi

# Build the APK with reproducible settings
log_info "Building APK (this may take several minutes)..."

./gradlew assembleRelease \
    --no-daemon \
    --no-build-cache \
    --no-configuration-cache \
    --no-parallel \
    -Dorg.gradle.jvmargs="-Xmx2g -Dfile.encoding=UTF-8" \
    -PbuildTimestamp="$SOURCE_DATE_EPOCH" \
    2>&1 | tee -a "$LOG_DIR/build-${BUILD_NUMBER}.log"

BUILD_STATUS=${PIPESTATUS[0]}

if [ $BUILD_STATUS -ne 0 ]; then
    log_error "Build failed with status $BUILD_STATUS"
    exit $BUILD_STATUS
fi

log_success "Build completed successfully"

# Find the built APK
log_info "Locating built APK..."

APK_PATH=$(find app/build/outputs/apk/release -name "*.apk" -type f | head -n 1)

if [ -z "$APK_PATH" ]; then
    log_error "APK not found in app/build/outputs/apk/release"
    exit 1
fi

log_success "APK found: $APK_PATH"

# Copy APK to output directory
APK_NAME="qwamos-build${BUILD_NUMBER}-$(date -u -d @$SOURCE_DATE_EPOCH +%Y%m%d).apk"
cp "$APK_PATH" "$OUTPUT_DIR/$APK_NAME"

log_success "APK copied to: $OUTPUT_DIR/$APK_NAME"

# Calculate checksums
log_info "Calculating checksums..."

cd "$OUTPUT_DIR"

# SHA-256
SHA256=$(sha256sum "$APK_NAME" | awk '{print $1}')
echo "$SHA256  $APK_NAME" > "$APK_NAME.sha256"
log_info "SHA-256: $SHA256"

# SHA-512
SHA512=$(sha512sum "$APK_NAME" | awk '{print $1}')
echo "$SHA512  $APK_NAME" > "$APK_NAME.sha512"
log_info "SHA-512: $SHA512"

# MD5 (for compatibility)
MD5=$(md5sum "$APK_NAME" | awk '{print $1}')
echo "$MD5  $APK_NAME" > "$APK_NAME.md5"
log_info "MD5: $MD5"

# Get APK size
APK_SIZE=$(stat -c%s "$APK_NAME")
log_info "APK size: $APK_SIZE bytes ($(numfmt --to=iec-i --suffix=B $APK_SIZE))"

# Extract APK metadata
log_info "Extracting APK metadata..."

if command -v aapt >/dev/null 2>&1; then
    aapt dump badging "$APK_NAME" > "$APK_NAME.metadata.txt" 2>&1 || true

    # Extract version info
    VERSION_NAME=$(aapt dump badging "$APK_NAME" | grep "versionName" | sed "s/.*versionName='\([^']*\)'.*/\1/" || echo "unknown")
    VERSION_CODE=$(aapt dump badging "$APK_NAME" | grep "versionCode" | sed "s/.*versionCode='\([^']*\)'.*/\1/" || echo "unknown")

    log_info "Version: $VERSION_NAME (code: $VERSION_CODE)"
fi

# Create build manifest
log_info "Creating build manifest..."

cat > "$APK_NAME.manifest.json" <<EOF
{
  "build_number": $BUILD_NUMBER,
  "apk_name": "$APK_NAME",
  "build_date": "$(date -u -d @$SOURCE_DATE_EPOCH +%Y-%m-%dT%H:%M:%SZ)",
  "source_date_epoch": $SOURCE_DATE_EPOCH,
  "version_name": "${VERSION_NAME:-unknown}",
  "version_code": "${VERSION_CODE:-unknown}",
  "checksums": {
    "sha256": "$SHA256",
    "sha512": "$SHA512",
    "md5": "$MD5"
  },
  "size_bytes": $APK_SIZE,
  "build_environment": {
    "lang": "$LANG",
    "tz": "$TZ",
    "java_tool_options": "$JAVA_TOOL_OPTIONS"
  },
  "gradle_version": "$(grep distributionUrl $PROJECT_ROOT/android/gradle/wrapper/gradle-wrapper.properties | sed 's/.*gradle-//' | sed 's/-bin.*//' || echo 'unknown')",
  "build_host": "$(uname -n)",
  "build_os": "$(uname -s) $(uname -r)"
}
EOF

log_success "Build manifest created: $APK_NAME.manifest.json"

# Summary
log_info ""
log_info "=== Build Summary ==="
log_info "Build Number: $BUILD_NUMBER"
log_info "APK: $OUTPUT_DIR/$APK_NAME"
log_info "SHA-256: $SHA256"
log_info "Size: $(numfmt --to=iec-i --suffix=B $APK_SIZE)"
log_info "Build completed: $(date -u)"
log_info ""

log_success "Reproducible build completed successfully!"

exit 0
