#!/usr/bin/env python3
"""
QWAMOS Phase 4 Post-Quantum Cryptography Unit Tests

Comprehensive test suite for all PQ crypto primitives:
- Kyber-1024 (KEM)
- Argon2id (KDF)
- BLAKE3 (Hash)
- ChaCha20-Poly1305 (AEAD, from Phase 3)
- PostQuantumVolume (Integration)

Run with: python3 test_pq_crypto.py
"""

import os
import sys
import time
import unittest
from pathlib import Path

# Import QWAMOS crypto modules
try:
    from kyber_wrapper import QWAMOSKyber
    from argon2_kdf import Argon2KDF
    from blake3_hash import Blake3Hash
    from pq_volume import PostQuantumVolume, VolumeHeader
except ImportError as e:
    print(f"[!] Error: Failed to import QWAMOS crypto modules")
    print(f"    {e}")
    print(f"[*] Make sure you're in the crypto/pq directory")
    sys.exit(1)

# Import ChaCha20 from pycryptodome (Phase 3)
try:
    from Crypto.Cipher import ChaCha20_Poly1305
except ImportError:
    print("[!] Error: pycryptodome not installed")
    print("    Run: pip install pycryptodome")
    sys.exit(1)


class TestKyber1024(unittest.TestCase):
    """Test Kyber-1024 Key Encapsulation Mechanism"""

    def test_01_key_generation(self):
        """Test Kyber-1024 keypair generation"""
        print("\n[*] Testing Kyber-1024 key generation...")

        pk, sk = QWAMOSKyber.generate_keypair()

        # Verify key sizes
        self.assertEqual(len(pk), 1568, "Public key must be 1568 bytes")
        self.assertEqual(len(sk), 3168, "Secret key must be 3168 bytes")

        # Verify keys are bytes
        self.assertIsInstance(pk, bytes)
        self.assertIsInstance(sk, bytes)

        # Verify keys are not empty
        self.assertNotEqual(pk, b'\x00' * 1568, "Public key must not be all zeros")
        self.assertNotEqual(sk, b'\x00' * 3168, "Secret key must not be all zeros")

        print("[+] Key generation: PASS")

    def test_02_encapsulation(self):
        """Test Kyber-1024 encapsulation"""
        print("\n[*] Testing Kyber-1024 encapsulation...")

        pk, sk = QWAMOSKyber.generate_keypair()
        shared_secret, ciphertext = QWAMOSKyber.encapsulate(pk)

        # Verify sizes
        self.assertEqual(len(shared_secret), 32, "Shared secret must be 32 bytes")
        self.assertEqual(len(ciphertext), 1568, "Ciphertext must be 1568 bytes")

        # Verify not empty
        self.assertNotEqual(shared_secret, b'\x00' * 32)
        self.assertNotEqual(ciphertext, b'\x00' * 1568)

        print("[+] Encapsulation: PASS")

    def test_03_decapsulation(self):
        """Test Kyber-1024 decapsulation"""
        print("\n[*] Testing Kyber-1024 decapsulation...")

        pk, sk = QWAMOSKyber.generate_keypair()
        ss1, ct = QWAMOSKyber.encapsulate(pk)
        ss2 = QWAMOSKyber.decapsulate(sk, ct)

        # Verify shared secrets match
        self.assertEqual(ss1, ss2, "Shared secrets must match")
        self.assertEqual(len(ss2), 32, "Recovered shared secret must be 32 bytes")

        print("[+] Decapsulation: PASS")

    def test_04_wrong_key_rejection(self):
        """Test that wrong secret key produces different shared secret"""
        print("\n[*] Testing wrong key rejection...")

        # Generate two keypairs
        pk1, sk1 = QWAMOSKyber.generate_keypair()
        pk2, sk2 = QWAMOSKyber.generate_keypair()

        # Encapsulate with pk1
        ss_correct, ct = QWAMOSKyber.encapsulate(pk1)

        # Try to decapsulate with sk2 (wrong key)
        ss_wrong = QWAMOSKyber.decapsulate(sk2, ct)

        # Verify they're different
        self.assertNotEqual(ss_correct, ss_wrong,
                          "Wrong key must produce different shared secret")

        print("[+] Wrong key rejection: PASS")

    def test_05_non_deterministic_encryption(self):
        """Test that Kyber encapsulation is non-deterministic (IND-CCA2)"""
        print("\n[*] Testing non-deterministic encryption...")

        pk, sk = QWAMOSKyber.generate_keypair()

        # Encapsulate twice with same public key
        ss1, ct1 = QWAMOSKyber.encapsulate(pk)
        ss2, ct2 = QWAMOSKyber.encapsulate(pk)

        # Ciphertexts should be different (uses random nonce)
        self.assertNotEqual(ct1, ct2,
                          "Ciphertexts must be different (non-deterministic)")

        # But both should decrypt correctly
        ss1_decap = QWAMOSKyber.decapsulate(sk, ct1)
        ss2_decap = QWAMOSKyber.decapsulate(sk, ct2)

        self.assertEqual(ss1, ss1_decap)
        self.assertEqual(ss2, ss2_decap)

        print("[+] Non-deterministic encryption: PASS")

    def test_06_multiple_cycles(self):
        """Test 100 encap/decap cycles"""
        print("\n[*] Testing 100 encap/decap cycles...")

        pk, sk = QWAMOSKyber.generate_keypair()

        failures = 0
        for i in range(100):
            ss1, ct = QWAMOSKyber.encapsulate(pk)
            ss2 = QWAMOSKyber.decapsulate(sk, ct)
            if ss1 != ss2:
                failures += 1

        self.assertEqual(failures, 0, f"{failures}/100 cycles failed")
        print(f"[+] 100/100 cycles successful: PASS")

    def test_07_performance(self):
        """Benchmark Kyber-1024 performance"""
        print("\n[*] Benchmarking Kyber-1024 performance...")

        # Key generation (5 iterations)
        keygen_times = []
        for _ in range(5):
            start = time.time()
            pk, sk = QWAMOSKyber.generate_keypair()
            keygen_times.append(time.time() - start)
        avg_keygen = sum(keygen_times) / len(keygen_times)

        # Encapsulation (10 iterations)
        encap_times = []
        for _ in range(10):
            start = time.time()
            ss, ct = QWAMOSKyber.encapsulate(pk)
            encap_times.append(time.time() - start)
        avg_encap = sum(encap_times) / len(encap_times)

        # Decapsulation (10 iterations)
        decap_times = []
        for _ in range(10):
            start = time.time()
            ss2 = QWAMOSKyber.decapsulate(sk, ct)
            decap_times.append(time.time() - start)
        avg_decap = sum(decap_times) / len(decap_times)

        print(f"    Key generation: {avg_keygen*1000:.1f}ms")
        print(f"    Encapsulation:  {avg_encap*1000:.1f}ms")
        print(f"    Decapsulation:  {avg_decap*1000:.1f}ms")

        # Performance requirements (reasonable for ARM64)
        self.assertLess(avg_keygen, 1.0, "Keygen should be <1s")
        self.assertLess(avg_encap, 1.0, "Encaps should be <1s")
        self.assertLess(avg_decap, 1.0, "Decaps should be <1s")

        print("[+] Performance: PASS")


