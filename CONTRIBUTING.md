# Contributing to QWAMOS

Thank you for your interest in contributing to QWAMOS (Quantum-Wrapped Android Mobile Operating System)! We welcome contributions from developers, security researchers, privacy advocates, and anyone passionate about mobile security and privacy.

QWAMOS is a modular, privacy-first operating environment that provides VM isolation, post-quantum cryptography, and anonymous networking for Android devices. Your contributions help make mobile privacy accessible to journalists, activists, researchers, and privacy-conscious users worldwide.

---

## Table of Contents

- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Documentation Requirements](#documentation-requirements)
- [Security Guidelines](#security-guidelines)
- [Branching Structure](#branching-structure)
- [Testing & Verification](#testing--verification)
- [Pull Request Checklist](#pull-request-checklist)
- [Community Guidelines](#community-guidelines)
- [Getting Help](#getting-help)

---

## Getting Started

### Prerequisites

Before contributing, please:

1. **Read the Documentation**:
   - [README.md](README.md) - Project overview
   - [Developer Guide Wiki](https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide) - Detailed development guide
   - [Architecture Wiki](https://github.com/Dezirae-Stark/QWAMOS/wiki/Architecture) - System architecture
   - [Roadmap Wiki](https://github.com/Dezirae-Stark/QWAMOS/wiki/Roadmap) - Development roadmap

2. **Set Up Development Environment**:
   ```bash
   # Clone your fork
   git clone https://github.com/YOUR-USERNAME/QWAMOS.git
   cd QWAMOS

   # Add upstream remote
   git remote add upstream https://github.com/Dezirae-Stark/QWAMOS.git

   # Install development dependencies
   pip install -r requirements-dev.txt

   # Install pre-commit hooks
   pre-commit install
   ```

3. **Understand the Architecture**:
   - QWAMOS uses a modular architecture with VM isolation layers
   - Core modules: VM management, cryptography, gateway, panic system
   - Each module is designed for independence and testability

---

## How to Contribute

### Fork and Branch Workflow

We follow the standard fork and branch workflow:

1. **Fork the Repository**:
   - Click "Fork" on GitHub
   - Clone your fork locally

2. **Create a Feature Branch**:
   ```bash
   # For new features
   git checkout -b feature/descriptive-name

   # For bug fixes
   git checkout -b fix/issue-description

   # For documentation
   git checkout -b docs/what-youre-documenting
   ```

3. **Make Your Changes**:
   - Write clean, well-documented code
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Commit Your Changes**:
   Use **Conventional Commits** format:

   ```bash
   git commit -m "[TYPE] Brief description (50 chars max)

   Detailed explanation of what and why, not how.
   Wrap at 72 characters.

   Fixes: #123
   See-Also: #456"
   ```

   **Commit Types**:
   - `[FEATURE]` - New functionality
   - `[FIX]` - Bug fix
   - `[SECURITY]` - Security fix or improvement
   - `[PHASE]` - Roadmap phase implementation
   - `[DOC]` - Documentation updates
   - `[TEST]` - Test additions or modifications
   - `[REFACTOR]` - Code refactoring (no functional change)
   - `[PERF]` - Performance improvements
   - `[CHORE]` - Build process, dependencies, tooling

   **Examples**:
   ```
   [FEATURE] Add support for VeraCrypt hidden volumes

   Implements hidden volume mounting for plausible deniability.
   Users can now specify both decoy and real passwords.

   Fixes: #142
   See-Also: phases/phase13_pqc_storage/

   [SECURITY] Fix VM escape via shared memory vulnerability

   CVE-2025-1234: Heap overflow in shared memory handler.
   Applied namespace isolation to prevent cross-VM access.

   Credit: Security Researcher Name
   ```

5. **Push to Your Fork**:
   ```bash
   git push origin feature/descriptive-name
   ```

6. **Create a Pull Request**:
   - Go to GitHub and create a PR from your fork
   - Fill out the PR template completely
   - Link related issues
   - Request review from maintainers

### Pull Request Requirements

Before submitting a PR, ensure:

- ✅ **Code Quality**: All linters pass (pylint, mypy, black)
- ✅ **Tests**: New code has appropriate test coverage
- ✅ **Documentation**: README/Wiki updated if needed
- ✅ **Commit Messages**: Follow conventional commit format
- ✅ **No Conflicts**: Branch is up to date with upstream
- ✅ **Issue Links**: Related issues are referenced
- ✅ **Screenshots**: UI changes include before/after screenshots

### Testing Requirements

All contributions must pass the following tests:

```bash
# Run code formatter
black qwamos/

# Run linter
pylint qwamos/

# Run type checker
mypy qwamos/

# Run unit tests
pytest tests/

# Run integration tests (if applicable)
pytest tests/integration/ --integration
```

---

## Code Style Guidelines

### Python Standards

QWAMOS follows **PEP 8** with modifications:

**Line Length**: 100 characters (not 79)

**Type Hints**: Always use type hints
```python
from typing import List, Dict, Optional, Tuple

def create_vm(
    name: str,
    disk_size: int,
    ram_mb: int = 2048,
    kvm_enabled: bool = False
) -> Optional[VM]:
    """Create new virtual machine.

    Args:
        name: VM identifier
        disk_size: Disk size in MB
        ram_mb: RAM allocation in MB (default: 2048)
        kvm_enabled: Use KVM acceleration if available

    Returns:
        VM instance if successful, None otherwise

    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If VM creation fails
    """
    # Implementation...
```

**Docstrings**: Use Google-style docstrings
```python
def encrypt_data(plaintext: bytes, key: KyberKey) -> EncryptedData:
    """Encrypt data using Kyber-1024 + ChaCha20-Poly1305.

    This function performs post-quantum encryption using the NIST
    FIPS 203 Kyber-1024 KEM for key encapsulation and ChaCha20-Poly1305
    for authenticated encryption.

    Args:
        plaintext: Raw data to encrypt
        key: Kyber-1024 public key

    Returns:
        EncryptedData object containing ciphertext and authentication tag

    Raises:
        EncryptionError: If encryption fails
        ValueError: If key is invalid

    Example:
        >>> key = generate_kyber_key()
        >>> encrypted = encrypt_data(b"secret", key.public_key)
        >>> assert encrypted.verify()
    """
```

**Naming Conventions**:
```python
# Variables and functions: snake_case
vm_manager = VMManager()
def start_virtual_machine(vm_name: str) -> bool:
    pass

# Classes: PascalCase
class KyberKeyEncapsulation:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_VM_COUNT = 10
DEFAULT_CIPHER = "chacha20-poly1305"

# Private methods: _leading_underscore
def _internal_helper(self) -> None:
    pass
```

**Imports**: Alphabetical within groups
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import numpy as np
from cryptography.hazmat.primitives import hashes

# Local modules
from qwamos.crypto import kyber
from qwamos.vm import manager
```

### Kotlin/Flutter Standards

For Android UI components (React Native/Kotlin):

**Kotlin**:
```kotlin
// Use meaningful names
class VmManagerActivity : AppCompatActivity() {
    private lateinit var vmAdapter: VmListAdapter

    // Document public methods
    /**
     * Initialize VM list from storage
     * @return List of available VMs
     */
    fun loadVirtualMachines(): List<VirtualMachine> {
        // Implementation
    }
}
```

**Flutter/Dart** (if applicable):
```dart
/// Creates a new VM configuration widget
class VmConfigWidget extends StatefulWidget {
  final String vmName;
  final VmConfig initialConfig;

  const VmConfigWidget({
    Key? key,
    required this.vmName,
    required this.initialConfig,
  }) : super(key: key);
}
```

### Shell Script Formatting

**Bash/Shell scripts**:
```bash
#!/bin/bash
# Script: create_vm.sh
# Purpose: Create and configure a new QWAMOS virtual machine
# Usage: ./create_vm.sh --name <vm-name> --size <disk-size-mb>

set -e  # Exit on error
set -u  # Exit on undefined variable

# Constants in uppercase
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly DEFAULT_VM_SIZE=10240

# Functions use snake_case
create_virtual_machine() {
    local vm_name="$1"
    local disk_size="$2"

    echo "Creating VM: ${vm_name} with ${disk_size}MB disk..."

    # Implementation
}

# Main execution
main() {
    if [[ $# -lt 2 ]]; then
        echo "Usage: $0 --name <vm-name> --size <disk-size-mb>"
        exit 1
    fi

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --name)
                vm_name="$2"
                shift 2
                ;;
            --size)
                disk_size="$2"
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    create_virtual_machine "${vm_name}" "${disk_size}"
}

main "$@"
```

### VM Module Layout Rules

When creating new VM modules:

```
qwamos/
├── vm/
│   ├── __init__.py          # Module exports
│   ├── manager.py           # VM lifecycle management
│   ├── isolation.py         # Isolation layer implementation
│   ├── scheduler.py         # Resource scheduling
│   └── backends/
│       ├── __init__.py
│       ├── qemu.py          # QEMU backend
│       ├── kvm.py           # KVM backend
│       ├── chroot.py        # Chroot backend
│       └── proot.py         # PRoot backend
```

**Module Requirements**:
- Each module must have `__init__.py`
- Public API clearly defined in `__init__.py`
- Separation of concerns (one module, one responsibility)
- Comprehensive unit tests in `tests/`

### Linting Expectations

All code must pass:

**Python**:
```bash
# Format code
black qwamos/ tests/

# Check style
pylint qwamos/ --max-line-length=100

# Type checking
mypy qwamos/ --strict

# Import sorting
isort qwamos/ tests/
```

**Expected Results**: No errors, warnings are acceptable with justification

---

## Documentation Requirements

### When to Update Documentation

Update documentation when:
- ✅ Adding new features or modules
- ✅ Changing public APIs
- ✅ Modifying configuration options
- ✅ Updating installation procedures
- ✅ Fixing bugs that affect documented behavior

### Documentation Standards

**README.md Updates**:
- Keep the README concise and high-level
- Update badges if adding new CI/CD checks
- Update feature lists if adding major functionality
- Keep installation instructions current

**Wiki Updates**:
- [Developer Guide](https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide) - Development procedures
- [Architecture](https://github.com/Dezirae-Stark/QWAMOS/wiki/Architecture) - System design
- [Installation & Setup Guide](https://github.com/Dezirae-Stark/QWAMOS/wiki/Installation-&-Setup-Guide) - User installation
- [FAQ](https://github.com/Dezirae-Stark/QWAMOS/wiki/FAQ) - Common questions
- [Roadmap](https://github.com/Dezirae-Stark/QWAMOS/wiki/Roadmap) - Development phases

**Markdown Consistency**:
```markdown
# Main Heading (H1) - Only one per document

## Section Heading (H2)

### Subsection Heading (H3)

**Bold for emphasis**
*Italic for technical terms*

- Bullet points for lists
- Second item

1. Numbered lists for steps
2. Second step

`inline code` for commands

\`\`\`bash
# Code blocks with language specification
./command --option value
\`\`\`
```

**Include Diagrams When Relevant**:
```markdown
# ASCII Diagrams
┌─────────────┐
│  Component  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Feature   │
└─────────────┘

# Or reference external diagrams
![Architecture Diagram](docs/images/architecture.png)
```

**Code Examples**:
- Always include working code examples
- Add comments explaining non-obvious parts
- Show both usage and expected output

---

## Security Guidelines

### Responsible Disclosure

Found a security vulnerability? **DO NOT create a public issue.**

**Private Reporting Channels**:
1. **GitHub Security Advisories**: [Report Privately](https://github.com/Dezirae-Stark/QWAMOS/security/advisories/new)
2. **Encrypted Email**: qwamos@tutanota.com (PGP key available on request)

**What to Include**:
- Vulnerability type (VM escape, crypto weakness, etc.)
- Affected versions
- Steps to reproduce (if safe to share)
- Impact assessment (Confidentiality, Integrity, Availability)
- Proof of concept (share privately, not in public issues)
- Suggested fix (optional but appreciated)

**Response Timeline**:
- Initial Response: 24 hours
- Severity Assessment: 3 days
- Patch Development: Varies by severity (critical: 7 days)
- Public Disclosure: After patch release + 90 days

**Credit Policy**:
- Security researchers credited in release notes
- CVE assignment for qualifying vulnerabilities
- Optional inclusion in SECURITY.md hall of fame

### Sensitive Information Policy

**NEVER submit the following in public issues or PRs**:
- ❌ Passwords, API keys, tokens
- ❌ Private keys or certificates
- ❌ Personally identifiable information (PII)
- ❌ Real vulnerability exploits (proof of concepts should be shared privately)
- ❌ Sensitive configuration details

**Use the Security Issue Template** for security-related reports:
- [Security Vulnerability Template](https://github.com/Dezirae-Stark/QWAMOS/issues/new?template=security_vulnerability.md)

---

## Branching Structure

QWAMOS uses a structured branching model:

### Branch Types

**`master` (or `main`)** - Stable Release Branch
- Always deployable
- Only accepts PRs from `dev` or `hotfix/*` branches
- Tagged with version numbers (v1.0.0, v1.1.0, etc.)
- Protected branch (requires reviews)

**`dev`** - Next Release Branch
- Integration branch for upcoming release
- Accepts PRs from `feature/*` branches
- Regular integration testing
- Merged to `master` for releases

**`feature/<name>`** - Feature Development
- Created from `dev`
- Naming: `feature/descriptive-feature-name`
- Examples:
  - `feature/veracrypt-hidden-volumes`
  - `feature/apparmor-profiles`
  - `feature/react-native-ui`
- Merged back to `dev` via PR

**`fix/<name>`** - Bug Fixes
- Created from `dev` (or `master` for hotfixes)
- Naming: `fix/issue-description`
- Examples:
  - `fix/vm-memory-leak`
  - `fix/gateway-connection-timeout`
  - `fix/kyber-key-generation`
- Merged back to source branch via PR

**`hotfix/<name>`** - Critical Production Fixes
- Created from `master`
- Naming: `hotfix/critical-issue`
- Examples:
  - `hotfix/security-vulnerability-cve-2025-1234`
  - `hotfix/crash-on-startup`
- Merged to both `master` AND `dev`

**`docs/<name>`** - Documentation Changes
- Created from `dev`
- Naming: `docs/what-youre-documenting`
- Examples:
  - `docs/update-installation-guide`
  - `docs/add-api-reference`
- Merged to `dev` via PR

### Branch Creation Examples

```bash
# Create feature branch
git checkout dev
git pull upstream dev
git checkout -b feature/my-new-feature

# Create fix branch
git checkout dev
git pull upstream dev
git checkout -b fix/bug-description

# Create hotfix branch (from master)
git checkout master
git pull upstream master
git checkout -b hotfix/critical-issue

# Create docs branch
git checkout dev
git pull upstream dev
git checkout -b docs/update-readme
```

### Branch Protection Rules

**`master` branch**:
- ✅ Require pull request reviews (1+ approvals)
- ✅ Require status checks to pass
- ✅ No force pushes
- ✅ No deletions
- ✅ Require linear history (optional)

**`dev` branch**:
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ No force pushes

---

## Testing & Verification

### VM Isolation Testing

**Test QEMU Isolation**:
```bash
# Create test VM
./scripts/create_vm.sh --name test-vm --type browser --backend qemu

# Start VM
./scripts/start_vm.sh test-vm

# Verify isolation
ps aux | grep qemu  # Check process isolation
ip netns list       # Check network namespace
ls -la /proc/$(pgrep qemu)/ns/  # Check namespace isolation

# Attempt cross-VM access (should fail)
# Try to access another VM's memory or network
```

**Test Chroot Isolation**:
```bash
# Create chroot VM
./scripts/create_vm.sh --name chroot-test --backend chroot

# Verify chroot jail
sudo chroot /path/to/vm/rootfs /bin/bash
ls /  # Should only see VM filesystem, not host
```

**Test PRoot Isolation** (no root required):
```bash
# Create PRoot VM
./scripts/create_vm.sh --name proot-test --backend proot

# Verify userspace isolation
proot -r /path/to/vm/rootfs /bin/bash
```

**Test KVM Acceleration** (requires hardware support):
```bash
# Check KVM availability
./tests/kvm_hardware_suite/kvm_hardware_check.sh

# Create KVM VM
./scripts/create_vm.sh --name kvm-test --backend kvm

# Verify hardware acceleration
lsmod | grep kvm  # kvm and kvm_intel/kvm_amd should be loaded
```

### Gateway Connectivity Testing

**Test Tor Gateway**:
```bash
# Check Tor service
systemctl status tor  # or appropriate service manager

# Test SOCKS5 proxy
curl --socks5 127.0.0.1:9050 https://check.torproject.org

# Verify circuit isolation
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip
# Run multiple times, should see different exit IPs
```

**Test I2P Gateway**:
```bash
# Check I2P router
curl http://127.0.0.1:7657  # I2P console

# Test HTTP proxy
curl --proxy http://127.0.0.1:4444 http://stats.i2p/

# Test eepsite access
curl --proxy http://127.0.0.1:4444 http://example.i2p/
```

**Test DNSCrypt**:
```bash
# Verify DNSCrypt is running
ps aux | grep dnscrypt-proxy

# Test DNS resolution
nslookup example.com 127.0.0.1 -port=5354

# Verify DNSSEC
dig @127.0.0.1 -p 5354 example.com +dnssec
```

### Post-Quantum Crypto Verification

**Test Kyber-1024 Key Generation**:
```bash
# Generate Kyber key pair
python3 << EOF
from qwamos.crypto.kyber import generate_keypair

public_key, private_key = generate_keypair()
print(f"Public key size: {len(public_key.to_bytes())} bytes")
print(f"Private key size: {len(private_key.to_bytes())} bytes")

# Expected: Public ~1568 bytes, Private ~3168 bytes
assert len(public_key.to_bytes()) == 1568
assert len(private_key.to_bytes()) == 3168
print("✅ Kyber-1024 key generation successful")
EOF
```

**Test ChaCha20-Poly1305 Encryption**:
```bash
# Test AEAD encryption
python3 << EOF
from qwamos.crypto.chacha20 import encrypt, decrypt

plaintext = b"Test message for encryption"
key = b"0" * 32  # 256-bit key (use proper key in production)
nonce = b"0" * 12  # 96-bit nonce

ciphertext, tag = encrypt(plaintext, key, nonce)
decrypted = decrypt(ciphertext, tag, key, nonce)

assert decrypted == plaintext
print("✅ ChaCha20-Poly1305 AEAD encryption successful")
EOF
```

**Test Full PQC Stack**:
```bash
# End-to-end encryption test
python3 << EOF
from qwamos.crypto import kyber, chacha20, blake3

# 1. Generate Kyber keypair
public_key, private_key = kyber.generate_keypair()

# 2. Encapsulate shared secret
ciphertext, shared_secret = kyber.encapsulate(public_key)

# 3. Derive encryption key
key = blake3.hash(shared_secret)[:32]

# 4. Encrypt data
plaintext = b"Sensitive data"
nonce = blake3.hash(b"unique-nonce")[:12]
encrypted, tag = chacha20.encrypt(plaintext, key, nonce)

# 5. Verify decapsulation and decryption
recovered_secret = kyber.decapsulate(ciphertext, private_key)
recovered_key = blake3.hash(recovered_secret)[:32]
decrypted = chacha20.decrypt(encrypted, tag, recovered_key, nonce)

assert decrypted == plaintext
print("✅ Full post-quantum cryptography stack verified")
EOF
```

### Integration Testing

**Run Full Test Suite**:
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/ --integration

# KVM hardware tests (requires /dev/kvm)
cd tests/kvm_hardware_suite/
./kvm_hardware_check.sh
python3 kvm_capability_report.py

# Differential QEMU vs KVM tests
cd tests/differential_kvm_qemu/
python3 diff_runner.py --output-dir .
python3 comparison_engine.py
```

---

## Pull Request Checklist

Before submitting your PR, verify:

### Code Quality
- [ ] Code follows style guidelines (PEP 8, 100 char line length)
- [ ] All linters pass (`black`, `pylint`, `mypy`)
- [ ] Type hints included for all functions
- [ ] Docstrings written for all public methods
- [ ] No debug code or print statements left in

### Testing
- [ ] Unit tests added for new functionality
- [ ] All existing tests pass
- [ ] Integration tests run successfully (if applicable)
- [ ] VM isolation tested (if modifying VM code)
- [ ] Gateway connectivity tested (if modifying network code)
- [ ] PQC stack tested (if modifying crypto code)

### Documentation
- [ ] README updated (if adding major features)
- [ ] Wiki pages updated (if changing architecture or APIs)
- [ ] Code comments explain non-obvious logic
- [ ] CHANGELOG.md updated (for releases)
- [ ] Migration guide provided (if breaking changes)

### Security
- [ ] No sensitive information in code or commits
- [ ] Security implications considered and documented
- [ ] No new security vulnerabilities introduced
- [ ] Security tests pass (if applicable)

### Git
- [ ] Commit messages follow conventional format
- [ ] Branch is up to date with target branch
- [ ] No merge conflicts
- [ ] Commits are logically organized (squash if needed)
- [ ] Related issues linked in PR description

### UI Changes (if applicable)
- [ ] Screenshots included (before/after)
- [ ] Tested on multiple screen sizes
- [ ] Accessibility considerations addressed
- [ ] Dark mode support (if UI component)

### Performance
- [ ] No significant performance regression
- [ ] Memory leaks checked (if applicable)
- [ ] Benchmarks run (if performance-critical code)

---

## Community Guidelines

### Code of Conduct

**Be Respectful**:
- ✅ Respectful and constructive feedback
- ✅ Assume good intentions
- ✅ Help newcomers learn
- ✅ Share knowledge freely
- ❌ No harassment, discrimination, or personal attacks
- ❌ No spam or off-topic discussions

**Be Collaborative**:
- ✅ Review others' code thoughtfully
- ✅ Accept feedback gracefully
- ✅ Acknowledge contributions
- ✅ Share credit appropriately

**Be Professional**:
- ✅ Keep discussions on-topic
- ✅ Use clear, technical language
- ✅ Provide evidence for claims
- ✅ Respect maintainer decisions

### Communication Channels

**GitHub Issues**: Bug reports, feature requests
**GitHub Discussions**: Q&A, ideas, general discussion
**Pull Requests**: Code contributions
**Email**: qwamos@tutanota.com (security, private matters)

### Response Times

**Issues**: 48 hours for initial response
**Pull Requests**: 7 days for initial review
**Security Reports**: 24 hours for initial response

---

## Getting Help

### Documentation

- **[Developer Guide](https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide)** - Comprehensive development guide
- **[Architecture](https://github.com/Dezirae-Stark/QWAMOS/wiki/Architecture)** - System architecture
- **[FAQ](https://github.com/Dezirae-Stark/QWAMOS/wiki/FAQ)** - Frequently asked questions
- **[Security Model](https://github.com/Dezirae-Stark/QWAMOS/wiki/Security-Model)** - Security implementation

### Support Channels

**Questions?**
- Search existing [GitHub Issues](https://github.com/Dezirae-Stark/QWAMOS/issues)
- Browse [GitHub Discussions](https://github.com/Dezirae-Stark/QWAMOS/discussions)
- Check the [FAQ](https://github.com/Dezirae-Stark/QWAMOS/wiki/FAQ)

**Stuck on something?**
- Post in [Q&A Discussions](https://github.com/Dezirae-Stark/QWAMOS/discussions/categories/q-a)
- Ask in [Developer Lounge](https://github.com/Dezirae-Stark/QWAMOS/discussions/categories/developer-lounge)
- Email: qwamos@tutanota.com

**Found a bug?**
- Use the [Bug Report Template](https://github.com/Dezirae-Stark/QWAMOS/issues/new?template=bug_report.md)

**Have a feature idea?**
- Use the [Feature Request Template](https://github.com/Dezirae-Stark/QWAMOS/issues/new?template=feature_request.md)

**Security concern?**
- Use [Security Advisories](https://github.com/Dezirae-Stark/QWAMOS/security/advisories/new)
- Or email: qwamos@tutanota.com

---

## Recognition

### Contributors

Contributors are recognized in multiple ways:

**For All Contributors**:
- Credit in release notes
- Mention in README.md contributors section
- Eternal gratitude from the community 🙏

**For Significant Contributions** (100+ LOC, major features):
- Co-author attribution in git commits
- Invitation to core contributor team
- Input on roadmap decisions

**For Security Researchers**:
- Credit in security advisories
- CVE co-authorship (if applicable)
- Inclusion in SECURITY.md hall of fame

---

## License

By contributing to QWAMOS, you agree that:

1. Your contributions are your original work
2. You have the right to submit the contribution
3. Your contributions are licensed under **AGPL-3.0**
4. You grant QWAMOS project maintainers perpetual license to use your contributions

No formal CLA signing required - your first PR implies acceptance.

See [LICENSE](LICENSE) for full license text.

---

## Thank You! 🙏

Thank you for contributing to QWAMOS and helping make mobile privacy accessible to everyone!

**Together, we're building privacy tools that empower people worldwide.**

---

**Questions?** Email: qwamos@tutanota.com
**Project**: https://github.com/Dezirae-Stark/QWAMOS
**Wiki**: https://github.com/Dezirae-Stark/QWAMOS/wiki

*Last Updated: 2025-11-18*
