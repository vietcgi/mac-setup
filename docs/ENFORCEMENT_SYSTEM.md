# Enforcement System - How Quality Standards Are Enforced

## Overview

The commit quality standard is enforced through **three layers** of automated and manual verification, with **four enforcement mechanisms** that work together to ensure every commit meets the high-bar standard.

## Layer 1: Automated Enforcement (Git Hooks)

### What It Does
Git hooks automatically run **before** and **after** every commit attempt. If any gate fails, the commit is **blocked immediately** - there's no way around it.

### The Hook Chain

```
User runs: git commit -m "message"
    ↓
    ├─→ pre-commit hook (runs first)
    │    ├─ Trailing whitespace check
    │    ├─ Large file detection (>10MB)
    │    ├─ Syntax check (python3 -m py_compile)
    │    └─ Custom quality checks
    │         ├─ Code style (pylint)
    │         ├─ Test execution (pytest)
    │         ├─ Coverage verification (85%+)
    │         ├─ Type checking (mypy strict)
    │         ├─ Security scan (bandit)
    │         └─ Complexity check (radon)
    │
    │    If ANY fails → ✗ COMMIT BLOCKED → exit 1
    │    If ALL pass → ✓ Continue
    ↓
    ├─→ commit-msg hook (validates message format)
    │    ├─ Check message not empty
    │    ├─ Check first line ≤ 50 characters
    │    ├─ Check blank line between subject/body
    │    ├─ Check conventional commit format
    │    └─ Check scope format
    │
    │    If fails → ✗ COMMIT BLOCKED → exit 1
    │    If passes → ✓ Continue
    ↓
    ├─→ Commit is created and signed (GPG)
    │
    ↓
    ├─→ post-commit hook (logging/audit only)
    │    ├─ Extract commit hash
    │    ├─ Extract commit message
    │    ├─ Extract author info
    │    ├─ Log to audit trail (~/.devkit/git/commits.log)
    │    └─ Run optional post-commit scripts
    │
    │    (Does NOT block commit - it's already committed)
    ↓
✓ SUCCESS: Commit is complete and logged
```

### Hook Files

All hooks are installed in: `~/.git-templates/hooks/`

| Hook | Purpose | Behavior |
|------|---------|----------|
| `pre-commit` | Quality enforcement | **BLOCKS commit** if any gate fails |
| `commit-msg` | Message validation | **BLOCKS commit** if format invalid |
| `post-commit` | Audit logging | Records commit (non-blocking) |
| `prepare-commit-msg` | Auto-prefixes | Prepends branch name (optional) |

### Configuration

Hooks are deployed via Ansible role `ansible/roles/git/`:

**File: `defaults/main.yml`**
- Configurable quality check thresholds
- Enable/disable specific checks
- Set minimum coverage (default: 85%)
- Set minimum linting score (default: 8.0)

**File: `templates/hooks/pre-commit.sh.j2`**
- Template that renders with configuration values
- Lines 21-82: Quality gate implementations
- Colored output (green ✓, red ✗, yellow ⚠)

**File: `handlers/main.yml`**
- Auto-reload on configuration changes
- Makes hooks executable
- Verifies hook accessibility

### Quality Gates Enforced by Hooks