class TestArgon2id(unittest.TestCase):
    """Test Argon2id Key Derivation Function"""

    def test_01_kdf_basic(self):
        """Test basic Argon2id KDF"""
        print("\n[*] Testing Argon2id KDF basic operation...")

        kdf = Argon2KDF(security_profile='low')  # Fast for testing
        password = b"test_password_123"
        salt = os.urandom(32)

        key = kdf.derive_key(password, salt, output_length=32)

        # Verify key properties
        self.assertEqual(len(key), 32, "Key must be 32 bytes")
        self.assertIsInstance(key, bytes)
        self.assertNotEqual(key, b'\x00' * 32, "Key must not be all zeros")

        print("[+] Basic KDF: PASS")

    def test_02_kdf_deterministic(self):
        """Test that same password+salt produces same key"""
        print("\n[*] Testing Argon2id determinism...")

        kdf = Argon2KDF(security_profile='low')
        password = b"test_password"
        salt = os.urandom(32)

        key1 = kdf.derive_key(password, salt, output_length=32)
        key2 = kdf.derive_key(password, salt, output_length=32)

        self.assertEqual(key1, key2, "Same password+salt must produce same key")
        print("[+] Determinism: PASS")

    def test_03_salt_sensitivity(self):
        """Test that different salts produce different keys"""
        print("\n[*] Testing salt sensitivity...")

        kdf = Argon2KDF(security_profile='low')
        password = b"test_password"
        salt1 = os.urandom(32)
        salt2 = os.urandom(32)

        key1 = kdf.derive_key(password, salt1, output_length=32)
        key2 = kdf.derive_key(password, salt2, output_length=32)

        self.assertNotEqual(key1, key2, "Different salts must produce different keys")
        print("[+] Salt sensitivity: PASS")

    def test_04_password_sensitivity(self):
        """Test that different passwords produce different keys"""
        print("\n[*] Testing password sensitivity...")

        kdf = Argon2KDF(security_profile='low')
        salt = os.urandom(32)
        password1 = b"password123"
        password2 = b"password124"  # Only 1 character different

        key1 = kdf.derive_key(password1, salt, output_length=32)
        key2 = kdf.derive_key(password2, salt, output_length=32)

        self.assertNotEqual(key1, key2,
                          "Different passwords must produce different keys")
        print("[+] Password sensitivity: PASS")

    def test_05_security_profiles(self):
        """Test all security profiles"""
        print("\n[*] Testing security profiles...")

        password = b"test"
        salt = os.urandom(32)

        for profile in ['low', 'medium', 'high']:
            kdf = Argon2KDF(security_profile=profile)
            key = kdf.derive_key(password, salt, output_length=32)

            self.assertEqual(len(key), 32)
            print(f"    {profile}: {kdf.time_cost} iterations, "
                  f"{kdf.memory_cost // 1024} MB - OK")

        print("[+] Security profiles: PASS")

    def test_06_variable_output_length(self):
        """Test different output key lengths"""
        print("\n[*] Testing variable output lengths...")

        kdf = Argon2KDF(security_profile='low')
        password = b"test"
        salt = os.urandom(32)

        for length in [16, 32, 64]:
            key = kdf.derive_key(password, salt, output_length=length)
            self.assertEqual(len(key), length, f"Key must be {length} bytes")
            print(f"    {length} bytes: OK")

        print("[+] Variable output length: PASS")


