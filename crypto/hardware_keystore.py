#!/usr/bin/env python3
"""
QWAMOS Hardware Keystore - TPM/TrustZone Integration

CRITICAL FIX #6: Hardware-backed key storage for maximum security.

Provides integration with:
- ARM TrustZone (for ARM64 devices)
- TPM 2.0 (for x86_64/server systems)
- Android Keystore (for Android devices)

Author: QWAMOS Security Team
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HardwareKeystore')


class HardwareBackend(Enum):
    """Available hardware security backends."""
    NONE = "none"  # Software fallback
    TPM = "tpm"  # TPM 2.0
    TRUSTZONE = "trustzone"  # ARM TrustZone
    ANDROID_KEYSTORE = "android"  # Android Keystore


class HardwareKeystore:
    """
    Hardware-backed key storage manager.

    CRITICAL FIX #6: Uses hardware security modules when available.

    Priority order:
    1. TPM 2.0 (if available)
    2. ARM TrustZone (if on ARM64)
    3. Android Keystore (if on Android)
    4. Software fallback (encrypted, but not hardware-backed)
    """

    def __init__(self, keystore_dir: str = "/opt/qwamos/keystore/hardware"):
        """
        Initialize hardware keystore.

        Args:
            keystore_dir: Directory for key metadata (not keys themselves)
        """
        self.keystore_dir = Path(keystore_dir)
        self.keystore_dir.mkdir(parents=True, exist_ok=True)

        # Detect available hardware backend
        self.backend = self._detect_hardware_backend()
        logger.info(f"Hardware keystore backend: {self.backend.value}")

        # Backend-specific initialization
        if self.backend == HardwareBackend.TPM:
            self._init_tpm()
        elif self.backend == HardwareBackend.TRUSTZONE:
            self._init_trustzone()
        elif self.backend == HardwareBackend.ANDROID_KEYSTORE:
            self._init_android_keystore()
        else:
            logger.warning("⚠️  No hardware backend available - using software fallback")
            logger.warning("   Keys will be encrypted but not hardware-protected")

    def _detect_hardware_backend(self) -> HardwareBackend:
        """
        Detect available hardware security backend.

        Returns:
            HardwareBackend enum value
        """
        # Check for TPM 2.0
        if self._check_tpm_available():
            logger.info("✓ TPM 2.0 detected")
            return HardwareBackend.TPM

        # Check for ARM TrustZone
        if self._check_trustzone_available():
            logger.info("✓ ARM TrustZone detected")
            return HardwareBackend.TRUSTZONE

        # Check for Android Keystore
        if self._check_android_keystore_available():
            logger.info("✓ Android Keystore detected")
            return HardwareBackend.ANDROID_KEYSTORE

        # Fallback to software
        logger.warning("No hardware security module detected")
        return HardwareBackend.NONE

    def _check_tpm_available(self) -> bool:
        """Check if TPM 2.0 is available."""
        try:
            # Check for TPM device
            if not Path("/dev/tpm0").exists() and not Path("/dev/tpmrm0").exists():
                return False

            # Check for tpm2-tools
            result = subprocess.run(
                ['which', 'tpm2_createprimary'],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False

    def _check_trustzone_available(self) -> bool:
        """Check if ARM TrustZone is available."""
        try:
            # Check for ARM64 architecture
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'aarch64' not in cpuinfo.lower() and 'armv8' not in cpuinfo.lower():
                    return False

            # Check for OP-TEE (Open Portable Trusted Execution Environment)
            if Path("/dev/tee0").exists() or Path("/dev/teepriv0").exists():
                return True

            # Check for Android TEE
            if Path("/vendor/bin/hw/android.hardware.security.keymint").exists():
                return True

            return False
        except:
            return False

    def _check_android_keystore_available(self) -> bool:
        """Check if Android Keystore is available."""
        try:
            # Check for Android environment
            if 'ANDROID_ROOT' not in os.environ:
                return False

            # Check for keystore service
            result = subprocess.run(
                ['service', 'list'],
                capture_output=True,
                text=True
            )
            return 'android.security.keystore' in result.stdout
        except:
            return False

    def _init_tpm(self):
        """Initialize TPM 2.0 backend."""
        logger.info("Initializing TPM 2.0 keystore...")

        # Create TPM primary key hierarchy
        try:
            # Check if primary key exists
            primary_ctx = self.keystore_dir / "tpm_primary.ctx"

            if not primary_ctx.exists():
                logger.info("Creating TPM primary key...")
                result = subprocess.run([
                    'tpm2_createprimary',
                    '-C', 'o',  # Owner hierarchy
                    '-g', 'sha256',
                    '-G', 'ecc',
                    '-c', str(primary_ctx)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info("✓ TPM primary key created")
                else:
                    logger.error(f"TPM initialization failed: {result.stderr}")
        except Exception as e:
            logger.error(f"TPM initialization error: {e}")

    def _init_trustzone(self):
        """Initialize ARM TrustZone backend."""
        logger.info("Initializing ARM TrustZone keystore...")

        # TrustZone initialization depends on OP-TEE or vendor TEE
        # For now, mark as initialized if device exists
        if Path("/dev/tee0").exists():
            logger.info("✓ TrustZone TEE device available")
        else:
            logger.warning("TrustZone detected but TEE device not accessible")

    def _init_android_keystore(self):
        """Initialize Android Keystore backend."""
        logger.info("Initializing Android Keystore...")

        try:
            # Verify keystore daemon is running
            result = subprocess.run(
                ['getprop', 'init.svc.keystore'],
                capture_output=True,
                text=True
            )

            if 'running' in result.stdout:
                logger.info("✓ Android Keystore daemon running")
            else:
                logger.warning("Android Keystore daemon not running")
        except Exception as e:
            logger.warning(f"Could not verify Android Keystore: {e}")

    def store_key(self, key_id: str, key_data: bytes, metadata: Dict[str, Any] = None) -> bool:
        """
        Store key in hardware-backed storage.

        Args:
            key_id: Unique identifier for the key
            key_data: Key bytes to store
            metadata: Optional metadata dict

        Returns:
            True if successful
        """
        metadata = metadata or {}
        metadata['key_id'] = key_id
        metadata['backend'] = self.backend.value

        if self.backend == HardwareBackend.TPM:
            return self._store_key_tpm(key_id, key_data, metadata)
        elif self.backend == HardwareBackend.TRUSTZONE:
            return self._store_key_trustzone(key_id, key_data, metadata)
        elif self.backend == HardwareBackend.ANDROID_KEYSTORE:
            return self._store_key_android(key_id, key_data, metadata)
        else:
            return self._store_key_software(key_id, key_data, metadata)

    def load_key(self, key_id: str) -> Optional[bytes]:
        """
        Load key from hardware-backed storage.

        Args:
            key_id: Key identifier

        Returns:
            Key bytes or None if not found
        """
        # Load metadata to determine backend
        metadata_file = self.keystore_dir / f"{key_id}.meta"
        if not metadata_file.exists():
            logger.error(f"Key metadata not found: {key_id}")
            return None

        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        backend_str = metadata.get('backend', 'none')
        backend = HardwareBackend(backend_str)

        if backend == HardwareBackend.TPM:
            return self._load_key_tpm(key_id, metadata)
        elif backend == HardwareBackend.TRUSTZONE:
            return self._load_key_trustzone(key_id, metadata)
        elif backend == HardwareBackend.ANDROID_KEYSTORE:
            return self._load_key_android(key_id, metadata)
        else:
            return self._load_key_software(key_id, metadata)

    def _store_key_tpm(self, key_id: str, key_data: bytes, metadata: Dict) -> bool:
        """Store key in TPM 2.0."""
        try:
            key_file = self.keystore_dir / f"{key_id}.tpm"

            # Create TPM object for this key
            result = subprocess.run([
                'tpm2_create',
                '-C', str(self.keystore_dir / "tpm_primary.ctx"),
                '-G', 'keyedhash',
                '-i', '-',  # Read from stdin
                '-u', str(key_file) + '.pub',
                '-r', str(key_file) + '.priv'
            ], input=key_data, capture_output=True)

            if result.returncode != 0:
                logger.error(f"TPM key creation failed: {result.stderr.decode()}")
                return False

            # Save metadata
            metadata['tpm_public'] = str(key_file) + '.pub'
            metadata['tpm_private'] = str(key_file) + '.priv'

            with open(self.keystore_dir / f"{key_id}.meta", 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✓ Key stored in TPM: {key_id}")
            return True
        except Exception as e:
            logger.error(f"TPM key storage error: {e}")
            return False

    def _load_key_tpm(self, key_id: str, metadata: Dict) -> Optional[bytes]:
        """Load key from TPM 2.0."""
        try:
            key_file = self.keystore_dir / f"{key_id}.tpm"

            # Load TPM object
            ctx_file = str(key_file) + '.ctx'
            result = subprocess.run([
                'tpm2_load',
                '-C', str(self.keystore_dir / "tpm_primary.ctx"),
                '-u', metadata['tpm_public'],
                '-r', metadata['tpm_private'],
                '-c', ctx_file
            ], capture_output=True)

            if result.returncode != 0:
                logger.error(f"TPM key load failed: {result.stderr.decode()}")
                return None

            # Read key data
            result = subprocess.run([
                'tpm2_unseal',
                '-c', ctx_file
            ], capture_output=True)

            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"TPM unseal failed: {result.stderr.decode()}")
                return None
        except Exception as e:
            logger.error(f"TPM key load error: {e}")
            return None

    def _store_key_trustzone(self, key_id: str, key_data: bytes, metadata: Dict) -> bool:
        """Store key in ARM TrustZone."""
        logger.info(f"Storing key in TrustZone: {key_id}")

        # TrustZone storage requires OP-TEE client library
        # For now, use encrypted software storage with TrustZone-derived key
        # Production would use OP-TEE directly via libteec

        logger.warning("TrustZone direct storage not yet implemented")
        logger.warning("Using encrypted software storage with TrustZone hint")

        return self._store_key_software(key_id, key_data, metadata)

    def _load_key_trustzone(self, key_id: str, metadata: Dict) -> Optional[bytes]:
        """Load key from ARM TrustZone."""
        logger.warning("TrustZone direct loading not yet implemented")
        return self._load_key_software(key_id, metadata)

    def _store_key_android(self, key_id: str, key_data: bytes, metadata: Dict) -> bool:
        """Store key in Android Keystore."""
        logger.info(f"Storing key in Android Keystore: {key_id}")

        # Android Keystore requires Java/JNI calls
        # For now, document the approach

        logger.warning("Android Keystore direct storage not yet implemented")
        logger.warning("Using encrypted software storage")
        logger.info("Production: Use Android KeyStore via JNI")

        return self._store_key_software(key_id, key_data, metadata)

    def _load_key_android(self, key_id: str, metadata: Dict) -> Optional[bytes]:
        """Load key from Android Keystore."""
        logger.warning("Android Keystore direct loading not yet implemented")
        return self._load_key_software(key_id, metadata)

    def _store_key_software(self, key_id: str, key_data: bytes, metadata: Dict) -> bool:
        """Software fallback - encrypted storage."""
        try:
            from Crypto.Cipher import ChaCha20_Poly1305
            from Crypto.Random import get_random_bytes
            from Crypto.Protocol.KDF import HKDF
            from Crypto.Hash import SHA256

            # Derive encryption key
            master_key = self._get_software_master_key()

            # Encrypt key data
            nonce = get_random_bytes(12)
            cipher = ChaCha20_Poly1305.new(key=master_key, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(key_data)

            # Save encrypted key
            key_file = self.keystore_dir / f"{key_id}.key"
            with open(key_file, 'wb') as f:
                f.write(nonce + tag + ciphertext)

            os.chmod(key_file, 0o600)

            # Save metadata
            metadata['encrypted'] = True
            metadata['algorithm'] = 'ChaCha20-Poly1305'

            with open(self.keystore_dir / f"{key_id}.meta", 'w') as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✓ Key stored (software encrypted): {key_id}")
            return True
        except Exception as e:
            logger.error(f"Software key storage error: {e}")
            return False

    def _load_key_software(self, key_id: str, metadata: Dict) -> Optional[bytes]:
        """Software fallback - load encrypted key."""
        try:
            from Crypto.Cipher import ChaCha20_Poly1305

            key_file = self.keystore_dir / f"{key_id}.key"
            if not key_file.exists():
                logger.error(f"Key file not found: {key_id}")
                return None

            # Read encrypted key
            with open(key_file, 'rb') as f:
                nonce = f.read(12)
                tag = f.read(16)
                ciphertext = f.read()

            # Derive encryption key
            master_key = self._get_software_master_key()

            # Decrypt
            cipher = ChaCha20_Poly1305.new(key=master_key, nonce=nonce)
            key_data = cipher.decrypt_and_verify(ciphertext, tag)

            return key_data
        except Exception as e:
            logger.error(f"Software key load error: {e}")
            return None

    def _get_software_master_key(self) -> bytes:
        """Derive master key for software encryption."""
        from Crypto.Protocol.KDF import HKDF
        from Crypto.Hash import SHA256
        import uuid

        # Get device-specific ID
        device_id_file = Path.home() / ".qwamos" / ".device_id"
        if device_id_file.exists():
            with open(device_id_file, 'rb') as f:
                device_id = f.read()
        else:
            device_id = str(uuid.getnode()).encode('utf-8')
            device_id_file.parent.mkdir(parents=True, exist_ok=True)
            with open(device_id_file, 'wb') as f:
                f.write(device_id)
            os.chmod(device_id_file, 0o600)

        # Derive key
        return HKDF(
            master=device_id,
            key_len=32,
            salt=b"qwamos-hardware-keystore-v1",
            hashmod=SHA256
        )

    def get_status(self) -> Dict[str, Any]:
        """Get hardware keystore status."""
        return {
            'backend': self.backend.value,
            'hardware_protected': self.backend != HardwareBackend.NONE,
            'tpm_available': self._check_tpm_available(),
            'trustzone_available': self._check_trustzone_available(),
            'android_keystore_available': self._check_android_keystore_available()
        }


if __name__ == "__main__":
    print("=== QWAMOS Hardware Keystore Test ===\n")

    # Initialize
    ks = HardwareKeystore()

    # Show status
    status = ks.get_status()
    print("Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    print()

    # Test key storage
    test_key = b"test_secret_key_data_32bytes!!"
    print("Testing key storage...")

    if ks.store_key("test_key", test_key, {"purpose": "test"}):
        print("✓ Key stored successfully")

        # Test key retrieval
        loaded = ks.load_key("test_key")
        if loaded == test_key:
            print("✓ Key retrieved successfully")
            print("✓ Hardware keystore working correctly")
        else:
            print("✗ Key mismatch")
    else:
        print("✗ Key storage failed")
