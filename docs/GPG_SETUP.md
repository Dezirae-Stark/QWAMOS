# GPG Release Signing Setup Guide

This guide explains how to configure GitHub Secrets for automated GPG release signing.

## Prerequisites

You already have a GPG key in your profile. This guide will help you export it and configure the workflow.

## Step 1: List Your GPG Keys

```bash
# List all GPG keys
gpg --list-secret-keys --keyid-format LONG
```

**Output example:**
```
sec   rsa4096/ABCD1234EFGH5678 2024-01-01 [SC]
      1234567890ABCDEF1234567890ABCDEF12345678
uid                 [ultimate] Your Name <your.email@example.com>
ssb   rsa4096/IJKL9012MNOP3456 2024-01-01 [E]
```

The key ID is: `ABCD1234EFGH5678` (or use the full fingerprint)

## Step 2: Export Private Key

```bash
# Export your GPG private key (replace KEY_ID with your key ID)
gpg --armor --export-secret-keys YOUR_KEY_ID > qwamos-private-key.asc

# Verify the export
cat qwamos-private-key.asc
```

**Expected format:**
```
-----BEGIN PGP PRIVATE KEY BLOCK-----

lQdGBGW...
[base64 encoded key data]
...
-----END PGP PRIVATE KEY BLOCK-----
```

## Step 3: Copy the Private Key

```bash
# Copy the entire private key including the BEGIN/END lines
cat qwamos-private-key.asc
```

Select and copy all the text from `-----BEGIN PGP PRIVATE KEY BLOCK-----` to `-----END PGP PRIVATE KEY BLOCK-----`.

## Step 4: Add to GitHub Secrets

### Via GitHub Web Interface:

1. Go to your repository: https://github.com/Dezirae-Stark/QWAMOS
2. Click **Settings** (repository settings, not profile)
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**

**Create Secret 1: GPG_PRIVATE_KEY**
- **Name:** `GPG_PRIVATE_KEY`
- **Value:** Paste the entire private key (including BEGIN/END lines)
- Click **Add secret**

**Create Secret 2: GPG_PASSPHRASE**
- **Name:** `GPG_PASSPHRASE`
- **Value:** Your GPG key passphrase
- Click **Add secret**

### Via GitHub CLI (Alternative):

```bash
# Set GPG_PRIVATE_KEY secret
gh secret set GPG_PRIVATE_KEY < qwamos-private-key.asc

# Set GPG_PASSPHRASE secret
gh secret set GPG_PASSPHRASE
# (will prompt for passphrase input)
```

## Step 5: Verify Setup

Once secrets are added, verify they appear in your repository:

```bash
# List repository secrets
gh secret list

# Expected output:
# GPG_PASSPHRASE    Updated YYYY-MM-DD
# GPG_PRIVATE_KEY   Updated YYYY-MM-DD
```

## Step 6: Test the Workflow

### Option 1: Create a Test Release

```bash
# Create a test release
gh release create v0.0.1-test \
  --title "Test Release" \
  --notes "Testing automated GPG signing" \
  --prerelease

# Upload a test file
echo "test content" > test-file.txt
gh release upload v0.0.1-test test-file.txt
```

The workflow will automatically:
1. Download test-file.txt
2. Sign it with your GPG key
3. Upload test-file.txt.asc
4. Upload SIGNATURES_MANIFEST.txt

### Option 2: Manual Workflow Trigger

```bash
# Trigger manually (requires existing release)
gh workflow run release-signing.yml \
  -f release_tag=v0.0.1-test \
  -f force_resign=true
```

## Step 7: Verify Signatures

After the workflow runs:

```bash
# Download the release and signatures
gh release download v0.0.1-test

# Import your public key from manifest
gpg --import SIGNATURES_MANIFEST.txt

# Verify the signature
gpg --verify test-file.txt.asc test-file.txt
```

**Expected output:**
```
gpg: Signature made [date]
gpg:                using RSA key [your key fingerprint]
gpg: Good signature from "Your Name <your.email@example.com>"
```

## Security Best Practices

### ✅ DO:
- Use a strong passphrase (20+ characters)
- Keep your private key secure
- Verify the workflow completes successfully
- Test signatures after creation
- Review workflow logs for any issues

### ❌ DON'T:
- Share your private key or passphrase
- Commit secrets to the repository
- Use an expired or revoked key
- Skip signature verification testing

## Troubleshooting

### "Bad passphrase" Error

**Problem:** Workflow fails with "gpg: signing failed: Bad passphrase"

**Solution:**
1. Verify passphrase is correct: `echo "test" | gpg --clearsign`
2. Update GitHub Secret with correct passphrase
3. Re-run the workflow

### "No secret key" Error

**Problem:** Workflow fails with "gpg: signing failed: No secret key"

**Solution:**
1. Verify private key export: `gpg --armor --export-secret-keys YOUR_KEY_ID`
2. Ensure entire key is copied (including BEGIN/END lines)
3. Update `GPG_PRIVATE_KEY` secret
4. Re-run the workflow

### Workflow Doesn't Trigger

**Problem:** Workflow doesn't run when release is created

**Solution:**
1. Check workflow file exists: `.github/workflows/release-signing.yml`
2. Verify GitHub Actions is enabled: Settings → Actions → General
3. Check workflow permissions: Settings → Actions → General → Workflow permissions
4. Ensure "Read and write permissions" is enabled

### Signature Verification Fails

**Problem:** `gpg --verify` shows "BAD signature"

**Solution:**
1. Re-download the file and signature
2. Check file wasn't modified after signing
3. Verify correct public key is imported
4. Check workflow logs for signing errors

## Key Rotation

To rotate your GPG key:

1. Generate new key:
   ```bash
   gpg --full-generate-key
   ```

2. Export new private key:
   ```bash
   gpg --armor --export-secret-keys NEW_KEY_ID > new-private-key.asc
   ```

3. Update GitHub Secrets with new key

4. Re-sign existing releases:
   ```bash
   gh workflow run release-signing.yml \
     -f release_tag=v1.0.0 \
     -f force_resign=true
   ```

5. Revoke old key (if compromised):
   ```bash
   gpg --gen-revoke OLD_KEY_ID > revocation.asc
   gpg --import revocation.asc
   gpg --send-keys OLD_KEY_ID
   ```

## Cleanup

After setup, securely delete local copies:

```bash
# Securely delete private key export
shred -vfz -n 10 qwamos-private-key.asc

# Or on macOS
srm -v qwamos-private-key.asc

# Verify deletion
ls -la qwamos-private-key.asc  # Should show "No such file"
```

## Additional Resources

- [GPG Documentation](https://www.gnupg.org/documentation/)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Release Signing Workflow](../.github/workflows/release-signing.yml)
- [Signature Verification Guide](../signatures/README.md)

## Support

If you encounter issues:
- Check workflow logs: Actions → Release Signing → View logs
- Review [SECURITY.md](../SECURITY.md) for security concerns
- Contact: security@qwamos.org
