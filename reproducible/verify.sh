#!/bin/bash
#
# QWAMOS Reproducible Build Verification Script
# Rebuilds APK and verifies reproducibility
#

set -e
set -o pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/output/apk"
REPORT_DIR="$SCRIPT_DIR/output/reports"
LOG_DIR="$SCRIPT_DIR/output/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_DIR/verify.log"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_DIR/verify.log"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_DIR/verify.log"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_DIR/verify.log"
}

# Create output directories
mkdir -p "$OUTPUT_DIR" "$REPORT_DIR" "$LOG_DIR"

log_info "=== QWAMOS Reproducible Build Verification ==="
log_info "Verification started: $(date -u)"

# Install dependencies if needed
install_dependencies() {
    log_info "Checking dependencies..."

    # Check for diffoscope
    if ! command -v diffoscope >/dev/null 2>&1; then
        log_warning "diffoscope not found, attempting to install..."

        if command -v pip3 >/dev/null 2>&1; then
            pip3 install diffoscope || {
                log_warning "Failed to install diffoscope via pip3"
                log_warning "Binary diff comparison will be limited"
            }
        elif command -v apt-get >/dev/null 2>&1; then
            sudo apt-get update && sudo apt-get install -y diffoscope || {
                log_warning "Failed to install diffoscope via apt"
            }
        else
            log_warning "Cannot install diffoscope automatically"
        fi
    else
        log_success "diffoscope found: $(diffoscope --version | head -1)"
    fi

    # Check for apktool
    if ! command -v apktool >/dev/null 2>&1; then
        log_warning "apktool not found, APK analysis will be limited"
    fi
}

install_dependencies

# Step 1: Build first APK
log_info ""
log_info "=== Step 1: Building First APK ==="

"$SCRIPT_DIR/build.sh" 1 || {
    log_error "First build failed"
    exit 1
}

# Find first build APK
APK_BUILD1=$(find "$OUTPUT_DIR" -name "qwamos-build1-*.apk" -type f | head -n 1)

if [ -z "$APK_BUILD1" ]; then
    log_error "First build APK not found"
    exit 1
fi

log_success "First build completed: $(basename "$APK_BUILD1")"

# Get first build checksums
SHA256_BUILD1=$(cat "$APK_BUILD1.sha256" | awk '{print $1}')
log_info "Build 1 SHA-256: $SHA256_BUILD1"

# Wait a moment to ensure different build time
sleep 2

# Step 2: Build second APK
log_info ""
log_info "=== Step 2: Building Second APK (Verification Build) ==="

"$SCRIPT_DIR/build.sh" 2 || {
    log_error "Second build failed"
    exit 1
}

# Find second build APK
APK_BUILD2=$(find "$OUTPUT_DIR" -name "qwamos-build2-*.apk" -type f | head -n 1)

if [ -z "$APK_BUILD2" ]; then
    log_error "Second build APK not found"
    exit 1
fi

log_success "Second build completed: $(basename "$APK_BUILD2")"

# Get second build checksums
SHA256_BUILD2=$(cat "$APK_BUILD2.sha256" | awk '{print $1}')
log_info "Build 2 SHA-256: $SHA256_BUILD2"

# Step 3: Compare checksums
log_info ""
log_info "=== Step 3: SHA-256 Hash Comparison ==="

if [ "$SHA256_BUILD1" = "$SHA256_BUILD2" ]; then
    log_success "✅ SHA-256 MATCH! Builds are byte-for-byte identical"
    REPRODUCIBLE=true
else
    log_error "❌ SHA-256 MISMATCH! Builds differ"
    log_error "Build 1: $SHA256_BUILD1"
    log_error "Build 2: $SHA256_BUILD2"
    REPRODUCIBLE=false
fi

# Step 4: Binary comparison
log_info ""
log_info "=== Step 4: Binary Comparison ==="

# Simple binary diff
if cmp -s "$APK_BUILD1" "$APK_BUILD2"; then
    log_success "✅ Binary comparison: IDENTICAL"
else
    log_warning "⚠️  Binary comparison: DIFFERENT"

    # Show byte-level differences
    if command -v xxd >/dev/null 2>&1; then
        log_info "First 100 differing bytes:"
        diff -u <(xxd "$APK_BUILD1" | head -100) <(xxd "$APK_BUILD2" | head -100) | head -50 > "$REPORT_DIR/binary-diff-sample.txt" || true
    fi
