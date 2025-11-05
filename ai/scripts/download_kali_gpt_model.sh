#!/bin/bash
#
# Download Kali GPT Model (Llama 3.1 8B Quantized)
#
# This script downloads the Kali GPT language model from HuggingFace
# Model: Llama 3.1 8B Q4_K_M quantized (~4.5GB)
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
MODEL_DIR="/opt/qwamos/ai/kali_gpt/models"
MODEL_FILE="llama-3.1-8b-q4.gguf"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"
MODEL_URL="https://huggingface.co/TheBloke/Llama-2-13B-GGUF/resolve/main/llama-2-13b.Q4_K_M.gguf"
EXPECTED_SIZE=4500000000  # ~4.5GB

# Alternative models (different sizes/quality)
declare -A MODELS=(
    ["Q2_K"]="https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q2_K.gguf"
    ["Q3_K_M"]="https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q3_K_M.gguf"
    ["Q4_K_M"]="https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q4_K_M.gguf"
    ["Q5_K_M"]="https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q5_K_M.gguf"
    ["Q8_0"]="https://huggingface.co/TheBloke/Llama-3.1-8B-GGUF/resolve/main/llama-3.1-8b.Q8_0.gguf"
)

declare -A MODEL_SIZES=(
    ["Q2_K"]="2.8GB - Lowest quality, fastest inference"
    ["Q3_K_M"]="3.5GB - Low quality, fast inference"
    ["Q4_K_M"]="4.5GB - Good quality, balanced (RECOMMENDED)"
    ["Q5_K_M"]="5.5GB - High quality, slower inference"
    ["Q8_0"]="8.5GB - Highest quality, slowest inference"
)

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    log_error "This script must be run as root"
    log_info "Usage: sudo $0"
    exit 1
fi

# Create model directory
mkdir -p "$MODEL_DIR"

# Check if model already exists
if [[ -f "$MODEL_PATH" ]]; then
    log_warning "Model file already exists: $MODEL_PATH"
    MODEL_SIZE=$(stat -c%s "$MODEL_PATH")
    log_info "Current size: $(numfmt --to=iec-i --suffix=B $MODEL_SIZE)"

    read -p "Re-download model? (y/n) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Keeping existing model"
        exit 0
    fi

    log_info "Backing up existing model..."
    mv "$MODEL_PATH" "$MODEL_PATH.backup"
fi

# Model selection
echo
echo "═══════════════════════════════════════════════════════════"
echo "  Kali GPT Model Selection"
echo "═══════════════════════════════════════════════════════════"
echo
echo "Available models (quantization levels):"
echo
for quant in Q2_K Q3_K_M Q4_K_M Q5_K_M Q8_0; do
    if [[ "$quant" == "Q4_K_M" ]]; then
        echo "  [$quant] ${MODEL_SIZES[$quant]} ⭐ RECOMMENDED"
    else
        echo "  [$quant] ${MODEL_SIZES[$quant]}"
    fi
done
echo
log_info "Q4_K_M offers the best balance of quality and performance"
echo

read -p "Select quantization [Q4_K_M]: " SELECTED_QUANT
SELECTED_QUANT=${SELECTED_QUANT:-Q4_K_M}

if [[ ! -v "MODELS[$SELECTED_QUANT]" ]]; then
    log_error "Invalid selection: $SELECTED_QUANT"
    exit 1
fi

MODEL_URL="${MODELS[$SELECTED_QUANT]}"
MODEL_FILE="llama-3.1-8b-${SELECTED_QUANT,,}.gguf"
MODEL_PATH="$MODEL_DIR/$MODEL_FILE"

log_info "Selected: $SELECTED_QUANT (${MODEL_SIZES[$SELECTED_QUANT]})"

# Check disk space
AVAILABLE_SPACE=$(df -B1 "$MODEL_DIR" | awk 'NR==2 {print $4}')
REQUIRED_SPACE=10000000000  # 10GB to be safe

if [[ $AVAILABLE_SPACE -lt $REQUIRED_SPACE ]]; then
    log_error "Insufficient disk space"
    log_info "Available: $(numfmt --to=iec-i --suffix=B $AVAILABLE_SPACE)"
    log_info "Required: ~10GB"
    exit 1
fi

