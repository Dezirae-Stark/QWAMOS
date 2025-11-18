# QWAMOS Reproducible Build Framework

This directory contains tools and scripts for verifying that QWAMOS APK builds are reproducible.

## What is Reproducible Builds?

Reproducible builds allow independent verification that the distributed APK was built from the published source code without hidden modifications. Multiple parties can build the APK from source and verify they get byte-for-byte identical binaries.

## Quick Start

### Prerequisites

- Linux or macOS
- Java 17 or higher
- Android SDK installed
- Python 3.8+ with diffoscope (optional but recommended)

### Running Verification

```bash
# Navigate to this directory
cd reproducible/

# Run the verification (builds twice and compares)
./verify.sh
```

The verification script will:
1. Build the APK from source (Build #1)
2. Build the APK again (Build #2)
3. Compare the two builds byte-for-byte
4. Generate detailed reports

## Scripts

### `build.sh`

Builds the QWAMOS APK with reproducible settings.

**Usage:**
```bash
./build.sh [BUILD_NUMBER]
```

**Features:**
- Normalizes timestamps using SOURCE_DATE_EPOCH
- Disables Gradle daemon and caching
- Sets deterministic environment variables
- Outputs APK to `output/apk/`
- Generates SHA-256, SHA-512, and MD5 checksums
- Creates build manifest JSON

**Environment Variables:**
- `SOURCE_DATE_EPOCH` - Unix timestamp for reproducible builds (default: 1704067200)

### `verify.sh`

Rebuilds the APK and verifies reproducibility.

**Usage:**
```bash
./verify.sh
```

**Verification Steps:**
1. SHA-256 hash comparison
2. Binary diff analysis
3. File size comparison
4. APK structure analysis
5. File ordering check
6. Timestamp detection
7. Diffoscope comprehensive analysis
8. Report generation

**Exit Codes:**
- `0` - Build is reproducible
- `1` - Build is NOT reproducible

### `hash_manifest.json`

Template for storing verified build hashes and metadata.

**Contents:**
- Expected checksums for releases
- Build environment details
- Verification instructions
- Known issues and workarounds
- Security notes

## Output Structure

```
output/
├── apk/
│   ├── qwamos-build1-YYYYMMDD.apk
│   ├── qwamos-build1-YYYYMMDD.apk.sha256
│   ├── qwamos-build1-YYYYMMDD.apk.sha512
│   ├── qwamos-build1-YYYYMMDD.apk.manifest.json
│   ├── qwamos-build2-YYYYMMDD.apk
│   └── ...
├── logs/
│   ├── build-1.log
│   ├── build-2.log
│   └── verify.log
└── reports/
    ├── verification-report.json
    ├── diffoscope-report.html
    ├── diffoscope-report.txt
    ├── file-list-diff.txt
    ├── file-order-diff.txt
    └── timestamps-found.txt
```

## GitHub Actions

The workflow `.github/workflows/reproducible-build.yml` automatically verifies reproducibility on:
- Release creation
- Push to main/master
- Pull requests affecting Android code

## Reproducibility Checklist

For a build to be reproducible, it must:

- ✅ Use fixed timestamps (SOURCE_DATE_EPOCH)
- ✅ Have deterministic file ordering
- ✅ Use consistent locale and timezone (UTF-8, UTC)
- ✅ Disable Gradle daemon and caching
- ✅ Normalize all timestamps in ZIP entries
- ✅ Avoid random elements (UUIDs, nonces)
- ✅ Use deterministic compression

## Common Issues

### Timestamps

**Problem:** Embedded timestamps cause different builds.

**Solution:** Set `SOURCE_DATE_EPOCH` environment variable:
```bash
export SOURCE_DATE_EPOCH=1704067200
```

### File Ordering

**Problem:** ZIP file entries in different order.

**Solution:** Use deterministic ZIP ordering (handled by build script).

### Gradle Metadata

**Problem:** Gradle includes build-time metadata.

**Solution:** Disable caching and use `--no-daemon` flag.

### Native Libraries

**Problem:** Native libraries have build IDs.

**Solution:** Strip build IDs or use fixed build ID.

## Verification Reports

### diffoscope Report

The diffoscope report (`diffoscope-report.html`) provides detailed analysis:
- File-by-file comparison
- Binary diffs
- Archive contents
- Metadata differences

View the HTML report in a web browser for interactive exploration.

### Verification Report JSON

The `verification-report.json` contains:
```json
{
  "reproducible": true,
  "builds": {
    "build1": {"sha256": "...", "size_bytes": 12345},
    "build2": {"sha256": "...", "size_bytes": 12345}
  },
  "checks": {
    "sha256_match": true,
    "size_match": true,
    "binary_identical": true
  }
}
```

## Security Implications

Reproducible builds provide:

1. **Transparency** - Anyone can verify the APK matches the source code
2. **Supply Chain Security** - Detect backdoors inserted during build
3. **Trust Distribution** - Multiple parties can verify independently
4. **Audit Trail** - Historical builds can be re-verified

## Further Reading

- [Reproducible Builds Project](https://reproducible-builds.org/)
- [Android Reproducible Builds](https://developer.android.com/studio/build/reproducible-builds)
- [SOURCE_DATE_EPOCH Specification](https://reproducible-builds.org/docs/source-date-epoch/)
- [Diffoscope Documentation](https://diffoscope.org/)

## Support

For issues with reproducible builds:

1. Check the verification logs in `output/logs/`
2. Review the diffoscope report for specific differences
3. Ensure all prerequisites are installed
4. Verify environment variables are set correctly
5. Open an issue on GitHub with logs attached

---

🔒 **Reproducible builds ensure the integrity and trustworthiness of QWAMOS.**
