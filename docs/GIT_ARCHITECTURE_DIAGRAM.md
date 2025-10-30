# Git Configuration Architecture Diagram

Visual representation of the git configuration system architecture.

## Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEVKIT GIT CONFIGURATION SYSTEM                   │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  INPUT LAYER                                                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Ansible Role    │  │ Python Manager   │  │ Direct Edit      │  │
│  │ Variables       │  │ CLI Tool         │  │ ~/.gitconfig*    │  │
│  │ group_vars/     │  │ git_config_      │  │ ~/.gitconfig.    │  │
│  │ host_vars/      │  │ manager.py       │  │ local            │  │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘  │
│
│            All inputs merge into CONFIGURATION LAYER ↓
│
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  CONFIGURATION LAYER                                                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Configuration Engine                                         │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  1. LOAD PHASE                                              │  │
│  │     ├─ Read schema (config/schema.yaml)                     │  │
│  │     ├─ Load defaults (defaults/main.yml)                    │  │
│  │     ├─ Deep merge configs (highest to lowest priority)      │  │
│  │     └─ Apply environment variable overrides                 │  │
│  │                                                              │  │
│  │  2. VALIDATE PHASE                                          │  │
│  │     ├─ YAML syntax validation                               │  │
│  │     ├─ Schema constraints check                             │  │
│  │     ├─ Type checking                                        │  │
│  │     └─ Permission validation                                │  │
│  │                                                              │  │
│  │  3. TRANSFORM PHASE                                         │  │
│  │     ├─ Jinja2 template rendering                            │  │
│  │     ├─ Variable interpolation                               │  │
│  │     └─ Path expansion                                       │  │
│  │                                                              │  │
│  │  4. OUTPUT PHASE                                            │  │
│  │     ├─ Generate ~/.gitconfig                                │  │
│  │     ├─ Generate ~/.gitconfig.local                          │  │
│  │     ├─ Generate ~/.gitattributes                            │  │
│  │     └─ Generate ~/.config/git/ignore                        │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│
│           Configuration ready for deployment ↓
│
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  DEPLOYMENT LAYER (Ansible Role)                                     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Tasks                     Files Generated         Handlers        │
│  ─────                     ────────────────        ────────        │
│                                                                      │
│  Deploy gitconfig ──→ ~/.gitconfig ────────────→ reload git config │
│  Deploy local    ──→ ~/.gitconfig.local        │                   │
│  Deploy attrs    ──→ ~/.gitattributes          │                   │
│  Deploy ignore   ──→ ~/.config/git/ignore      │                   │
│  Deploy hooks    ──→ ~/.git-templates/hooks    │ reload git hooks  │
│  Backup config   ──→ ~/.devkit/git/backup.*    │                   │
│  Setup aliases   ──→ (in gitconfig)            │                   │
│  Setup signing   ──→ (in gitconfig)            │                   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  RELOAD LAYER                                                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Reload Mechanisms:                                                 │
│                                                                      │
│  Ansible (Full)              Python Manager (Targeted)             │
│  ───────────────────         ──────────────────────               │
│  ansible-playbook            python3 cli/git_config_manager.py    │
│  setup.yml --tags git        --component config/hooks/creds       │
│                              --dry-run                             │
│                              --verbose                             │
│                                                                      │
│  Steps:                                                             │
│  1. ✓ Validate config syntax                                        │
│  2. ✓ Detect changes                                                │
│  3. ✓ Create backup                                                 │
│  4. ✓ Make hooks executable                                         │
│  5. ✓ Update git settings                                           │
│  6. ✓ Reload credential helpers                                     │
│  7. ✓ Log changes to audit trail                                    │
│  8. ✓ Display report                                                │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  GIT HOOKS EXECUTION LAYER                                           │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Commit Lifecycle with Hooks:                                       │
│                                                                      │
│    $ git commit                                                     │
│           ↓                                                         │
│    ┌─────────────────────┐                                          │
│    │ 1. pre-commit hook  │  ← Can PREVENT commit                   │
│    │ ├─ Check trailing WS│                                          │
│    │ ├─ Check file size  │                                          │
│    │ ├─ Syntax validation│                                          │
│    │ └─ Custom scripts   │                                          │
│    └─────────────────────┘                                          │
│           ↓ (if passed)                                             │
│    [Editor opens for message]                                      │
│           ↓                                                         │
│    ┌──────────────────────────┐                                     │
│    │ 2. prepare-commit-msg   │  ← Can MODIFY message               │
│    │ ├─ Auto-prefix with ID  │                                      │
│    │ └─ Auto-format          │                                      │
│    └──────────────────────────┘                                     │
│           ↓                                                         │
│    [User continues editing/confirms]                               │
│           ↓                                                         │
│    ┌──────────────────────────┐                                     │
│    │ 3. commit-msg hook      │  ← Can PREVENT commit               │
│    │ ├─ Validate format      │                                      │
│    │ ├─ Check line length    │                                      │
│    │ ├─ Verify type/scope    │                                      │
│    │ └─ Suggest imperative   │                                      │
│    └──────────────────────────┘                                     │
│           ↓ (if passed)                                             │
│    [Commit created]                                                │
│           ↓                                                         │
│    ┌──────────────────────────┐                                     │
│    │ 4. post-commit hook     │  ← CANNOT prevent commit            │
│    │ ├─ Log commit info      │                                      │
│    │ ├─ Run notifications    │                                      │
│    │ └─ Run custom scripts   │                                      │
│    └──────────────────────────┘                                     │
│           ↓                                                         │
│    [Commit successful]                                             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  PERSISTENCE & LOGGING LAYER                                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Configuration Files:                                               │
│  ~/.gitconfig                 ← Main config (Ansible-managed)      │
│  ~/.gitconfig.local           ← Local overrides (user-managed)     │
│  ~/.config/git/ignore         ← Global gitignore                   │
│  ~/.gitattributes             ← File type rules                    │
│                                                                      │
│  Hook Files:                                                        │
│  ~/.git-templates/hooks/pre-commit            (755)                │
│  ~/.git-templates/hooks/commit-msg            (755)                │
│  ~/.git-templates/hooks/post-commit           (755)                │
│  ~/.git-templates/hooks/prepare-commit-msg    (755)                │
│                                                                      │
│  Backups & Logs:                                                    │
│  ~/.devkit/git/gitconfig.backup.* ← Timestamped backups            │
│  ~/.devkit/logs/git.log           ← Config reload events            │
│  ~/.devkit/git/logs/commits.log   ← Commit audit trail              │
│  ~/.devkit/git/logs/commit-msg.log← Message validation logs         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Configuration Hierarchy (Priority Order)

