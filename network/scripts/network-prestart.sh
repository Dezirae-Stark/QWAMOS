#!/bin/bash
#
# QWAMOS Network Manager Pre-Start Script
#
# Prepares the system for network isolation services:
# - Creates necessary directories
# - Sets up permissions
# - Validates configurations
# - Initializes firewall rules
#

set -e

QWAMOS_DIR="/opt/qwamos/network"
LOG_DIR="/var/log/qwamos"
STATE_DIR="/var/lib/qwamos"

echo "QWAMOS Network Pre-Start Checks"
echo "==============================="

# 1. Create required directories
echo "[1/6] Creating required directories..."
mkdir -p "$LOG_DIR"
mkdir -p "$STATE_DIR"
mkdir -p "$QWAMOS_DIR/tor/data"
mkdir -p "$QWAMOS_DIR/i2p/data"
mkdir -p "$QWAMOS_DIR/dnscrypt/data"
mkdir -p "$QWAMOS_DIR/vpn/configs"
mkdir -p "$QWAMOS_DIR/vpn/pq_keys"

# 2. Set up permissions
echo "[2/6] Setting up permissions..."
chown -R qwamos:qwamos "$LOG_DIR" || true
chown -R qwamos:qwamos "$STATE_DIR" || true
chown -R tor:tor "$QWAMOS_DIR/tor/data" || true
chown -R i2pd:i2pd "$QWAMOS_DIR/i2p/data" || true
chown -R dnscrypt:dnscrypt "$QWAMOS_DIR/dnscrypt/data" || true

# 3. Validate configurations
echo "[3/6] Validating configurations..."

# Check if network mode config exists
if [ ! -f "$QWAMOS_DIR/current_mode.json" ]; then
    echo "   No active mode, setting default to tor-dnscrypt"
    cp "$QWAMOS_DIR/modes/tor-dnscrypt.json" "$QWAMOS_DIR/current_mode.json"
fi

# Validate Tor config
if [ ! -f "$QWAMOS_DIR/tor/torrc" ]; then
    echo "   ERROR: Tor configuration not found!"
    exit 1
fi

# Validate DNSCrypt config
if [ ! -f "$QWAMOS_DIR/dnscrypt/dnscrypt-proxy.toml" ]; then
    echo "   ERROR: DNSCrypt configuration not found!"
    exit 1
fi

echo "   ✅ Configurations valid"

# 4. Check for required binaries
echo "[4/6] Checking required binaries..."
REQUIRED_BINS=("tor" "dnscrypt-proxy" "nft" "python3")

for bin in "${REQUIRED_BINS[@]}"; do
    if ! command -v "$bin" &> /dev/null; then
        echo "   ERROR: Required binary '$bin' not found!"
        exit 1
    fi
done

echo "   ✅ All required binaries present"

# 5. Initialize firewall
echo "[5/6] Initializing firewall rules..."

# Clear any existing QWAMOS tables
nft delete table inet qwamos_filter 2>/dev/null || true
nft delete table ip6 qwamos_filter6 2>/dev/null || true

# Load base firewall rules based on current mode
MODE=$(python3 -c "import json; print(json.load(open('$QWAMOS_DIR/current_mode.json'))['mode'])")
FIREWALL_RULES="$QWAMOS_DIR/firewall/rules/${MODE}.nft"

if [ -f "$FIREWALL_RULES" ]; then
    nft -f "$FIREWALL_RULES"
    echo "   ✅ Loaded firewall rules for mode: $MODE"
else
    echo "   WARNING: No firewall rules found for mode: $MODE"
    # Load default fallback rules
    nft -f "$QWAMOS_DIR/firewall/rules/tor-dnscrypt.nft" || true
fi

# 6. Network readiness check
echo "[6/6] Checking network readiness..."

# Wait for network to be online
for i in {1..10}; do
    if ping -c 1 -W 2 1.1.1.1 &> /dev/null || \
       ping -c 1 -W 2 8.8.8.8 &> /dev/null; then
        echo "   ✅ Network is online"
        break
    fi

    if [ $i -eq 10 ]; then
        echo "   WARNING: Network appears to be offline"
    fi

    sleep 1
done

echo ""
echo "✅ Pre-start checks complete"
echo "   Mode: $MODE"
echo "   Ready to start network services"
echo ""

exit 0
