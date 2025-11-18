#!/usr/bin/env python3
"""
QWAMOS Post-Quantum Encrypted Volume Manager
Phase XIII: PQC Storage Subsystem

Manages encrypted virtual block devices for VM storage with:
- ChaCha20-Poly1305 AEAD encryption
- 4KB block size for optimal performance
- Sparse file support for efficient space usage
- Integrity verification per block
- Transparent encryption/decryption

Author: QWAMOS Project
License: MIT
"""

import os
import json
import struct
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass, asdict

import sys
sys.path.append(str(Path(__file__).parent.parent / "crypto"))
from pqc_keystore import PQCKeystore

# Constants
BLOCK_SIZE = 4096  # 4 KB blocks
HEADER_SIZE = 4096  # 4 KB header
MAGIC = b'QWAMOS-PQC-VOL-v1'


@dataclass
class VolumeHeader:
    """Metadata header for encrypted volumes."""
    magic: str
    version: int
    volume_name: str
    vm_name: str
    key_id: str
    total_blocks: int
    block_size: int
    created_at: str
    encrypted: bool
    compression: str  # "none", "zstd" (future)


class PQCVolume:
    """
    Post-Quantum Encrypted Volume for VM Storage.

    Implements a virtual encrypted block device with:
    - Per-block encryption with ChaCha20-Poly1305
    - Authenticated integrity checking
    - Sparse file support
    - Fast random access
    """

    def __init__(self, volume_path: str, keystore: Optional[PQCKeystore] = None):
        """
        Initialize volume manager.

        Args:
            volume_path: Path to volume file
            keystore: PQCKeystore instance (creates new if None)
        """
        self.volume_path = Path(volume_path)
        self.keystore = keystore or PQCKeystore()
        self.header: Optional[VolumeHeader] = None
        self.encryption_key: Optional[bytes] = None
        self.file_handle = None

    def create(self, volume_name: str, vm_name: str, size_mb: int) -> str:
        """
        Create a new encrypted volume.

        Args:
            volume_name: Name for the volume
            vm_name: Associated VM name
            size_mb: Volume size in megabytes

        Returns:
            Key ID used for encryption
        """
        # Generate encryption keys
        _, _, key_id = self.keystore.generate_vm_keys(vm_name)
        self.encryption_key = self.keystore.derive_storage_key(
            key_id,
            context=f"volume-{volume_name}".encode('utf-8')
        )

        # Calculate total blocks
        total_size = size_mb * 1024 * 1024
        total_blocks = total_size // BLOCK_SIZE

        # Create volume header
        from datetime import datetime
        self.header = VolumeHeader(
            magic=MAGIC.decode('utf-8'),
            version=1,
            volume_name=volume_name,
            vm_name=vm_name,
            key_id=key_id,
            total_blocks=total_blocks,
            block_size=BLOCK_SIZE,
            created_at=datetime.now().isoformat(),
            encrypted=True,
            compression="none"
        )

        # Create sparse file
        self._create_volume_file(total_blocks)

        # Write header
        self._write_header()

        print(f"✅ Created encrypted volume: {self.volume_path}")
        print(f"   Size: {size_mb} MB ({total_blocks} blocks)")
        print(f"   Key ID: {key_id}")

        return key_id

    def open(self, readonly: bool = False):
        """
        Open an existing encrypted volume.

        Args:
            readonly: Open in read-only mode
        """
        if not self.volume_path.exists():
            raise FileNotFoundError(f"Volume not found: {self.volume_path}")

        # Open file
        mode = 'rb' if readonly else 'r+b'
        self.file_handle = open(self.volume_path, mode)

        # Read and validate header
        self._read_header()

        # Derive encryption key
        self.encryption_key = self.keystore.derive_storage_key(
            self.header.key_id,
            context=f"volume-{self.header.volume_name}".encode('utf-8')
        )

    def close(self):
        """Close the volume file."""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

    def read_block(self, block_number: int) -> bytes:
        """
        Read and decrypt a block.

        Args:
            block_number: Block index to read

        Returns:
            Decrypted block data (BLOCK_SIZE bytes)
        """
        if block_number >= self.header.total_blocks:
            raise ValueError(f"Block {block_number} out of range")

        # Seek to block position (after header)
        block_offset = HEADER_SIZE + (block_number * (BLOCK_SIZE + 16 + 12 + 4))
        self.file_handle.seek(block_offset)

        # Read encrypted block with metadata
        # Format: [4B size][12B nonce][BLOCK_SIZE ciphertext][16B tag]
        size_bytes = self.file_handle.read(4)
        if len(size_bytes) < 4:
            # Uninitialized block, return zeros
            return b'\x00' * BLOCK_SIZE

        size = struct.unpack('<I', size_bytes)[0]
        if size == 0:
            # Sparse block
            return b'\x00' * BLOCK_SIZE

        nonce = self.file_handle.read(12)
        ciphertext = self.file_handle.read(BLOCK_SIZE)
        tag = self.file_handle.read(16)

        # Decrypt
        plaintext = self.keystore.decrypt_data(ciphertext, nonce, tag, self.encryption_key)

        # Pad to block size if needed
        if len(plaintext) < BLOCK_SIZE:
            plaintext += b'\x00' * (BLOCK_SIZE - len(plaintext))

        return plaintext

    def write_block(self, block_number: int, data: bytes):
        """
        Encrypt and write a block.

        Args:
            block_number: Block index to write
            data: Block data (up to BLOCK_SIZE bytes)
        """
        if block_number >= self.header.total_blocks:
            raise ValueError(f"Block {block_number} out of range")

        if len(data) > BLOCK_SIZE:
            raise ValueError(f"Data exceeds block size ({len(data)} > {BLOCK_SIZE})")

        # Pad to block size
        if len(data) < BLOCK_SIZE:
            data += b'\x00' * (BLOCK_SIZE - len(data))

        # Encrypt
        encrypted = self.keystore.encrypt_data(data, self.encryption_key)

        # Seek to block position
        block_offset = HEADER_SIZE + (block_number * (BLOCK_SIZE + 16 + 12 + 4))
        self.file_handle.seek(block_offset)

        # Write encrypted block
        # Format: [4B size][12B nonce][BLOCK_SIZE ciphertext][16B tag]
        size = struct.pack('<I', BLOCK_SIZE)
        self.file_handle.write(size)
        self.file_handle.write(encrypted['nonce'])
        self.file_handle.write(encrypted['ciphertext'])
        self.file_handle.write(encrypted['tag'])

    def zero_block(self, block_number: int):
        """
        Mark a block as sparse (all zeros) without writing data.

        Args:
            block_number: Block index to zero
        """
        if block_number >= self.header.total_blocks:
            raise ValueError(f"Block {block_number} out of range")

        # Seek to block position
        block_offset = HEADER_SIZE + (block_number * (BLOCK_SIZE + 16 + 12 + 4))
        self.file_handle.seek(block_offset)

        # Write zero size marker
        self.file_handle.write(struct.pack('<I', 0))

    def get_stats(self) -> Dict:
        """
        Get volume statistics.

        Returns:
            Dictionary with volume stats
        """
        actual_size = self.volume_path.stat().st_size if self.volume_path.exists() else 0

        return {
            'volume_name': self.header.volume_name,
            'vm_name': self.header.vm_name,
            'total_blocks': self.header.total_blocks,
            'block_size': self.header.block_size,
            'logical_size_mb': (self.header.total_blocks * self.header.block_size) / (1024 * 1024),
            'actual_size_mb': actual_size / (1024 * 1024),
            'compression_ratio': f"{(actual_size / (self.header.total_blocks * self.header.block_size) * 100):.1f}%",
            'encrypted': self.header.encrypted,
            'created_at': self.header.created_at
        }

    # Private methods

    def _create_volume_file(self, total_blocks: int):
        """Create sparse volume file."""
        # Create parent directory
        self.volume_path.parent.mkdir(parents=True, exist_ok=True)

        # Create sparse file (truncate creates holes)
        total_size = HEADER_SIZE + (total_blocks * (BLOCK_SIZE + 16 + 12 + 4))

        with open(self.volume_path, 'wb') as f:
            f.truncate(total_size)

    def _write_header(self):
        """Write volume header to file."""
        header_dict = asdict(self.header)
        header_json = json.dumps(header_dict, indent=2).encode('utf-8')

        # Pad to HEADER_SIZE
        if len(header_json) > HEADER_SIZE - len(MAGIC) - 4:
            raise ValueError("Header too large")

        header_data = MAGIC + struct.pack('<I', len(header_json)) + header_json
        header_data += b'\x00' * (HEADER_SIZE - len(header_data))

        with open(self.volume_path, 'r+b') as f:
            f.write(header_data)

    def _read_header(self):
        """Read and validate volume header."""
        self.file_handle.seek(0)
        magic = self.file_handle.read(len(MAGIC))

        if magic != MAGIC:
            raise ValueError(f"Invalid volume file (bad magic)")

        size_bytes = self.file_handle.read(4)
        header_size = struct.unpack('<I', size_bytes)[0]

        header_json = self.file_handle.read(header_size)
        header_dict = json.loads(header_json.decode('utf-8'))

        self.header = VolumeHeader(**header_dict)


