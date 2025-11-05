#!/bin/bash

###############################################################################
# QWAMOS Phase 9: AI App Builder - Validation Script
#
# Validates Phase 9 deployment and checks all components
#
# Usage: ./validate_phase9_deployment.sh
###############################################################################

set -e

echo "════════════════════════════════════════════════════════════════"
echo "  QWAMOS Phase 9: Deployment Validation"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VALIDATION_PASSED=true

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2 (file not found: $1)"
        VALIDATION_PASSED=false
        return 1
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "${RED}✗${NC} $2 (directory not found: $1)"
        VALIDATION_PASSED=false
        return 1
    fi
}

echo "Checking directory structure..."
echo "─────────────────────────────────────────────────────────────────"

check_dir "/opt/qwamos/ai_app_builder" "Main directory"
check_dir "/opt/qwamos/ai_app_builder/pipeline" "Pipeline directory"
check_dir "/opt/qwamos/ai_app_builder/auditor" "Auditor directory"
check_dir "/opt/qwamos/ai_app_builder/qa" "QA directory"
check_dir "/opt/qwamos/ai_app_builder/engine" "Engine directory"
check_dir "/opt/qwamos/ai_app_builder/build" "Build directory"
check_dir "/opt/qwamos/ai_app_builder/deployment" "Deployment directory"
check_dir "/opt/qwamos/ai_app_builder/ui" "UI directory"
check_dir "/opt/qwamos/ai_app_builder/config" "Config directory"
check_dir "/opt/qwamos/ai_app_builder/logs" "Logs directory"

echo ""
echo "Checking Python components..."
echo "─────────────────────────────────────────────────────────────────"

check_file "/opt/qwamos/ai_app_builder/pipeline/coordinator/multi_ai_pipeline.py" "Multi-AI Pipeline"
check_file "/opt/qwamos/ai_app_builder/pipeline/crosscheck/code_reviewer.py" "Code Crosscheck Reviewer"
check_file "/opt/qwamos/ai_app_builder/auditor/security/security_auditor.py" "Triple-AI Security Auditor"
check_file "/opt/qwamos/ai_app_builder/qa/quality_assurance.py" "Quality Assurance System"
check_file "/opt/qwamos/ai_app_builder/engine/enhancement_engine.py" "Enhancement Engine"
check_file "/opt/qwamos/ai_app_builder/build/isolated_builder.py" "Isolated Build System"
check_file "/opt/qwamos/ai_app_builder/deployment/deployment_manager.py" "Deployment Manager"

echo ""
echo "Checking UI components..."
echo "─────────────────────────────────────────────────────────────────"

check_file "/opt/qwamos/ai_app_builder/ui/screens/AppBuilderScreen.tsx" "App Builder Screen"
check_file "/opt/qwamos/ai_app_builder/ui/services/AppBuilderService.ts" "App Builder Service"

echo ""
echo "Checking configuration..."
echo "─────────────────────────────────────────────────────────────────"

check_file "/opt/qwamos/ai_app_builder/config/app_builder_config.json" "Configuration file"

# Validate JSON configuration
if command -v python3 &> /dev/null; then
    if python3 -c "import json; json.load(open('/opt/qwamos/ai_app_builder/config/app_builder_config.json'))" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Configuration JSON is valid"
    else
        echo -e "${RED}✗${NC} Configuration JSON is invalid"
        VALIDATION_PASSED=false
    fi
fi

echo ""
echo "Checking QWAMOS integration..."
echo "─────────────────────────────────────────────────────────────────"

check_dir "/opt/qwamos" "QWAMOS base directory"
check_dir "/opt/qwamos/ai_assistants" "Phase 6 (AI Assistants)"

echo ""
echo "Checking permissions..."
echo "─────────────────────────────────────────────────────────────────"

# Check directory permissions
if [ -w "/opt/qwamos/ai_app_builder/logs" ]; then
    echo -e "${GREEN}✓${NC} Logs directory is writable"
else
    echo -e "${RED}✗${NC} Logs directory is not writable"
    VALIDATION_PASSED=false
fi

