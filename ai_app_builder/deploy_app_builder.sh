#!/bin/bash

###############################################################################
# QWAMOS Phase 9: AI App Builder - Deployment Script
#
# Deploys the AI App Builder system to QWAMOS
#
# Usage: ./deploy_app_builder.sh
#
# Prerequisites:
# - QWAMOS Phases 1-8 installed
# - Phase 6 (AI Assistants) operational
# - Python 3.8+
# - React Native 0.70+
# - Root access
###############################################################################

set -e  # Exit on error

echo "════════════════════════════════════════════════════════════════"
echo "  QWAMOS Phase 9: AI App Builder - Deployment"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ This script must be run as root${NC}"
    exit 1
fi

echo "Step 1: Checking prerequisites..."
echo "─────────────────────────────────────────────────────────────────"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"

# Check QWAMOS installation
if [ ! -d "/opt/qwamos" ]; then
    echo -e "${RED}✗ QWAMOS not found at /opt/qwamos${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} QWAMOS installation found"

# Check Phase 6 (AI Assistants)
if [ ! -d "/opt/qwamos/ai_assistants" ]; then
    echo -e "${RED}✗ Phase 6 (AI Assistants) not found${NC}"
    echo "   Please install Phase 6 before deploying Phase 9"
    exit 1
fi
echo -e "${GREEN}✓${NC} Phase 6 (AI Assistants) found"

echo ""
echo "Step 2: Creating directory structure..."
echo "─────────────────────────────────────────────────────────────────"

# Create main directories
mkdir -p /opt/qwamos/ai_app_builder/{pipeline,auditor,qa,engine,build,deployment,ui,config,logs,generated_apps,build_snapshots,app_vms}

# Create subdirectories
mkdir -p /opt/qwamos/ai_app_builder/pipeline/{coordinator,crosscheck}
mkdir -p /opt/qwamos/ai_app_builder/auditor/security
mkdir -p /opt/qwamos/ai_app_builder/ui/{screens,services,components}

echo -e "${GREEN}✓${NC} Directory structure created"

echo ""
echo "Step 3: Installing Python components..."
echo "─────────────────────────────────────────────────────────────────"

# Copy Python files
cp pipeline/coordinator/*.py /opt/qwamos/ai_app_builder/pipeline/coordinator/
cp pipeline/crosscheck/*.py /opt/qwamos/ai_app_builder/pipeline/crosscheck/
cp auditor/security/*.py /opt/qwamos/ai_app_builder/auditor/security/
cp qa/*.py /opt/qwamos/ai_app_builder/qa/
cp engine/*.py /opt/qwamos/ai_app_builder/engine/
cp build/*.py /opt/qwamos/ai_app_builder/build/
cp deployment/*.py /opt/qwamos/ai_app_builder/deployment/

echo -e "${GREEN}✓${NC} Python components installed"

echo ""
echo "Step 4: Installing UI components..."
echo "─────────────────────────────────────────────────────────────────"

# Copy React Native files
cp ui/screens/*.tsx /opt/qwamos/ai_app_builder/ui/screens/
cp ui/services/*.ts /opt/qwamos/ai_app_builder/ui/services/

echo -e "${GREEN}✓${NC} UI components installed"

echo ""
echo "Step 5: Installing configuration..."
echo "─────────────────────────────────────────────────────────────────"

# Copy configuration
cp config/*.json /opt/qwamos/ai_app_builder/config/

echo -e "${GREEN}✓${NC} Configuration installed"

echo ""
echo "Step 6: Setting up permissions..."
echo "─────────────────────────────────────────────────────────────────"

# Set ownership
chown -R root:root /opt/qwamos/ai_app_builder

# Set permissions
chmod -R 755 /opt/qwamos/ai_app_builder
chmod -R 777 /opt/qwamos/ai_app_builder/logs
chmod -R 777 /opt/qwamos/ai_app_builder/generated_apps
chmod -R 777 /opt/qwamos/ai_app_builder/build_snapshots
chmod -R 777 /opt/qwamos/ai_app_builder/app_vms

echo -e "${GREEN}✓${NC} Permissions configured"

echo ""
echo "Step 7: Creating QWAMOS keystore..."
echo "─────────────────────────────────────────────────────────────────"

# Create keystore directory
mkdir -p /opt/qwamos/keys

# Generate keystore if it doesn't exist
if [ ! -f "/opt/qwamos/keys/qwamos_release.keystore" ]; then
    keytool -genkeypair \
        -alias qwamos_release \
        -keyalg RSA \
        -keysize 4096 \
        -validity 10000 \
        -keystore /opt/qwamos/keys/qwamos_release.keystore \
        -storepass qwamos123 \
        -keypass qwamos123 \
        -dname "CN=QWAMOS, OU=Security, O=QWAMOS Project, L=Unknown, ST=Unknown, C=US" \
        2>&1 | grep -v "Warning"

    echo -e "${GREEN}✓${NC} QWAMOS keystore created"
else
    echo -e "${YELLOW}✓${NC} QWAMOS keystore already exists"
fi

echo ""
echo "Step 8: Validating installation..."
echo "─────────────────────────────────────────────────────────────────"

# Run validation script
if [ -f "validate_phase9_deployment.sh" ]; then
    bash validate_phase9_deployment.sh
else
    echo -e "${YELLOW}⚠${NC} Validation script not found, skipping validation"
fi

echo ""
echo "Step 9: Creating systemd service..."
echo "─────────────────────────────────────────────────────────────────"

# Create systemd service for app builder
cat > /etc/systemd/system/qwamos-app-builder.service <<EOF
[Unit]
Description=QWAMOS AI App Builder Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/qwamos/ai_app_builder
ExecStart=/usr/bin/python3 -m pipeline.coordinator.multi_ai_pipeline
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo -e "${GREEN}✓${NC} Systemd service created"

echo ""
echo "Step 10: Deployment summary..."
echo "─────────────────────────────────────────────────────────────────"

# Count installed files
PYTHON_FILES=$(find /opt/qwamos/ai_app_builder -name "*.py" | wc -l)
UI_FILES=$(find /opt/qwamos/ai_app_builder/ui -name "*.tsx" -o -name "*.ts" | wc -l)
CONFIG_FILES=$(find /opt/qwamos/ai_app_builder/config -name "*.json" | wc -l)

echo "Installed components:"
echo "  • Python modules:      ${PYTHON_FILES}"
echo "  • UI components:       ${UI_FILES}"
echo "  • Configuration files: ${CONFIG_FILES}"
echo ""
echo "Installation path:   /opt/qwamos/ai_app_builder"
echo "Configuration:       /opt/qwamos/ai_app_builder/config/"
echo "Logs:                /opt/qwamos/ai_app_builder/logs/"
echo "Generated apps:      /opt/qwamos/ai_app_builder/generated_apps/"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}✅ Phase 9 deployment complete!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Start the service:  systemctl start qwamos-app-builder"
echo "  2. Enable at boot:     systemctl enable qwamos-app-builder"
echo "  3. Check status:       systemctl status qwamos-app-builder"
echo "  4. View logs:          tail -f /opt/qwamos/ai_app_builder/logs/app_builder.log"
echo ""
echo "Usage:"
echo "  • Open QWAMOS app"
echo "  • Navigate to 'AI App Builder'"
echo "  • Describe your app in natural language"
echo "  • Review and approve the generated code"
echo "  • Deploy to dedicated VM"
echo ""
echo "Documentation: /opt/qwamos/ai_app_builder/README.md"
echo ""
