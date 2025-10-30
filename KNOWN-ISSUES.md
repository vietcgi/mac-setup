# Known Issues and Solutions

## Issue #1: tenv conflicts with existing terraform installation

### Problem: tenv/Terraform Conflict

When upgrading from direct `terraform` installation to `tenv` (Terraform version
manager), the installation fails with:

```bash
Error: The `brew link` step did not complete successfully
Could not symlink bin/terraform
Target /opt/homebrew/bin/terraform
is a symlink belonging to terraform.
```

### Root Cause: Symlink Conflict

`tenv` manages multiple Terraform versions and provides its own `terraform`
binary. If you have Terraform installed directly via Homebrew, the symlinks
conflict.

### Solution: Automatic Unlink in Playbook

**AUTOMATICALLY FIXED IN PLAYBOOK** (as of 2025-10-26)

The playbook now includes tasks (setup.yml:60-75) that automatically detect and
unlink the old terraform installation before installing packages.

### Manual Fix (if needed): Unlink Terraform

If you encounter this issue outside the playbook:

```bash
# Unlink old terraform
brew unlink terraform

# Link tenv (which provides terraform)
brew link --overwrite tenv

# Verify tenv works
tenv --version
```

### Why tenv? Improved Version Management

- **Version Management**: Switch between Terraform/OpenTofu/Terragrunt versions
    per project
- **Better Workflow**: Automatic version detection from `.terraform-version`
    or `.tenv-version`
- **Multi-tool**: Manages terraform, terragrunt, and OpenTofu with one tool

### Using tenv: Examples

**Install specific Terraform version**:

```bash
tenv tf install 1.6.0
tenv tf use 1.6.0
```

**List available versions**:

```bash
tenv tf list-remote
```

**Auto-detect from project**:

```bash
# Create .terraform-version in project root
echo "1.6.0" > .terraform-version

# tenv will automatically use it
terraform --version  # Uses version from .terraform-version
```

**Switch tools**:

```bash
# Use OpenTofu instead
tenv tofu install latest
tenv tofu use latest

# Use Terragrunt
tenv tg install latest
tenv tg use latest
```

---

## Issue #2: LSP deprecation warning in Neovim 0.11+

### Problem: Neovim LSP Warning

When using Neovim 0.11+, you see this warning:

```
The `require('lspconfig')` "framework" is deprecated, use vim.lsp.config
Feature will be removed in nvim-lspconfig v3.0.0
```

### Root Cause: Deprecated LSP Config

Neovim 0.11 introduced native LSP configuration via `vim.lsp.config`,
deprecating the old `require('lspconfig')` pattern.

### Solution: Updated LSP Configuration

**AUTOMATICALLY FIXED IN PLAYBOOK** (as of 2025-10-26)

The LSP configuration has been updated to use:

- `LspAttach` autocmd for keybindings (modern approach)
- Removed `on_attach` callbacks (deprecated)
- Uses `pcall` for compatibility with both old and new Neovim versions

**File updated**: `dotfiles/nvim/lua/plugins/lsp.lua`

### Manual Fix (if needed): Update LSP Config

If you see this warning in your existing config:

```bash
# The playbook will automatically deploy the updated config
ansible-playbook -i inventory.yml setup.yml --tags neovim

# Or manually copy the updated file
cp /Users/kevin/devkit/dotfiles/nvim/lua/plugins/lsp.lua ~/.config/nvim/lua/plugins/
nvim +":Lazy sync" +qa
```

### What Changed: LSP API Update

**Old approach (deprecated)**:

```lua
local on_attach = function(client, bufnr)
  -- keybindings here
end
lspconfig.lua_ls.setup({ on_attach = on_attach })
```

**New approach (Neovim 0.11+)**:

```lua
vim.api.nvim_create_autocmd("LspAttach", {
  callback = function(ev)
    -- keybindings here
  end,
})
lspconfig.lua_ls.setup({ capabilities = capabilities })
```

---

## Issue #3: which-key plugin warnings

### Problem: which-key Warnings

When starting Neovim, you see:

```
There were issues reported with your **which-key** mappings.
Use `:checkhealth which-key` to find out more.
```

### Root Cause: which-key API Change

which-key.nvim v3.0.0+ changed its API from `wk.register()` to `wk.add()` with a
new syntax.

### Solution: Updated which-key Configuration

**AUTOMATICALLY FIXED IN PLAYBOOK** (as of 2025-10-26)

The which-key configuration has been updated to use the new v3 API.

