#!/usr/bin/env python3
"""
Unit Tests for Phase XIII: PQC Storage Subsystem

Tests for:
- PQC Keystore (key generation, derivation, rotation)
- Encrypted Volume Manager (create, read, write, integrity)
- End-to-end encryption workflow

Author: QWAMOS Project
License: MIT
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from crypto.pqc_keystore import PQCKeystore, KeyMetadata
from storage.pqc_volume import PQCVolume


class TestPQCKeystore(unittest.TestCase):
    """Test cases for PQC Keystore."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.keystore = PQCKeystore(keystore_path=self.test_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_generate_vm_keys(self):
        """Test VM key generation."""
        public_key, private_key, key_id = self.keystore.generate_vm_keys("test-vm")

        self.assertIsNotNone(public_key)
        self.assertIsNotNone(private_key)
        self.assertTrue(key_id.startswith("vm-test-vm-"))
        self.assertGreater(len(public_key), 0)
        self.assertGreater(len(private_key), 0)

    def test_derive_storage_key(self):
        """Test storage key derivation."""
        _, _, key_id = self.keystore.generate_vm_keys("test-vm")
        storage_key = self.keystore.derive_storage_key(key_id)

        self.assertEqual(len(storage_key), 32)  # 256-bit key

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption/decryption round trip."""
        _, _, key_id = self.keystore.generate_vm_keys("test-vm")
        storage_key = self.keystore.derive_storage_key(key_id)

        plaintext = b"QWAMOS Test Data: Lorem ipsum dolor sit amet"

        # Encrypt
        encrypted = self.keystore.encrypt_data(plaintext, storage_key)
        self.assertIn('ciphertext', encrypted)
        self.assertIn('nonce', encrypted)
        self.assertIn('tag', encrypted)

        # Decrypt
        decrypted = self.keystore.decrypt_data(
            encrypted['ciphertext'],
            encrypted['nonce'],
            encrypted['tag'],
            storage_key
        )

        self.assertEqual(plaintext, decrypted)

    def test_tamper_detection(self):
        """Test that tampering is detected."""
        _, _, key_id = self.keystore.generate_vm_keys("test-vm")
        storage_key = self.keystore.derive_storage_key(key_id)

        plaintext = b"QWAMOS Sensitive Data"
        encrypted = self.keystore.encrypt_data(plaintext, storage_key)

        # Tamper with ciphertext
        tampered_ciphertext = bytes([b ^ 1 for b in encrypted['ciphertext']])

        # Should raise ValueError on tampering
        with self.assertRaises(ValueError):
            self.keystore.decrypt_data(
                tampered_ciphertext,
                encrypted['nonce'],
                encrypted['tag'],
                storage_key
            )

    def test_key_rotation(self):
        """Test key rotation."""
        _, _, old_key_id = self.keystore.generate_vm_keys("test-vm")
        new_key_id = self.keystore.rotate_key(old_key_id)

        self.assertNotEqual(old_key_id, new_key_id)
        self.assertTrue(new_key_id.startswith("vm-test-vm-"))

        # Check rotation count
        metadata = self.keystore._load_metadata(new_key_id)
        self.assertEqual(metadata.rotation_count, 1)

    def test_list_keys(self):
        """Test listing keys."""
        self.keystore.generate_vm_keys("vm1")
        self.keystore.generate_vm_keys("vm2")
        self.keystore.generate_vm_keys("vm1")  # Second key for vm1

        all_keys = self.keystore.list_vm_keys()
        self.assertEqual(len(all_keys), 3)

        vm1_keys = self.keystore.list_vm_keys(vm_name="vm1")
        self.assertEqual(len(vm1_keys), 2)

        for key in vm1_keys:
            self.assertEqual(key.vm_name, "vm1")

    def test_delete_key(self):
        """Test key deletion."""
        _, _, key_id = self.keystore.generate_vm_keys("test-vm")

        # Verify key exists
        keys = self.keystore.list_vm_keys()
        self.assertEqual(len(keys), 1)

        # Delete key
        self.keystore.delete_key(key_id)

        # Verify deleted
        keys = self.keystore.list_vm_keys()
        self.assertEqual(len(keys), 0)


class TestPQCVolume(unittest.TestCase):
    """Test cases for PQC Encrypted Volume."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.keystore_dir = os.path.join(self.test_dir, "keystore")
        self.volume_path = os.path.join(self.test_dir, "test_volume.qvol")

        self.keystore = PQCKeystore(keystore_path=self.keystore_dir)
        self.volume = PQCVolume(self.volume_path, keystore=self.keystore)

    def tearDown(self):
        """Clean up test environment."""
        if self.volume.file_handle:
            self.volume.close()
        shutil.rmtree(self.test_dir)

    def test_create_volume(self):
        """Test volume creation."""
        key_id = self.volume.create("test-vol", "test-vm", size_mb=1)

        self.assertIsNotNone(key_id)
        self.assertTrue(Path(self.volume_path).exists())
        self.assertIsNotNone(self.volume.header)
        self.assertEqual(self.volume.header.volume_name, "test-vol")
        self.assertEqual(self.volume.header.vm_name, "test-vm")

    def test_open_volume(self):
        """Test opening existing volume."""
        # Create volume
        key_id = self.volume.create("test-vol", "test-vm", size_mb=1)
        self.volume.close()

        # Open volume
        volume2 = PQCVolume(self.volume_path, keystore=self.keystore)
        volume2.open()

        self.assertEqual(volume2.header.volume_name, "test-vol")
        self.assertEqual(volume2.header.key_id, key_id)

        volume2.close()

    def test_write_read_block(self):
        """Test block write and read."""
        self.volume.create("test-vol", "test-vm", size_mb=1)
        self.volume.open()

        test_data = b"Test block data for QWAMOS encrypted storage"

        # Write block
        self.volume.write_block(0, test_data)

        # Read block
        read_data = self.volume.read_block(0)
        recovered = read_data[:len(test_data)]

        self.assertEqual(test_data, recovered)

    def test_multiple_blocks(self):
        """Test writing and reading multiple blocks."""
        self.volume.create("test-vol", "test-vm", size_mb=1)
        self.volume.open()

        test_blocks = [
            b"Block 0 data",
            b"Block 1 data with more content",
            b"Block 2: Even more test data here",
        ]

        # Write blocks
        for i, data in enumerate(test_blocks):
            self.volume.write_block(i, data)

        # Read and verify all blocks
        for i, expected in enumerate(test_blocks):
            read_data = self.volume.read_block(i)
            recovered = read_data[:len(expected)]
            self.assertEqual(expected, recovered)

    def test_sparse_blocks(self):
        """Test sparse block handling."""
        self.volume.create("test-vol", "test-vm", size_mb=1)
        self.volume.open()

        # Read uninitialized block (should return zeros)
        data = self.volume.read_block(100)
        self.assertEqual(data, b'\x00' * 4096)

        # Zero a block explicitly
        self.volume.zero_block(50)
        data = self.volume.read_block(50)
        self.assertEqual(data, b'\x00' * 4096)

    def test_block_boundary(self):
        """Test handling of block size boundaries."""
        self.volume.create("test-vol", "test-vm", size_mb=1)
        self.volume.open()

        # Test with exactly block size data
        full_block = b"X" * 4096
        self.volume.write_block(0, full_block)
        read_data = self.volume.read_block(0)
        self.assertEqual(full_block, read_data)

    def test_volume_stats(self):
        """Test volume statistics."""
        self.volume.create("test-vol", "test-vm", size_mb=5)
        self.volume.open()

        stats = self.volume.get_stats()

        self.assertEqual(stats['volume_name'], "test-vol")
        self.assertEqual(stats['vm_name'], "test-vm")
        self.assertEqual(stats['logical_size_mb'], 5.0)
        self.assertTrue(stats['encrypted'])
        self.assertIn('actual_size_mb', stats)

    def test_encryption_persistence(self):
        """Test that data remains encrypted on disk."""
        self.volume.create("test-vol", "test-vm", size_mb=1)
        self.volume.open()

        plaintext = b"Sensitive data that should be encrypted"
        self.volume.write_block(0, plaintext)
        self.volume.close()

        # Read raw file data (should be encrypted)
        with open(self.volume_path, 'rb') as f:
            raw_data = f.read()

        # Plaintext should NOT appear in raw data
        self.assertNotIn(plaintext, raw_data)


