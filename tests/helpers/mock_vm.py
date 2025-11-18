"""
QWAMOS Mock VM Implementations
Mock implementations for testing QEMU and PRoot without actual virtualization
"""

import os
from typing import Dict, List, Optional
from enum import Enum


class VMState(Enum):
    """VM states"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


class VMType(Enum):
    """VM types"""
    QEMU_KVM = "qemu-kvm"
    QEMU_TCG = "qemu-tcg"
    PROOT = "proot"


class MockQEMUVM:
    """Mock QEMU virtual machine for testing"""

    def __init__(self, vm_id: str, vm_type: VMType = VMType.QEMU_TCG):
        self.vm_id = vm_id
        self.vm_type = vm_type
        self.state = VMState.STOPPED
        self.cpu_cores = 2
        self.memory_mb = 2048
        self.disk_image = None
        self.network_interfaces = []
        self.kvm_enabled = (vm_type == VMType.QEMU_KVM)

    def start(self) -> bool:
        """Start the VM"""
        if self.state == VMState.RUNNING:
            return True

        self.state = VMState.STARTING
        # Simulate startup delay
        self.state = VMState.RUNNING
        return True

    def stop(self) -> bool:
        """Stop the VM"""
        if self.state == VMState.STOPPED:
            return True

        self.state = VMState.STOPPING
        self.state = VMState.STOPPED
        return True

    def pause(self) -> bool:
        """Pause the VM"""
        if self.state != VMState.RUNNING:
            raise RuntimeError(f"Cannot pause VM in state: {self.state}")

        self.state = VMState.PAUSED
        return True

    def resume(self) -> bool:
        """Resume the VM"""
        if self.state != VMState.PAUSED:
            raise RuntimeError(f"Cannot resume VM in state: {self.state}")

        self.state = VMState.RUNNING
        return True

    def get_state(self) -> VMState:
        """Get current VM state"""
        return self.state

    def set_cpu_cores(self, cores: int):
        """Set number of CPU cores"""
        if self.state == VMState.RUNNING:
            raise RuntimeError("Cannot change CPU cores while VM is running")
        self.cpu_cores = cores

    def set_memory(self, memory_mb: int):
        """Set memory size in MB"""
        if self.state == VMState.RUNNING:
            raise RuntimeError("Cannot change memory while VM is running")
        self.memory_mb = memory_mb

    def attach_disk(self, disk_path: str):
        """Attach disk image"""
        if self.state == VMState.RUNNING:
            raise RuntimeError("Cannot attach disk while VM is running")
        self.disk_image = disk_path

    def add_network_interface(self, interface_type: str = "virtio-net"):
        """Add network interface"""
        interface = {
            "type": interface_type,
            "mac": f"52:54:00:12:34:{len(self.network_interfaces):02x}"
        }
        self.network_interfaces.append(interface)
        return interface

    def check_kvm_support(self) -> bool:
        """Check if KVM is available"""
        return self.kvm_enabled

    def get_info(self) -> Dict:
        """Get VM information"""
        return {
            "vm_id": self.vm_id,
            "type": self.vm_type.value,
            "state": self.state.value,
            "cpu_cores": self.cpu_cores,
            "memory_mb": self.memory_mb,
            "kvm_enabled": self.kvm_enabled,
            "disk": self.disk_image,
            "network_interfaces": len(self.network_interfaces)
        }


class MockPRootContainer:
    """Mock PRoot container for testing"""

    def __init__(self, container_id: str, rootfs_path: str):
        self.container_id = container_id
        self.rootfs_path = rootfs_path
        self.state = VMState.STOPPED
        self.bind_mounts = []
        self.environment = {}
        self.working_dir = "/"

    def start(self, command: str = "/bin/sh") -> bool:
        """Start PRoot container"""
        if self.state == VMState.RUNNING:
            return True

        self.state = VMState.RUNNING
        return True

    def stop(self) -> bool:
        """Stop PRoot container"""
        if self.state == VMState.STOPPED:
            return True

        self.state = VMState.STOPPED
        return True

    def add_bind_mount(self, host_path: str, container_path: str):
        """Add bind mount"""
        if self.state == VMState.RUNNING:
            raise RuntimeError("Cannot add bind mount while container is running")

        self.bind_mounts.append({
            "host": host_path,
            "container": container_path
        })

    def set_environment(self, key: str, value: str):
        """Set environment variable"""
        self.environment[key] = value

    def set_working_dir(self, path: str):
        """Set working directory"""
        if self.state == VMState.RUNNING:
            raise RuntimeError("Cannot change working directory while container is running")
        self.working_dir = path

    def execute(self, command: str) -> Dict:
        """Execute command in container"""
        if self.state != VMState.RUNNING:
            raise RuntimeError("Container is not running")

        return {
            "exit_code": 0,
            "stdout": f"Mock execution of: {command}",
            "stderr": ""
        }

    def get_info(self) -> Dict:
        """Get container information"""
        return {
            "container_id": self.container_id,
            "type": "proot",
            "state": self.state.value,
            "rootfs": self.rootfs_path,
            "bind_mounts": len(self.bind_mounts),
            "working_dir": self.working_dir
        }


class MockVMIsolation:
    """Mock VM isolation for testing network/disk isolation"""

    def __init__(self, vm):
        self.vm = vm
        self.network_isolated = False
        self.disk_isolated = True
        self.allowed_hosts = []

    def enable_network_isolation(self):
        """Enable network isolation"""
        self.network_isolated = True

    def disable_network_isolation(self):
        """Disable network isolation"""
        self.network_isolated = False

    def add_allowed_host(self, host: str):
        """Add host to allowlist"""
        if host not in self.allowed_hosts:
            self.allowed_hosts.append(host)

    def remove_allowed_host(self, host: str):
        """Remove host from allowlist"""
        if host in self.allowed_hosts:
            self.allowed_hosts.remove(host)

    def check_network_access(self, host: str) -> bool:
        """Check if network access to host is allowed"""
        if not self.network_isolated:
            return True
        return host in self.allowed_hosts

    def enable_disk_isolation(self):
        """Enable disk isolation"""
        self.disk_isolated = True

    def disable_disk_isolation(self):
        """Disable disk isolation (dangerous!)"""
        self.disk_isolated = False

    def get_isolation_status(self) -> Dict:
        """Get isolation status"""
        return {
            "network_isolated": self.network_isolated,
            "disk_isolated": self.disk_isolated,
            "allowed_hosts": self.allowed_hosts.copy()
        }


class MockVMManager:
    """Mock VM manager for managing multiple VMs"""

    def __init__(self):
        self.vms = {}
        self.next_vm_id = 1

    def create_qemu_vm(self, vm_type: VMType = VMType.QEMU_TCG) -> MockQEMUVM:
        """Create new QEMU VM"""
        vm_id = f"qemu_vm_{self.next_vm_id}"
        self.next_vm_id += 1

        vm = MockQEMUVM(vm_id, vm_type)
        self.vms[vm_id] = vm
        return vm

    def create_proot_container(self, rootfs_path: str) -> MockPRootContainer:
        """Create new PRoot container"""
        container_id = f"proot_container_{self.next_vm_id}"
        self.next_vm_id += 1

        container = MockPRootContainer(container_id, rootfs_path)
        self.vms[container_id] = container
        return container

    def get_vm(self, vm_id: str):
        """Get VM by ID"""
        return self.vms.get(vm_id)

    def list_vms(self) -> List[str]:
        """List all VM IDs"""
        return list(self.vms.keys())

    def delete_vm(self, vm_id: str) -> bool:
        """Delete VM"""
        if vm_id not in self.vms:
            return False

        vm = self.vms[vm_id]
        if hasattr(vm, 'state') and vm.state == VMState.RUNNING:
            vm.stop()

        del self.vms[vm_id]
        return True

    def get_all_vm_info(self) -> List[Dict]:
        """Get information for all VMs"""
        return [vm.get_info() for vm in self.vms.values()]


class MockVMSnapshot:
    """Mock VM snapshot functionality"""

    def __init__(self, vm):
        self.vm = vm
        self.snapshots = {}
        self.next_snapshot_id = 1

    def create_snapshot(self, name: str) -> str:
        """Create VM snapshot"""
        snapshot_id = f"snapshot_{self.next_snapshot_id}"
        self.next_snapshot_id += 1

        self.snapshots[snapshot_id] = {
            "id": snapshot_id,
            "name": name,
            "vm_state": self.vm.get_state(),
            "timestamp": "2024-01-01T00:00:00Z"
        }

        return snapshot_id

    def restore_snapshot(self, snapshot_id: str) -> bool:
        """Restore VM to snapshot"""
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        snapshot = self.snapshots[snapshot_id]
        # Simulate restoration
        return True

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete snapshot"""
        if snapshot_id not in self.snapshots:
            return False

        del self.snapshots[snapshot_id]
        return True

    def list_snapshots(self) -> List[Dict]:
        """List all snapshots"""
        return list(self.snapshots.values())
