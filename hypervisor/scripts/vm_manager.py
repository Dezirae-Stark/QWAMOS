#!/usr/bin/env python3
"""
QWAMOS VM Manager
Manages QEMU virtual machines with post-quantum security
Phase XII: KVM hardware acceleration support
Phase XIII: Post-quantum encrypted storage support
"""

import os
import sys
import yaml
import subprocess
import argparse
from pathlib import Path

# Add hypervisor module to path
QWAMOS_ROOT = Path.home() / "QWAMOS"
sys.path.insert(0, str(QWAMOS_ROOT / "hypervisor"))
sys.path.insert(0, str(QWAMOS_ROOT / "crypto"))
sys.path.insert(0, str(QWAMOS_ROOT / "storage"))

# Import KVM Manager (Phase XII)
try:
    from kvm_manager import KVMManager
    KVM_AVAILABLE = True
except ImportError:
    KVM_AVAILABLE = False
    print("⚠️  KVM Manager not found - using legacy mode")

# Import PQC Storage (Phase XIII)
try:
    from pqc_keystore import PQCKeystore
    from pqc_volume import PQCVolume
    PQC_STORAGE_AVAILABLE = True
except ImportError:
    PQC_STORAGE_AVAILABLE = False
    print("⚠️  PQC Storage not found - encryption disabled")

# QWAMOS Paths
VMS_DIR = QWAMOS_ROOT / "vms"
HYPERVISOR_DIR = QWAMOS_ROOT / "hypervisor"
LOGS_DIR = HYPERVISOR_DIR / "logs"

