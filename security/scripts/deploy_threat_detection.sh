#!/bin/bash
#
# QWAMOS Phase 7: ML Threat Detection Deployment Script
#
# This script automates the deployment of QWAMOS ML threat detection system:
# - Creates necessary directories
# - Copies ML detectors and AI response components
# - Installs systemd services
# - Sets up permissions
# - Configures ML models
# - Creates quarantine directories
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

    mkdir -p /opt/qwamos/security/{ml,ai_response,actions,monitors,config,quarantine}
    mkdir -p /opt/qwamos/security/ml/{models,training,data}
    mkdir -p /var/log/qwamos
    mkdir -p /var/run/qwamos

    log_success "Directories created"
}

# Copy ML detection components
copy_ml_components() {
    log_info "Copying ML detection components..."

    # Copy ML detectors
    cp ml/network_anomaly_detector.py /opt/qwamos/security/ml/
    cp ml/file_system_monitor.py /opt/qwamos/security/ml/
    cp ml/system_call_analyzer.py /opt/qwamos/security/ml/

    chmod +x /opt/qwamos/security/ml/*.py

    log_success "ML detectors copied"
}

# Copy AI response components
copy_ai_components() {
    log_info "Copying AI response components..."

    # Copy AI response coordinator
    cp ai_response/ai_response_coordinator.py /opt/qwamos/security/ai_response/

    # Copy action executor
    cp actions/action_executor.py /opt/qwamos/security/actions/

    chmod +x /opt/qwamos/security/ai_response/*.py
    chmod +x /opt/qwamos/security/actions/*.py

    log_success "AI components copied"
}

# Copy helper scripts
copy_scripts() {
    log_info "Copying helper scripts..."

    # Create helper scripts directory
    mkdir -p /opt/qwamos/security/scripts

    # Copy all scripts
    cp scripts/*.py /opt/qwamos/security/scripts/ 2>/dev/null || true

    chmod +x /opt/qwamos/security/scripts/*.py 2>/dev/null || true

    log_success "Helper scripts copied"
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

    # Ensure qwamos user exists
    if ! id -u qwamos > /dev/null 2>&1; then
        useradd -r -s /bin/false qwamos
        log_info "Created qwamos user"
    fi

    # Set ownership
    chown -R qwamos:qwamos /opt/qwamos/security
    chown -R qwamos:qwamos /var/log/qwamos
    chown -R qwamos:qwamos /var/run/qwamos

    # Special permissions for quarantine
    chmod 755 /opt/qwamos/security/quarantine

    # Config directory - protect sensitive data
    chmod 700 /opt/qwamos/security/config

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
        tensorflow-lite \
        numpy \
        scapy \
        watchdog \
        asyncio

    log_success "Python dependencies installed"
}

# Create configuration files
create_config_files() {
    log_info "Creating configuration files..."

    # AI Response Coordinator config
    cat > /opt/qwamos/security/config/ai_response_config.json <<EOF
{
  "auto_response_severity": "MEDIUM",
  "require_permission_above": "HIGH",
  "ai_timeout": 60,
  "max_concurrent_responses": 5,
  "alert_channels": ["log", "ui"],
  "enable_auto_patching": false,
  "enable_network_isolation": true
}
EOF

    # Action Executor config
    cat > /opt/qwamos/security/config/action_executor_config.json <<EOF
{
  "dry_run": false,
  "log_actions": true,
  "backup_before_action": true,
  "max_concurrent_actions": 10,
  "action_timeout": 300,
  "allowed_actions": [
    "firewall",
    "kill_process",
    "network_isolation",
    "vm_snapshot",
    "quarantine_file",
    "patch"
  ]
}
EOF

    # User permissions
    cat > /opt/qwamos/security/config/permissions.json <<EOF
{
  "auto_isolate_vm": true,
  "auto_block_ip": true,
  "auto_kill_process": false,
  "auto_patch": false,
  "auto_snapshot": true
}
EOF

    chown qwamos:qwamos /opt/qwamos/security/config/*.json
    chmod 600 /opt/qwamos/security/config/*.json

    log_success "Configuration files created"
}

# Download ML models (placeholders)
download_ml_models() {
    log_info "Checking for ML models..."

    MODELS_DIR="/opt/qwamos/security/ml/models"

    # Check if models exist
    if [[ -f "$MODELS_DIR/network_ae.tflite" ]] && \
       [[ -f "$MODELS_DIR/file_classifier.tflite" ]] && \
       [[ -f "$MODELS_DIR/syscall_lstm.tflite" ]]; then
        log_success "ML models already present"
        return
    fi

    log_warning "ML models not found"
    log_info "Models need to be trained or downloaded separately"
    log_info "Expected models:"
    log_info "  - $MODELS_DIR/network_ae.tflite (Network Anomaly Autoencoder)"
    log_info "  - $MODELS_DIR/file_classifier.tflite (File System Random Forest)"
    log_info "  - $MODELS_DIR/syscall_lstm.tflite (System Call LSTM)"
    log_info ""
    log_info "The detectors will run in rule-based mode until models are available."
    log_info "To train models, run: /opt/qwamos/security/ml/training/train_models.sh"
}

# Enable and start services
enable_services() {
    log_info "Would you like to enable ML detection services to start on boot?"

    read -p "Enable Network Anomaly Detector? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable qwamos-ml-network-anomaly.service
        log_success "Network Anomaly Detector enabled"
    fi

    read -p "Enable File System Monitor? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable qwamos-ml-file-system.service
        log_success "File System Monitor enabled"
    fi

    read -p "Enable System Call Analyzer? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable qwamos-ml-system-call.service
        log_success "System Call Analyzer enabled"
    fi

    read -p "Enable AI Response Coordinator? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl enable qwamos-ai-response.service
        log_success "AI Response Coordinator enabled"
    fi
}

# Start services
start_services() {
    log_info "Would you like to start ML detection services now?"

    read -p "Start services? (y/n) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Services not started. Start them manually with:"
        log_info "  sudo systemctl start qwamos-ml-network-anomaly.service"
        log_info "  sudo systemctl start qwamos-ml-file-system.service"
        log_info "  sudo systemctl start qwamos-ml-system-call.service"
        log_info "  sudo systemctl start qwamos-ai-response.service"
        return
    fi

    # Start services
    log_info "Starting ML detection services..."

    # Note: May fail if ML models not present
    systemctl start qwamos-ai-response.service || log_warning "AI Response failed to start"
    sleep 2

    systemctl start qwamos-ml-network-anomaly.service || log_warning "Network Anomaly failed to start"
    systemctl start qwamos-ml-file-system.service || log_warning "File System Monitor failed to start"
    systemctl start qwamos-ml-system-call.service || log_warning "System Call Analyzer failed to start"

    sleep 2

    # Check status
    log_info "Checking service status..."
    systemctl is-active --quiet qwamos-ml-network-anomaly.service && log_success "Network Anomaly Detector: Active" || log_warning "Network Anomaly Detector: Inactive"
    systemctl is-active --quiet qwamos-ml-file-system.service && log_success "File System Monitor: Active" || log_warning "File System Monitor: Inactive"
    systemctl is-active --quiet qwamos-ml-system-call.service && log_success "System Call Analyzer: Active" || log_warning "System Call Analyzer: Inactive"
    systemctl is-active --quiet qwamos-ai-response.service && log_success "AI Response Coordinator: Active" || log_warning "AI Response Coordinator: Inactive"
}

# Print summary
print_summary() {
    echo
    echo "═══════════════════════════════════════════════════════════"
    echo "  QWAMOS Phase 7: ML Threat Detection Deployment Complete"
    echo "═══════════════════════════════════════════════════════════"
    echo
    echo "Installation Summary:"
    echo "  • ML Detectors: /opt/qwamos/security/ml/"
    echo "  • AI Response: /opt/qwamos/security/ai_response/"
    echo "  • Action Executor: /opt/qwamos/security/actions/"
    echo "  • Configuration: /opt/qwamos/security/config/"
    echo "  • Quarantine: /opt/qwamos/security/quarantine/"
    echo "  • Logs: /var/log/qwamos/"
    echo "  • Systemd Services: /etc/systemd/system/qwamos-ml-*.service"
    echo
    echo "Installed Services:"
    echo "  • qwamos-ml-network-anomaly.service - Network threat detection"
    echo "  • qwamos-ml-file-system.service - File system monitoring"
    echo "  • qwamos-ml-system-call.service - System call analysis"
    echo "  • qwamos-ai-response.service - AI-powered response coordination"
    echo
    echo "Next Steps:"
    echo
    echo "1. Check service status:"
    echo "   systemctl status qwamos-ml-*.service"
    echo
    echo "2. View logs:"
    echo "   sudo journalctl -u qwamos-ml-network-anomaly.service -f"
    echo "   sudo journalctl -u qwamos-ml-file-system.service -f"
    echo
    echo "3. Train ML models (if not already trained):"
    echo "   /opt/qwamos/security/ml/training/train_models.sh"
    echo
    echo "4. Configure permissions:"
    echo "   Edit: /opt/qwamos/security/config/permissions.json"
    echo
    echo "5. Test threat detection:"
    echo "   # Watch for threats in real-time"
    echo "   sudo journalctl -f -u 'qwamos-ml-*'"
    echo
    echo "6. Access React Native UI:"
    echo "   # Open ThreatDashboard screen in QWAMOS app"
    echo
    echo "Documentation: /opt/qwamos/docs/PHASE7_THREAT_DETECTION_GUIDE.md"
    echo "═══════════════════════════════════════════════════════════"
    echo
}

# Main deployment flow
main() {
    echo
    echo "═══════════════════════════════════════════════════════════"
    echo "  QWAMOS Phase 7: ML Threat Detection Deployment"
    echo "═══════════════════════════════════════════════════════════"
    echo

    check_root

    log_info "Starting deployment..."
    echo

    create_directories
    copy_ml_components
    copy_ai_components
    copy_scripts
    install_systemd_services
    set_permissions
    install_dependencies
    create_config_files
    download_ml_models
    enable_services
    start_services

    echo
    log_success "Deployment completed successfully!"
    echo

    print_summary
}

# Run main function
main "$@"
