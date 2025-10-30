# Quality Standards Index

Complete reference for the commit quality standards in this repository.

## The Mandate

**Every commit to this repository MUST be quality, clean, working code.**

This applies to:
- ✅ All developers (junior, senior, contractors)
- ✅ All code types (features, fixes, tests, docs, automation)
- ✅ All scenarios (normal work, deadlines, emergencies)
- ✅ All systems (human-written, AI-generated, automation)

**No exceptions. No shortcuts. No bypasses.**

## Quick Navigation

### **For Your First Commit**

1. **Read**: `QUALITY_MANIFESTO.md` (understand why)
2. **Read**: `docs/COMMIT_CHECKLIST.md` (how to prepare)
3. **Run**: `python3 cli/commit_validator.py` (validate code)
4. **Commit**: `git commit -S -m "message"` (automatic hooks verify)

### **For Understanding the Standards**

1. `QUALITY_MANIFESTO.md` - The "why" (inspirational)
2. `docs/COMMIT_QUALITY_STANDARD.md` - The "what" (detailed rules)
3. `docs/COMMIT_CHECKLIST.md` - The "how" (practical guide)

### **For Reference During Work**

- Checklist: `docs/COMMIT_CHECKLIST.md`
- Standard: `docs/COMMIT_QUALITY_STANDARD.md`
- Validator: `cli/commit_validator.py`

### **For Team Leadership**

- Vision: `QUALITY_MANIFESTO.md` (show the team)
- Standard: `docs/COMMIT_QUALITY_STANDARD.md` (enforce it)
- Audit: `~/.devkit/git/commits.log` (verify compliance)

## The Six Quality Gates

Every commit MUST pass all six gates:

```
┌────────────────────────────────────────────────┐
│ GATE 1: SYNTAX CHECK                           │
│ Code must compile without errors               │
├────────────────────────────────────────────────┤
│ GATE 2: TESTS (100% pass rate)                 │
│ All tests must pass, zero failures allowed     │
├────────────────────────────────────────────────┤
│ GATE 3: TEST COVERAGE (85%+ required)          │
│ Minimum 85% overall, 95% for critical paths    │
├────────────────────────────────────────────────┤
│ GATE 4: TYPE CHECKING (mypy strict)            │
│ All type hints required, no implicit Any       │
├────────────────────────────────────────────────┤
│ GATE 5: SECURITY SCAN (0 issues)               │
│ No vulnerabilities, no hardcoded secrets       │
├────────────────────────────────────────────────┤
│ GATE 6: CODE LINTING (8.0+ score)              │
│ Pylint score must be 8.0 or higher             │
└────────────────────────────────────────────────┘

If ANY gate fails → COMMIT BLOCKED
If ALL gates pass → Commit is allowed
```

## File Guide

### **Core Documents**

| File | Purpose | Audience | When to Read |
|------|---------|----------|--------------|
| `QUALITY_MANIFESTO.md` | Establish the high bar, explain why | Everyone | Before first commit |
| `docs/COMMIT_QUALITY_STANDARD.md` | Define the exact standards | Developers | Reference material |
| `docs/COMMIT_CHECKLIST.md` | Day-to-day verification steps | Developers | Before every commit |

### **Tools**

| File | Purpose | Audience | When to Use |
|------|---------|----------|-------------|
| `cli/commit_validator.py` | Validate code before committing | Developers | Before git commit |
| `ansible/roles/git/` | Automatic enforcement via hooks | All developers | Automatic on commit |

### **Configuration**

| File | Purpose | Audience | When to Update |
|------|---------|----------|-----------------|
| `group_vars/all.yml` | Git role settings | DevOps/Admin | During setup |
| `~/.devkit/git/commits.log` | Audit trail of all commits | Leadership | Weekly review |

## Enforcement

### **Layer 1: Automated (Git Hooks)**

Pre-commit hooks automatically run on every `git commit`:
- Syntax check
- Test execution (must be 100%)
- Coverage verification (must be 85%+)
- Type checking (mypy strict)
- Security scan (0 vulnerabilities)
- Code linting (8.0+ score)

**If any gate fails → commit is blocked immediately**

### **Layer 2: Human Review**

Before merging to main:
- Code review (quality, architecture, security)
- Test review (coverage, completeness)
- Documentation review (clarity, completeness)

### **Layer 3: Audit Trail**

Every commit is logged with:
- Timestamp
- Author
- Changes (files, lines)
- Test results (pass/fail, count)
- Coverage metrics
- Security scan results
- GPG signature

## Key Numbers

