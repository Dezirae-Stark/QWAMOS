# QWAMOS Release Signatures

This directory contains GPG signatures for QWAMOS release artifacts, ensuring authenticity
and integrity of all published releases.

## Directory Structure

```
signatures/
├── README.md                    # This file
├── latest/                      # Latest release signatures
│   ├── *.asc                   # GPG signature files
│   ├── SIGNATURES_MANIFEST.txt # Signature manifest with public key
│   └── README.md               # Latest release info
└── releases/                    # Release-specific signatures
    └── v1.0.0/                 # Example: signatures for v1.0.0
        ├── *.asc               # GPG signature files
        └── SIGNATURES_MANIFEST.txt
```

## What is Signed?

Every QWAMOS release includes GPG signatures for:

- **Release tarballs** (`.tar.gz`)
- **Release zip files** (`.zip`)
- **SBOM files** (Software Bill of Materials, if present)
- **Build artifacts** (wheels, packages)
- **VM templates** (QEMU, PRoot, Chroot)

## Signature Format

All signatures use **detached ASCII-armored GPG signatures** with `.asc` extension:

- `qwamos-1.0.0.tar.gz` → `qwamos-1.0.0.tar.gz.asc`
- `qwamos-1.0.0.zip` → `qwamos-1.0.0.zip.asc`

## Verification

### Quick Verification

```bash
# Download release and signatures
gh release download v1.0.0 --repo Dezirae-Stark/QWAMOS

# Import GPG public key from manifest
gpg --import SIGNATURES_MANIFEST.txt

# Verify a signature
gpg --verify qwamos-1.0.0.tar.gz.asc qwamos-1.0.0.tar.gz
```

### Step-by-Step Verification

#### 1. Import the QWAMOS Release Signing Key

```bash
# From signature manifest
gpg --import SIGNATURES_MANIFEST.txt

# Or from key file (if available)
gpg --import qwamos-release-key.asc

# Verify key fingerprint (compare with official sources)
gpg --fingerprint "QWAMOS Release Signing Key"
```

#### 2. Verify a Release Artifact

```bash
# General syntax
gpg --verify <signature-file> <artifact-file>

# Example: Verify tarball
gpg --verify qwamos-1.0.0.tar.gz.asc qwamos-1.0.0.tar.gz
```

**Expected output:**
```
gpg: Signature made [date]
gpg:                using RSA key [fingerprint]
gpg: Good signature from "QWAMOS Release Signing Key"
```

#### 3. Trust the Key (Optional)

If you trust the QWAMOS project:

```bash
# Edit key trust
gpg --edit-key "QWAMOS Release Signing Key"

# At the gpg> prompt:
gpg> trust
# Select option 5 (ultimate trust)
gpg> quit
```

### Verification with SHA256 Checksums

Signature manifest includes SHA256 checksums for additional verification:

```bash
# Extract checksums from manifest
grep "SHA256:" SIGNATURES_MANIFEST.txt

# Verify checksum
sha256sum qwamos-1.0.0.tar.gz
```

## Automated Signing Process

Signatures are generated automatically by the [Release Signing Workflow](../.github/workflows/release-signing.yml):

1. **Triggered** when a new release is created
2. **Imports** GPG private key from GitHub Secrets
3. **Signs** all release artifacts with detached signatures
4. **Verifies** each signature after creation
5. **Uploads** signatures to GitHub Release
6. **Commits** signatures to this repository
7. **Deletes** GPG keys securely (shred + rm)

## Security

### Key Security

- ✅ GPG private key stored in GitHub Secrets (encrypted)
- ✅ Passphrase stored separately in GitHub Secrets
- ✅ Keys imported to temporary directory only
- ✅ Keys securely deleted (shredded) after signing
- ✅ No keys persist after workflow completion

### Signature Verification Security

**Always verify signatures before using release artifacts:**

```bash
# ❌ INSECURE: Don't skip verification
tar -xzf qwamos-1.0.0.tar.gz

# ✅ SECURE: Verify first, then extract
gpg --verify qwamos-1.0.0.tar.gz.asc qwamos-1.0.0.tar.gz && \
  tar -xzf qwamos-1.0.0.tar.gz
```

### Key Fingerprint Verification

