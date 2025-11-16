#!/bin/bash

# QWAMOS Demo Animation Video Generator
# This script helps generate MP4 and GIF files from the HTML animation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HTML_FILE="$SCRIPT_DIR/qwamos-demo.html"
OUTPUT_DIR="$SCRIPT_DIR/output"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}QWAMOS Demo Animation Video Generator${NC}"
echo "========================================"
echo ""

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: FFmpeg is not installed${NC}"
    echo "Please install FFmpeg:"
    echo "  - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  - macOS: brew install ffmpeg"
    echo "  - Windows: Download from https://ffmpeg.org/"
    exit 1
fi

echo -e "${YELLOW}Note: This script requires manual screen recording${NC}"
echo "Please follow these steps:"
echo ""
echo "1. Open qwamos-demo.html in your browser"
echo "   File location: $HTML_FILE"
echo ""
echo "2. Record the screen for 10 seconds using:"
echo "   - OBS Studio (recommended)"
echo "   - Built-in screen recorder"
echo "   - FFmpeg screen capture"
echo ""
echo "3. Save the recording as: $OUTPUT_DIR/qwamos-demo.mp4"
echo ""
read -p "Press Enter when you have the MP4 file ready..."

# Check if MP4 exists
if [ ! -f "$OUTPUT_DIR/qwamos-demo.mp4" ]; then
    echo -e "${RED}Error: MP4 file not found at $OUTPUT_DIR/qwamos-demo.mp4${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}MP4 file found! Generating GIF versions...${NC}"
echo ""

# Generate high-quality GIF (for desktop viewing)
echo "Generating high-quality GIF (720p, 30fps)..."
ffmpeg -i "$OUTPUT_DIR/qwamos-demo.mp4" \
    -vf "fps=30,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5" \
    -loop 0 -y "$OUTPUT_DIR/qwamos-demo.gif" 2>&1 | grep -v "frame=" || true

echo -e "${GREEN}✓ High-quality GIF created${NC}"

# Generate optimized GIF (for GitHub README)
echo "Generating optimized GIF (540p, 20fps)..."
ffmpeg -i "$OUTPUT_DIR/qwamos-demo.mp4" \
    -vf "fps=20,scale=540:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4" \
    -loop 0 -y "$OUTPUT_DIR/qwamos-demo-optimized.gif" 2>&1 | grep -v "frame=" || true

echo -e "${GREEN}✓ Optimized GIF created${NC}"

# Generate thumbnail
echo "Generating thumbnail image..."
ffmpeg -i "$OUTPUT_DIR/qwamos-demo.mp4" \
    -ss 00:00:05 -vframes 1 -vf "scale=1920:-1" \
    -y "$OUTPUT_DIR/qwamos-demo-thumbnail.png" 2>&1 | grep -v "frame=" || true

echo -e "${GREEN}✓ Thumbnail created${NC}"

# Display file sizes
echo ""
echo "======================================"
echo "Output Files:"
echo "======================================"
ls -lh "$OUTPUT_DIR" | grep -E "\.(mp4|gif|png)$" | awk '{printf "%-40s %8s\n", $9, $5}'

echo ""
echo -e "${GREEN}Done! Files are in: $OUTPUT_DIR${NC}"
echo ""
echo "Next steps:"
echo "1. Review the generated files"
echo "2. Upload to GitHub releases:"
echo "   gh release create v1.0.0 $OUTPUT_DIR/qwamos-demo.* --title 'Demo Animation'"
echo "3. Update README.md with the GIF URL"
echo ""
