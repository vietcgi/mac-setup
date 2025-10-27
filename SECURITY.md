# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 3.0.x   | :white_check_mark: |
| 2.0.x   | :x:                |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **Email**: Send details to the repository maintainer
2. **GitHub Security Advisories**: Use the [Security tab](../../security/advisories/new) in this repository

### What to Include

Please include the following information in your report:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours of report
- **Status Update**: Within 7 days with initial assessment
- **Fix Timeline**: Security fixes are prioritized and typically released within 30 days
- **Public Disclosure**: After fix is released and users have had time to update (minimum 7 days)

### Security Update Process

1. Security issue is reported privately
2. Issue is confirmed and severity assessed
3. Fix is developed in a private branch
4. Fix is tested and reviewed
5. Security advisory is prepared
6. Fix is released with security advisory
7. Public disclosure after users have time to update

## Security Best Practices

When using this setup, follow these security practices:

### 1. Keep Software Updated

```bash
# Run update script regularly
./update.sh

# Check for outdated packages
brew outdated
mise outdated
```

### 2. Review Installed Packages

Before running the setup, review:
- `Brewfile` - All packages that will be installed
- `Brewfile.sre` - SRE-specific packages
- `setup.yml` - Ansible tasks that will run

### 3. Sensitive Data Protection

- Never commit sensitive data (passwords, API keys, tokens)
- Use `.env.local` for local secrets (already in .gitignore)
- Review all dotfiles before applying with chezmoi
- Use vault or password managers for credentials

### 4. Verify Downloads

The setup downloads software from:
- Homebrew official repositories
- GitHub official repositories (Oh My Zsh, Powerlevel10k, etc.)
- npm/pip official registries (via mise)

All downloads use HTTPS and official sources.

### 5. Run with Minimal Privileges

- Never run bootstrap as root
- Scripts will prompt for sudo when needed
- Review sudoers configuration (disabled by default)

### 6. Regular Security Audits

```bash
# Run security verification
./verify-setup.sh

# Check for known vulnerabilities
brew audit --strict
npm audit (for Node.js projects)
```

### 7. Network Security

If running in a corporate environment:
- Configure proxy settings in shell RC files
- Verify firewall allows Homebrew/GitHub access
- Use VPN if required by organization

## Known Security Considerations

### Package Installation

This setup installs 100+ packages from Homebrew. Each package is:
- Downloaded from official Homebrew formulae
- Verified with checksums by Homebrew
- From trusted sources (official maintainers)

Review the Brewfile to understand what will be installed.

### Shell Configuration

The setup modifies shell configuration (~/.zshrc). Review:
- `dotfiles/.zshrc` before applying
- Ensure no untrusted plugins are added
- Verify PATH modifications

### Sudo Access

The `configure_sudoers` option is **disabled by default** for security. Only enable if you understand the implications and trust your environment.

### Pre-commit Hooks

Pre-commit hooks run code on every commit. Review:
- `.pre-commit-config.yaml` for all hooks
- Ensure hooks are from trusted sources
- Update hooks regularly: `pre-commit autoupdate`

## Security Scanning

This repository includes automated security scanning:

- **Shellcheck**: Catches shell script vulnerabilities
- **Ansible-lint**: Catches Ansible security issues
- **Secret detection**: Pre-commit hook detects private keys
- **Dependency scanning**: CI checks for outdated packages

## Security-Related Configuration

### Minimal Permissions

Scripts request minimal permissions:
- No root access by default
- Sudo only when absolutely necessary
- User consent required for sensitive operations

### Secure Defaults

- Telemetry disabled in VS Code
- Passwordless sudo **disabled** by default
- Secrets excluded via .gitignore
- Private key detection in pre-commit

### Audit Trail

All changes are logged:
- Git history tracks all modifications
- CI logs available for review
- Pre-commit hooks enforce quality gates

## Disclosure Policy

We follow a **coordinated disclosure** process:

1. Reporter notifies us privately
2. We confirm and develop fix
3. Fix is released
4. Public disclosure after 7+ days
5. Credit given to reporter (if desired)

## Security Contacts

For security concerns, please refer to the repository maintainer information in the README.

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [Homebrew Security](https://docs.brew.sh/Security)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

**Last Updated**: 2025-10-27
**Security Policy Version**: 1.0
