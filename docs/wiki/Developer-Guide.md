# Developer Guide

**[← Back to Home](Home)**

---

## Welcome Contributors!

QWAMOS is an open-source project that welcomes contributions from developers, security researchers, and privacy advocates. This guide will help you get started.

---

## Quick Start for Developers

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/QWAMOS.git
cd QWAMOS

# 3. Add upstream remote
git remote add upstream https://github.com/Dezirae-Stark/QWAMOS.git

# 4. Create feature branch
git checkout -b feature/my-awesome-feature

# 5. Make changes and commit
git add .
git commit -m "[FEATURE] Add my awesome feature"

# 6. Push to your fork
git push origin feature/my-awesome-feature

# 7. Create Pull Request on GitHub
```

---

## Development Environment Setup

### Prerequisites

**Required Tools:**
- Git 2.30+
- Python 3.9+ (`python3 --version`)
- GCC/Clang compiler
- QEMU 7.0+ (for testing)
- Docker (for reproducible builds)

**Recommended:**
- VS Code with Python extension
- `black` (code formatter)
- `pylint` (linter)
- `mypy` (type checker)

### Setup Development Environment

```bash
# Install Python dependencies
pip install -r requirements-dev.txt

# This installs:
# - pytest (testing framework)
# - black (code formatter)
# - pylint (linter)
# - mypy (type checker)
# - pre-commit (git hooks)

# Install pre-commit hooks
pre-commit install

# Hooks will run on every commit:
# - black (format code)
# - pylint (check code quality)
# - mypy (type checking)
# - trailing whitespace removal
```

### Verify Setup

```bash
# Run tests
pytest tests/

# Expected output:
# ===== test session starts =====
# collected 247 items
#
# tests/test_vm.py ............
# tests/test_crypto.py ............
# tests/test_gateway.py ............
#
# ===== 247 passed in 3.42s =====

# Run linters
pylint qwamos/
mypy qwamos/

# Format code
black qwamos/
```

---

## Code Style & Standards

### Python Style Guide

QWAMOS follows **PEP 8** with some modifications:

**Line Length:**
- Max 100 characters (not 79)
- Exception: Long URLs, import statements

**Formatting:**
```python
# ✅ GOOD
def encrypt_vm_disk(
    plaintext: bytes,
    vm_name: str,
    kyber_key: KyberPublicKey
) -> EncryptedDisk:
    """Encrypt VM disk image using Kyber-1024 + ChaCha20.

    Args:
        plaintext: Raw VM disk data
        vm_name: VM identifier
        kyber_key: Kyber-1024 public key

    Returns:
        Encrypted disk with authentication tag

    Raises:
        EncryptionError: If encryption fails
    """
    # Implementation...

# ❌ BAD (no type hints, no docstring)
def encrypt_vm_disk(plaintext, vm_name, kyber_key):
    # Implementation...
```

**Naming Conventions:**
```python
# Variables & functions: snake_case
vm_manager = VMManager()
def start_virtual_machine(vm_name):
    pass

# Classes: PascalCase
class KyberKeyEncapsulation:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_VM_COUNT = 10
DEFAULT_CIPHER = "chacha20-poly1305"

# Private methods: _leading_underscore
def _internal_helper(self):
    pass
```

**Imports:**
```python
# Standard library (alphabetical)
import os
import sys
from pathlib import Path

# Third-party (alphabetical)
import numpy as np
from cryptography.hazmat.primitives import hashes

# Local modules (alphabetical)
from qwamos.crypto import kyber
from qwamos.vm import manager
```

**Type Hints:**
```python
# Always use type hints
from typing import List, Dict, Optional, Tuple

def create_vm(
    name: str,
    disk_size: int,
    ram_mb: int = 2048,
    kvm_enabled: bool = False
) -> Optional[VM]:
    """Create new virtual machine."""
    # Implementation...
```

### Commit Message Format

**Conventional Commits:**

```
[TYPE] Brief description (50 chars max)

Detailed explanation of what and why, not how.
Wrap at 72 characters.

Fixes: #123
See-Also: #456
```

**Types:**
- `[FEATURE]` - New functionality
- `[FIX]` - Bug fix
- `[SECURITY]` - Security fix (CVE, vulnerability)
- `[PHASE]` - Roadmap phase implementation
- `[DOC]` - Documentation update
- `[TEST]` - Test additions/modifications
- `[REFACTOR]` - Code refactoring (no functional change)
- `[PERF]` - Performance improvement
- `[CHORE]` - Build process, dependencies, etc.

**Examples:**
```
[FEATURE] Add Kyber-1024 key encapsulation module

Implements NIST FIPS 203 standard for post-quantum key encapsulation.
Uses reference implementation from PQClean project.

Fixes: #42
See-Also: phases/phase13_pqc_storage/

[SECURITY] Fix buffer overflow in QEMU network stack

