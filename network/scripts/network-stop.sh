#!/bin/bash
#
# QWAMOS Network Manager Stop Script
#
# Gracefully shuts down network isolation services:
# - Stops all network services
# - Cleans up firewall rules
# - Saves current state
# - Optional: Restore direct network access
#

set -e

QWAMOS_DIR="/opt/qwamos/network"
LOG_DIR="/var/log/qwamos"
STATE_DIR="/var/lib/qwamos"

echo "QWAMOS Network Shutdown"
echo "======================="

# 1. Save current state
echo "[1/4] Saving network state..."
if [ -f "$QWAMOS_DIR/current_mode.json" ]; then
    cp "$QWAMOS_DIR/current_mode.json" "$STATE_DIR/last_mode.json"
    echo "   ✅ State saved"
fi

# 2. Stop VPN if active
echo "[2/4] Stopping VPN connections..."
if command -v wg-quick &> /dev/null; then
    wg-quick down wg0 2>/dev/null || true
    echo "   ✅ VPN stopped"
fi

# 3. Clean up firewall rules
echo "[3/4] Cleaning up firewall rules..."

# Remove QWAMOS firewall tables
nft delete table inet qwamos_filter 2>/dev/null || true
nft delete table ip6 qwamos_filter6 2>/dev/null || true
nft delete table inet qwamos_killswitch 2>/dev/null || true

# Restore basic connectivity (allow all)
nft add table inet qwamos_temp
nft add chain inet qwamos_temp output '{ type filter hook output priority 0; policy accept; }'
nft add chain inet qwamos_temp input '{ type filter hook input priority 0; policy accept; }'

echo "   ✅ Firewall rules cleaned up"
echo "   ⚠️  Direct network access restored (no anonymization)"

# 4. Log shutdown
echo "[4/4] Logging shutdown..."
echo "$(date): Network isolation services stopped" >> "$LOG_DIR/network-manager.log"

echo ""
echo "✅ Network shutdown complete"
echo "   All anonymization services stopped"
echo "   Direct network access active"
echo ""

exit 0
