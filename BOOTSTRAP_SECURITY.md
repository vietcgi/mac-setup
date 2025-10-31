# Bootstrap Script Security

## CRITICAL SECURITY: Checksum Verification

The Devkit bootstrap script includes built-in integrity verification to protect against supply chain attacks (e.g., man-in-the-middle attacks on GitHub).

### Current Bootstrap Checksum

```
SHA256: dbc6106138b9c9c1b349d8e047465e33e4ec0bd175363131ed97423458a0ec1c
```

This checksum is automatically verified when:

- Running the bootstrap script with `DEVKIT_BOOTSTRAP_CHECKSUM` environment variable set
- Publishing a new release (CI/CD updates this automatically)

### How It Works

1. **For Users (Safe Usage)**

   ```bash
   # Download and run with checksum verification
   export DEVKIT_BOOTSTRAP_CHECKSUM="dbc6106138b9c9c1b349d8e047465e33e4ec0bd175363131ed97423458a0ec1c"
   curl -fsSL https://raw.githubusercontent.com/vietcgi/devkit/main/bootstrap.sh | bash
   ```

2. **For Local Development (No Verification)**

   ```bash
   # Run locally without checksum (development mode)
   ./bootstrap.sh
   ```

3. **For CI/CD (Automated)**
   - GitHub Actions automatically updates checksum on release
   - Each version gets unique checksum in release notes
   - Users can verify before running

### Verification in bootstrap.sh

The script:

1. Checks if `DEVKIT_BOOTSTRAP_CHECKSUM` environment variable is set
2. If set, computes SHA256 of the actual script
3. Compares with expected value
4. Aborts if checksums don't match (FAIL SECURE)
5. Logs detailed error messages to help users diagnose issues

### Security Guarantees

✅ **Supply Chain Attack Prevention**

- Detects man-in-the-middle attacks on GitHub
- Detects script tampering during download
- Detects corrupted downloads

✅ **Fail Secure**

- Always aborts if checksum fails
- Never silently proceeds with mismatched checksums
- Clear error messages for troubleshooting

⚠️ **Current Limitations**

- Only works when checksum is set (opt-in for users)
- Doesn't prevent compromised GitHub account attacks
- Requires users to verify checksum before running

### How to Update Checksum (CI/CD)

**For Release Process:**

1. When creating a new release, run:

   ```bash
   sha256sum bootstrap.sh
   ```

2. Update release notes with the new checksum

3. Add to release body:

   ```
   **Security: Verify Bootstrap Script Integrity**

   SHA256: <NEW_CHECKSUM>

   Verification:
   export DEVKIT_BOOTSTRAP_CHECKSUM="<NEW_CHECKSUM>"
   curl -fsSL https://raw.githubusercontent.com/vietcgi/devkit/main/bootstrap.sh | bash
   ```

4. GitHub Actions should automatically update this for releases

### Testing Checksum Verification

```bash
# Test 1: Correct checksum (should succeed)
export DEVKIT_BOOTSTRAP_CHECKSUM="dbc6106138b9c9c1b349d8e047465e33e4ec0bd175363131ed97423458a0ec1c"
./bootstrap.sh --verify-only

# Test 2: Wrong checksum (should fail with security error)
export DEVKIT_BOOTSTRAP_CHECKSUM="0000000000000000000000000000000000000000000000000000000000000000"
./bootstrap.sh --verify-only
# Should output: "SECURITY WARNING: Script may have been tampered with"

# Test 3: Development mode (no checksum, should skip verification)
unset DEVKIT_BOOTSTRAP_CHECKSUM
./bootstrap.sh --verify-only
# Should output: "Bootstrap integrity check skipped (development mode)"
```

### Related Files

- **bootstrap.sh** - Main bootstrap script with checksum verification (lines 41-156)
- **bootstrap-ansible.sh** - Alternative Ansible-specific bootstrap
- **.github/workflows/release.yml** - Automates checksum generation on releases

### Future Improvements

1. **Public Key Infrastructure (PKI)**
   - Sign bootstrap script with project key
   - Users verify signature instead of checksum
   - Better protection against GitHub compromise

2. **Automation**
   - GitHub Actions auto-updates checksum in documentation
   - Auto-generates release notes with checksum
   - Auto-sends checksum to official website

3. **User Experience**
   - One-liner with built-in verification
   - Check checksum before executing
   - Clear security status indicators

### Security Contact

If you discover a security issue in Devkit:

- **DO NOT** create a public GitHub issue
- Email: <security@devkit.example.com>
- See SECURITY.md for vulnerability reporting process

---

**Implementation Date:** October 30, 2025
**Checksum Last Updated:** October 30, 2025
**Status:** ✅ ACTIVE - Verification enabled
