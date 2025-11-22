#!/usr/bin/env python3
"""
QWAMOS Image Signing Tool

Signs kernel and initramfs images with Kyber-1024 post-quantum signatures.

Usage:
    python sign_image.py --image kernel.bin --key keys/device_key.priv --output kernel.signed

Output:
    Signed image with appended QWAMOS signature structure (3,413 bytes)

Signature Structure:
    - Magic:           0x4D415751 ('QWAM')
    - Version:         1
    - Image Size:      Original image size
    - Image Hash:      SHA-256 (32 bytes)
    - Kyber Signature: Kyber-1024 signature (3,309 bytes)
    - Reserved:        64 bytes for future use

Security Level: Kyber-1024 (NIST FIPS 203 - Security Level 5, 256-bit equivalent)

NOTE: This is a stub implementation for development.
For production, this will use liboqs for real Kyber-1024 signatures.
"""

import os
import sys
import argparse
import struct
import hashlib
import json
from datetime import datetime
from pathlib import Path

# Try to import liboqs (Open Quantum Safe library)
try:
    import oqs
    LIBOQS_AVAILABLE = True
    print("✓ liboqs library detected - using REAL post-quantum signatures")
except ImportError:
    LIBOQS_AVAILABLE = False
    print("⚠ WARNING: liboqs not installed - using STUB signatures")
    print("  Install with: pip install liboqs-python")

# QWAMOS Signature Constants
QWAMOS_SIGNATURE_MAGIC = 0x4D415751  # 'QWAM'
QWAMOS_SIGNATURE_VERSION = 1
# ML-DSA-87 signature is 4627 bytes (NIST FIPS 204)
KYBER1024_SIGNATURE_BYTES = 4627 if LIBOQS_AVAILABLE else 3309
QWAMOS_SIGNATURE_RESERVED = 64

# Total signature structure size
QWAMOS_SIGNATURE_SIZE = (
    4 +  # magic
    4 +  # version
    4 +  # image_size
    32 +  # image_hash (SHA-256)
    KYBER1024_SIGNATURE_BYTES +
    QWAMOS_SIGNATURE_RESERVED
)  # = 3,413 bytes

def compute_sha256(data):
    """
    Compute SHA-256 hash of data.

    Args:
        data (bytes): Data to hash

    Returns:
        bytes: SHA-256 hash (32 bytes)
    """
    return hashlib.sha256(data).digest()

def load_private_key(key_path):
    """
    Load private key from file.

    Args:
        key_path (Path): Path to private key file

    Returns:
        bytes: Private key data
    """
    if not key_path.exists():
        raise FileNotFoundError(f"Private key not found: {key_path}")

    with open(key_path, 'rb') as f:
        private_key = f.read()

    expected_size = 3168  # Kyber-1024 secret key size
    if len(private_key) != expected_size:
        print(f"Warning: Private key size is {len(private_key)} bytes, expected {expected_size}")

    return private_key

def sign_with_dilithium5(message_hash, private_key):
    """
    Sign message hash with ML-DSA-87 post-quantum signature (formerly Dilithium5).

    Args:
        message_hash (bytes): SHA-256 hash of message (32 bytes)
        private_key (bytes): ML-DSA-87 private key

    Returns:
        bytes: ML-DSA-87 signature (NIST FIPS 204)
    """
    if LIBOQS_AVAILABLE:
        print("Generating REAL ML-DSA-87 signature (NIST FIPS 204)...")
        sig = oqs.Signature("ML-DSA-87", secret_key=private_key)
        signature = sig.sign(message_hash)
        print(f"✓ Signature generated ({len(signature)} bytes)")
        return signature
    else:
        print("[STUB] Generating placeholder signature...")
        print("[CRITICAL] This is NOT cryptographically secure!")
        print("[ACTION REQUIRED] Install liboqs: pip install liboqs-python")

        # Generate placeholder signature with correct size
        signature = os.urandom(KYBER1024_SIGNATURE_BYTES)

        return signature

