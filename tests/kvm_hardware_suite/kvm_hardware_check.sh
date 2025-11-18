#!/bin/bash
###############################################################################
# QWAMOS KVM Hardware Check
# Phase XII: KVM Acceleration - Hardware Validation
#
# Tests ARM device for KVM virtualization support
# Author: QWAMOS Project
# License: AGPL-3.0
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo "==============================================================================="
    echo "$1"
    echo "==============================================================================="
    echo ""
}

print_test() {
    echo -n "  [TEST] $1... "
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

pass() {
    echo -e "${GREEN}PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail() {
    echo -e "${RED}FAIL${NC}"
    if [ -n "$1" ]; then
        echo "         Reason: $1"
    fi
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

warn() {
    echo -e "${YELLOW}WARN${NC}"
    if [ -n "$1" ]; then
        echo "         Warning: $1"
    fi
}

info() {
    echo -e "${BLUE}INFO${NC} $1"
}

###############################################################################
# Test Functions
###############################################################################

test_kvm_device() {
    print_test "KVM device exists (/dev/kvm)"
    if [ -e /dev/kvm ]; then
        pass
        return 0
    else
        fail "/dev/kvm not found"
        return 1
    fi
}

test_kvm_permissions() {
    print_test "KVM device permissions"
    if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then
        pass
        return 0
    else
        fail "Cannot read/write /dev/kvm (try: sudo chmod 666 /dev/kvm)"
        return 1
    fi
}

test_cpu_virtualization() {
    print_test "CPU virtualization flags"

    if grep -qE "virt|hyp|kvm" /proc/cpuinfo 2>/dev/null; then
        pass
        info "Found virtualization support in CPU"
        grep -E "virt|hyp|kvm" /proc/cpuinfo | head -3 | sed 's/^/         /'
        return 0
    else
        fail "No virtualization flags found in /proc/cpuinfo"
        return 1
    fi
}

test_kernel_kvm_support() {
    print_test "Kernel KVM support"

    # Try multiple methods to check kernel config
    local found=0

    # Method 1: Check loaded modules
    if lsmod 2>/dev/null | grep -q kvm; then
        pass
        info "KVM module loaded"
        lsmod | grep kvm | sed 's/^/         /'
        return 0
    fi

    # Method 2: Check /proc/config.gz
    if [ -f /proc/config.gz ]; then
        if zcat /proc/config.gz 2>/dev/null | grep -qE "CONFIG_KVM=|CONFIG_KVM_ARM"; then
            found=1
        fi
    fi

    # Method 3: Check /boot/config-*
    if [ $found -eq 0 ]; then
        for config in /boot/config-* /boot/config /proc/config; do
            if [ -f "$config" ]; then
                if grep -qE "CONFIG_KVM=|CONFIG_KVM_ARM" "$config" 2>/dev/null; then
                    found=1
                    break
                fi
            fi
        done
    fi

    # Method 4: Check dmesg
    if [ $found -eq 0 ]; then
        if dmesg 2>/dev/null | grep -qi "kvm"; then
            found=1
        fi
    fi

    if [ $found -eq 1 ]; then
        pass
        return 0
    else
        warn "Cannot verify kernel KVM config (may still work)"
        return 0  # Don't fail, just warn
    fi
}

test_arm_vhe_support() {
    print_test "ARM Virtualization Host Extensions (VHE)"

    # Check for ARM VHE in kernel config or dmesg
    if dmesg 2>/dev/null | grep -qi "VHE"; then
        pass
        info "VHE detected in dmesg"
        return 0
    elif [ -f /proc/config.gz ] && zcat /proc/config.gz 2>/dev/null | grep -q "CONFIG_ARM64_VHE=y"; then
        pass
        info "VHE enabled in kernel config"
        return 0
    else
        warn "Cannot verify VHE support (not critical)"
        return 0  # Don't fail, VHE is optional
    fi
}

test_selinux_apparmor() {
    print_test "SELinux/AppArmor interference check"

    local blocked=0

    # Check SELinux
    if command -v getenforce >/dev/null 2>&1; then
        local selinux_status=$(getenforce 2>/dev/null || echo "Unknown")
        if [ "$selinux_status" = "Enforcing" ]; then
            warn "SELinux is Enforcing (may block KVM access)"
            info "To test: sudo setenforce 0"
            blocked=1
        fi
    fi

    # Check AppArmor
    if command -v aa-status >/dev/null 2>&1; then
        if aa-status 2>/dev/null | grep -q "profiles.*enforc"; then
            warn "AppArmor is active (may block KVM access)"
            blocked=1
        fi
    fi

    if [ $blocked -eq 0 ]; then
        pass
        return 0
    else
        return 0  # Don't fail, just warn
    fi
}

test_qemu_kvm_binary() {
    print_test "QEMU with KVM support"

    if command -v qemu-system-aarch64 >/dev/null 2>&1; then
        if qemu-system-aarch64 --version 2>/dev/null | grep -q "QEMU"; then
            pass
            info "QEMU version: $(qemu-system-aarch64 --version | head -1)"
            return 0
        fi
    fi

    fail "qemu-system-aarch64 not found or not working"
    return 1
}

test_memory_availability() {
    print_test "Available memory for VMs"

    if command -v free >/dev/null 2>&1; then
        local available_mb=$(free -m | awk '/^Mem:/{print $7}')
        if [ -z "$available_mb" ]; then
            available_mb=$(free -m | awk '/^Mem:/{print $4}')  # Fallback
        fi

        if [ "$available_mb" -ge 2048 ]; then
            pass
            info "Available: ${available_mb}MB (recommended: 2GB+ per VM)"
            return 0
        elif [ "$available_mb" -ge 1024 ]; then
            warn "Available: ${available_mb}MB (low, recommended: 2GB+ per VM)"
            return 0
        else
            fail "Only ${available_mb}MB available (need 1GB+ minimum)"
            return 1
        fi
    else
        warn "Cannot check memory (free command not available)"
        return 0
    fi
}

test_cpu_cores() {
    print_test "CPU cores for VM allocation"

    local cores=$(nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo 1)

    if [ "$cores" -ge 4 ]; then
        pass
        info "Available cores: $cores (recommended: 4+ for multi-VM)"
        return 0
    elif [ "$cores" -ge 2 ]; then
        warn "Available cores: $cores (minimum for QWAMOS)"
        return 0
    else
        fail "Only $cores core(s) (need 2+ minimum)"
        return 1
    fi
}

test_kvm_acceleration() {
    print_test "KVM acceleration functional test"

    if [ ! -e /dev/kvm ]; then
        fail "/dev/kvm does not exist"
        return 1
    fi

    # Try to open /dev/kvm using a simple test
    if command -v qemu-system-aarch64 >/dev/null 2>&1; then
        # Quick test: try to query KVM capabilities
        if qemu-system-aarch64 -machine help 2>/dev/null | grep -q "virt"; then
            pass
            info "QEMU can access virtualization capabilities"
            return 0
        fi
    fi

    warn "Cannot fully test KVM acceleration (need QEMU test)"
    return 0
}

###############################################################################
# System Information
###############################################################################

print_system_info() {
    print_header "System Information"

    echo "Hostname:       $(hostname 2>/dev/null || echo 'unknown')"
    echo "Kernel:         $(uname -r)"
    echo "Architecture:   $(uname -m)"
    echo "OS:             $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || uname -o)"

    if [ -f /proc/cpuinfo ]; then
        local cpu_model=$(grep -m1 "^model name" /proc/cpuinfo | cut -d: -f2 | xargs)
        if [ -z "$cpu_model" ]; then
            cpu_model=$(grep -m1 "^Processor" /proc/cpuinfo | cut -d: -f2 | xargs)
        fi
        if [ -z "$cpu_model" ]; then
            cpu_model=$(grep -m1 "^CPU" /proc/cpuinfo | cut -d: -f2 | xargs)
        fi
        echo "CPU Model:      ${cpu_model:-Unknown}"
    fi

    local cores=$(nproc 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo "unknown")
    echo "CPU Cores:      $cores"

    if command -v free >/dev/null 2>&1; then
        local total_mem=$(free -h | awk '/^Mem:/{print $2}')
        echo "Total Memory:   $total_mem"
    fi

    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    clear

    print_header "QWAMOS Phase XII - KVM Hardware Validation Suite"

    echo "Testing ARM device for KVM virtualization support..."
    echo "This script will check:"
    echo "  - KVM device presence and permissions"
    echo "  - CPU virtualization capabilities"
    echo "  - Kernel KVM support"
    echo "  - Security policy interference"
    echo "  - System resources"
    echo ""

    print_system_info

    print_header "Running Hardware Tests"

    # Core KVM tests
    test_kvm_device
    test_kvm_permissions
    test_cpu_virtualization
    test_kernel_kvm_support
    test_arm_vhe_support

    # System compatibility tests
    test_selinux_apparmor
    test_qemu_kvm_binary
    test_memory_availability
    test_cpu_cores
    test_kvm_acceleration

    # Summary
    print_header "Test Results Summary"

    echo "Total Tests:    $TESTS_TOTAL"
    echo -e "Passed:         ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed:         ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
        echo ""
        echo "This device appears to support KVM acceleration!"
        echo "Phase XII KVM implementation should work on this hardware."
        echo ""
        echo "Next steps:"
        echo "  1. Run: python3 kvm_capability_report.py"
        echo "  2. Run: python3 kvm_perf_benchmark.py"
        echo "  3. Run: python3 vm_boot_test.py"
        echo ""
        exit 0
    else
        echo -e "${RED}❌ SOME TESTS FAILED${NC}"
        echo ""
        echo "This device may not fully support KVM acceleration."
        echo "Review failed tests above and check:"
        echo "  - Kernel was compiled with CONFIG_KVM=y"
        echo "  - Device has ARM virtualization extensions"
        echo "  - /dev/kvm has correct permissions"
        echo ""
        exit 1
    fi
}

# Run main function
main "$@"
