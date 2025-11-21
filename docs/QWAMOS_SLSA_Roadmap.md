# QWAMOS SLSA 3/4 Compliance Roadmap

**Post-Quantum Mobile OS Supply Chain Assurance**

**Author:** Dezirae Stark, First Sterling Capital, LLC
**Version:** 1.0
**Date:** 2025-11-17
**Status:** Active Roadmap

---

## 1. Overview

### What is SLSA?

Supply-chain Levels for Software Artifacts (SLSA, pronounced "salsa") is a security framework developed by the Open Source Security Foundation (OpenSSF) and Google to protect software supply chains against tampering, unauthorized modifications, and malicious code injection. SLSA provides graduated security levels (1-4) with increasingly stringent requirements for build integrity, provenance, and reproducibility.

### QWAMOS and SLSA

QWAMOS is a post-quantum hardened mobile operating system that demands exceptional supply chain security. As a project designed to resist nation-state adversaries, hardware tampering, and sophisticated supply chain attacks, achieving SLSA Level 3+ certification is a natural alignment with our security philosophy.

**Strategic Goals:**
- **SLSA Level 3:** Reproducible builds, non-forgeable provenance, isolated build environment (Target: 12-18 months)
- **SLSA Level 4:** Hermetic builds, two-person review, hardware-backed signing (Aspirational: 18-36 months)

This roadmap documents our current baseline, maps existing capabilities to SLSA requirements, and defines concrete milestones for achieving higher assurance levels.

---

## 2. Current State (Baseline)

QWAMOS has already implemented significant supply chain security controls:

### Existing Security Controls

#### ✅ Code Integrity & Signing
- **Signed Git Commits:** All commits signed with Ed448 GPG key (Fingerprint: `18C4E89E37D5ECD392F52E85269CD0658D8BD942DCF33BE4E37CC94933E4C4D2`)
- **Release Tagging:** Cryptographically signed release tags
- **Public Key Distribution:** GPG public keys published in repository (`gpg_public_key.asc`, `desirae_public.asc`)

#### ✅ Documentation & Transparency
- **SECURITY.md:** Comprehensive vulnerability disclosure policy with severity classifications
- **SUPPLYCHAIN.md:** Full dependency inventory with checksums and trust model definitions
- **Checksum Files:** SHA-256 checksums for Phase 7 and Phase 8 releases

#### ✅ Automated Security Scanning
- **GitHub Actions Workflows:**
  - CodeQL static analysis for security vulnerabilities
  - Secret scanning to prevent credential leaks
  - SBOM (Software Bill of Materials) generation
  - Forensic audit workflows
- **Dependency Scanning:** Automated CVE tracking via GitHub security advisories

#### ✅ Build Reproducibility Foundations
- **Documented Build Process:** Build scripts in `build/scripts/`, `tools/`, and component directories
- **Dependency Pinning:** Fixed versions documented in SUPPLYCHAIN.md
- **Source Transparency:** All build configurations version-controlled

### Current SLSA Mapping
Based on our existing controls, QWAMOS currently operates at approximately **SLSA Level 1-2**:
- ✅ Version control (GitHub)
- ✅ Build scripts
- ✅ Basic provenance (commit signatures)
- ⚠️ Partial reproducibility (documented but not enforced)
- ❌ Non-forgeable provenance (not yet implemented)
- ❌ Hermetic builds (not yet implemented)

---

## 3. SLSA Level 1-2 Mapping

| SLSA Requirement | Status | Implementation Notes |
|-----------------|--------|---------------------|
| **Version Controlled Source** | ✅ Complete | GitHub repository with full history |
| **Build Scripts** | ✅ Complete | Build automation in `build/`, `tools/`, makefiles |
| **Build Service** | ⚠️ Partial | Manual builds + GitHub Actions (not enforced for releases) |
| **Provenance Available** | ✅ Complete | Signed commits, release tags, checksum files |
| **Provenance Authenticated** | ✅ Complete | GPG signatures (Ed448) |
| **Service-Generated Provenance** | ⚠️ Partial | GitHub Actions generates artifacts but not full SLSA provenance |

