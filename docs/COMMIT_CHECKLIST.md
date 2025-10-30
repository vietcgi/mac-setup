# Commit Checklist

**Before you commit any code to this repository, check these items.**

This checklist applies to everyone: humans, AI, automated systems - no exceptions.

## Pre-Commit Verification (5 minutes)

```
STEP 1: Code Quality
┌─────────────────────────────────────┐
□ No syntax errors
□ All imports valid
□ No undefined variables
□ Code runs without errors
□ No obvious bugs

Run: python3 -m py_compile *.py
```

```
STEP 2: Tests Pass
┌─────────────────────────────────────┐
□ All tests pass (100%)
□ No test failures
□ No test skips
□ No test timeouts
□ Run count same or higher

Run: pytest -v
```

```
STEP 3: Coverage Sufficient
┌─────────────────────────────────────┐
□ Overall coverage ≥ 85%
□ Critical paths ≥ 95%
□ No coverage drop
□ New code tested

Run: coverage report --fail-under=85
```

```
STEP 4: Type Safety
┌─────────────────────────────────────┐
□ All type hints present
□ Type hints correct
□ No implicit Any
□ mypy strict passes

Run: mypy --strict *.py
```

```
STEP 5: Security
┌─────────────────────────────────────┐
□ No hardcoded secrets
□ No SQL injection
□ Input validated
□ No vulnerabilities
□ No suspicious patterns

Run: bandit -r -ll *.py
```

```
STEP 6: Code Quality
┌─────────────────────────────────────┐
□ PEP 8 compliant
□ No high complexity
□ Clear variable names
□ Well-commented
□ Linting score ≥ 8.0

Run: pylint *.py
```

```
STEP 7: Documentation
┌─────────────────────────────────────┐
□ Module docstring present
□ Function docstrings present
□ Parameters documented
□ Returns documented
□ Examples provided

Run: pydocstyle *.py
```

## Commit Message Checklist

```
BEFORE WRITING COMMIT MESSAGE
┌─────────────────────────────────────┐
□ All changes complete
□ All tests passing
□ Coverage sufficient
□ Documentation done
□ Code reviewed by self
```

```
COMMIT MESSAGE FORMAT
┌─────────────────────────────────────┐
□ Subject ≤ 50 characters
□ Imperative mood (fix, add, update)
□ No period at end
□ Context in body
□ Testing info included
□ Coverage percentage included
□ Reference issue (#123)
```

### **Commit Message Template**

```
type(scope): brief subject [max 50 chars]

Explain what changed and why.

Testing:
- What tests were added
- Coverage percentage
- Test count

Fixes #123
```

### **Example Good Commit**

```
feat(auth): add password reset functionality

Added secure password reset flow with email verification.
Implements industry best practices including:
- Time-limited reset tokens
- Secure token generation
- Email verification
- Rate limiting

Testing:
- 12 new tests added
- 100% coverage on password_reset module
- Integration tests with email service
Coverage: 89%

Fixes #456
```

### **Example Bad Commit**

```
❌ fix: stuff
❌ Updated code
❌ Changes
❌ work in progress
❌ WIP: feature
```

## Final Verification (Before git commit)

```
FINAL CHECKLIST
┌─────────────────────────────────────┐

Code:
  □ Syntax valid
  □ Imports work
  □ Code runs

Tests:
  □ All pass (100%)
  □ Coverage ≥ 85%
  □ New tests added

Quality:
  □ Type check pass
  □ Security scan pass
  □ Linting ≥ 8.0
  □ Documented

Message:
  □ Clear description
  □ Testing info
  □ Coverage %
  □ Issue reference
  □ Proper format

System:
  □ GPG key ready
  □ Git configured
  □ No local changes

RESULT:
  □ Ready to commit
```

## Git Commands

```bash
# Stage files
git add file.py

# Verify before commit (runs quality checks)
python3 cli/commit_validator.py

# Make commit (hooks will validate)
git commit -S -m "type(scope): message"

# Verify commit signed
git log --show-signature -1

# View audit trail
cat ~/.devkit/git/commits.log | jq '.[-1]'
```

## What Happens During Commit

```
git commit
  ↓
1. Pre-commit hooks run
   ├─ Syntax check
   ├─ Tests (must pass 100%)
   ├─ Coverage (must be 85%+)
   ├─ Type check (must pass)
   ├─ Security (must pass)
   └─ Linting (must be 8.0+)
  ↓ (if ANY fails → COMMIT BLOCKED)
  ↓
2. Commit message validated
   ├─ Format check
   ├─ Length check
   └─ Content check
  ↓
3. Commit created
  ↓
4. GPG sign
  ↓
5. Log to audit trail
  ↓
6. Success!
```

## If Commit Fails

### **Failed Tests**

```
Error: test_auth.py::test_login FAILED

Action:
1. Look at the error
2. Fix the test or code
3. Re-run: pytest test_auth.py
4. Try commit again
```

### **Failed Coverage**

```
Error: Coverage 78% < 85% required

Action:
1. Add more tests
2. Check coverage report: coverage report
3. Identify untested code
4. Add tests for missing coverage
5. Re-run: coverage report
6. Try commit again
```

### **Failed Type Check**

```
Error: mypy found type errors

Action:
1. Read the error message
2. Fix the type hints
3. Re-run: mypy --strict *.py
4. Try commit again
```

### **Failed Security Scan**

```
Error: bandit found vulnerabilities

Action:
1. Read the vulnerability description
2. Fix the security issue
3. Remove hardcoded secrets
4. Add input validation
5. Re-run: bandit -r -ll *.py
6. Try commit again
```

## Quick Checklist (Minimal)

If in a hurry, do this minimum:

```
□ Run: pytest
   (must see "passed")

□ Run: coverage report --fail-under=85
   (must see "Coverage is X%")

□ Run: mypy --strict *.py
   (must see "Success: no issues")

□ Write commit message
   (must follow format)

□ Commit: git commit -S -m "message"
```

## Common Issues

### **"Coverage is 65%"**

- Add more tests
- Test edge cases
- Test error handling
- Until coverage ≥ 85%

### **"1 test failed"**

- Which test failed?
- Why did it fail?
- Fix the code
- Verify test passes
- Retry commit

### **"Type errors detected"**

- Add type hints
- Use proper types
- Run mypy again
- Until no errors

### **"Security vulnerability"**

- Don't hardcode secrets
- Validate input
- Escape output
- Remove sensitive data
- Rerun bandit

### **"Commit blocked"**

- This is correct behavior
- Fix the issue
- Re-validate
- Retry commit

## Questions?

**Q: Can I skip tests?**
A: No. Commit will be blocked.

**Q: Can I use --no-verify?**
A: No. The checks still run.

**Q: Can coverage be 84%?**
A: No. Minimum is 85%.

**Q: Can I commit failing tests?**
A: No. All tests must pass.

**Q: Can a senior person skip this?**
A: No. Same rules for everyone.

---

## Summary

Before every commit:

1. ✅ Tests pass (100%)
2. ✅ Coverage ≥ 85%
3. ✅ Type check pass
4. ✅ Security scan pass
5. ✅ Linting ≥ 8.0
6. ✅ Documentation complete
7. ✅ Message formatted correctly

**If all are ✅, commit!**
**If any are ❌, fix them.**

---

**Last Updated**: October 30, 2024
**Version**: 1.0.0
**Status**: Active Standard
