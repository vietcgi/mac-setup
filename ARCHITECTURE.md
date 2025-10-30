# Devkit Architecture & Best Practices

This document outlines the infrastructure-as-code architecture for Devkit and explains the design decisions made.

## Current Architecture

### Overview

```
┌─────────────────────────────────────────────────────────┐
│                   bootstrap.sh                          │
│         (Prerequisites: Homebrew, Python, Ansible)      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                   setup.yml (Playbook)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Inline Tasks (Package Install, Config)          │   │
│  │  - Homebrew/apt/dnf packages                     │   │
│  │  - Environment setup                             │   │
│  │  - macOS defaults                                │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Role Includes                                   │   │
│  │  - include_role: dotfiles                        │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                   Ansible Roles                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  dotfiles/ (NEW - Best Practice)                │   │
│  │  ├─ defaults/main.yml (variables)               │   │
│  │  ├─ meta/main.yml (dependencies)                │   │
│  │  ├─ tasks/main.yml (deployment logic)           │   │
│  │  ├─ handlers/main.yml (event handlers)          │   │
│  │  └─ README.md (documentation)                   │   │
│  │                                                  │   │
│  │  Old/Legacy (To be refactored):                 │   │
│  │  ├─ shell/                                      │   │
│  │  ├─ editors/                                    │   │
│  │  ├─ core/                                       │   │
│  │  └─ security/                                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                Configuration Files                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  dotfiles/ (Repository)                          │   │
│  │  ├─ .tmux.conf (Tmux configuration)             │   │
│  │  ├─ .zshrc (Zsh shell)                          │   │
│  │  ├─ .inputrc (Readline)                         │   │
│  │  ├─ .direnvrc (Direnv)                          │   │
│  │  ├─ nvim/ (Neovim editor)                       │   │
│  │  └─ ghostty/ (Ghostty terminal)                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│             User Home Directory (~/)                     │
│  ├─ .tmux.conf                                         │
│  ├─ .zshrc                                             │
│  ├─ .inputrc                                           │
│  ├─ .direnvrc                                          │
│  ├─ .config/nvim/                                      │
│  └─ .config/ghostty/                                   │
└─────────────────────────────────────────────────────────┘
```

## Best Practices Implemented

### 1. Infrastructure as Code (IaC)

All system configuration is managed through Ansible, not shell scripts. This ensures:

- **Idempotency**: Running the playbook multiple times has the same effect
- **Auditability**: All changes are tracked and documented
- **Portability**: Same configuration works on macOS and Linux
- **Repeatability**: Easy to provision new machines consistently

### 2. Dotfiles Management

The `dotfiles` role implements proper configuration file management:

```yaml
# Declarative deployment
- Files are the source of truth
- Deployed from `dotfiles/` directory to home
- Automatic backups before overwriting
- Change detection and reporting
- Syntax validation where applicable
```

**Key Principle**: Configuration files should be in version control, not hardcoded in playbooks.

### 3. Role Structure

Each Ansible role follows the standard structure:

```
role_name/
├─ defaults/main.yml       # Default variables (overrideable)
├─ meta/main.yml           # Role metadata & dependencies
├─ tasks/main.yml          # Task definitions
├─ handlers/main.yml       # Event handlers (restarts, reloads)
├─ files/                  # Static files (if needed)
├─ templates/              # Dynamic templates (if needed)
└─ README.md              # Role documentation
```

### 4. Separation of Concerns

- **bootstrap.sh**: Only handles prerequisites (no configuration)
- **setup.yml**: Orchestrates roles and inline tasks
- **Roles**: Each role has a single responsibility
- **Dotfiles role**: Specifically handles all configuration file deployment

### 5. Idempotency

All tasks are idempotent:

- Copy module only updates changed files
- Stat module checks prerequisites
- Handlers deferred to end of playbook
- No rm/destructive operations unless necessary
- Backups created before modifications

### 6. Version Control

Configuration is tracked in Git:

```
devkit/
├─ bootstrap.sh            # Prerequisites script
├─ setup.yml              # Main playbook
├─ ansible/roles/          # Ansible roles
├─ dotfiles/               # Configuration files (version controlled!)
│  ├─ .tmux.conf
│  ├─ .zshrc
│  └─ ...
├─ group_vars/            # Variable overrides
├─ inventory.yml          # Host inventory
└─ ARCHITECTURE.md        # This file!
```

## Migration Path to Full Best Practices

While the current architecture has both inline tasks and roles, the path to full best practices is:

### Phase 1: Dotfiles Role (COMPLETED ✓)

- [x] Create dedicated `dotfiles` role
- [x] Implement proper role structure with defaults/, meta/, etc.
- [x] Add role documentation (README.md)
- [x] Add configuration file deployment logic
- [x] Integrate into setup.yml via include_role

