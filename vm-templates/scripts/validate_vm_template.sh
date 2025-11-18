#!/usr/bin/env bash
# Validate QWAMOS VM Templates
# Performs comprehensive validation of VM template structure and integrity

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_TEMPLATES_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# Functions for output
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN_COUNT++))
}

info() {
    echo -e "ℹ $1"
}

# Usage function
usage() {
    cat << EOF
Usage: $0 <template-file> [options]

Validate QWAMOS VM templates

Arguments:
  template-file     Path to template .tar.gz file

Options:
  -t, --type TYPE   Expected VM type (qemu|proot|chroot)
  -v, --verbose     Verbose output
  -h, --help        Show this help message

Examples:
  $0 qwamos-qemu-template.tar.gz
  $0 qwamos-proot-template.tar.gz --type proot
  $0 /path/to/template.tar.gz --verbose
EOF
}

# Parse arguments
TEMPLATE_FILE=""
EXPECTED_TYPE=""
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            EXPECTED_TYPE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            if [ -z "$TEMPLATE_FILE" ]; then
                TEMPLATE_FILE="$1"
            else
                echo "Error: Unknown argument: $1"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if template file provided
if [ -z "$TEMPLATE_FILE" ]; then
    echo "Error: Template file required"
    usage
    exit 1
fi

echo "========================================"
echo "QWAMOS VM Template Validator"
echo "========================================"
echo "Template: $(basename "$TEMPLATE_FILE")"
echo "========================================"
echo ""

# Create temporary directory
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Test 1: Check if file exists
info "[1/10] Checking file existence..."
if [ -f "$TEMPLATE_FILE" ]; then
    pass "Template file exists"
else
    fail "Template file not found: $TEMPLATE_FILE"
    exit 1
fi

# Test 2: Check file size
info "[2/10] Checking file size..."
FILE_SIZE=$(stat -f%z "$TEMPLATE_FILE" 2>/dev/null || stat -c%s "$TEMPLATE_FILE" 2>/dev/null || echo "0")
if [ "$FILE_SIZE" -gt 0 ]; then
    SIZE_MB=$((FILE_SIZE / 1024 / 1024))
    pass "File size: ${SIZE_MB}MB"

    if [ "$FILE_SIZE" -lt 1024 ]; then
        warn "File size suspiciously small (< 1KB)"
    fi
else
    fail "File is empty or size cannot be determined"
fi

# Test 3: Verify checksum file
info "[3/10] Checking for checksum file..."
CHECKSUM_FILE="${TEMPLATE_FILE}.sha256"
if [ -f "$CHECKSUM_FILE" ]; then
    pass "Checksum file found"

    # Verify checksum
    if command -v sha256sum &> /dev/null; then
        info "Verifying checksum..."
        cd "$(dirname "$TEMPLATE_FILE")"
        if sha256sum -c "$(basename "$CHECKSUM_FILE")" &> /dev/null; then
            pass "Checksum verification passed"
        else
            fail "Checksum verification failed"
        fi
    else
        warn "sha256sum not available, skipping verification"
    fi
else
    warn "Checksum file not found: $CHECKSUM_FILE"
fi

# Test 4: Extract archive
info "[4/10] Extracting template archive..."
cd "$TEMP_DIR"
if tar xzf "$TEMPLATE_FILE" 2>/dev/null; then
    pass "Archive extracted successfully"
else
    fail "Failed to extract archive"
    exit 1
fi

# Test 5: Check for required files
info "[5/10] Checking for required files..."

# Look for metadata JSON
JSON_FILE=$(find . -name "*.json" -type f | head -n1)
if [ -n "$JSON_FILE" ]; then
    pass "Metadata file found: $(basename "$JSON_FILE")"
else
    fail "No metadata JSON file found"
fi

# Look for rootfs tarball
ROOTFS_TAR=$(find . -name "*-rootfs.tar.gz" -type f | head -n1)
if [ -n "$ROOTFS_TAR" ]; then
    pass "Rootfs tarball found: $(basename "$ROOTFS_TAR")"
else
    warn "No rootfs tarball found"
fi

# Test 6: Validate metadata JSON
info "[6/10] Validating metadata JSON..."
if [ -n "$JSON_FILE" ]; then
    # Check if valid JSON
    if command -v python3 &> /dev/null; then
        if python3 -c "import json; json.load(open('$JSON_FILE'))" 2>/dev/null; then
            pass "JSON is valid"

            # Extract and display key fields
            VM_TYPE=$(python3 -c "import json; print(json.load(open('$JSON_FILE')).get('type', 'unknown'))" 2>/dev/null)
            VM_VERSION=$(python3 -c "import json; print(json.load(open('$JSON_FILE')).get('version', 'unknown'))" 2>/dev/null)

            info "  VM Type: $VM_TYPE"
            info "  Version: $VM_VERSION"

            # Check expected type if specified
            if [ -n "$EXPECTED_TYPE" ]; then
                if [ "$VM_TYPE" = "$EXPECTED_TYPE" ]; then
                    pass "VM type matches expected: $EXPECTED_TYPE"
                else
                    fail "VM type mismatch. Expected: $EXPECTED_TYPE, Got: $VM_TYPE"
                fi
            fi

        else
            fail "Invalid JSON format"
        fi
    else
        warn "Python3 not available, skipping JSON validation"
    fi
