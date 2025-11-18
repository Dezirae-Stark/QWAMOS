"""
QWAMOS VM Isolation Integration Tests
Tests for VM isolation, network containment, and disk isolation
"""

import pytest
from tests.helpers.mock_vm import (
    MockQEMUVM,
    MockPRootContainer,
    MockVMIsolation,
    MockVMManager,
    MockVMSnapshot,
    VMState,
    VMType
)


class TestQEMUVMIsolation:
    """Test QEMU VM isolation"""

    def test_qemu_vm_creation(self):
        """Test QEMU VM creation"""
        vm = MockQEMUVM("test_vm_1", VMType.QEMU_TCG)
        assert vm.vm_id == "test_vm_1"
        assert vm.state == VMState.STOPPED
        assert vm.vm_type == VMType.QEMU_TCG

    def test_qemu_vm_start_stop(self):
        """Test VM start and stop"""
        vm = MockQEMUVM("test_vm_1")

        assert vm.start() is True
        assert vm.state == VMState.RUNNING

        assert vm.stop() is True
        assert vm.state == VMState.STOPPED

    def test_qemu_vm_pause_resume(self):
        """Test VM pause and resume"""
        vm = MockQEMUVM("test_vm_1")
        vm.start()

        assert vm.pause() is True
        assert vm.state == VMState.PAUSED

        assert vm.resume() is True
        assert vm.state == VMState.RUNNING

    def test_qemu_vm_pause_fails_when_not_running(self):
        """Test pause fails when VM is not running"""
        vm = MockQEMUVM("test_vm_1")

        with pytest.raises(RuntimeError, match="Cannot pause"):
            vm.pause()

    def test_qemu_vm_resume_fails_when_not_paused(self):
        """Test resume fails when VM is not paused"""
        vm = MockQEMUVM("test_vm_1")
        vm.start()

        with pytest.raises(RuntimeError, match="Cannot resume"):
            vm.resume()

    def test_qemu_vm_cpu_configuration(self):
        """Test CPU configuration"""
        vm = MockQEMUVM("test_vm_1")

        vm.set_cpu_cores(4)
        assert vm.cpu_cores == 4

    def test_qemu_vm_cpu_config_fails_when_running(self):
        """Test CPU config fails when running"""
        vm = MockQEMUVM("test_vm_1")
        vm.start()

        with pytest.raises(RuntimeError, match="Cannot change CPU"):
            vm.set_cpu_cores(4)

    def test_qemu_vm_memory_configuration(self):
        """Test memory configuration"""
        vm = MockQEMUVM("test_vm_1")

        vm.set_memory(4096)
        assert vm.memory_mb == 4096

    def test_qemu_vm_memory_config_fails_when_running(self):
        """Test memory config fails when running"""
        vm = MockQEMUVM("test_vm_1")
        vm.start()

        with pytest.raises(RuntimeError, match="Cannot change memory"):
            vm.set_memory(4096)

    def test_qemu_vm_disk_attachment(self):
        """Test disk attachment"""
        vm = MockQEMUVM("test_vm_1")

        vm.attach_disk("/path/to/disk.qcow2")
        assert vm.disk_image == "/path/to/disk.qcow2"

    def test_qemu_vm_network_interface(self):
        """Test network interface creation"""
        vm = MockQEMUVM("test_vm_1")

        interface = vm.add_network_interface("virtio-net")

        assert interface["type"] == "virtio-net"
        assert len(interface["mac"]) == 17  # MAC address format
        assert len(vm.network_interfaces) == 1

    def test_qemu_vm_kvm_support(self):
        """Test KVM support detection"""
        vm_tcg = MockQEMUVM("test_vm_1", VMType.QEMU_TCG)
        vm_kvm = MockQEMUVM("test_vm_2", VMType.QEMU_KVM)

        assert vm_tcg.check_kvm_support() is False
        assert vm_kvm.check_kvm_support() is True

    def test_qemu_vm_info(self):
        """Test VM info retrieval"""
        vm = MockQEMUVM("test_vm_1", VMType.QEMU_TCG)
        vm.set_cpu_cores(4)
        vm.set_memory(4096)

        info = vm.get_info()

        assert info["vm_id"] == "test_vm_1"
        assert info["type"] == "qemu-tcg"
        assert info["cpu_cores"] == 4
        assert info["memory_mb"] == 4096