### Phase 2: Refactor Installation Roles (TODO)

- [ ] Move package installation to dedicated `package_manager` role
- [ ] Refactor `shell` role to only install/config (not deploy files)
- [ ] Refactor `editors` role similarly
- [ ] Add `meta/main.yml` to all roles with dependencies

### Phase 3: Clean Separation (TODO)

- [ ] Move all inline package tasks from setup.yml to roles
- [ ] Make setup.yml only contain include_role statements
- [ ] Remove duplicate configuration logic
- [ ] Implement pre_tasks and post_tasks for setup

### Phase 4: Full Modularity (TODO)

- [ ] Enable running individual roles: `ansible-playbook setup.yml --tags shell`
- [ ] Make roles completely testable in isolation
- [ ] Add role testing infrastructure (molecule, etc.)
- [ ] Create role documentation site

##  Best Practices: What We Got Right

✅ **Single Source of Truth**: Dotfiles in version control
✅ **Idempotent Operations**: Safe to run multiple times
✅ **Auditable Changes**: All configuration in Git
✅ **Portable**: Works on macOS and Linux
✅ **Documented**: Each role has README
✅ **Templated**: Uses Ansible variables, not hardcoded values
✅ **Backed Up**: Automatic backups before overwriting files
✅ **Validated**: Configuration syntax checking
✅ **Reported**: Detailed deployment summaries

## Best Practices: What Needs Improvement

❌ **Mixed Concerns**: setup.yml has both roles and inline tasks
❌ **Duplication**: Some configuration logic scattered
❌ **Tight Coupling**: Some tasks reference playbook_dir directly
❌ **Incomplete Roles**: Some roles missing defaults/meta/README
❌ **Test Coverage**: No automated testing of roles
❌ **Documentation**: Not all design decisions documented

## Usage Examples

### Deploy Everything

```bash
./bootstrap.sh
```

This runs:
1. Installs prerequisites (Homebrew, Python, Ansible)
2. Runs `setup.yml` which:
   - Installs packages
   - Deploys dotfiles via `dotfiles` role
   - Configures system
   - Reports results

### Deploy Only Dotfiles

```bash
ansible-playbook -i inventory.yml setup.yml --tags dotfiles
```

### Update a Single Config

```bash
# Edit dotfiles/.tmux.conf
vim dotfiles/.tmux.conf

# Commit change
git commit -m "fix: improve tmux highlight color"

# Deploy
ansible-playbook -i inventory.yml setup.yml --tags dotfiles
```

### Check What Will Change

```bash
ansible-playbook -i inventory.yml setup.yml --check
```

### Dry-run (No Changes)

```bash
ansible-playbook -i inventory.yml setup.yml --check --diff
```

## Key Files

| File | Purpose |
|------|---------|
| `bootstrap.sh` | Entry point - installs prerequisites |
| `setup.yml` | Main playbook - orchestrates configuration |
| `ansible/roles/dotfiles/` | Role for deploying configuration files |
| `dotfiles/` | Version-controlled configuration files |
| `inventory.yml` | Ansible inventory - defines hosts |
| `group_vars/` | Group-level variable overrides |
| `ARCHITECTURE.md` | This file! |

## Testing

To verify the architecture works:

```bash
# Full run
./bootstrap.sh

# Idempotency test (should show 0 changed)
ansible-playbook -i inventory.yml setup.yml

# Dry-run test
ansible-playbook -i inventory.yml setup.yml --check

# Specific role test
ansible-playbook -i inventory.yml setup.yml --tags dotfiles -v
```

## Future Improvements

1. **Molecule Testing**: Add automated role testing
2. **Linting**: Use ansible-lint for code quality
3. **Full Role Separation**: Move all inline tasks to roles
4. **Pre/Post Tasks**: Implement hooks for custom logic
5. **Better Reporting**: More detailed deployment reports
6. **Documentation Site**: Auto-generated docs from roles
7. **Role Versions**: Tag roles with versions
8. **Secrets Management**: Handle sensitive config properly

## References

- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Ansible Roles](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html)
- [Infrastructure as Code](https://en.wikipedia.org/wiki/Infrastructure_as_code)
- [Idempotent Operations](https://en.wikipedia.org/wiki/Idempotence)

## Questions?

For questions about this architecture:

1. Check role READMEs in `ansible/roles/*/README.md`
2. Review task definitions in `ansible/roles/*/tasks/main.yml`
3. Check default variables in `ansible/roles/*/defaults/main.yml`
4. Review Git history: `git log --oneline`

---

**Last Updated**: October 30, 2025
**Architecture Version**: 1.0
**Status**: Partial Implementation (Phase 1 Complete, Phase 2+ TODO)