log_success "Disk space check passed ($(numfmt --to=iec-i --suffix=B $AVAILABLE_SPACE) available)"

# Check network connectivity
log_info "Testing network connectivity..."

if ! ping -c 1 -W 5 huggingface.co &> /dev/null; then
    log_error "Cannot reach huggingface.co"
    log_info "Please check your internet connection"
    exit 1
fi

log_success "Network connectivity OK"

# Download model
echo
log_info "Downloading Kali GPT model..."
log_info "URL: $MODEL_URL"
log_info "Destination: $MODEL_PATH"
log_warning "This may take 10-30 minutes depending on your connection"
echo

cd "$MODEL_DIR"

# Use wget with resume support and progress bar
wget --continue \
     --progress=bar:force \
     --show-progress \
     --timeout=30 \
     --tries=5 \
     --retry-connrefused \
     "$MODEL_URL" \
     -O "$MODEL_FILE"

# Verify download
if [[ ! -f "$MODEL_PATH" ]]; then
    log_error "Download failed - file not found"
    exit 1
fi

DOWNLOADED_SIZE=$(stat -c%s "$MODEL_PATH")
log_info "Downloaded: $(numfmt --to=iec-i --suffix=B $DOWNLOADED_SIZE)"

# Basic validation (check if file is at least 1GB)
if [[ $DOWNLOADED_SIZE -lt 1000000000 ]]; then
    log_error "Downloaded file is too small - may be corrupted"
    log_info "Expected: ~${MODEL_SIZES[$SELECTED_QUANT]}"
    log_info "Got: $(numfmt --to=iec-i --suffix=B $DOWNLOADED_SIZE)"
    exit 1
fi

log_success "Model downloaded successfully!"

# Set permissions
chown qwamos:qwamos "$MODEL_PATH"
chmod 644 "$MODEL_PATH"

log_success "Permissions set"

# Update configuration
CONFIG_FILE="/opt/qwamos/ai/config/kali_gpt_config.json"

if [[ -f "$CONFIG_FILE" ]]; then
    log_info "Updating configuration..."

    # Update model_path in config
    python3 -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
config['model_path'] = '$MODEL_PATH'
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
"
    log_success "Configuration updated"
fi

# Clean up backup if exists
if [[ -f "$MODEL_PATH.backup" ]]; then
    log_info "Removing backup..."
    rm "$MODEL_PATH.backup"
fi

# Test model loading (optional)
echo
read -p "Test model loading? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Testing model loading..."

    python3 << EOF
import sys
try:
    from llama_cpp import Llama
    llm = Llama(model_path="$MODEL_PATH", n_ctx=512, n_threads=2)
    print("✅ Model loaded successfully!")
    print(f"   Context length: {llm.n_ctx()}")
    print(f"   Vocab size: {llm.n_vocab()}")
except Exception as e:
    print(f"❌ Model loading failed: {e}", file=sys.stderr)
    sys.exit(1)
EOF

    if [[ $? -eq 0 ]]; then
        log_success "Model test passed"
    else
        log_error "Model test failed"
        log_info "The model file may be corrupted. Try re-downloading."
        exit 1
    fi
fi

# Summary
echo
echo "═══════════════════════════════════════════════════════════"
echo "  Kali GPT Model Download Complete"
echo "═══════════════════════════════════════════════════════════"
echo
echo "Model Details:"
echo "  File: $MODEL_FILE"
echo "  Path: $MODEL_PATH"
echo "  Size: $(numfmt --to=iec-i --suffix=B $DOWNLOADED_SIZE)"
echo "  Quantization: $SELECTED_QUANT"
echo
echo "Next Steps:"
echo
echo "1. Enable Kali GPT service:"
echo "   /opt/qwamos/ai/qwamos-ai enable kali-gpt"
echo
echo "2. Start the service:"
echo "   sudo systemctl start qwamos-ai-kali-gpt.service"
echo
echo "3. Test Kali GPT:"
echo "   /opt/qwamos/ai/qwamos-ai query kali-gpt 'How do I use nmap?'"
echo
echo "4. Check service status:"
echo "   systemctl status qwamos-ai-kali-gpt.service"
echo
echo "═══════════════════════════════════════════════════════════"
echo

log_success "Model ready for use!"
