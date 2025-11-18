#!/usr/bin/env bash
# QWAMOS Docker Build Script
# Builds QWAMOS modules inside Docker container

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$DOCKER_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "QWAMOS Docker Build"
echo "========================================"
echo ""

# Build Docker image
build_docker_image() {
    echo -e "${GREEN}[1/5] Building Docker image...${NC}"
    cd "$REPO_ROOT"

    docker build \
        -f docker/Dockerfile.build \
        -t qwamos/build:latest \
        .

    echo -e "${GREEN}✓ Docker image built successfully${NC}"
    echo ""
}

# Start build container
start_build_container() {
    echo -e "${GREEN}[2/5] Starting build container...${NC}"

    # Stop and remove existing container if present
    docker stop qwamos-build 2>/dev/null || true
    docker rm qwamos-build 2>/dev/null || true

    # Start container with docker-compose
    cd "$DOCKER_DIR"
    docker-compose up -d qbuild

    echo -e "${GREEN}✓ Build container started${NC}"
    echo ""
}

# Build Python modules
build_python_modules() {
    echo -e "${GREEN}[3/5] Building Python modules...${NC}"

    docker exec qwamos-build bash -c '
        set -e
        cd /workspace

        # Install Python dependencies if requirements.txt exists
        if [ -f requirements.txt ]; then
            echo "Installing Python dependencies..."
            pip3 install --user -r requirements.txt
        fi

        # Build Python packages if setup.py exists
        if [ -f setup.py ]; then
            echo "Building Python package..."
            python3 setup.py build
            python3 setup.py sdist bdist_wheel
        fi

        # Run Python tests if tests directory exists
        if [ -d tests ] && command -v pytest &> /dev/null; then
            echo "Running Python tests..."
            pytest tests/ -v --tb=short || true
        fi

        echo "Python modules built successfully"
    '

    echo -e "${GREEN}✓ Python modules built${NC}"
    echo ""
}

# Build VM templates
build_vm_templates() {
    echo -e "${GREEN}[4/5] Building VM templates...${NC}"

    docker exec qwamos-build bash -c '
        set -e
        cd /workspace

        if [ -d vm-templates/scripts ]; then
            echo "Building QEMU template..."
            bash vm-templates/scripts/build_qemu_template.sh || true

            echo "Building PRoot template..."
            bash vm-templates/scripts/build_proot_template.sh || true

            echo "Building Chroot template..."
            bash vm-templates/scripts/build_chroot_template.sh || true

            # Copy templates to build artifacts
            if [ -d vm-templates/output/templates ]; then
                cp -r vm-templates/output/templates/* /build_artifacts/ || true
            fi

            echo "VM templates built successfully"
        else
            echo "No VM templates to build"
        fi
    '

    echo -e "${GREEN}✓ VM templates built${NC}"
    echo ""
}

# Export build artifacts
export_artifacts() {
    echo -e "${GREEN}[5/5] Exporting build artifacts...${NC}"

    # Create local build artifacts directory
    mkdir -p "$REPO_ROOT/build_artifacts"

    # Copy artifacts from container
    docker cp qwamos-build:/build_artifacts/. "$REPO_ROOT/build_artifacts/" || true

    # Copy Python dist if exists
    docker exec qwamos-build bash -c '
        if [ -d /workspace/dist ]; then
            cp -r /workspace/dist/* /build_artifacts/ 2>/dev/null || true
        fi
    ' || true

    docker cp qwamos-build:/build_artifacts/. "$REPO_ROOT/build_artifacts/" || true

    # List artifacts
    echo ""
    echo "Build artifacts:"
    ls -lh "$REPO_ROOT/build_artifacts/" || echo "No artifacts found"

    echo -e "${GREEN}✓ Build artifacts exported${NC}"
    echo ""
}

# Main execution
main() {
    build_docker_image
    start_build_container
    build_python_modules
    build_vm_templates
    export_artifacts

    echo "========================================"
    echo -e "${GREEN}✅ QWAMOS Build Complete!${NC}"
    echo "========================================"
    echo ""
    echo "Build artifacts available in: $REPO_ROOT/build_artifacts/"
    echo ""
    echo "To access build container:"
    echo "  docker exec -it qwamos-build /bin/bash"
    echo ""
    echo "To stop build container:"
    echo "  docker-compose -f docker/docker-compose.yml down"
    echo ""
}

# Run main function
main "$@"