| Metric | Requirement | Why |
|--------|-------------|-----|
| **Test Pass Rate** | 100% | Untested code breaks |
| **Code Coverage** | 85%+ (95%+ critical) | Missing test cases |
| **Type Safety** | 100% (mypy strict) | Type errors cause bugs |
| **Security Issues** | 0 | Vulnerabilities affect users |
| **Linting Score** | 8.0+ | Code quality matters |
| **Complexity** | Reasonable (cyclomatc < 10) | High complexity = bugs |
| **Documentation** | 100% of functions | Undocumented code is forgotten |

## The Commitment

### **To Our Code**

```
We commit to:
✓ Never merge untested code
✓ Never skip security checks
✓ Never decrease test coverage
✓ Never ignore type errors
✓ Never hardcode secrets
✓ Never compromise on documentation
✓ Never bypass validation
✓ Never prioritize speed over quality
```

### **To Our Users**

```
This ensures:
✓ No untested code reaches production
✓ No security vulnerabilities in releases
✓ No surprises in production
✓ Reliable, stable systems
✓ Code we can maintain
✓ Code we're proud of
```

### **To Our Team**

```
This provides:
✓ Clear expectations
✓ Consistent standards
✓ No surprises
✓ Easier debugging
✓ Faster feature development
✓ Less firefighting
✓ More satisfaction
```

## Before You Commit

### **The 5-Minute Checklist**

```
□ Run: pytest
   (must see "passed")

□ Run: coverage report --fail-under=85
   (must see "Coverage is X%")

□ Run: mypy --strict *.py
   (must see "Success: no issues")

□ Run: bandit -r -ll *.py
   (must see "No issues identified")

□ Run: pylint *.py
   (must see score >= 8.0)
```

## Frequently Asked Questions

**Q: Can I skip tests?**
A: No. Commit hooks will block it.

**Q: Can I use --no-verify?**
A: No. Hooks still run.

**Q: Can coverage be 84%?**
A: No. Minimum is 85%.

**Q: Can I commit with a failing test?**
A: No. All tests must pass.

**Q: Can a senior dev skip validation?**
A: No. Same standards for everyone.

**Q: Can I bypass for a deadline?**
A: No. Standards don't change.

**Q: Can I commit at 3am?**
A: Yes, but it still must pass all gates.

**Q: What if it's an emergency?**
A: Still must pass all gates.

**Q: Can the commit be unsigned?**
A: No. GPG signature required.

**Q: Can I modify the rules?**
A: No. These are the standards.

## Success

### **How You Know It's Working**

**Week 1:**
- Commits take longer
- More tests written
- Some frustration

**Week 4:**
- Fewer bugs discovered
- Faster debugging
- Smoother code reviews

**Month 3:**
- System is stable
- Code is maintainable
- Team is efficient

**Month 6+:**
- Production quality
- Minimal firefighting
- Maximum satisfaction

## Resources

### **Tools**

- `cli/commit_validator.py` - Validate before commit
- `ansible/roles/git/` - Automatic enforcement
- `~/.devkit/git/commits.log` - Audit trail

### **Documentation**

- `QUALITY_MANIFESTO.md` - The vision
- `docs/COMMIT_QUALITY_STANDARD.md` - The standard
- `docs/COMMIT_CHECKLIST.md` - The checklist

### **Metrics & Reporting**

- Audit trail: `~/.devkit/git/commits.log`
- Coverage reports: `coverage report`
- Test results: `pytest -v`
- Type errors: `mypy --strict`
- Security issues: `bandit -r -ll`
- Linting: `pylint`

## Getting Started

### **For Developers**

1. Read `QUALITY_MANIFESTO.md`
2. Read `docs/COMMIT_CHECKLIST.md`
3. Setup git role (if not already done)
4. Make your changes
5. Run validator: `python3 cli/commit_validator.py`
6. Commit: `git commit -S -m "message"`
7. Hooks verify automatically

### **For Team Leads**

1. Share `QUALITY_MANIFESTO.md` with team
2. Review `docs/COMMIT_QUALITY_STANDARD.md`
3. Setup git role deployment
4. Review audit trail weekly
5. Monitor metrics
6. Celebrate improvements

### **For DevOps/Admin**

1. Deploy git role with quality gates
2. Configure `group_vars/all.yml`
3. Verify hooks are executable
4. Test locally
5. Monitor audit trail
6. Report metrics

## The Bottom Line

**Every commit to this repository must be:**

✅ **Tested** (100% pass rate)
✅ **Complete** (85%+ coverage)
✅ **Safe** (type-safe, security-scanned)
✅ **Clean** (linting compliant)
✅ **Documented** (fully documented)
✅ **Auditable** (GPG signed, logged)

**This is not optional.**
**This is not negotiable.**
**This is the standard.**

---

**Version**: 1.0.0
**Created**: October 30, 2024
**Status**: Active ✅
**Enforcement**: Automatic + Manual
**Exceptions**: None
