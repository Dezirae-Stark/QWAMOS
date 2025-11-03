#!/usr/bin/env python3
"""
QWAMOS Argon2id Key Derivation Function
Post-Quantum resistant memory-hard KDF for Phase 4

Argon2id is the recommended variant (hybrid of Argon2i and Argon2d):
- Argon2i: Data-independent memory access (side-channel resistant)
- Argon2d: Data-dependent memory access (GPU/ASIC resistant)
- Argon2id: Best of both worlds (first half Argon2i, second half Argon2d)
"""

import sys
from typing import Tuple

try:
    from argon2 import PasswordHasher, low_level
    from argon2.low_level import Type
except ImportError:
    print("[!] Error: argon2-cffi not installed")
    print("    Run: pip install argon2-cffi")
    sys.exit(1)

# Security levels for different use cases
SECURITY_PROFILES = {
    'low': {
        'memory_mb': 256,
        'time_cost': 3,
        'parallelism': 4,
        'description': 'Fast unlock (~0.5s), suitable for testing'
    },
    'medium': {
        'memory_mb': 512,
        'time_cost': 5,
        'parallelism': 4,
        'description': 'Balanced security (~1.5s), recommended for most users'
    },
    'high': {
        'memory_mb': 1024,
        'time_cost': 10,
        'parallelism': 4,
        'description': 'Strong security (~3s), recommended for QWAMOS'
    },
    'paranoid': {
        'memory_mb': 2048,
        'time_cost': 20,
        'parallelism': 4,
        'description': 'Maximum security (~8s), for AEGIS Vault'
    }
}

class Argon2KDF:
    """
    Argon2id Key Derivation Function for QWAMOS Phase 4

    Provides memory-hard password-based key derivation using Argon2id,
    which is resistant to:
    - GPU/FPGA/ASIC attacks (memory-hard)
    - Side-channel attacks (first half is data-independent)
    - Quantum computing attacks (Grover's algorithm doesn't help much)
    """

    def __init__(self, profile='high'):
        """
        Initialize Argon2 KDF with security profile

        Args:
            profile: Security level ('low', 'medium', 'high', 'paranoid')
        """
        if profile not in SECURITY_PROFILES:
            raise ValueError(f"Invalid profile. Choose from: {list(SECURITY_PROFILES.keys())}")

        self.profile = SECURITY_PROFILES[profile]
        self.memory_cost = self.profile['memory_mb'] * 1024  # Convert to KiB
        self.time_cost = self.profile['time_cost']
        self.parallelism = self.profile['parallelism']

    def derive_key(self, password: str, salt: bytes,
                   output_length: int = 32) -> bytes:
        """
        Derive encryption key from password using Argon2id

        Args:
            password: User password (UTF-8 string)
            salt: Random salt (recommend 16-64 bytes)
            output_length: Desired key length in bytes (default: 32 for 256-bit)

        Returns:
            Derived key (bytes)

        Example:
            >>> kdf = Argon2KDF(profile='high')
            >>> salt = os.urandom(16)
            >>> key = kdf.derive_key("MySecurePassword", salt, 32)
            >>> len(key)
            32
        """
        if not isinstance(password, str):
            raise TypeError("Password must be a string")
        if not isinstance(salt, bytes):
            raise TypeError("Salt must be bytes")
        if len(salt) < 8:
            raise ValueError("Salt must be at least 8 bytes")

        # Derive key using Argon2id
        derived = low_level.hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=output_length,
            type=Type.ID  # Argon2id (hybrid mode)
        )

        return derived

    def derive_key_with_pim(self, password: str, salt: bytes,
                            pim: int, output_length: int = 32) -> bytes:
        """
        Derive key with Personal Iterations Multiplier (PIM)

        PIM allows users to increase security by multiplying the time cost.
        Similar to VeraCrypt's PIM feature.

        Args:
            password: User password
            salt: Random salt
            pim: Personal Iterations Multiplier (1-10 recommended)
            output_length: Key length in bytes

        Returns:
            Derived key

        Example:
            >>> kdf = Argon2KDF(profile='high')
            >>> key = kdf.derive_key_with_pim("password", salt, pim=2)
            # This will take 2x longer than normal
        """
        if pim < 1:
            raise ValueError("PIM must be >= 1")
        if pim > 20:
            print(f"[!] Warning: PIM={pim} will result in very long unlock times")

        # Multiply time cost by PIM
        time_cost = self.time_cost * pim

        derived = low_level.hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=output_length,
            type=Type.ID
        )

        return derived

    def get_parameters(self) -> dict:
        """
        Get current Argon2 parameters

        Returns:
            Dictionary with memory_cost (KiB), time_cost, parallelism
        """
        return {
            'memory_cost_kib': self.memory_cost,
            'memory_cost_mb': self.memory_cost // 1024,
            'time_cost': self.time_cost,
            'parallelism': self.parallelism,
            'profile': self.profile
        }

    @staticmethod
    def estimate_time(profile='high') -> str:
        """
        Estimate unlock time for a given profile

        Args:
            profile: Security level

        Returns:
            Estimated time as string
        """
        if profile not in SECURITY_PROFILES:
            return "Unknown profile"

        # Rough estimates based on ARM Cortex-A57
        estimates = {
            'low': '~0.5 seconds',
            'medium': '~1.5 seconds',
            'high': '~3 seconds',
            'paranoid': '~8 seconds'
        }

        return estimates[profile]

