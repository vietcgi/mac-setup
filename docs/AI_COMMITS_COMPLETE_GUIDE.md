# Complete Guide: AI Commits with Quality Assurance

Comprehensive guide to AI-generated commits with built-in quality assurance, ensuring working, well-documented code.

## Quick Overview

```
┌─────────────────────────────────────────────────────────────┐
│          AI COMMIT QUALITY ASSURANCE SYSTEM                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  AI generates code                                          │
│         ↓                                                   │
│  ┌───────────────────────────────────────────┐            │
│  │ QUALITY GATE 1: CODE CORRECTNESS          │            │
│  │ ✓ Syntax check                            │            │
│  │ ✓ All tests pass (100%)                   │            │
│  │ ✓ Type checking (mypy strict)             │            │
│  │ ✓ Security scan (bandit)                  │            │
│  │ ✓ Coverage 85%+ (critical 95%+)          │            │
│  └───────────────────────────────────────────┘            │
│         ↓ (MUST PASS - blocks commit if fails)             │
│  ┌───────────────────────────────────────────┐            │
│  │ QUALITY GATE 2: CODE QUALITY              │            │
│  │ ✓ Linting (pylint 8.0+)                   │            │
│  │ ✓ Complexity check (no high complexity)   │            │
│  │ ✓ Code style (PEP 8)                      │            │
│  │ ✓ Documentation complete                  │            │
│  └───────────────────────────────────────────┘            │
│         ↓ (SHOULD PASS - blocks commit if fails)           │
│  ┌───────────────────────────────────────────┐            │
│  │ QUALITY GATE 3: AUDIT & METADATA          │            │
│  │ ✓ Add [AI] marker                         │            │
│  │ ✓ Add confidence score                    │            │
│  │ ✓ Add generated-by field                  │            │
│  │ ✓ Add unique commit ID                    │            │
│  │ ✓ Log to audit trail                      │            │
│  │ ✓ GPG sign commit                         │            │
│  └───────────────────────────────────────────┘            │
│         ↓ (automatic)                                      │
│  COMMIT SAFELY STORED                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Three-Tier Quality System

### **Tier 1: CODE CORRECTNESS** (Hard Requirements)

**"Working Code, Not Buggy"**

```
GATE              REQUIREMENT              CONSEQUENCE
────────────────────────────────────────────────────────
Syntax            Must compile             ❌ BLOCK if fails
Tests             All must pass            ❌ BLOCK if fails
Coverage          85%+ required            ❌ BLOCK if fails
Type Checking     mypy strict              ❌ BLOCK if fails
Security          No vulnerabilities       ❌ BLOCK if fails
```

**Tools & Checks:**

```bash
# 1. Syntax & Compilation
python3 -m py_compile *.py

# 2. Test Execution (must be 100% pass)
pytest --tb=short -v

# 3. Code Coverage (must be 85%+ minimum)
coverage run -m pytest
coverage report --fail-under=85

# 4. Type Checking (strict mode)
mypy --strict *.py

# 5. Security Scan
bandit -r -ll *.py
```

**Example: Corrected Code**

```python
# ❌ WRONG: Missing error handling
def get_user_by_id(user_id: int):
    return database.query(User).filter(User.id == user_id).first()

