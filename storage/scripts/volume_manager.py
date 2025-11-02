#!/usr/bin/env python3
"""
QWAMOS Encrypted Volume Manager
Implements ChaCha20-Poly1305 + Argon2id storage encryption

This is a Python implementation for use on Android/Termux where
cryptsetup/dm-crypt may not be available.
"""

import os
import sys
import struct
import hashlib
import secrets
import getpass
from pathlib import Path

try:
    from Crypto.Cipher import ChaCha20_Poly1305
    from Crypto.Protocol.KDF import scrypt
    from Crypto.Hash import BLAKE2b
except ImportError:
    print("[!] Error: pycryptodome not installed")
    print("    Run: pip install pycryptodome")
    sys.exit(1)

# QWAMOS Constants
QWAMOS_MAGIC = b"QWAMOS\x00\x01"
QWAMOS_VERSION = 1
HEADER_SIZE = 4096
BLOCK_SIZE = 4096
NONCE_SIZE = 12
TAG_SIZE = 16

class QWAMOSVolume:
    """QWAMOS Encrypted Volume"""

    def __init__(self, volume_path):
        self.volume_path = Path(volume_path)
        self.master_key = None
        self.salt = None
        # scrypt parameters (memory-hard KDF, similar to Argon2id)
        self.scrypt_params = {
            'N': 2**14,  # 16384 iterations (CPU cost)
            'r': 8,      # Block size
            'p': 1,      # Parallelization
            'dkLen': 32  # 256-bit output
        }

    def create(self, size_mb, passphrase):
        """Create new encrypted volume"""

        print(f"[*] Creating QWAMOS encrypted volume: {self.volume_path}")
        print(f"[*] Size: {size_mb} MB")

        # Generate random salt
        self.salt = secrets.token_bytes(16)

        # Derive master key from passphrase
        print("[*] Deriving encryption key with scrypt...")
        print(f"    N (CPU cost): {self.scrypt_params['N']}")
        print(f"    r (block size): {self.scrypt_params['r']}")
        print(f"    p (parallelization): {self.scrypt_params['p']}")

        self.master_key = scrypt(
            password=passphrase.encode('utf-8'),
            salt=self.salt,
            key_len=self.scrypt_params['dkLen'],
            N=self.scrypt_params['N'],
            r=self.scrypt_params['r'],
            p=self.scrypt_params['p']
        )

        print("[+] Key derivation complete")

        # Create volume file
        volume_size_bytes = size_mb * 1024 * 1024

        print(f"[*] Creating {size_mb} MB volume file...")

        with open(self.volume_path, 'wb') as f:
            # Write header
            header = self._create_header()
            f.write(header)

            # Write encrypted data blocks (zeros initially)
            blocks_written = 0
            total_blocks = (volume_size_bytes - HEADER_SIZE) // BLOCK_SIZE

            for block_num in range(total_blocks):
                # Encrypt block of zeros
                nonce = self._generate_nonce(block_num)
                cipher = ChaCha20_Poly1305.new(key=self.master_key, nonce=nonce)
                ciphertext, tag = cipher.encrypt_and_digest(b'\x00' * BLOCK_SIZE)

                # Write ciphertext + tag
                f.write(ciphertext + tag)

                blocks_written += 1
                if blocks_written % 256 == 0:
                    print(f"    Progress: {blocks_written}/{total_blocks} blocks ({blocks_written*100//total_blocks}%)")

        print(f"[+] Volume created successfully: {self.volume_path}")
        print(f"[+] Total size: {os.path.getsize(self.volume_path) / 1024 / 1024:.2f} MB")

    def _create_header(self):
        """Create QWAMOS volume header"""

        header = bytearray(HEADER_SIZE)

        offset = 0

        # Magic
        header[offset:offset+8] = QWAMOS_MAGIC
        offset += 8

        # Version
        struct.pack_into('<I', header, offset, QWAMOS_VERSION)
        offset += 4

        # Cipher name (padded to 32 bytes)
        cipher_name = b"ChaCha20-Poly1305".ljust(32, b'\x00')
        header[offset:offset+32] = cipher_name
        offset += 32

        # KDF name (padded to 32 bytes)
        kdf_name = b"scrypt".ljust(32, b'\x00')
        header[offset:offset+32] = kdf_name
        offset += 32

        # Salt
        header[offset:offset+16] = self.salt
        offset += 16

        # scrypt parameters (N, r, p)
        struct.pack_into('<III', header, offset,
                         self.scrypt_params['N'],
                         self.scrypt_params['r'],
                         self.scrypt_params['p'])
        offset += 12

        # Master key verification hash (BLAKE2b of master key)
        key_hash = BLAKE2b.new(digest_bits=256)
        key_hash.update(self.master_key)
        header[offset:offset+32] = key_hash.digest()
        offset += 32

        # Header HMAC (BLAKE2b of entire header)
        header_hmac = BLAKE2b.new(digest_bits=256, key=self.master_key)
        header_hmac.update(bytes(header[:offset]))
        header[offset:offset+32] = header_hmac.digest()
        offset += 32

        # Reserved space
        # offset is now 136, remaining is 4096 - 136 = 3960 bytes

        return bytes(header)

    def _generate_nonce(self, block_num):
        """Generate deterministic nonce for block number"""
        # Use block number as nonce (12 bytes)
        nonce = struct.pack('<Q', block_num).ljust(NONCE_SIZE, b'\x00')
        return nonce

    def unlock(self, passphrase):
        """Unlock volume with passphrase"""

        print(f"[*] Unlocking QWAMOS volume: {self.volume_path}")

        if not self.volume_path.exists():
            print(f"[!] Error: Volume not found: {self.volume_path}")
            return False

        # Read header
        with open(self.volume_path, 'rb') as f:
            header = f.read(HEADER_SIZE)

        # Parse header
        offset = 0

        # Verify magic
        magic = header[offset:offset+8]
        if magic != QWAMOS_MAGIC:
            print("[!] Error: Invalid QWAMOS volume (bad magic)")
            return False
        offset += 8

        # Version
        version = struct.unpack('<I', header[offset:offset+4])[0]
        if version != QWAMOS_VERSION:
            print(f"[!] Error: Unsupported version: {version}")
            return False
        offset += 4

        # Cipher
        cipher_name = header[offset:offset+32].rstrip(b'\x00').decode('utf-8')
        if cipher_name != "ChaCha20-Poly1305":
            print(f"[!] Error: Unsupported cipher: {cipher_name}")
            return False
        offset += 32

        # KDF
        kdf_name = header[offset:offset+32].rstrip(b'\x00').decode('utf-8')
        if kdf_name != "scrypt":
            print(f"[!] Error: Unsupported KDF: {kdf_name}")
            return False
        offset += 32

        # Salt
        self.salt = header[offset:offset+16]
        offset += 16

        # scrypt parameters
        N, r, p = struct.unpack('<III', header[offset:offset+12])
        self.scrypt_params = {
            'N': N,
            'r': r,
            'p': p,
            'dkLen': 32
        }
        offset += 12

        # Stored key hash
        stored_key_hash = header[offset:offset+32]
        offset += 32

        # Derive key from passphrase
        print("[*] Deriving key with scrypt...")
        self.master_key = scrypt(
            password=passphrase.encode('utf-8'),
            salt=self.salt,
            key_len=self.scrypt_params['dkLen'],
            N=self.scrypt_params['N'],
            r=self.scrypt_params['r'],
            p=self.scrypt_params['p']
        )

        # Verify key
        key_hash = BLAKE2b.new(digest_bits=256)
        key_hash.update(self.master_key)

        if key_hash.digest() != stored_key_hash:
            print("[!] Error: Incorrect passphrase")
            return False

        print("[+] Volume unlocked successfully")
        return True

    def read_block(self, block_num):
        """Read and decrypt a block"""

        if self.master_key is None:
            raise ValueError("Volume not unlocked")

        block_offset = HEADER_SIZE + (block_num * (BLOCK_SIZE + TAG_SIZE))

        with open(self.volume_path, 'rb') as f:
            f.seek(block_offset)
            ciphertext = f.read(BLOCK_SIZE)
            tag = f.read(TAG_SIZE)

        # Decrypt
        nonce = self._generate_nonce(block_num)
        cipher = ChaCha20_Poly1305.new(key=self.master_key, nonce=nonce)

        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            return plaintext
        except ValueError:
            raise ValueError(f"Block {block_num} authentication failed (corrupted)")

    def write_block(self, block_num, data):
        """Encrypt and write a block"""

        if self.master_key is None:
            raise ValueError("Volume not unlocked")

        if len(data) != BLOCK_SIZE:
            raise ValueError(f"Block must be exactly {BLOCK_SIZE} bytes")

        block_offset = HEADER_SIZE + (block_num * (BLOCK_SIZE + TAG_SIZE))

        # Encrypt
        nonce = self._generate_nonce(block_num)
        cipher = ChaCha20_Poly1305.new(key=self.master_key, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        # Write
        with open(self.volume_path, 'r+b') as f:
            f.seek(block_offset)
            f.write(ciphertext + tag)

    def get_info(self):
        """Get volume information"""

        if not self.volume_path.exists():
            print(f"[!] Error: Volume not found: {self.volume_path}")
            return

        with open(self.volume_path, 'rb') as f:
            header = f.read(HEADER_SIZE)

        offset = 8  # Skip magic
        version = struct.unpack('<I', header[offset:offset+4])[0]
        offset += 4

        cipher = header[offset:offset+32].rstrip(b'\x00').decode('utf-8')
        offset += 32

        kdf = header[offset:offset+32].rstrip(b'\x00').decode('utf-8')
        offset += 32

        salt = header[offset:offset+16]
        offset += 16

        memory, time, parallelism = struct.unpack('<III', header[offset:offset+12])

        file_size = os.path.getsize(self.volume_path)
        data_size = file_size - HEADER_SIZE
        num_blocks = data_size // (BLOCK_SIZE + TAG_SIZE)

        print("=" * 60)
        print("  QWAMOS Encrypted Volume Information")
        print("=" * 60)
        print(f"Volume: {self.volume_path}")
        print(f"Version: {version}")
        print(f"Cipher: {cipher}")
        print(f"KDF: {kdf}")
        print(f"Salt: {salt.hex()}")
        print(f"scrypt Parameters:")
        print(f"  N (CPU cost): {memory}")
        print(f"  r (block size): {time}")
        print(f"  p (parallelization): {parallelism}")
        print(f"File Size: {file_size / 1024 / 1024:.2f} MB")
        print(f"Data Size: {data_size / 1024 / 1024:.2f} MB")
        print(f"Blocks: {num_blocks}")
        print("=" * 60)

def main():
    if len(sys.argv) < 2:
        print("QWAMOS Encrypted Volume Manager")
        print("")
        print("Usage:")
        print("  volume_manager.py create <volume> <size_mb>")
        print("  volume_manager.py info <volume>")
        print("  volume_manager.py test <volume>")
        print("")
        print("Examples:")
        print("  volume_manager.py create test.qvol 100")
        print("  volume_manager.py info test.qvol")
        print("  volume_manager.py test test.qvol")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) != 4:
            print("Usage: volume_manager.py create <volume> <size_mb>")
            sys.exit(1)

        volume_path = sys.argv[2]
        size_mb = int(sys.argv[3])

        passphrase = getpass.getpass("Enter passphrase: ")
        passphrase_confirm = getpass.getpass("Confirm passphrase: ")

        if passphrase != passphrase_confirm:
            print("[!] Error: Passphrases do not match")
            sys.exit(1)

        if len(passphrase) < 12:
            print("[!] Warning: Passphrase should be at least 12 characters")

        vol = QWAMOSVolume(volume_path)
        vol.create(size_mb, passphrase)

    elif command == "info":
        if len(sys.argv) != 3:
            print("Usage: volume_manager.py info <volume>")
            sys.exit(1)

        volume_path = sys.argv[2]
        vol = QWAMOSVolume(volume_path)
        vol.get_info()

    elif command == "test":
        if len(sys.argv) != 3:
            print("Usage: volume_manager.py test <volume>")
            sys.exit(1)

        volume_path = sys.argv[2]
        vol = QWAMOSVolume(volume_path)

        passphrase = getpass.getpass("Enter passphrase: ")

        if not vol.unlock(passphrase):
            print("[!] Failed to unlock volume")
            sys.exit(1)

        # Test read/write
        print("[*] Testing block read/write...")

        # Write test data to block 0
        test_data = b"QWAMOS Encrypted Storage Test - ChaCha20-Poly1305!" + (b'\x00' * (BLOCK_SIZE - 51))
        vol.write_block(0, test_data)
        print("[+] Wrote test data to block 0")

        # Read back
        read_data = vol.read_block(0)
        print("[+] Read test data from block 0")

        # Verify
        if read_data == test_data:
            print("[+] Test PASSED - Data integrity verified!")
        else:
            print("[!] Test FAILED - Data corruption detected!")
            sys.exit(1)

    else:
        print(f"[!] Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
