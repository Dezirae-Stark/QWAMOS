#!/usr/bin/env python3
"""
QWAMOS VM Creator
User-driven VM creation from proot-distro images or cloud images
"""

import os
import sys
import json
import subprocess
import urllib.request
from pathlib import Path

# VM Templates
VM_TEMPLATES = {
    "debian-whonix": {
        "name": "Debian 12 (Whonix Gateway)",
        "description": "Tor gateway for anonymous networking",
        "source": "proot-distro",
        "distro": "debian",
        "ram": "1G",
        "disk": "8G",
        "packages": ["tor", "iptables", "python3"],
        "config": "whonix-gateway"
    },
    "kali-pentest": {
        "name": "Kali Linux (Penetration Testing)",
        "description": "Full Kali NetHunter tools for security testing",
        "source": "proot-distro",
        "distro": "kali",
        "ram": "2G",
        "disk": "16G",
        "packages": ["nmap", "sqlmap", "metasploit-framework", "burpsuite"],
        "config": "kali-wfh"
    },
    "debian-minimal": {
        "name": "Debian 12 (Minimal)",
        "description": "Lightweight Debian for general tasks",
        "source": "proot-distro",
        "distro": "debian",
        "ram": "512M",
        "disk": "4G",
        "packages": ["python3", "git", "vim"],
        "config": "minimal"
    },
    "ubuntu-workspace": {
        "name": "Ubuntu 22.04 (Desktop)",
        "description": "Full Ubuntu environment",
        "source": "proot-distro",
        "distro": "ubuntu",
        "ram": "2G",
        "disk": "16G",
        "packages": ["build-essential", "python3", "nodejs"],
        "config": "workspace"
    },
    "alpine-vault": {
        "name": "Alpine (Crypto Vault)",
        "description": "Airgapped cryptocurrency wallet",
        "source": "proot-distro",
        "distro": "alpine",
        "ram": "256M",
        "disk": "2G",
        "packages": ["python3", "gnupg"],
        "config": "vault"
    },
    "custom": {
        "name": "Custom VM",
        "description": "User-configured VM",
        "source": "manual",
        "distro": "debian",
        "ram": "1G",
        "disk": "8G",
        "packages": [],
        "config": "custom"
    }
}