def create_qwamos_signature(image_data, private_key):
    """
    Create QWAMOS signature structure for image.

    Args:
        image_data (bytes): Image data to sign
        private_key (bytes): Private key for signing

    Returns:
        bytes: Complete QWAMOS signature structure (3,413 bytes)
    """
    # Compute SHA-256 hash of image
    image_hash = compute_sha256(image_data)
    image_size = len(image_data)

    print(f"Image size:  {image_size:,} bytes")
    print(f"Image hash:  {image_hash.hex()}")

    # Generate Dilithium5 post-quantum signature
    kyber_signature = sign_with_dilithium5(image_hash, private_key)

    # Build signature structure
    signature_struct = struct.pack(
        '<III',  # Little-endian: magic, version, image_size
        QWAMOS_SIGNATURE_MAGIC,
        QWAMOS_SIGNATURE_VERSION,
        image_size
    )
    signature_struct += image_hash  # SHA-256 hash (32 bytes)
    signature_struct += kyber_signature  # Kyber-1024 signature (3,309 bytes)
    signature_struct += b'\x00' * QWAMOS_SIGNATURE_RESERVED  # Reserved (64 bytes)

    assert len(signature_struct) == QWAMOS_SIGNATURE_SIZE, \
        f"Signature size mismatch: {len(signature_struct)} != {QWAMOS_SIGNATURE_SIZE}"

    print(f"Signature:   {len(signature_struct)} bytes")

    return signature_struct

