# GPG Commit Signing Setup for QWAMOS

## Current Status

GPG commit signing has been configured for the QWAMOS repository.

**Configuration:**
- Algorithm: Ed25519 (EdDSA - GitHub compatible)
- Key ID: `3FFB3F558F4E2B12`
- Full Fingerprint: `A9331CFF1AA96BFC0F454B8B3FFB3F558F4E2B12`
- Auto-sign: Configured (no passphrase required for this key)

---

## To Complete Setup

### Step 1: Add Public Key to GitHub

1. Copy the entire GPG public key from `gpg_github_public_key.asc` file
2. Go to: https://github.com/settings/keys
3. Click "New GPG key"
4. Paste the public key
5. Click "Add GPG key"

**Public key location:** `~/QWAMOS/gpg_github_public_key.asc`

Or copy directly:
```bash
cat ~/QWAMOS/gpg_github_public_key.asc
```

**The key to copy:**
```
-----BEGIN PGP PUBLIC KEY BLOCK-----

mDMEaQYTYxYJKwYBBAHaRw8BAQdAYNFo03LaW0iSfAfJZcj2ywIuLwEkXccP6A2H
56PEQuS0RkRlemlyYWUtU3RhcmsgKFFXQU1PUyBHaXRIdWIgU2lnbmluZyBLZXkp
IDxzZWlkaGJlcmVuZGlyQHR1dGFtYWlsLmNvbT6IrgQTFgoAVxYhBKkzHP8aqWv8
D0VLiz/7P1WPTisSBQJpBhNjGxSAAAAAAAQADm1hbnUyLDIuNSsxLjExLDMsMgIb
AwULCQgHAgIiAgYVCgkICwIEFgIDAQIeBwIXgAAKCRA/+z9Vj04rEmvnAP9UILo9
qzlPr6SBsPhjMUOAO/aWzcc8S3tl4JujBXzqXAD4oR1PhMEIe48lP+4ED2nFl44M
ZxFkghS/jXvE9W1sD7g4BGkGE2MSCisGAQQBl1UBBQEBB0DxoOjj+ZH+u0BRKepo
RJ/f7SF6llJtV1CSVdxVyayJMQMBCAeIlAQYFgoAPBYhBKkzHP8aqWv8D0VLiz/7
P1WPTisSBQJpBhNjGxSAAAAAAAQADm1hbnUyLDIuNSsxLjExLDMsMgIbDAAKCRA/
+z9Vj04rEvdYAQC94CfmB8X8IHkXGyct+4olR9CxbKvhLIPUBQ//253xZAEA9Alq
xkHrGueNP7hc4K7q01zibh/cAMTrT/i7LhpDMwg=
=EGm+
-----END PGP PUBLIC KEY BLOCK-----
```

### Step 2: Test Signed Commit

Once you've added the key to GitHub, create a test signed commit manually:

```bash
cd ~/QWAMOS
export GPG_TTY=$(tty)
git commit -S -m "Test signed commit"
```

You'll be prompted for your GPG key passphrase. Enter it to sign the commit.

### Step 3: Enable Auto-Signing

After confirming signing works, enable automatic signing:

```bash
cd ~/QWAMOS
git config commit.gpgsign true
```

---

## Verification

Check if a commit is signed:
```bash
git log -1 --show-signature
```

Signed commits will show:
```
gpg: Signature made [date]
gpg: Good signature from "Desirae Ann Stark <sentinel.raven@tuta.io>"
```

On GitHub, signed commits display a green "Verified" badge.

---

## Why GPG Signing?

For a security-focused project like QWAMOS, GPG signing provides:

1. **Authenticity**: Proves commits are from the legitimate author
2. **Integrity**: Detects any tampering with commit content
3. **Non-repudiation**: Author cannot deny creating the commit
4. **Post-Quantum Security**: Ed448 + Kyber1024 resists quantum attacks

This aligns with QWAMOS principles:
- Post-quantum cryptography throughout the entire stack
- Verifiable software supply chain
- Defense-in-depth security architecture

---

## Post-Quantum Cryptography Details

Your GPG key uses cutting-edge cryptography:

**Primary Key:**
- Algorithm: Ed448 (EdDSA with Curve448)
- Security: ~224-bit quantum security
- Purpose: Signing commits

**Encryption Subkey:**
- Algorithm: Kyber1024 + Curve448 hybrid
- Security: NIST Level 5 post-quantum + 224-bit classical
- Purpose: Encrypting messages (if needed)

This provides security against both classical and quantum adversaries.

---

## Troubleshooting

### "gpg failed to sign the data"

Ensure GPG_TTY is set:
```bash
export GPG_TTY=$(tty)
gpg-connect-agent updatestartuptty /bye
```

Add to `~/.bashrc` for persistence:
```bash
echo 'export GPG_TTY=$(tty)' >> ~/.bashrc
```

### Passphrase Caching

To avoid entering passphrase repeatedly, configure gpg-agent:
```bash
mkdir -p ~/.gnupg
echo "default-cache-ttl 3600" >> ~/.gnupg/gpg-agent.conf
echo "max-cache-ttl 7200" >> ~/.gnupg/gpg-agent.conf
gpgconf --kill gpg-agent
```

This caches the passphrase for 1 hour (up to 2 hours max).

---

## Current Git Configuration

```
user.name = Dezirae-Stark
user.email = seidhberendir@tutamail.com
user.signingkey = 3FFB3F558F4E2B12
commit.gpgsign = false  (enable with: git config commit.gpgsign true)
```

## Why Ed25519 Instead of Ed448?

**GitHub Compatibility Issue:**
- Your original Ed448 + Kyber1024 key is MORE secure (post-quantum)
- However, GitHub only supports: RSA, Ed25519, and ECDSA
- Ed448 and Kyber1024 are not yet supported by GitHub

**Current Setup:**
- Ed25519 key for GitHub compatibility (still very secure: ~128-bit security)
- You can keep your Ed448 + Kyber1024 key for other purposes
- Both keys coexist - use Ed25519 for GitHub commits

---

**Last Updated:** 2025-11-01
**Status:** Configured, awaiting passphrase test and GitHub key upload
