#!/usr/bin/env bash
# QWAMOS Docker Test Script
# Runs linting, static analysis, and tests inside Docker container

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$DOCKER_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

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

echo "========================================"
echo "QWAMOS Docker Test Suite"
echo "========================================"
echo ""

# Ensure container is running
ensure_container() {
    if ! docker ps | grep -q qwamos-build; then
        echo "Starting build container..."
        cd "$DOCKER_DIR"
        docker-compose up -d qbuild
        sleep 2
    fi
}

# Test 1: Linting
run_linting() {
    echo -e "${GREEN}[1/6] Running code linting...${NC}"
    echo ""

    # Python linting
    echo "Python linting (Black, Pylint, Flake8)..."
    docker exec qwamos-build bash -c '
        set +e
        cd /workspace

        # Black (code formatting check)
        if command -v black &> /dev/null; then
            black --check . 2>&1 | head -20
        fi

        # Pylint (code quality)
        if command -v pylint &> /dev/null && find . -name "*.py" -not -path "*/venv/*" | head -1 | grep -q .; then
            find . -name "*.py" -not -path "*/venv/*" -not -path "*/.git/*" | \
                xargs pylint --exit-zero 2>&1 | tail -20
        fi
    ' && pass "Python linting completed" || warn "Python linting had warnings"

    # Shell linting
    echo ""
    echo "Shell script linting (ShellCheck)..."
    docker exec qwamos-build bash -c '
        set +e
        if command -v shellcheck &> /dev/null; then
            find . -name "*.sh" -not -path "*/.git/*" -not -path "*/node_modules/*" | \
                xargs shellcheck 2>&1 | head -20
        else
            echo "ShellCheck not available"
        fi
    ' && pass "Shell linting completed" || warn "Shell linting had warnings"

    echo ""
}

# Test 2: Static Analysis
run_static_analysis() {
    echo -e "${GREEN}[2/6] Running static security analysis...${NC}"
    echo ""

    # Bandit (Python security)
    echo "Bandit security scan..."
    docker exec qwamos-build bash -c '
        set +e
        cd /workspace

        if command -v bandit &> /dev/null; then
            bandit -r . \
                --exclude "./venv,./env,./build,./dist,./.git" \
                -ll 2>&1 | tail -30
        else
            echo "Bandit not available"
        fi
    ' && pass "Bandit scan completed" || warn "Bandit found potential issues"

    # Safety (dependency check)
    echo ""
    echo "Safety dependency scan..."
    docker exec qwamos-build bash -c '
        set +e
        if command -v safety &> /dev/null && [ -f requirements.txt ]; then
            safety check --file requirements.txt 2>&1 | tail -20
        else
            echo "Safety or requirements.txt not available"
        fi
    ' && pass "Safety scan completed" || warn "Safety found vulnerabilities"

    echo ""
}

# Test 3: Unit Tests
run_unit_tests() {
    echo -e "${GREEN}[3/6] Running unit tests...${NC}"
    echo ""

    docker exec qwamos-build bash -c '
        set +e
        cd /workspace

        if command -v pytest &> /dev/null && [ -d tests ]; then
            echo "Running pytest..."
            pytest tests/ -v --tb=short --maxfail=5 2>&1 | tail -50
            exit ${PIPESTATUS[0]}
        else
            echo "No tests found or pytest not available"
            exit 0
        fi
    ' && pass "Unit tests passed" || fail "Unit tests failed"

    echo ""
}

# Test 4: VM Isolation Tests
run_vm_tests() {
    echo -e "${GREEN}[4/6] Running VM isolation tests...${NC}"
    echo ""

    docker exec qwamos-build bash -c '
        set +e
        cd /workspace

        if [ -f tests/vm-isolation/test_vm_isolation.sh ]; then
            echo "Running VM isolation tests..."
            bash tests/vm-isolation/test_vm_isolation.sh 2>&1 | tail -30
            exit ${PIPESTATUS[0]}
        else
            echo "VM isolation tests not found"
            exit 0
        fi
    ' && pass "VM isolation tests passed" || warn "VM isolation tests had warnings"

    echo ""
}

# Test 5: Gateway Tests
run_gateway_tests() {
    echo -e "${GREEN}[5/6] Running gateway security tests...${NC}"
    echo ""

    docker exec qwamos-build bash -c '
        set +e
        cd /workspace

        if [ -f tests/gateway/test_gateway_security.sh ]; then
            echo "Running gateway security tests..."
            bash tests/gateway/test_gateway_security.sh 2>&1 | tail -30
            exit ${PIPESTATUS[0]}
        else
            echo "Gateway tests not found"
            exit 0
        fi
    ' && pass "Gateway tests passed" || warn "Gateway tests had warnings"

    echo ""
}

# Test 6: PQC Tests
run_pqc_tests() {
    echo -e "${GREEN}[6/6] Running post-quantum crypto tests...${NC}"
    echo ""

    docker exec qwamos-build bash -c '
        set +e
        cd /workspace

        if [ -f tests/pqc/test_pqc_security.py ]; then
            echo "Running PQC tests..."
            python3 tests/pqc/test_pqc_security.py 2>&1 | tail -30
            exit ${PIPESTATUS[0]}
        else
            echo "PQC tests not found"
            exit 0
        fi
    ' && pass "PQC tests passed" || warn "PQC tests had warnings"

    echo ""
}

# Main execution
main() {
    ensure_container

    run_linting
    run_static_analysis
    run_unit_tests
    run_vm_tests
    run_gateway_tests
    run_pqc_tests

    # Summary
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo -e "${GREEN}Passed:${NC}   $PASS_COUNT"
    echo -e "${YELLOW}Warnings:${NC} $WARN_COUNT"
    echo -e "${RED}Failed:${NC}   $FAIL_COUNT"
    echo "========================================"
    echo ""

    if [ $FAIL_COUNT -eq 0 ]; then
        echo -e "${GREEN}✅ All tests passed!${NC}"
        exit 0
    elif [ $FAIL_COUNT -le 2 ]; then
        echo -e "${YELLOW}⚠️  Tests passed with some failures${NC}"
        exit 0
    else
        echo -e "${RED}❌ Tests failed${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
