# QWAMOS VM Templates

Automated build system for QWAMOS virtual machine templates supporting multiple virtualization modes.

## 📦 Available Templates

### QEMU Template
- **Type**: Full virtualization with hardware acceleration
- **Use Case**: Maximum performance with KVM support
- **Requirements**: QEMU 5.0+, KVM (optional)
- **Best For**: Production deployments, testing

### PRoot Template
- **Type**: Userspace virtualization (no root required)
- **Use Case**: Android/Termux environments
- **Requirements**: PRoot 5.1+
- **Best For**: Mobile devices, non-root environments

### Chroot Template
- **Type**: Lightweight namespace isolation
- **Use Case**: Server deployments with root access
- **Requirements**: Linux kernel 3.8+, root access
- **Best For**: Containers, lightweight isolation

## 🏗️ Building Templates

### Build All Templates

```bash
# Build QEMU template
./vm-templates/scripts/build_qemu_template.sh

# Build PRoot template
./vm-templates/scripts/build_proot_template.sh

# Build Chroot template
./vm-templates/scripts/build_chroot_template.sh
```

### Validate Templates

```bash
# Validate a specific template
./vm-templates/scripts/validate_vm_template.sh \
  vm-templates/output/templates/qwamos-qemu-template.tar.gz \
  --type qemu --verbose

# Validate all templates
for template in vm-templates/output/templates/*.tar.gz; do
  ./vm-templates/scripts/validate_vm_template.sh "$template"
done
```

### Export for Release

```bash
# Export templates with checksums and release notes
./vm-templates/scripts/export_vm_template.sh

# Output will be in vm-templates/output/release/
```

## 🤖 Automated Builds

Templates are automatically built via GitHub Actions when a release is created:

1. **Trigger**: Release creation or manual workflow dispatch
2. **Build**: All three templates built in parallel
3. **Validate**: Each template validated with comprehensive checks
4. **Export**: Templates compressed with checksums
5. **Upload**: Automatically attached to GitHub Release

### Manual Workflow Trigger

```bash
# Using GitHub CLI
gh workflow run build-vm-templates.yml

# Or via GitHub web interface:
# Actions → Build VM Templates → Run workflow
```

## 📂 Directory Structure

```
vm-templates/
├── scripts/
│   ├── build_qemu_template.sh      # Build QEMU VM template
│   ├── build_proot_template.sh     # Build PRoot VM template
│   ├── build_chroot_template.sh    # Build Chroot VM template
│   ├── validate_vm_template.sh     # Validate template integrity
│   └── export_vm_template.sh       # Export for release
├── configs/
│   └── (template configuration files)
├── output/
│   ├── templates/                  # Built templates
│   └── release/                    # Export-ready packages
└── work/                           # Build working directories
    ├── qemu/
    ├── proot/
    └── chroot/
```

## 🔐 Template Features

All templates include:

- ✅ Post-Quantum Cryptography (Kyber-1024, ChaCha20-Poly1305, BLAKE3)
- ✅ Network isolation and gateway mode support
- ✅ QWAMOS configuration structure
- ✅ Launcher scripts for easy deployment
- ✅ Metadata and checksums
- ✅ Documentation

## 📥 Using Templates

### QEMU Template

```bash
# Download and extract
tar xzf qwamos-qemu-template.tar.gz
cd qwamos-qemu-template

# Launch with QEMU
qemu-system-x86_64 \
  -hda qwamos-qemu-template.img \
  -m 2G \
  -smp 2 \
  -enable-kvm  # If KVM available
```

### PRoot Template

```bash
# Download and extract
tar xzf qwamos-proot-template.tar.gz
cd qwamos-proot-template

# Extract rootfs
tar xzf qwamos-proot-template-rootfs.tar.gz

# Launch
./launch-proot.sh

# Or manually with proot
proot -r rootfs -b /dev -b /proc -b /sys /bin/bash
```

### Chroot Template

```bash
# Download and extract
tar xzf qwamos-chroot-template.tar.gz
cd qwamos-chroot-template

# Extract rootfs
tar xzf qwamos-chroot-template-rootfs.tar.gz

# Launch (requires root)
sudo ./launch-chroot.sh

# Or manually
sudo chroot rootfs /bin/bash
```

## 🧪 Development

### Adding a New Template Type

1. Create `vm-templates/scripts/build_<type>_template.sh`
2. Follow the structure of existing build scripts:
   - Create rootfs
   - Apply QWAMOS configs
   - Create metadata JSON
   - Package template
   - Export to output directory
3. Add validation to `validate_vm_template.sh`
4. Update `.github/workflows/build-vm-templates.yml`

### Build Script Structure

```bash
#!/usr/bin/env bash
set -euo pipefail

# Configuration
VM_NAME="qwamos-<type>-template"
OUTPUT_DIR="vm-templates/output/templates"

# Build steps
main() {
    create_rootfs
    apply_qwamos_configs
    create_metadata
    package_template
    export_template
}

main "$@"
```

## 📊 Validation Checks

The validation script performs 10 comprehensive checks:

1. ✓ File existence
2. ✓ File size validation
3. ✓ Checksum verification
4. ✓ Archive extraction
5. ✓ Required files check
6. ✓ Metadata JSON validation
7. ✓ Rootfs structure verification
8. ✓ Launcher script check
9. ✓ Internal checksums verification
10. ✓ Documentation presence

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
on:
  release:
    types: [created, published]

jobs:
  - build-qemu-template
  - build-proot-template
  - build-chroot-template
  - export-and-release
```

### Artifacts

- Template archives (.tar.gz, .tar.xz)
- SHA256 and SHA512 checksums
- Combined SHA256SUMS file
- MANIFEST.txt with all template info
- RELEASE_NOTES.md for GitHub Release

## 📝 Template Metadata Format

```json
{
  "name": "qwamos-<type>-template",
  "type": "qemu|proot|chroot",
  "version": "1.2.0",
  "architecture": "x86_64|aarch64|amd64",
  "os": "Debian bookworm",
  "features": {
    "pqc_enabled": true,
    "kyber_1024": true,
    "chacha20_poly1305": true,
    "blake3": true,
    "network_isolation": true
  },
  "requirements": {
    "ram_min": "256M",
    "ram_recommended": "2G",
    "storage": "8G"
  },
  "files": {
    "disk_image": "qwamos-<type>-template.img",
    "rootfs": "qwamos-<type>-template-rootfs.tar.gz",
    "metadata": "qwamos-<type>-template.json"
  }
}
```

## 🔧 Troubleshooting

### Build Failures

```bash
# Check logs
tail -f vm-templates/work/<type>/build.log

# Clean work directory
rm -rf vm-templates/work/<type>

# Rebuild
./vm-templates/scripts/build_<type>_template.sh
```

### Validation Failures

```bash
# Run validation with verbose output
./vm-templates/scripts/validate_vm_template.sh \
  path/to/template.tar.gz \
  --type <type> \
  --verbose
```

### Permission Issues

```bash
# Make scripts executable
chmod +x vm-templates/scripts/*.sh

# For chroot, ensure root access
sudo ./vm-templates/scripts/build_chroot_template.sh
```

## 📄 License

AGPL-3.0 - See LICENSE file

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines.

## 🔗 Links

- [QWAMOS Documentation](https://dezirae-stark.github.io/QWAMOS)
- [GitHub Repository](https://github.com/Dezirae-Stark/QWAMOS)
- [GitHub Releases](https://github.com/Dezirae-Stark/QWAMOS/releases)
- [Security Policy](../SECURITY.md)
