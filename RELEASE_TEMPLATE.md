# QWAMOS Release Notes

<!-- This template is auto-populated by the release-generator workflow -->
<!-- Manual sections can be added for additional context -->

## Version {{VERSION}} - {{DATE}}

**Release Type**: {{RELEASE_TYPE}}
**Git Tag**: `{{TAG}}`
**Build**: {{BUILD_NUMBER}}

---

## Overview

{{OVERVIEW}}

<!-- Auto-generated summary of this release -->
<!-- Key highlights and motivation for this version -->

---

## 🔒 Security Improvements

{{SECURITY_IMPROVEMENTS}}

<!-- Critical security fixes, PQC updates, VM isolation improvements -->
<!-- Format: - [SECURITY] Description (#issue) -->

### Post-Quantum Cryptography Updates

{{PQC_UPDATES}}

<!-- Kyber-1024, ChaCha20-Poly1305, BLAKE3 improvements -->

### VM Isolation Enhancements

{{VM_ISOLATION_UPDATES}}

<!-- QEMU, Chroot, PRoot, KVM security improvements -->

### Network Anonymization

{{NETWORK_UPDATES}}

<!-- Tor, I2P, DNSCrypt security updates -->

---

## ✨ New Features

{{NEW_FEATURES}}

<!-- Major new functionality added in this release -->
<!-- Format: - [FEATURE] Description (#issue) -->

### VM Management

{{VM_FEATURES}}

<!-- New VM modes, management tools, disk encryption features -->

### Gateway Functionality

{{GATEWAY_FEATURES}}

<!-- Tor/I2P/DNSCrypt new features -->

### Cryptographic Features

{{CRYPTO_FEATURES}}

<!-- New crypto modules, algorithms, key management -->

### User Interface

{{UI_FEATURES}}

<!-- Android app improvements, CLI enhancements -->

---

## 🐛 Bug Fixes

{{BUG_FIXES}}

<!-- Bug fixes and stability improvements -->
<!-- Format: - [FIX] Description (#issue) -->

### Critical Fixes

{{CRITICAL_FIXES}}

<!-- High-priority bugs that affected functionality -->

### Minor Fixes

{{MINOR_FIXES}}

<!-- Low-priority bugs and edge cases -->

---

## ⚡ Performance Improvements

{{PERFORMANCE_IMPROVEMENTS}}

<!-- Performance optimizations and speed improvements -->
<!-- Format: - [PERF] Description (#issue) -->

### VM Performance

{{VM_PERFORMANCE}}

<!-- QEMU/KVM optimizations, boot time improvements -->

### Cryptographic Performance

{{CRYPTO_PERFORMANCE}}

<!-- PQC algorithm optimizations, key generation speed -->

### Network Performance

{{NETWORK_PERFORMANCE}}

<!-- Gateway connection speed, bandwidth improvements -->

---

## 🎨 Refactoring & Code Quality

{{REFACTORING}}

<!-- Code refactoring, architecture improvements -->
<!-- Format: - [REFACTOR] Description (#issue) -->

---

## 📝 Documentation Updates

{{DOCUMENTATION_UPDATES}}

<!-- Documentation improvements, wiki updates -->
<!-- Format: - [DOCS] Description (#issue) -->

---

## 🧪 Testing Improvements

{{TESTING_UPDATES}}

<!-- New tests, test coverage improvements -->
<!-- Format: - [TEST] Description (#issue) -->

---

## 🔧 Build & Tooling

{{BUILD_UPDATES}}

<!-- Build system changes, CI/CD improvements -->
<!-- Format: - [BUILD] or [CI] Description (#issue) -->

---

## ⚠️ Breaking Changes

{{BREAKING_CHANGES}}

<!-- Breaking changes that require user action -->
<!-- Format: - Description with migration guide -->

### API Changes

{{API_BREAKING_CHANGES}}

<!-- Module interface changes, function signature changes -->

### Configuration Changes

{{CONFIG_BREAKING_CHANGES}}

<!-- VM config format changes, gateway config updates -->

### Migration Required

{{MIGRATION_REQUIRED}}

<!-- Data migrations, disk format changes -->

---

## 🚫 Deprecations

{{DEPRECATIONS}}

<!-- Features marked for removal in future releases -->
<!-- Format: - Feature (will be removed in version X.Y.Z) -->

---

## ⚠️ Known Issues

{{KNOWN_ISSUES}}

<!-- Known bugs and limitations in this release -->
<!-- Format: - Issue description (workaround if available) -->

### VM Mode Issues

{{VM_KNOWN_ISSUES}}

<!-- Known issues with QEMU/Chroot/PRoot/KVM -->

### Gateway Issues

{{GATEWAY_KNOWN_ISSUES}}

<!-- Known issues with Tor/I2P/DNSCrypt -->

### Platform-Specific Issues

{{PLATFORM_KNOWN_ISSUES}}

<!-- Android version compatibility, device-specific issues -->

---

## 📦 Installation & Upgrade

### New Installation

**Termux Installation**:
```bash
# Clone repository
git clone https://github.com/Dezirae-Stark/QWAMOS.git
cd QWAMOS

# Checkout release tag
git checkout {{TAG}}

# Run installation script
./scripts/install.sh
```

**Requirements**:
- Android 10+ (Android 14+ recommended)
- Termux (latest version)
- 4GB+ free storage
- 2GB+ RAM

### Upgrade from Previous Version

{{UPGRADE_STEPS}}

<!-- Auto-generated upgrade instructions based on changes -->

**General Upgrade Process**:

```bash
# Backup current installation
./scripts/backup.sh

# Pull latest changes
cd QWAMOS
git fetch --tags
git checkout {{TAG}}

# Run upgrade script
./scripts/upgrade.sh

# Verify installation
./scripts/verify.sh
```

### VM Migration Steps

{{VM_MIGRATION_STEPS}}

<!-- Steps for migrating VMs to new format if required -->

### Gateway Reconfiguration

{{GATEWAY_MIGRATION_STEPS}}

<!-- Steps for updating gateway configurations -->

### Data Migration

{{DATA_MIGRATION_STEPS}}

<!-- Steps for migrating encrypted volumes, keys, etc. -->

---

## 🔍 Verification & Testing

### Post-Install Verification

**Verify VM Modes**:
```bash
# Test QEMU
./scripts/test_vm.sh qemu

# Test Chroot
./scripts/test_vm.sh chroot

# Test PRoot
./scripts/test_vm.sh proot

# Test KVM (if rooted)
./scripts/test_vm.sh kvm
```

**Verify Gateways**:
```bash
# Test Tor
curl --socks5 127.0.0.1:9050 https://check.torproject.org

# Test I2P
curl --proxy http://127.0.0.1:4444 http://stats.i2p/

# Test DNSCrypt
dig @127.0.0.1 -p 5353 google.com
```

**Verify Post-Quantum Cryptography**:
```bash
# Run crypto test suite
pytest tests/crypto/ -v

# Test Kyber-1024
python3 -c "from qwamos.crypto.kyber import generate_keypair; print('Kyber-1024: OK')"

# Test ChaCha20-Poly1305
python3 -c "from qwamos.crypto.symmetric import encrypt, decrypt; print('ChaCha20: OK')"

# Test BLAKE3
python3 -c "from qwamos.crypto.hash import blake3_hash; print('BLAKE3: OK')"
```

---

## 📊 Release Statistics

{{RELEASE_STATISTICS}}

<!-- Auto-generated statistics -->

**Changes in this release**:
- **Total Commits**: {{COMMIT_COUNT}}
- **Contributors**: {{CONTRIBUTOR_COUNT}}
- **Files Changed**: {{FILES_CHANGED}}
- **Lines Added**: {{LINES_ADDED}}
- **Lines Removed**: {{LINES_REMOVED}}

**Issue Tracking**:
- **Issues Closed**: {{ISSUES_CLOSED}}
- **Pull Requests Merged**: {{PRS_MERGED}}

**Test Coverage**:
- **Unit Tests**: {{UNIT_TEST_COUNT}}
- **Integration Tests**: {{INTEGRATION_TEST_COUNT}}
- **Code Coverage**: {{CODE_COVERAGE}}%

---

## 🤝 Contributors

{{CONTRIBUTORS}}

<!-- Auto-generated list of contributors to this release -->

Special thanks to all contributors who made this release possible!

### New Contributors

{{NEW_CONTRIBUTORS}}

<!-- First-time contributors in this release -->

---

## 🔗 Links & Resources

**Download**:
- **Source Code (zip)**: https://github.com/Dezirae-Stark/QWAMOS/archive/refs/tags/{{TAG}}.zip
- **Source Code (tar.gz)**: https://github.com/Dezirae-Stark/QWAMOS/archive/refs/tags/{{TAG}}.tar.gz

**Documentation**:
- **Wiki**: https://github.com/Dezirae-Stark/QWAMOS/wiki
- **Installation Guide**: https://github.com/Dezirae-Stark/QWAMOS/wiki/Installation-&-Setup-Guide
- **Developer Guide**: https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide
- **Security Model**: https://github.com/Dezirae-Stark/QWAMOS/wiki/Security-Model

**Community**:
- **Discussions**: https://github.com/Dezirae-Stark/QWAMOS/discussions
- **Issues**: https://github.com/Dezirae-Stark/QWAMOS/issues
- **Email**: qwamos@tutanota.com

**Security**:
- **Security Policy**: https://github.com/Dezirae-Stark/QWAMOS/security/policy
- **Report Vulnerability**: qwamos@tutanota.com (private disclosure)

---

## 📜 Full Changelog

{{FULL_CHANGELOG}}

<!-- Auto-generated detailed changelog with all commits -->

**View full diff**: https://github.com/Dezirae-Stark/QWAMOS/compare/{{PREVIOUS_TAG}}...{{TAG}}

---

## 🛡️ Security Considerations

### Threat Model Impact

This release affects the following threat model tiers:

{{THREAT_MODEL_IMPACT}}

<!-- Impact on Tier 1-5 adversaries (see Security-Model.md) -->

### Security Audit Status

{{SECURITY_AUDIT_STATUS}}

<!-- Status of security audits for this release -->

### Known Security Limitations

{{SECURITY_LIMITATIONS}}

<!-- Security limitations users should be aware of -->

---

## 📞 Support

**Need help with this release?**

- **General Questions**: Post in [Q&A Discussions](https://github.com/Dezirae-Stark/QWAMOS/discussions/3)
- **Bug Reports**: Open an [Issue](https://github.com/Dezirae-Stark/QWAMOS/issues/new?template=bug_report.md)
- **Security Issues**: Email qwamos@tutanota.com (private disclosure)
- **Feature Requests**: Post in [Feature Request Discussion](https://github.com/Dezirae-Stark/QWAMOS/discussions/5)

**Response Times**:
- Critical security issues: 24-48 hours
- Critical bugs: 3-7 days
- General support: 1-3 days

---

## 📅 Next Release

**Upcoming in next release**:

{{NEXT_RELEASE_PREVIEW}}

<!-- Preview of features planned for next version -->

**Roadmap**: See [Roadmap Wiki](https://github.com/Dezirae-Stark/QWAMOS/wiki/Roadmap) for detailed plans.

---

**Release Manager**: {{RELEASE_MANAGER}}
**Release Date**: {{RELEASE_DATE}}
**Release Verification**: {{RELEASE_VERIFICATION_HASH}}

**This release is signed with**: {{SIGNING_KEY_ID}}

---

**🤖 Generated with [Claude Code](https://claude.com/claude-code)**

**License**: AGPL-3.0
**Copyright**: © 2025 QWAMOS Project
**Contact**: qwamos@tutanota.com