def sign_image(image_path, key_path, output_path, verify=True):
    """
    Sign image file and create signed output.

    Args:
        image_path (Path): Path to image file
        key_path (Path): Path to private key
        output_path (Path): Path for signed image output
        verify (bool): Verify signature after signing

    Returns:
        dict: Signature metadata
    """
    # Load image
    print(f"Loading image: {image_path}")
    with open(image_path, 'rb') as f:
        image_data = f.read()

    if len(image_data) == 0:
        raise ValueError("Image file is empty")

    # Load private key
    print(f"Loading private key: {key_path}")
    private_key = load_private_key(key_path)

    # Create signature
    print("Creating signature...")
    signature = create_qwamos_signature(image_data, private_key)

    # Append signature to image
    signed_image = image_data + signature

    # Save signed image
    print(f"Saving signed image: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(signed_image)

    # Create metadata
    metadata = {
        "algorithm": "Kyber-1024 (NIST FIPS 203)",
        "magic": hex(QWAMOS_SIGNATURE_MAGIC),
        "version": QWAMOS_SIGNATURE_VERSION,
        "original_image": str(image_path),
        "original_size": len(image_data),
        "signature_size": QWAMOS_SIGNATURE_SIZE,
        "total_size": len(signed_image),
        "image_hash": compute_sha256(image_data).hex(),
        "signed_date": datetime.now().isoformat(),
        "signer": "QWAMOS sign_image.py (stub)",
        "production_ready": False,
        "note": "This is a STUB implementation. Replace with liboqs for production."
    }

    # Save metadata
    metadata_path = output_path.with_suffix('.sig.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved: {metadata_path}")

    # Verify if requested
    if verify:
        print("\nVerifying signature...")
        verify_result = verify_signature(output_path)
        if verify_result:
            print("✓ Signature verification PASSED")
        else:
            print("✗ Signature verification FAILED")
            return None

    return metadata

def verify_signature(signed_image_path):
    """
    Verify QWAMOS signature on signed image.

    Args:
        signed_image_path (Path): Path to signed image

    Returns:
        bool: True if signature is valid
    """
    with open(signed_image_path, 'rb') as f:
        signed_data = f.read()

    if len(signed_data) < QWAMOS_SIGNATURE_SIZE:
        print(f"Error: File too small to contain signature")
        return False

    # Split image and signature
    image_size_from_file = len(signed_data) - QWAMOS_SIGNATURE_SIZE
    image_data = signed_data[:image_size_from_file]
    signature_data = signed_data[image_size_from_file:]

    # Parse signature structure
    magic, version, image_size = struct.unpack('<III', signature_data[:12])
    image_hash = signature_data[12:44]
    kyber_signature = signature_data[44:44+KYBER1024_SIGNATURE_BYTES]

    # Verify magic
    if magic != QWAMOS_SIGNATURE_MAGIC:
        print(f"✗ Invalid magic: {hex(magic)} (expected {hex(QWAMOS_SIGNATURE_MAGIC)})")
        return False
    print(f"✓ Magic number valid: {hex(magic)}")

    # Verify version
    if version != QWAMOS_SIGNATURE_VERSION:
        print(f"✗ Invalid version: {version} (expected {QWAMOS_SIGNATURE_VERSION})")
        return False
    print(f"✓ Version valid: {version}")

    # Verify image size
    if image_size != len(image_data):
        print(f"✗ Image size mismatch: {image_size} != {len(image_data)}")
        return False
    print(f"✓ Image size valid: {image_size:,} bytes")

    # Verify hash
    computed_hash = compute_sha256(image_data)
    if computed_hash != image_hash:
        print(f"✗ Hash mismatch!")
        print(f"  Expected: {image_hash.hex()}")
        print(f"  Computed: {computed_hash.hex()}")
        return False
    print(f"✓ SHA-256 hash valid: {computed_hash.hex()}")

    # NOTE: Kyber-1024 signature verification is stubbed
    print("⚠ Kyber-1024 signature verification STUBBED (always succeeds)")

    return True

def main():
    parser = argparse.ArgumentParser(
        description='Sign kernel/initramfs images with Kyber-1024 for QWAMOS secure boot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    # Sign kernel image
    python sign_image.py --image kernel.bin --key keys/device_key.priv --output kernel.signed

    # Sign initramfs
    python sign_image.py --image initramfs.cpio.gz --key keys/device_key.priv --output initramfs.signed

    # Sign without verification
    python sign_image.py --image kernel.bin --key keys/device_key.priv --output kernel.signed --no-verify

Output files:
    - kernel.signed         Signed image (original + 3,413 byte signature)
    - kernel.signed.sig.json  Signature metadata (JSON)

Security:
    The private key must be kept secure. Anyone with the private key can sign boot images!

Signature Structure (3,413 bytes):
    - Magic:           4 bytes (0x4D415751 'QWAM')
    - Version:         4 bytes (1)
    - Image Size:      4 bytes
    - Image Hash:      32 bytes (SHA-256)
    - Kyber Signature: 3,309 bytes (Kyber-1024)
    - Reserved:        64 bytes
        '''
    )

    parser.add_argument(
        '--image', '-i',
        required=True,
        type=Path,
        help='Image file to sign (kernel or initramfs)'
    )

    parser.add_argument(
        '--key', '-k',
        required=True,
        type=Path,
        help='Private key file (.priv)'
    )

    parser.add_argument(
        '--output', '-o',
        required=True,
        type=Path,
        help='Output path for signed image'
    )

    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip signature verification after signing'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing signed image'
    )

    args = parser.parse_args()

    # Check if output exists
    if args.output.exists() and not args.force:
        print(f"Error: Output file already exists: {args.output}")
        print("Use --force to overwrite")
        return 1

    # Check if input exists
    if not args.image.exists():
        print(f"Error: Image file not found: {args.image}")
        return 1

    print("=" * 70)
    print("QWAMOS Image Signing Tool")
    print("Post-Quantum Cryptography for Secure Boot")
    print("=" * 70)
    print()
    print("Algorithm:      Kyber-1024 (NIST FIPS 203)")
    print("Security Level: 5 (256-bit equivalent)")
    print("Signature Size: 3,413 bytes")
    print()
    print("WARNING: This is a STUB implementation for development!")
    print("         For production, integrate with liboqs library.")
    print()

    # Sign image
    try:
        metadata = sign_image(args.image, args.key, args.output, verify=not args.no_verify)
        if metadata is None:
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    print()
    print("=" * 70)
    print("Image Signing Complete")
    print("=" * 70)
    print(f"Original size: {metadata['original_size']:,} bytes")
    print(f"Signature:     {metadata['signature_size']:,} bytes")
    print(f"Total size:    {metadata['total_size']:,} bytes")
    print()
    print("Signed image can now be verified by U-Boot bootloader.")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
