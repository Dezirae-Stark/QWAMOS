#!/usr/bin/env python3
"""
QWAMOS Differential Testing - Cryptographic Stress Workload
Phase XII: KVM vs QEMU Comparison

PQC operations: Kyber keygen, ChaCha20 encryption, BLAKE3 hashing
Author: QWAMOS Project
License: AGPL-3.0
"""

import os
import sys
import time
import json
import hashlib
from typing import Dict, List, Tuple
from datetime import datetime


class CryptoStressWorkload:
    """Cryptographic workload testing PQC and symmetric operations."""

    def __init__(self, iterations: int = 100):
        """
        Initialize crypto stress test.

        Args:
            iterations: Number of crypto operation iterations
        """
        self.iterations = iterations
        self.results = {
            "workload": "crypto_stress",
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "iterations": iterations
            },
            "metrics": {},
            "errors": []
        }

    def simulate_kyber_keygen(self) -> Tuple[bytes, bytes]:
        """
        Simulate Kyber-1024 keypair generation.

        Note: This is a simulation using hash-based key derivation.
        Production QWAMOS uses actual Kyber implementation.

        Returns:
            (public_key, secret_key)
        """
        # Simulate Kyber-1024 parameters
        # Real Kyber public key: 1568 bytes, secret key: 3168 bytes
        seed = os.urandom(32)

        # Derive keys using hash expansion (simulating matrix operations)
        pk_seed = hashlib.sha3_512(b"kyber_pk" + seed).digest()
        sk_seed = hashlib.sha3_512(b"kyber_sk" + seed).digest()

        # Expand to full key sizes
        public_key = pk_seed * (1568 // 64 + 1)[:1568]
        secret_key = sk_seed * (3168 // 64 + 1)[:3168]

        return public_key, secret_key

    def simulate_chacha20_poly1305(self, data: bytes, key: bytes, nonce: bytes) -> bytes:
        """
        Simulate ChaCha20-Poly1305 AEAD encryption.

        Note: This uses AES as fallback for simulation.
        Production QWAMOS uses actual ChaCha20-Poly1305.

        Args:
            data: Plaintext data
            key: 256-bit key
            nonce: 96-bit nonce

        Returns:
            Ciphertext (with MAC)
        """
        try:
            from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
            cipher = ChaCha20Poly1305(key[:32])
            ciphertext = cipher.encrypt(nonce[:12], data, None)
            return ciphertext
        except ImportError:
            # Fallback: Use hash-based stream cipher simulation
            stream = hashlib.sha3_512(key + nonce + data).digest()
            # Simple XOR "encryption" for simulation
            ciphertext = bytes(a ^ b for a, b in zip(data, stream * (len(data) // 64 + 1)))
            # Append simulated MAC
            mac = hashlib.sha256(ciphertext + key).digest()[:16]
            return ciphertext + mac

    def test_kyber_keygen(self) -> Dict:
        """Test Kyber keypair generation performance."""
        print(f"   Testing Kyber-1024 keygen ({self.iterations} iterations)...", end=" ", flush=True)

        start = time.time()
        keys_generated = 0
        total_pk_bytes = 0
        total_sk_bytes = 0

        try:
            for _ in range(self.iterations):
                pk, sk = self.simulate_kyber_keygen()
                keys_generated += 1
                total_pk_bytes += len(pk)
                total_sk_bytes += len(sk)

            duration = time.time() - start
            keys_per_sec = keys_generated / duration

            print(f"{duration:.3f}s ({keys_per_sec:.2f} keypairs/sec)")

            return {
                "test": "kyber_keygen",
                "duration_sec": round(duration, 3),
                "iterations": self.iterations,
                "keys_per_sec": round(keys_per_sec, 2),
                "avg_pk_size_bytes": total_pk_bytes // keys_generated,
                "avg_sk_size_bytes": total_sk_bytes // keys_generated
            }

        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "kyber_keygen", "error": str(e)})
            return {
                "test": "kyber_keygen",
                "error": str(e)
            }

    def test_chacha20_encryption(self, data_size_kb: int = 1024) -> Dict:
        """Test ChaCha20-Poly1305 encryption performance."""
        print(f"   Testing ChaCha20-Poly1305 encryption ({self.iterations} × {data_size_kb} KB)...", end=" ", flush=True)

        data_size_bytes = data_size_kb * 1024
        total_bytes_encrypted = 0

        try:
            # Generate key and nonce once
            key = os.urandom(32)
            nonce = os.urandom(12)

            start = time.time()

            for _ in range(self.iterations):
                plaintext = os.urandom(data_size_bytes)
                ciphertext = self.simulate_chacha20_poly1305(plaintext, key, nonce)
                total_bytes_encrypted += len(plaintext)

            duration = time.time() - start
            throughput_mb_per_sec = (total_bytes_encrypted / (1024 * 1024)) / duration

            print(f"{duration:.3f}s ({throughput_mb_per_sec:.2f} MB/s)")

            return {
                "test": "chacha20_encryption",
                "duration_sec": round(duration, 3),
                "iterations": self.iterations,
                "data_size_kb": data_size_kb,
                "total_mb_encrypted": round(total_bytes_encrypted / (1024 * 1024), 2),
                "throughput_mb_per_sec": round(throughput_mb_per_sec, 2)
            }

        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "chacha20_encryption", "error": str(e)})
            return {
                "test": "chacha20_encryption",
                "error": str(e)
            }

    def test_blake3_hashing(self, data_size_mb: int = 10) -> Dict:
        """Test BLAKE3 hashing performance (fallback to BLAKE2b)."""
        print(f"   Testing BLAKE3 hashing ({data_size_mb} MB)...", end=" ", flush=True)

        data_size_bytes = data_size_mb * 1024 * 1024

        try:
            # Generate test data
            data = os.urandom(data_size_bytes)

            start = time.time()

            # BLAKE2b as BLAKE3 fallback
            hash_obj = hashlib.blake2b(data)
            digest = hash_obj.hexdigest()

            duration = time.time() - start
            throughput_mb_per_sec = data_size_mb / duration

            print(f"{duration:.3f}s ({throughput_mb_per_sec:.2f} MB/s)")

            return {
                "test": "blake3_hashing",
                "duration_sec": round(duration, 3),
                "data_size_mb": data_size_mb,
                "throughput_mb_per_sec": round(throughput_mb_per_sec, 2),
                "digest_length_bytes": len(digest) // 2  # hex to bytes
            }

        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "blake3_hashing", "error": str(e)})
            return {
                "test": "blake3_hashing",
                "error": str(e)
            }

    def test_sha3_hashing(self, data_size_mb: int = 10) -> Dict:
        """Test SHA3-512 hashing performance."""
        print(f"   Testing SHA3-512 hashing ({data_size_mb} MB)...", end=" ", flush=True)

        data_size_bytes = data_size_mb * 1024 * 1024

        try:
            # Generate test data
            data = os.urandom(data_size_bytes)

            start = time.time()

            hash_obj = hashlib.sha3_512(data)
            digest = hash_obj.hexdigest()

            duration = time.time() - start
            throughput_mb_per_sec = data_size_mb / duration

            print(f"{duration:.3f}s ({throughput_mb_per_sec:.2f} MB/s)")

            return {
                "test": "sha3_hashing",
                "duration_sec": round(duration, 3),
                "data_size_mb": data_size_mb,
                "throughput_mb_per_sec": round(throughput_mb_per_sec, 2),
                "digest_length_bytes": len(digest) // 2
            }

        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "sha3_hashing", "error": str(e)})
            return {
                "test": "sha3_hashing",
                "error": str(e)
            }

    def test_mixed_crypto_workload(self) -> Dict:
        """Test mixed cryptographic workload."""
        print(f"   Testing mixed crypto workload ({self.iterations} cycles)...", end=" ", flush=True)

        try:
            start = time.time()

            operations = 0
            for _ in range(self.iterations):
                # Generate Kyber keypair
                pk, sk = self.simulate_kyber_keygen()
                operations += 1

                # Encrypt data with ChaCha20
                data = os.urandom(4096)
                key = os.urandom(32)
                nonce = os.urandom(12)
                ciphertext = self.simulate_chacha20_poly1305(data, key, nonce)
                operations += 1

                # Hash the ciphertext
                digest = hashlib.blake2b(ciphertext).digest()
                operations += 1

            duration = time.time() - start
            ops_per_sec = operations / duration

            print(f"{duration:.3f}s ({ops_per_sec:.2f} ops/sec)")

            return {
                "test": "mixed_crypto_workload",
                "duration_sec": round(duration, 3),
                "cycles": self.iterations,
                "total_operations": operations,
                "ops_per_sec": round(ops_per_sec, 2)
            }

        except Exception as e:
            print(f"❌ {e}")
            self.results["errors"].append({"test": "mixed_crypto_workload", "error": str(e)})
            return {
                "test": "mixed_crypto_workload",
                "error": str(e)
            }

    def run(self) -> Dict:
        """
        Execute crypto stress test.

        Returns:
            Results dictionary
        """
        print(f"🔐 Crypto Stress Test - {self.iterations} iterations")

        overall_start = time.time()
        test_results = []

        # Run all crypto tests
        test_results.append(self.test_kyber_keygen())
        test_results.append(self.test_chacha20_encryption(data_size_kb=1024))
        test_results.append(self.test_blake3_hashing(data_size_mb=10))
        test_results.append(self.test_sha3_hashing(data_size_mb=10))
        test_results.append(self.test_mixed_crypto_workload())

        overall_duration = time.time() - overall_start

        # Calculate aggregate metrics
        self.results["metrics"] = {
            "total_duration_sec": round(overall_duration, 3),
            "tests_completed": len([t for t in test_results if "error" not in t]),
            "tests_failed": len([t for t in test_results if "error" in t]),
            "test_details": test_results
        }

        # Print summary
        print(f"   ✅ Completed in {overall_duration:.3f}s")
        print(f"   Tests passed: {self.results['metrics']['tests_completed']}/{len(test_results)}")

        if self.results["metrics"]["tests_failed"] > 0:
            print(f"   ⚠️  Tests failed: {self.results['metrics']['tests_failed']}")

        return self.results

    def save_results(self, output_path: str):
        """Save results to JSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="QWAMOS Crypto Stress Workload")
    parser.add_argument('--iterations', type=int, default=100, help='Number of iterations')
    parser.add_argument('--output', type=str, default='crypt_stress_results.json', help='Output file')
    args = parser.parse_args()

    workload = CryptoStressWorkload(iterations=args.iterations)
    results = workload.run()
    workload.save_results(args.output)

    print(f"\n✅ Results saved to: {args.output}")

    # Return non-zero exit code if errors occurred
    sys.exit(1 if results["metrics"]["tests_failed"] > 0 else 0)


if __name__ == "__main__":
    main()