fi

# Step 5: File size comparison
log_info ""
log_info "=== Step 5: File Size Comparison ==="

SIZE_BUILD1=$(stat -c%s "$APK_BUILD1")
SIZE_BUILD2=$(stat -c%s "$APK_BUILD2")

log_info "Build 1 size: $SIZE_BUILD1 bytes ($(numfmt --to=iec-i --suffix=B $SIZE_BUILD1))"
log_info "Build 2 size: $SIZE_BUILD2 bytes ($(numfmt --to=iec-i --suffix=B $SIZE_BUILD2))"

if [ "$SIZE_BUILD1" -eq "$SIZE_BUILD2" ]; then
    log_success "✅ File sizes match"
else
    SIZE_DIFF=$((SIZE_BUILD1 - SIZE_BUILD2))
    log_warning "⚠️  File sizes differ by $SIZE_DIFF bytes"
fi

# Step 6: APK structure analysis
log_info ""
log_info "=== Step 6: APK Structure Analysis ==="

# Extract APKs
EXTRACT_DIR1="$REPORT_DIR/build1_extracted"
EXTRACT_DIR2="$REPORT_DIR/build2_extracted"

mkdir -p "$EXTRACT_DIR1" "$EXTRACT_DIR2"

log_info "Extracting APK contents..."
unzip -q "$APK_BUILD1" -d "$EXTRACT_DIR1" 2>&1 | tee -a "$LOG_DIR/verify.log" || true
unzip -q "$APK_BUILD2" -d "$EXTRACT_DIR2" 2>&1 | tee -a "$LOG_DIR/verify.log" || true

# Compare file lists
log_info "Comparing file lists..."

(cd "$EXTRACT_DIR1" && find . -type f | sort) > "$REPORT_DIR/build1-files.txt"
(cd "$EXTRACT_DIR2" && find . -type f | sort) > "$REPORT_DIR/build2-files.txt"

if diff -u "$REPORT_DIR/build1-files.txt" "$REPORT_DIR/build2-files.txt" > "$REPORT_DIR/file-list-diff.txt"; then
    log_success "✅ File lists are identical"
else
    log_warning "⚠️  File lists differ"
    log_info "Differences saved to: $REPORT_DIR/file-list-diff.txt"
fi

# Check file ordering in ZIP
log_info "Checking file ordering..."

unzip -l "$APK_BUILD1" | awk '{print $4}' | grep -v "^$" | tail -n +4 > "$REPORT_DIR/build1-order.txt" || true
unzip -l "$APK_BUILD2" | awk '{print $4}' | grep -v "^$" | tail -n +4 > "$REPORT_DIR/build2-order.txt" || true

if diff -u "$REPORT_DIR/build1-order.txt" "$REPORT_DIR/build2-order.txt" > "$REPORT_DIR/file-order-diff.txt"; then
    log_success "✅ File ordering is consistent"
else
    log_warning "⚠️  File ordering differs (may affect reproducibility)"
fi

# Step 7: Timestamp detection
log_info ""
log_info "=== Step 7: Timestamp Detection ==="

log_info "Checking for embedded timestamps..."

# Check ZIP timestamps
log_info "ZIP entry timestamps (Build 1):"
unzip -l "$APK_BUILD1" | head -20 | tee -a "$LOG_DIR/verify.log"

# Search for timestamp patterns in extracted files
log_info "Searching for timestamp strings..."

TIMESTAMPS_FOUND=false

for file in $(find "$EXTRACT_DIR1" -type f -name "*.xml" -o -name "*.properties" -o -name "*.MF"); do
    if grep -iE "([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{10,13}|timestamp|buildtime)" "$file" 2>/dev/null | head -5 >> "$REPORT_DIR/timestamps-found.txt"; then
        TIMESTAMPS_FOUND=true
    fi
done

if [ "$TIMESTAMPS_FOUND" = true ]; then
    log_warning "⚠️  Potential timestamps found in APK contents"
    log_info "See: $REPORT_DIR/timestamps-found.txt"
else
    log_success "✅ No obvious timestamp strings found"
fi

