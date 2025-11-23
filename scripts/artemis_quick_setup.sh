#!/bin/bash
# QWAMOS Artemis Quick Setup Script
# Installs all security analysis tools on Ubuntu/Debian

set -euo pipefail

echo "════════════════════════════════════════════════════════════"
echo "  QWAMOS ARTEMIS PIPELINE - TOOL INSTALLATION"
echo "  Claude Sonnet 4.5 Autonomous Security System"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
  SUDO=""
else
  SUDO="sudo"
fi

echo "[1/5] Updating package lists..."
$SUDO apt-get update -qq

echo "[2/5] Installing base packages..."
$SUDO apt-get install -y -qq \
  build-essential \
  python3-pip python3-venv \
  git curl wget \
  shellcheck \
  cppcheck \
  default-jre \
  golang-go \
  jq

echo "[3/5] Installing Python security tools..."
pip3 install --user --quiet \
  bandit \
  semgrep \
  safety \
  pip-audit

echo "[4/5] Installing gitleaks..."
if ! command -v gitleaks &> /dev/null; then
  wget -q https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
  tar -xzf gitleaks_8.18.0_linux_x64.tar.gz
  $SUDO mv gitleaks /usr/local/bin/
  rm gitleaks_8.18.0_linux_x64.tar.gz
fi

echo "[5/5] Installing syft and grype..."
if ! command -v syft &> /dev/null; then
  curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
fi

if ! command -v grype &> /dev/null; then
  curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ INSTALLATION COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Installed tools:"
echo "  • bandit (Python security)"
echo "  • semgrep (Multi-language analysis)"
echo "  • shellcheck (Shell script analysis)"
echo "  • gitleaks (Secret scanning)"
echo "  • syft (SBOM generation)"
echo "  • grype (Vulnerability scanning)"
echo ""
echo "Next steps:"
echo "  1. cd ~/QWAMOS"
echo "  2. python3 artemis_full_pipeline.py"
echo ""
