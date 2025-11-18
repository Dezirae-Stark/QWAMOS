"""
QWAMOS Mock Cryptography Implementations
Mock implementations for testing without requiring actual crypto libraries
"""

import hashlib
import os
from typing import Tuple


class MockKyberKeygen:
    """Mock Kyber-1024 key generation for testing"""

    def __init__(self):
        self.public_key_size = 1568  # Kyber-1024 public key size
        self.private_key_size = 3168  # Kyber-1024 private key size

    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate a mock Kyber-1024 keypair"""
        public_key = os.urandom(self.public_key_size)
        private_key = os.urandom(self.private_key_size)
        return public_key, private_key


class MockChaCha20Poly1305:
    """Mock ChaCha20-Poly1305 AEAD cipher for testing"""

    def __init__(self):
        self.tag_size = 16  # Poly1305 tag size

    def encrypt(self, plaintext: bytes, key: bytes, nonce: bytes) -> Tuple[bytes, bytes]:
        """Mock encryption - XOR with key+nonce hash"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes")
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes")

        # Generate deterministic keystream from key+nonce
        keystream = self._generate_keystream(key, nonce, len(plaintext))
        ciphertext = bytes([p ^ k for p, k in zip(plaintext, keystream)])

        # Generate authentication tag
        tag = self._generate_tag(ciphertext, key, nonce)

        return ciphertext, tag

    def decrypt(self, ciphertext: bytes, tag: bytes, key: bytes, nonce: bytes) -> bytes:
        """Mock decryption - verify tag then XOR"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes")
        if len(nonce) != 12:
            raise ValueError("Nonce must be 12 bytes")

        # Verify authentication tag
        expected_tag = self._generate_tag(ciphertext, key, nonce)
        if tag != expected_tag:
            raise ValueError("Authentication verification failed")

        # Decrypt
        keystream = self._generate_keystream(key, nonce, len(ciphertext))
        plaintext = bytes([c ^ k for c, k in zip(ciphertext, keystream)])

        return plaintext

    def _generate_keystream(self, key: bytes, nonce: bytes, length: int) -> bytes:
        """Generate mock keystream from key and nonce"""
        keystream = b""
        counter = 0
        while len(keystream) < length:
            block = hashlib.sha256(key + nonce + counter.to_bytes(4, 'little')).digest()
            keystream += block
            counter += 1
        return keystream[:length]

    def _generate_tag(self, data: bytes, key: bytes, nonce: bytes) -> bytes:
        """Generate mock authentication tag"""
        return hashlib.sha256(data + key + nonce).digest()[:self.tag_size]


class MockArgon2id:
    """Mock Argon2id password hashing for testing"""

    def __init__(self, time_cost: int = 2, memory_cost: int = 65536, parallelism: int = 4):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.hash_length = 32

    def hash(self, password: str, salt: bytes) -> bytes:
        """Mock Argon2id hash using PBKDF2"""
        if len(salt) < 16:
            raise ValueError("Salt must be at least 16 bytes")

        password_bytes = password.encode('utf-8')
        iterations = self.time_cost * 1000  # Mock iteration count

        hash_result = hashlib.pbkdf2_hmac(
            'sha256',
            password_bytes,
            salt,
            iterations,
            dklen=self.hash_length
        )

        return hash_result

    def verify(self, password: str, hash_result: bytes, salt: bytes) -> bool:
        """Verify password against hash"""
        expected_hash = self.hash(password, salt)
        return hash_result == expected_hash


class MockBLAKE3:
    """Mock BLAKE3 hashing using BLAKE2b as substitute"""

    @staticmethod
    def hash(data: bytes, length: int = 32) -> bytes:
        """Hash data with BLAKE3 (using BLAKE2b)"""
        return hashlib.blake2b(data, digest_size=length).digest()

    @staticmethod
    def keyed_hash(data: bytes, key: bytes, length: int = 32) -> bytes:
        """Keyed hash with BLAKE3"""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes")
        return hashlib.blake2b(data, key=key[:16], digest_size=length).digest()


class MockPBKDF2:
    """Mock PBKDF2 key derivation"""

    @staticmethod
    def derive_key(password: bytes, salt: bytes, iterations: int = 100000, length: int = 32) -> bytes:
        """Derive key using PBKDF2-HMAC-SHA256"""
        return hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=length)
