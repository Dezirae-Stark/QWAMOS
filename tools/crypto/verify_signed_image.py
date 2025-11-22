#!/usr/bin/env python3
"""
QWAMOS Signed Image Verification Tool

Verifies ML-DSA-87 signatures on signed kernel/initramfs images.
This demonstrates that the bootloader will accept properly signed images.

Usage:
    python verify_signed_image.py --image kernel/Image.signed --pubkey test/keys/qwamos_device.pub
"""

import os
import sys
import struct
import hashlib
import argparse

# Try to import liboqs
try:
    import oqs
    LIBOQS_AVAILABLE = True
except ImportError:
    LIBOQS_AVAILABLE = False
    print("ERROR: liboqs not available - cannot verify signatures")
    sys.exit(1)

# QWAMOS Signature Constants
QWAMOS_SIGNATURE_MAGIC = 0x4D415751  # 'QWAM'
QWAMOS_SIGNATURE_VERSION = 1
SIGNATURE_SIZE = 4627  # ML-DSA-87


def extract_signature_components(signed_image_path):
    """Extract image and signature from signed image file."""
    with open(signed_image_path, 'rb') as f:
        data = f.read()

    # Signature is appended at the end
    # Format: magic(4) + version(4) + image_size(4) + hash(32) + signature(4627) + reserved(64)
    header_size = 4 + 4 + 4 + 32
    signature_struct_size = header_size + SIGNATURE_SIZE + 64

    if len(data) < signature_struct_size:
        raise ValueError(f"File too small: {len(data)} bytes (expected at least {signature_struct_size})")

    # Extract signature structure from end
    signature_data = data[-signature_struct_size:]
    original_image = data[:-signature_struct_size]

    # Parse signature structure
    magic, version, image_size = struct.unpack('<III', signature_data[:12])

    if magic != QWAMOS_SIGNATURE_MAGIC:
        raise ValueError(f"Invalid magic: 0x{magic:08x} (expected 0x{QWAMOS_SIGNATURE_MAGIC:08x})")

    if version != QWAMOS_SIGNATURE_VERSION:
        raise ValueError(f"Invalid version: {version} (expected {QWAMOS_SIGNATURE_VERSION})")

    if image_size != len(original_image):
        raise ValueError(f"Image size mismatch: {image_size} != {len(original_image)}")

    # Extract hash and signature
    image_hash = signature_data[12:44]
    signature = signature_data[44:44+SIGNATURE_SIZE]

    return original_image, image_hash, signature


def verify_signature(image_data, signature, public_key_path):
    """Verify ML-DSA-87 signature using public key."""
    # Load public key
    with open(public_key_path, 'rb') as f:
        public_key = f.read()

    # Compute SHA-256 hash of image
    computed_hash = hashlib.sha256(image_data).digest()

    print(f"  Image size:     {len(image_data):,} bytes")
    print(f"  Computed hash:  {computed_hash.hex()}")
    print(f"  Public key size: {len(public_key)} bytes")
    print(f"  Signature size:  {len(signature)} bytes")

    # Verify signature using ML-DSA-87
    try:
        sig = oqs.Signature("ML-DSA-87")
        is_valid = sig.verify(computed_hash, signature, public_key)

        return is_valid, computed_hash
    except Exception as e:
        print(f"  Verification error: {e}")
        return False, computed_hash


def main():
    parser = argparse.ArgumentParser(description='Verify QWAMOS signed images')
    parser.add_argument('--image', required=True, help='Signed image file')
    parser.add_argument('--pubkey', required=True, help='Public key file')

    args = parser.parse_args()

    print("=" * 70)
    print("QWAMOS Signed Image Verification")
    print("=" * 70)
    print()

    print(f"Signed image: {args.image}")
    print(f"Public key:   {args.pubkey}")
    print()

    # Extract components
    print("[1] Extracting signature components...")
    try:
        original_image, stored_hash, signature = extract_signature_components(args.image)
        print(f"  ✓ Signature structure valid")
        print(f"  ✓ Stored hash: {stored_hash.hex()}")
    except Exception as e:
        print(f"  ✗ Failed to extract signature: {e}")
        return 1

    print()

    # Verify signature
    print("[2] Verifying ML-DSA-87 signature...")
    is_valid, computed_hash = verify_signature(original_image, signature, args.pubkey)

    print()

    if stored_hash != computed_hash:
        print("  ✗ Hash mismatch!")
        print(f"    Stored:   {stored_hash.hex()}")
        print(f"    Computed: {computed_hash.hex()}")
        return 1
    else:
        print("  ✓ Hash matches")

    if is_valid:
        print("  ✓ Signature verification PASSED")
        print()
        print("=" * 70)
        print("✅ IMAGE VERIFICATION SUCCESSFUL")
        print("=" * 70)
        print()
        print("This image would be accepted by the QWAMOS bootloader.")
        print("Secure boot validation: PASSED")
        return 0
    else:
        print("  ✗ Signature verification FAILED")
        print()
        print("=" * 70)
        print("❌ IMAGE VERIFICATION FAILED")
        print("=" * 70)
        print()
        print("This image would be REJECTED by the QWAMOS bootloader.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
