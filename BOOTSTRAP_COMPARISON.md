# Bootstrap Script Comparison: bootstrap-ansible.sh vs bootstrap.sh

**Context:** bootstrap.sh was created during testing and is now archived as bootstrap.sh.backup

---

## Quick Summary

| Aspect | bootstrap-ansible.sh | bootstrap.sh |
|--------|----------------------|--------------|
| **Purpose** | Direct Ansible setup | Configure system first, then Ansible |
| **Focus** | Ansible-first | Python/tools first |
| **Lines** | 400 | 553 |
| **Current Status** | ✅ ACTIVE (production) | ❌ ARCHIVED (testing artifact) |
| **Recommended** | ✅ YES | ❌ NO |

---

## Detailed Comparison

### 1. Overall Purpose

**bootstrap-ansible.sh (ACTIVE)**
- Installs prerequisites and immediately runs Ansible
- Direct path: System detection → Install Homebrew → Install Ansible → Run playbooks
- Focused and streamlined
- Faster setup

**bootstrap.sh (ARCHIVED)**
- Installs multiple tools first, then handles configuration
- Complex path: System detection → Install Homebrew → Install Python → Install Ansible → Configure → Run setup wizard
- More comprehensive preparation
- Slower, more steps

### 2. Installation Flow

**bootstrap-ansible.sh (ACTIVE)**
```
┌─ Detect OS/Arch
├─ Install Xcode CLI (macOS only)
├─ Install Homebrew
├─ Install Ansible
├─ Create config (~/.devkit/config.yaml)
└─ Run ansible-playbook setup.yml
```

**bootstrap.sh (ARCHIVED)**
```
┌─ Detect OS/Arch
├─ Install Homebrew
├─ Install Python 3
├─ Install Ansible
├─ Create configuration
├─ Validate configuration
├─ Optional: Interactive setup wizard
├─ Verification checks
└─ Run ansible-playbook setup.yml
```

### 3. Key Differences

#### A. Python Handling
| Aspect | bootstrap-ansible.sh | bootstrap.sh |
|--------|---|---|
| **Python Required** | No | Optional but automatic |
| **Python Installation** | None | Automatic via Homebrew |
| **Setup Wizard** | Not included | Interactive wizard option |
| **Python Tools** | N/A | config_engine, setup_wizard, plugin_system |

**Code Example:**
```bash
# bootstrap-ansible.sh: No Python
# Goes straight to Ansible

# bootstrap.sh: Installs Python
if [[ "$PYTHON_REQUIRED" == "true" ]]; then
    install_python || {
        log_warning "Python installation failed."
    }
fi
```

#### B. Configuration Management
| Aspect | bootstrap-ansible.sh | bootstrap.sh |
|---|---|---|
| **Config Creation** | Simple YAML | Complex with Python tools |
| **Validation** | Ansible only | Python + Bash validation |
| **Interactive Setup** | No | Optional |
| **Setup Wizard** | No | Yes |

#### C. Error Handling
| Aspect | bootstrap-ansible.sh | bootstrap.sh |
|---|---|---|
| **Error Strategy** | Fail fast (set -euo pipefail) | Continue with warnings |
| **Retry Logic** | Built-in retry function | Minimal |
| **Network Failures** | Retry up to 3 times | Fail immediately |

**Code Example:**
```bash
# bootstrap-ansible.sh: Robust retry
retry() {
    local max_attempts=3
    while (( attempt <= max_attempts )); do
        "$@" && return 0
        sleep 5
        attempt=$(( attempt + 1 ))
    done
}

# bootstrap.sh: Simple try-once
install_homebrew() {
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/...)" || {
        log_error "Failed to install Homebrew"
        return 1
    }
}
```

#### D. Code Quality
| Aspect | bootstrap-ansible.sh | bootstrap.sh |
|---|---|---|
| **Error Set** | set -euo pipefail | set -e |
| **Strictness** | More strict | Less strict |
| **Logging** | Consistent [INFO] prefix | Mixed emoji prefixes |
| **Functions** | Focused functions | Larger functions |

### 4. Features Comparison

