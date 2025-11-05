#!/bin/bash
#
# QWAMOS AI Services Deployment Script
#
# This script automates the deployment of QWAMOS AI backend services:
# - Creates necessary directories
# - Copies configuration files
# - Installs systemd services
# - Sets up permissions
# - Downloads Kali GPT model (optional)
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        log_info "Usage: sudo $0"
        exit 1
    fi
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."

    mkdir -p /opt/qwamos/ai/{kali_gpt,claude,chatgpt,config,cache,logs}
    mkdir -p /opt/qwamos/ai/kali_gpt/{models,prompts,tools,knowledge,cache}
    mkdir -p /opt/qwamos/ai/claude/{prompts,cache}
    mkdir -p /opt/qwamos/ai/chatgpt/{prompts,cache}
    mkdir -p /var/log/qwamos
    mkdir -p /var/run/qwamos

    log_success "Directories created"
}

# Copy Python backend files
copy_backend_files() {
    log_info "Copying Python backend files..."

    # Copy main scripts
    cp ai_manager.py /opt/qwamos/ai/
    cp qwamos-ai /opt/qwamos/ai/
    chmod +x /opt/qwamos/ai/qwamos-ai

    # Copy controllers
    cp kali_gpt/kali_gpt_controller.py /opt/qwamos/ai/kali_gpt/
    cp claude/claude_controller.py /opt/qwamos/ai/claude/
    cp chatgpt/chatgpt_controller.py /opt/qwamos/ai/chatgpt/

    # Copy security modules
    cp -r security/ /opt/qwamos/ai/

    log_success "Backend files copied"
}

# Copy configuration files
copy_config_files() {
    log_info "Copying configuration files..."

    cp config/*.json /opt/qwamos/ai/config/

    log_success "Configuration files copied"
}

# Install systemd services
install_systemd_services() {
    log_info "Installing systemd services..."

    # Copy service files
    cp systemd/*.service /etc/systemd/system/

    # Reload systemd
    systemctl daemon-reload

    log_success "Systemd services installed"
}

# Set permissions
set_permissions() {
    log_info "Setting permissions..."

    # Create qwamos user if doesn't exist
    if ! id -u qwamos > /dev/null 2>&1; then
        useradd -r -s /bin/false qwamos
        log_info "Created qwamos user"
    fi

    # Set ownership
    chown -R qwamos:qwamos /opt/qwamos/ai
    chown -R qwamos:qwamos /var/log/qwamos
    chown -R qwamos:qwamos /var/run/qwamos

    # Set permissions
    chmod 755 /opt/qwamos/ai
    chmod 700 /opt/qwamos/ai/config  # Protect API keys
    chmod 755 /opt/qwamos/ai/cache

    log_success "Permissions set"
}

# Install Python dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."

    # Check if pip3 is installed
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 not found. Please install Python 3 and pip3"
        exit 1
    fi

    # Install required packages
    pip3 install --upgrade \
        anthropic \
        openai \
        requests \
        pysocks \
        cryptography \
        llama-cpp-python

    log_success "Python dependencies installed"
}

# Download Kali GPT model
download_kali_gpt_model() {
    log_info "Checking Kali GPT model..."

    MODEL_PATH="/opt/qwamos/ai/kali_gpt/models/llama-3.1-8b-q4.gguf"

    if [[ -f "$MODEL_PATH" ]]; then
        log_success "Kali GPT model already downloaded"
        return
    fi

    log_warning "Kali GPT model not found"
    log_info "Model download required: ~4.5GB download"

    read -p "Download Kali GPT model now? (y/n) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Skipping model download. Kali GPT will not work until model is downloaded."
        log_info "To download later, run: sudo /opt/qwamos/ai/scripts/download_kali_gpt_model.sh"
        return
    fi

    log_info "Downloading Kali GPT model (this may take a while)..."

    cd /opt/qwamos/ai/kali_gpt/models

    # Download from HuggingFace
    wget -c https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q4_K_M.gguf \
        -O llama-3.1-8b-q4.gguf

    # Verify download
    if [[ -f "$MODEL_PATH" ]]; then
        MODEL_SIZE=$(stat -c%s "$MODEL_PATH")
        log_success "Model downloaded successfully (${MODEL_SIZE} bytes)"
        chown qwamos:qwamos "$MODEL_PATH"
    else
        log_error "Model download failed"
        exit 1
    fi
}

# Enable and start services
enable_services() {
    log_info "Would you like to enable AI services to start on boot?"

    read -p "Enable AI Manager service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable qwamos-ai-manager.service
        log_success "AI Manager enabled"
    fi

    read -p "Enable Kali GPT service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable qwamos-ai-kali-gpt.service
        log_success "Kali GPT enabled"
    fi

    read -p "Enable Claude service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable qwamos-ai-claude.service
        log_success "Claude enabled"
    fi

    read -p "Enable ChatGPT service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable qwamos-ai-chatgpt.service
        log_success "ChatGPT enabled"
    fi
}

# Start services
start_services() {
    log_info "Would you like to start AI services now?"

    read -p "Start services? (y/n) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Services not started. Start them manually with:"
        log_info "  sudo systemctl start qwamos-ai-manager.service"
        return
    fi

    # Start AI Manager
    systemctl start qwamos-ai-manager.service
    sleep 2

    if systemctl is-active --quiet qwamos-ai-manager.service; then
        log_success "AI Manager started"
    else
        log_error "AI Manager failed to start"
        log_info "Check logs: sudo journalctl -u qwamos-ai-manager.service -n 50"
    fi
}

# Print summary
print_summary() {
    echo
    echo "═══════════════════════════════════════════════════════════"
    echo "  QWAMOS AI Services Deployment Complete"
    echo "═══════════════════════════════════════════════════════════"
    echo
    echo "Installation Summary:"
    echo "  • Backend files: /opt/qwamos/ai/"
    echo "  • Configuration: /opt/qwamos/ai/config/"
    echo "  • Logs: /var/log/qwamos/"
    echo "  • Systemd services: /etc/systemd/system/qwamos-ai-*.service"
    echo
    echo "Next Steps:"
    echo
    echo "1. Configure API keys (for cloud services):"
    echo "   sudo /opt/qwamos/ai/qwamos-ai enable claude --api-key sk-ant-YOUR_KEY"
    echo "   sudo /opt/qwamos/ai/qwamos-ai enable chatgpt --api-key sk-proj-YOUR_KEY"
    echo
    echo "2. Enable Kali GPT (local, no API key needed):"
    echo "   sudo /opt/qwamos/ai/qwamos-ai enable kali-gpt"
    echo
    echo "3. Check service status:"
    echo "   systemctl status qwamos-ai-*.service"
    echo
    echo "4. View logs:"
    echo "   sudo journalctl -u qwamos-ai-manager.service -f"
    echo
    echo "5. Test AI services:"
    echo "   /opt/qwamos/ai/qwamos-ai query kali-gpt 'How do I use nmap?'"
    echo
    echo "Documentation: /opt/qwamos/ai/README.md"
    echo "═══════════════════════════════════════════════════════════"
    echo
}

# Main deployment flow
main() {
    echo
    echo "═══════════════════════════════════════════════════════════"
    echo "  QWAMOS AI Services Deployment"
    echo "═══════════════════════════════════════════════════════════"
    echo

    check_root

    log_info "Starting deployment..."
    echo

    create_directories
    copy_backend_files
    copy_config_files
    install_systemd_services
    set_permissions
    install_dependencies
    download_kali_gpt_model
    enable_services
    start_services

    echo
    log_success "Deployment completed successfully!"
    echo

    print_summary
}

# Run main function
main "$@"