# Step 8: Diffoscope analysis (comprehensive)
log_info ""
log_info "=== Step 8: Diffoscope Analysis ==="

if command -v diffoscope >/dev/null 2>&1; then
    log_info "Running diffoscope (this may take a few minutes)..."

    diffoscope \
        --max-report-size 50M \
        --html "$REPORT_DIR/diffoscope-report.html" \
        --text "$REPORT_DIR/diffoscope-report.txt" \
        --json "$REPORT_DIR/diffoscope-report.json" \
        "$APK_BUILD1" "$APK_BUILD2" 2>&1 | tee -a "$LOG_DIR/verify.log" || {
        DIFFOSCOPE_EXIT=$?

        if [ $DIFFOSCOPE_EXIT -eq 0 ]; then
            log_success "✅ Diffoscope: No differences found"
        elif [ $DIFFOSCOPE_EXIT -eq 1 ]; then
            log_warning "⚠️  Diffoscope: Differences detected"
            log_info "HTML report: $REPORT_DIR/diffoscope-report.html"
            log_info "Text report: $REPORT_DIR/diffoscope-report.txt"
        else
            log_error "Diffoscope failed with exit code $DIFFOSCOPE_EXIT"
        fi
    }
else
    log_warning "Diffoscope not available, skipping detailed analysis"
fi

# Step 9: Generate verification report
log_info ""
log_info "=== Step 9: Generating Verification Report ==="

cat > "$REPORT_DIR/verification-report.json" <<EOF
{
  "verification_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "reproducible": $REPRODUCIBLE,
  "builds": {
    "build1": {
      "apk": "$(basename "$APK_BUILD1")",
      "sha256": "$SHA256_BUILD1",
      "size_bytes": $SIZE_BUILD1
    },
    "build2": {
      "apk": "$(basename "$APK_BUILD2")",
      "sha256": "$SHA256_BUILD2",
      "size_bytes": $SIZE_BUILD2
    }
  },
  "checks": {
    "sha256_match": $([ "$SHA256_BUILD1" = "$SHA256_BUILD2" ] && echo "true" || echo "false"),
    "size_match": $([ "$SIZE_BUILD1" -eq "$SIZE_BUILD2" ] && echo "true" || echo "false"),
    "binary_identical": $(cmp -s "$APK_BUILD1" "$APK_BUILD2" && echo "true" || echo "false")
  },
  "reports": {
    "diffoscope_html": "diffoscope-report.html",
    "diffoscope_text": "diffoscope-report.txt",
    "file_list_diff": "file-list-diff.txt",
    "file_order_diff": "file-order-diff.txt",
    "timestamps_found": "timestamps-found.txt"
  }
}
EOF

log_success "Verification report created: $REPORT_DIR/verification-report.json"

# Step 10: Final summary
log_info ""
log_info "=== Verification Summary ==="
log_info "Build 1: $(basename "$APK_BUILD1")"
log_info "Build 2: $(basename "$APK_BUILD2")"
log_info ""

if [ "$REPRODUCIBLE" = true ]; then
    log_success "✅✅✅ REPRODUCIBLE BUILD VERIFIED ✅✅✅"
    log_success "Both builds are byte-for-byte identical!"
    log_success "SHA-256: $SHA256_BUILD1"
    log_info ""
    log_info "This verifies that:"
    log_info "  - The build process is deterministic"
    log_info "  - No random elements are introduced"
    log_info "  - Timestamps are properly normalized"
    log_info "  - File ordering is consistent"
    EXIT_CODE=0
else
    log_error "❌❌❌ BUILD NOT REPRODUCIBLE ❌❌❌"
    log_error "The two builds differ!"
    log_info ""
    log_info "Common causes of non-reproducibility:"
    log_info "  - Embedded timestamps"
    log_info "  - Random elements (UUIDs, nonces)"
    log_info "  - Inconsistent file ordering"
    log_info "  - Environment-dependent build steps"
    log_info "  - Non-deterministic compression"
    log_info ""
    log_info "Check the diffoscope report for details:"
    log_info "  $REPORT_DIR/diffoscope-report.html"
    EXIT_CODE=1
fi

log_info ""
log_info "Verification completed: $(date -u)"
log_info "All reports saved to: $REPORT_DIR"

exit $EXIT_CODE
