# AI Code Correctness Framework

Comprehensive framework ensuring AI-generated code is **working, not buggy**. Focuses on correctness, reliability, and production-readiness.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Testing Strategy](#testing-strategy)
3. [Verification Checklist](#verification-checklist)
4. [Quality Gates](#quality-gates)
5. [Runtime Validation](#runtime-validation)
6. [Integration Testing](#integration-testing)
7. [Failure Modes](#failure-modes)
8. [Implementation](#implementation)

## Core Principles

### **Three Rules of Correct Code**

```
RULE 1: TESTS PASS
├─ Unit tests pass 100%
├─ Integration tests pass 100%
├─ E2E tests pass 100%
└─ Minimum coverage: 85%

RULE 2: LOGIC IS SOUND
├─ No undefined behavior
├─ No race conditions
├─ No memory issues
├─ Error handling complete

RULE 3: WORKS IN PRODUCTION
├─ Handles edge cases
├─ Handles errors gracefully
├─ Performance acceptable
├─ No regressions introduced
```

### **Test Pyramid for AI Code**

```
                    ▲
                   /│\
                  / │ \
                 /  │  \  E2E Tests (10%)
                /   │   \
               ───────────
              /     │     \
             /      │      \  Integration (25%)
            /       │       \
           ─────────────────
          /         │         \
         /          │          \  Unit Tests (65%)
        /           │           \
       ▼────────────────────────▼
```

**Test Coverage by Level:**
- **Unit Tests**: 65% of test suite (test individual functions)
- **Integration Tests**: 25% of test suite (test component interactions)
- **E2E Tests**: 10% of test suite (test complete workflows)

**Minimum Coverage Thresholds:**
- Overall: 85% code coverage
- Critical paths: 95% code coverage
- Security code: 100% code coverage
- Business logic: 90% code coverage

## Testing Strategy

### **Unit Testing**

Every function MUST have unit tests:

```python
# ✓ GOOD: Comprehensive unit tests
class TestUserAuthentication:
    def test_valid_credentials(self):
        """Test authentication with valid credentials"""
        user = User.authenticate("user@example.com", "password123")
        assert user is not None
        assert user.email == "user@example.com"

    def test_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        user = User.authenticate("user@example.com", "wrongpass")
        assert user is None

    def test_empty_email(self):
        """Test authentication with empty email"""
        user = User.authenticate("", "password")
        assert user is None

    def test_empty_password(self):
        """Test authentication with empty password"""
        user = User.authenticate("user@example.com", "")
        assert user is None

    def test_sql_injection_attempt(self):
        """Test authentication prevents SQL injection"""
        user = User.authenticate("' OR '1'='1", "password")
        assert user is None

    def test_password_hashing(self):
        """Test password is properly hashed"""
        user = User.create("user@example.com", "password123")
        assert user.password_hash != "password123"
        assert user.password_hash == User.hash_password("password123")
```

**Unit Test Requirements:**
- ✅ Test normal cases
- ✅ Test edge cases
- ✅ Test error cases
- ✅ Test security cases
- ✅ Test boundary conditions
- ✅ 100% function coverage

### **Integration Testing**

Test component interactions:

```python
# ✓ GOOD: Integration test
def test_user_signup_flow():
    """Test complete signup flow"""
    # Setup
    email = "newuser@example.com"
    password = "SecurePass123!"

    # Act
    user = User.create(email, password)
    user.send_verification_email()
    verification_link = EmailService.get_latest_verification_link(email)
    user.verify_email(verification_link)
    user.save()

    # Assert
    assert user.email_verified == True
    assert user.is_active == True
    assert database.get_user(email) is not None

    # Verify side effects
    assert EmailService.get_unverified_emails().count() == 0
    assert AuditLog.get_latest_event("USER_CREATED").user_id == user.id
```

**Integration Test Requirements:**
- ✅ Test actual database interactions
- ✅ Test API interactions
- ✅ Test event handling
- ✅ Test transaction boundaries
- ✅ Test external service calls

### **End-to-End Testing**

Test complete user workflows:

```python
# ✓ GOOD: E2E test
@pytest.mark.e2e
def test_user_authentication_flow():
    """Test complete auth flow: signup -> login -> access protected resource"""
    # Setup
    client = TestClient(app)
    email = "e2e@example.com"
    password = "SecurePass123!"

    # 1. Signup
    response = client.post("/auth/signup", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 201
    user_id = response.json()["user_id"]

    # 2. Verify email (skip verification for test)
    User.get(user_id).update(email_verified=True)

    # 3. Login
    response = client.post("/auth/login", json={
        "email": email,
        "password": password
    })
    assert response.status_code == 200
    token = response.json()["token"]

    # 4. Access protected resource
    response = client.get(
        "/api/user/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == email

    # 5. Logout
    response = client.post("/auth/logout")
    assert response.status_code == 200

    # 6. Verify can't access without token
    response = client.get("/api/user/profile")
    assert response.status_code == 401
```

**E2E Test Requirements:**
- ✅ Test real workflows
- ✅ Test end-to-end scenarios
- ✅ Test error recovery
- ✅ Test success paths
- ✅ Test alternative paths

## Verification Checklist

Before ANY AI-generated code commit, verify:

### **Code Correctness**

```
Code Correctness Checklist
═══════════════════════════════════════════════════════════

LOGIC & CORRECTNESS
  □ No syntax errors
  □ All imports valid
  □ All variables defined before use
  □ All function parameters validated
  □ Return values correct type
  □ No unreachable code
  □ All branches tested

ERROR HANDLING
  □ All exceptions caught
  □ Error messages clear
  □ Graceful degradation on errors
  □ Proper error logging
  □ Rollback on transaction failure
  □ Cleanup on exception
  □ No silent failures

TYPE SAFETY
  □ All type hints present
  □ Type hints correct
  □ Type checking passes (mypy)
  □ No implicit None returns
  □ Proper type conversions
  □ No duck typing issues

CONCURRENCY (if applicable)
  □ No race conditions
  □ Thread-safe operations
  □ Proper locking
  □ Atomic operations
  □ Deadlock-free
  □ No shared state issues
```

### **Testing**

```
Testing Checklist
═══════════════════════════════════════════════════════════

UNIT TESTS
  □ All functions have unit tests
  □ Normal cases tested (50% of tests)
  □ Edge cases tested (30% of tests)
  □ Error cases tested (15% of tests)
  □ Security cases tested (5% of tests)
  □ All tests pass
  □ 85%+ code coverage

INTEGRATION TESTS
  □ Component interactions tested
  □ Database operations tested
  □ API endpoints tested
  □ Event handling tested
  □ Transaction boundaries tested
  □ All tests pass
  □ Real database used (not mocked)

E2E TESTS
  □ Main workflows tested
  □ User journeys tested
  □ Error paths tested
  □ Alternative paths tested
  □ Recovery paths tested
  □ All tests pass
  □ Real environment used

PERFORMANCE TESTS (where needed)
  □ Response times acceptable
  □ Database queries optimized
  □ No memory leaks
  □ Scaling tested
  □ Load tests pass
```

### **Security**

```
Security Checklist
═══════════════════════════════════════════════════════════

INPUT VALIDATION
  □ All inputs validated
  □ SQL injection prevented
  □ XSS prevented
  □ CSRF prevented
  □ Path traversal prevented
  □ Type validation
  □ Length validation

AUTHENTICATION & AUTHORIZATION
  □ Only authorized access allowed
  □ Sessions properly handled
  □ Tokens properly validated
  □ Passwords properly hashed
  □ No hardcoded secrets
  □ Keys properly managed
  □ No information disclosure

DATA PROTECTION
  □ Sensitive data encrypted
  □ Encryption keys secure
  □ No data logged
  □ Secure deletion implemented
  □ Access controls enforced
  □ Audit trail maintained

DEPENDENCIES
  □ No known vulnerabilities
  □ All dependencies pinned
  □ Minimal dependencies
  □ Regular updates checked
  □ Security patches applied
```

### **Documentation**

```
Documentation Checklist
═══════════════════════════════════════════════════════════

CODE DOCUMENTATION
  □ Module docstrings present
  □ Function docstrings present
  □ Parameter documentation
  □ Return value documentation
  □ Exception documentation
  □ Complex logic explained
  □ Assumptions documented

USAGE DOCUMENTATION
  □ How to use documented
  □ Examples provided
  □ API documented
  □ Configuration documented
  □ Error handling documented
  □ Edge cases documented

REQUIREMENTS
  □ Requirements.txt updated
  □ Version conflicts resolved
  □ New dependencies justified
  □ License compatible
  □ Installation instructions clear
```

## Quality Gates

### **Automated Quality Gates**

Every commit MUST pass:

```
╔════════════════════════════════════════════════════════════╗
║                    QUALITY GATES (GO/NO-GO)               ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║ GATE 1: SYNTAX & IMPORTS                                  ║
│   ✓ MUST PASS                                             ║
│   - No syntax errors                                       ║
│   - All imports valid                                      ║
│   - Python compiles                                        ║
│   ├─ FAIL → BLOCK COMMIT                                  ║
│                                                            ║
║ GATE 2: UNIT TESTS                                         ║
│   ✓ MUST PASS                                             ║
│   - All unit tests pass                                    ║
│   - 85%+ code coverage                                     ║
│   - Critical paths 95%+                                    ║
│   ├─ FAIL → BLOCK COMMIT                                  ║
│                                                            ║
║ GATE 3: INTEGRATION TESTS                                  ║
│   ✓ MUST PASS                                             ║
│   - All integration tests pass                             ║
│   - Database operations verified                           ║
│   - API interactions verified                              ║
│   ├─ FAIL → BLOCK COMMIT                                  ║
│                                                            ║
║ GATE 4: TYPE CHECKING                                      ║
│   ✓ MUST PASS                                             ║
│   - mypy passes with strict settings                       ║
│   - No type errors                                         ║
│   - All annotations present                                ║
│   ├─ FAIL → BLOCK COMMIT                                  ║
│                                                            ║
║ GATE 5: SECURITY                                           ║
│   ✓ MUST PASS                                             ║
│   - No SQL injection                                       ║
│   - No hardcoded secrets                                   ║
│   - No vulnerabilities detected                            ║
│   ├─ FAIL → BLOCK COMMIT                                  ║
│                                                            ║
║ GATE 6: LINTING                                            ║
│   ✓ MUST PASS                                             ║
│   - Code style checks pass                                 ║
│   - pylint score 8.0+                                      ║
│   - No style violations                                    ║
│   ├─ FAIL → BLOCK COMMIT                                  ║
│                                                            ║
║ GATE 7: DOCUMENTATION                                      ║
│   ✓ MUST PASS                                             ║
│   - All functions documented                               ║
│   - All parameters documented                              ║
│   - Usage examples provided                                ║
│   ├─ WARN → REQUIRE REVIEW                                ║
│                                                            ║
║ GATE 8: PERFORMANCE                                        ║
│   ✓ ACCEPTABLE                                            ║
│   - No obvious performance issues                          ║
│   - Database queries optimized                             ║
│   - No N+1 queries                                         ║
│   ├─ FAIL → REQUIRE INVESTIGATION                         ║
│                                                            ║
║ OVERALL RESULT                                             ║
│ ALL GATES → SAFE TO COMMIT                                ║
│ ANY FAILED → BLOCK COMMIT                                 ║
│                                                            ║
╚════════════════════════════════════════════════════════════╝
```

### **Gate Configuration**

```yaml
# In git role defaults
git_ai_quality_gates:
  syntax_check:
    enabled: true
    blocking: true

  unit_tests:
    enabled: true
    blocking: true
    min_coverage: 85

  integration_tests:
    enabled: true
    blocking: true

  type_checking:
    enabled: true
    blocking: true

  security_check:
    enabled: true
    blocking: true

  linting:
    enabled: true
    blocking: true
    min_score: 8.0

  documentation:
    enabled: true
    blocking: false  # Warning only

  performance:
    enabled: true
    blocking: false  # Investigation required
```

## Runtime Validation

### **Production Readiness Check**

```python
# MUST pass before production deployment
def verify_production_ready(commit_hash):
    checks = {
        "all_tests_pass": run_all_tests(),
        "no_warnings": check_no_warnings(),
        "coverage_sufficient": check_coverage(min=90),
        "security_passed": run_security_checks(),
        "performance_acceptable": check_performance(),
        "backwards_compatible": check_compatibility(),
        "data_migration_safe": verify_migrations(),
        "rollback_plan": has_rollback_procedure(),
    }

    if not all(checks.values()):
        raise ProductionReadyError(
            f"Not production ready: {checks}"
        )

    return True
```

### **Failure Scenarios**

Every AI commit must handle:

```python
# CRITICAL: All failure modes must be handled

class UserAuthentication:
    def login(self, email: str, password: str) -> Optional[User]:
        """Login user - handles all failure modes"""

        # FAIL 1: Invalid input
        if not email or not password:
            logging.warning(f"Empty credentials attempt")
            raise ValidationError("Email and password required")

        # FAIL 2: User not found
        user = database.get_user(email)
        if not user:
            logging.info(f"Login attempt for nonexistent user: {email}")
            raise AuthenticationError("Invalid credentials")

        # FAIL 3: Wrong password
        if not user.verify_password(password):
            logging.info(f"Failed login attempt for: {email}")
            # Don't reveal which is wrong (email or password)
            raise AuthenticationError("Invalid credentials")

        # FAIL 4: Account locked
        if user.account_locked:
            logging.warning(f"Login attempt on locked account: {email}")
            raise AuthenticationError("Account locked")

        # FAIL 5: Account inactive
        if not user.is_active:
            logging.info(f"Login attempt on inactive account: {email}")
            raise AuthenticationError("Account inactive")

        # FAIL 6: MFA required
        if user.mfa_enabled:
            session_token = create_mfa_session(user)
            return {"mfa_required": True, "session": session_token}

        # SUCCESS: Return authenticated user
        session = create_session(user)
        logging.info(f"Successful login: {email}")
        return user
```

## Integration Testing

### **Component Interaction Testing**

```python
@pytest.mark.integration
class TestAuthenticationFlow:
    """Test authentication system end-to-end"""

    def setup_method(self):
        """Setup test database"""
        self.db = TestDatabase()
        self.auth_service = AuthenticationService(self.db)
        self.email_service = EmailService()

    def test_signup_to_verified_user(self):
        """Test complete signup flow"""
        # 1. User signs up
        user = self.auth_service.signup(
            email="test@example.com",
            password="SecurePass123!"
        )
        assert user.email_verified == False

        # 2. Email service sends verification
        verification_link = self.email_service.get_link_for_user(user.id)
        assert verification_link is not None

        # 3. User clicks verification link
        user.verify_email(verification_link)
        assert user.email_verified == True

        # 4. User can now login
        authenticated = self.auth_service.login(
            "test@example.com",
            "SecurePass123!"
        )
        assert authenticated.id == user.id

    def test_failed_login_increments_attempts(self):
        """Test login attempt tracking"""
        user = self.auth_service.create_user(
            email="test@example.com",
            password="SecurePass123!"
        )
        user.email_verified = True

        # Try to login 3 times with wrong password
        for i in range(3):
            with pytest.raises(AuthenticationError):
                self.auth_service.login(
                    "test@example.com",
                    "WrongPassword"
                )

        # Account should be locked after 3 attempts
        assert user.failed_attempts == 3
        assert user.account_locked == True
```

## Failure Modes

### **Critical Failures That Block Commit**

```
❌ ALWAYS BLOCK:
├─ Syntax errors
├─ Import failures
├─ Any test fails
├─ Security vulnerability found
├─ SQL injection possible
├─ Hardcoded password/API key
├─ Code doesn't compile
├─ Type checking fails
├─ Missing exception handling
└─ No tests provided

⚠️  REVIEW REQUIRED:
├─ Documentation incomplete
├─ Code coverage < 85%
├─ Performance degradation
├─ Complex logic unexplained
└─ Architectural change

✅ ACCEPTABLE:
├─ Minor style issues
├─ Non-critical warnings
├─ Documentation could be better
└─ Performance optimizable (but acceptable)
```

## Implementation

### **Pre-Commit Hook**

```bash
#!/bin/bash
# ~/.git-templates/hooks/ai-verify-correctness

echo "🔍 Verifying AI code correctness..."

# 1. Syntax check
python3 -m py_compile $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ $? -ne 0 ]; then
    echo "❌ Syntax errors found"
    exit 1
fi

# 2. Run tests
pytest --tb=short
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

# 3. Type checking
mypy $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ $? -ne 0 ]; then
    echo "❌ Type checking failed"
    exit 1
fi

# 4. Security check
bandit -r -ll $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
if [ $? -ne 0 ]; then
    echo "❌ Security issues found"
    exit 1
fi

# 5. Coverage check
coverage report --fail-under=85
if [ $? -ne 0 ]; then
    echo "❌ Coverage insufficient"
    exit 1
fi

echo "✅ Code correctness verified - safe to commit"
exit 0
```

### **Configuration**

```yaml
# In group_vars/all.yml
git_ai_code_quality:
  verify_correctness: true

  required_gates:
    - syntax_check
    - unit_tests
    - integration_tests
    - type_checking
    - security_check
    - linting

  test_configuration:
    minimum_coverage: 85
    critical_path_coverage: 95
    unit_test_percentage: 65
    integration_test_percentage: 25
    e2e_test_percentage: 10

  blocking_failures:
    - syntax_errors
    - test_failures
    - type_errors
    - security_vulnerabilities
    - hardcoded_secrets
    - coverage_insufficient

  security_requirements:
    require_no_sql_injection: true
    require_no_hardcoded_secrets: true
    require_input_validation: true
    require_error_handling: true
    scan_dependencies: true
```

---

**Status**: Framework Complete ✅
**Focus**: Working Code, Not Buggy Code
**Principle**: Quality Gates Enforce Correctness
**Created**: October 30, 2024
