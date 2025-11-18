# KVM Acceleration Requirements Specification

## Hardware Requirements

### Minimum Requirements
- **CPU**: ARM64 with Virtualization Extensions (ARMv8.0-A or later)
- **RAM**: 8GB total (6GB available after OS)
- **Storage**: 2GB free for kernel modules and QEMU binaries
- **SoC Features**:
  - SMMU/IOMMU support
  - GICv3 or later (for interrupt virtualization)
  - Hardware timers with virtualization support

### Recommended Requirements
- **CPU**: ARMv9.2-A (Snapdragon 8 Gen 3, Dimensity 9300)
- **RAM**: 12GB or more
- **Storage**: 4GB+ free for VM images
- **SoC Features**:
  - Memory Tagging Extension (MTE)
  - Pointer Authentication (PAuth)
  - Branch Target Identification (BTI)

### Tested Devices
- ✅ Motorola Edge 2025 (Snapdragon 8 Gen 3)
- ⏳ Google Pixel 9 Pro (Tensor G4) - planned
- ⏳ OnePlus 13 (Snapdragon 8 Gen 4) - future
- ❌ Older devices (Snapdragon 8 Gen 1/2) - may work with reduced features

## Software Requirements

### Kernel Configuration
```bash
CONFIG_KVM=y
CONFIG_KVM_ARM_HOST=y
CONFIG_KVM_ARM_PMU=y
CONFIG_VHOST=y
CONFIG_VHOST_NET=y
CONFIG_VHOST_VSOCK=y
CONFIG_VHOST_CROSS_ENDIAN_LEGACY=n  # Not needed for ARM64
CONFIG_TUN=y
CONFIG_MACVTAP=y
CONFIG_HUGETLBFS=y
CONFIG_HUGETLB_PAGE=y
CONFIG_TRANSPARENT_HUGEPAGE=y
```

### QEMU Version
- Minimum: QEMU 7.0
- Recommended: QEMU 8.0+
- Required features:
  - ARM64 KVM support (`-accel kvm`)
  - VirtIO 1.1+ devices
  - Multi-core guest support
  - vhost-net backend

### Hypervisor Control Plane
- Python 3.10+ (for control scripts)
- libvirt 9.0+ (optional, for advanced management)
- virsh CLI tools (optional)

## Performance Requirements

### Target Metrics

**VM Startup Time**
- Cold boot (from shutdown): <2 seconds to shell prompt
- Warm boot (from suspend): <500ms to resume
- Disposable VM creation: <1 second

**CPU Performance** (compared to native execution)
- Single-threaded integer: ≥90%
- Multi-threaded workloads: ≥85%
- Floating-point operations: ≥85%
- Cryptographic operations: ≥80% (without hardware offload)

**Memory Performance**
- Read latency: <120% of native
- Write latency: <130% of native
- Memory bandwidth: ≥75% of native

**I/O Performance**
- VirtIO block read: ≥500 MB/s
- VirtIO block write: ≥300 MB/s
- VirtIO network: ≥800 Mbps throughput
- Latency overhead: <5ms for VirtIO operations

**Power Efficiency**
- Idle VM power draw: <100mW per VM
- Active VM power draw: <1.5W per VM under load
- Battery life impact: <15% additional drain with 3 VMs running

### Benchmark Suite
1. **UnixBench**: Overall system performance
2. **sysbench**: CPU, memory, I/O tests
3. **stress-ng**: Sustained load testing
4. **iperf3**: Network throughput (VirtIO-net)
5. **fio**: Disk I/O (VirtIO-blk)

## Security Requirements

### Mandatory Features
1. **Memory Isolation**: Stage-2 translation must prevent cross-VM memory access
2. **CPU Isolation**: vCPU scheduling must not leak timing information
3. **Interrupt Isolation**: Virtual GIC must prevent interrupt injection attacks
4. **Device Isolation**: SMMU must enforce DMA restrictions

### Hardening Requirements
- Enable Kernel Page Table Isolation (KPTI)
- Use Spectre-v2 mitigations (retpolines, IBPB)
- Enable Control Flow Integrity (CFI) if supported
- Disable KVM debugging interfaces in production builds

### Attack Surface Reduction
- Minimize `/dev/kvm` access (only hypervisor process)
- Use seccomp to restrict KVM ioctl surface
- SELinux strict mode for KVM device access
- Audit all KVM-related kernel modules

## Compatibility Requirements

### Fallback Support
- Automatic detection of KVM availability
- Graceful fallback to QEMU TCG (software emulation) if KVM unavailable
- User notification when running without acceleration
- Performance warning for non-KVM mode

### Cross-Device Compatibility
- VM images must be portable between KVM/non-KVM devices
- Configuration files should auto-detect acceleration capability
- No hard dependency on KVM (optional optimization only)

### Migration Path
- VMs created without KVM must boot with KVM enabled
- Settings migration for upgrading from non-accelerated builds
- Backward compatibility with Phase 3 hypervisor implementation

## Testing Requirements

### Functional Tests
- ✅ `/dev/kvm` device creation
- ✅ KVM module loading/unloading
- ✅ vCPU creation and scheduling
- ✅ Memory allocation and mapping
- ✅ VirtIO device initialization
- ✅ Multi-VM concurrent execution

### Performance Tests
- ✅ Baseline benchmarks (no KVM)
- ✅ Accelerated benchmarks (with KVM)
- ✅ Comparison to native execution
- ✅ Power consumption measurement
- ✅ Thermal throttling behavior

### Security Tests
- ✅ VM escape attempts (known CVEs)
- ✅ Memory isolation verification
- ✅ Side-channel attack resistance
- ✅ Hypervisor fuzzing (syzkaller)

### Regression Tests
- ✅ Phase 3 hypervisor still works
- ✅ Tor Gateway VM boots and routes traffic
- ✅ Workstation VM isolation maintained
- ✅ Post-quantum crypto performance unchanged

## Documentation Requirements

### User Documentation
1. **Setup Guide**: How to verify KVM support on device
2. **Performance Guide**: Expected speedups and battery savings
3. **Troubleshooting**: Common issues and solutions
4. **FAQ**: "Why isn't KVM working on my device?"

### Developer Documentation
1. **Architecture Overview**: How KVM integrates with hypervisor
2. **API Reference**: Control plane functions for KVM management
3. **Kernel Configuration**: Required config options and modules
4. **Debugging Guide**: How to diagnose KVM issues

### Deployment Documentation
1. **Build Instructions**: Compiling kernel with KVM support
2. **Installation Steps**: Loading modules and configuring permissions
3. **Verification Steps**: Testing KVM acceleration
4. **Rollback Procedure**: Reverting to non-KVM build if needed

## Success Criteria

### Phase XII is complete when:
- ✅ KVM kernel modules compile and load on Snapdragon 8 Gen 3
- ✅ All existing VMs boot with KVM acceleration enabled
- ✅ Performance benchmarks show ≥85% native CPU performance
- ✅ VM startup time reduced to <2 seconds
- ✅ Power consumption reduced by ≥40% vs software emulation
- ✅ Security audit passes (no new attack surface introduced)
- ✅ Fallback to non-KVM mode works automatically
- ✅ All Phase 3 hypervisor tests still pass
- ✅ Documentation complete and reviewed

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Status:** Planning - Pending Implementation
