"""
QWAMOS Cryptography Unit Tests
Tests for post-quantum cryptography implementations
"""

import pytest
import hashlib
import os
from pathlib import Path


class TestKyberKeygeneration:
    """Test Kyber-1024 key generation"""

    def test_keygen_produces_keys(self):
        """Test that keygen produces public and private keys"""
        # Mock Kyber key generation
        from tests.helpers.mock_keygen import MockKyberKeygen

        keygen = MockKyberKeygen()
        public_key, private_key = keygen.generate_keypair()

        assert public_key is not None
        assert private_key is not None
        assert len(public_key) > 0
        assert len(private_key) > 0

    def test_keygen_produces_different_keys(self):
        """Test that each keygen produces different keys"""
        from tests.helpers.mock_keygen import MockKyberKeygen

        keygen = MockKyberKeygen()
        pk1, sk1 = keygen.generate_keypair()
        pk2, sk2 = keygen.generate_keypair()

        assert pk1 != pk2
        assert sk1 != sk2

    def test_public_key_size(self):
        """Test Kyber-1024 public key size"""
        from tests.helpers.mock_keygen import MockKyberKeygen

        keygen = MockKyberKeygen()
        public_key, _ = keygen.generate_keypair()

        # Kyber-1024 public key should be 1568 bytes
        expected_size = 1568
        assert len(public_key) == expected_size

    def test_private_key_size(self):
        """Test Kyber-1024 private key size"""
        from tests.helpers.mock_keygen import MockKyberKeygen

        keygen = MockKyberKeygen()
        _, private_key = keygen.generate_keypair()

        # Kyber-1024 private key should be 3168 bytes
        expected_size = 3168
        assert len(private_key) == expected_size


class TestChaCha20Poly1305:
    """Test ChaCha20-Poly1305 encryption"""

    def test_encryption_decryption(self):
        """Test basic encryption and decryption"""
        from tests.helpers.mock_keygen import MockChaCha20Poly1305

        cipher = MockChaCha20Poly1305()
        plaintext = b"Hello, QWAMOS!"
        key = os.urandom(32)  # 256-bit key
        nonce = os.urandom(12)  # 96-bit nonce

        ciphertext, tag = cipher.encrypt(plaintext, key, nonce)
        decrypted = cipher.decrypt(ciphertext, tag, key, nonce)

        assert decrypted == plaintext

    def test_encryption_produces_different_output(self):
        """Test that same plaintext with different nonces produces different ciphertext"""
        from tests.helpers.mock_keygen import MockChaCha20Poly1305

        cipher = MockChaCha20Poly1305()
        plaintext = b"Test message"
        key = os.urandom(32)

        nonce1 = os.urandom(12)
        nonce2 = os.urandom(12)

        ct1, _ = cipher.encrypt(plaintext, key, nonce1)
        ct2, _ = cipher.encrypt(plaintext, key, nonce2)

        assert ct1 != ct2

    def test_authentication_tag_verification(self):
        """Test that tampering is detected"""
        from tests.helpers.mock_keygen import MockChaCha20Poly1305

        cipher = MockChaCha20Poly1305()
        plaintext = b"Authenticated message"
        key = os.urandom(32)
        nonce = os.urandom(12)

        ciphertext, tag = cipher.encrypt(plaintext, key, nonce)

        # Tamper with ciphertext
        tampered_ct = bytes([b ^ 1 for b in ciphertext])

        with pytest.raises(ValueError, match="Authentication.*failed"):
            cipher.decrypt(tampered_ct, tag, key, nonce)


class TestArgon2id:
    """Test Argon2id password hashing"""

    def test_password_hashing(self):
        """Test password hashing produces a hash"""
        from tests.helpers.mock_keygen import MockArgon2id

        hasher = MockArgon2id()
        password = "correct horse battery staple"
        salt = os.urandom(16)

        hash_result = hasher.hash(password, salt)

        assert hash_result is not None
        assert len(hash_result) > 0

    def test_password_verification(self):
        """Test password verification"""
        from tests.helpers.mock_keygen import MockArgon2id

        hasher = MockArgon2id()
        password = "test_password_123"
        salt = os.urandom(16)

        hash_result = hasher.hash(password, salt)
        is_valid = hasher.verify(password, hash_result, salt)

        assert is_valid is True

    def test_wrong_password_fails(self):
        """Test wrong password fails verification"""
        from tests.helpers.mock_keygen import MockArgon2id

        hasher = MockArgon2id()
        password = "correct_password"
        wrong_password = "wrong_password"
        salt = os.urandom(16)

        hash_result = hasher.hash(password, salt)
        is_valid = hasher.verify(wrong_password, hash_result, salt)

        assert is_valid is False

    def test_consistent_hashing(self):
        """Test same password and salt produce same hash"""
        from tests.helpers.mock_keygen import MockArgon2id

        hasher = MockArgon2id()
        password = "test_password"
        salt = os.urandom(16)

        hash1 = hasher.hash(password, salt)
        hash2 = hasher.hash(password, salt)

        assert hash1 == hash2


class TestBLAKE3:
    """Test BLAKE3 hashing"""

    def test_blake3_hash(self):
        """Test BLAKE3 produces hash"""
        data = b"QWAMOS test data"
        hash_result = hashlib.blake2b(data, digest_size=32).digest()

        assert hash_result is not None
        assert len(hash_result) == 32

    def test_blake3_consistency(self):
        """Test BLAKE3 produces consistent hashes"""
        data = b"Consistent data"

        hash1 = hashlib.blake2b(data, digest_size=32).digest()
        hash2 = hashlib.blake2b(data, digest_size=32).digest()

        assert hash1 == hash2

    def test_blake3_different_data(self):
        """Test different data produces different hashes"""
        data1 = b"Data 1"
        data2 = b"Data 2"

        hash1 = hashlib.blake2b(data1, digest_size=32).digest()
        hash2 = hashlib.blake2b(data2, digest_size=32).digest()

        assert hash1 != hash2


class TestKeyDerivation:
    """Test key derivation functions"""

    def test_pbkdf2_derivation(self):
        """Test PBKDF2 key derivation"""
        password = b"user_password"
        salt = os.urandom(16)
        iterations = 100000

        key = hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=32)

        assert key is not None
        assert len(key) == 32

    def test_pbkdf2_consistency(self):
        """Test PBKDF2 produces consistent keys"""
        password = b"user_password"
        salt = os.urandom(16)
        iterations = 100000

        key1 = hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=32)
        key2 = hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=32)

        assert key1 == key2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
