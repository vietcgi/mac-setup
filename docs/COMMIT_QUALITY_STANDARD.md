# Universal Commit Quality Standard

**Every commit to this repository MUST meet these quality standards.**

This applies to:
- ✅ AI-generated commits
- ✅ Human-written commits
- ✅ Automated commits
- ✅ All contributors
- ✅ No exceptions

## Table of Contents

1. [Core Requirement](#core-requirement)
2. [Quality Gates](#quality-gates)
3. [Testing Requirements](#testing-requirements)
4. [Commit Message Format](#commit-message-format)
5. [Validation Checklist](#validation-checklist)
6. [What Gets Blocked](#what-gets-blocked)
7. [Audit & Tracking](#audit--tracking)

## Core Requirement

```
┌─────────────────────────────────────────┐
│  BEFORE ANY COMMIT IS ACCEPTED           │
├─────────────────────────────────────────┤
│                                         │
│  ALL quality gates MUST pass:           │
│                                         │
│  ✓ Syntax check (no errors)             │
│  ✓ Tests (100% pass rate)               │
│  ✓ Coverage (85%+ minimum)              │
│  ✓ Type checking (strict mode)          │
│  ✓ Security scan (0 issues)             │
│  ✓ Code linting (8.0+ score)            │
│                                         │
│  NO EXCEPTIONS                          │
│  NO BYPASSING                           │
│  NO --no-verify                         │
│                                         │
└─────────────────────────────────────────┘
```

## Quality Gates

### **Hard Blocks (Commit CANNOT be made)**

```
If ANY of these fail → COMMIT BLOCKED

┌──────────────────────────────────┐
│ GATE 1: SYNTAX                   │
├──────────────────────────────────┤
│ ✗ FAIL if:                       │
│  • Code doesn't compile          │
│  • Invalid Python syntax         │
│  • Missing imports               │
│  • Undefined variables           │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ GATE 2: TESTS                    │
├──────────────────────────────────┤
│ ✗ FAIL if:                       │
│  • ANY test fails                │
│  • Test count decreases          │
│  • Tests don't run               │
│  • Pass rate < 100%              │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ GATE 3: COVERAGE                 │
├──────────────────────────────────┤
│ ✗ FAIL if:                       │
│  • Overall coverage < 85%        │
│  • Critical paths < 95%          │
│  • Security code < 100%          │
│  • Coverage decreases            │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ GATE 4: TYPE CHECKING            │
├──────────────────────────────────┤
│ ✗ FAIL if:                       │
│  • Type errors detected          │
│  • mypy strict mode fails        │
│  • Missing type hints            │
│  • Implicit Any types            │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ GATE 5: SECURITY                 │
├──────────────────────────────────┤
│ ✗ FAIL if:                       │
│  • Vulnerabilities found         │
│  • Hardcoded secrets             │
│  • SQL injection possible        │
│  • Known CVEs in deps            │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ GATE 6: LINTING                  │
├──────────────────────────────────┤
│ ✗ FAIL if:                       │
│  • Pylint score < 8.0            │
│  • Style violations              │
│  • Code smell detected           │
│  • Complexity issues             │
└──────────────────────────────────┘
```

### **Soft Warnings (Should pass, can override with review)**

```
If these fail → WARNING (review needed)

┌──────────────────────────────────┐
│ GATE 7: DOCUMENTATION            │
├──────────────────────────────────┤
│ ⚠️ WARN if:                      │
│  • Functions undocumented        │
│  • Parameters not documented     │
│  • Missing examples              │
│  • Unclear code                  │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ GATE 8: PERFORMANCE              │
├──────────────────────────────────┤
│ ⚠️ WARN if:                      │
│  • Obvious inefficiency          │
│  • N+1 queries                   │
│  • Memory leaks possible         │
│  • Response time > baseline      │
└──────────────────────────────────┘
```

## Testing Requirements

### **Unit Tests (Minimum 65% of test suite)**

Every function MUST have unit tests:

```python
✓ REQUIRED:
  - Normal case (happy path)
  - Edge cases (boundary conditions)
  - Error cases (exceptions)
  - Security cases (if applicable)
```

### **Integration Tests (Minimum 25% of test suite)**

Test component interactions:

```python
✓ REQUIRED:
  - Database operations
  - API calls
  - Service interactions
  - Transaction boundaries
```

### **End-to-End Tests (Minimum 10% of test suite)**

Test complete workflows:

```python
✓ REQUIRED:
  - User workflows
  - Main features
  - Error recovery
  - Alternative paths
```

### **Test Pass Rate: 100% (Non-Negotiable)**

```
0 failures = acceptable
1 failure = COMMIT BLOCKED

There are no exceptions to this rule.
```

## Commit Message Format

```
type(scope): subject

Body explaining change

Testing:
- Test 1: description
- Test 2: description

Coverage: XX%

Fixes #123
```

### **Commit Types**

```
feat    - New feature
fix     - Bug fix
refactor - Code restructuring
docs    - Documentation
test    - Test additions
chore   - Maintenance
perf    - Performance improvement
```

### **Commit Message Rules**

```
✓ MUST:
  - Subject line ≤ 50 characters
  - First line imperative mood
  - Explain what changed
  - Explain why it changed
  - Include test summary
  - Include coverage percentage

✗ MUST NOT:
  - Use past tense ("fixed" → "fix")
  - Have spelling errors
  - Be vague ("update stuff")
  - Omit context
  - Omit test info
```

## Validation Checklist

Before committing, verify:

### **Code Correctness**

```
□ No syntax errors
□ All imports valid
□ All variables defined
□ All functions tested
□ All parameters validated
□ Return values correct type
□ No unreachable code
□ All branches tested
```

### **Testing**

```
□ All tests pass (100%)
□ New tests added for changes
□ Edge cases tested
□ Error cases tested
□ Coverage ≥ 85%
□ Critical paths ≥ 95%
□ No test flakiness
□ Tests are deterministic
```

### **Type Safety**

```
□ All type hints present
□ Type hints correct
□ mypy strict passes
□ No implicit Any
□ Proper type conversions
□ No duck typing
```

### **Security**

```
□ No hardcoded secrets
□ Input validation
□ SQL injection prevented
□ XSS prevented
□ No authentication bypass
□ No privilege escalation
□ Secure defaults
```

### **Code Quality**

```
□ PEP 8 compliant
□ Pylint 8.0+
□ No high complexity
□ Functions focused
□ DRY principle
□ Readable variable names
□ Well-commented
```

### **Documentation**

```
□ Module docstring
□ Function docstrings
□ Parameter documentation
□ Return documentation
□ Exception documentation
□ Usage examples
□ Design decisions explained
```

## What Gets Blocked

### **Automatic Blocks (No exceptions)**

```
❌ Syntax errors anywhere
❌ ANY test failure
❌ Coverage drop
❌ Type errors
❌ Security issues
❌ Missing test coverage
❌ Hardcoded credentials
❌ Failing imports
❌ --no-verify attempts
```

### **Cannot Override**

```
These cannot be bypassed, even with --no-verify:

❌ Failing tests
❌ Syntax errors
❌ Type errors
❌ Security vulnerabilities
❌ Coverage below 85%

There is no --force option.
There is no way around these.
```

## Audit & Tracking

### **Every Commit Logged**

```
Location: ~/.devkit/git/commits.log (JSONL)

Fields recorded:
- timestamp
- commit_hash
- author
- subject
- files_changed
- lines_added
- lines_removed
- tests_passed
- tests_total
- coverage
- type_check
- security_scan
- linting_score
- review_status
- signature (GPG)
```

### **Query Examples**

```bash
# All commits today
cat ~/.devkit/git/commits.log | \
  jq '.[] | select(.timestamp | startswith("2024-10-30"))'

# Low coverage commits
cat ~/.devkit/git/commits.log | \
  jq '.[] | select(.coverage < 85)'

# Failed security scans
cat ~/.devkit/git/commits.log | \
  jq '.[] | select(.security_scan != "passed")'

# By contributor
cat ~/.devkit/git/commits.log | \
  jq '.[] | select(.author == "alice@example.com")'
```

### **Statistics**

```bash
# Average test pass rate
cat ~/.devkit/git/commits.log | \
  jq '[.[] | (.tests_passed / .tests_total * 100)] | add / length'

# Average coverage
cat ~/.devkit/git/commits.log | \
  jq '[.[] | .coverage] | add / length'

# Total commits
cat ~/.devkit/git/commits.log | wc -l
```

## Pre-Commit Hook Integration

The git role includes hooks that enforce these standards:

```bash
~/.git-templates/hooks/pre-commit
  ├─ Syntax check
  ├─ Run tests
  ├─ Check coverage
  ├─ Type checking
  ├─ Security scan
  └─ Linting
```

## Exceptions Policy

### **There are NO exceptions**

```
Q: Can I skip tests?
A: No.

Q: Can I use --no-verify?
A: No. It won't work anyway.

Q: Can I commit if coverage drops?
A: No.

Q: Can I commit if a test fails?
A: No.

Q: Can I bypass type checking?
A: No.

Q: Can a senior developer skip validation?
A: No. Same rules for everyone.

Q: Can I commit at 11pm to meet deadline?
A: No. Standards don't change by time.

Q: Can I add security-critical code without testing?
A: Absolutely not.
```

## Configuration

In `group_vars/all.yml`:

```yaml
# Commit Quality Standards
git_commit_quality:
  # Hard requirements (block commits)
  enforce_syntax_check: true
  enforce_test_execution: true
  enforce_test_coverage: true
  enforce_type_checking: true
  enforce_security_scan: true
  enforce_linting: true

  # Thresholds
  minimum_coverage: 85
  critical_path_coverage: 95
  minimum_pylint_score: 8.0
  security_issues_allowed: 0
  type_errors_allowed: 0
  test_failures_allowed: 0

  # Options
  allow_bypass: false
  allow_skip_verification: false
  require_gpg_signature: true
  log_all_commits: true

  # Tools
  coverage_tool: pytest-cov
  type_checker: mypy
  linter: pylint
  security_scanner: bandit
  formatter: black
```

## Enforcement

### **Who enforces this?**

```
✓ Git hooks (automatic)
✓ Pre-commit checks
✓ CI/CD pipeline
✓ Code review (humans)
✓ Audit trail (compliance)
```

### **What happens if violated?**

```
1. Commit is blocked
2. Error message shown
3. Issues logged
4. User must fix
5. Re-commit with validation pass
```

## Benefits

✅ **Code Quality**
- Every commit meets standards
- No technical debt accumulation
- Consistent codebase

✅ **Reliability**
- All tests pass (100%)
- All security scanned
- All types checked

✅ **Maintainability**
- Well-documented code
- No surprises later
- Easy to understand

✅ **Accountability**
- Complete audit trail
- Who committed what
- When and why

✅ **Safety**
- No breaking changes
- No regressions
- No security issues

## Examples

### ✅ GOOD: Commit that passes

```
$ git commit -m "feat(auth): add password reset"

✓ Syntax check: PASS
✓ Tests (25/25): PASS
✓ Coverage: 92%
✓ Type check: PASS
✓ Security: PASS
✓ Linting: 9.1/10

✅ COMMIT ACCEPTED
```

### ❌ BAD: Commit that fails

```
$ git commit -m "fix: stuff"

✗ Syntax check: FAIL
  Missing import: DatabaseError on line 45

❌ COMMIT BLOCKED
Fix the error and try again.
```

### ❌ BAD: Test failure

```
$ git commit -m "refactor: optimize query"

✓ Syntax check: PASS
✗ Tests: FAIL
  test_auth.py::test_login_invalid_password FAILED

❌ COMMIT BLOCKED
All tests must pass (currently 24/25).
```

### ❌ BAD: Coverage drop

```
$ git commit -m "feat: new feature"

✓ Syntax check: PASS
✓ Tests: PASS
✗ Coverage: 78% (was 85%)

❌ COMMIT BLOCKED
Coverage decreased. Add tests to reach 85%+.
```

## Summary

**Every single commit to this repository:**

✅ Compiles without errors
✅ Passes 100% of tests
✅ Has 85%+ test coverage
✅ Passes type checking (strict)
✅ Has 0 security issues
✅ Meets linting standards
✅ Is fully documented
✅ Is GPG signed
✅ Is logged and auditable

**This is not optional. This is the standard.**

---

**Status**: Standard Established ✅
**Applies To**: All commits (no exceptions)
**Enforcement**: Automatic + Manual
**Version**: 1.0.0
**Created**: October 30, 2024