```
┌────────────────────────────────────────┐
│ GATE 1: SYNTAX CHECK                   │ ← Hard Block
├────────────────────────────────────────┤
│ Command: python3 -m py_compile *.py    │
│ Fails if: SyntaxError, ImportError     │
│ Blocks commit: YES                     │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ GATE 2: TESTS (100% pass rate)         │ ← Hard Block
├────────────────────────────────────────┤
│ Command: pytest -v                     │
│ Fails if: ANY test failure             │
│ Requirement: 100% pass rate            │
│ Blocks commit: YES                     │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ GATE 3: COVERAGE (85%+ required)       │ ← Hard Block
├────────────────────────────────────────┤
│ Command: coverage report --fail-under=85│
│ Fails if: Coverage < 85%               │
│ Critical paths: 95%+ required          │
│ Blocks commit: YES                     │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ GATE 4: TYPE CHECKING (mypy strict)    │ ← Hard Block
├────────────────────────────────────────┤
│ Command: mypy --strict *.py            │
│ Fails if: Type errors detected         │
│ Requirement: No implicit Any types     │
│ Blocks commit: YES                     │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ GATE 5: SECURITY (0 issues)            │ ← Hard Block
├────────────────────────────────────────┤
│ Command: bandit -r -ll *.py            │
│ Fails if: Vulnerability found          │
│ Requirement: 0 security issues         │
│ Blocks commit: YES                     │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ GATE 6: LINTING (8.0+ score)           │ ← Hard Block
├────────────────────────────────────────┤
│ Command: pylint *.py                   │
│ Fails if: Score < 8.0                  │
│ Requirement: 8.0 or higher             │
│ Blocks commit: YES                     │
└────────────────────────────────────────┘
```

## Layer 2: Supplementary Validation Tool

### What It Does
`cli/commit_validator.py` is a **standalone Python tool** that developers can run **before attempting a commit** to catch issues early.

### When to Use It

```bash
# Before committing (recommended)
python3 cli/commit_validator.py

# Or during development to validate specific files
python3 cli/commit_validator.py --files src/auth.py src/models.py

# Or check specific category
python3 cli/commit_validator.py --check coverage
```

### What It Validates

```python
class CodeQualityValidator:
    # Code Quality
    def check_code_style(files)       # PEP 8, pylint
    def check_test_coverage(files)    # 85%+ coverage
    def check_security(files)         # bandit scan
    def check_complexity(files)       # radon complexity
    def check_tests_pass(files)       # pytest execution
    def check_documentation(files)    # docstring presence
    def check_dependencies(files)     # dependency audit

    # Reporting
    def run_all_checks(files)         # Full validation
    def display_summary(report)       # Colored output
    def save_quality_report(report)   # JSON storage
```

### Output Example

```
🔍 Running code quality checks...

ℹ Checking code style (PEP 8)...
✓ Code style check passed

ℹ Checking test coverage...
✓ Test coverage: 92%

ℹ Checking security...
✓ Security check passed

ℹ Running tests...
✓ All tests passed (45/45)

═══════════════════════════════════════
QUALITY REPORT SUMMARY
═══════════════════════════════════════
✓ Code Style:        PASS (100/100)
✓ Test Coverage:     PASS (92%)
✓ Security:         PASS (0 issues)
✓ Complexity:       PASS (avg 3.2)
✓ Tests:            PASS (45/45)
✓ Documentation:    PASS (100%)

OVERALL: PASS ✓
═══════════════════════════════════════
```

## Layer 3: Human Review

### Code Review Requirements

Before merging to `main`, a human reviewer verifies:

1. **Code Quality**
   - Is the code clean and readable?
   - Are there better approaches?
   - Is complexity justified?

2. **Test Coverage**
   - Do tests cover the feature?
   - Are edge cases tested?
   - Is coverage adequate?

3. **Security Review**
   - Input validation present?
   - No hardcoded secrets?
   - Secure defaults?

4. **Design Review**
   - Is the architecture sound?
   - Are patterns consistent?
   - Is the design maintainable?

5. **Documentation**
   - Is intent clear?
   - Are APIs documented?
   - Are examples provided?

### Pull Request Checklist

```markdown
## PR Quality Checklist

- [ ] All automated checks passed (green CI)
- [ ] Code coverage ≥ 85% (preferably 90%+)
- [ ] All tests passing (100% pass rate)
- [ ] Type checking passed (mypy strict)
- [ ] Security scan passed (0 issues)
- [ ] Code documented (docstrings, examples)
- [ ] Commit messages follow format
- [ ] No breaking changes (or documented)
- [ ] Performance impact assessed

Only merge if ALL boxes are checked.
```

## Layer 4: Audit Trail

### What Gets Logged

Every commit is automatically logged to: `~/.devkit/git/commits.log`

**Format:** JSONL (one JSON object per line)

