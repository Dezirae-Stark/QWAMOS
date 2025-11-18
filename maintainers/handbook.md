# QWAMOS Maintainer Handbook

**Version**: 1.0
**Last Updated**: November 2025
**Status**: Active

This handbook defines the governance, processes, and responsibilities for QWAMOS project maintainers.

---

## Table of Contents

1. [Governance Model](#section-1--governance-model)
2. [PR Review Process](#section-2--pr-review-process)
3. [Issue Triage Guidelines](#section-3--issue-triage-guidelines)
4. [Branch Protection Rules](#section-4--branch-protection-rules)
5. [Release Engineering](#section-5--release-engineering)
6. [Documentation Requirements](#section-6--documentation-requirements)
7. [Security Responsibilities](#section-7--security-responsibilities)
8. [Contacts & Communication](#section-8--contacts--communication)

---

## SECTION 1 — Governance Model

### 1.1 Maintainer Roles

QWAMOS uses a tiered maintainer structure:

#### Lead Maintainer
- **Responsibilities**:
  - Final decision authority on technical disputes
  - Release approval and signing
  - Security disclosure coordination
  - Strategic direction and roadmap
  - Maintainer onboarding/offboarding
- **Requirements**:
  - 2+ years active contribution to QWAMOS
  - Deep knowledge of PQC, VM isolation, and gateway architecture
  - Trusted GPG key for release signing

#### Core Maintainers
- **Responsibilities**:
  - Code review and PR merging
  - Issue triage and labeling
  - Security vulnerability assessment
  - Feature implementation approval
  - Documentation oversight
- **Requirements**:
  - 1+ year active contribution
  - Expertise in at least one QWAMOS subsystem (crypto, VM, gateway, UI)
  - Demonstrated security-first mindset

#### Module Maintainers
- **Focus Areas**:
  - **Crypto Module**: Post-quantum cryptography (Kyber, ChaCha20, BLAKE3)
  - **VM Module**: QEMU, PRoot, Chroot isolation
  - **Gateway Module**: Tor, I2P, DNSCrypt integration
  - **UI Module**: React Native, Android frontend
  - **Build System**: CI/CD, release automation
- **Responsibilities**:
  - Expert review in their domain
  - Security assessment of module-specific PRs
  - Performance testing and benchmarking
  - Documentation for their module

#### Emeritus Maintainers
- Former maintainers who have stepped back
- Retain commit access (view-only)
- Advisory role, no active review duties

### 1.2 Review Responsibilities

All maintainers must:
- **Respond to PRs within 48 hours** (acknowledge, even if full review pending)
- **Complete reviews within 7 days** for standard PRs
- **Complete reviews within 24 hours** for security patches
- **Test changes locally** before approval (no "LGTM without testing")
- **Verify CI passes** before merging
- **Check for breaking changes** and update CHANGELOG

### 1.3 Decision-Making Rules

#### Consensus Model
- **Standard PRs**: 1 maintainer approval required
- **Security-sensitive PRs**: 2 maintainer approvals required (one must be Lead or Core)
- **Breaking changes**: 2 core maintainer approvals + 7-day comment period
- **Architecture changes**: Lazy consensus (proposal + 14-day comment period, no blocking objections)

#### Voting
When consensus cannot be reached:
1. Discussion period: 7 days minimum
2. Vote called by Lead Maintainer
3. Simple majority of Core Maintainers
4. Lead Maintainer breaks ties

#### Veto Power
- Lead Maintainer has veto power on security-critical decisions
- Must provide written justification within 48 hours

### 1.4 Release Manager Duties

**Rotating Role**: Assigned per release cycle (typically 1 month)

**Pre-Release** (2 weeks before target):
- Create release tracking issue
- Review merged PRs since last release
- Identify blocking issues
- Coordinate with module maintainers on readiness

**Release Week**:
- Run automated security scans
- Execute full test suite (VM isolation, gateway, PQC)
- Update version numbers and CHANGELOG
- Create release branch (`release/vX.Y.Z`)
- Tag release with signed GPG tag
- Trigger release-generator workflow
- Build and test VM templates
- Generate release notes
- Publish GitHub Release
- Update documentation site

**Post-Release**:
- Monitor for critical issues (48 hours)
- Coordinate hotfix releases if needed
- Update release metrics
- Hand off to next Release Manager

---

## SECTION 2 — PR Review Process

### 2.1 Required Checks

All PRs must pass:

#### Automated Checks
- ✅ **CI Build**: All workflows pass
- ✅ **Linting**: CodeQL, Semgrep, Bandit (zero critical/high issues)
- ✅ **Tests**: Unit tests, integration tests, security tests
- ✅ **Code Coverage**: No regression in coverage (>80% for new code)
- ✅ **VM Templates**: If modified, all templates build successfully
- ✅ **Documentation**: Docs build without errors

#### Manual Checks (Reviewer Responsibility)
- ✅ **Code Quality**: Readable, well-structured, follows project conventions
- ✅ **Security Review**: No vulnerabilities introduced
- ✅ **Performance**: No significant regressions
- ✅ **Breaking Changes**: Documented and justified
- ✅ **Tests**: Adequate test coverage for new code
- ✅ **Documentation**: Updated for user-facing changes

### 2.2 Security-First Review Rules

**CRITICAL**: Security always takes precedence over features.

For all PRs, verify:

1. **Input Validation**
   - All user inputs sanitized
   - No command injection vectors
   - Path traversal prevention
   - SQL injection prevention (if applicable)

2. **Cryptography Usage**
   - Only approved algorithms: Kyber-1024, ChaCha20-Poly1305, BLAKE3, Argon2id
   - No use of deprecated/weak crypto: AES, Serpent, Twofish, SHA-1, MD5
   - Proper key generation (cryptographically secure RNG)
   - No hardcoded keys or secrets

3. **Authentication & Authorization**
   - Proper authentication checks
   - Least privilege principle
   - No privilege escalation paths

4. **Memory Safety**
   - No buffer overflows
   - Proper bounds checking
   - No use-after-free vulnerabilities

5. **Dependency Security**
   - No new dependencies with known vulnerabilities
   - License compatibility check (AGPL-3.0)
   - Supply chain verification

### 2.3 Crypto Module Verification

**Crypto module PRs require special scrutiny**:

#### Mandatory Steps:
1. **Algorithm Review**
   - Verify NIST PQC compliance (for PQC changes)
   - Check for side-channel resistance
   - Validate constant-time operations (timing-safe comparisons)

2. **Implementation Review**
   - Cross-reference with liboqs reference implementation
   - Verify parameter choices (e.g., Kyber security level)
   - Check for proper error handling

3. **Testing Requirements**
   - Known Answer Tests (KAT) must pass
   - Fuzzing for at least 1 hour
   - Timing analysis for constant-time operations
   - Negative test cases (invalid inputs)

4. **Documentation**
   - Algorithm choice justification
   - Security proofs or references
   - Performance benchmarks
   - Migration path (if changing existing crypto)

### 2.4 Gateway Regression Tests

**Gateway changes must not break anonymization**:

Before approving gateway PRs:

1. **Tor Connectivity**
   ```bash
   # Run gateway test suite
   ./tests/gateway/test_gateway_security.sh

   # Verify Tor circuit
   curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
   ```

2. **I2P Functionality**
   - Check I2P router status
   - Verify tunnel creation
   - Test .i2p domain resolution

3. **DNSCrypt Fallback**
   - Verify DNS-over-HTTPS works
   - Test fallback to Cloudflare/Quad9
   - Check for DNS leaks

4. **Network Isolation**
   - Confirm default DROP firewall policy
   - Verify VPN-only egress
   - Test block-without-gateway rules

5. **Performance**
   - Measure latency impact (<20% regression acceptable)
   - Test under load (100 concurrent connections)
   - Check memory usage (no leaks)

---

## SECTION 3 — Issue Triage Guidelines

### 3.1 Label Definitions

#### Priority Labels
- **`priority: critical`**: Security vulnerability, data loss, system crash
  - Response: Within 4 hours
  - Resolution: Within 24-48 hours

- **`priority: high`**: Major bug, feature regression, broken core functionality
  - Response: Within 24 hours
  - Resolution: Within 1 week

- **`priority: medium`**: Minor bug, enhancement request, documentation issue
  - Response: Within 1 week
  - Resolution: Next release cycle

- **`priority: low`**: Nice-to-have, cosmetic issue, optimization
  - Response: Best effort
  - Resolution: When time permits

#### Type Labels
- **`type: bug`**: Something broken or not working as intended
- **`type: enhancement`**: New feature or improvement
- **`type: security`**: Security vulnerability or hardening
- **`type: documentation`**: Documentation improvement
- **`type: performance`**: Performance optimization
- **`type: question`**: Support or clarification request
- **`type: duplicate`**: Duplicate of existing issue
- **`type: wontfix`**: Not planned for implementation

#### Component Labels
- **`component: crypto`**: Post-quantum cryptography (Kyber, ChaCha20, BLAKE3)
- **`component: vm`**: VM isolation (QEMU, PRoot, Chroot)
- **`component: gateway`**: Network anonymization (Tor, I2P, DNSCrypt)
- **`component: ui`**: User interface (React Native, Android)
- **`component: build`**: Build system, CI/CD, workflows
- **`component: docs`**: Documentation, wiki, website

#### Status Labels
- **`status: triaged`**: Reviewed and categorized
- **`status: in-progress`**: Actively being worked on
- **`status: blocked`**: Waiting on dependency or decision
- **`status: needs-info`**: Waiting for more information from reporter
- **`status: ready-for-review`**: PR submitted, awaiting review

### 3.2 Security vs Bug vs Enhancement Handling

#### Security Issues
**DO NOT** file as public issues. Follow private disclosure:
1. Reporter emails `qwamos@tutanota.com`
2. Lead Maintainer acknowledges within 24 hours
3. Assessment within 72 hours (CVSS scoring)
4. Private patch development
5. Coordinated disclosure (90 days or less)
6. Public advisory after fix released

If accidentally filed publicly:
1. Immediately mark as `type: security`
2. Lock issue (disable comments)
3. Contact reporter to delete or redact
4. Move to private security advisory
5. Follow standard disclosure process

#### Bug Reports
**Triage Checklist**:
- [ ] Reproducible? (ask for steps if not clear)
- [ ] Version affected? (check if fixed in latest)
- [ ] Impact severity? (data loss, crash, minor glitch)
- [ ] Component? (crypto, vm, gateway, ui, build, docs)
- [ ] Priority? (critical, high, medium, low)
- [ ] Labels applied
- [ ] Assigned to module maintainer (if clear ownership)

#### Enhancement Requests
**Evaluation Criteria**:
1. **Alignment with QWAMOS goals** (privacy, security, anonymity)
2. **Complexity** (effort required vs benefit)
3. **Security impact** (does it introduce new attack surface?)
4. **Maintenance burden** (ongoing support cost)
5. **Community interest** (👍 reactions, discussion)

**Process**:
1. Add `type: enhancement` label
2. Add `status: needs-discussion` if unclear
3. Request RFC (Request for Comments) for large changes
4. Lazy consensus period (14 days)
5. If approved: add to roadmap, assign milestone

### 3.3 Escalation Paths

#### Path 1: Bug → Critical Bug
Trigger: Bug causes data loss, security breach, or system crash

1. Module Maintainer → Core Maintainer
2. Add `priority: critical` label
3. Create hotfix branch
4. Fast-track review (24 hours)
5. Emergency release if needed

#### Path 2: Enhancement → Architecture Change
Trigger: Enhancement requires significant architectural changes

1. Module Maintainer → Core Maintainers
2. Request RFC document
3. Design review meeting (all Core Maintainers)
4. Lazy consensus period (14 days)
5. Final decision by Lead Maintainer if no consensus

#### Path 3: Security Disclosure → Emergency Response
Trigger: Active exploit or critical vulnerability

1. Reporter → Lead Maintainer (`qwamos@tutanota.com`)
2. Lead Maintainer → All Core Maintainers (private channel)
3. Immediate assessment (CVSS scoring)
4. Emergency patch development (parallel work)
5. Coordinated disclosure (can be <90 days for active exploits)
6. Public advisory + patch release

---

## SECTION 4 — Branch Protection Rules

### 4.1 Main Branch Requirements

**Branch**: `master` (primary stable branch)

**Protection Settings**:
- ✅ **Require pull request reviews**: 1 approval minimum (2 for security-sensitive)
- ✅ **Require status checks**: All CI workflows must pass
- ✅ **Require signed commits**: GPG-signed commits only
- ✅ **Require linear history**: No merge commits (rebase only)
- ✅ **Include administrators**: Rules apply to maintainers too
- ✅ **Restrict push access**: Only maintainers with write access
- ✅ **Restrict force push**: Disabled
- ✅ **Restrict deletions**: Disabled

**Required Status Checks**:
- CI Build (all workflows pass)
- CodeQL Security Scan
- Linting (Semgrep, Bandit, ShellCheck)
- Unit Tests (>80% coverage)
- Integration Tests
- VM Template Builds (if modified)
- Documentation Build

**Merge Strategy**:
- Squash and merge (for feature PRs)
- Rebase and merge (for hotfixes)
- Never merge commits (keep linear history)

### 4.2 Dev Branch Flow

**Branch**: `dev` (integration branch)

**Purpose**: Staging area for next release

**Protection Settings**:
- ✅ **Require pull request reviews**: 1 approval
- ✅ **Require status checks**: CI must pass
- ❌ **Require signed commits**: Optional (but recommended)
- ❌ **Require linear history**: Merge commits allowed

**Workflow**:
1. Feature branches merge to `dev`
2. `dev` undergoes integration testing
3. Release Manager creates `release/vX.Y.Z` from `dev`
4. Release branch merges to `master` after final testing
5. `master` back-merges to `dev` after release

**Branch Lifecycle**:
```
feature/user-auth → dev → release/v1.2.0 → master
                      ↖                       ↓
                        ←←←←←←←←←←←←←←←←←←←←←←
                             (back-merge)
```

### 4.3 Release Tagging Process

**Tag Format**: `vMAJOR.MINOR.PATCH` (semantic versioning)

**Examples**:
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.1.1` - Patch release (bug fixes)
- `v1.2.0-rc.1` - Release candidate
- `v1.2.0-beta.1` - Beta release

**Tagging Steps**:

1. **Create Release Branch**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b release/v1.2.0
   ```

2. **Update Version Files**
   ```bash
   # Update VERSION file
   echo "v1.2.0" > VERSION

   # Update package.json (if exists)
   npm version 1.2.0 --no-git-tag-version

   # Update CHANGELOG.md (use release-generator workflow)
   ```

3. **Commit Version Bump**
   ```bash
   git add VERSION CHANGELOG.md package.json
   git commit -S -m "chore: Bump version to v1.2.0"
   ```

4. **Create Signed Tag**
   ```bash
   git tag -s v1.2.0 -m "Release v1.2.0"

   # Verify signature
   git tag -v v1.2.0
   ```

5. **Push Tag**
   ```bash
   git push origin v1.2.0
   ```

6. **Merge to Master**
   ```bash
   git checkout master
   git merge --no-ff release/v1.2.0
   git push origin master
   ```

7. **Back-merge to Dev**
   ```bash
   git checkout dev
   git merge --no-ff master
   git push origin dev
   ```

8. **Delete Release Branch** (optional)
   ```bash
   git branch -d release/v1.2.0
   git push origin --delete release/v1.2.0
   ```

---

## SECTION 5 — Release Engineering

### 5.1 How to Cut a Stable Release

**Timeline**: Releases typically occur monthly (first Monday of each month)

**Roles**:
- **Release Manager**: Coordinates release process
- **Module Maintainers**: Verify their components are ready
- **Lead Maintainer**: Final approval and signing

**Release Process** (Standard Release):

#### T-14 days: Planning Phase
1. **Create Release Tracking Issue**
   - Title: `Release v1.2.0 Tracking`
   - Checklist of blocking issues
   - Feature freeze announcement
   - Assign to Release Manager

2. **Review Merged PRs**
   ```bash
   # List PRs since last release
   gh pr list --state merged --base master --since "2025-10-01"
   ```

3. **Identify Blockers**
   - Critical bugs
   - Security vulnerabilities
   - Breaking changes needing documentation

#### T-7 days: Feature Freeze
1. **Announce Feature Freeze**
   - Post to GitHub Discussions
   - Update tracking issue
   - Only bug fixes allowed after this point

2. **Create Release Branch**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b release/v1.2.0
   git push origin release/v1.2.0
   ```

3. **Run Full Test Suite**
   - Automated tests (CI)
   - Manual testing (VM templates, gateway, UI)
   - Performance benchmarks
   - Security scans

#### T-3 days: Release Candidate
1. **Tag Release Candidate**
   ```bash
   git tag -s v1.2.0-rc.1 -m "Release Candidate 1 for v1.2.0"
   git push origin v1.2.0-rc.1
   ```

2. **Build and Test RC**
   - Trigger VM template builds
   - Test on multiple platforms (Android, Linux, macOS)
   - Community testing (invite select users)

3. **Fix Critical Issues**
   - Cherry-pick fixes to release branch
   - Create RC2 if needed

#### T-0 days: Release Day
1. **Final Checks**
   - All CI passes
   - All blockers resolved
   - Documentation updated
   - CHANGELOG generated

2. **Update Version Numbers**
   ```bash
   echo "v1.2.0" > VERSION
   git add VERSION
   git commit -S -m "chore: Bump version to v1.2.0"
   ```

3. **Create Signed Tag**
   ```bash
   git tag -s v1.2.0 -m "$(cat <<EOF
   Release v1.2.0

   See CHANGELOG.md for full details.

   Notable changes:
   - Added Kyber-1024 key rotation
   - Improved VM isolation with seccomp
   - Updated Tor to latest stable

   SHA256 checksums:
   <checksums will be added by release workflow>
   EOF
   )"

   git push origin v1.2.0
   ```

4. **Trigger Release Workflow**
   - GitHub Actions automatically triggers on tag push
   - Builds VM templates
   - Generates release notes
   - Uploads artifacts
   - Creates GitHub Release

5. **Publish Release**
   - Review auto-generated release notes
   - Add any manual notes
   - Publish (switch from draft if needed)

6. **Announce Release**
   - GitHub Discussions
   - Project website
   - Social media (if applicable)

#### T+2 days: Post-Release
1. **Monitor for Issues**
   - Watch GitHub Issues
   - Monitor community feedback
   - Check crash reports

2. **Hotfix if Needed**
   - Critical bugs get immediate hotfix release
   - Follow expedited process (see below)

3. **Back-merge to Dev**
   ```bash
   git checkout dev
   git merge --no-ff master
   git push origin dev
   ```

### 5.2 Versioning Scheme (Semantic Versioning)

QWAMOS follows **Semantic Versioning 2.0.0**: `MAJOR.MINOR.PATCH`

#### MAJOR Version (X.0.0)
**Increment when**: Breaking changes to public API or architecture

**Examples**:
- Removing support for a VM type
- Changing crypto algorithm (e.g., Kyber upgrade that breaks existing keys)
- Major UI redesign that changes user workflows
- Removing deprecated features

**Release Frequency**: ~1 year

#### MINOR Version (1.X.0)
**Increment when**: New features in backward-compatible manner

**Examples**:
- Adding new VM template type
- Adding new gateway protocol
- New UI features
- Performance improvements
- Security hardening (non-breaking)

**Release Frequency**: ~1 month

#### PATCH Version (1.1.X)
**Increment when**: Backward-compatible bug fixes

**Examples**:
- Fixing VM isolation bug
- Gateway connectivity fix
- UI crash fixes
- Documentation corrections
- Dependency updates (security)

**Release Frequency**: As needed (typically 1-2 weeks for critical fixes)

#### Pre-release Identifiers
- **Alpha**: `v1.2.0-alpha.1` - Early testing, unstable
- **Beta**: `v1.2.0-beta.1` - Feature complete, testing phase
- **RC**: `v1.2.0-rc.1` - Release candidate, final testing

**Rules**:
- Pre-release versions MUST NOT be used in production
- Each pre-release increments the identifier (alpha.1 → alpha.2)
- Promotion path: alpha → beta → rc → stable

### 5.3 How to Run Release-Generator Workflow

The `release-generator.yml` workflow automates CHANGELOG generation and GitHub Release creation.

**Trigger Methods**:

#### Method 1: Manual Workflow Dispatch
1. Go to **Actions** → **Release Generator**
2. Click **Run workflow**
3. Fill in parameters:
   - **Version**: `v1.2.0`
   - **Release Type**: `Minor Release`
   - **Prerelease**: `false`
   - **Draft**: `false`
4. Click **Run workflow**

#### Method 2: GitHub CLI
```bash
gh workflow run release-generator.yml \
  -f version="v1.2.0" \
  -f release_type="Minor Release" \
  -f prerelease=false \
  -f draft=false
```

#### Method 3: Automatic on Tag Push
```bash
# Pushing a tag automatically triggers the workflow
git tag -s v1.2.0 -m "Release v1.2.0"
git push origin v1.2.0
```

**Workflow Process**:
1. **Parse Commits**: Analyzes commits since last release
2. **Categorize Changes**: Groups by type (security, features, fixes, etc.)
3. **Generate CHANGELOG**: Creates structured changelog
4. **Build Artifacts**: Triggers VM template builds
5. **Create GitHub Release**: Publishes release with notes and artifacts
6. **Commit CHANGELOG**: Updates repository with new changelog

**Output**:
- Updated `CHANGELOG.md` in repository
- GitHub Release with:
  - Auto-generated release notes
  - VM template artifacts
  - Checksums (SHA256/SHA512)
  - Installation instructions

---

## SECTION 6 — Documentation Requirements

### 6.1 Wiki Update Rules

**When to Update Wiki**:
- New features require user-facing documentation
- Architecture changes need design documentation
- Security updates require advisory notices
- Deprecations need migration guides

**Wiki Structure**:
```
Home
├── Overview
├── Installation & Setup Guide
├── Architecture
│   ├── System Architecture
│   ├── Security Model
│   └── Component Diagrams
├── User Guides
│   ├── VM Creation
│   ├── Gateway Configuration
│   └── Security Hardening
├── Developer Guide
│   ├── Build Instructions
│   ├── Contributing
│   └── API Reference
├── FAQ
└── Roadmap
```

**Update Process**:
1. Edit wiki pages locally:
   ```bash
   git clone https://github.com/Dezirae-Stark/QWAMOS.wiki.git
   cd QWAMOS.wiki
   # Edit .md files
   git commit -m "docs: Update VM creation guide"
   git push origin master
   ```

2. Or use GitHub web editor (for minor changes)

3. Verify sync to `/docs/wiki/` via doc-sync workflow

**Review Requirements**:
- Technical accuracy verified by module maintainer
- No sensitive information (private keys, credentials)
- Links work (checked by nightly link validation)
- Consistent formatting (Markdown linting)

### 6.2 Docs Site Updates

**Documentation Site**: https://dezirae-stark.github.io/QWAMOS

**When to Update**:
- Every release (automatic via workflows)
- New features with user-facing changes
- Security advisories
- Deprecation notices

**Manual Updates**:

1. **Edit Markdown Files**:
   ```bash
   # Edit files in /docs directory
   vim docs/ANDROID_VM_SETUP_GUIDE.md
   ```

2. **Test Locally** (optional):
   ```bash
   cd docs
   bundle install
   bundle exec jekyll serve
   # Visit http://localhost:4000/QWAMOS
   ```

3. **Commit and Push**:
   ```bash
   git add docs/
   git commit -m "docs: Update Android VM setup guide"
   git push origin master
   ```

4. **Verify Deployment**:
   - GitHub Actions builds Jekyll site
   - Deploys to GitHub Pages
   - Check https://dezirae-stark.github.io/QWAMOS

**Automated Updates**:
- **README Sync**: `doc-sync.yml` syncs README.md to docs/
- **Wiki Sync**: `doc-sync.yml` syncs wiki to docs/wiki/
- **Banner Updates**: `readme-banner.yml` updates badges

**Navigation Updates**:
- Edit `docs/navigation.yml` to add/remove pages
- Update `docs/_config.yml` for site-wide settings

### 6.3 Commit Requirements

**Commit Message Format** (Conventional Commits):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `build`: Build system or dependencies
- `ci`: CI/CD changes
- `chore`: Other changes (e.g., version bumps)
- `security`: Security fixes or hardening

**Scopes** (component affected):
- `crypto`: Cryptography module
- `vm`: VM isolation
- `gateway`: Network anonymization
- `ui`: User interface
- `build`: Build system
- `docs`: Documentation

**Examples**:

```
feat(crypto): Add Kyber-1024 key rotation support

Implements automatic key rotation for Kyber-1024 keypairs
after 30 days or 10,000 uses, whichever comes first.

Closes #123
```

```
fix(gateway): Resolve Tor circuit timeout issue

Increases Tor circuit build timeout from 60s to 120s
to handle slow guard relays.

Fixes #456
```

```
security(vm): Patch privilege escalation in chroot launcher

Addresses CVE-2025-XXXX by adding capability dropping
before entering chroot environment.

BREAKING CHANGE: Requires kernel 4.4+ for capability support
```

**Commit Signing**:
- All commits to `master` MUST be GPG-signed
- Configure GPG key:
  ```bash
  git config --global user.signingkey <KEY_ID>
  git config --global commit.gpgsign true
  ```
- Verify signature:
  ```bash
  git log --show-signature
  ```

**Commit Best Practices**:
- **Atomic commits**: One logical change per commit
- **Descriptive**: Subject line summarizes change
- **Detailed body**: Explain why, not just what
- **References**: Link to issues/PRs (`Closes #123`, `Fixes #456`)
- **Breaking changes**: Clearly marked in footer
- **Signed**: GPG signature for authenticity

---

## SECTION 7 — Security Responsibilities

### 7.1 Handling Private Disclosures

**Disclosure Email**: `qwamos@tutanota.com` (private, encrypted)

**Process for Maintainers**:

#### Step 1: Acknowledgment (Within 24 Hours)
```
Subject: Re: [SECURITY] <Brief Description>

Dear [Reporter],

Thank you for reporting this security issue to QWAMOS. We have
received your report and are currently assessing the vulnerability.

Assigned ID: QWAMOS-SEC-2025-001
Severity: [TBD]
Estimated Response: [72 hours]

We will keep you updated on our progress and coordinate disclosure
timing with you.

Best regards,
QWAMOS Security Team
```

#### Step 2: Assessment (Within 72 Hours)
1. **Reproduce the vulnerability**
2. **Calculate CVSS score** (use https://www.first.org/cvss/calculator/)
3. **Determine impact**:
   - Critical: Remote code execution, key compromise
   - High: Privilege escalation, network bypass
   - Medium: Information disclosure, DoS
   - Low: Minor information leak
4. **Identify affected versions**
5. **Create private security advisory** (GitHub Security tab)

#### Step 3: Patch Development (Parallel Work)
1. Create private branch (`security/QWAMOS-SEC-2025-001`)
2. Develop fix (may involve multiple maintainers)
3. Write tests (verify fix works, test regression)
4. Document the vulnerability (for future advisory)
5. Coordinate with reporter (get feedback on fix)

#### Step 4: Coordinated Disclosure
**Standard Timeline**: 90 days from initial report

**Expedited Timeline** (active exploit): 7-14 days

**Disclosure Checklist**:
- [ ] Fix developed and tested
- [ ] Patch release ready (versioned as PATCH bump)
- [ ] Security advisory drafted
- [ ] Reporter agrees to disclosure timeline
- [ ] CVE requested (if warranted)
- [ ] Downstream projects notified (if applicable)

#### Step 5: Public Disclosure
1. **Publish Security Advisory** (GitHub Security tab)
   - Description of vulnerability
   - Affected versions
   - Fixed version
   - CVE identifier (if assigned)
   - Credit to reporter
   - Mitigation steps

2. **Release Patch**
   - Tag patch release (e.g., `v1.2.1`)
   - Include fix in release notes
   - Mark as security release

3. **Announce Publicly**
   - GitHub Discussions
   - Security advisory
   - Update SECURITY.md if needed

**Example Advisory**:
```markdown
# Security Advisory: QWAMOS-SEC-2025-001

## Privilege Escalation in Chroot VM Launcher

**Severity**: High (CVSS 7.8)
**Affected Versions**: v1.0.0 - v1.2.0
**Fixed Version**: v1.2.1
**CVE**: CVE-2025-12345

### Description
A vulnerability in the chroot VM launcher allows a local attacker
to escalate privileges by exploiting improper capability handling
during chroot initialization.

### Impact
An attacker with local access can gain root privileges within
the chroot environment, potentially compromising VM isolation.

### Mitigation
Upgrade to v1.2.1 or later immediately. No workaround available.

### Credit
Reported by: [Researcher Name]
Fixed by: QWAMOS Security Team

### Timeline
- 2025-10-01: Initial report
- 2025-10-03: Confirmed and assigned QWAMOS-SEC-2025-001
- 2025-10-15: Patch developed
- 2025-10-20: Patch released (v1.2.1)
- 2025-10-20: Public disclosure
```

### 7.2 Mitigation Patch Protocol

**Emergency Patch Process** (Critical/High Severity):

#### Immediate Actions (Hour 0)
1. **Assemble Response Team**
   - Lead Maintainer
   - Module Maintainer (affected component)
   - At least one Core Maintainer

2. **Create Private Branch**
   ```bash
   git checkout -b security/emergency-fix-<issue-id>
   ```

3. **Notify Stakeholders** (if applicable)
   - Users of affected features
   - Downstream projects

#### Patch Development (Hours 1-24)
1. **Develop Fix**
   - Minimal changes (only what's needed)
   - No feature additions
   - Focus on security fix only

2. **Test Thoroughly**
   - Unit tests
   - Integration tests
   - Security regression tests
   - Manual testing

3. **Code Review** (Fast-track)
   - 2 maintainer approvals required
   - Security-focused review
   - No delays for style/formatting

#### Release (Hours 24-48)
1. **Version Bump** (PATCH increment)
   ```bash
   # Current: v1.2.0
   # New: v1.2.1
   echo "v1.2.1" > VERSION
   ```

2. **Tag and Release**
   ```bash
   git tag -s v1.2.1 -m "Security fix for QWAMOS-SEC-2025-001"
   git push origin v1.2.1
   ```

3. **Trigger Release Workflow**
   - Automated build and publish
   - VM templates built
   - Artifacts uploaded

4. **Announce Security Release**
   - Mark as "Security Release" in GitHub
   - Include advisory link
   - Recommend immediate upgrade

### 7.3 Emergency Response Procedures

**Triggers**:
- Active exploit in the wild
- Critical vulnerability (CVSS 9.0+)
- Zero-day discovered
- Key compromise

**Emergency Response Team (ERT)**:
- **Lead**: Lead Maintainer
- **Members**: All Core Maintainers
- **Support**: Module Maintainers as needed

**Communication Protocol**:
1. **Internal**: Encrypted Signal group or private GitHub repo
2. **External**: `qwamos@tutanota.com` for coordination
3. **Public**: GitHub Security Advisory (after mitigation)

**Emergency Procedure**:

#### Phase 1: Detection and Confirmation (0-4 hours)
1. Receive alert (report, automated scan, or public disclosure)
2. Assemble ERT (all hands on deck)
3. Confirm vulnerability
4. Assess scope and impact
5. Create incident tracking issue (private)

#### Phase 2: Containment (4-12 hours)
1. **If key compromise**:
   - Revoke compromised keys
   - Generate new keys
   - Notify all users

2. **If exploit active**:
   - Document attack vectors
   - Implement temporary mitigations
   - Consider service disruption if needed

3. **Communication**:
   - Internal: Keep ERT informed
   - External: Prepare holding statement

#### Phase 3: Mitigation (12-48 hours)
1. Develop permanent fix
2. Test exhaustively
3. Prepare patch release
4. Coordinate disclosure

#### Phase 4: Recovery (48+ hours)
1. Release patch
2. Public disclosure
3. Monitor for successful deployments
4. Address follow-up issues

#### Phase 5: Post-Incident Review (1 week later)
1. Document timeline
2. Identify lessons learned
3. Update security processes
4. Improve detection/prevention

**Example Scenarios**:

**Scenario A: Active Exploit**
```
Hour 0: Exploit detected affecting VM isolation
Hour 1: ERT assembled, vulnerability confirmed
Hour 4: Temporary mitigation (disable feature via config)
Hour 12: Patch developed and tested
Hour 24: Patch released as v1.2.1
Hour 24: Public advisory published
Hour 48: Monitor for updates, provide support
```

**Scenario B: Key Compromise**
```
Hour 0: Release signing key compromised
Hour 1: Revoke old key, generate new key
Hour 2: Sign existing releases with new key
Hour 4: Announce key rotation
Hour 24: All users notified
Hour 72: Old key fully deprecated
```

---

## SECTION 8 — Contacts & Communication

### 8.1 Maintainer Contact Information

**Note**: This section contains placeholders. Actual contact information is maintained privately.

#### Lead Maintainer
- **Name**: `[LEAD_MAINTAINER_NAME]`
- **GitHub**: `@[GITHUB_USERNAME]`
- **Email**: `[EMAIL_ADDRESS]` (encrypted: GPG key `[KEY_ID]`)
- **GPG Fingerprint**: `[GPG_FINGERPRINT]`
- **Timezone**: `[TIMEZONE]`
- **Availability**: `[HOURS]`

#### Core Maintainers

**Maintainer 1** (Crypto Module)
- **Name**: `[MAINTAINER_1_NAME]`
- **GitHub**: `@[GITHUB_USERNAME_1]`
- **Email**: `[EMAIL_1]`
- **GPG Fingerprint**: `[GPG_FINGERPRINT_1]`
- **Focus**: Post-Quantum Cryptography
- **Timezone**: `[TIMEZONE_1]`

**Maintainer 2** (VM Module)
- **Name**: `[MAINTAINER_2_NAME]`
- **GitHub**: `@[GITHUB_USERNAME_2]`
- **Email**: `[EMAIL_2]`
- **GPG Fingerprint**: `[GPG_FINGERPRINT_2]`
- **Focus**: VM Isolation (QEMU, PRoot, Chroot)
- **Timezone**: `[TIMEZONE_2]`

**Maintainer 3** (Gateway Module)
- **Name**: `[MAINTAINER_3_NAME]`
- **GitHub**: `@[GITHUB_USERNAME_3]`
- **Email**: `[EMAIL_3]`
- **GPG Fingerprint**: `[GPG_FINGERPRINT_3]`
- **Focus**: Network Anonymization (Tor, I2P, DNSCrypt)
- **Timezone**: `[TIMEZONE_3]`

### 8.2 Preferred Communication Channels

#### Public Communication
**Use for**: Feature discussions, bug reports (non-security), general questions

1. **GitHub Issues**
   - URL: https://github.com/Dezirae-Stark/QWAMOS/issues
   - Response Time: 24-48 hours
   - Best for: Bug reports, feature requests

2. **GitHub Discussions**
   - URL: https://github.com/Dezirae-Stark/QWAMOS/discussions
   - Response Time: 1-3 days
   - Best for: Q&A, ideas, community chat

3. **GitHub Pull Requests**
   - URL: https://github.com/Dezirae-Stark/QWAMOS/pulls
   - Response Time: 48 hours (acknowledge), 7 days (review)
   - Best for: Code contributions

#### Private Communication
**Use for**: Security vulnerabilities, maintainer coordination, sensitive issues

1. **Security Email** (Encrypted)
   - Email: `qwamos@tutanota.com`
   - Encryption: PGP/GPG required
   - Public Key: `[SECURITY_TEAM_GPG_KEY]`
   - Response Time: 24 hours
   - Best for: Security disclosures

2. **Maintainer Mailing List** (Private)
   - Email: `[MAINTAINER_LIST_EMAIL]`
   - Members: Lead + Core Maintainers only
   - Response Time: 24-48 hours
   - Best for: Internal coordination, governance decisions

3. **Emergency Contact** (Encrypted Chat)
   - Platform: `[ENCRYPTED_CHAT_PLATFORM]` (e.g., Signal)
   - Group: `QWAMOS Emergency Response`
   - Members: Lead + Core Maintainers
   - Response Time: <4 hours
   - Best for: Active exploits, critical incidents

#### Code Review
**Use for**: PR reviews, technical discussions

1. **GitHub PR Comments**
   - Inline comments for specific code
   - General comments for overall feedback
   - Request changes if needed

2. **Draft PRs for Design Discussion**
   - Create draft PR early for feedback
   - Discuss approach before full implementation

#### Synchronous Communication (Optional)
**Use for**: Complex discussions, planning meetings

1. **Video Calls** (Scheduled)
   - Platform: `[VIDEO_PLATFORM]` (e.g., Jitsi, Zoom)
   - Frequency: Monthly maintainer sync
   - Agenda published 48 hours in advance

2. **IRC/Matrix** (Optional)
   - Channel: `[IRC_CHANNEL]` (e.g., #qwamos on Libera.Chat)
   - Logging: Public (for transparency)
   - Not for security discussions

### Communication Guidelines

**Response Time Expectations**:
- **Critical Security**: <4 hours
- **Security Disclosures**: <24 hours
- **PR Reviews**: 48 hours (acknowledge), 7 days (complete)
- **Issues**: 24-48 hours (acknowledge), varies (resolution)
- **Discussions**: 1-3 days (best effort)

**Communication Etiquette**:
- Be respectful and professional
- Assume good intent
- Provide context (link to issues/PRs)
- Use threaded replies to keep discussions organized
- Mark resolved discussions as resolved

**Escalation**:
If no response within expected time:
1. Comment again with gentle reminder
2. Mention specific maintainer (`@username`)
3. Email Lead Maintainer if urgent
4. For emergencies, use emergency contact

---

## Appendix

### A. Useful Commands

#### Release Management
```bash
# Check out release branch
git checkout -b release/v1.2.0

# Tag release
git tag -s v1.2.0 -m "Release v1.2.0"

# List releases
gh release list

# Create release
gh release create v1.2.0 --title "Version 1.2.0" --notes-file RELEASE_NOTES.md
```

#### Security
```bash
# Run security scans
gh workflow run nightly-security.yml

# Check CodeQL results
gh api /repos/Dezirae-Stark/QWAMOS/code-scanning/alerts

# Create security advisory
gh api /repos/Dezirae-Stark/QWAMOS/security-advisories \
  -f summary="Brief description" \
  -f description="Detailed description" \
  -f severity=high
```

#### Testing
```bash
# Run all tests
./tests/gateway/test_gateway_security.sh
./tests/vm-isolation/test_vm_isolation.sh
python3 ./tests/pqc/test_pqc_security.py

# Build VM templates
./vm-templates/scripts/build_qemu_template.sh
./vm-templates/scripts/validate_vm_template.sh \
  vm-templates/output/templates/qwamos-qemu-template.tar.gz
```

### B. Glossary

- **CVSS**: Common Vulnerability Scoring System (0.0-10.0 scale)
- **GPG**: GNU Privacy Guard (encryption/signing)
- **KEM**: Key Encapsulation Mechanism (e.g., Kyber)
- **AEAD**: Authenticated Encryption with Associated Data (e.g., ChaCha20-Poly1305)
- **PQC**: Post-Quantum Cryptography
- **ERT**: Emergency Response Team
- **RC**: Release Candidate
- **LGTM**: Looks Good To Me (approval)
- **WIP**: Work In Progress (draft PR)
- **PTAL**: Please Take A Look (review request)

### C. References

- [QWAMOS Security Policy](../SECURITY.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [CVSS Calculator](https://www.first.org/cvss/calculator/)
- [GitHub Security Advisories](https://docs.github.com/en/code-security/security-advisories)

---

## Changelog

### v1.0 (November 2025)
- Initial maintainer handbook
- Established governance model
- Defined review processes
- Created release procedures
- Documented security responsibilities

---

**Maintainer Handbook v1.0**
Last Updated: November 2025
Next Review: February 2026

For questions or updates to this handbook, please contact the Lead Maintainer or submit a PR.