def benchmark_argon2(profiles=['low', 'medium', 'high'], iterations=3):
    """
    Benchmark Argon2id performance on current hardware

    Args:
        profiles: List of profiles to test
        iterations: Number of iterations per profile

    Example:
        >>> benchmark_argon2(['medium', 'high'])
        Profile: medium (512 MB, t=5)
          Run 1: 1.42s
          Run 2: 1.45s
          Run 3: 1.43s
          Average: 1.43s
    """
    import os
    import time

    print("[*] Benchmarking Argon2id performance...")
    print(f"[*] Running {iterations} iterations per profile\n")

    password = "BenchmarkPassword123!"
    salt = os.urandom(16)

    results = {}

    for profile in profiles:
        print(f"Profile: {profile} ({SECURITY_PROFILES[profile]['memory_mb']} MB, "
              f"t={SECURITY_PROFILES[profile]['time_cost']})")

        kdf = Argon2KDF(profile=profile)
        times = []

        for i in range(iterations):
            start = time.time()
            key = kdf.derive_key(password, salt)
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"  Run {i+1}: {elapsed:.2f}s")

        avg_time = sum(times) / len(times)
        results[profile] = avg_time
        print(f"  Average: {avg_time:.2f}s\n")

    return results

# Example usage
if __name__ == "__main__":
    import os

    print("=" * 60)
    print("QWAMOS Argon2id KDF - Phase 4")
    print("=" * 60)

    # Show available profiles
    print("\n[*] Available Security Profiles:")
    for name, params in SECURITY_PROFILES.items():
        print(f"  {name:10s}: {params['memory_mb']:4d} MB, "
              f"t={params['time_cost']:2d}, "
              f"unlock ~{Argon2KDF.estimate_time(name)}")

    # Example: Derive key with 'high' profile
    print("\n[*] Example: Deriving 256-bit key with 'high' profile...")

    kdf = Argon2KDF(profile='high')
    password = "MySecurePassword123!"
    salt = os.urandom(16)

    print(f"[*] Password: {password}")
    print(f"[*] Salt: {salt.hex()[:32]}...")
    print(f"[*] Parameters: {kdf.get_parameters()}")

    import time
    start = time.time()
    key = kdf.derive_key(password, salt, output_length=32)
    elapsed = time.time() - start

    print(f"\n[+] Key derived successfully!")
    print(f"[+] Key (hex): {key.hex()}")
    print(f"[+] Key length: {len(key)} bytes")
    print(f"[+] Time taken: {elapsed:.2f} seconds")

    # Verify determinism
    print("\n[*] Verifying determinism (same password + salt → same key)...")
    key2 = kdf.derive_key(password, salt, output_length=32)
    if key == key2:
        print("[+] ✓ Determinism verified: Keys match")
    else:
        print("[!] ✗ ERROR: Keys don't match!")

    # Test with different salt
    print("\n[*] Testing with different salt...")
    salt2 = os.urandom(16)
    key3 = kdf.derive_key(password, salt2, output_length=32)
    if key != key3:
        print("[+] ✓ Different salt produces different key")
    else:
        print("[!] ✗ ERROR: Same key with different salt!")

    # Run quick benchmark
    print("\n[*] Running performance benchmark...")
    benchmark_argon2(profiles=['medium', 'high'], iterations=2)

    print("\n" + "=" * 60)
    print("Argon2id KDF initialization complete!")
    print("=" * 60)
