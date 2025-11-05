#!/bin/bash
################################################################################
# QWAMOS Phase 10: Deployment Script
################################################################################
#
# Deploys and validates Phase 10 advanced hardware security components.
#
# Components:
#   1. ML Bootloader Override System
#   2. Firmware Integrity Monitor
#   3. A/B Partition Isolation
#   4. Hardware Kill Switch Kernel Driver
#   5. UI Integration (Bootloader Lock Toggle)
#
# Usage:
#   ./deploy_phase10.sh [--dry-run] [--skip-tests]
#
# Version: 1.0.0
# Date: 2025-11-05
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
QWAMOS_ROOT="/data/data/com.termux/files/home/QWAMOS"
SECURITY_DIR="$QWAMOS_ROOT/security"
HYPERVISOR_DIR="$QWAMOS_ROOT/hypervisor"
UI_DIR="$QWAMOS_ROOT/system/ui"

DRY_RUN=false
SKIP_TESTS=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
    esac
done

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo ""
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

################################################################################
# Deployment Steps
################################################################################

print_header "QWAMOS Phase 10 Deployment"

echo "Deployment Configuration:"
echo "  QWAMOS Root: $QWAMOS_ROOT"
echo "  Dry Run: $DRY_RUN"
echo "  Skip Tests: $SKIP_TESTS"
echo ""

if [ "$DRY_RUN" = true ]; then
    print_warning "Running in DRY RUN mode (no changes will be made)"
    echo ""
fi

# Step 1: Check prerequisites
print_header "Step 1: Checking Prerequisites"

check_root

# Check Python 3
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 3 installed: $PYTHON_VERSION"
else
    print_error "Python 3 not found"
    exit 1
fi

# Check required Python packages
print_info "Checking Python dependencies..."
python3 -c "import hashlib, json, subprocess" 2>/dev/null && print_success "Python dependencies OK" || {
    print_error "Missing Python dependencies"
    exit 1
}

# Check kernel headers (for driver compilation)
if [ -d "/lib/modules/$(uname -r)/build" ]; then
    print_success "Kernel headers found"
else
    print_warning "Kernel headers not found (driver compilation will fail)"
fi

# Step 2: Deploy ML Bootloader Override
print_header "Step 2: Deploying ML Bootloader Override System"

if [ "$DRY_RUN" = false ]; then
    # Create config directory
    mkdir -p /etc/qwamos
    chmod 755 /etc/qwamos

    # Deploy Python module
    cp "$SECURITY_DIR/ml_bootloader_override.py" /usr/local/bin/
    chmod 755 /usr/local/bin/ml_bootloader_override.py

    # Create default config
    if [ ! -f /etc/qwamos/ml_override.conf ]; then
        cat > /etc/qwamos/ml_override.conf << EOF
{
  "user_lock_enabled": false,
  "permission_timeout": 10,
  "biometric_required": true,
  "log_all_events": true,
  "auto_lock_on_timeout": true
}
EOF
        chmod 600 /etc/qwamos/ml_override.conf
        print_success "Created default ML override config"
    else
        print_info "ML override config already exists"
    fi

    # Create log directory
    mkdir -p /var/log/qwamos
    chmod 755 /var/log/qwamos

    print_success "ML Bootloader Override deployed"
else
    print_info "[DRY RUN] Would deploy ML Bootloader Override"
fi

# Step 3: Deploy Firmware Integrity Monitor
print_header "Step 3: Deploying Firmware Integrity Monitor"

if [ "$DRY_RUN" = false ]; then
    cp "$SECURITY_DIR/firmware_integrity_monitor.py" /usr/local/bin/
    chmod 755 /usr/local/bin/firmware_integrity_monitor.py

    print_success "Firmware Integrity Monitor deployed"
else
    print_info "[DRY RUN] Would deploy Firmware Integrity Monitor"
fi

# Step 4: Deploy A/B Partition Isolation
print_header "Step 4: Deploying A/B Partition Isolation"

if [ "$DRY_RUN" = false ]; then
    cp "$SECURITY_DIR/ab_partition_isolation.py" /usr/local/bin/
    chmod 755 /usr/local/bin/ab_partition_isolation.py

    print_success "A/B Partition Isolation deployed"
else
    print_info "[DRY RUN] Would deploy A/B Partition Isolation"
