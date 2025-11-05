#!/bin/bash
#
# QWAMOS Phase 7: Deployment Validation Script
#
# This script validates the Phase 7 deployment by checking:
# - All files are present
# - File integrity (line counts)
# - Directory structure
# - Python syntax
# - Systemd service files
# - Documentation completeness
#
# Usage:
#   ./validate_phase7_deployment.sh [--pre-deploy|--post-deploy]
#
# --pre-deploy:  Validate package before transfer to device
# --post-deploy: Validate installation on device after deployment
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASS=0
FAIL=0
WARN=0

# Mode
MODE="${1:---pre-deploy}"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  QWAMOS Phase 7: Deployment Validation${NC}"
echo -e "${BLUE}  Mode: $MODE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Helper functions
check_file() {
    local file="$1"
    local expected_lines="$2"
    local tolerance="${3:-50}"  # Allow ±50 lines by default

    if [[ ! -f "$file" ]]; then
        echo -e "${RED}✗${NC} File missing: $file"
        ((FAIL++))
        return 1
    fi

    if [[ -n "$expected_lines" ]]; then
        local actual_lines=$(wc -l < "$file")
        local diff=$((actual_lines - expected_lines))
        local abs_diff=${diff#-}

        if [[ $abs_diff -gt $tolerance ]]; then
            echo -e "${YELLOW}⚠${NC} File size mismatch: $file (expected ~$expected_lines lines, got $actual_lines)"
            ((WARN++))
        else
            echo -e "${GREEN}✓${NC} $file ($actual_lines lines)"
            ((PASS++))
        fi
    else
        echo -e "${GREEN}✓${NC} $file"
        ((PASS++))
    fi
}

check_directory() {
    local dir="$1"

    if [[ ! -d "$dir" ]]; then
        echo -e "${RED}✗${NC} Directory missing: $dir"
        ((FAIL++))
        return 1
    fi

    echo -e "${GREEN}✓${NC} $dir"
    ((PASS++))
}

check_python_syntax() {
    local file="$1"

    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${RED}✗${NC} Python syntax error: $file"
        ((FAIL++))
        return 1
    fi

    echo -e "${GREEN}✓${NC} Python syntax valid: $file"
    ((PASS++))
}

# Pre-deployment validation (on development machine)
if [[ "$MODE" == "--pre-deploy" ]]; then
    echo "Validating Phase 7 package before deployment..."
    echo ""

    # Check if package exists
    if [[ -f "QWAMOS_Phase7_Deployment_20251105.tar.gz" ]]; then
        echo -e "${GREEN}✓${NC} Deployment package found"
        ((PASS++))

        # Check package size
        SIZE=$(stat -c%s "QWAMOS_Phase7_Deployment_20251105.tar.gz" 2>/dev/null || stat -f%z "QWAMOS_Phase7_Deployment_20251105.tar.gz" 2>/dev/null)
        SIZE_KB=$((SIZE / 1024))
        echo -e "${GREEN}✓${NC} Package size: ${SIZE_KB}KB"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} Deployment package not found"
        ((FAIL++))
    fi

    echo ""
    echo "Validating source files..."
    echo ""

    # Python ML Detectors
    echo -e "${BLUE}ML Detectors:${NC}"
    check_file "security/ml/network_anomaly_detector.py" 600
    check_file "security/ml/file_system_monitor.py" 550
    check_file "security/ml/system_call_analyzer.py" 500

    echo ""
    echo -e "${BLUE}AI Response System:${NC}"
    check_file "security/ai_response/ai_response_coordinator.py" 550
    check_file "security/actions/action_executor.py" 400

    echo ""
    echo -e "${BLUE}Systemd Services:${NC}"
    check_file "security/systemd/qwamos-ml-network-anomaly.service" 52 10
    check_file "security/systemd/qwamos-ml-file-system.service" 50 10
    check_file "security/systemd/qwamos-ml-system-call.service" 52 10
    check_file "security/systemd/qwamos-ai-response.service" 53 10

    echo ""
    echo -e "${BLUE}Deployment Scripts:${NC}"
    check_file "security/scripts/deploy_threat_detection.sh" 395

    echo ""
    echo -e "${BLUE}React Native UI:${NC}"
    check_file "ui/screens/ThreatDetection/ThreatDashboard.tsx" 600
    check_file "ui/services/ThreatDetectionService.ts" 350

    echo ""
    echo -e "${BLUE}Java Native Bridge:${NC}"
    check_file "ui/native/QWAMOSThreatBridge.java" 280
    check_file "ui/native/QWAMOSThreatPackage.java" 40 20

    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    check_file "docs/PHASE7_DEPLOYMENT_GUIDE.md" 1200
    check_file "docs/PHASE7_ML_TRAINING_GUIDE.md" 1300
    check_file "docs/PHASE7_API_DOCUMENTATION.md" 700
    check_file "docs/PHASE7_COMPLETION_SUMMARY.md" 900
    check_file "docs/PHASE7_ML_THREAT_DETECTION.md" 900
    check_file "security/README.md" 500

    echo ""
    echo -e "${BLUE}Python Syntax Validation:${NC}"
    for py_file in security/ml/*.py security/ai_response/*.py security/actions/*.py; do
        if [[ -f "$py_file" ]]; then
            check_python_syntax "$py_file"
        fi
    done

fi

# Post-deployment validation (on device)
if [[ "$MODE" == "--post-deploy" ]]; then
    echo "Validating Phase 7 installation on device..."
    echo ""

    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        echo -e "${YELLOW}⚠${NC} Not running as root. Some checks may fail."
        echo -e "   Run with: sudo $0 $MODE"
        echo ""
    fi

    # Check directory structure
    echo -e "${BLUE}Directory Structure:${NC}"
    check_directory "/opt/qwamos/security/ml"
    check_directory "/opt/qwamos/security/ai_response"
    check_directory "/opt/qwamos/security/actions"
    check_directory "/opt/qwamos/security/config"
    check_directory "/opt/qwamos/security/quarantine"
    check_directory "/var/log/qwamos"

    echo ""
    echo -e "${BLUE}Installed Files:${NC}"
    check_file "/opt/qwamos/security/ml/network_anomaly_detector.py" 600
    check_file "/opt/qwamos/security/ml/file_system_monitor.py" 550
    check_file "/opt/qwamos/security/ml/system_call_analyzer.py" 500
    check_file "/opt/qwamos/security/ai_response/ai_response_coordinator.py" 550
    check_file "/opt/qwamos/security/actions/action_executor.py" 400

    echo ""
    echo -e "${BLUE}Systemd Services:${NC}"
    check_file "/etc/systemd/system/qwamos-ml-network-anomaly.service" 52 10
    check_file "/etc/systemd/system/qwamos-ml-file-system.service" 50 10
    check_file "/etc/systemd/system/qwamos-ml-system-call.service" 52 10
    check_file "/etc/systemd/system/qwamos-ai-response.service" 53 10

    echo ""
    echo -e "${BLUE}Configuration Files:${NC}"
    check_file "/opt/qwamos/security/config/ai_response_config.json"
    check_file "/opt/qwamos/security/config/action_executor_config.json"
    check_file "/opt/qwamos/security/config/permissions.json"

    echo ""
    echo -e "${BLUE}Service Status:${NC}"

    # Check if systemd services are enabled and running
    for service in qwamos-ml-network-anomaly qwamos-ml-file-system qwamos-ml-system-call qwamos-ai-response; do
        if systemctl is-active --quiet ${service}.service 2>/dev/null; then
            echo -e "${GREEN}✓${NC} ${service}.service is running"
            ((PASS++))
        else
            echo -e "${RED}✗${NC} ${service}.service is not running"
            ((FAIL++))
        fi

        if systemctl is-enabled --quiet ${service}.service 2>/dev/null; then
            echo -e "${GREEN}✓${NC} ${service}.service is enabled"
            ((PASS++))
        else
            echo -e "${YELLOW}⚠${NC} ${service}.service is not enabled on boot"
            ((WARN++))
        fi
    done

    echo ""
    echo -e "${BLUE}Python Dependencies:${NC}"

    # Check Python dependencies
    for package in tensorflow scapy watchdog numpy; do
        if pip3 list 2>/dev/null | grep -i "$package" > /dev/null; then
            echo -e "${GREEN}✓${NC} $package installed"
            ((PASS++))
        else
            echo -e "${RED}✗${NC} $package not installed"
            ((FAIL++))
        fi
    done

    echo ""
    echo -e "${BLUE}Permissions:${NC}"

    # Check qwamos user exists
    if id qwamos &>/dev/null; then
        echo -e "${GREEN}✓${NC} qwamos user exists"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} qwamos user does not exist"
        ((FAIL++))
    fi

    # Check file ownership
    if [[ -d "/opt/qwamos/security" ]]; then
        OWNER=$(stat -c '%U' /opt/qwamos/security/ml 2>/dev/null || stat -f '%Su' /opt/qwamos/security/ml 2>/dev/null)
        if [[ "$OWNER" == "qwamos" ]]; then
            echo -e "${GREEN}✓${NC} Correct ownership (qwamos)"
            ((PASS++))
        else
            echo -e "${YELLOW}⚠${NC} Incorrect ownership: $OWNER (expected qwamos)"
            ((WARN++))
        fi
    fi

    echo ""
    echo -e "${BLUE}Recent Logs (last 5 minutes):${NC}"

    # Check for errors in logs
    ERROR_COUNT=$(journalctl -u 'qwamos-ml-*' -u 'qwamos-ai-response' --since "5 minutes ago" --no-pager 2>/dev/null | grep -i "error" | wc -l)

    if [[ $ERROR_COUNT -eq 0 ]]; then
        echo -e "${GREEN}✓${NC} No errors in recent logs"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠${NC} $ERROR_COUNT errors found in recent logs"
        ((WARN++))
    fi

fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Validation Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Passed:${NC}  $PASS"
echo -e "${YELLOW}Warnings:${NC} $WARN"
echo -e "${RED}Failed:${NC}  $FAIL"
echo ""

if [[ $FAIL -eq 0 ]]; then
    echo -e "${GREEN}✓ Validation PASSED${NC}"
    if [[ $WARN -gt 0 ]]; then
        echo -e "${YELLOW}  $WARN warnings (review recommended)${NC}"
    fi
    exit 0
else
    echo -e "${RED}✗ Validation FAILED${NC}"
    echo -e "  $FAIL critical issues found"
    exit 1
fi
