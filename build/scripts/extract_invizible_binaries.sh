#!/bin/bash
#
# QWAMOS InviZible Pro Binary Extraction Script
#
# Extracts Tor, I2P (i2pd), and DNSCrypt-proxy binaries from InviZible Pro APK
# These are production-ready ARM64 binaries optimized for Android
#
# InviZible Pro: https://github.com/Gedsh/InviZible
# APK: https://f-droid.org/packages/pan.alexander.tordnscrypt.stable/
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QWAMOS_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BINARIES_DIR="$QWAMOS_ROOT/network/binaries"
TEMP_DIR="$HOME/.cache/qwamos_invizible_extract"

# InviZible Pro APK download URL (F-Droid)
INVIZIBLE_VERSION="7.4.3"
INVIZIBLE_URL="https://f-droid.org/repo/pan.alexander.tordnscrypt.stable_${INVIZIBLE_VERSION}.apk"

echo "========================================================================"
echo "QWAMOS InviZible Pro Binary Extraction"
echo "========================================================================"
echo ""
echo "InviZible Pro is an excellent privacy app that bundles:"
echo "  - Tor (The Onion Router)"
echo "  - Purple I2P (i2pd)"
echo "  - DNSCrypt-proxy"
echo ""
echo "All compiled for ARM64 Android with optimizations."
echo ""
echo "========================================================================"
echo ""

# Check for required tools
echo "[1/8] Checking required tools..."
REQUIRED_TOOLS=("curl" "unzip" "file")

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        echo "   ERROR: Required tool '$tool' not found!"
        echo "   Install with: pkg install $tool"
        exit 1
    fi
done

echo "   ✅ All required tools present"

# Create directories
echo ""
echo "[2/8] Creating directories..."
mkdir -p "$BINARIES_DIR"/{tor,i2p,dnscrypt}
mkdir -p "$TEMP_DIR"
echo "   ✅ Directories created"

# Download InviZible Pro APK
echo ""
echo "[3/8] Downloading InviZible Pro APK..."
echo "   URL: $INVIZIBLE_URL"
echo "   Size: ~50MB (this may take a few minutes)"

if [ -f "$TEMP_DIR/invizible.apk" ]; then
    echo "   ℹ️  APK already downloaded, skipping..."
else
    curl -L -o "$TEMP_DIR/invizible.apk" "$INVIZIBLE_URL" || {
        echo "   ❌ Download failed!"
        echo "   Please download manually from:"
        echo "   https://f-droid.org/packages/pan.alexander.tordnscrypt.stable/"
        echo "   And place at: $TEMP_DIR/invizible.apk"
        exit 1
    }
    echo "   ✅ Download complete"
fi

# Extract APK
echo ""
echo "[4/8] Extracting APK..."
cd "$TEMP_DIR"
unzip -q -o invizible.apk -d extracted/
echo "   ✅ APK extracted"

# Locate ARM64 binaries
echo ""
echo "[5/8] Locating ARM64 binaries..."

# InviZible Pro stores binaries in lib/arm64-v8a/
LIB_DIR="$TEMP_DIR/extracted/lib/arm64-v8a"

if [ ! -d "$LIB_DIR" ]; then
    echo "   ❌ ARM64 library directory not found!"
    echo "   Expected: $LIB_DIR"
    echo "   APK structure may have changed."
    exit 1
fi

echo "   Found ARM64 library directory"

# List all libraries
echo ""
echo "   Available libraries:"
ls -lh "$LIB_DIR"/ | awk '{print "   - " $9 " (" $5 ")"}'

# Extract Tor binary
echo ""
echo "[6/8] Extracting Tor binary..."

TOR_LIB="$LIB_DIR/libtor.so"
if [ -f "$TOR_LIB" ]; then
    cp "$TOR_LIB" "$BINARIES_DIR/tor/tor"
    chmod +x "$BINARIES_DIR/tor/tor"

    # Verify
    file "$BINARIES_DIR/tor/tor"
    size=$(stat -f%z "$BINARIES_DIR/tor/tor" 2>/dev/null || stat -c%s "$BINARIES_DIR/tor/tor")
    echo "   ✅ Tor extracted ($((size / 1024 / 1024))MB)"
else
    echo "   ⚠️  Tor binary not found (libtor.so)"
fi

# Extract I2P binary
echo ""
echo "[7/8] Extracting I2P binary..."

I2P_LIB="$LIB_DIR/libi2pd.so"
if [ -f "$I2P_LIB" ]; then
    cp "$I2P_LIB" "$BINARIES_DIR/i2p/i2pd"
    chmod +x "$BINARIES_DIR/i2p/i2pd"

    # Verify
    file "$BINARIES_DIR/i2p/i2pd"
    size=$(stat -f%z "$BINARIES_DIR/i2p/i2pd" 2>/dev/null || stat -c%s "$BINARIES_DIR/i2p/i2pd")
    echo "   ✅ I2P extracted ($((size / 1024 / 1024))MB)"
else
    echo "   ⚠️  I2P binary not found (libi2pd.so)"
fi

# Extract DNSCrypt binary
echo ""
echo "[8/8] Extracting DNSCrypt binary..."

DNSCRYPT_LIB="$LIB_DIR/libdnscrypt-proxy.so"
if [ -f "$DNSCRYPT_LIB" ]; then
    cp "$DNSCRYPT_LIB" "$BINARIES_DIR/dnscrypt/dnscrypt-proxy"
    chmod +x "$BINARIES_DIR/dnscrypt/dnscrypt-proxy"

    # Verify
    file "$BINARIES_DIR/dnscrypt/dnscrypt-proxy"
    size=$(stat -f%z "$BINARIES_DIR/dnscrypt/dnscrypt-proxy" 2>/dev/null || stat -c%s "$BINARIES_DIR/dnscrypt/dnscrypt-proxy")
    echo "   ✅ DNSCrypt extracted ($((size / 1024 / 1024))MB)"
else
    echo "   ⚠️  DNSCrypt binary not found (libdnscrypt-proxy.so)"
fi

# Create version info
echo ""
echo "Creating version information..."
cat > "$BINARIES_DIR/VERSION" <<EOF
QWAMOS Network Binaries
Extracted from: InviZible Pro v${INVIZIBLE_VERSION}
Source: https://github.com/Gedsh/InviZible
License: GPLv3
Extraction Date: $(date)

Binaries:
- Tor: $(file "$BINARIES_DIR/tor/tor" 2>/dev/null || echo "Not found")
- I2P: $(file "$BINARIES_DIR/i2p/i2pd" 2>/dev/null || echo "Not found")
- DNSCrypt: $(file "$BINARIES_DIR/dnscrypt/dnscrypt-proxy" 2>/dev/null || echo "Not found")

These binaries are production-ready and optimized for ARM64 Android.
EOF

# Cleanup option
echo ""
read -p "Clean up temporary files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$TEMP_DIR"
    echo "   ✅ Temporary files cleaned"
fi

# Summary
echo ""
echo "========================================================================"
echo "✅ Binary Extraction Complete"
echo "========================================================================"
echo ""
echo "Extracted binaries location: $BINARIES_DIR/"
echo ""
echo "Next steps:"
echo "  1. Test binaries: ./network/scripts/test_binaries.sh"
echo "  2. Update controller paths to use extracted binaries"
echo "  3. Run integration tests"
echo ""
echo "Note: These binaries are .so files but work as standalone executables"
echo "      when copied and made executable."
echo ""

exit 0
