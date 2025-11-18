# GPU Isolation Architecture Design

## Security Model

### Threat Scenarios

1. **Malicious VM Exploits GPU Driver**: VM escapes to host via GPU driver vulnerability
2. **Cross-VM GPU Spying**: VM reads another VM's GPU memory or framebuffer
3. **GPU Timing Attacks**: VM infers secrets by measuring GPU operation latency
4. **DMA Attacks**: GPU performs unauthorized memory access via DMA

### Mitigation Strategies

| Threat | Mitigation | Implementation |
|--------|-----------|----------------|
| Driver Exploit | Vulkan proxy sanitization | Validate all API calls before GPU submission |
| Cross-VM Spying | Memory scrubbing | Zero GPU memory on context switch |
| Timing Attacks | Constant-time execution | Add random delays to GPU operations |
| DMA Attacks | SMMU enforcement | IOMMU restricts GPU memory access |

## GPU Passthrough Options

### Option 1: Full GPU Passthrough (VFIO)

**Advantages**: Maximum performance, full GPU features
**Disadvantages**: Only one VM can use GPU at a time, complex driver requirements

### Option 2: VirtIO-GPU Paravirtualization

**Advantages**: Multiple VMs can share GPU, simpler implementation
**Disadvantages**: Lower performance, limited feature set

### Option 3: Vulkan Proxy (Recommended)

**Advantages**: Balance of performance and isolation, flexible security policies
**Disadvantages**: Requires custom Vulkan proxy development

## Vulkan Proxy Architecture

```
[VM Guest App]
      ↓
[Vulkan API Calls]
      ↓
[Vulkan Proxy (Host)] ← Validates and sanitizes
      ↓
[GPU Driver (Adreno)]
      ↓
[Adreno 750 GPU Hardware]
```

### Proxy Responsibilities

1. **API Validation**: Ensure Vulkan calls are well-formed
2. **Resource Limits**: Enforce VRAM and compute quotas per VM
3. **Command Sanitization**: Strip dangerous GPU commands
4. **Timing Obfuscation**: Add random delays to prevent timing leaks

## References

- [Qualcomm Adreno GPU Documentation](https://developer.qualcomm.com/software/adreno-gpu-sdk)
- [VirtIO-GPU Specification](https://docs.oasis-open.org/virtio/virtio/v1.1/virtio-v1.1.html)
- [VFIO GPU Passthrough Guide](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF)

---

**Last Updated:** 2025-11-17