**File updated**: `dotfiles/nvim/lua/plugins/which-key.lua`

### What Changed: which-key API Update

**Old API (deprecated)**:

```lua
wk.register({
  ["<leader>f"] = { name = "Find" },
  ["<leader>e"] = { name = "Explorer" },
})
```

**New API (v3.0.0+)**:

```lua
wk.add({
  { "<leader>f", group = "Find" },
  { "<leader>e", group = "Explorer" },
})
```

### Manual Fix (if needed): Update which-key Config

```bash
# Copy updated config
cp /Users/kevin/devkit/dotfiles/nvim/lua/plugins/which-key.lua ~/.config/nvim/lua/plugins/

# Restart Neovim
nvim
```

---

## Issue #4: Neovim plugins not loading

### Problem: Neovim Plugins Missing

After installation, Neovim opens but plugins are missing or not configured.

### Solution: Manual Plugin Trigger

Lazy.nvim (plugin manager) installs plugins on first run, but may need a manual
trigger:

```bash
# Open neovim
nvim

# Inside neovim, run:
:Lazy sync

# Or force restore
:Lazy restore

# Check plugin status
:Lazy
```

### First-Time Setup: Plugin Installation

The first time you open Neovim after installation:

1. Plugins will auto-install (wait for completion)
2. LSP servers may need manual installation via `:Mason`
3. Treesitter parsers install on-demand

---

## Issue #5: GNU tools not in PATH

### Problem: BSD Tools Preferred

Running `sed`, `tar`, or other commands still uses macOS BSD versions instead
of GNU versions.

### Solution: Verify .zshrc PATH

#### Status: Automatically Fixed in Playbook

The .zshrc includes 9 PATH exports (setup.yml:160-183). If not working:

```bash
# Reload shell
source ~/.zshrc

# Verify GNU tools are first in PATH
which sed     # Should show: /opt/homebrew/opt/gnu-sed/libexec/gnubin/sed
which tar     # Should show: /opt/homebrew/opt/gnu-tar/libexec/gnubin/tar
which grep    # Should show: /opt/homebrew/opt/grep/libexec/gnubin/grep

# Check version (GNU tools show --version)
sed --version   # Should show "GNU sed"
tar --version   # Should show "GNU tar"
```

If still using BSD versions, check that .zshrc was properly loaded and the PATH
exports are present.

---

## Issue #6: direnv not activating

### Problem: .envrc Not Loading

`.envrc` files in projects aren't being loaded automatically.

### Solution: Check direnv Hook

**Check direnv is hooked**:

```bash
# Should be in .zshrc
grep "direnv hook" ~/.zshrc
# Should show: eval "$(direnv hook zsh)"

# Reload shell
source ~/.zshrc

# Allow direnv for project
cd /path/to/project
direnv allow
```

**First-time project setup**:

```bash
cd your-project

# Create .envrc
cat > .envrc << 'EOF'
use mise
export AWS_PROFILE=production
export KUBECONFIG=$PWD/.kube/config
EOF

# Allow direnv to load it
direnv allow
```

---

## Issue #7: grc (Generic Colouriser) not working

### Problem: grc Not Colorizing

Commands like `ping`, `dig`, `netstat` aren't colorized.

### Solution: Verify grc.zsh Sourcing

#### Status: Automatically Fixed in Playbook

The .zshrc now sources grc.zsh (setup.yml:71). If not working:

```bash
# Check if grc.zsh exists
ls -la /opt/homebrew/etc/grc.zsh

# Verify it's sourced in .zshrc
grep "grc.zsh" ~/.zshrc
# Should show: [ -f /opt/homebrew/etc/grc.zsh ] && source /opt/homebrew/etc/grc.zsh

# Reload shell
source ~/.zshrc

# Test with a grc-supported command
ping -c 3 google.com  # Should show colorized output
```

---

## Issue #8: Dock configuration not applying

### Problem: Dock Config Not Applied

After running playbook, Dock still has unwanted apps or missing desired apps.

### Solution: Restart Dock

**Restart Dock**:

```bash
killall Dock
```

**Manually verify/configure**:

```bash
# Check current Dock items
/opt/homebrew/bin/dockutil --list

# Remove unwanted items
/opt/homebrew/bin/dockutil --remove 'App Name'

# Add missing items
/opt/homebrew/bin/dockutil --add /Applications/AppName.app
```

**Re-run playbook dock tasks**:

```bash
ansible-playbook -i inventory.yml setup.yml --tags dock
```