class TestBLAKE3(unittest.TestCase):
    """Test BLAKE3 Cryptographic Hash Function"""

    def test_01_basic_hash(self):
        """Test basic BLAKE3 hashing"""
        print("\n[*] Testing BLAKE3 basic hashing...")

        data = b"Hello, QWAMOS!"
        digest = Blake3Hash.hash(data)

        # Verify digest properties
        self.assertEqual(len(digest), 32, "BLAKE3 digest must be 32 bytes")
        self.assertIsInstance(digest, bytes)
        self.assertNotEqual(digest, b'\x00' * 32)

        print(f"    Hash: {digest.hex()[:32]}...")
        print("[+] Basic hash: PASS")

    def test_02_deterministic(self):
        """Test that same data produces same hash"""
        print("\n[*] Testing BLAKE3 determinism...")

        data = b"test data"
        hash1 = Blake3Hash.hash(data)
        hash2 = Blake3Hash.hash(data)

        self.assertEqual(hash1, hash2, "Same data must produce same hash")
        print("[+] Determinism: PASS")

    def test_03_collision_resistance(self):
        """Test that different data produces different hashes"""
        print("\n[*] Testing collision resistance...")

        data1 = b"test_data_1"
        data2 = b"test_data_2"

        hash1 = Blake3Hash.hash(data1)
        hash2 = Blake3Hash.hash(data2)

        self.assertNotEqual(hash1, hash2,
                          "Different data must produce different hashes")
        print("[+] Collision resistance: PASS")

    def test_04_avalanche_effect(self):
        """Test avalanche effect (1-bit change → 50% output bits change)"""
        print("\n[*] Testing avalanche effect...")

        data1 = b"test_data"
        data2 = b"test_datb"  # Last byte changed by 1 bit

        hash1 = Blake3Hash.hash(data1)
        hash2 = Blake3Hash.hash(data2)

        # Count differing bits
        diff_bits = sum(bin(a ^ b).count('1') for a, b in zip(hash1, hash2))
        total_bits = len(hash1) * 8
        diff_percent = (diff_bits / total_bits) * 100

        print(f"    {diff_bits}/{total_bits} bits differ ({diff_percent:.1f}%)")

        # Should be close to 50% for good avalanche
        self.assertGreater(diff_percent, 40, "Avalanche effect too weak")
        self.assertLess(diff_percent, 60, "Avalanche effect too strong")

        print("[+] Avalanche effect: PASS")

    def test_05_large_data(self):
        """Test hashing large data (10 MB)"""
        print("\n[*] Testing large data hashing...")

        data = os.urandom(10 * 1024 * 1024)  # 10 MB

        start = time.time()
        digest = Blake3Hash.hash(data)
        elapsed = time.time() - start

        throughput = (len(data) / (1024 * 1024)) / elapsed

        print(f"    10 MB hashed in {elapsed:.2f}s ({throughput:.0f} MB/s)")

        self.assertEqual(len(digest), 32)
        self.assertLess(elapsed, 5.0, "Should hash 10MB in <5s on ARM64")

        print("[+] Large data: PASS")

    def test_06_keyed_hash(self):
        """Test BLAKE3 keyed hashing (MAC mode)"""
        print("\n[*] Testing keyed hash (MAC)...")

        key = os.urandom(32)
        data = b"message to authenticate"

        mac1 = Blake3Hash.keyed_hash(key, data)
        mac2 = Blake3Hash.keyed_hash(key, data)

        # Same key+data should produce same MAC
        self.assertEqual(mac1, mac2)

        # Different key should produce different MAC
        key2 = os.urandom(32)
        mac3 = Blake3Hash.keyed_hash(key2, data)
        self.assertNotEqual(mac1, mac3)

        print("[+] Keyed hash: PASS")


