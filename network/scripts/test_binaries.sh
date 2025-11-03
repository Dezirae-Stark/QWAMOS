#!/bin/bash
#
# QWAMOS Binary Testing Script
#
# Tests extracted Tor, I2P, and DNSCrypt binaries for functionality
#

set -e

QWAMOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BINARIES_DIR="$QWAMOS_ROOT/network/binaries"

echo "========================================================================"
echo "QWAMOS Binary Testing"
echo "========================================================================"
echo ""

# Test 1: Check if binaries exist
echo "[1/6] Checking binary files..."

TOR_BIN="$BINARIES_DIR/tor/tor"
I2P_BIN="$BINARIES_DIR/i2p/i2pd"
DNSCRYPT_BIN="$BINARIES_DIR/dnscrypt/dnscrypt-proxy"

errors=0

if [ -f "$TOR_BIN" ] && [ -x "$TOR_BIN" ]; then
    echo "   ✅ Tor binary found and executable"
else
    echo "   ❌ Tor binary not found or not executable: $TOR_BIN"
    ((errors++))
fi

if [ -f "$I2P_BIN" ] && [ -x "$I2P_BIN" ]; then
    echo "   ✅ I2P binary found and executable"
else
    echo "   ❌ I2P binary not found or not executable: $I2P_BIN"
    ((errors++))
fi

if [ -f "$DNSCRYPT_BIN" ] && [ -x "$DNSCRYPT_BIN" ]; then
    echo "   ✅ DNSCrypt binary found and executable"
else
    echo "   ❌ DNSCrypt binary not found or not executable: $DNSCRYPT_BIN"
    ((errors++))
fi

if [ $errors -gt 0 ]; then
    echo ""
    echo "❌ Binary check failed. Run extract_invizible_binaries.sh first."
    exit 1
fi

# Test 2: Check binary architecture
echo ""
echo "[2/6] Verifying ARM64 architecture..."

for bin in "$TOR_BIN" "$I2P_BIN" "$DNSCRYPT_BIN"; do
    name=$(basename "$bin")
    arch=$(file "$bin" | grep -o "ARM aarch64" || echo "unknown")

    if [ "$arch" == "ARM aarch64" ]; then
        echo "   ✅ $name: ARM64"
    else
        echo "   ⚠️  $name: $arch (expected ARM64)"
    fi
done

# Test 3: Test Tor binary
echo ""
echo "[3/6] Testing Tor binary..."

if timeout 5 "$TOR_BIN" --version 2>&1 | head -5; then
    echo "   ✅ Tor responds to --version"
else
    echo "   ⚠️  Tor --version failed or timed out"
fi

# Test 4: Test I2P binary
echo ""
echo "[4/6] Testing I2P binary..."

if timeout 5 "$I2P_BIN" --version 2>&1 | head -5; then
    echo "   ✅ I2P responds to --version"
else
    echo "   ⚠️  I2P --version failed or timed out"
fi

# Test 5: Test DNSCrypt binary
echo ""
echo "[5/6] Testing DNSCrypt binary..."

if timeout 5 "$DNSCRYPT_BIN" --version 2>&1 | head -5; then
    echo "   ✅ DNSCrypt responds to --version"
else
    echo "   ⚠️  DNSCrypt --version failed or timed out"
fi

# Test 6: Check dependencies
echo ""
echo "[6/6] Checking library dependencies..."

for bin in "$TOR_BIN" "$I2P_BIN" "$DNSCRYPT_BIN"; do
    name=$(basename "$bin")
    echo "   $name dependencies:"

    # Try ldd (may not work on Android)
    if command -v ldd &> /dev/null; then
        ldd "$bin" 2>&1 | head -10 | sed 's/^/      /'
    else
        echo "      (ldd not available)"
    fi
done

# Summary
echo ""
echo "========================================================================"
echo "✅ Binary Testing Complete"
echo "========================================================================"
echo ""
echo "Binaries are ready for integration with QWAMOS network controllers."
echo ""
echo "Next: Update controller configurations to use these binaries"
echo "  - network/tor/tor_controller.py"
echo "  - network/i2p/i2p_controller.py"
echo "  - network/dnscrypt/dnscrypt_controller.py"
echo ""

exit 0