def main():
    """Demo and testing."""
    print("=" * 70)
    print("QWAMOS Post-Quantum Encrypted Volume Manager - Demo")
    print("=" * 70)

    volume_path = os.path.expanduser("~/.qwamos/test_pqc_volume.qvol")

    # Create volume
    print("\n1. Creating encrypted volume...")
    volume = PQCVolume(volume_path)
    key_id = volume.create("test-volume", "test-vm", size_mb=10)
    print(f"   ✅ Volume created with key: {key_id}")

    # Open volume
    print("\n2. Opening volume...")
    volume.open()
    print(f"   ✅ Volume opened successfully")

    # Write test data
    print("\n3. Writing encrypted blocks...")
    test_data = [
        b"Block 0: QWAMOS Encrypted Storage Test",
        b"Block 1: Post-Quantum Cryptography",
        b"Block 2: ChaCha20-Poly1305 AEAD Cipher"
    ]

    for i, data in enumerate(test_data):
        volume.write_block(i, data)
        print(f"   ✅ Written block {i} ({len(data)} bytes)")

    # Read back data
    print("\n4. Reading encrypted blocks...")
    for i in range(len(test_data)):
        decrypted = volume.read_block(i)
        original_len = len(test_data[i])
        recovered = decrypted[:original_len]
        print(f"   ✅ Block {i}: {recovered.decode('utf-8')}")
        print(f"      Integrity: {recovered == test_data[i]}")

    # Get stats
    print("\n5. Volume statistics...")
    stats = volume.get_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")

    # Close volume
    volume.close()
    print("\n✅ Volume closed")

    # Cleanup
    os.remove(volume_path)
    print("✅ Test volume removed")

    print("\n" + "=" * 70)
    print("✅ PQC Volume Manager operational - Ready for VM integration")
    print("=" * 70)


if __name__ == "__main__":
    main()
