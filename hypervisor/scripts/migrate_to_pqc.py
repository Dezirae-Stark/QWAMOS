#!/usr/bin/env python3
"""
QWAMOS VM Storage Migration Tool
Phase XIII: Migrate existing VMs to PQC encrypted storage

Converts unencrypted QCOW2 disk images to encrypted PQC volumes.

Usage:
    python migrate_to_pqc.py <vm_name> [--backup]

Author: QWAMOS Project
License: MIT
"""

import os
import sys
import yaml
import argparse
import subprocess
import shutil
from pathlib import Path

# Add modules to path
QWAMOS_ROOT = Path.home() / "QWAMOS"
sys.path.insert(0, str(QWAMOS_ROOT / "crypto"))
sys.path.insert(0, str(QWAMOS_ROOT / "storage"))

from pqc_keystore import PQCKeystore
from pqc_volume import PQCVolume

VMS_DIR = QWAMOS_ROOT / "vms"


class VMStorageMigrator:
    """Migrates VM storage to encrypted PQC volumes."""

    def __init__(self, vm_name, backup=True):
        self.vm_name = vm_name
        self.vm_dir = VMS_DIR / vm_name
        self.config_file = self.vm_dir / "config.yaml"
        self.backup_enabled = backup

        # Initialize PQC storage
        self.keystore = PQCKeystore()

        # Load VM config
        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def migrate(self):
        """Perform migration from QCOW2 to PQC volume."""
        print("=" * 70)
        print(f"QWAMOS Storage Migration: {self.vm_name}")
        print("=" * 70)
        print()

        # Get current disk info
        disk_config = self.config['hardware']['disk']['primary']
        old_disk_path = Path(disk_config['path'])
        disk_size = disk_config['size']

        # Check if already encrypted
        if old_disk_path.suffix == '.qvol':
            print(f"✅ VM '{self.vm_name}' is already using encrypted storage")
            print(f"   Disk: {old_disk_path}")
            return

        # Check if disk exists
        if not old_disk_path.exists():
            print(f"⚠️  Warning: Disk file not found: {old_disk_path}")
            print(f"   Skipping migration (disk will be created encrypted on first start)")
            self._update_config_for_encryption(old_disk_path, None)
            return

        # Get disk size in MB
        actual_size_mb = self._get_qcow2_size_mb(old_disk_path)
        print(f"Current disk: {old_disk_path}")
        print(f"Format:       QCOW2 (unencrypted)")
        print(f"Size:         {actual_size_mb} MB")
        print()

        # Create backup if requested
        if self.backup_enabled:
            print("Creating backup...")
            backup_path = old_disk_path.with_suffix('.qcow2.backup')
            shutil.copy2(old_disk_path, backup_path)
            print(f"✓ Backup created: {backup_path}")
            print()

        # Create new encrypted volume path
        new_disk_path = old_disk_path.with_suffix('.qvol')

        # Create encrypted volume
        print("Creating encrypted PQC volume...")
        volume = PQCVolume(str(new_disk_path), keystore=self.keystore)
        key_id = volume.create(
            volume_name=f"{self.vm_name}-primary",
            vm_name=self.vm_name,
            size_mb=actual_size_mb
        )
        print()

        # Migrate data from QCOW2 to PQC volume
        print("Migrating data to encrypted volume...")
        self._copy_disk_data(old_disk_path, volume, actual_size_mb)
        print()

        # Update config
        print("Updating VM configuration...")
        self._update_config_for_encryption(new_disk_path, key_id)
        print()

        # Cleanup
        if not self.backup_enabled:
            print(f"Removing old disk: {old_disk_path}")
            old_disk_path.unlink()
        else:
            print(f"Old disk preserved as backup: {old_disk_path}")
            print(f"You can safely delete it after verifying the encrypted VM works")

        print()
        print("=" * 70)
        print("✅ Migration Complete!")
        print("=" * 70)
        print(f"New encrypted disk: {new_disk_path}")
        print(f"Encryption key ID:  {key_id}")
        print(f"Algorithm:          ChaCha20-Poly1305")
        print()
        print("Next steps:")
        print(f"1. Test the VM: cd hypervisor/scripts && ./vm_manager.py start {self.vm_name}")
        print(f"2. Verify data integrity")
        if self.backup_enabled:
            print(f"3. Delete backup: rm {old_disk_path}")
        print("=" * 70)

    def _get_qcow2_size_mb(self, qcow2_path):
        """Get actual size of QCOW2 image in MB."""
        result = subprocess.run(
            ["qemu-img", "info", "--output=json", str(qcow2_path)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # Fallback to config size
            size_str = self.config['hardware']['disk']['primary']['size']
            return self._parse_size_to_mb(size_str)

        import json
        info = json.loads(result.stdout)
        virtual_size = info.get('virtual-size', 0)

        return max(1, virtual_size // (1024 * 1024))

    def _parse_size_to_mb(self, size_str):
        """Parse size string to MB."""
        size_str = size_str.upper().strip()

        if size_str.endswith('G'):
            return int(size_str[:-1]) * 1024
        elif size_str.endswith('M'):
            return int(size_str[:-1])
        elif size_str.endswith('K'):
            return max(1, int(size_str[:-1]) // 1024)
        else:
            return max(1, int(size_str) // (1024 * 1024))

    def _copy_disk_data(self, source_qcow2, dest_volume, size_mb):
        """
        Copy data from QCOW2 to PQC volume.

        Note: This is a simplified block-level copy.
        In production, you might want to use qemu-nbd for better compatibility.
        """
        BLOCK_SIZE = 4096
        total_blocks = (size_mb * 1024 * 1024) // BLOCK_SIZE

        # Convert QCOW2 to raw temporarily
        temp_raw = source_qcow2.with_suffix('.raw.tmp')

        print(f"   Converting QCOW2 to RAW (temporary)...")
        result = subprocess.run(
            ["qemu-img", "convert", "-f", "qcow2", "-O", "raw",
             str(source_qcow2), str(temp_raw)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to convert QCOW2: {result.stderr}")

        try:
            # Open volume for writing
            dest_volume.open()

            # Copy blocks
            print(f"   Copying {total_blocks} blocks ({size_mb} MB)...")

            with open(temp_raw, 'rb') as src:
                for block_num in range(total_blocks):
                    data = src.read(BLOCK_SIZE)

                    if not data:
                        break

                    # Check if block is all zeros (sparse)
                    if data == b'\x00' * len(data):
                        dest_volume.zero_block(block_num)
                    else:
                        dest_volume.write_block(block_num, data)

                    # Progress indicator
                    if (block_num + 1) % 1000 == 0:
                        progress = ((block_num + 1) / total_blocks) * 100
                        print(f"   Progress: {progress:.1f}% ({block_num + 1}/{total_blocks} blocks)")

            dest_volume.close()
            print(f"   ✓ Data migration complete")

        finally:
            # Cleanup temp file
            if temp_raw.exists():
                temp_raw.unlink()

    def _update_config_for_encryption(self, new_disk_path, key_id):
        """Update VM config to use encrypted storage."""
        # Update disk path
        self.config['hardware']['disk']['primary']['path'] = str(new_disk_path)

        # Add storage encryption config
        if 'storage' not in self.config:
            self.config['storage'] = {}

        self.config['storage']['encryption'] = {
            'enabled': True,
            'algorithm': 'chacha20-poly1305',
            'key_encapsulation': 'ecdh-curve25519',
            'key_id': key_id if key_id else 'pending'
        }

        # Save config
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

        print(f"✓ Configuration updated: {self.config_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate QWAMOS VM to encrypted PQC storage"
    )

    parser.add_argument(
        "vm_name",
        help="Name of the VM to migrate"
    )

    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup of original disk (not recommended)"
    )

    args = parser.parse_args()

    # Check if VM exists
    vm_dir = VMS_DIR / args.vm_name
    config_file = vm_dir / "config.yaml"

    if not config_file.exists():
        print(f"❌ Error: VM '{args.vm_name}' not found")
        print(f"   Expected config: {config_file}")
        sys.exit(1)

    # Perform migration
    migrator = VMStorageMigrator(args.vm_name, backup=not args.no_backup)

    try:
        migrator.migrate()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