CVE-2025-1234: Heap overflow in virtio-net packet handling.
Backported patch from QEMU upstream.

Credit: Security Researcher Name
```

---

## Module Structure

### Directory Layout

```
QWAMOS/
├── qwamos/                # Main Python package
│   ├── __init__.py
│   ├── vm/                # VM management
│   │   ├── manager.py     # VM lifecycle
│   │   ├── scheduler.py   # Resource allocation
│   │   ├── qemu.py        # QEMU backend
│   │   └── kvm.py         # KVM backend
│   ├── crypto/            # Cryptographic operations
│   │   ├── kyber.py       # Kyber-1024 KEM
│   │   ├── chacha20.py    # ChaCha20-Poly1305
│   │   ├── blake3.py      # BLAKE3 hashing
│   │   └── keyring.py     # Key management
│   ├── gateway/           # Anonymous networking
│   │   ├── tor.py
│   │   ├── i2p.py
│   │   └── firewall.py
│   ├── panic/             # Emergency wipe
│   │   ├── triggers.py
│   │   └── wipe.py
│   └── utils/             # Shared utilities
│       ├── logging.py
│       └── config.py
├── scripts/               # Bash scripts
│   ├── create_vm.sh
│   ├── start_vm.sh
│   └── init_qwamos.sh
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── kvm_hardware_suite/  # Hardware validation
├── phases/                # Roadmap phase planning
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── requirements-dev.txt   # Development dependencies
├── setup.py               # Package installer
├── Dockerfile             # Reproducible build environment
└── LICENSE                # AGPL-3.0
```

### Creating New Modules

**Template:**

```python
"""
Module: qwamos/new_module.py
Purpose: Brief description of module purpose

Author: QWAMOS Project
License: AGPL-3.0
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class NewFeature:
    """Brief class description.

    Detailed explanation of what this class does,
    its responsibilities, and usage examples.

    Attributes:
        config: Configuration dict
        state: Current state

    Example:
        >>> feature = NewFeature(config)
        >>> feature.do_something()
    """

    def __init__(self, config: dict):
        """Initialize NewFeature.

        Args:
            config: Configuration dictionary

        Raises:
            ValueError: If config is invalid
        """
        self.config = config
        self.state = "initialized"
        logger.info("NewFeature initialized")

    def do_something(self, param: str) -> bool:
        """Perform some operation.

        Args:
            param: Input parameter

        Returns:
            True if successful, False otherwise

        Raises:
            RuntimeError: If operation fails
        """
        try:
            # Implementation
            logger.debug(f"Processing {param}")
            return True
        except Exception as e:
            logger.error(f"Failed: {e}")
            raise RuntimeError(f"Operation failed: {e}")


def helper_function(input_data: bytes) -> str:
    """Brief function description.

    Args:
        input_data: Raw bytes

    Returns:
        Processed string
    """
    return input_data.decode('utf-8')
```

---

## Build & Test Workflow

### Running Tests

**Unit Tests:**
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_crypto.py

# Run specific test
pytest tests/test_crypto.py::test_kyber_keygen

# Run with coverage
pytest --cov=qwamos tests/

# Generate HTML coverage report
pytest --cov=qwamos --cov-report=html tests/
# Open htmlcov/index.html in browser
```

**Integration Tests:**
```bash
# Requires QEMU installed
pytest tests/integration/ --integration

# KVM hardware tests (requires /dev/kvm)
cd tests/kvm_hardware_suite/
./kvm_hardware_check.sh
python3 kvm_capability_report.py
```

**Differential Tests:**
```bash
cd tests/differential_kvm_qemu/
python3 diff_runner.py
python3 comparison_engine.py
```

### Reproducible Builds

**Build Docker Image:**
```bash
# Build reproducible environment
docker build -t qwamos-builder -f Dockerfile.build .

# Build QWAMOS inside container
docker run --rm -v $(pwd):/build qwamos-builder ./build_reproducible.sh

# Verify hash
sha256sum qwamos-v1.2.0.img
```

**Build Script:** `build_reproducible.sh`
```bash
#!/bin/bash
set -e

# Deterministic timestamps
export SOURCE_DATE_EPOCH=1700000000

# Fixed locale
export LC_ALL=C

# Reproducible Python bytecode
export PYTHONHASHSEED=0

# Build
python3 setup.py build

# Package
python3 setup.py sdist

# Generate checksum
sha256sum dist/*.tar.gz > SHA256SUMS
```

---

## Contributing Guidelines

### Pull Request Process

1. **Fork & Branch**
   ```bash
   git checkout -b feature/descriptive-name
   ```

2. **Implement Feature**
   - Write code following style guide
   - Add tests for new functionality
   - Update documentation (docstrings, wiki)

3. **Run Tests Locally**
   ```bash
   pytest tests/
   pylint qwamos/
   mypy qwamos/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "[FEATURE] Descriptive commit message"
   ```

5. **Push to Fork**
   ```bash
   git push origin feature/descriptive-name
   ```

6. **Create Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill out PR template
   - Link related issues

7. **Address Review Comments**
   - Make requested changes
   - Push additional commits
   - Request re-review

8. **Merge**
   - Maintainer will merge once approved
   - Delete feature branch after merge

### PR Checklist

Before submitting PR, ensure:

- [ ] Code follows PEP 8 style guide
- [ ] All tests pass (`pytest tests/`)
- [ ] New tests added for new functionality
- [ ] Documentation updated (docstrings, wiki)
- [ ] Commit messages follow conventional format
- [ ] No merge conflicts with master
- [ ] PR description explains what and why
- [ ] Related issues linked

### Code Review Standards

**Reviewers check for:**
- ✅ Correctness (does it work?)
- ✅ Security (no vulnerabilities?)
- ✅ Performance (no regressions?)
- ✅ Readability (clean code?)
- ✅ Tests (adequate coverage?)
- ✅ Documentation (clear?)

**Review Timeline:**
- Initial review: 7 days
- Follow-up: 3 days
- Final approval: 2 days

---

## Priority Contribution Areas

### 1. Android VM Integration ⭐⭐⭐

**Goal:** Compile full Android OS (AOSP) that runs inside QWAMOS VMs

**Tasks:**
- Build AOSP for ARM64
- Create QEMU-compatible Android images
- Integrate Google-free (MicroG) services
- Test popular apps (Signal, WhatsApp, etc.)

**Skills Needed:** Android build system, Java/Kotlin, ARM assembly

**Impact:** HIGH (enables real-world Android app usage)

### 2. React Native UI ⭐⭐

**Goal:** Modern mobile UI for QWAMOS management

**Tasks:**
- Design mockups (Figma)
- Implement React Native components
- Connect to QWAMOS API (gRPC)
- Add VM lifecycle controls (start, stop, snapshot)

**Skills Needed:** React Native, JavaScript/TypeScript, mobile UI/UX

**Impact:** MEDIUM (improves usability)

### 3. Hardware Testing ⭐⭐⭐

**Goal:** Validate KVM performance on real devices

**Tasks:**
- Run KVM hardware test suite
- Document device-specific quirks
- Create device compatibility matrix
- Submit performance benchmarks

**Skills Needed:** Android kernels, hardware debugging

**Impact:** HIGH (validates Phase XII KVM acceleration)

### 4. Security Audits ⭐⭐⭐

**Goal:** Independent security review of cryptographic implementations

**Tasks:**
- Audit Kyber-1024 integration
- Review ChaCha20-Poly1305 usage
- Pen-test VM isolation boundaries
- Fuzz-test panic wipe system

**Skills Needed:** Cryptography, security research, penetration testing

**Impact:** CRITICAL (ensures security guarantees)

### 5. Documentation ⭐

**Goal:** Improve user and developer documentation

**Tasks:**
- Add more wiki pages
- Create video tutorials
- Write blog posts
- Translate to other languages

**Skills Needed:** Technical writing, video editing

**Impact:** MEDIUM (lowers barrier to entry)

---

## Getting Help

**Communication Channels:**

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Q&A, ideas, general discussion
- **Email:** qwamos@tutanota.com
- **Matrix:** Coming soon

**Response Times:**
- Issues: 48 hours
- Pull Requests: 7 days
- Security reports: 24 hours

---

## License & CLA

**License:** AGPL-3.0

**Contributor License Agreement (CLA):**

By contributing to QWAMOS, you agree that:

1. Your contributions are your original work
2. You have the right to submit the contribution
3. Your contributions are licensed under AGPL-3.0
4. You grant QWAMOS project maintainers perpetual license to use your contributions

**No formal CLA signing required** - your first PR implies acceptance.

---

## Release Process

**Versioning:** Semantic Versioning (SemVer)
- **Major:** Breaking changes (e.g., 1.0.0 → 2.0.0)
- **Minor:** New features (e.g., 1.2.0 → 1.3.0)
- **Patch:** Bug fixes (e.g., 1.2.0 → 1.2.1)

**Release Cadence:**
- **Major:** Annually
- **Minor:** Quarterly
- **Patch:** As needed (security fixes immediately)

**Release Checklist:**
1. Update VERSION file
2. Update CHANGELOG.md
3. Run full test suite
4. Build reproducible binary
5. Generate SHA256SUMS
6. Create Git tag (`git tag v1.3.0`)
7. Push tag (`git push --tags`)
8. Create GitHub Release
9. Update documentation
10. Announce on social media

---

## Next Steps

- **[FAQ](FAQ):** Common developer questions
- **[Roadmap](Roadmap):** Upcoming features and phases
- **[Security Model](Security-Model):** Security implementation details

---

**[← Back to Home](Home)**