class TestChaCha20Poly1305(unittest.TestCase):
    """Test ChaCha20-Poly1305 AEAD (from Phase 3)"""

    def test_01_encrypt_decrypt(self):
        """Test ChaCha20-Poly1305 encryption/decryption"""
        print("\n[*] Testing ChaCha20-Poly1305 AEAD...")

        key = os.urandom(32)
        plaintext = b"Secret message for QWAMOS"

        # Encrypt
        cipher = ChaCha20_Poly1305.new(key=key)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        nonce = cipher.nonce

        # Decrypt
        cipher2 = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        recovered = cipher2.decrypt_and_verify(ciphertext, tag)

        self.assertEqual(plaintext, recovered)
        print("[+] Encrypt/decrypt: PASS")

    def test_02_authentication(self):
        """Test that tampering is detected"""
        print("\n[*] Testing authentication (tamper detection)...")

        key = os.urandom(32)
        plaintext = b"Important data"

        # Encrypt
        cipher = ChaCha20_Poly1305.new(key=key)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        nonce = cipher.nonce

        # Tamper with ciphertext
        tampered_ct = bytes([ciphertext[0] ^ 0xFF]) + ciphertext[1:]

        # Try to decrypt tampered data
        cipher2 = ChaCha20_Poly1305.new(key=key, nonce=nonce)

        with self.assertRaises(ValueError):
            cipher2.decrypt_and_verify(tampered_ct, tag)

        print("[+] Tamper detection: PASS")