fi

# Step 5: Build and Load Kernel Driver
print_header "Step 5: Building Hardware Kill Switch Kernel Driver"

if [ -d "/lib/modules/$(uname -r)/build" ]; then
    if [ "$DRY_RUN" = false ]; then
        cd "$HYPERVISOR_DIR/drivers"

        # Build kernel module
        print_info "Building usb_killswitch.ko..."
        make clean
        make all

        if [ -f usb_killswitch.ko ]; then
            print_success "Kernel module built successfully"

            # Load kernel module
            print_info "Loading kernel module..."
            rmmod usb_killswitch 2>/dev/null || true
            insmod usb_killswitch.ko

            # Verify loaded
            if lsmod | grep usb_killswitch > /dev/null; then
                print_success "Kernel module loaded"
            else
                print_error "Failed to load kernel module"
            fi
        else
            print_error "Kernel module build failed"
        fi
    else
        print_info "[DRY RUN] Would build and load kernel driver"
    fi
else
    print_warning "Skipping kernel driver (kernel headers not found)"
fi

# Step 6: Deploy UI Components
print_header "Step 6: Deploying UI Components"

if [ "$DRY_RUN" = false ]; then
    cp "$UI_DIR/settings/security/bootloader_lock_toggle.tsx" "$UI_DIR/settings/security/"
    chmod 644 "$UI_DIR/settings/security/bootloader_lock_toggle.tsx"

    print_success "UI components deployed"
else
    print_info "[DRY RUN] Would deploy UI components"
fi

# Step 7: Run Integration Tests
if [ "$SKIP_TESTS" = false ]; then
    print_header "Step 7: Running Integration Tests"

    if [ "$DRY_RUN" = false ]; then
        cd "$SECURITY_DIR/tests"
        python3 test_phase10_integration.py

        if [ $? -eq 0 ]; then
            print_success "All tests passed"
        else
            print_error "Some tests failed"
            exit 1
        fi
    else
        print_info "[DRY RUN] Would run integration tests"
    fi
else
    print_warning "Skipping integration tests (--skip-tests)"
fi

# Step 8: Validation
print_header "Step 8: Validating Deployment"

if [ "$DRY_RUN" = false ]; then
    # Check files exist
    FILES=(
        "/usr/local/bin/ml_bootloader_override.py"
        "/usr/local/bin/firmware_integrity_monitor.py"
        "/usr/local/bin/ab_partition_isolation.py"
        "/etc/qwamos/ml_override.conf"
    )

    for file in "${FILES[@]}"; do
        if [ -f "$file" ]; then
            print_success "Found: $file"
        else
            print_error "Missing: $file"
        fi
    done

    # Check kernel module
    if lsmod | grep usb_killswitch > /dev/null; then
        print_success "Kernel module loaded"
    else
        print_warning "Kernel module not loaded"
    fi

    # Check sysfs interface
    if [ -d /sys/kernel/usb_killswitch ]; then
        print_success "Sysfs interface created"
    else
        print_warning "Sysfs interface not found"
    fi
else
    print_info "[DRY RUN] Would validate deployment"
fi

################################################################################
# Summary
################################################################################

print_header "Deployment Summary"

if [ "$DRY_RUN" = false ]; then
    echo "Phase 10 components deployed:"
    echo ""
    echo "  ✅ ML Bootloader Override System"
    echo "  ✅ Firmware Integrity Monitor"
    echo "  ✅ A/B Partition Isolation"
    echo "  ✅ Hardware Kill Switch Kernel Driver (if supported)"
    echo "  ✅ UI Components"
    echo ""
    echo "Configuration:"
    echo "  Config: /etc/qwamos/ml_override.conf"
    echo "  Logs:   /var/log/qwamos/"
    echo "  Sysfs:  /sys/kernel/usb_killswitch/"
    echo ""
    echo "Next Steps:"
    echo "  1. Configure expected bootloader hashes"
    echo "  2. Update firmware version in config"
    echo "  3. Test bootloader lock toggle in UI"
    echo "  4. Build and install USB kill switch hardware"
    echo "  5. Run full security audit"
    echo ""
    print_success "Phase 10 deployment complete!"
else
    print_info "Dry run complete (no changes made)"
fi

exit 0
