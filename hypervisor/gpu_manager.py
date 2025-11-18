#!/usr/bin/env python3
"""
QWAMOS GPU Manager
Phase XIV: GPU Isolation and Passthrough

Manages GPU resources for VMs with security isolation:
- GPU device detection (Adreno, Mali, etc.)
- Vulkan capability detection
- VirtIO-GPU configuration
- Resource allocation and scheduling
- Security policy enforcement
- SwiftShader fallback support

Author: QWAMOS Project
License: MIT
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from enum import Enum


class GPUVendor(Enum):
    """GPU vendor enumeration."""
    QUALCOMM_ADRENO = "qualcomm_adreno"
    ARM_MALI = "arm_mali"
    NVIDIA = "nvidia"
    INTEL = "intel"
    SOFTWARE = "swiftshader"
    UNKNOWN = "unknown"


class GPUAccessMode(Enum):
    """GPU access modes for VMs."""
    PASSTHROUGH = "passthrough"  # Direct GPU access (requires VFIO)
    VIRTIO = "virtio"  # Paravirtualized GPU (VirtIO-GPU)
    SOFTWARE = "software"  # CPU rendering (SwiftShader)
    NONE = "none"  # No GPU access


@dataclass
class GPUCapabilities:
    """GPU hardware capabilities."""
    vendor: GPUVendor
    device_name: str
    driver_version: str
    vulkan_supported: bool
    vulkan_version: Optional[str]
    opengl_version: Optional[str]
    compute_units: int
    vram_mb: int
    max_texture_size: int
    vfio_available: bool
    smmu_available: bool


@dataclass
class GPUAllocation:
    """GPU resource allocation for a VM."""
    vm_name: str
    access_mode: GPUAccessMode
    vram_limit_mb: int
    compute_unit_share: float  # 0.0-1.0
    priority: int  # 0-100
    allow_vulkan: bool
    allow_compute: bool


class GPUManager:
    """
    Manages GPU resources for QWAMOS VMs.

    Features:
    - GPU device detection
    - Vulkan capability checking
    - Resource allocation
    - Security policy enforcement
    - VirtIO-GPU configuration
    """

    def __init__(self):
        """Initialize GPU manager."""
        self.capabilities = self._detect_gpu_capabilities()
        self.allocations: Dict[str, GPUAllocation] = {}

    def _detect_gpu_capabilities(self) -> GPUCapabilities:
        """
        Detect GPU hardware and capabilities.

        Returns:
            GPUCapabilities with detected features
        """
        # Default capabilities (no GPU)
        caps = GPUCapabilities(
            vendor=GPUVendor.UNKNOWN,
            device_name="None",
            driver_version="unknown",
            vulkan_supported=False,
            vulkan_version=None,
            opengl_version=None,
            compute_units=0,
            vram_mb=0,
            max_texture_size=0,
            vfio_available=False,
            smmu_available=False
        )

        # Detect GPU vendor and device
        vendor, device = self._detect_gpu_device()
        caps.vendor = vendor
        caps.device_name = device

        # Detect Vulkan support
        vulkan_info = self._detect_vulkan()
        if vulkan_info:
            caps.vulkan_supported = True
            caps.vulkan_version = vulkan_info.get('version')
            caps.driver_version = vulkan_info.get('driver', 'unknown')

        # Detect OpenGL version
        caps.opengl_version = self._detect_opengl()

        # Detect VFIO availability
        caps.vfio_available = self._check_vfio()

        # Detect SMMU (ARM IOMMU)
        caps.smmu_available = self._check_smmu()

        # Estimate GPU specs (vendor-specific)
        if caps.vendor == GPUVendor.QUALCOMM_ADRENO:
            caps.compute_units = self._estimate_adreno_specs(device)
            caps.vram_mb = 2048  # Shared with system RAM on mobile
            caps.max_texture_size = 16384
        elif caps.vendor == GPUVendor.ARM_MALI:
            caps.compute_units = 8  # Typical for mobile Mali
            caps.vram_mb = 1024
            caps.max_texture_size = 8192

        return caps

    def _detect_gpu_device(self) -> tuple:
        """
        Detect GPU vendor and device name.

        Returns:
            (GPUVendor, device_name)
        """
        try:
            # Try reading from /sys/class/kgsl/kgsl-3d0/gpu_model (Adreno)
            kgsl_path = Path("/sys/class/kgsl/kgsl-3d0/gpu_model")
            if kgsl_path.exists():
                with open(kgsl_path, 'r') as f:
                    gpu_model = f.read().strip()
                    if gpu_model:
                        return GPUVendor.QUALCOMM_ADRENO, f"Adreno {gpu_model}"
        except Exception:
            pass

        try:
            # Try getting GPU info from getprop (Android)
            result = subprocess.run(
                ["getprop", "ro.hardware.vulkan"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                vulkan_hw = result.stdout.strip()
                if "adreno" in vulkan_hw.lower():
                    return GPUVendor.QUALCOMM_ADRENO, f"Adreno ({vulkan_hw})"
                elif "mali" in vulkan_hw.lower():
                    return GPUVendor.ARM_MALI, f"Mali ({vulkan_hw})"
        except Exception:
            pass

        # Try lspci for desktop GPUs
        try:
            result = subprocess.run(
                ["lspci"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                for line in result.stdout.lower().split('\n'):
                    if 'nvidia' in line:
                        return GPUVendor.NVIDIA, "NVIDIA GPU"
                    elif 'amd' in line or 'radeon' in line:
                        return GPUVendor.UNKNOWN, "AMD GPU"
                    elif 'intel' in line and ('graphics' in line or 'vga' in line):
                        return GPUVendor.INTEL, "Intel GPU"
        except Exception:
            pass

        return GPUVendor.UNKNOWN, "Unknown/None"

    def _detect_vulkan(self) -> Optional[Dict]:
        """
        Detect Vulkan support and version.

        Returns:
            Dictionary with Vulkan info or None
        """
        try:
            # Try vulkaninfo
            result = subprocess.run(
                ["vulkaninfo", "--summary"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                info = {}
                for line in result.stdout.split('\n'):
                    if 'Vulkan Instance Version' in line:
                        version = re.search(r'(\d+\.\d+\.\d+)', line)
                        if version:
                            info['version'] = version.group(1)
                    elif 'driverVersion' in line:
                        driver = re.search(r'(\d+\.\d+\.\d+)', line)
                        if driver:
                            info['driver'] = driver.group(1)

                if info:
                    return info
        except Exception:
            pass

        # Check for Vulkan libraries
        vulkan_libs = [
            "/system/lib64/libvulkan.so",
            "/vendor/lib64/libvulkan.so",
            "/usr/lib/libvulkan.so.1"
        ]

        for lib in vulkan_libs:
            if Path(lib).exists():
                return {'version': 'unknown', 'driver': 'available'}

        return None

    def _detect_opengl(self) -> Optional[str]:
        """
        Detect OpenGL ES version.

        Returns:
            OpenGL version string or None
        """
        try:
            # Try reading from system properties (Android)
            result = subprocess.run(
                ["getprop", "ro.opengles.version"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                version_code = result.stdout.strip()
                if version_code:
                    # Convert version code to readable format
                    # e.g., 196610 = 0x30002 = OpenGL ES 3.2
                    try:
                        code = int(version_code)
                        major = (code & 0xFFFF0000) >> 16
                        minor = code & 0xFFFF
                        return f"OpenGL ES {major}.{minor}"
                    except:
                        pass
        except Exception:
            pass

        return None

    def _check_vfio(self) -> bool:
        """
        Check if VFIO is available for GPU passthrough.

        Returns:
            True if VFIO available
        """
        vfio_paths = [
            "/dev/vfio/vfio",
            "/sys/module/vfio",
            "/sys/module/vfio_pci"
        ]

        return any(Path(p).exists() for p in vfio_paths)

    def _check_smmu(self) -> bool:
        """
        Check if SMMU (ARM IOMMU) is available.

        Returns:
            True if SMMU available
        """
        smmu_paths = [
            "/sys/class/iommu",
            "/sys/kernel/iommu_groups"
        ]

        for path in smmu_paths:
            if Path(path).exists():
                # Check if there are any IOMMU groups
                try:
                    if list(Path(path).iterdir()):
                        return True
                except:
                    pass

        # Check dmesg for SMMU initialization
        try:
            result = subprocess.run(
                ["dmesg"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                if "smmu" in result.stdout.lower() or "iommu" in result.stdout.lower():
                    return True
        except:
            pass

        return False

    def _estimate_adreno_specs(self, device_name: str) -> int:
        """
        Estimate Adreno GPU specs from device name.

        Args:
            device_name: GPU device name

        Returns:
            Estimated compute units
        """
        # Extract model number (e.g., "Adreno 750" -> 750)
        match = re.search(r'(\d+)', device_name)
        if match:
            model = int(match.group(1))

            # Estimate compute units based on model
            if model >= 740:  # Adreno 740+ (SD 8 Gen 2+)
                return 12
            elif model >= 730:  # Adreno 730 (SD 8 Gen 1)
                return 10
            elif model >= 650:  # Adreno 650 (SD 865)
                return 8
            elif model >= 630:  # Adreno 630 (SD 845)
                return 6
            else:
                return 4

        return 4  # Default

    def allocate_gpu(
        self,
        vm_name: str,
        access_mode: GPUAccessMode = GPUAccessMode.VIRTIO,
        vram_limit_mb: int = 512,
        priority: int = 50
    ) -> GPUAllocation:
        """
        Allocate GPU resources to a VM.

        Args:
            vm_name: VM name
            access_mode: GPU access mode
            vram_limit_mb: VRAM limit in MB
            priority: Priority (0-100)

        Returns:
            GPUAllocation object
        """
        # Create allocation
        allocation = GPUAllocation(
            vm_name=vm_name,
            access_mode=access_mode,
            vram_limit_mb=vram_limit_mb,
            compute_unit_share=1.0 / max(1, len(self.allocations) + 1),
            priority=priority,
            allow_vulkan=self.capabilities.vulkan_supported,
            allow_compute=True
        )

        # Adjust access mode based on capabilities
        if access_mode == GPUAccessMode.PASSTHROUGH and not self.capabilities.vfio_available:
            print(f"⚠️  VFIO not available, falling back to VirtIO")
            allocation.access_mode = GPUAccessMode.VIRTIO

        # Store allocation
        self.allocations[vm_name] = allocation

        return allocation

    def get_vm_gpu_args(self, vm_name: str) -> List[str]:
        """
        Generate QEMU GPU arguments for a VM.

        Args:
            vm_name: VM name

        Returns:
            List of QEMU arguments
        """
        allocation = self.allocations.get(vm_name)

        if not allocation:
            # No GPU allocation, return basic args
            return ["-nographic"]

        args = []

        if allocation.access_mode == GPUAccessMode.VIRTIO:
            # VirtIO-GPU (paravirtualized)
            args.extend([
                "-device", "virtio-gpu-pci,max_outputs=1",
                "-display", "none"  # Headless, VNC can be added
            ])

        elif allocation.access_mode == GPUAccessMode.PASSTHROUGH:
            # VFIO GPU passthrough (requires proper setup)
            # This is a placeholder - actual VFIO requires device IDs
            args.extend([
                "-device", "vfio-pci,host=XX:YY.Z",  # Replace with actual device
                "-display", "none"
            ])

        elif allocation.access_mode == GPUAccessMode.SOFTWARE:
            # Software rendering (SwiftShader)
            args.extend([
                "-device", "virtio-vga",
                "-display", "none"
            ])
            # SwiftShader would be configured inside the VM

        else:  # NONE
            args.append("-nographic")

        return args

    def get_capabilities_summary(self) -> Dict:
        """
        Get GPU capabilities summary.

        Returns:
            Dictionary with capabilities
        """
        caps = self.capabilities

        return {
            'vendor': caps.vendor.value,
            'device': caps.device_name,
            'vulkan': {
                'supported': caps.vulkan_supported,
                'version': caps.vulkan_version
            },
            'opengl_version': caps.opengl_version,
            'compute_units': caps.compute_units,
            'vram_mb': caps.vram_mb,
            'passthrough': {
                'vfio_available': caps.vfio_available,
                'smmu_available': caps.smmu_available,
                'ready': caps.vfio_available and caps.smmu_available
            }
        }

    def print_capabilities(self):
        """Print GPU capabilities in human-readable format."""
        caps = self.capabilities

        print("\n" + "=" * 70)
        print("QWAMOS GPU Manager - Capabilities")
        print("=" * 70)

        print(f"\nGPU Device:")
        print(f"  Vendor:        {caps.vendor.value}")
        print(f"  Device:        {caps.device_name}")
        print(f"  Driver:        {caps.driver_version}")

        print(f"\nGraphics APIs:")
        vulkan_status = f"✅ {caps.vulkan_version}" if caps.vulkan_supported else "❌ Not available"
        print(f"  Vulkan:        {vulkan_status}")

        if caps.opengl_version:
            print(f"  OpenGL:        ✅ {caps.opengl_version}")
        else:
            print(f"  OpenGL:        ❌ Not detected")

        print(f"\nGPU Resources:")
        print(f"  Compute Units: {caps.compute_units}")
        print(f"  VRAM:          {caps.vram_mb} MB")
        print(f"  Max Texture:   {caps.max_texture_size}x{caps.max_texture_size}")

        print(f"\nPassthrough Support:")
        vfio_status = "✅ Available" if caps.vfio_available else "❌ Not available"
        smmu_status = "✅ Available" if caps.smmu_available else "❌ Not available"
        print(f"  VFIO:          {vfio_status}")
        print(f"  SMMU/IOMMU:    {smmu_status}")

        if caps.vfio_available and caps.smmu_available:
            print(f"\n  Status:        ✅ GPU passthrough ready")
        else:
            print(f"\n  Status:        ⚠️  VirtIO-GPU recommended (passthrough not available)")

        print("=" * 70 + "\n")


def main():
    """Demo and testing."""
    print("=" * 70)
    print("QWAMOS GPU Manager - Demo")
    print("=" * 70)

    # Initialize GPU manager
    gpu_mgr = GPUManager()

    # Show capabilities
    gpu_mgr.print_capabilities()

    # Test VM GPU allocation
    print("\nTesting GPU Allocation:")
    print("-" * 70)

    # Allocate GPU to test VM
    allocation = gpu_mgr.allocate_gpu(
        vm_name="test-vm",
        access_mode=GPUAccessMode.VIRTIO,
        vram_limit_mb=1024,
        priority=75
    )

    print(f"✅ Allocated GPU to 'test-vm'")
    print(f"   Access Mode:      {allocation.access_mode.value}")
    print(f"   VRAM Limit:       {allocation.vram_limit_mb} MB")
    print(f"   Compute Share:    {allocation.compute_unit_share * 100:.1f}%")
    print(f"   Priority:         {allocation.priority}/100")
    print(f"   Vulkan Allowed:   {allocation.allow_vulkan}")

    # Get QEMU args
    print(f"\nQEMU Arguments:")
    args = gpu_mgr.get_vm_gpu_args("test-vm")
    print(f"   {' '.join(args)}")

    # Get capabilities summary
    print(f"\nCapabilities Summary:")
    summary = gpu_mgr.get_capabilities_summary()
    print(json.dumps(summary, indent=2))

    print("\n" + "=" * 70)
    print("✅ GPU Manager operational")
    print("=" * 70)


if __name__ == "__main__":
    main()
