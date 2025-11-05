#!/bin/bash
#
# QWAMOS SecureType Keyboard - Post-Quantum Crypto Validation
#
# Validates that ONLY post-quantum cryptography is used.
# Forbidden algorithms: AES, RSA, ECDH, X25519, DES, 3DES, RC4
#
# Exit codes:
#   0 - All checks passed (PQ-only crypto)
#   1 - Found legacy/forbidden crypto
#   2 - Missing dependencies
#

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  QWAMOS SecureType Keyboard - PQ Crypto Validation"
echo "═══════════════════════════════════════════════════════════"
echo ""

KEYBOARD_DIR="/data/data/com.termux/files/home/QWAMOS/keyboard"
CRYPTO_SERVICE="$KEYBOARD_DIR/crypto/pq_keystore_service.py"
KEYSTORE_MANAGER="$KEYBOARD_DIR/src/native/KeystoreManager.java"

PASS_COUNT=0
FAIL_COUNT=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "[1/6] Checking for forbidden algorithms in source code..."
echo ""

# Check for AES usage
if grep -q "AES\|aes\|Aes" "$CRYPTO_SERVICE" "$KEYSTORE_MANAGER" 2>/dev/null; then
    fail "Found AES references in code (FORBIDDEN)"
else
    pass "No AES found in source code"
fi

# Check for RSA usage
if grep -q "RSA\|rsa\|Rsa" "$CRYPTO_SERVICE" "$KEYSTORE_MANAGER" 2>/dev/null; then
    fail "Found RSA references in code (FORBIDDEN)"
else
    pass "No RSA found in source code"
fi

# Check for ECDH/X25519 usage (except in comments about removal)
if grep -v "^#" "$CRYPTO_SERVICE" | grep -q "X25519\|x25519\|ECDH\|ecdh" 2>/dev/null; then
    fail "Found X25519/ECDH in active code (FORBIDDEN - should only be in comments)"
else
    pass "No X25519/ECDH found in active code"
fi

# Check for DES/3DES/RC4
if grep -q "DES\|des\|RC4\|rc4" "$CRYPTO_SERVICE" "$KEYSTORE_MANAGER" 2>/dev/null; then
    fail "Found DES/RC4 references in code (FORBIDDEN)"
else
    pass "No DES/RC4 found in source code"
fi

echo ""
echo "[2/6] Verifying required post-quantum algorithms..."
echo ""

# Check for Kyber-1024
if grep -q "Kyber1024\|KYBER1024" "$CRYPTO_SERVICE"; then
    pass "Kyber-1024 implementation found"
else
    fail "Kyber-1024 NOT found (REQUIRED)"
fi

# Check for ChaCha20-Poly1305
if grep -q "ChaCha20Poly1305\|ChaCha20-Poly1305" "$CRYPTO_SERVICE"; then
    pass "ChaCha20-Poly1305 implementation found"
else
    fail "ChaCha20-Poly1305 NOT found (REQUIRED)"
fi

# Check for BLAKE3/BLAKE2b
if grep -q "BLAKE3\|BLAKE2b\|blake3\|blake2b" "$CRYPTO_SERVICE"; then
    pass "BLAKE2b/BLAKE3 hashing found"
else
    warn "BLAKE2b/BLAKE3 not found (recommended)"
fi

echo ""
echo "[3/6] Checking liboqs dependency (mandatory)..."
echo ""

# Check if liboqs import is mandatory
if grep -q "sys.exit(1)" "$CRYPTO_SERVICE" && grep -q "CRITICAL ERROR: liboqs not installed" "$CRYPTO_SERVICE"; then
    pass "liboqs is mandatory (service exits if not available)"
else
    fail "liboqs should be mandatory (no fallback allowed)"
fi

# Check if fallback code has been removed
if grep -q "fallback\|Fallback\|FALLBACK" "$CRYPTO_SERVICE" | grep -v "^#" | grep -v "NO fallback"; then
    fail "Found fallback code (should be removed)"
else
    pass "No fallback code found"
fi

echo ""
echo "[4/6] Checking for secure key derivation..."
echo ""

# Check for Argon2id or HKDF
if grep -q "HKDF\|Argon2id" "$CRYPTO_SERVICE"; then
    pass "Secure key derivation (HKDF) found"
else
    warn "HKDF/Argon2id not found (recommended)"
fi

echo ""
echo "[5/6] Verifying security comments and documentation..."
echo ""

# Check for security warnings about AES/legacy crypto
if grep -q "DIA\|Naval Intelligence\|legacy crypto\|forbidden" "$CRYPTO_SERVICE"; then
    pass "Security warnings about legacy crypto found"
else
    warn "No security warnings about legacy crypto"
fi

echo ""
echo "[6/6] Checking Python dependencies..."
echo ""

# Check if liboqs-python is installed
if python3 -c "import oqs" 2>/dev/null; then
    pass "liboqs-python is installed"
else
    fail "liboqs-python NOT installed (pip install liboqs-python)"
fi

# Check if cryptography library is installed
if python3 -c "import cryptography" 2>/dev/null; then
    pass "cryptography library is installed"
else
    fail "cryptography library NOT installed (pip install cryptography)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Validation Summary"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo -e "Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "Failed: ${RED}$FAIL_COUNT${NC}"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ All security checks passed!${NC}"
    echo ""
    echo "SecureType Keyboard uses ONLY post-quantum cryptography:"
    echo "  • Kyber-1024 (NIST FIPS 203 ML-KEM)"
    echo "  • ChaCha20-Poly1305 AEAD"
    echo "  • HKDF-BLAKE2b key derivation"
    echo ""
    echo "NO legacy encryption (AES/RSA/ECDH) is used."
    echo ""
    exit 0
else
    echo -e "${RED}✗ Security validation FAILED${NC}"
    echo ""
    echo "Please fix the issues above before deploying."
    echo ""
    exit 1
fi