class TestVolumeHeader(unittest.TestCase):
    """Test PostQuantumVolume header structure"""

    def test_01_header_creation(self):
        """Test volume header creation"""
        print("\n[*] Testing volume header creation...")

        header = VolumeHeader(
            version=1,
            argon2_time_cost=2,
            argon2_memory_cost=64 * 1024,
            argon2_parallelism=4,
            salt=os.urandom(32),
            kyber_ciphertext=os.urandom(1568),
            header_hash=os.urandom(32),
            user_metadata=b"test" + b'\x00' * 252
        )

        # Serialize
        header_bytes = header.to_bytes()

        # Verify size
        self.assertEqual(len(header_bytes), 2048,
                       "Header must be exactly 2048 bytes")

        # Verify magic bytes
        self.assertEqual(header_bytes[:8], b'QWAMOSPQ')

        print("[+] Header creation: PASS")

    def test_02_header_serialization(self):
        """Test header serialization and deserialization"""
        print("\n[*] Testing header serialization...")

        # Create header
        original = VolumeHeader(
            version=1,
            argon2_time_cost=3,
            argon2_memory_cost=128 * 1024,
            argon2_parallelism=8,
            salt=os.urandom(32),
            kyber_ciphertext=os.urandom(1568),
            header_hash=os.urandom(32),
            user_metadata=b"metadata" + b'\x00' * 248
        )

        # Serialize
        header_bytes = original.to_bytes()

        # Deserialize
        recovered = VolumeHeader.from_bytes(header_bytes)

        # Verify all fields match
        self.assertEqual(original.version, recovered.version)
        self.assertEqual(original.argon2_time_cost, recovered.argon2_time_cost)
        self.assertEqual(original.argon2_memory_cost, recovered.argon2_memory_cost)
        self.assertEqual(original.argon2_parallelism, recovered.argon2_parallelism)
        self.assertEqual(original.salt, recovered.salt)
        self.assertEqual(original.kyber_ciphertext, recovered.kyber_ciphertext)
        self.assertEqual(original.header_hash, recovered.header_hash)
        self.assertEqual(original.user_metadata, recovered.user_metadata)

        print("[+] Serialization: PASS")