class VMManager:
    """Manages QEMU VMs for QWAMOS"""

    def __init__(self, vm_name):
        self.vm_name = vm_name
        self.vm_dir = VMS_DIR / vm_name
        self.config_file = self.vm_dir / "config.yaml"
        self.config = None

        # Initialize KVM Manager (Phase XII)
        if KVM_AVAILABLE:
            self.kvm_manager = KVMManager()
            self.kvm_enabled = self.kvm_manager.enabled
        else:
            self.kvm_manager = None
            self.kvm_enabled = False

        # Initialize PQC Storage (Phase XIII)
        if PQC_STORAGE_AVAILABLE:
            self.pqc_keystore = PQCKeystore()
            self.pqc_storage_enabled = True
        else:
            self.pqc_keystore = None
            self.pqc_storage_enabled = False

        # Ensure logs directory exists
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

    def load_config(self):
        """Load VM configuration from YAML"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        return self.config

    def build_qemu_command(self):
        """Build QEMU command from configuration"""
        if not self.config:
            self.load_config()

        vm = self.config['vm']
        hw = self.config['hardware']
        net = self.config['network']
        boot = self.config['boot']
        machine = self.config['machine']

        # Phase XII: Use KVM Manager for optimal acceleration
        if self.kvm_manager:
            # Let KVM manager decide acceleration and CPU model
            vm_config = {
                "name": vm['name'],
                "cpu": hw['cpu']['cores'],
                "memory": str(hw['memory']['size']) + "M",
            }
            kvm_args = self.kvm_manager.generate_qemu_args(vm_config)

            # Start with base command
            cmd = ["qemu-system-aarch64", "-name", vm['name']]

            # Add KVM-optimized args (accel, cpu, machine, smp, memory)
            cmd.extend(kvm_args)
        else:
            # Legacy mode: use config directly
            cmd = [
                "qemu-system-aarch64",
                "-name", vm['name'],
                "-machine", f"{machine['type']},accel={machine['accel']},gic-version={machine['gic_version']}",
                "-cpu", hw['cpu']['model'],
                "-smp", str(hw['cpu']['cores']),
                "-m", str(hw['memory']['size']),
            ]

        # Boot configuration
        if os.path.exists(boot['kernel']):
            cmd.extend(["-kernel", boot['kernel']])

        if os.path.exists(boot['initrd']):
            cmd.extend(["-initrd", boot['initrd']])

        cmd.extend(["-append", boot['cmdline']])

        # Disk (create if doesn't exist)
        disk_path = hw['disk']['primary']['path']
        if not os.path.exists(disk_path):
            disk_size = hw['disk']['primary']['size']
            print(f"Creating disk image: {disk_path} ({disk_size})")
            self.create_disk(disk_path, disk_size)

        cmd.extend([
            "-drive", f"file={disk_path},if=virtio,format=qcow2,cache=writeback"
        ])

        # Network
        if net['mode'] == 'nat':
            nat_rules = net.get('nat_rules', [])
            hostfwd = []
            for rule in nat_rules:
                hostfwd.append(f"{rule['protocol']}::{rule['host_port']}-:{rule['guest_port']}")

            netdev_str = f"user,id=net0"
            if hostfwd:
                for fwd in hostfwd:
                    netdev_str += f",hostfwd={fwd}"

            cmd.extend([
                "-netdev", netdev_str,
                "-device", f"{net['device']},netdev=net0,mac={net['mac']}"
            ])

        # Graphics
        if hw.get('graphics', {}).get('type'):
            cmd.extend(["-device", hw['graphics']['type']])

        # Extra args
        extra_args = self.config.get('qemu_extra_args', [])
        cmd.extend(extra_args)

        return cmd

    def create_disk(self, disk_path, size, encrypted=None):
        """
        Create disk image (QCOW2 or encrypted PQC volume).

        Args:
            disk_path: Path to disk file
            size: Size string (e.g., "10G", "512M")
            encrypted: True/False/None (None = auto-detect from config)
        """
        os.makedirs(os.path.dirname(disk_path), exist_ok=True)

        # Auto-detect encryption from config if not specified
        if encrypted is None:
            encrypted = self.config.get('storage', {}).get('encryption', {}).get('enabled', False)

        if encrypted and self.pqc_storage_enabled:
            # Create encrypted PQC volume
            return self._create_encrypted_disk(disk_path, size)
        else:
            # Create standard QCOW2 image
            return self._create_qcow2_disk(disk_path, size)

    def _create_qcow2_disk(self, disk_path, size):
        """Create standard QCOW2 disk image."""
        cmd = [
            "qemu-img", "create",
            "-f", "qcow2",
            disk_path,
            size
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create disk: {result.stderr}")

        print(f"✓ Created QCOW2 disk: {disk_path}")

    def _create_encrypted_disk(self, disk_path, size):
        """Create encrypted PQC volume."""
        # Convert size string to MB (e.g., "10G" -> 10240, "512M" -> 512)
        size_mb = self._parse_size_to_mb(size)

        # Change extension to .qvol for encrypted volumes
        if disk_path.endswith('.qcow2'):
            encrypted_path = disk_path.replace('.qcow2', '.qvol')
        elif not disk_path.endswith('.qvol'):
            encrypted_path = disk_path + '.qvol'
        else:
            encrypted_path = disk_path

        # Create PQC volume
        volume = PQCVolume(encrypted_path, keystore=self.pqc_keystore)
        key_id = volume.create(
            volume_name=f"{self.vm_name}-primary",
            vm_name=self.vm_name,
            size_mb=size_mb
        )

        # Store key ID in VM config for future reference
        if 'storage' not in self.config:
            self.config['storage'] = {}
        if 'encryption' not in self.config['storage']:
            self.config['storage']['encryption'] = {}

        self.config['storage']['encryption']['key_id'] = key_id
        self.config['storage']['encryption']['enabled'] = True

        # Update disk path in config to .qvol
        self.config['hardware']['disk']['primary']['path'] = encrypted_path

        # Save updated config
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

        print(f"🔒 Created encrypted PQC volume: {encrypted_path}")
        print(f"   Size: {size_mb} MB")
        print(f"   Key ID: {key_id}")
        print(f"   Encryption: ChaCha20-Poly1305")

        return encrypted_path

    def _parse_size_to_mb(self, size_str):
        """Parse size string (e.g., '10G', '512M') to megabytes."""
        size_str = size_str.upper().strip()

        if size_str.endswith('G'):
            return int(size_str[:-1]) * 1024
        elif size_str.endswith('M'):
            return int(size_str[:-1])
        elif size_str.endswith('K'):
            return max(1, int(size_str[:-1]) // 1024)
        else:
            # Assume bytes, convert to MB
            return max(1, int(size_str) // (1024 * 1024))

    def start(self, background=False):
        """Start the VM"""
        print(f"Starting VM: {self.vm_name}")

        # Phase XII: Display acceleration status
        if self.kvm_manager:
            if self.kvm_enabled:
                print("🚀 KVM Hardware Acceleration: ENABLED")
            else:
                print("🐢 TCG Software Emulation: ENABLED (expect slower performance)")

        cmd = self.build_qemu_command()

        print(f"\nQEMU Command:")
        print(" ".join(cmd))
        print()

        log_file = LOGS_DIR / f"{self.vm_name}.log"

        if background:
            # Start in background
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT
                )
            print(f"✓ VM started in background (PID: {process.pid})")
            print(f"  Log: {log_file}")

            # Phase XII: Apply CPU affinity if configured
            if self.kvm_manager and 'cpu_affinity' in self.config.get('performance', {}):
                policy = self.config['performance']['cpu_affinity']
                self.kvm_manager.configure_vcpu_affinity(
                    vm_pid=process.pid,
                    vm_name=self.vm_name,
                    vcpu_policy=policy
                )
        else:
            # Interactive mode
            subprocess.run(cmd)

    def status(self):
        """Check VM status"""
        # Check if VM process is running
        result = subprocess.run(
            ["pgrep", "-f", f"qemu.*{self.vm_name}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"VM '{self.vm_name}' is RUNNING")
            print(f"PIDs: {', '.join(pids)}")
            return True
        else:
            print(f"VM '{self.vm_name}' is STOPPED")
            return False

    def stop(self):
        """Stop the VM"""
        result = subprocess.run(
            ["pkill", "-f", f"qemu.*{self.vm_name}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✓ VM '{self.vm_name}' stopped")
        else:
            print(f"VM '{self.vm_name}' was not running")

    def info(self):
        """Display VM information"""
        config = self.load_config()

        print(f"\n{'='*60}")
        print(f"VM: {config['vm']['name']}")
        print(f"{'='*60}")
        print(f"Type:        {config['vm']['type']}")
        print(f"Description: {config['vm']['description']}")
        print()
        print(f"CPU:         {config['hardware']['cpu']['cores']} x {config['hardware']['cpu']['model']}")
        print(f"Memory:      {config['hardware']['memory']['size']} MB")
        print(f"Disk:        {config['hardware']['disk']['primary']['size']}")
        print(f"Network:     {config['network']['mode']}")
        print(f"Autostart:   {config.get('autostart', False)}")

        # Phase XII: Show acceleration status
        if self.kvm_manager:
            accel_status = "✅ KVM" if self.kvm_enabled else "⚠️  TCG (software)"
            print(f"Acceleration: {accel_status}")

        # Phase XIII: Show encryption status
        storage_config = config.get('storage', {})
        encryption_config = storage_config.get('encryption', {})
        if encryption_config.get('enabled', False):
            key_id = encryption_config.get('key_id', 'unknown')
            print(f"Encryption:   🔒 ENABLED (PQC)")
            print(f"  Algorithm:  ChaCha20-Poly1305")
            print(f"  Key ID:     {key_id}")
        else:
            disk_path = config['hardware']['disk']['primary']['path']
            if disk_path.endswith('.qvol'):
                print(f"Encryption:   🔒 ENABLED (legacy)")
            else:
                print(f"Encryption:   ❌ DISABLED")

        print(f"{'='*60}\n")

def list_vms():
    """List all available VMs"""
    print("\nAvailable VMs:")
    print("-" * 60)

    if not VMS_DIR.exists():
        print("No VMs directory found")
        return

    vms = [d for d in VMS_DIR.iterdir() if d.is_dir() and (d / "config.yaml").exists()]

    if not vms:
        print("No VMs configured")
        return

    for vm_dir in sorted(vms):
        vm_name = vm_dir.name
        config_file = vm_dir / "config.yaml"

        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)

            desc = config['vm'].get('description', 'No description')
            vm_type = config['vm'].get('type', 'unknown')

            # Check if running
            result = subprocess.run(
                ["pgrep", "-f", f"qemu.*{vm_name}"],
                capture_output=True,
                text=True
            )
            status = "RUNNING" if result.returncode == 0 else "STOPPED"

            print(f"  {vm_name:20} [{status:8}] {vm_type:10} - {desc}")

        except Exception as e:
            print(f"  {vm_name:20} [ERROR] Could not load config")

    print("-" * 60 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="QWAMOS VM Manager - Manage QEMU virtual machines"
    )

    parser.add_argument(
        "command",
        choices=["start", "stop", "status", "info", "list"],
        help="Command to execute"
    )

    parser.add_argument(
        "vm_name",
        nargs="?",
        help="Name of the VM (not required for 'list')"
    )

    parser.add_argument(
        "-b", "--background",
        action="store_true",
        help="Start VM in background"
    )

    args = parser.parse_args()

    # List command doesn't need a VM name
    if args.command == "list":
        list_vms()
        return

    # All other commands require a VM name
    if not args.vm_name:
        parser.error(f"VM name required for '{args.command}' command")

    # Create VM manager
    vm = VMManager(args.vm_name)

    # Execute command
    if args.command == "start":
        vm.start(background=args.background)
    elif args.command == "stop":
        vm.stop()
    elif args.command == "status":
        vm.status()
    elif args.command == "info":
        vm.info()

if __name__ == "__main__":
    main()