fi

# Test 7: Check rootfs structure
info "[7/10] Validating rootfs structure..."
if [ -n "$ROOTFS_TAR" ]; then
    ROOTFS_EXTRACT="$TEMP_DIR/rootfs_check"
    mkdir -p "$ROOTFS_EXTRACT"

    if tar xzf "$ROOTFS_TAR" -C "$ROOTFS_EXTRACT" 2>/dev/null; then
        pass "Rootfs extracted for validation"

        # Check for essential directories
        REQUIRED_DIRS=("bin" "etc" "usr" "var" "opt")
        MISSING_DIRS=()

        for dir in "${REQUIRED_DIRS[@]}"; do
            if [ -d "$ROOTFS_EXTRACT/$dir" ]; then
                $VERBOSE && pass "  Directory exists: /$dir"
            else
                MISSING_DIRS+=("$dir")
            fi
        done

        if [ ${#MISSING_DIRS[@]} -eq 0 ]; then
            pass "All essential directories present"
        else
            fail "Missing directories: ${MISSING_DIRS[*]}"
        fi

        # Check for QWAMOS-specific structure
        if [ -d "$ROOTFS_EXTRACT/opt/qwamos" ]; then
            pass "QWAMOS directory structure found"

            # Check for config files
            if [ -f "$ROOTFS_EXTRACT/opt/qwamos/config/qwamos.conf" ]; then
                pass "QWAMOS configuration file present"
            else
                warn "QWAMOS configuration file missing"
            fi
        else
            warn "QWAMOS directory structure not found in /opt/qwamos"
        fi

    else
        fail "Failed to extract rootfs tarball"
    fi
fi

# Test 8: Check launcher scripts
info "[8/10] Checking for launcher scripts..."
LAUNCHER_FOUND=false

for launcher in launch-*.sh; do
    if [ -f "$launcher" ]; then
        pass "Launcher script found: $launcher"
        LAUNCHER_FOUND=true

        # Check if executable
        if [ -x "$launcher" ]; then
            pass "  Script is executable"
        else
            warn "  Script is not executable"
        fi
    fi
done

if ! $LAUNCHER_FOUND; then
    warn "No launcher script found"
fi

# Test 9: Verify checksums of extracted files
info "[9/10] Verifying internal file checksums..."
if command -v sha256sum &> /dev/null; then
    CHECKSUM_FILES=$(find . -name "*.sha256" -type f)

    if [ -n "$CHECKSUM_FILES" ]; then
        CHECKSUM_PASS=0
        CHECKSUM_FAIL=0

        for checksum in $CHECKSUM_FILES; do
            cd "$(dirname "$checksum")"
            if sha256sum -c "$(basename "$checksum")" &> /dev/null; then
                ((CHECKSUM_PASS++))
            else
                ((CHECKSUM_FAIL++))
            fi
            cd "$TEMP_DIR"
        done

        if [ $CHECKSUM_FAIL -eq 0 ]; then
            pass "All internal checksums verified ($CHECKSUM_PASS files)"
        else
            fail "Some checksums failed ($CHECKSUM_FAIL/$((CHECKSUM_PASS + CHECKSUM_FAIL)))"
        fi
    else
        warn "No internal checksum files found"
    fi
else
    warn "sha256sum not available"
fi

# Test 10: Check for documentation
info "[10/10] Checking for documentation..."
README_FOUND=false

for readme in README* readme* README.txt README.md; do
    if [ -f "$readme" ] || [ -f "rootfs_check/$readme" ]; then
        pass "Documentation found: $readme"
        README_FOUND=true
    fi
done

if ! $README_FOUND; then
    warn "No README documentation found"
fi

# Final summary
echo ""
echo "========================================"
echo "Validation Summary"
echo "========================================"
echo -e "${GREEN}Passed:${NC}  $PASS_COUNT"
echo -e "${YELLOW}Warnings:${NC} $WARN_COUNT"
echo -e "${RED}Failed:${NC}  $FAIL_COUNT"
echo "========================================"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✅ Template validation PASSED${NC}"
    exit 0
elif [ $FAIL_COUNT -le 2 ] && [ $PASS_COUNT -gt 5 ]; then
    echo -e "${YELLOW}⚠️  Template validation passed with warnings${NC}"
    exit 0
else
    echo -e "${RED}❌ Template validation FAILED${NC}"
    exit 1
fi