```
┌─────────────────────────────────────────────────────────┐
│           CONFIGURATION PRIORITY HIERARCHY              │
│            (Highest to Lowest Priority)                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 1. Repository Config (.git/config)            ✓ │ │  Highest
│  │    Specific to this repository                  │ │
│  └──────────────────────────────────────────────────┘ │
│         ↑ (overrides all below)                       │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 2. User Local Config (~/.gitconfig.local)   ✓ │ │
│  │    Machine/user specific                        │ │
│  └──────────────────────────────────────────────────┘ │
│         ↑ (overrides global)                          │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 3. Global Config (~/.gitconfig)              ✓ │ │
│  │    User-wide (Ansible managed)                  │ │
│  │    - Contains: user info, aliases, hooks path  │ │
│  └──────────────────────────────────────────────────┘ │
│         ↑ (overrides system)                          │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 4. System Config (/etc/gitconfig)            ✗ │ │
│  │    System-wide (rarely used)                    │ │
│  └──────────────────────────────────────────────────┘ │
│         ↑                                               │
│                                                         │
│                                  Lowest Priority       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Example: Finding user.email                            │
│                                                         │
│ git config --get user.email searches:                  │
│ 1. Check .git/config               ← Found here? Use  │
│ 2. Check ~/.gitconfig.local        ← Found here? Use  │
│ 3. Check ~/.gitconfig              ← Found here? Use  │
│ 4. Check /etc/gitconfig            ← Found? Use       │
│ 5. Not found anywhere? Error!                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## File Organization

```
~
├── .gitconfig                         ← GLOBAL CONFIG (main)
├── .gitconfig.local                   ← LOCAL CONFIG (overrides)
├── .gitattributes                     ← FILE ATTRIBUTES
├── .config/git/
│   └── ignore                         ← GLOBAL GITIGNORE
│
├── .git-templates/                    ← TEMPLATES DIR
│   ├── hooks/
│   │   ├── pre-commit                 ← Pre-commit checks
│   │   ├── commit-msg                 ← Message validation
│   │   ├── post-commit                ← Audit logging
│   │   ├── prepare-commit-msg         ← Auto-prefix
│   │   └── scripts/                   ← Custom scripts (optional)
│   │       ├── pre-commit-*.sh
│   │       └── post-commit-*.sh
│   │
│   └── info/                          ← Excluded patterns
│       └── exclude
│
├── .devkit/git/                       ← BACKUPS & LOGS
│   ├── gitconfig.backup.20240101_120000
│   ├── gitconfig.backup.20240102_120000
│   └── logs/
│       ├── git.log                    ← Reload events
│       ├── commit-msg.log             ← Validation logs
│       └── commits.log                ← Commit audit trail
│
└── devkit/                            ← PROJECT
    └── ansible/roles/git/
        ├── tasks/main.yml             ← Git setup tasks
        ├── handlers/main.yml          ← Reload handlers
        ├── defaults/main.yml          ← Default variables
        ├── meta/main.yml              ← Metadata
        ├── templates/
        │   ├── gitconfig.j2
        │   ├── gitconfig.local.j2
        │   ├── gitattributes.j2
        │   └── hooks/
        │       ├── pre-commit.sh.j2
        │       ├── commit-msg.sh.j2
        │       ├── post-commit.sh.j2
        │       └── prepare-commit-msg.sh.j2
        ├── files/
        │   └── gitignore_global
        └── README.md                  ← Role documentation
