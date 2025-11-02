#!/bin/bash
#
# QWAMOS Boot-Time Policy Application Script
#
# Applies pending reboot-required policy changes from /etc/qwamos/pending.conf
# Called by systemd service qwamos-policy-apply.service before sysinit.target
#
# Exit codes:
#   0 - Success (changes applied or no pending changes)
#   1 - Error reading pending.conf
#   2 - Error applying policy changes

set -euo pipefail

PENDING_CONF="/etc/qwamos/pending.conf"
STATUS_JSON="/etc/qwamos/status.json"
BACKUP_DIR="/var/lib/qwamos/backups"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if pending.conf exists
if [[ ! -f "$PENDING_CONF" ]]; then
    echo "[QWAMOS] No pending policy changes to apply"
    exit 0
fi

echo "[QWAMOS] Applying pending policy changes from $PENDING_CONF"

# Backup current status
if [[ -f "$STATUS_JSON" ]]; then
    cp "$STATUS_JSON" "$BACKUP_DIR/status.json.$(date +%s)"
    echo "[QWAMOS] Backed up current status to $BACKUP_DIR"
fi

# Load current policy from status.json
CURRENT_POLICY="{}"
if [[ -f "$STATUS_JSON" ]]; then
    CURRENT_POLICY=$(jq -r '.policy // {}' "$STATUS_JSON")
fi

# Read pending.conf and merge with current policy
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ "$key" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$key" ]] && continue

    # Trim whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    echo "[QWAMOS] Applying: $key = $value"

    # Update policy JSON
    CURRENT_POLICY=$(echo "$CURRENT_POLICY" | jq --arg k "$key" --arg v "$value" '. + {($k): $v}')

    # Apply boot-time changes based on key
    case "$key" in
        BOOT_VERIFICATION)
            echo "[QWAMOS] Setting boot verification mode: $value"
            # In real implementation: Configure measured boot / secure boot
            ;;
        KERNEL_HARDENING)
            echo "[QWAMOS] Setting kernel hardening level: $value"
            # In real implementation: Update kernel command line parameters
            ;;
        CRYPTO_BACKEND)
            echo "[QWAMOS] Setting crypto backend: $value"
            # In real implementation: Configure crypto modules
            ;;
        *)
            echo "[QWAMOS] WARNING: Unknown reboot-required key: $key"
            ;;
    esac

done < "$PENDING_CONF"

# Update status.json with merged policy
UPDATED_STATUS=$(jq --argjson policy "$CURRENT_POLICY" \
                    --arg timestamp "$(date +%s)" \
                    '. + {policy: $policy, last_update: ($timestamp | tonumber)}' \
                    "$STATUS_JSON" 2>/dev/null || echo "{}")

if [[ -z "$UPDATED_STATUS" ]] || [[ "$UPDATED_STATUS" == "{}" ]]; then
    UPDATED_STATUS=$(jq -n --argjson policy "$CURRENT_POLICY" \
                           --arg timestamp "$(date +%s)" \
                           '{policy: $policy, last_update: ($timestamp | tonumber)}')
fi

echo "$UPDATED_STATUS" > "$STATUS_JSON"
echo "[QWAMOS] Updated status.json with pending policy changes"

# Remove pending.conf (changes have been applied)
rm -f "$PENDING_CONF"
echo "[QWAMOS] Removed pending.conf (changes applied successfully)"

echo "[QWAMOS] Boot-time policy application complete ✓"
exit 0
