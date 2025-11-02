# Contributing to QWAMOS

## Code Quality Requirements

1. **Signed Commits**: All commits MUST be GPG-signed
   ```bash
   git config user.signingkey YOUR_GPG_KEY_ID
   git commit -S -m "Your commit message"
   ```

2. **GPG Setup**:
   ```bash
   gpg --gen-key
   gpg --list-secret-keys --keyid-format LONG
   gpg --armor --export YOUR_KEY_ID | clip
   # Add to GitHub: Settings → SSH and GPG keys
   ```

3. **Lint Requirements**:
   - Python: `python3 -m py_compile file.py`
   - Shell: `shellcheck script.sh`

4. **Testing**:
   - All tests must pass before PR
   - Add tests for new features

## CI Requirements

- GitHub Actions must pass
- No merge without green CI

## Code Review

- All PRs require 1 approval
- Security-sensitive PRs require 2 approvals

## License

By contributing, you agree to license your code under the project license.