```

## Data Flow: Configuration to Git

```
INPUT                    PROCESSING                OUTPUT
─────                    ──────────                ──────

group_vars/     ┐                          ┌─────────────────┐
all.yml         │                          │ Jinja2          │
                ├──→ Deep Merge    ──→    │ Template        │ ──→ ~/.gitconfig
host_vars/      │    & Validation         │ Engine          │
localhost.yml   │                          │ (renders)       │ ──→ ~/.gitconfig.local
                │                          └─────────────────┘
defaults/       ┘
main.yml


Example: git_aliases variable

INPUT (group_vars/all.yml):
┌───────────────────────────────────────┐
│ git_aliases:                          │
│   s: "status"                         │
│   co: "checkout"                      │
│   log: "log --oneline"                │
└───────────────────────────────────────┘
            ↓
PROCESSING (defaults merged):
┌───────────────────────────────────────┐
│ git_aliases: (from all.yml + defaults)│
│   s: "status"      (overrides default)│
│   d: "diff"        (from defaults)    │
│   co: "checkout"   (overrides default)│
│   br: "branch"     (from defaults)    │
└───────────────────────────────────────┘
            ↓
RENDERING (gitconfig.j2):
┌───────────────────────────────────────┐
│ {% for name, cmd in git_aliases %}   │
│   {{ name }} = {{ cmd }}              │
│ {% endfor %}                          │
└───────────────────────────────────────┘
            ↓
OUTPUT (~/.gitconfig):
┌───────────────────────────────────────┐
│ [alias]                               │
│   s = status                          │
│   d = diff                            │
│   co = checkout                       │
│   br = branch                         │
└───────────────────────────────────────┘
```

## Reload Process Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     RELOAD PROCESS FLOW                         │
└─────────────────────────────────────────────────────────────────┘

TRIGGER: ansible-playbook setup.yml --tags git
    or: python3 cli/git_config_manager.py

        ↓
┌──────────────────────────────────────┐
│ STEP 1: VALIDATION                   │
├──────────────────────────────────────┤
│ ✓ Check YAML syntax                  │
│ ✓ Verify file permissions            │
│ ✓ Check file ownership               │
│ ✓ Validate against schema            │
└──────────────────────────────────────┘
        ↓ (if validation passes)
┌──────────────────────────────────────┐
│ STEP 2: BACKUP                       │
├──────────────────────────────────────┤
│ ✓ Create timestamped backup          │
│ ✓ Store in ~/.devkit/git/            │
│ ✓ Log backup operation               │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ STEP 3: CHANGE DETECTION             │
├──────────────────────────────────────┤
│ ✓ Compare old vs new config          │
│ ✓ Identify changed keys              │
│ ✓ Report changes to user             │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ STEP 4: DEPLOY CONFIGURATION         │
├──────────────────────────────────────┤
│ ✓ Copy ~/.gitconfig                  │
│ ✓ Copy ~/.gitconfig.local            │
│ ✓ Copy ~/.gitattributes              │
│ ✓ Copy ~/.config/git/ignore          │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ STEP 5: DEPLOY HOOKS                 │
├──────────────────────────────────────┤
│ ✓ Copy pre-commit hook               │
│ ✓ Copy commit-msg hook               │
│ ✓ Copy post-commit hook              │
│ ✓ Copy prepare-commit-msg hook       │
│ ✓ Make all hooks executable (755)    │
│ ✓ Verify hook syntax                 │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ STEP 6: RELOAD COMPONENTS            │
├──────────────────────────────────────┤
│ ✓ Trigger: reload git config         │
│ ✓ Trigger: reload git hooks          │
│ ✓ Trigger: restart git services      │
│ ✓ Verify credential helpers          │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ STEP 7: VERIFICATION                 │
├──────────────────────────────────────┤
│ ✓ Verify git user config loaded      │
│ ✓ Verify hooks are executable        │
│ ✓ Test hook syntax (bash -n)         │
│ ✓ Verify hook path is set            │
└──────────────────────────────────────┘
        ↓
┌──────────────────────────────────────┐
│ STEP 8: AUDIT & REPORTING            │
├──────────────────────────────────────┤
│ ✓ Log to ~/.devkit/logs/git.log      │
│ ✓ Generate status report             │
│ ✓ Display results to user            │
│ ✓ Show configuration summary         │
└──────────────────────────────────────┘
        ↓
SUCCESS / FAILURE REPORT

If SUCCESS:
✓ Configuration reloaded
✓ All hooks verified
✓ Audit trail updated

If FAILURE:
✗ Validation errors shown
✗ Backup available
✗ Suggested fixes provided
✗ Logs available for debugging
```