**Critical**: Always verify the key fingerprint through multiple channels:

1. **GitHub Repository**: Check this file and releases
2. **Project Website**: https://qwamos.org/security/gpg-key
3. **Social Media**: Official QWAMOS accounts
4. **Direct Contact**: Reach out to maintainers

**Never trust a key without verifying its fingerprint!**

## Signature Manifest

Each release includes a `SIGNATURES_MANIFEST.txt` file containing:

- Release version and date
- GPG key fingerprint
- List of signed files with SHA256 checksums
- GPG public key (ASCII-armored)
- Verification instructions

## Troubleshooting

### "No public key" Error

```
gpg: Can't check signature: No public key
```

**Solution**: Import the public key first:
```bash
gpg --import SIGNATURES_MANIFEST.txt
```

### "Signature made by unknown key" Warning

```
gpg: WARNING: This key is not certified with a trusted signature!
```

**This is normal** - it means you haven't explicitly trusted the key yet. Verify the
fingerprint and trust the key if appropriate.

### Signature Verification Fails

```
gpg: BAD signature
```

**This is a security issue!** The artifact may have been tampered with:

1. ❌ **Do NOT use the artifact**
2. 🚨 Re-download from official sources
3. 📧 Report to security@qwamos.org
4. 🔍 Verify checksums match official release notes

## GPG Best Practices

### For Users

1. **Always verify signatures** before using releases
2. **Verify key fingerprint** through multiple channels
3. **Keep GPG up to date**: `gpg --version`
4. **Use strong verification**: Don't trust blindly

### For Maintainers

1. **Protect private key**: Never commit to repository
2. **Use strong passphrase**: Minimum 20 characters
3. **Rotate keys**: Consider annual key rotation
4. **Document fingerprint**: Multiple channels
5. **Revoke compromised keys**: Immediately if suspected

## Manual Signing (Maintainers)

If automated signing fails, maintainers can sign manually:

```bash
# Sign a file
gpg --detach-sign --armor --local-user "QWAMOS Release Signing Key" qwamos-1.0.0.tar.gz

# Verify signature
gpg --verify qwamos-1.0.0.tar.gz.asc qwamos-1.0.0.tar.gz

# Upload to release
gh release upload v1.0.0 qwamos-1.0.0.tar.gz.asc
```

## Re-signing a Release

To re-sign an existing release (maintainers only):

```bash
# Trigger workflow manually
gh workflow run release-signing.yml \
  -f release_tag=v1.0.0 \
  -f force_resign=true
```

## Public Key Distribution

The QWAMOS Release Signing public key is distributed through:

1. **Signature manifests**: In every release
2. **This repository**: `signatures/latest/SIGNATURES_MANIFEST.txt`
3. **GitHub Artifacts**: Workflow artifacts
4. **Key servers**: `gpg --keyserver keys.openpgp.org --send-keys [fingerprint]`

## Integration with Package Managers

### APT (Debian/Ubuntu)

```bash
# Add GPG key to APT
curl -fsSL https://github.com/Dezirae-Stark/QWAMOS/releases/latest/download/SIGNATURES_MANIFEST.txt | \
  gpg --dearmor | sudo tee /usr/share/keyrings/qwamos-archive-keyring.gpg
```

### DNF/YUM (Fedora/RHEL)

```bash
# Import GPG key
sudo rpm --import https://github.com/Dezirae-Stark/QWAMOS/releases/latest/download/SIGNATURES_MANIFEST.txt
```

## Reporting Security Issues

If you discover a signature verification issue or suspect key compromise:

1. **DO NOT** post publicly
2. **Email**: security@qwamos.org (PGP encrypted preferred)
3. **Include**: Release version, artifact name, error message
4. **Wait**: For security team response before disclosure

## Resources

- [GPG Tutorial](https://www.gnupg.org/gph/en/manual.html)
- [Verifying Signatures Guide](https://www.debian.org/CD/verify)
- [QWAMOS Security Policy](../SECURITY.md)
- [Release Workflow](.github/workflows/release-signing.yml)

## License

See [LICENSE](../LICENSE) file.

---

**Last Updated**: $(date -u +"%Y-%m-%d")
**Maintained by**: QWAMOS Security Team
