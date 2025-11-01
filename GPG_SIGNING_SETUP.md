# GPG Commit Signing Setup for QWAMOS

## Current Status

GPG commit signing has been configured for the QWAMOS repository with post-quantum cryptography.

**Configuration:**
- Algorithm: Ed448 (EdDSA) + Kyber1024-Curve448 (Post-Quantum Hybrid)
- Key ID: `D74E48E03C62D98E`
- Auto-sign: Configured (will be enabled after passphrase setup)

---

## To Complete Setup

### Step 1: Add Public Key to GitHub

1. Copy the entire GPG public key from `gpg_public_key.asc` file
2. Go to: https://github.com/settings/keys
3. Click "New GPG key"
4. Paste the public key
5. Click "Add GPG key"

**Public key location:** `~/QWAMOS/gpg_public_key.asc`

Or copy directly:
```bash
cat ~/QWAMOS/gpg_public_key.asc
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
user.signingkey = D74E48E03C62D98E
commit.gpgsign = false  (will be true after testing)
```

---

**Last Updated:** 2025-11-01
**Status:** Configured, awaiting passphrase test and GitHub key upload
