#!/bin/bash
# Deploy QWAMOS Security Layer to Motorola Edge 2025
# Supports both USB (adb) and Termux local deployment

set -e

DEVICE_IP="${1:-local}"
TERMUX_PREFIX="/data/data/com.termux/files"
QWAMOS_HOME="$HOME/QWAMOS/security"

echo "QWAMOS Security Layer - Device Deployment"
echo "=========================================="
echo ""

# Detect deployment mode
if [ "$DEVICE_IP" = "local" ]; then
    echo "Deployment mode: LOCAL (running in Termux)"
    DEPLOY_CMD=""
else
    echo "Deployment mode: REMOTE (adb to $DEVICE_IP)"
    DEPLOY_CMD="adb shell"
fi

# Step 1: Create directories
echo "[1/8] Creating directory structure..."
$DEPLOY_CMD mkdir -p /etc/qwamos/{keys,policy}
$DEPLOY_CMD mkdir -p /var/run/qwamos/control-bus
$DEPLOY_CMD mkdir -p /data/qwamos/{firewall,radio,policy,session-keys,attestation}
$DEPLOY_CMD mkdir -p /usr/share/qwamos
echo "✅ Directories created"

# Step 2: Copy files
echo ""
echo "[2/8] Copying files..."

if [ "$DEVICE_IP" = "local" ]; then
    # Local deployment
    cp -r dom0/* /data/qwamos/dom0/
    cp -r gateway_vm/* /data/qwamos/gateway_vm/
    cp -r ui_vm/* /data/qwamos/ui_vm/ 2>/dev/null || true
    cp -r attestation/* /data/qwamos/attestation/ 2>/dev/null || true
    cp -r crypto/* /data/qwamos/crypto/ 2>/dev/null || true
    cp -r panic/* /data/qwamos/panic/ 2>/dev/null || true
else
    # Remote deployment via adb
    adb push dom0/ $TERMUX_PREFIX/home/qwamos/security/dom0/
    adb push gateway_vm/ $TERMUX_PREFIX/home/qwamos/security/gateway_vm/
    adb push ui_vm/ $TERMUX_PREFIX/home/qwamos/security/ui_vm/
    adb push attestation/ $TERMUX_PREFIX/home/qwamos/security/attestation/
    adb push crypto/ $TERMUX_PREFIX/home/qwamos/security/crypto/
    adb push panic/ $TERMUX_PREFIX/home/qwamos/security/panic/
fi

echo "✅ Files copied"

# Step 3: Install dependencies
echo ""
echo "[3/8] Installing dependencies..."
$DEPLOY_CMD pkg install -y python tor iptables signify 2>/dev/null || \
$DEPLOY_CMD apt-get install -y python3 python3-pip tor iptables signify-openbsd
$DEPLOY_CMD pip3 install watchdog pycryptodome
echo "✅ Dependencies installed"

# Step 4: Generate signing keys
echo ""
echo "[4/8] Generating Ed25519 signing keys..."
$DEPLOY_CMD bash -c "
if [ ! -f /etc/qwamos/keys/dom0.sec ]; then
    cd /etc/qwamos/keys && signify -G -p dom0.pub -s dom0.sec
    echo '✅ Keys generated'
else
    echo 'ℹ️  Keys already exist'
fi
"

# Step 5: Install policy schema
echo ""
echo "[5/8] Installing policy schema..."
$DEPLOY_CMD cp $QWAMOS_HOME/dom0/policy/policy.schema.json /usr/share/qwamos/
echo "✅ Schema installed"

# Step 6: Install initial policy
echo ""
echo "[6/8] Installing default policy..."
$DEPLOY_CMD bash -c "
if [ ! -f /etc/qwamos/policy.conf ]; then
    cp $QWAMOS_HOME/dom0/policy/policy.conf.example /etc/qwamos/policy.conf
    echo '✅ Default policy installed'
else
    echo 'ℹ️  Policy already exists (keeping current)'
fi
"

# Step 7: Set permissions
echo ""
echo "[7/8] Setting permissions..."
$DEPLOY_CMD chmod +x /data/qwamos/dom0/qwamosd/qwamosd.py
$DEPLOY_CMD chmod +x /data/qwamos/gateway_vm/firewall/*.sh
$DEPLOY_CMD chmod +x /data/qwamos/gateway_vm/radio/*.sh
$DEPLOY_CMD chmod +x /data/qwamos/gateway_vm/policy/*.py
$DEPLOY_CMD chmod 600 /etc/qwamos/keys/dom0.sec
$DEPLOY_CMD chmod 644 /etc/qwamos/keys/dom0.pub
echo "✅ Permissions set"

# Step 8: Create systemd services (if available)
echo ""
echo "[8/8] Setting up services..."
if $DEPLOY_CMD which systemctl >/dev/null 2>&1; then
    echo "systemd detected - creating services..."

    # qwamosd service
    $DEPLOY_CMD bash -c "cat > /etc/systemd/system/qwamosd.service <<'EOF'
[Unit]
Description=QWAMOS Policy Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /data/qwamos/dom0/qwamosd/qwamosd.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF"

    # gateway-policyd service
    $DEPLOY_CMD bash -c "cat > /etc/systemd/system/gateway-policyd.service <<'EOF'
[Unit]
Description=QWAMOS Gateway Policy Daemon
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /data/qwamos/gateway_vm/policy/gateway-policyd.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF"

    # radio-monitor service
    $DEPLOY_CMD bash -c "cat > /etc/systemd/system/radio-monitor.service <<'EOF'
[Unit]
Description=QWAMOS Radio Idle Monitor
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash /data/qwamos/gateway_vm/radio/radio-ctrl.sh monitor
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF"

    $DEPLOY_CMD systemctl daemon-reload
    $DEPLOY_CMD systemctl enable qwamosd gateway-policyd radio-monitor

    echo "✅ Systemd services created"
    echo ""
    echo "To start services:"
    echo "  systemctl start qwamosd"
    echo "  systemctl start gateway-policyd"
    echo "  systemctl start radio-monitor"
else
    echo "⚠️  systemd not available - manual service startup required"
    echo ""
    echo "To start services manually:"
    echo "  python3 /data/qwamos/dom0/qwamosd/qwamosd.py &"
    echo "  python3 /data/qwamos/gateway_vm/policy/gateway-policyd.py &"
    echo "  bash /data/qwamos/gateway_vm/radio/radio-ctrl.sh monitor &"
fi

echo ""
echo "=========================================="
echo "✅ QWAMOS Security Layer deployed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Run first-boot wizard:"
echo "   python3 /data/qwamos/dom0/ui/first-boot-wizard.py"
echo ""
echo "2. View current policy:"
echo "   cat /etc/qwamos/policy.conf"
echo ""
echo "3. Edit policy:"
echo "   nano /etc/qwamos/policy.conf"
echo "   (qwamosd will auto-apply changes)"
echo ""
echo "4. Check services:"
echo "   systemctl status qwamosd"
echo "   systemctl status gateway-policyd"
echo ""
echo "5. Test radio control:"
echo "   bash /data/qwamos/gateway_vm/radio/radio-ctrl.sh status"
echo ""
echo "6. Apply firewall (basic mode):"
echo "   bash /data/qwamos/gateway_vm/firewall/rules-basic.sh"
echo ""
echo "7. Apply firewall (strict mode):"
echo "   bash /data/qwamos/gateway_vm/firewall/rules-strict.sh"
echo ""
echo "Documentation:"
echo "  - Architecture: ~/QWAMOS/security/README_QWAMOS_SecurityLayer.md"
echo "  - Quick start:  ~/QWAMOS/security/QUICK_START.md"
echo ""