class TestPRootContainerIsolation:
    """Test PRoot container isolation"""

    def test_proot_container_creation(self):
        """Test PRoot container creation"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")
        assert container.container_id == "test_container_1"
        assert container.rootfs_path == "/path/to/rootfs"
        assert container.state == VMState.STOPPED

    def test_proot_container_start_stop(self):
        """Test container start and stop"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")

        assert container.start() is True
        assert container.state == VMState.RUNNING

        assert container.stop() is True
        assert container.state == VMState.STOPPED

    def test_proot_bind_mount(self):
        """Test bind mount addition"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")

        container.add_bind_mount("/host/path", "/container/path")

        assert len(container.bind_mounts) == 1
        assert container.bind_mounts[0]["host"] == "/host/path"
        assert container.bind_mounts[0]["container"] == "/container/path"

    def test_proot_bind_mount_fails_when_running(self):
        """Test bind mount fails when running"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")
        container.start()

        with pytest.raises(RuntimeError, match="Cannot add bind mount"):
            container.add_bind_mount("/host/path", "/container/path")

    def test_proot_environment_variables(self):
        """Test environment variable setting"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")

        container.set_environment("PATH", "/usr/bin:/bin")
        container.set_environment("HOME", "/root")

        assert container.environment["PATH"] == "/usr/bin:/bin"
        assert container.environment["HOME"] == "/root"

    def test_proot_working_directory(self):
        """Test working directory setting"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")

        container.set_working_dir("/home/user")
        assert container.working_dir == "/home/user"

    def test_proot_command_execution(self):
        """Test command execution in container"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")
        container.start()

        result = container.execute("ls -la")

        assert result["exit_code"] == 0
        assert "ls -la" in result["stdout"]

    def test_proot_execution_fails_when_not_running(self):
        """Test execution fails when not running"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")

        with pytest.raises(RuntimeError, match="not running"):
            container.execute("ls")

    def test_proot_container_info(self):
        """Test container info retrieval"""
        container = MockPRootContainer("test_container_1", "/path/to/rootfs")
        container.add_bind_mount("/host", "/container")
        container.set_working_dir("/app")

        info = container.get_info()

        assert info["container_id"] == "test_container_1"
        assert info["type"] == "proot"
        assert info["rootfs"] == "/path/to/rootfs"
        assert info["bind_mounts"] == 1
        assert info["working_dir"] == "/app"


class TestVMNetworkIsolation:
    """Test VM network isolation"""

    def test_network_isolation_initialization(self):
        """Test network isolation initialization"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        assert isolation.network_isolated is False
        assert isolation.disk_isolated is True
        assert len(isolation.allowed_hosts) == 0

    def test_enable_network_isolation(self):
        """Test enabling network isolation"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        isolation.enable_network_isolation()
        assert isolation.network_isolated is True

    def test_disable_network_isolation(self):
        """Test disabling network isolation"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        isolation.enable_network_isolation()
        isolation.disable_network_isolation()
        assert isolation.network_isolated is False

    def test_add_allowed_host(self):
        """Test adding host to allowlist"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        isolation.add_allowed_host("example.com")
        isolation.add_allowed_host("api.example.com")

        assert len(isolation.allowed_hosts) == 2
        # lgtm[py/incomplete-url-substring-sanitization] - Checking set membership, not URL validation
        assert "example.com" in isolation.allowed_hosts

    def test_remove_allowed_host(self):
        """Test removing host from allowlist"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        isolation.add_allowed_host("example.com")
        isolation.remove_allowed_host("example.com")

        assert len(isolation.allowed_hosts) == 0

    def test_check_network_access_without_isolation(self):
        """Test network access check without isolation"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        assert isolation.check_network_access("any.host.com") is True

    def test_check_network_access_with_isolation(self):
        """Test network access check with isolation"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        isolation.enable_network_isolation()
        isolation.add_allowed_host("allowed.com")

        assert isolation.check_network_access("allowed.com") is True
        assert isolation.check_network_access("blocked.com") is False

    def test_disk_isolation_enabled_by_default(self):
        """Test disk isolation is enabled by default"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        assert isolation.disk_isolated is True

    def test_get_isolation_status(self):
        """Test getting isolation status"""
        vm = MockQEMUVM("test_vm_1")
        isolation = MockVMIsolation(vm)

        isolation.enable_network_isolation()
        isolation.add_allowed_host("example.com")

        status = isolation.get_isolation_status()

        assert status["network_isolated"] is True
        assert status["disk_isolated"] is True
        assert len(status["allowed_hosts"]) == 1


