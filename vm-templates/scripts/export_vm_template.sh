#!/usr/bin/env bash
# Export and prepare QWAMOS VM templates for distribution
# Handles compression, checksums, and release preparation

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VM_TEMPLATES_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${VM_TEMPLATES_DIR}/output/templates"
EXPORT_DIR="${VM_TEMPLATES_DIR}/output/release"

echo "========================================"
echo "QWAMOS VM Template Exporter"
echo "========================================"

# Create export directory
mkdir -p "${EXPORT_DIR}"

# Function to export single template
export_template() {
    local TEMPLATE_FILE="$1"
    local TEMPLATE_NAME=$(basename "$TEMPLATE_FILE" .tar.gz)

    echo ""
    echo "Exporting: $TEMPLATE_NAME"
    echo "---"

    if [ ! -f "$TEMPLATE_FILE" ]; then
        echo "✗ Template not found: $TEMPLATE_FILE"
        return 1
    fi

    # Copy to export directory
    cp "$TEMPLATE_FILE" "${EXPORT_DIR}/"

    # Generate SHA256 checksum
    if command -v sha256sum &> /dev/null; then
        cd "${EXPORT_DIR}"
        sha256sum "$(basename "$TEMPLATE_FILE")" > "$(basename "$TEMPLATE_FILE").sha256"
        echo "✓ SHA256 checksum generated"
    fi

    # Generate SHA512 checksum (additional security)
    if command -v sha512sum &> /dev/null; then
        cd "${EXPORT_DIR}"
        sha512sum "$(basename "$TEMPLATE_FILE")" > "$(basename "$TEMPLATE_FILE").sha512"
        echo "✓ SHA512 checksum generated"
    fi

    # Get file size
    FILE_SIZE=$(stat -f%z "$TEMPLATE_FILE" 2>/dev/null || stat -c%s "$TEMPLATE_FILE" 2>/dev/null || echo "0")
    SIZE_MB=$((FILE_SIZE / 1024 / 1024))
    echo "✓ Size: ${SIZE_MB}MB"

    # Try to compress further with xz (better compression)
    if command -v xz &> /dev/null && [ ! -f "${EXPORT_DIR}/$(basename "$TEMPLATE_FILE" .tar.gz).tar.xz" ]; then
        echo "Creating XZ compressed version..."
        cd "${EXPORT_DIR}"

        # Extract, then recompress with xz
        TEMP_DIR=$(mktemp -d)
        tar xzf "$(basename "$TEMPLATE_FILE")" -C "$TEMP_DIR"
        tar cJf "$(basename "$TEMPLATE_FILE" .tar.gz).tar.xz" -C "$TEMP_DIR" .
        rm -rf "$TEMP_DIR"

        # Generate checksum for xz
        sha256sum "$(basename "$TEMPLATE_FILE" .tar.gz).tar.xz" > "$(basename "$TEMPLATE_FILE" .tar.gz).tar.xz.sha256"

        XZ_SIZE=$(stat -f%z "$(basename "$TEMPLATE_FILE" .tar.gz).tar.xz" 2>/dev/null || stat -c%s "$(basename "$TEMPLATE_FILE" .tar.gz).tar.xz" 2>/dev/null || echo "0")
        XZ_SIZE_MB=$((XZ_SIZE / 1024 / 1024))
        SAVED=$((SIZE_MB - XZ_SIZE_MB))

        echo "✓ XZ version: ${XZ_SIZE_MB}MB (saved ${SAVED}MB)"
    fi

    echo "✓ Export complete: $TEMPLATE_NAME"
}

# Export all templates
echo "Scanning for templates in: $OUTPUT_DIR"
echo ""

TEMPLATE_COUNT=0