## Hook Execution Timeline

```
┌────────────────────────────────────────────────────────────────┐
│           GIT COMMIT WITH HOOKS - TIMELINE                     │
└────────────────────────────────────────────────────────────────┘

TIME    EVENT                      HOOK                STATUS
────    ─────                      ────                ──────

  T0    User runs: git commit      [START]

  T1    Git reads config
        from ~/.gitconfig,
        ~/.gitconfig.local

  T2    Core.hooksPath checked     ← Set to:
                                     ~/.git-templates/hooks

  T3    PRE-COMMIT HOOK runs       pre-commit.sh       [BLOCKING]
        ├─ Check trailing WS                           ✓ Can fail
        ├─ Check file size
        ├─ Syntax validation
        └─ Custom scripts

  T4    [If pre-commit failed]
        → Abort commit, show error
        [If pre-commit passed]     [CONTINUE]
        → Proceed to editor

  T5    Editor opens for
        message entry

  T6    User types message

  T7    PREPARE-COMMIT-MSG hook    prepare-commit-msg  [MODIFYING]
        ├─ Check branch name                           ✓ Can modify
        └─ Auto-prefix if needed                       ✗ Can't fail

  T8    Editor shows prepared
        message to user

  T9    User confirms/edits
        message

  T10   COMMIT-MSG HOOK runs       commit-msg.sh       [BLOCKING]
        ├─ Validate format                             ✓ Can fail
        ├─ Check line length
        ├─ Verify type/scope
        └─ Check convention

  T11   [If commit-msg failed]
        → Abort commit, show error
        [If commit-msg passed]     [CONTINUE]
        → Proceed to create commit

  T12   Commit object created
        Commit written to
        git database

  T13   POST-COMMIT HOOK runs      post-commit.sh      [NON-BLOCKING]
        ├─ Log commit info                             ✗ Can't fail
        ├─ Run notifications
        └─ Custom scripts

  T14   Return to shell
        User sees: [branch] $
        Commit successful!         [END]

────────────────────────────────────────────────────────────────

Legend:
[BLOCKING]      = Can prevent commit (exit code 1)
[MODIFYING]     = Can modify message
[NON-BLOCKING]  = Runs after commit, can't prevent it
✓ Can fail      = Hook can cause commit to abort
✗ Can't fail    = Hook runs regardless of outcome
```

## Role Dependency Graph

```
┌───────────────────────────────────────────────────────┐
│            ROLE DEPENDENCY HIERARCHY                  │
└───────────────────────────────────────────────────────┘

                     ┌──────────────┐
                     │  setup.yml   │
                     │   (master)   │
                     └──────────────┘
                           ↑
                           │ includes
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───────┐          ┌───────┐         ┌────────┐
    │ CORE  │          │ SHELL │         │ EDITORS│
    │       │          │       │         │        │
    │ base  │          │ zsh   │         │ nvim   │
    │ setup │          │ Oh-My │         │ vscode │
    └───────┘          │ Zsh   │         └────────┘
        ↑              │ Plugins
        │              └───────┘
        │
    ┌───────┐
    │  GIT  │ ← (THIS ROLE)
    │ (YOU) │
    │       │
    │ Deps: │
    │ ├─ core ✓
    │ └─ none else (independent)
    └───────┘
        ↑
    ┌───────┐
    │ shell │ (optional: git integration)
    │       │
    │ uses: │
    │ ├─ git aliases
    │ └─ git hooks
    └───────┘


Can be deployed:
✓ Standalone (depends only on core)
✓ Before shell (shell can use git)
✓ After shell (works independently)
✓ With other roles (no conflicts)
```

---

**Created:** October 30, 2024
**Purpose:** Visual reference for git configuration architecture
**Status:** Complete ✅
