#!/usr/bin/env python3
"""
QWAMOS Post-Quantum Volume Header Structure
Phase 4 - 2048-byte encrypted volume header

Header Layout (2048 bytes total):
┌─────────────────────────────────────────────────────────────┐
│ OFFSET  SIZE  FIELD              DESCRIPTION                 │
├─────────────────────────────────────────────────────────────┤
│ 0       8     Magic              "QWAMOSPQ" (8 bytes)       │
│ 8       2     Version            0x0401 (Phase 4, v1)       │
│ 10      2     Header Size        2048 (0x0800)              │
│ 12      4     Flags              Encryption options          │
│ 16      8     Volume Size        Total volume bytes          │
│ 24      8     Created            Unix timestamp              │
│ 32      8     Modified           Unix timestamp              │
│ 40      32    Salt               Argon2id salt               │
│ 72      4     Argon2 Memory      Memory cost (MB)            │
│ 76      4     Argon2 Time        Time cost (iterations)      │
│ 80      4     Argon2 Parallelism Thread count                │
│ 84      4     Reserved           (alignment)                 │
│ 88      1568  Kyber Ciphertext   Encrypted master key        │
│ 1656    32    Master Key BLAKE3  Hash of decrypted key       │
│ 1688    32    Header BLAKE3      Hash of header (0-1688)     │
│ 1720    64    Reserved           Future use                  │
│ 1784    256   User Metadata      Label, notes, etc.          │
│ 2040    8     Footer Magic       "QWAMOEND" (8 bytes)        │
└─────────────────────────────────────────────────────────────┘

Encryption Flow (Volume Creation):
1. User provides password
2. Generate random salt (32 bytes)
3. Argon2id(password, salt) → Kyber secret key (3168 bytes)
4. Generate Kyber keypair (pk, sk)
5. Generate random master key (32 bytes)
6. Kyber.encapsulate(pk) → (shared_secret, ciphertext)
7. ChaCha20(shared_secret, master_key) → encrypted_master_key
8. Store ciphertext in header
9. BLAKE3(master_key) → master_key_hash
10. BLAKE3(header[0:1688]) → header_hash

Decryption Flow (Volume Unlock):
1. User provides password
2. Read salt from header
3. Argon2id(password, salt) → Kyber secret key
4. Read ciphertext from header
5. Kyber.decapsulate(sk, ciphertext) → shared_secret
6. ChaCha20(shared_secret, encrypted_master_key) → master_key
7. Verify BLAKE3(master_key) == master_key_hash
8. Use master_key to decrypt volume data
"""

import struct
import time
from typing import Tuple, Optional
from dataclasses import dataclass


# Header constants
MAGIC_HEADER = b"QWAMOSPQ"  # 8 bytes
MAGIC_FOOTER = b"QWAMOEND"  # 8 bytes (was 9 bytes - "QWAMOSEND")
HEADER_VERSION = 0x0401  # Phase 4, version 1
HEADER_SIZE = 2048  # Total header size

# Field offsets
OFFSET_MAGIC = 0
OFFSET_VERSION = 8
OFFSET_HEADER_SIZE = 10
OFFSET_FLAGS = 12
OFFSET_VOLUME_SIZE = 16
OFFSET_CREATED = 24
OFFSET_MODIFIED = 32
OFFSET_SALT = 40
OFFSET_ARGON2_MEMORY = 72
OFFSET_ARGON2_TIME = 76
OFFSET_ARGON2_PARALLELISM = 80
OFFSET_RESERVED_1 = 84
OFFSET_KYBER_CIPHERTEXT = 88
OFFSET_MASTER_KEY_HASH = 1656
OFFSET_HEADER_HASH = 1688
OFFSET_RESERVED_2 = 1720
OFFSET_USER_METADATA = 1784
OFFSET_FOOTER_MAGIC = 2040

# Field sizes
SIZE_MAGIC = 8
SIZE_VERSION = 2
SIZE_HEADER_SIZE = 2
SIZE_FLAGS = 4
SIZE_VOLUME_SIZE = 8
SIZE_CREATED = 8
SIZE_MODIFIED = 8
SIZE_SALT = 32
SIZE_ARGON2_MEMORY = 4
SIZE_ARGON2_TIME = 4
SIZE_ARGON2_PARALLELISM = 4
SIZE_RESERVED_1 = 4
SIZE_KYBER_CIPHERTEXT = 1568
SIZE_MASTER_KEY_HASH = 32
SIZE_HEADER_HASH = 32
SIZE_RESERVED_2 = 64
SIZE_USER_METADATA = 256
SIZE_FOOTER_MAGIC = 8

