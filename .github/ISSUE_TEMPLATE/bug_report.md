---
name: Bug Report
about: Report a bug or unexpected behavior in QWAMOS
title: "[BUG] "
labels: bug
assignees: ''

---

## Bug Description

**Describe the bug**
A clear and concise description of what the bug is.

## Steps to Reproduce

Please provide detailed steps to reproduce the issue:

1. Go to '...'
2. Run command '...'
3. Start VM with '...'
4. See error

## Expected Behavior

What did you expect to happen?

## Actual Behavior

What actually happened instead?

## Environment Details

**Device Information:**
- Device Model: [e.g., Pixel 7 Pro, Samsung S23]
- Android Version: [e.g., Android 14]
- QWAMOS Version: [e.g., v1.2.0]
- Installation Method: [Termux / Rooted KVM / Custom ROM]
- Root Access: [Yes / No]
- KVM Available: [Yes / No]

**VM Configuration:**
- VM Mode Used: [QEMU / Chroot / PRoot / KVM]
- VM Name: [e.g., secure-browser]
- VM Type: [e.g., browser, messaging, development]
- RAM Allocated: [e.g., 2GB]
- Disk Size: [e.g., 10GB]

**Gateway Configuration:**
- Tor: [Enabled / Disabled]
- I2P: [Enabled / Disabled]
- DNSCrypt: [Enabled / Disabled]
- Gateway Mode: [Per-VM / Shared]

## Logs or Screenshots

**Error Logs:**
```bash
# Paste relevant error messages here
# Include output from:
./scripts/check_compatibility.sh
# Or VM startup logs:
cat ~/.qwamos/vms/vm-name/logs/startup.log
```

**Screenshots:**
If applicable, add screenshots to help explain your problem.

## Reproduction Rate

- [ ] Happens every time
- [ ] Happens sometimes (approximately __%)
- [ ] Happened only once

## Additional Context

Add any other context about the problem here:
- Were you doing anything specific when the bug occurred?
- Did this work in previous versions?
- Have you made any custom modifications?
- Any relevant configuration files or settings?

## Possible Solution (Optional)

If you have ideas on how to fix this, please share them here.

---

**Before submitting:**
- [ ] I have searched existing issues to avoid duplicates
- [ ] I have included all required environment details
- [ ] I have provided logs or error messages
- [ ] I have included steps to reproduce the issue

**Contact:** qwamos@tutanota.com