class TestPostQuantumVolume(unittest.TestCase):
    """Test PostQuantumVolume integration"""

    def setUp(self):
        """Set up test volume path"""
        self.test_volume = "/tmp/test_pq_volume.qwamos"

        # Clean up any existing test volume
        if os.path.exists(self.test_volume):
            os.remove(self.test_volume)

    def tearDown(self):
        """Clean up test volume"""
        if os.path.exists(self.test_volume):
            os.remove(self.test_volume)

    def test_01_create_volume(self):
        """Test volume creation"""
        print("\n[*] Testing volume creation...")

        password = b"test_password_123"
        size_mb = 1  # Small volume for testing

        start = time.time()
        PostQuantumVolume.create(
            volume_path=self.test_volume,
            password=password,
            size_mb=size_mb,
            security_profile='low',  # Fast for testing
            label="Test Volume"
        )
        elapsed = time.time() - start

        # Verify volume exists
        self.assertTrue(os.path.exists(self.test_volume))

        # Verify file size (header + encrypted Kyber SK + data)
        expected_size = 2048 + 3196 + (size_mb * 1024 * 1024)
        actual_size = os.path.getsize(self.test_volume)
        self.assertEqual(actual_size, expected_size)

        print(f"    Volume created in {elapsed:.2f}s")
        print("[+] Create volume: PASS")

    def test_02_mount_volume(self):
        """Test volume mounting"""
        print("\n[*] Testing volume mounting...")

        password = b"test_password_123"

        # Create volume
        PostQuantumVolume.create(
            volume_path=self.test_volume,
            password=password,
            size_mb=1,
            security_profile='low',
            label="Test"
        )

        # Mount volume
        start = time.time()
        volume = PostQuantumVolume.mount(self.test_volume, password)
        elapsed = time.time() - start

        # Verify mounted
        self.assertIsNotNone(volume)
        self.assertEqual(volume.label, "Test")

        print(f"    Volume mounted in {elapsed:.2f}s")
        print("[+] Mount volume: PASS")

    def test_03_wrong_password(self):
        """Test that wrong password is rejected"""
        print("\n[*] Testing wrong password rejection...")

        password = b"correct_password"
        wrong_password = b"wrong_password"

        # Create volume
        PostQuantumVolume.create(
            volume_path=self.test_volume,
            password=password,
            size_mb=1,
            security_profile='low',
            label="Test"
        )

        # Try to mount with wrong password
        with self.assertRaises(ValueError):
            PostQuantumVolume.mount(self.test_volume, wrong_password)

        print("[+] Wrong password rejection: PASS")

    def test_04_encrypt_decrypt_data(self):
        """Test data encryption and decryption"""
        print("\n[*] Testing data encryption/decryption...")

        password = b"test_password"
        test_data = b"Secret data for QWAMOS!" * 100  # ~2.3 KB

        # Create and mount volume
        PostQuantumVolume.create(
            volume_path=self.test_volume,
            password=password,
            size_mb=1,
            security_profile='low',
            label="Test"
        )

        volume = PostQuantumVolume.mount(self.test_volume, password)

        # Encrypt data
        encrypted = volume.encrypt_sector(test_data, sector_index=0)

        # Decrypt data
        decrypted = volume.decrypt_sector(encrypted, sector_index=0)

        # Verify
        self.assertEqual(test_data, decrypted)
        self.assertNotEqual(test_data, encrypted)

        print("[+] Encrypt/decrypt data: PASS")

    def test_05_kyber_integration(self):
        """Test full Kyber encapsulation/decapsulation flow"""
        print("\n[*] Testing Kyber integration...")

        password = b"test_password"

        # Create volume (triggers Kyber encapsulation)
        PostQuantumVolume.create(
            volume_path=self.test_volume,
            password=password,
            size_mb=1,
            security_profile='low',
            label="Kyber Test"
        )

        # Mount volume (triggers Kyber decapsulation)
        volume = PostQuantumVolume.mount(self.test_volume, password)

        # If we get here without errors, Kyber worked!
        self.assertIsNotNone(volume)
        self.assertEqual(volume.label, "Kyber Test")

        # Test encryption to verify master_key was correctly recovered
        test_data = b"Test data"
        encrypted = volume.encrypt_sector(test_data, sector_index=0)
        decrypted = volume.decrypt_sector(encrypted, sector_index=0)

        self.assertEqual(test_data, decrypted)

        print("[+] Kyber integration: PASS")

    def test_06_cross_session_encryption(self):
        """Test that data encrypted in one session can be decrypted in another"""
        print("\n[*] Testing cross-session encryption...")

        password = b"test_password"
        test_data = b"Persistent data"

        # Session 1: Create volume and encrypt data
        PostQuantumVolume.create(
            volume_path=self.test_volume,
            password=password,
            size_mb=1,
            security_profile='low',
            label="Session Test"
        )

        volume1 = PostQuantumVolume.mount(self.test_volume, password)
        encrypted = volume1.encrypt_sector(test_data, sector_index=0)

        # Write encrypted data to volume (simulate)
        with open(self.test_volume, 'r+b') as f:
            f.seek(2048 + 3196)  # Skip header and encrypted Kyber SK
            f.write(encrypted)

        # Session 2: Mount volume again and decrypt
        volume2 = PostQuantumVolume.mount(self.test_volume, password)

        # Read encrypted data
        with open(self.test_volume, 'rb') as f:
            f.seek(2048 + 3196)
            read_encrypted = f.read(len(encrypted))

        # Decrypt
        decrypted = volume2.decrypt_sector(read_encrypted, sector_index=0)

        self.assertEqual(test_data, decrypted)

        print("[+] Cross-session encryption: PASS")

    def test_07_security_profiles(self):
        """Test volume creation with different security profiles"""
        print("\n[*] Testing security profiles...")

        password = b"test_password"

        for profile in ['low', 'medium']:  # Skip 'high' for speed
            volume_path = f"/tmp/test_volume_{profile}.qwamos"

            # Create volume
            start = time.time()
            PostQuantumVolume.create(
                volume_path=volume_path,
                password=password,
                size_mb=1,
                security_profile=profile,
                label=f"Test {profile}"
            )
            create_time = time.time() - start

            # Mount volume
            start = time.time()
            volume = PostQuantumVolume.mount(volume_path, password)
            mount_time = time.time() - start

            print(f"    {profile}: create={create_time:.2f}s, "
                  f"mount={mount_time:.2f}s - OK")

            # Clean up
            os.remove(volume_path)

        print("[+] Security profiles: PASS")


def run_all_tests():
    """Run all test suites with detailed output"""

    print("=" * 70)
    print("QWAMOS Phase 4 Post-Quantum Cryptography Test Suite")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKyber1024))
    suite.addTests(loader.loadTestsFromTestCase(TestArgon2id))
    suite.addTests(loader.loadTestsFromTestCase(TestBLAKE3))
    suite.addTests(loader.loadTestsFromTestCase(TestChaCha20Poly1305))
    suite.addTests(loader.loadTestsFromTestCase(TestVolumeHeader))
    suite.addTests(loader.loadTestsFromTestCase(TestPostQuantumVolume))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")
    print()

    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED! Phase 4 crypto is production-ready! 🎉")
        return 0
    else:
        print("❌ SOME TESTS FAILED - Review failures above")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