# Flags
FLAG_NONE = 0x00000000
FLAG_COMPRESSED = 0x00000001  # Volume data is compressed
FLAG_HIDDEN = 0x00000002  # Hidden volume (VeraCrypt-style)
FLAG_KEYFILE = 0x00000004  # Requires keyfile in addition to password


@dataclass
class VolumeHeaderMetadata:
    """
    Volume header metadata (parsed from 2048-byte header)
    """
    magic: bytes  # Should be b"QWAMOSPQ"
    version: int  # Should be 0x0401
    header_size: int  # Should be 2048
    flags: int  # Encryption/volume options
    volume_size: int  # Total volume size in bytes
    created: int  # Unix timestamp
    modified: int  # Unix timestamp
    salt: bytes  # 32-byte Argon2id salt
    argon2_memory: int  # Memory cost (MB)
    argon2_time: int  # Time cost (iterations)
    argon2_parallelism: int  # Thread count
    kyber_ciphertext: bytes  # 1568-byte Kyber ciphertext
    master_key_hash: bytes  # 32-byte BLAKE3 hash of master key
    header_hash: bytes  # 32-byte BLAKE3 hash of header
    user_metadata: bytes  # 256 bytes user data (label, notes)
    footer_magic: bytes  # Should be b"QWAMOSEND"

    def is_valid(self) -> bool:
        """Verify header magic and basic sanity checks"""
        return (
            self.magic == MAGIC_HEADER and
            self.footer_magic == MAGIC_FOOTER and
            self.version == HEADER_VERSION and
            self.header_size == HEADER_SIZE and
            len(self.salt) == SIZE_SALT and
            len(self.kyber_ciphertext) == SIZE_KYBER_CIPHERTEXT and
            len(self.master_key_hash) == SIZE_MASTER_KEY_HASH and
            len(self.header_hash) == SIZE_HEADER_HASH
        )