if [ -w "/opt/qwamos/ai_app_builder/generated_apps" ]; then
    echo -e "${GREEN}✓${NC} Generated apps directory is writable"
else
    echo -e "${RED}✗${NC} Generated apps directory is not writable"
    VALIDATION_PASSED=false
fi

echo ""
echo "Checking Python dependencies..."
echo "─────────────────────────────────────────────────────────────────"

# Check Python modules
python3 -c "import asyncio" 2>/dev/null && echo -e "${GREEN}✓${NC} asyncio available" || echo -e "${YELLOW}⚠${NC} asyncio not available"
python3 -c "import dataclasses" 2>/dev/null && echo -e "${GREEN}✓${NC} dataclasses available" || echo -e "${YELLOW}⚠${NC} dataclasses not available"
python3 -c "import typing" 2>/dev/null && echo -e "${GREEN}✓${NC} typing available" || echo -e "${YELLOW}⚠${NC} typing not available"
python3 -c "import json" 2>/dev/null && echo -e "${GREEN}✓${NC} json available" || echo -e "${RED}✗${NC} json not available"

echo ""
echo "Checking keystore..."
echo "─────────────────────────────────────────────────────────────────"

if [ -f "/opt/qwamos/keys/qwamos_release.keystore" ]; then
    echo -e "${GREEN}✓${NC} QWAMOS keystore exists"

    # Check keystore validity
    if command -v keytool &> /dev/null; then
        if keytool -list -keystore /opt/qwamos/keys/qwamos_release.keystore -storepass qwamos123 -alias qwamos_release &>/dev/null; then
            echo -e "${GREEN}✓${NC} QWAMOS keystore is valid"
        else
            echo -e "${RED}✗${NC} QWAMOS keystore is invalid"
            VALIDATION_PASSED=false
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} QWAMOS keystore not found (will be created on first use)"
fi

echo ""
echo "Calculating component sizes..."
echo "─────────────────────────────────────────────────────────────────"

# Count lines of code
TOTAL_PYTHON_LINES=0
for file in $(find /opt/qwamos/ai_app_builder -name "*.py" 2>/dev/null); do
    LINES=$(wc -l < "$file")
    TOTAL_PYTHON_LINES=$((TOTAL_PYTHON_LINES + LINES))
done

TOTAL_TS_LINES=0
for file in $(find /opt/qwamos/ai_app_builder/ui -name "*.ts" -o -name "*.tsx" 2>/dev/null); do
    LINES=$(wc -l < "$file")
    TOTAL_TS_LINES=$((TOTAL_TS_LINES + LINES))
done

echo "  • Python code:       ~${TOTAL_PYTHON_LINES} lines"
echo "  • TypeScript code:   ~${TOTAL_TS_LINES} lines"
echo "  • Total:             ~$((TOTAL_PYTHON_LINES + TOTAL_TS_LINES)) lines"

echo ""
echo "Component verification..."
echo "─────────────────────────────────────────────────────────────────"

# Count files
TOTAL_FILES=$(find /opt/qwamos/ai_app_builder -type f 2>/dev/null | wc -l)
PYTHON_FILES=$(find /opt/qwamos/ai_app_builder -name "*.py" 2>/dev/null | wc -l)
TS_FILES=$(find /opt/qwamos/ai_app_builder -name "*.ts" -o -name "*.tsx" 2>/dev/null | wc -l)
JSON_FILES=$(find /opt/qwamos/ai_app_builder -name "*.json" 2>/dev/null | wc -l)

echo "  • Total files:       ${TOTAL_FILES}"
echo "  • Python modules:    ${PYTHON_FILES}"
echo "  • TypeScript files:  ${TS_FILES}"
echo "  • Config files:      ${JSON_FILES}"

echo ""
echo "════════════════════════════════════════════════════════════════"

if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "  ${GREEN}✅ Validation PASSED${NC}"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "All components are properly installed and configured."
    echo "Phase 9 is ready for use."
    echo ""
    exit 0
else
    echo -e "  ${RED}❌ Validation FAILED${NC}"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "Some components are missing or misconfigured."
    echo "Please review the errors above and re-deploy Phase 9."
    echo ""
    exit 1
fi