**Fields:**
```json
{
  "timestamp": "2024-10-30T15:23:45Z",
  "commit_hash": "a1b2c3d4",
  "commit_short": "a1b2c3d",
  "author": "alice@example.com",
  "author_name": "Alice Smith",
  "subject": "feat(auth): add password reset",
  "body": "Added secure password reset...",
  "files_changed": 3,
  "lines_added": 45,
  "lines_removed": 12,
  "tests_passed": true,
  "tests_count": 25,
  "coverage": 92,
  "type_check": "passed",
  "security_scan": "passed",
  "linting_score": 9.1,
  "gpg_signature": "trusted",
  "review_status": "pending",
  "tags": ["quality-gate-passed"]
}
```

### Audit Trail Benefits

1. **Accountability** - Who committed what and when
2. **Compliance** - Verify all commits met standards
3. **Metrics** - Track coverage trends over time
4. **Debugging** - Find when bugs were introduced
5. **Reporting** - Generate quality metrics

### Query Examples

```bash
# All commits today
cat ~/.devkit/git/commits.log | jq '.[] | select(.timestamp | startswith("2024-10-30"))'

# Low coverage commits
cat ~/.devkit/git/commits.log | jq '.[] | select(.coverage < 85)'

# Failed security scans
cat ~/.devkit/git/commits.log | jq '.[] | select(.security_scan != "passed")'

# By contributor
cat ~/.devkit/git/commits.log | jq '.[] | select(.author == "alice@example.com")'

# Average coverage this week
cat ~/.devkit/git/commits.log | jq '[.[] | .coverage] | add / length'
```

## How Enforcement Works in Practice

### Scenario 1: Developer Tries to Commit Broken Tests

```bash
$ git commit -m "feat: new feature"

🔍 Running pre-commit checks...
   Checking syntax... ✓
   Checking tests...
      ✗ test_auth.py::test_login FAILED

❌ PRE-COMMIT CHECKS FAILED

Commit aborted. Fix the issues above and try again.
   → Make tests pass
   → Re-run: pytest test_auth.py
   → Try commit again
```

**Result:** Commit blocked. No way around it. Must fix tests first.

### Scenario 2: Developer Tries with Low Coverage

```bash
$ git commit -m "feat: new authentication"

🔍 Running pre-commit checks...
   Checking syntax... ✓
   Checking tests... ✓ (25/25 passed)
   Checking coverage...
      ✗ Coverage 78% < 85% required

❌ PRE-COMMIT CHECKS FAILED

Commit aborted. Coverage is 78% but 85%+ required.
   → Add more tests
   → Run: coverage report
   → Identify untested code
   → Add tests for missing lines
   → Try commit again
```

**Result:** Commit blocked until coverage reaches 85%.

### Scenario 3: Developer Tries with Type Errors

```bash
$ git commit -m "refactor: simplify auth"

🔍 Running pre-commit checks...
   Checking syntax... ✓
   Checking tests... ✓ (25/25 passed)
   Checking coverage... ✓ (92%)
   Checking types...
      ✗ error: Argument 1 to "authenticate" has incompatible type
        "str | None"; expected "str" [arg-type]

❌ PRE-COMMIT CHECKS FAILED

Commit aborted. Type errors detected.
   → Add type hints: def authenticate(token: str) -> bool:
   → Run: mypy --strict *.py
   → Try commit again
```

**Result:** Commit blocked. Type safety is non-negotiable.

### Scenario 4: Developer Tries with Security Issue

```bash
$ git commit -m "fix: add password validation"

🔍 Running pre-commit checks...
   Checking syntax... ✓
   Checking tests... ✓ (30/30 passed)
   Checking coverage... ✓ (95%)
   Checking types... ✓
   Checking security...
      ✗ Issue: Hardcoded password found
        Location: auth.py:45

❌ PRE-COMMIT CHECKS FAILED

Commit aborted. Security vulnerability detected.
   → Remove hardcoded secrets
   → Use environment variables or secrets manager
   → Run: bandit -r -ll *.py
   → Try commit again
```

**Result:** Commit blocked. Security issues are not allowed.

### Scenario 5: Developer Commits with All Gates Passing