class VolumeHeader:
    """
    QWAMOS Post-Quantum Volume Header Manager

    Handles serialization/deserialization of 2048-byte volume headers
    containing Kyber-1024 ciphertexts and Argon2id parameters.
    """

    @staticmethod
    def create(
        volume_size: int,
        salt: bytes,
        argon2_memory: int,
        argon2_time: int,
        argon2_parallelism: int,
        kyber_ciphertext: bytes,
        master_key_hash: bytes,
        flags: int = FLAG_NONE,
        user_metadata: bytes = b""
    ) -> bytes:
        """
        Create a new 2048-byte volume header

        Args:
            volume_size: Total volume size in bytes
            salt: 32-byte Argon2id salt
            argon2_memory: Memory cost in MB
            argon2_time: Time cost (iterations)
            argon2_parallelism: Thread count
            kyber_ciphertext: 1568-byte Kyber ciphertext
            master_key_hash: 32-byte BLAKE3 hash of master key
            flags: Volume options (compression, hidden, etc.)
            user_metadata: Optional 256-byte user data

        Returns:
            2048-byte header (ready to write to volume file)

        Example:
            >>> header = VolumeHeader.create(
            ...     volume_size=100*1024*1024,  # 100 MB
            ...     salt=os.urandom(32),
            ...     argon2_memory=1024,
            ...     argon2_time=10,
            ...     argon2_parallelism=4,
            ...     kyber_ciphertext=ciphertext,
            ...     master_key_hash=key_hash
            ... )
            >>> len(header)
            2048
        """
        # Validate inputs
        if len(salt) != SIZE_SALT:
            raise ValueError(f"Salt must be {SIZE_SALT} bytes")
        if len(kyber_ciphertext) != SIZE_KYBER_CIPHERTEXT:
            raise ValueError(f"Kyber ciphertext must be {SIZE_KYBER_CIPHERTEXT} bytes")
        if len(master_key_hash) != SIZE_MASTER_KEY_HASH:
            raise ValueError(f"Master key hash must be {SIZE_MASTER_KEY_HASH} bytes")

        # Pad/truncate user metadata to 256 bytes
        if len(user_metadata) > SIZE_USER_METADATA:
            user_metadata = user_metadata[:SIZE_USER_METADATA]
        else:
            user_metadata = user_metadata.ljust(SIZE_USER_METADATA, b'\x00')

        # Get timestamps
        now = int(time.time())

        # Build header (without header_hash yet)
        header = bytearray(HEADER_SIZE)

        # Magic and version (use byte-wise assignment to prevent array growth)
        for i in range(SIZE_MAGIC):
            header[OFFSET_MAGIC + i] = MAGIC_HEADER[i]
        struct.pack_into('>H', header, OFFSET_VERSION, HEADER_VERSION)
        struct.pack_into('>H', header, OFFSET_HEADER_SIZE, HEADER_SIZE)

        # Flags and volume info
        struct.pack_into('>I', header, OFFSET_FLAGS, flags)
        struct.pack_into('>Q', header, OFFSET_VOLUME_SIZE, volume_size)
        struct.pack_into('>Q', header, OFFSET_CREATED, now)
        struct.pack_into('>Q', header, OFFSET_MODIFIED, now)

        # Argon2id parameters
        for i in range(SIZE_SALT):
            header[OFFSET_SALT + i] = salt[i]
        struct.pack_into('>I', header, OFFSET_ARGON2_MEMORY, argon2_memory)
        struct.pack_into('>I', header, OFFSET_ARGON2_TIME, argon2_time)
        struct.pack_into('>I', header, OFFSET_ARGON2_PARALLELISM, argon2_parallelism)

        # Kyber ciphertext and master key hash (use individual byte assignment to prevent array growth)
        for i in range(SIZE_KYBER_CIPHERTEXT):
            header[OFFSET_KYBER_CIPHERTEXT + i] = kyber_ciphertext[i]
        for i in range(SIZE_MASTER_KEY_HASH):
            header[OFFSET_MASTER_KEY_HASH + i] = master_key_hash[i]

        # User metadata
        for i in range(SIZE_USER_METADATA):
            header[OFFSET_USER_METADATA + i] = user_metadata[i]

        # Footer magic
        for i in range(SIZE_FOOTER_MAGIC):
            header[OFFSET_FOOTER_MAGIC + i] = MAGIC_FOOTER[i]

        # Compute header hash (hash of bytes 0-1688)
        try:
            from .blake3_hash import Blake3Hash
        except ImportError:
            from blake3_hash import Blake3Hash
        header_hash = Blake3Hash.hash(bytes(header[:OFFSET_HEADER_HASH]))

        # Write hash using exact slice (prevent array growth)
        for i in range(SIZE_HEADER_HASH):
            header[OFFSET_HEADER_HASH + i] = header_hash[i]

        # Verify header is exactly HEADER_SIZE bytes
        if len(header) != HEADER_SIZE:
            raise ValueError(f"Internal error: header is {len(header)} bytes, expected {HEADER_SIZE}")

        return bytes(header)

    @staticmethod
    def parse(header_bytes: bytes) -> VolumeHeaderMetadata:
        """
        Parse 2048-byte header into metadata structure

        Args:
            header_bytes: 2048-byte header from volume file

        Returns:
            VolumeHeaderMetadata object

        Raises:
            ValueError: If header is invalid (wrong size, bad magic, etc.)

        Example:
            >>> with open("volume.qwamos", "rb") as f:
            ...     header_bytes = f.read(2048)
            >>> metadata = VolumeHeader.parse(header_bytes)
            >>> metadata.is_valid()
            True
        """
        if len(header_bytes) != HEADER_SIZE:
            raise ValueError(f"Header must be {HEADER_SIZE} bytes, got {len(header_bytes)}")

        # Parse all fields
        magic = header_bytes[OFFSET_MAGIC:OFFSET_MAGIC + SIZE_MAGIC]
        version = struct.unpack_from('>H', header_bytes, OFFSET_VERSION)[0]
        header_size = struct.unpack_from('>H', header_bytes, OFFSET_HEADER_SIZE)[0]
        flags = struct.unpack_from('>I', header_bytes, OFFSET_FLAGS)[0]
        volume_size = struct.unpack_from('>Q', header_bytes, OFFSET_VOLUME_SIZE)[0]
        created = struct.unpack_from('>Q', header_bytes, OFFSET_CREATED)[0]
        modified = struct.unpack_from('>Q', header_bytes, OFFSET_MODIFIED)[0]

        salt = header_bytes[OFFSET_SALT:OFFSET_SALT + SIZE_SALT]
        argon2_memory = struct.unpack_from('>I', header_bytes, OFFSET_ARGON2_MEMORY)[0]
        argon2_time = struct.unpack_from('>I', header_bytes, OFFSET_ARGON2_TIME)[0]
        argon2_parallelism = struct.unpack_from('>I', header_bytes, OFFSET_ARGON2_PARALLELISM)[0]

        kyber_ciphertext = header_bytes[OFFSET_KYBER_CIPHERTEXT:OFFSET_KYBER_CIPHERTEXT + SIZE_KYBER_CIPHERTEXT]
        master_key_hash = header_bytes[OFFSET_MASTER_KEY_HASH:OFFSET_MASTER_KEY_HASH + SIZE_MASTER_KEY_HASH]
        header_hash = header_bytes[OFFSET_HEADER_HASH:OFFSET_HEADER_HASH + SIZE_HEADER_HASH]

        user_metadata = header_bytes[OFFSET_USER_METADATA:OFFSET_USER_METADATA + SIZE_USER_METADATA]
        footer_magic = header_bytes[OFFSET_FOOTER_MAGIC:OFFSET_FOOTER_MAGIC + SIZE_FOOTER_MAGIC]

        metadata = VolumeHeaderMetadata(
            magic=magic,
            version=version,
            header_size=header_size,
            flags=flags,
            volume_size=volume_size,
            created=created,
            modified=modified,
            salt=salt,
            argon2_memory=argon2_memory,
            argon2_time=argon2_time,
            argon2_parallelism=argon2_parallelism,
            kyber_ciphertext=kyber_ciphertext,
            master_key_hash=master_key_hash,
            header_hash=header_hash,
            user_metadata=user_metadata,
            footer_magic=footer_magic
        )

        # Verify header magic
        if not metadata.is_valid():
            raise ValueError("Invalid header: bad magic, version, or field sizes")

        # Verify header hash
        try:
            from .blake3_hash import Blake3Hash
        except ImportError:
            from blake3_hash import Blake3Hash
        computed_hash = Blake3Hash.hash(header_bytes[:OFFSET_HEADER_HASH])
        if computed_hash != header_hash:
            raise ValueError("Header hash verification failed (header corrupted or tampered)")

        return metadata

    @staticmethod
    def update_timestamp(header_bytes: bytes) -> bytes:
        """
        Update the 'modified' timestamp in existing header

        Args:
            header_bytes: Existing 2048-byte header

        Returns:
            Updated 2048-byte header with new timestamp and header_hash

        Example:
            >>> updated = VolumeHeader.update_timestamp(old_header)
        """
        if len(header_bytes) != HEADER_SIZE:
            raise ValueError(f"Header must be {HEADER_SIZE} bytes")

        header = bytearray(header_bytes)

        # Update modified timestamp
        now = int(time.time())
        struct.pack_into('>Q', header, OFFSET_MODIFIED, now)

        # Recompute header hash
        try:
            from .blake3_hash import Blake3Hash
        except ImportError:
            from blake3_hash import Blake3Hash
        header_hash = Blake3Hash.hash(bytes(header[:OFFSET_HEADER_HASH]))
        header[OFFSET_HEADER_HASH:OFFSET_HEADER_HASH + SIZE_HEADER_HASH] = header_hash

        return bytes(header)