# ✅ RIGHT: Complete error handling
def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID with proper error handling.

    Args:
        user_id: User ID to fetch

    Returns:
        User object or None if not found

    Raises:
        ValueError: If user_id is invalid
        DatabaseError: If database query fails
    """
    # Validate input
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")

    try:
        user = database.query(User).filter(User.id == user_id).first()
        return user
    except DatabaseError as e:
        logging.error(f"Database error fetching user {user_id}: {e}")
        raise DatabaseError(f"Failed to fetch user: {e}")
    except Exception as e:
        logging.error(f"Unexpected error fetching user {user_id}: {e}")
        raise


# ✅ TESTS: 100% coverage
class TestGetUserById:
    def test_valid_user(self):
        """Test getting valid user"""
        user = get_user_by_id(1)
        assert user.id == 1

    def test_nonexistent_user(self):
        """Test getting nonexistent user"""
        user = get_user_by_id(9999)
        assert user is None

    def test_invalid_id_zero(self):
        """Test with user_id=0"""
        with pytest.raises(ValueError):
            get_user_by_id(0)

    def test_invalid_id_negative(self):
        """Test with negative user_id"""
        with pytest.raises(ValueError):
            get_user_by_id(-1)

    def test_invalid_id_string(self):
        """Test with non-integer input"""
        with pytest.raises(ValueError):
            get_user_by_id("invalid")

    def test_database_error(self, mocker):
        """Test handling database errors"""
        mocker.patch('database.query', side_effect=DatabaseError("Connection lost"))
        with pytest.raises(DatabaseError):
            get_user_by_id(1)
```

### **Tier 2: CODE QUALITY** (Soft Requirements)

**"Well-Written, Maintainable Code"**

```
GATE              REQUIREMENT              CONSEQUENCE
────────────────────────────────────────────────────────
Linting           pylint 8.0+              ⚠️ WARN if fails
Complexity        No high complexity       ⚠️ WARN if fails
Style             PEP 8 compliant          ⚠️ WARN if fails
Docs              All functions docs       ⚠️ WARN if fails
```

**Tools & Checks:**

```bash
# 1. Code Linting
pylint --fail-under=8.0 *.py

# 2. Complexity Check
radon cc -a *.py

# 3. Code Style
flake8 *.py

# 4. Documentation Check
pydocstyle *.py
```

### **Tier 3: AUDIT & METADATA** (Tracking)

**"Complete Accountability Trail"**

```
Field                   Purpose                    Automated
──────────────────────────────────────────────────────────
[AI] marker            Identify AI commits         Yes
Generated-By           Which AI model              Yes
Confidence             AI confidence %             Yes (from tests)
Review-Status          Human review status         Manual/Auto
Commit-ID              Unique identifier           Yes
Timestamp              When generated              Yes
Test Results           Coverage & test counts      Yes
Signature              GPG signature               Yes
```

## Commit Message Template

```
feat(scope): brief description [AI]

Context:
Why was this change needed? What problem does it solve?

Changes:
- Specific change 1
- Specific change 2
- Specific change 3

Testing:
What tests were added/modified?
- Test 1: description
- Test 2: description
Code coverage: 87%

Documentation:
What documentation was added/updated?
- Feature documentation
- API documentation

Reasoning:
Why was this approach chosen over alternatives?
What design decisions were made?

Generated-By: claude-3.5-sonnet
Confidence: 92%
Review-Status: pending
Commit-ID: ai-20241030-abc123
Timestamp: 2024-10-30T15:30:45Z
Files-Changed: 5
Tests-Passed: 45/45
Coverage: 87%
```

## Step-by-Step Process

### **Step 1: AI Generates Code**

```
Input:  Feature request
Output: Code + initial commit message
```

### **Step 2: Syntax & Compilation Check**

```bash
# Automatic check before anything else
python3 -m py_compile new_code.py
if [ $? -ne 0 ]; then
    echo "❌ Syntax error - cannot proceed"
    exit 1
fi
```

### **Step 3: Run ALL Tests**

```bash
# Unit, integration, and E2E tests MUST pass 100%
pytest -v --tb=short

# Example output:
# test_auth.py::test_valid_login PASSED
# test_auth.py::test_invalid_password PASSED
# test_auth.py::test_empty_email PASSED
# ... 42 more tests ...
# ===================== 45 passed in 2.31s =====================
```

### **Step 4: Check Code Coverage**

```bash
# Coverage must be 85%+ overall, 95%+ for critical paths
coverage run -m pytest
coverage report

# Example output:
# Name                Stmts   Miss  Cover   Missing
# ─────────────────────────────────────────────────
# auth.py               150     15    90%    42-45, 67-70
# models.py              200     10    95%    156-160
# utils.py               80      5    94%    45-49
# ─────────────────────────────────────────────────
# TOTAL                 430     30    93%
#
# Coverage is 93% (>85% ✓)
```

### **Step 5: Type Checking**

```bash
# All types must be checked in strict mode
mypy --strict auth.py models.py utils.py

# Example output:
# Success: no issues found in 3 source files
```

### **Step 6: Security Scan**

```bash
# No vulnerabilities allowed
bandit -r -ll *.py

# Example output:
# No issues identified in code scanned
```

### **Step 7: Linting**

```bash
# Code must meet linting standards
pylint --fail-under=8.0 *.py

# Example output:
# Your code has been rated at 8.5/10
```

### **Step 8: Generate Metadata**

```
Timestamp: 2024-10-30T15:30:45Z
Generated-By: claude-3.5-sonnet
Tests-Passed: 45/45
Coverage: 93%
Confidence: 92% (calculated from test results)
Commit-ID: ai-20241030-feat-auth-abc123
```

### **Step 9: GPG Sign**

```bash
# Sign with GPG key
git commit -S -m "feat(auth): add MFA support [AI]"

# Verify signature
git verify-commit HEAD
# Good signature from <GPG Key>
```

### **Step 10: Log to Audit Trail**

```json
{
  "timestamp": "2024-10-30T15:30:45Z",
  "commit_hash": "abc123def456",
  "ai_model": "claude-3.5-sonnet",
  "subject": "feat(auth): add MFA support",
  "tests_passed": 45,
  "coverage": 93,
  "confidence": 92,
  "signed": true,
  "security_scan": "passed",
  "review_status": "pending"
}
```

## Real Example: Complete Flow

### **Scenario: Adding User Two-Factor Authentication**

**Step 1: AI Generates Code**

```python
class TwoFactorAuth:
    """Two-factor authentication service"""

    def setup_totp(self, user_id: int) -> str:
        """Setup TOTP for user"""
        secret = pyotp.random_base32()
        user = User.get(user_id)
        user.totp_secret = secret
        user.save()
        return secret

    def verify_totp(self, user_id: int, token: str) -> bool:
        """Verify TOTP token"""
        user = User.get(user_id)
        return pyotp.TOTP(user.totp_secret).verify(token)
```

**Step 2: Syntax Check** ✅ PASS

**Step 3: Run Tests** (AI also generated tests)

```python
class TestTwoFactorAuth:
    def test_setup_totp(self):
        """Test TOTP setup"""
        user = User.create(email="test@example.com")
        auth = TwoFactorAuth()
        secret = auth.setup_totp(user.id)
        assert user.totp_secret == secret
        assert len(secret) == 32  # Base32 length

    def test_verify_valid_token(self):
        """Test valid TOTP token verification"""
        user = User.create(email="test@example.com")
        secret = "JBSWY3DPEBLW64TMMQ======"  # Test secret
        user.totp_secret = secret
        user.save()

        # Generate valid token
        totp = pyotp.TOTP(secret)
        token = totp.now()

        auth = TwoFactorAuth()
        assert auth.verify_totp(user.id, token) == True

    def test_verify_invalid_token(self):
        """Test invalid TOTP token rejection"""
        user = User.create(email="test@example.com")
        user.totp_secret = "JBSWY3DPEBLW64TMMQ======"
        user.save()

        auth = TwoFactorAuth()
        assert auth.verify_totp(user.id, "000000") == False

    def test_verify_expired_token(self):
        """Test expired TOTP token rejection"""
        user = User.create(email="test@example.com")
        user.totp_secret = "JBSWY3DPEBLW64TMMQ======"
        user.save()

        auth = TwoFactorAuth()
        # Use old timestamp to simulate expired token
        import time
        old_time = int(time.time()) - 120
        totp = pyotp.TOTP(user.totp_secret)
        token = totp.at(old_time)

        assert auth.verify_totp(user.id, token) == False

    def test_user_not_found(self):
        """Test handling nonexistent user"""
        auth = TwoFactorAuth()
        with pytest.raises(UserNotFoundError):
            auth.verify_totp(9999, "123456")
```

**Step 4: Coverage Check** ✅ PASS (100%)

**Step 5: Type Check** ✅ PASS

**Step 6: Security Scan** ✅ PASS (no vulnerabilities)

**Step 7: Linting** ✅ PASS (score 9.1/10)

**Step 8: Create Commit Message**

```
feat(auth): add two-factor authentication with TOTP [AI]

Context:
Users have requested two-factor authentication support to enhance
account security. This implementation adds Time-based One-Time
Password (TOTP) support, compatible with authenticator apps like
Google Authenticator and Authy.

Changes:
- Added TwoFactorAuth service class
- Added user.totp_secret field to User model
- Added database migration for new field
- Added /auth/2fa/setup endpoint
- Added /auth/2fa/verify endpoint
- Added comprehensive test suite (100% coverage)
- Updated user documentation

Testing:
- 8 unit tests added, all passing
- Coverage: 100%
- Integration tests with database: PASS
- E2E user flow tests: PASS
- Security vulnerabilities scan: PASS (0 issues)

Documentation:
- Added TOTP setup guide
- Added TOTP verification flow documentation
- Added troubleshooting guide for authenticator apps
- Added API documentation

Reasoning:
TOTP was chosen over SMS-based 2FA because:
1. No external service dependency (lower cost)
2. Better security (not vulnerable to SIM swapping)
3. Industry standard (works with all authenticator apps)
4. Better user experience (works offline)

Generated-By: claude-3.5-sonnet
Confidence: 95%
Review-Status: pending
Commit-ID: ai-20241030-feat-auth-totp-abc123
Timestamp: 2024-10-30T15:30:45Z
Files-Changed: 8
Lines-Added: 245
Lines-Removed: 0
Tests-Passed: 8/8
Coverage: 100%
Type-Check: PASS
Security-Scan: PASS (0 vulns)
Pylint-Score: 9.1/10
```

**Step 9: GPG Sign** ✅ SIGNED

**Step 10: Commit Created**

```
✅ COMMIT SUCCESSFUL

Hash: abc123def456
Subject: feat(auth): add two-factor authentication with TOTP [AI]
Author: AI (claude-3.5-sonnet)
Signed: Yes (verified)

Quality Summary:
  Tests: 8/8 passed (100%)
  Coverage: 100%
  Type-check: PASS
  Security: PASS (0 vulns)
  Linting: 9.1/10
  Confidence: 95%

Status: Safe to merge (meets all quality gates)
```

## Integration with Git Workflow

### **Hook Configuration**

```bash
# ~/.git-templates/hooks/ai-commit-validate
#!/bin/bash

echo "🤖 Validating AI commit..."

# Get staged files
STAGED_FILES=$(git diff --cached --name-only)

# 1. Syntax check
python3 -m py_compile $STAGED_FILES 2>/dev/null || exit 1

# 2. Run tests (must pass 100%)
pytest -q || exit 1

# 3. Coverage check (must be 85%+)
coverage report --fail-under=85 || exit 1

# 4. Type checking
mypy --strict $STAGED_FILES || exit 1

# 5. Security scan
bandit -q -ll $STAGED_FILES || exit 1

echo "✅ AI commit validation passed"
exit 0
```

### **Pre-commit Configuration**

```yaml
# In .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ai-commit-validate
        name: AI Commit Validation
        entry: bash ~/.git-templates/hooks/ai-commit-validate
        language: system
        stages: [commit]
        pass_filenames: false
```

## Configuration

```yaml
# In group_vars/all.yml

git_ai_quality_gates:
  # Blocking gates (MUST PASS)
  syntax_check:
    enabled: true
    blocking: true

  unit_tests:
    enabled: true
    blocking: true
    must_pass: 100%

  test_coverage:
    enabled: true
    blocking: true
    minimum: 85%
    critical_paths: 95%

  type_checking:
    enabled: true
    blocking: true
    mode: strict

  security_scan:
    enabled: true
    blocking: true
    allowed_severities: []  # No issues allowed

  # Warning gates (SHOULD PASS)
  linting:
    enabled: true
    blocking: false
    minimum_score: 8.0

  code_complexity:
    enabled: true
    blocking: false
    max_complexity: 10

  documentation:
    enabled: true
    blocking: false
    required_for_functions: true
```

## Audit & Reporting

### **View All AI Commits**

```bash
cat ~/.devkit/git/ai-commits.log | jq '.' | head -50
```

### **Generate Quality Report**

```bash
python3 ~/devkit/cli/ai_commit_manager.py report --period month
```

### **Search by Criteria**

```bash
# Low confidence commits
cat ~/.devkit/git/ai-commits.log | jq '.[] | select(.confidence < 70)'

# Unreviewed commits
cat ~/.devkit/git/ai-commits.log | jq '.[] | select(.review_status == "pending")'

# By AI model
cat ~/.devkit/git/ai-commits.log | jq '.[] | select(.ai_model == "claude-3.5-sonnet")'
```

## Summary

**Three-Tier Quality Assurance:**

1. ✅ **Correctness** (Hard blocks): Tests, types, security
2. ✅ **Quality** (Soft warns): Linting, complexity, docs
3. ✅ **Audit** (Automatic): Metadata, logging, signing

**Result: Working, Well-Tested Code**

---

**Status**: Complete Guide ✅
**Focus**: Quality, Correctness, Accountability
**Last Updated**: October 30, 2024