class TestEndToEndWorkflow(unittest.TestCase):
    """Integration tests for complete PQC storage workflow."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.keystore_dir = os.path.join(self.test_dir, "keystore")
        self.keystore = PQCKeystore(keystore_path=self.keystore_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def test_multi_vm_isolation(self):
        """Test that multiple VMs have isolated encryption."""
        # Create volumes for two different VMs
        vol1_path = os.path.join(self.test_dir, "vm1.qvol")
        vol2_path = os.path.join(self.test_dir, "vm2.qvol")

        vol1 = PQCVolume(vol1_path, keystore=self.keystore)
        vol2 = PQCVolume(vol2_path, keystore=self.keystore)

        key1 = vol1.create("vol1", "vm1", size_mb=1)
        key2 = vol2.create("vol2", "vm2", size_mb=1)

        # Keys should be different
        self.assertNotEqual(key1, key2)

        # Write different data to each
        vol1.open()
        vol2.open()

        vol1.write_block(0, b"VM1 private data")
        vol2.write_block(0, b"VM2 private data")

        # Read back
        data1 = vol1.read_block(0)[:16]
        data2 = vol2.read_block(0)[:16]

        self.assertEqual(data1, b"VM1 private data")
        self.assertEqual(data2, b"VM2 private data")

        vol1.close()
        vol2.close()

    def test_key_rotation_workflow(self):
        """Test complete key rotation workflow."""
        vol_path = os.path.join(self.test_dir, "test.qvol")
        volume = PQCVolume(vol_path, keystore=self.keystore)

        # Create volume with original key
        old_key_id = volume.create("test-vol", "test-vm", size_mb=1)
        volume.open()

        # Write data
        original_data = b"Data encrypted with original key"
        volume.write_block(0, original_data)
        volume.close()

        # Rotate key
        new_key_id = self.keystore.rotate_key(old_key_id)
        self.assertNotEqual(old_key_id, new_key_id)

        # Note: In production, you would re-encrypt all blocks with new key
        # For this test, we just verify the key rotation mechanism works

        # Verify new key can be used
        new_storage_key = self.keystore.derive_storage_key(new_key_id)
        self.assertEqual(len(new_storage_key), 32)


def run_tests():
    """Run all tests with detailed output."""
    print("=" * 70)
    print("Phase XIII: PQC Storage Subsystem - Unit Tests")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPQCKeystore))
    suite.addTests(loader.loadTestsFromTestCase(TestPQCVolume))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndWorkflow))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
