#!/usr/bin/env python3
"""
QWAMOS Kyber-1024 Keypair Generation Tool

Generates post-quantum cryptographic keypairs for QWAMOS secure boot.

Usage:
    python gen_kyber_keypair.py --output keys/device_key

Output:
    - device_key.pub    (1,568 bytes) - Public key for U-Boot
    - device_key.priv   (3,168 bytes) - Private key for signing
    - device_key.info   (JSON metadata)

Security Level: Kyber-1024 (NIST FIPS 203 - Security Level 5, 256-bit equivalent)

NOTE: This is a stub implementation for development.
For production, this will use liboqs for real Kyber-1024 key generation.
"""

import os
import sys
import argparse
import json
import hashlib
from datetime import datetime
from pathlib import Path

# Kyber-1024 Parameters (NIST FIPS 203)
KYBER1024_PUBLIC_KEY_BYTES = 1568
KYBER1024_SECRET_KEY_BYTES = 3168
KYBER1024_SIGNATURE_BYTES = 3309

def generate_secure_random(size):
    """
    Generate cryptographically secure random bytes.

    Uses os.urandom() which is suitable for cryptographic use.

    Args:
        size (int): Number of bytes to generate

    Returns:
        bytes: Cryptographically secure random bytes
    """
    return os.urandom(size)

def generate_kyber1024_keypair_stub():
    """
    Generate Kyber-1024 keypair (STUB IMPLEMENTATION).

    NOTE: This generates random data with the correct structure for testing.
    In production, this should use liboqs OQS_SIG_keypair() for real Kyber-1024.

    Returns:
        tuple: (public_key, private_key) as bytes
    """
    print("[STUB] Generating Kyber-1024 keypair...")
    print("[TODO] Integrate with liboqs for real post-quantum key generation")

    # Generate placeholder keys with correct sizes
    public_key = generate_secure_random(KYBER1024_PUBLIC_KEY_BYTES)
    private_key = generate_secure_random(KYBER1024_SECRET_KEY_BYTES)

    return public_key, private_key

def compute_key_fingerprint(public_key):
    """
    Compute SHA-256 fingerprint of public key for identification.

    Args:
        public_key (bytes): Public key bytes

    Returns:
        str: Hex-encoded SHA-256 hash (first 16 bytes for readability)
    """
    full_hash = hashlib.sha256(public_key).digest()
    return full_hash[:16].hex()

def save_keys(output_path, public_key, private_key):
    """
    Save keypair to files.

    Args:
        output_path (str): Base path for key files (without extension)
        public_key (bytes): Public key
        private_key (bytes): Private key
    """
    base_path = Path(output_path)
    base_path.parent.mkdir(parents=True, exist_ok=True)

    # Save public key
    pub_path = base_path.with_suffix('.pub')
    with open(pub_path, 'wb') as f:
        f.write(public_key)
    print(f"✓ Public key saved:  {pub_path} ({len(public_key)} bytes)")

    # Save private key with restricted permissions
    priv_path = base_path.with_suffix('.priv')
    with open(priv_path, 'wb') as f:
        f.write(private_key)
    os.chmod(priv_path, 0o600)  # Owner read/write only
    print(f"✓ Private key saved: {priv_path} ({len(private_key)} bytes) [600]")

    # Save metadata
    fingerprint = compute_key_fingerprint(public_key)
    metadata = {
        "algorithm": "Kyber-1024 (NIST FIPS 203)",
        "security_level": 5,
        "security_bits": 256,
        "public_key_size": len(public_key),
        "private_key_size": len(private_key),
        "signature_size": KYBER1024_SIGNATURE_BYTES,
        "fingerprint": fingerprint,
        "generated": datetime.now().isoformat(),
        "generator": "QWAMOS gen_kyber_keypair.py (stub)",
        "production_ready": False,
        "note": "This is a STUB implementation. Replace with liboqs for production."
    }

    info_path = base_path.with_suffix('.info')
    with open(info_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Key info saved:    {info_path}")

    return fingerprint, metadata

def format_key_for_c_header(public_key, var_name="qwamos_public_key"):
    """
    Format public key as C array for embedding in U-Boot.

    Args:
        public_key (bytes): Public key
        var_name (str): C variable name

    Returns:
        str: C code defining the key array
    """
    lines = [
        f"/* QWAMOS Kyber-1024 Public Key ({len(public_key)} bytes) */",
        f"static const uint8_t {var_name}[{len(public_key)}] = {{",
    ]

    # Format as hex bytes, 12 per line
    for i in range(0, len(public_key), 12):
        chunk = public_key[i:i+12]
        hex_bytes = ', '.join(f'0x{b:02x}' for b in chunk)
        lines.append(f"    {hex_bytes},")

    lines.append("};")
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(
        description='Generate Kyber-1024 keypair for QWAMOS secure boot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    # Generate keypair in keys/ directory
    python gen_kyber_keypair.py --output keys/device_key

    # Generate keypair and create C header
    python gen_kyber_keypair.py --output keys/device_key --c-header

Output files:
    - device_key.pub    Public key (embed in U-Boot)
    - device_key.priv   Private key (for signing images)
    - device_key.info   Key metadata (JSON)
    - device_key.h      C header (if --c-header specified)

Security:
    Private key is saved with 0600 permissions (owner read/write only).
    Keep the private key secure - it signs all boot images!
        '''
    )

    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output path for keys (without extension)'
    )

    parser.add_argument(
        '--c-header',
        action='store_true',
        help='Generate C header file for U-Boot integration'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing keys'
    )

    args = parser.parse_args()

    # Check if keys already exist
    pub_path = Path(args.output).with_suffix('.pub')
    if pub_path.exists() and not args.force:
        print(f"Error: Keys already exist at {args.output}")
        print("Use --force to overwrite")
        return 1

    print("=" * 70)
    print("QWAMOS Kyber-1024 Keypair Generator")
    print("Post-Quantum Cryptography for Secure Boot")
    print("=" * 70)
    print()
    print("Algorithm:      Kyber-1024 (NIST FIPS 203)")
    print("Security Level: 5 (256-bit equivalent)")
    print("Use Case:       Secure Boot signature verification")
    print()
    print("WARNING: This is a STUB implementation for development!")
    print("         For production, integrate with liboqs library.")
    print()

    # Generate keypair
    public_key, private_key = generate_kyber1024_keypair_stub()

    # Save keys
    fingerprint, metadata = save_keys(args.output, public_key, private_key)

    # Generate C header if requested
    if args.c_header:
        header_path = Path(args.output).with_suffix('.h')
        c_code = format_key_for_c_header(public_key)
        with open(header_path, 'w') as f:
            f.write(c_code)
        print(f"✓ C header saved:    {header_path}")

    print()
    print("=" * 70)
    print("Keypair Generation Complete")
    print("=" * 70)
    print(f"Fingerprint: {fingerprint}")
    print()
    print("Next Steps:")
    print("1. Embed public key in U-Boot bootloader")
    print("2. Use private key to sign kernel and initramfs images")
    print("3. Keep private key secure (it signs all boot images!)")
    print()
    print("For production use:")
    print("- Complete liboqs library build")
    print("- Replace stub key generation with OQS_SIG_keypair()")
    print("- Test with real Kyber-1024 signatures")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