#### bootstrap-ansible.sh (ACTIVE)
✅ **Pros:**
- Simpler, faster setup
- Fewer dependencies
- Focused on one job: bootstrap Ansible
- Better error handling with retries
- Smaller code footprint (400 lines)
- Production-ready and tested

❌ **Cons:**
- No interactive setup wizard
- Less configuration options upfront
- No Python tools available during bootstrap

#### bootstrap.sh (ARCHIVED)
✅ **Pros:**
- More comprehensive setup
- Interactive wizard for configuration
- Python tools available
- More detailed verification

❌ **Cons:**
- Larger codebase (553 lines)
- More complex error handling
- Slower setup process
- Creates Python dependency
- More moving parts = more failure points

### 5. Why bootstrap-ansible.sh is Better

1. **Simpler is Better**
   - One focused job: install Ansible and run it
   - Less can go wrong
   - Easier to understand and maintain

2. **Ansible Does Configuration**
   - Don't duplicate what Ansible can do
   - All the complexity is handled by Ansible roles
   - Consistent configuration across roles

3. **No Python Dependency During Bootstrap**
   - Python is installed by Ansible if needed
   - Bootstrap script itself has zero Python dependency
   - More flexible for different setups

4. **Better Error Handling**
   - Retry logic for network failures
   - Proper error set (set -euo pipefail)
   - Clear error messages

5. **Production Proven**
   - Simpler code is less likely to have bugs
   - Easier to test and debug
   - Clearer execution path

### 6. Which One to Use?

**Use bootstrap-ansible.sh:**
✅ Normal users - just run: `./bootstrap-ansible.sh`
✅ Most common case
✅ Recommended for all scenarios
✅ Actively maintained

**Don't use bootstrap.sh:**
❌ It's archived (bootstrap.sh.backup)
❌ Was created during testing
❌ Superseded by bootstrap-ansible.sh
❌ Not maintained

---

## Migration Guide (if needed)

If you were using bootstrap.sh:

```bash
# Old way (archived)
./bootstrap.sh

# New way (current)
./bootstrap-ansible.sh

# If you need interactive setup (use Ansible directly)
ansible-playbook --ask-tags setup.yml

# If you need specific configuration
nano ~/.devkit/config.yaml
./bootstrap-ansible.sh
```

---

## Technical Details

### Error Handling Comparison

```bash
# bootstrap-ansible.sh: Modern strict mode
set -euo pipefail
# -e: Exit on any error
# -u: Error on undefined variables
# -o pipefail: Error if any pipe fails

# bootstrap.sh: Basic mode
set -e
# -e: Exit on any error
# (allows undefined variables)
```

### Logging Comparison

```bash
# bootstrap-ansible.sh: Consistent format
print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# bootstrap.sh: Emoji format
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}
```

### Network Reliability

```bash
# bootstrap-ansible.sh: Retry mechanism
retry() {
    local max_attempts=3
    local timeout=5
    while (( attempt <= max_attempts )); do
        "$@" && return 0
        sleep $timeout
        attempt=$(( attempt + 1 ))
    done
    return 1
}

# bootstrap.sh: No retry
# Direct curl with -fsSL (fail on error)
```

---

## Summary

| Criterion | Winner |
|-----------|--------|
| **Simplicity** | bootstrap-ansible.sh |
| **Code Quality** | bootstrap-ansible.sh |
| **Error Handling** | bootstrap-ansible.sh |
| **Maintenance** | bootstrap-ansible.sh |
| **Production Readiness** | bootstrap-ansible.sh |
| **Speed** | bootstrap-ansible.sh |
| **Interactivity** | bootstrap.sh (but not needed) |
| **Configuration Options** | bootstrap.sh (but Ansible does it) |

**WINNER: bootstrap-ansible.sh** ✅

---

## Current Status

### Active Script
- **Location:** `/bootstrap-ansible.sh`
- **Status:** ✅ Production
- **Recommended:** ✅ YES

### Archived Script
- **Location:** `/bootstrap.sh.backup` (removed from main)
- **Status:** ❌ Testing artifact
- **Recommended:** ❌ NO

---

**Recommendation:** Use `bootstrap-ansible.sh` for all new setups. It's simpler, faster, and more reliable.

For users: **Just run `./bootstrap-ansible.sh` and you're done!** 🚀