```bash
$ git commit -m "feat(auth): add password reset"

🔍 Running pre-commit checks...
   Checking syntax... ✓
   Checking tests... ✓ (35/35 passed)
   Checking coverage... ✓ (92%)
   Checking types... ✓
   Checking security... ✓
   Checking linting... ✓ (9.1/10)

✓ Pre-commit checks passed

✓ Commit message format valid

[main abc1234] feat(auth): add password reset
 3 files changed, 45 insertions(+), 12 deletions(-)

✓ Commit successful
  Hash: abc1234
  Message: feat(auth): add password reset
```

**Result:** Commit succeeds. Automatically logged to audit trail.

## Why This Works

### 1. **Automation Removes Debate**
- No negotiating about "just this once"
- Hooks enforce standards automatically
- Everyone knows the same rules apply

### 2. **Fast Feedback**
- Developers know immediately if code is acceptable
- Failing tests show specific errors
- Coverage reports show exactly what's untested

### 3. **No Bypass Possible**
- Hooks run before commit is created (can't skip)
- `--no-verify` flag is documented as non-functional
- Standards apply universally

### 4. **Audit Trail Creates Accountability**
- Every commit is logged with full metadata
- Can query who committed what and when
- Compliance is verifiable

### 5. **Human Review Ensures Quality**
- Automated checks ensure technical standards
- Human reviewers ensure design quality
- Combined approach catches issues at multiple levels

## Configuration

### In `ansible/roles/git/defaults/main.yml`

```yaml
# Quality gate thresholds
git_pre_commit_checks:
  syntax_check: true
  tests_execution: true
  coverage_minimum: 85
  type_checking: true
  security_scan: true
  linting_minimum: 8.0

# Commit message validation
git_commit_msg_maxline: 50
git_commit_msg_check_type: true
git_commit_msg_check_scope: true
```

### In `ansible/roles/git/templates/hooks/pre-commit.sh.j2`

These values are templated at deployment time:
- Lines 21-66: Configurable checks
- Each check references configuration values
- Hooks are regenerated when config changes
- Handlers automatically reload hooks

## Enforcement Timeline

```
TIME    LAYER               ACTION
────────────────────────────────────────────────
       Setup Phase
────────────────────────────────────────────────
T0     Ansible             Deploy git role
       Configuration       Set quality thresholds
       Templates           Render hooks with config
       Permissions         Make hooks executable

────────────────────────────────────────────────
       Development Phase
────────────────────────────────────────────────
T1     Developer           Makes code changes
T2     Developer           Runs tests locally
T3     (Optional)          Runs ai_commit_validator.py
T4     Developer           Runs git commit
       Hook: pre-commit    Validates code quality
       Hook: commit-msg    Validates message format
       Commit created      Signed with GPG
       Hook: post-commit   Logs to audit trail
T5     Result              Commit successful or blocked

────────────────────────────────────────────────
       Review Phase
────────────────────────────────────────────────
T6     Developer           Creates pull request
       CI/CD               Runs checks again
T7     Reviewer            Reviews code
       Reviewer            Checks quality checklist
T8     Decision            Approve and merge or request changes
       Audit Trail         Logged with review status

────────────────────────────────────────────────
       Reporting Phase
────────────────────────────────────────────────
T9+    Leadership          Queries audit trail
       Metrics             Track coverage trends
       Compliance          Verify standards met
       Reports             Generate compliance reports
```

## Summary

The enforcement system works through **four complementary mechanisms**:

1. **Automated Hooks** - Prevent bad commits at the source
2. **Validator Tool** - Help developers catch issues early
3. **Human Review** - Ensure design and architecture quality
4. **Audit Trail** - Track accountability and verify compliance

This creates a **system that works** because:

- ✅ Automation handles technical checks (can't be skipped)
- ✅ Clear feedback tells developers exactly what's wrong
- ✅ Human judgment ensures quality beyond metrics
- ✅ Complete logging creates accountability
- ✅ All three layers together = production-ready code

**Result:** Every single commit to the repository is quality, clean, working code. No exceptions.