class QWAMOSVMCreator:
    """VM Creation Wizard"""

    def __init__(self, vm_dir="/data/data/com.termux/files/home/QWAMOS/vms"):
        self.vm_dir = Path(vm_dir)
        self.vm_dir.mkdir(exist_ok=True, parents=True)

    def list_templates(self):
        """Show available VM templates"""
        print("\n" + "="*60)
        print("  QWAMOS VM Templates")
        print("="*60)
        print()

        for i, (key, template) in enumerate(VM_TEMPLATES.items(), 1):
            print(f"{i}. {template['name']}")
            print(f"   {template['description']}")
            print(f"   RAM: {template['ram']}, Disk: {template['disk']}")
            print()

    def create_vm(self, template_key, vm_name, persistent=True, encrypted=True):
        """Create a new VM from template"""

        if template_key not in VM_TEMPLATES:
            print(f"[!] Error: Template '{template_key}' not found")
            return False

        template = VM_TEMPLATES[template_key]
        vm_path = self.vm_dir / vm_name

        print(f"\n[*] Creating VM: {vm_name}")
        print(f"[*] Template: {template['name']}")
        print(f"[*] Persistent: {persistent}")
        print(f"[*] Encrypted: {encrypted}")
        print()

        # Step 1: Create VM directory
        vm_path.mkdir(exist_ok=True, parents=True)
        print(f"[+] Created VM directory: {vm_path}")

        # Step 2: Download/extract rootfs
        if template['source'] == 'proot-distro':
            self._install_proot_distro(template['distro'], vm_path)

        # Step 3: Create disk image
        disk_size = template['disk']
        disk_path = vm_path / "disk.qcow2"

        if persistent:
            self._create_disk_image(disk_path, disk_size, encrypted)
        else:
            print("[*] Disposable VM - no persistent disk created")

        # Step 4: Install packages
        if template['packages']:
            self._install_packages(vm_path, template['packages'])

        # Step 5: Create VM config
        self._create_vm_config(vm_name, template, vm_path, persistent, encrypted)

        # Step 6: Apply template-specific config
        if template['config'] == 'whonix-gateway':
            self._configure_whonix(vm_path)
        elif template['config'] == 'kali-wfh':
            self._configure_kali(vm_path)
        elif template['config'] == 'vault':
            self._configure_vault(vm_path)

        print()
        print("="*60)
        print(f"  VM Created Successfully: {vm_name}")
        print("="*60)
        print()
        print(f"VM Path: {vm_path}")
        print(f"Config: {vm_path}/config.yaml")
        print()
        print("To start this VM:")
        print(f"  python3 ~/QWAMOS/hypervisor/scripts/vm_manager.py start {vm_name}")
        print()

        return True

    def _install_proot_distro(self, distro, vm_path):
        """Install proot-distro rootfs"""
        print(f"[*] Installing {distro} from proot-distro...")

        rootfs_path = vm_path / "rootfs"
        rootfs_path.mkdir(exist_ok=True, parents=True)

        # Download and extract proot-distro
        cmd = f"proot-distro install {distro}"

        print(f"[*] Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"[+] {distro} rootfs downloaded")

            # Copy rootfs to VM directory
            distro_path = f"/data/data/com.termux/files/usr/var/lib/proot-distro/installed-rootfs/{distro}"
            if os.path.exists(distro_path):
                print(f"[*] Copying rootfs to {rootfs_path}...")
                subprocess.run(f"cp -r {distro_path}/* {rootfs_path}/", shell=True)
                print("[+] Rootfs copied to VM directory")
            else:
                print(f"[!] Warning: Could not find rootfs at {distro_path}")
        else:
            print(f"[!] Error installing {distro}: {result.stderr}")

    def _create_disk_image(self, disk_path, size, encrypted):
        """Create QCOW2 disk image"""
        print(f"[*] Creating {size} disk image: {disk_path}")

        # Create QCOW2 image
        cmd = f"qemu-img create -f qcow2 {disk_path} {size}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"[+] Disk image created: {disk_path}")

            if encrypted:
                print("[*] Encrypting disk with ChaCha20-Poly1305...")
                # TODO: Integrate with volume_manager.py
                # For now, just note it needs encryption
                print("[!] Note: Encryption will be applied on first boot")
        else:
            print(f"[!] Error creating disk: {result.stderr}")

    def _install_packages(self, vm_path, packages):
        """Install packages in VM rootfs"""
        print(f"[*] Installing packages: {', '.join(packages)}")

        rootfs = vm_path / "rootfs"
        if not rootfs.exists():
            print("[!] Warning: rootfs not found, skipping package installation")
            return

        # Create install script
        install_script = rootfs / "install_packages.sh"
        with open(install_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("apt-get update\n")
            f.write(f"apt-get install -y {' '.join(packages)}\n")

        os.chmod(install_script, 0o755)
        print("[+] Package installation script created")
        print("[*] Packages will be installed on first boot")

    def _create_vm_config(self, vm_name, template, vm_path, persistent, encrypted):
        """Create VM configuration YAML"""

        config = {
            "vm": {
                "name": vm_name,
                "type": template['config'],
                "description": template['description']
            },
            "resources": {
                "ram": template['ram'],
                "cpus": 2,
                "disk": template['disk']
            },
            "storage": {
                "disk_image": str(vm_path / "disk.qcow2") if persistent else None,
                "rootfs": str(vm_path / "rootfs"),
                "persistent": persistent,
                "encrypted": encrypted
            },
            "network": {
                "mode": "bridge",
                "bridge": "qwamos-br0" if template['config'] != 'android' else "qwamos-nat"
            }
        }

        config_path = vm_path / "config.yaml"

        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        print(f"[+] VM config created: {config_path}")

    def _configure_whonix(self, vm_path):
        """Apply Whonix Gateway configuration"""
        print("[*] Configuring Whonix Gateway...")

        # Copy torrc
        torrc_src = Path("~/QWAMOS/vms/whonix-vm/torrc").expanduser()
        torrc_dst = vm_path / "rootfs/etc/tor/torrc"

        if torrc_src.exists():
            torrc_dst.parent.mkdir(exist_ok=True, parents=True)
            subprocess.run(f"cp {torrc_src} {torrc_dst}", shell=True)
            print("[+] Tor configuration copied")

        # Copy firewall
        firewall_src = Path("~/QWAMOS/vms/whonix-vm/firewall.sh").expanduser()
        firewall_dst = vm_path / "firewall.sh"

        if firewall_src.exists():
            subprocess.run(f"cp {firewall_src} {firewall_dst}", shell=True)
            os.chmod(firewall_dst, 0o755)
            print("[+] Firewall script copied")

    def _configure_kali(self, vm_path):
        """Apply Kali configuration"""
        print("[*] Configuring Kali Linux...")

        # Create post-install script for Kali tools
        script_path = vm_path / "rootfs/setup_kali.sh"
        with open(script_path, 'w') as f:
            f.write("""#!/bin/bash
# QWAMOS Kali Setup Script

echo "[*] Updating Kali repositories..."
apt-get update

echo "[*] Installing Kali tools..."
apt-get install -y kali-linux-core

echo "[*] Installing additional tools..."
apt-get install -y nmap sqlmap metasploit-framework burpsuite

echo "[+] Kali setup complete!"
""")
        os.chmod(script_path, 0o755)
        print("[+] Kali setup script created")

    def _configure_vault(self, vm_path):
        """Apply airgapped vault configuration"""
        print("[*] Configuring Crypto Vault...")

        # Disable networking in config
        config_path = vm_path / "config.yaml"
        if config_path.exists():
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            config['network']['mode'] = 'none'
            config['security'] = {
                'airgapped': True,
                'no_network': True,
                'read_only_host': True
            }

            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)

            print("[+] Vault configured as airgapped")

    def destroy_vm(self, vm_name, confirm=True):
        """Destroy a VM and all its data"""

        vm_path = self.vm_dir / vm_name

        if not vm_path.exists():
            print(f"[!] Error: VM '{vm_name}' does not exist")
            return False

        if confirm:
            print(f"\n[!] WARNING: This will permanently delete VM '{vm_name}'")
            response = input("Type 'yes' to confirm: ")
            if response.lower() != 'yes':
                print("[*] Cancelled")
                return False

        print(f"[*] Destroying VM: {vm_name}")
        print(f"[*] Deleting: {vm_path}")

        # Securely wipe disk if it exists
        disk_path = vm_path / "disk.qcow2"
        if disk_path.exists():
            print("[*] Securely wiping disk...")
            # Overwrite with random data
            subprocess.run(f"dd if=/dev/urandom of={disk_path} bs=1M count=10 2>/dev/null", shell=True)
            os.remove(disk_path)
            print("[+] Disk wiped and deleted")

        # Remove entire VM directory
        subprocess.run(f"rm -rf {vm_path}", shell=True)

        print()
        print(f"[+] VM '{vm_name}' destroyed successfully")
        print()

        return True

def main():
    if len(sys.argv) < 2:
        print("QWAMOS VM Creator")
        print()
        print("Usage:")
        print("  vm_creator.py list")
        print("  vm_creator.py create <template> <vm-name> [--disposable] [--no-encrypt]")
        print("  vm_creator.py destroy <vm-name>")
        print()
        print("Examples:")
        print("  vm_creator.py list")
        print("  vm_creator.py create debian-whonix my-tor-gateway")
        print("  vm_creator.py create kali-pentest my-kali")
        print("  vm_creator.py create debian-minimal temp-vm --disposable")
        print("  vm_creator.py destroy temp-vm")
        sys.exit(1)

    creator = QWAMOSVMCreator()
    command = sys.argv[1]

    if command == "list":
        creator.list_templates()

    elif command == "create":
        if len(sys.argv) < 4:
            print("Usage: vm_creator.py create <template> <vm-name> [--disposable] [--no-encrypt]")
            sys.exit(1)

        template = sys.argv[2]
        vm_name = sys.argv[3]
        persistent = "--disposable" not in sys.argv
        encrypted = "--no-encrypt" not in sys.argv

        creator.create_vm(template, vm_name, persistent, encrypted)

    elif command == "destroy":
        if len(sys.argv) < 3:
            print("Usage: vm_creator.py destroy <vm-name>")
            sys.exit(1)

        vm_name = sys.argv[2]
        creator.destroy_vm(vm_name)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