class TestVMManager:
    """Test VM manager functionality"""

    def test_vm_manager_creation(self):
        """Test VM manager creation"""
        manager = MockVMManager()
        assert len(manager.vms) == 0

    def test_create_qemu_vm(self):
        """Test creating QEMU VM"""
        manager = MockVMManager()

        vm = manager.create_qemu_vm(VMType.QEMU_TCG)

        assert vm is not None
        assert isinstance(vm, MockQEMUVM)
        assert len(manager.vms) == 1

    def test_create_proot_container(self):
        """Test creating PRoot container"""
        manager = MockVMManager()

        container = manager.create_proot_container("/path/to/rootfs")

        assert container is not None
        assert isinstance(container, MockPRootContainer)
        assert len(manager.vms) == 1

    def test_get_vm(self):
        """Test getting VM by ID"""
        manager = MockVMManager()
        vm = manager.create_qemu_vm()

        retrieved_vm = manager.get_vm(vm.vm_id)

        assert retrieved_vm is vm

    def test_list_vms(self):
        """Test listing all VMs"""
        manager = MockVMManager()

        vm1 = manager.create_qemu_vm()
        vm2 = manager.create_qemu_vm()
        container = manager.create_proot_container("/path")

        vm_list = manager.list_vms()

        assert len(vm_list) == 3
        assert vm1.vm_id in vm_list
        assert vm2.vm_id in vm_list
        assert container.container_id in vm_list

    def test_delete_vm(self):
        """Test deleting VM"""
        manager = MockVMManager()
        vm = manager.create_qemu_vm()

        result = manager.delete_vm(vm.vm_id)

        assert result is True
        assert len(manager.vms) == 0

    def test_delete_running_vm_stops_first(self):
        """Test deleting running VM stops it first"""
        manager = MockVMManager()
        vm = manager.create_qemu_vm()
        vm.start()

        manager.delete_vm(vm.vm_id)

        assert vm.state == VMState.STOPPED

    def test_get_all_vm_info(self):
        """Test getting info for all VMs"""
        manager = MockVMManager()

        manager.create_qemu_vm()
        manager.create_proot_container("/path")

        all_info = manager.get_all_vm_info()

        assert len(all_info) == 2
        assert all(isinstance(info, dict) for info in all_info)


class TestVMSnapshot:
    """Test VM snapshot functionality"""

    def test_snapshot_creation(self):
        """Test snapshot creation"""
        vm = MockQEMUVM("test_vm_1")
        snapshots = MockVMSnapshot(vm)

        snapshot_id = snapshots.create_snapshot("snapshot1")

        assert snapshot_id is not None
        assert len(snapshots.snapshots) == 1

    def test_snapshot_restore(self):
        """Test snapshot restoration"""
        vm = MockQEMUVM("test_vm_1")
        snapshots = MockVMSnapshot(vm)

        snapshot_id = snapshots.create_snapshot("snapshot1")
        result = snapshots.restore_snapshot(snapshot_id)

        assert result is True

    def test_snapshot_restore_fails_if_not_exists(self):
        """Test snapshot restore fails if snapshot doesn't exist"""
        vm = MockQEMUVM("test_vm_1")
        snapshots = MockVMSnapshot(vm)

        with pytest.raises(ValueError, match="not found"):
            snapshots.restore_snapshot("nonexistent")

    def test_snapshot_deletion(self):
        """Test snapshot deletion"""
        vm = MockQEMUVM("test_vm_1")
        snapshots = MockVMSnapshot(vm)

        snapshot_id = snapshots.create_snapshot("snapshot1")
        result = snapshots.delete_snapshot(snapshot_id)

        assert result is True
        assert len(snapshots.snapshots) == 0

    def test_list_snapshots(self):
        """Test listing snapshots"""
        vm = MockQEMUVM("test_vm_1")
        snapshots = MockVMSnapshot(vm)

        snapshots.create_snapshot("snapshot1")
        snapshots.create_snapshot("snapshot2")

        snapshot_list = snapshots.list_snapshots()

        assert len(snapshot_list) == 2
        assert all("name" in s for s in snapshot_list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