---

## Issue #9: macOS defaults not applying

### Problem: macOS Defaults Not Set

Keyboard repeat, Finder settings, or other macOS preferences aren't configured.

### Solution: Logout/Restart

**Logout and login** (or restart) for some settings to take effect.

**Verify settings**:

```bash
# Check keyboard repeat
defaults read NSGlobalDomain KeyRepeat
# Should show: 2

# Check Finder path bar
defaults read com.apple.finder ShowPathbar
# Should show: 1 (true)
```

**Re-apply defaults**:

```bash
ansible-playbook -i inventory.yml setup.yml --tags macos
killall Finder
killall Dock
```

---

## Issue #10: Passwordless sudo not working

### Problem: Sudo Requires Password

Still prompted for password when running `sudo` commands.

### Solution: Enable Passwordless Sudo

The sudoers configuration is **disabled by default** for security.

**Enable passwordless sudo**:

1. Edit `group_vars/all.yml`
2. Set: `configure_sudoers: yes`
3. Run playbook with sudo:

    ```bash
    ansible-playbook -i inventory.yml setup.yml --tags sudoers --ask-become-pass
    ```

**Verify**:

```bash
sudo -n true 2>/dev/null && echo "Passwordless sudo: enabled" || echo "Passwordless sudo: disabled"
```

**Security Note**: Only enable on trusted machines you fully control.

---

## Getting Help

### Check Ansible Logs: Verbose Output

Run playbook with verbose output:

```bash
ansible-playbook -i inventory.yml setup.yml -vvv
```

### Verify File Existence: Dotfiles and Configs

```bash
# Check all dotfiles exist
ls -la ~/.*rc ~/.*config

# Check Brewfile
cat /Users/kevin/devkit/Brewfile

# Check group vars
cat /Users/kevin/devkit/group_vars/all.yml
```

### Test Individual Components: Targeted Playbook Runs

```bash
# Test only shell configuration
ansible-playbook -i inventory.yml setup.yml --tags shell

# Test only packages
ansible-playbook -i inventory.yml setup.yml --tags packages

# Test only neovim
ansible-playbook -i inventory.yml setup.yml --tags neovim
```

### Rollback: Restore from Backups

If issues persist, restore from backups (automatically created by playbook):

```bash
# Restore zshrc
cp ~/.zshrc.backup ~/.zshrc

# Restore tmux.conf
cp ~/.tmux.conf.backup ~/.tmux.conf

# Restore neovim config
rm -rf ~/.config/nvim
cp -r ~/.config/nvim.backup ~/.config/nvim
```

---

## Issue #11: Node.js version manager conflict (nvm vs mise)

### Problem: nvm/mise Conflict

If you upgraded from an older version of this setup, you may have both `nvm` and
`mise` installed, causing Node.js version conflicts.

**Symptoms**:

- Node.js version changes unexpectedly
- `which node` shows different paths in different terminals
- `mise current node` shows one version, `node --version` shows another
- NPM packages installed in wrong location

### Root Cause: Multiple Version Managers

Older versions of this setup installed both:

- `nvm` (Node Version Manager) via Homebrew
- `mise` (modern unified version manager) via Brewfile

Both tools try to manage Node.js, causing PATH conflicts.

### Solution: Remove nvm, Use mise

**AUTOMATICALLY FIXED IN CURRENT VERSION** (as of 2025-10-27)

The Brewfile now only includes `mise`. If you have an old installation:

```bash
# Remove nvm completely
brew uninstall nvm
rm -rf ~/.nvm

# Ensure mise is managing node
mise install node@lts
mise use -g node@lts

# Verify node is managed by mise
which node
# Should show: /Users/yourusername/.local/share/mise/installs/node/<version>/bin/node

# Verify version
node --version
mise current node  # Should match
```

### Why mise instead of nvm? Superior Version Management

- **Unified**: Manages node, python, go, ruby, terraform with one tool
- **Faster**: No shell initialization delay
- **Project-aware**: Automatically switches versions per project
- **Simpler**: One config file (.mise.toml) instead of multiple

### Using mise for Node.js: Examples

**Global version**:

```bash
mise use -g node@lts
mise use -g node@20.11.0
```

**Project-specific version**:

```bash
cd your-project
mise use node@18.19.0
# Creates/updates .mise.toml in project
```

**List installed versions**:

```bash
mise list node
```

**List available versions**:

```bash
mise list-remote node
```

---

**Last Updated**: 2025-10-27