**Assessment:** QWAMOS meets most SLSA Level 2 requirements. Primary gap: formalized provenance attestations in standardized format.

---

## 4. SLSA Level 3 Roadmap

SLSA Level 3 requires:
1. **Non-forgeable provenance:** Cryptographically signed attestations that cannot be tampered with
2. **Isolated build environment:** Builds run in ephemeral, controlled environments
3. **Reproducible builds:** Identical source → identical artifacts
4. **Retention policy:** Build logs and provenance stored for audit

### Concrete Action Items

#### 4.1 Implement SLSA Provenance Generation (Priority: High)
**Timeline:** 0-6 months

**Tasks:**
- [ ] Adopt [in-toto attestation format](https://in-toto.io/) for build provenance
- [ ] Generate provenance metadata for each release artifact:
  - Builder identity (GitHub Actions runner)
  - Build timestamp
  - Dependency checksums
  - Build command invocation
  - Output artifact hashes
- [ ] Sign provenance with Ed448 key (existing `desirae_public.asc`)
- [ ] Store provenance alongside release artifacts (e.g., `QWAMOS-v1.0.0-provenance.jsonl`)

**Deliverable:** Signed provenance files for bootloader, kernel, initramfs, UI APK

---

#### 4.2 Reproducible Build System (Priority: High)
**Timeline:** 3-12 months

**Tasks:**
- [ ] **Bootloader (U-Boot):**
  - Pin compiler version (Clang 21.1.3)
  - Freeze build environment (Termux package versions)
  - Document build flags in `.buildconfig`
  - Verify: Independent builds produce identical `u-boot` binary

- [ ] **Kernel:**
  - Pin Debian chroot version (Debian 12 Bookworm)
  - Lock kernel config (`kernel/qwamos_defconfig`)
  - Timestamp normalization (SOURCE_DATE_EPOCH)
  - Verify: Independent builds produce identical `Image` binary

- [ ] **Initramfs:**
  - Pin BusyBox version (v1.37.0 static)
  - CPIO archive with deterministic ordering
  - Verify: Identical `initramfs.cpio.gz`

- [ ] **UI Components:**
  - React Native: Pin Node.js and npm versions
  - Flutter: Pin Dart SDK version
  - Lock dependency files (`package-lock.json`, `pubspec.lock`)

**Verification:**
- Establish "reproducible build verification" process
- Independent third-party should reproduce checksums
- Document variance (if any) and root cause

**Deliverable:** Reproducible build documentation + verification script

---

#### 4.3 Isolated Build Environment (Priority: Medium)
**Timeline:** 6-12 months

**Tasks:**
- [ ] Migrate CI builds to containerized environments:
  - Docker/Podman images with pinned base OS
  - No network access during build (hermetic-lite)
  - Snapshot build dependencies
- [ ] Create build recipes:
  - `Dockerfile.bootloader`
  - `Dockerfile.kernel`
  - `Dockerfile.ui`
- [ ] Enforce ephemeral builds:
  - Fresh container per build
  - No persistent state between builds

**Deliverable:** Containerized build system with isolation guarantees

---

#### 4.4 SBOM Integration (Priority: Medium)
**Timeline:** 0-6 months

**Tasks:**
- [ ] Generate SBOM for each release in standardized format:
  - CycloneDX JSON/XML
  - SPDX format
- [ ] Include SBOM in provenance metadata
- [ ] Automate SBOM diffing between releases
- [ ] Publish SBOMs alongside releases

**Deliverable:** SBOM files for all Phase 11+ releases

---

#### 4.5 Build Audit Logs (Priority: Low)
**Timeline:** 6-18 months

**Tasks:**
- [ ] Archive full GitHub Actions build logs
- [ ] Retain provenance metadata for 2+ years
- [ ] Implement tamper-evident log storage (e.g., append-only S3)

**Deliverable:** Audit trail retention policy document

---

## 5. SLSA Level 4 Aspirational Targets

SLSA Level 4 represents the highest assurance level and requires:
1. **Hermetic builds:** Zero external network access during build
2. **Two-person review:** All changes reviewed by at least two trusted persons
3. **Hardware-backed signing:** Signing keys stored in HSM or hardware token

### Aspirational Goals (18-36 months)

#### 5.1 Fully Hermetic Builds
**Challenge:** Current builds download dependencies from PyPI, npm, apt repositories

**Solution Path:**
- Pre-cache all dependencies in version-controlled `vendor/` directory
- Verify checksums before build
- Block network access via build container network policies

**Effort:** High (requires dependency vendoring infrastructure)

---

#### 5.2 Two-Person Review
**Challenge:** Solo-maintained project (Dezirae Stark)

**Solution Path:**
- Establish trusted reviewer pool (security researchers, contributors)
- Require PR approval from 1+ trusted reviewer for merge
- Use branch protection rules on GitHub

**Effort:** Medium (requires community building)

---

#### 5.3 Hardware-Backed Signing
**Challenge:** GPG keys stored in software (Termux environment)

**Solution Path:**
- Migrate to hardware security token:
  - YubiKey 5 NFC (supports OpenPGP Ed25519, compatible with Ed448 via custom firmware)
  - Nitrokey Pro 2 (OpenPGP 3.3 compliant)
- Store signing key in HSM (e.g., AWS CloudHSM for CI/CD)
- Require hardware token for all release signatures

**Effort:** Medium (hardware acquisition + key migration)

---

#### 5.4 Build Environment Attestation
**Challenge:** Proving build environment integrity

**Solution Path:**
- Implement Trusted Platform Module (TPM) measurements
- Remote attestation of build VMs
- Measured boot chain for build infrastructure

**Effort:** Very High (requires TPM-enabled infrastructure)

---

## 6. Implementation Timeline

### Short-Term (0-6 months)
- ✅ Complete this SLSA roadmap document
- 🔄 Implement in-toto provenance generation
- 🔄 Generate SBOMs in CycloneDX/SPDX format
- 🔄 Publish provenance with next release (v1.1.0)

### Mid-Term (6-18 months)
- 🔄 Achieve reproducible builds for bootloader + kernel
- 🔄 Containerized build environment (Docker-based)
- 🔄 Establish two-person review policy
- 🔄 SLSA Level 3 certification (informal self-assessment)

### Long-Term (18-36 months)
- 🔄 Fully hermetic builds (vendored dependencies)
- 🔄 Hardware-backed signing (YubiKey/Nitrokey)
- 🔄 SLSA Level 4 aspirational targets
- 🔄 Third-party SLSA audit (formal certification)

---

## 7. Governance and Ownership

### Project Ownership
**QWAMOS** is maintained by **First Sterling Capital, LLC**, with **Dezirae Stark** as the primary developer and security architect.

### Responsibilities
- **Security Policy:** Defined in `SECURITY.md`
- **Supply Chain:** Documented in `SUPPLYCHAIN.md`
- **Build Process:** Scripts in `build/`, `tools/`, GitHub Actions
- **SLSA Compliance:** This roadmap document + future provenance artifacts

### Contact
For questions regarding SLSA compliance or supply chain security:
- **Email:** qwamos@tutanota.com (PGP encrypted preferred)
- **GitHub Issues:** https://github.com/Dezirae-Stark/QWAMOS/issues (non-sensitive only)

---

## 8. External Resources

- **SLSA Framework:** https://slsa.dev/
- **in-toto Project:** https://in-toto.io/
- **SBOM Standards:**
  - CycloneDX: https://cyclonedx.org/
  - SPDX: https://spdx.dev/
- **Reproducible Builds:** https://reproducible-builds.org/

---

## 9. Changelog

- **2025-11-17:** Initial SLSA roadmap published (v1.0)
- *(Future milestones will be documented here)*

---

**Commitment Statement**

QWAMOS is committed to achieving SLSA Level 3 certification within 18 months and will make best-effort progress toward Level 4 aspirational goals. This roadmap will be updated quarterly to reflect implementation progress.

---

© 2025 First Sterling Capital, LLC · QWAMOS Project
Licensed under AGPL-3.0
