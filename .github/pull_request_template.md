## Pull Request Title
<!-- Provide a clear, concise title following conventional commit format -->
<!-- Format: [TYPE] Brief description (50 chars max) -->
<!-- Example: [FEATURE] Add VeraCrypt hidden volume support -->

---

## Summary

<!-- Provide a brief 2-3 sentence summary of what this PR does and why it's needed -->



---

## Related Issues

<!-- Link related issues using #issue_number -->
<!-- Example: Fixes #123, See-Also #456 -->

- Fixes: #
- Related: #
- See-Also: #

---

## Description of Changes

### What changed?

<!-- Describe the technical changes you made -->
<!-- Be specific about which modules, files, or components were modified -->



### Why was this change needed?

<!-- Explain the motivation and context for this change -->
<!-- What problem does it solve? What feature does it add? -->



### How does it work?

<!-- Explain the implementation approach -->
<!-- Highlight any important architectural decisions -->



---

## Type of Change

<!-- Check all that apply -->

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 🔒 Security fix (addresses a security vulnerability)
- [ ] 📝 Documentation update (changes to README, Wiki, or code comments)
- [ ] 🎨 Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test additions or modifications
- [ ] 🔧 Build/tooling changes

---

## Testing Performed

### Test Environment

**Device**: <!-- e.g., Pixel 7 Pro, Samsung S23, Emulator -->
**Android Version**: <!-- e.g., Android 14 -->
**QWAMOS Version**: <!-- e.g., v1.2.0 or current dev branch -->
**Installation Method**: <!-- Termux / Rooted KVM / Custom ROM -->

### Tests Conducted

<!-- Describe what tests you performed to verify your changes -->
<!-- Include commands run and their results -->

**Unit Tests**:
```bash
# Example
pytest tests/test_your_module.py
```

**Integration Tests**:
```bash
# Example
pytest tests/integration/ --integration
```

**Manual Testing**:
<!-- Describe manual testing steps -->
1.
2.
3.

### VM Mode Testing

<!-- If this PR affects VM functionality, check all modes tested -->

- [ ] QEMU (software emulation) - Tested and working
- [ ] Chroot (namespace isolation) - Tested and working
- [ ] PRoot (userspace virtualization) - Tested and working
- [ ] KVM (hardware acceleration) - Tested and working
- [ ] N/A - This PR does not affect VM modes

**Test Commands**:
```bash
# Example VM testing commands
# ./scripts/create_vm.sh --name test-vm --backend qemu
# ./scripts/start_vm.sh test-vm
```

### Gateway Testing

<!-- If this PR affects networking, check all gateways tested -->

- [ ] Tor - Connectivity verified
- [ ] I2P - Connectivity verified
- [ ] DNSCrypt - DNS resolution verified
- [ ] N/A - This PR does not affect gateway functionality

**Test Commands**:
```bash
# Example gateway testing
# curl --socks5 127.0.0.1:9050 https://check.torproject.org
```

### Post-Quantum Cryptography

<!-- If this PR affects crypto modules, verify they still work -->

- [ ] Kyber-1024 - Key generation and encapsulation tested
- [ ] ChaCha20-Poly1305 - Encryption/decryption verified
- [ ] BLAKE3 - Hashing verified
- [ ] N/A - This PR does not affect PQC modules

**Test Commands**:
```bash
# Example crypto testing
# python3 -c "from qwamos.crypto.kyber import generate_keypair; ..."
```

---

## Screenshots

<!-- If this PR includes UI changes, add before/after screenshots -->
<!-- Delete this section if not applicable -->

### Before
<!-- Screenshot or description of UI before changes -->


### After
<!-- Screenshot or description of UI after changes -->


---

## Breaking Changes

<!-- If this PR introduces breaking changes, describe them here -->
<!-- Include migration instructions for users upgrading -->

- [ ] This PR introduces breaking changes
- [ ] Migration guide provided below

**Migration Guide**:
<!-- If breaking changes exist, provide clear migration steps -->



---

## Security Considerations

<!-- Describe any security implications of this change -->

- [ ] This PR has security implications (describe below)
- [ ] No security implications

**Security Impact**:
<!-- If applicable, describe:
     - What security aspects are affected
     - How vulnerabilities are mitigated
     - Any new attack surface introduced
     - Testing performed for security
-->



---

## Performance Impact

<!-- Describe any performance implications -->

- [ ] Performance improvement
- [ ] No significant performance change
- [ ] Performance regression (justified below)

**Performance Notes**:
<!-- If applicable, include benchmark results or performance analysis -->



---

## Pull Request Checklist

### Code Quality

- [ ] Code follows the style guidelines (PEP 8, 100 char line length)
- [ ] Code compiles/runs without errors
- [ ] All linters pass (`black`, `pylint`, `mypy`)
- [ ] Type hints included for all new functions
- [ ] Docstrings written for all new public methods
- [ ] No debug code or print statements left in

### Testing

- [ ] Unit tests added for new functionality
- [ ] All existing tests pass
- [ ] Integration tests pass (if applicable)
- [ ] VM isolation tested (if modifying VM code)
- [ ] Gateway connectivity tested (if modifying network code)
- [ ] PQC stack tested (if modifying crypto code)

### Documentation

- [ ] README.md updated (if adding major features)
- [ ] Wiki pages updated (if changing architecture or APIs)
- [ ] Code comments explain non-obvious logic
- [ ] Inline documentation is clear and accurate
- [ ] CHANGELOG.md updated (for releases)

### Security

- [ ] No sensitive information in code (passwords, keys, tokens)
- [ ] No sensitive information in commit history
- [ ] Security implications considered and documented
- [ ] No new security vulnerabilities introduced
- [ ] Security tests pass (if applicable)

### Git Hygiene

- [ ] Commit messages follow conventional format
- [ ] Branch is up to date with target branch (`dev` or `master`)
- [ ] No merge conflicts
- [ ] Commits are logically organized (squashed if needed)
- [ ] All commit messages are clear and descriptive

### QWAMOS-Specific

- [ ] VM modes tested (QEMU/Chroot/PRoot/KVM) - if applicable
- [ ] Gateway connectivity verified (Tor/I2P/DNSCrypt) - if applicable
- [ ] Post-quantum crypto modules unaffected or properly tested
- [ ] No breaking changes to VM isolation boundaries
- [ ] No breaking changes to cryptographic implementations
- [ ] Module interfaces remain backward compatible (or migration provided)

---

## Additional Notes

<!-- Any additional information reviewers should know -->
<!-- Context, design decisions, alternative approaches considered, etc. -->



---

## Reviewer Notes

<!-- Optional: Specific areas you'd like reviewers to focus on -->
<!-- Questions for reviewers, areas of uncertainty, etc. -->



---

## Post-Merge Tasks

<!-- If there are follow-up tasks after merge, list them here -->

- [ ] Update documentation website
- [ ] Announce in Discussions
- [ ] Update Roadmap wiki
- [ ] Create release notes
- [ ] Other: _________________

---

## Acknowledgments

<!-- Optional: Credit co-authors, helpers, or inspirations -->



---

**By submitting this PR, I confirm that**:
- [ ] I have read the [CONTRIBUTING.md](CONTRIBUTING.md) guide
- [ ] My contribution is my original work
- [ ] I agree to license this contribution under AGPL-3.0
- [ ] I have no conflicts of interest to disclose

---

**Questions?** Contact: qwamos@tutanota.com
**Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
**Developer Guide**: [Wiki](https://github.com/Dezirae-Stark/QWAMOS/wiki/Developer-Guide)