# Example usage and tests
if __name__ == "__main__":
    import os
    from blake3_hash import Blake3Hash

    print("=" * 70)
    print("QWAMOS Post-Quantum Volume Header - Phase 4")
    print("=" * 70)

    print("\n[*] Header Layout:")
    print(f"    Total size: {HEADER_SIZE} bytes")
    print(f"    Magic: {MAGIC_HEADER.decode('ascii')} (offset {OFFSET_MAGIC})")
    print(f"    Version: 0x{HEADER_VERSION:04x} (offset {OFFSET_VERSION})")
    print(f"    Kyber ciphertext: {SIZE_KYBER_CIPHERTEXT} bytes (offset {OFFSET_KYBER_CIPHERTEXT})")
    print(f"    Footer: {MAGIC_FOOTER.decode('ascii')} (offset {OFFSET_FOOTER_MAGIC})")

    # Test 1: Create header
    print("\n[*] Test 1: Create volume header")
    salt = os.urandom(32)
    kyber_ct = os.urandom(1568)  # Stub ciphertext for testing
    master_hash = Blake3Hash.hash(b"test_master_key_32_bytes_long!!!")

    header = VolumeHeader.create(
        volume_size=100 * 1024 * 1024,  # 100 MB
        salt=salt,
        argon2_memory=1024,
        argon2_time=10,
        argon2_parallelism=4,
        kyber_ciphertext=kyber_ct,
        master_key_hash=master_hash,
        user_metadata=b"Test Volume Label"
    )

    print(f"[+] Header created: {len(header)} bytes")
    print(f"[+] Magic: {header[:8]}")
    print(f"[+] Footer: {header[2040:2048]}")

    # Test 2: Parse header
    print("\n[*] Test 2: Parse header")
    metadata = VolumeHeader.parse(header)
    print(f"[+] Parsed successfully")
    print(f"    Magic: {metadata.magic.decode('ascii')}")
    print(f"    Version: 0x{metadata.version:04x}")
    print(f"    Volume size: {metadata.volume_size:,} bytes")
    print(f"    Argon2 memory: {metadata.argon2_memory} MB")
    print(f"    Argon2 time: {metadata.argon2_time} iterations")
    print(f"    User metadata: {metadata.user_metadata[:17].decode('ascii')}")
    print(f"[+] Header valid: {metadata.is_valid()}")

    # Test 3: Round-trip
    print("\n[*] Test 3: Round-trip (create → parse → verify)")
    metadata2 = VolumeHeader.parse(header)
    if (metadata2.salt == salt and
        metadata2.kyber_ciphertext == kyber_ct and
        metadata2.master_key_hash == master_hash):
        print("[+] ✓ Round-trip successful (all fields match)")
    else:
        print("[!] ✗ ERROR: Round-trip failed!")

    # Test 4: Header hash verification
    print("\n[*] Test 4: Header hash verification")
    # Tamper with header
    tampered = bytearray(header)
    tampered[100] ^= 0xFF  # Flip bits in salt
    try:
        VolumeHeader.parse(bytes(tampered))
        print("[!] ✗ ERROR: Tampered header was accepted!")
    except ValueError as e:
        print(f"[+] ✓ Tampered header rejected: {e}")

    # Test 5: Update timestamp
    print("\n[*] Test 5: Update timestamp")
    import time
    time.sleep(1)
    updated_header = VolumeHeader.update_timestamp(header)
    metadata_updated = VolumeHeader.parse(updated_header)
    if metadata_updated.modified > metadata.modified:
        print(f"[+] ✓ Timestamp updated ({metadata.modified} → {metadata_updated.modified})")
    else:
        print("[!] ✗ ERROR: Timestamp not updated")

    # Test 6: Field offsets sanity check
    print("\n[*] Test 6: Verify field offsets don't overlap")
    offsets = [
        ("Magic", OFFSET_MAGIC, SIZE_MAGIC),
        ("Version", OFFSET_VERSION, SIZE_VERSION),
        ("Header Size", OFFSET_HEADER_SIZE, SIZE_HEADER_SIZE),
        ("Flags", OFFSET_FLAGS, SIZE_FLAGS),
        ("Volume Size", OFFSET_VOLUME_SIZE, SIZE_VOLUME_SIZE),
        ("Created", OFFSET_CREATED, SIZE_CREATED),
        ("Modified", OFFSET_MODIFIED, SIZE_MODIFIED),
        ("Salt", OFFSET_SALT, SIZE_SALT),
        ("Argon2 Memory", OFFSET_ARGON2_MEMORY, SIZE_ARGON2_MEMORY),
        ("Argon2 Time", OFFSET_ARGON2_TIME, SIZE_ARGON2_TIME),
        ("Argon2 Parallelism", OFFSET_ARGON2_PARALLELISM, SIZE_ARGON2_PARALLELISM),
        ("Kyber Ciphertext", OFFSET_KYBER_CIPHERTEXT, SIZE_KYBER_CIPHERTEXT),
        ("Master Key Hash", OFFSET_MASTER_KEY_HASH, SIZE_MASTER_KEY_HASH),
        ("Header Hash", OFFSET_HEADER_HASH, SIZE_HEADER_HASH),
        ("User Metadata", OFFSET_USER_METADATA, SIZE_USER_METADATA),
        ("Footer Magic", OFFSET_FOOTER_MAGIC, SIZE_FOOTER_MAGIC),
    ]

    last_end = 0
    all_valid = True
    for name, offset, size in offsets:
        if offset < last_end:
            print(f"[!] ✗ ERROR: {name} overlaps with previous field!")
            all_valid = False
        last_end = offset + size

    if last_end > HEADER_SIZE:
        print(f"[!] ✗ ERROR: Header exceeds {HEADER_SIZE} bytes ({last_end} total)")
        all_valid = False

    if all_valid:
        print(f"[+] ✓ All field offsets valid (total: {last_end}/{HEADER_SIZE} bytes)")

    print("\n" + "=" * 70)
    print("Volume header implementation complete!")
    print("=" * 70)
    print("\n[*] Next: Implement PostQuantumVolume class")