for template in "${OUTPUT_DIR}"/*.tar.gz; do
    if [ -f "$template" ]; then
        export_template "$template"
        ((TEMPLATE_COUNT++))
    fi
done

if [ $TEMPLATE_COUNT -eq 0 ]; then
    echo "⚠️  No templates found to export"
    exit 1
fi

# Generate release manifest
echo ""
echo "Generating release manifest..."

MANIFEST_FILE="${EXPORT_DIR}/MANIFEST.txt"
cat > "$MANIFEST_FILE" << EOF
QWAMOS VM Templates - Release Manifest
Generated: $(date -Iseconds)
Version: 1.2.0

Templates Included:
EOF

cd "${EXPORT_DIR}"
for template in *.tar.gz; do
    if [ -f "$template" ]; then
        SIZE=$(stat -f%z "$template" 2>/dev/null || stat -c%s "$template" 2>/dev/null || echo "0")
        SIZE_MB=$((SIZE / 1024 / 1024))
        SHA256=$(cat "${template}.sha256" 2>/dev/null | cut -d' ' -f1 || echo "N/A")

        cat >> "$MANIFEST_FILE" << EOF

- $template
  Size: ${SIZE_MB}MB
  SHA256: $SHA256
EOF
    fi
done

cat >> "$MANIFEST_FILE" << EOF

Installation:
1. Download desired template
2. Verify checksum:
   sha256sum -c <template>.tar.gz.sha256
3. Extract:
   tar xzf <template>.tar.gz
4. Follow template-specific README

For more information, visit:
https://github.com/Dezirae-Stark/QWAMOS

EOF

echo "✓ Manifest created: $MANIFEST_FILE"

# Generate checksums file (all in one)
echo ""
echo "Generating combined checksums file..."

CHECKSUMS_FILE="${EXPORT_DIR}/SHA256SUMS"
rm -f "$CHECKSUMS_FILE"

cd "${EXPORT_DIR}"
for file in *.tar.gz *.tar.xz MANIFEST.txt; do
    if [ -f "$file" ]; then
        sha256sum "$file" >> "$CHECKSUMS_FILE"
    fi
done

echo "✓ Combined checksums: $CHECKSUMS_FILE"

# Create release notes template
RELEASE_NOTES="${EXPORT_DIR}/RELEASE_NOTES.md"
cat > "$RELEASE_NOTES" << 'EOF'
# QWAMOS VM Templates Release

## 📦 Available Templates

### QEMU Template
- **File**: `qwamos-qemu-template.tar.gz`
- **Use Case**: Full virtualization with hardware acceleration
- **Requirements**: QEMU 5.0+, KVM support (optional)
- **Recommended**: 2GB RAM, 8GB storage

### PRoot Template
- **File**: `qwamos-proot-template.tar.gz`
- **Use Case**: Userspace virtualization, no root required
- **Requirements**: PRoot 5.1+
- **Recommended**: 1GB RAM, 2GB storage
- **Best For**: Android/Termux environments

### Chroot Template
- **File**: `qwamos-chroot-template.tar.gz`
- **Use Case**: Lightweight isolation with namespaces
- **Requirements**: Linux kernel 3.8+, root access
- **Recommended**: 1GB RAM, 2GB storage

## 🔐 Security Features

All templates include:
- ✅ Post-Quantum Cryptography (Kyber-1024, ChaCha20-Poly1305, BLAKE3)
- ✅ Network isolation and gateway mode
- ✅ Encrypted storage support
- ✅ Secure boot configuration

## 📥 Download & Verify

```bash
# Download template
wget https://github.com/Dezirae-Stark/QWAMOS/releases/download/v1.2.0/qwamos-<type>-template.tar.gz

# Verify checksum
sha256sum -c qwamos-<type>-template.tar.gz.sha256

# Extract
tar xzf qwamos-<type>-template.tar.gz

# Launch (follow template-specific instructions)
```

## 📝 Usage

See individual template README files for specific usage instructions.

## 🐛 Issues

Report issues at: https://github.com/Dezirae-Stark/QWAMOS/issues

## 📄 License

AGPL-3.0 - See LICENSE file
EOF

echo "✓ Release notes template: $RELEASE_NOTES"

# Generate upload script for GitHub releases
UPLOAD_SCRIPT="${EXPORT_DIR}/upload-to-release.sh"
cat > "$UPLOAD_SCRIPT" << 'EOF'
#!/bin/bash
# Upload templates to GitHub Release
# Usage: ./upload-to-release.sh <release-tag>

set -e

RELEASE_TAG="${1:-v1.2.0}"

if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) not installed"
    echo "Install: https://cli.github.com/"
    exit 1
fi

echo "Uploading templates to release: $RELEASE_TAG"
echo ""

# Upload all templates
for file in *.tar.gz *.tar.xz *.sha256 *.sha512 SHA256SUMS MANIFEST.txt RELEASE_NOTES.md; do
    if [ -f "$file" ]; then
        echo "Uploading: $file"
        gh release upload "$RELEASE_TAG" "$file" --clobber
    fi
done

echo ""
echo "✅ Upload complete!"
echo "View release: gh release view $RELEASE_TAG --web"
EOF

chmod +x "$UPLOAD_SCRIPT"
echo "✓ Upload script created: $UPLOAD_SCRIPT"

# Final summary
echo ""
echo "========================================"
echo "Export Summary"
echo "========================================"
echo "Templates exported: $TEMPLATE_COUNT"
echo "Export directory: $EXPORT_DIR"
echo ""
echo "Files created:"
ls -lh "${EXPORT_DIR}" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "✅ Export complete!"
echo ""
echo "Next steps:"
echo "  1. Review MANIFEST.txt and RELEASE_NOTES.md"
echo "  2. Test templates with validate_vm_template.sh"
echo "  3. Upload to GitHub Release:"
echo "     cd $EXPORT_DIR"
echo "     ./upload-to-release.sh v1.2.0"
echo ""
