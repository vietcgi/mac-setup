# AI Commit Formalization Process

Comprehensive framework for formalizing AI-generated commits with proper audit trails, validation, and safety mechanisms.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [AI Commit Message Format](#ai-commit-message-format)
3. [Commit Lifecycle](#commit-lifecycle)
4. [Validation Rules](#validation-rules)
5. [Audit & Tracking](#audit--tracking)
6. [Safety Mechanisms](#safety-mechanisms)
7. [Implementation Guide](#implementation-guide)
8. [Examples](#examples)

## Architecture Overview

### **Three-Tier Commit System**

```
┌─────────────────────────────────┐
│  TIER 1: GENERATION             │
├─────────────────────────────────┤
│ • AI generates commit message   │
│ • AI identifies change type     │
│ • AI adds context/reasoning     │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  TIER 2: VALIDATION & AUDIT     │
├─────────────────────────────────┤
│ • Validate format               │
│ • Check for required fields     │
│ • Verify commit classification  │
│ • Add metadata (timestamp, ID)  │
│ • Sign commit (GPG)             │
└─────────────────────────────────┘
           ↓
┌─────────────────────────────────┐
│  TIER 3: STORAGE & TRACKING     │
├─────────────────────────────────┤
│ • Store in git                  │
│ • Log to audit trail            │
│ • Index for searching           │
│ • Generate statistics           │
└─────────────────────────────────┘
```

## AI Commit Message Format

### **Standard Format**

```
type(scope): subject [AI]

Context: <what was changed and why>

Changes:
- <specific change 1>
- <specific change 2>
- <specific change 3>

Reasoning: <AI explanation of rationale>

Generated-By: <ai_model>
Confidence: <0-100%>
Review-Status: <pending|reviewed|approved>
Commit-ID: <unique_id>
Timestamp: <ISO8601>
```

### **Field Definitions**

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| **type** | ✅ | Conventional commit type | `feat`, `fix`, `refactor` |
| **scope** | ✅ | Area of code affected | `auth`, `config`, `cli` |
| **subject** | ✅ | Brief description (≤50 chars) | `add two-factor authentication` |
| **[AI]** | ✅ | AI marker flag | `[AI]` or `[AI:claude]` |
| **Context** | ✅ | What was changed and why | Multi-line explanation |
| **Changes** | ✅ | Bulleted list of changes | Specific, actionable items |
| **Reasoning** | ✅ | AI explanation of rationale | Why this approach was chosen |
| **Generated-By** | ✅ | Which AI model generated | `claude-3.5-sonnet`, `gpt-4` |
| **Confidence** | ✅ | AI confidence level | `85%`, `92%` |
| **Review-Status** | ✅ | Human review status | `pending`, `reviewed`, `approved` |
| **Commit-ID** | ✅ | Unique identifier | `ai-20240101-abc123` |
| **Timestamp** | ✅ | When commit was made | `2024-10-30T15:30:45Z` |

### **Commit Type Categories**

```
FEATURE COMMITS (feat)
├─ [AI] New functionality
├─ [AI] New components
├─ [AI] New utilities
└─ Requires: Clear scope, full context

FIX COMMITS (fix)
├─ [AI] Bug fixes
├─ [AI] Error handling
├─ [AI] Performance improvements
└─ Requires: Problem description, solution

REFACTOR COMMITS (refactor)
├─ [AI] Code restructuring
├─ [AI] Simplification
├─ [AI] Performance optimization
└─ Requires: Before/after comparison, rationale

DOCUMENTATION COMMITS (docs)
├─ [AI] Generated documentation
├─ [AI] API documentation
├─ [AI] User guides
└─ Requires: Content summary

TEST COMMITS (test)
├─ [AI] Generated tests
├─ [AI] Test improvements
├─ [AI] Coverage additions
└─ Requires: Test scope, coverage metrics

CHORE COMMITS (chore)
├─ [AI] Dependency updates
├─ [AI] Configuration changes
├─ [AI] Build tooling
└─ Requires: Justification
```

## Commit Lifecycle

### **AI Commit Flow**

```
1. CODE GENERATION
   ├─ AI analyzes requirements
   ├─ AI generates code changes
   └─ AI creates initial commit message

2. AUTOMATIC VALIDATION
   ├─ Check format compliance
   ├─ Verify required fields
   ├─ Validate commit type
   ├─ Check confidence threshold
   └─ Flag potential issues

3. PRE-COMMIT HOOKS
   ├─ Run syntax checks
   ├─ Run tests (if applicable)
   ├─ Verify file changes
   ├─ Check for secrets
   └─ Validate against rules

4. GIT HOOKS (commit-msg)
   ├─ Final message validation
   ├─ Add metadata (timestamp, ID)
   ├─ Create audit entry
   └─ Append footer information

5. GPG SIGNING
   ├─ Sign commit with key
   ├─ Verify signature
   ├─ Add signature to metadata
   └─ Log signing event

6. STORAGE
   ├─ Commit to git
   ├─ Log to audit trail
   ├─ Index for searching
   ├─ Update statistics
   └─ Send notifications (optional)

7. POST-COMMIT
   ├─ Generate summary
   ├─ Send for review (if needed)
   ├─ Create notification
   └─ Archive metadata
```

### **Example Lifecycle**

```
TIME | STEP | ACTION | OUTPUT
───────────────────────────────────────────────────────────────
T0   | 1    | AI generates commit
     |      | "feat(auth): add two-factor"
     |      |
T1   | 2    | Validation runs
     |      | ✓ Format OK
     |      | ✓ Fields present
     |      | ✓ Confidence: 92%
     |
T2   | 3    | Pre-commit hooks
     |      | ✓ Python syntax
     |      | ✓ Tests pass
     |      | ✓ No secrets
     |
T3   | 4    | Commit-msg hook
     |      | Added metadata:
     |      | Commit-ID: ai-20241030-abc123
     |      | Timestamp: 2024-10-30T15:30:45Z
     |
T4   | 5    | GPG signing
     |      | ✓ Signed with GPG key
     |      | ✓ Signature verified
     |
T5   | 6    | Git storage
     |      | ✓ Committed
     |      | ✓ Logged to audit
     |      | ✓ Indexed
     |
T6   | 7    | Post-commit
     |      | ✓ Summary generated
     |      | ✓ Sent for review
     |      | ✓ Notification sent
```

## Validation Rules

### **Format Validation**

```
✓ MUST have format: type(scope): subject [AI]
✓ Subject MUST be ≤ 50 characters
✓ Subject MUST start with lowercase
✓ Type MUST be from approved list
✓ Scope MUST be relevant to changes
✓ MUST have [AI] marker
```

### **Content Validation**

```
✓ Context section MUST explain what changed
✓ Context MUST explain why it was changed
✓ Changes section MUST list specific changes
✓ Changes MUST be bulleted and actionable
✓ Reasoning MUST explain AI's approach
✓ Reasoning MUST justify design choices
```

### **Metadata Validation**

```
✓ Generated-By MUST specify AI model
✓ Confidence MUST be 0-100%
✓ Confidence < 70% REQUIRES review before merge
✓ Review-Status MUST be: pending|reviewed|approved
✓ Commit-ID MUST be unique
✓ Commit-ID MUST follow format: ai-YYYYMMDD-{random}
✓ Timestamp MUST be ISO8601 format
```

### **Review Requirements**

```
CONFIDENCE LEVEL → REVIEW REQUIREMENT
─────────────────────────────────────
90-100%          → Auto-approved (≤ 5 files)
80-89%           → Spot-check required
70-79%           → Full review required
< 70%            → Blocked until review
```

### **File Change Limits**

```
COMMIT TYPE  | MAX FILES | MAX LINES | COMPLEXITY
──────────────────────────────────────────────────
feat         | 10        | 500       | High
fix          | 5         | 300       | Medium
refactor     | 15        | 1000      | High
docs         | 20        | 5000      | Low
test         | 20        | 2000      | Medium
chore        | 10        | 500       | Low
```

## Audit & Tracking

### **Commit Audit Fields**

Every AI commit MUST include:

```
# In commit message footer
Commit-ID: ai-20241030-abc123
Generated-By: claude-3.5-sonnet
Confidence: 92%
Review-Status: pending
Timestamp: 2024-10-30T15:30:45Z
Files-Changed: 3
Lines-Added: 125
Lines-Removed: 45
Complexity-Score: 7/10
Tests-Passed: ✓ (42/42)
```

### **Audit Trail Storage**

Location: `~/.devkit/git/ai-commits.log`

Format:

```json
{
  "commit_id": "ai-20241030-abc123",
  "hash": "abc123def456",
  "timestamp": "2024-10-30T15:30:45Z",
  "ai_model": "claude-3.5-sonnet",
  "subject": "feat(auth): add two-factor authentication",
  "files_changed": 3,
  "lines_added": 125,
  "lines_removed": 45,
  "confidence": 92,
  "review_status": "pending",
  "human_reviewer": null,
  "review_timestamp": null,
  "signed": true,
  "signature_valid": true,
  "tags": ["feature", "auth", "security"]
}
```

### **Audit Trail Queries**

```bash
# View all AI commits
cat ~/.devkit/git/ai-commits.log | jq '.'

# Find commits by AI model
cat ~/.devkit/git/ai-commits.log | jq '.[] | select(.ai_model == "claude-3.5-sonnet")'

# Find low-confidence commits
cat ~/.devkit/git/ai-commits.log | jq '.[] | select(.confidence < 70)'

# Find unreviewed commits
cat ~/.devkit/git/ai-commits.log | jq '.[] | select(.review_status == "pending")'

# Find commits by file
git log --grep="Files-Changed: 3" --oneline

# Generate statistics
cat ~/.devkit/git/ai-commits.log | jq '[.[] | .confidence] | add / length'
```

### **Audit Trail Reporting**

Generate monthly reports:

```bash
#!/bin/bash
# ai-commits-report.sh

MONTH=$(date +%Y-%m)
LOGFILE=~/.devkit/git/ai-commits.log

echo "=== AI Commits Report: $MONTH ==="
echo ""

# Total commits
TOTAL=$(cat $LOGFILE | jq '. [] | select(.timestamp | startswith("'$MONTH'"))' | wc -l)
echo "Total AI Commits: $TOTAL"

# By model
echo "By Model:"
cat $LOGFILE | jq -r '. [] | select(.timestamp | startswith("'$MONTH'")) | .ai_model' | sort | uniq -c

# By type
echo "By Type:"
cat $LOGFILE | jq -r '. [] | select(.timestamp | startswith("'$MONTH'")) | .subject' | cut -d'(' -f1 | sort | uniq -c

# Average confidence
echo "Average Confidence:"
cat $LOGFILE | jq '[. [] | select(.timestamp | startswith("'$MONTH'")) | .confidence] | add / length'

# Review status
echo "Review Status:"
cat $LOGFILE | jq -r '. [] | select(.timestamp | startswith("'$MONTH'")) | .review_status' | sort | uniq -c
```

## Safety Mechanisms

### **Confidence Thresholds**

```
CONFIDENCE  STATUS              ACTION
────────────────────────────────────────────
90-100%     ✅ Auto-approve     Can merge immediately (with spot checks)
80-89%      ⚠️  Review required  Human must review before merge
70-79%      🔴 Needs review     Full review required, high priority
< 70%       ❌ Blocked          Cannot merge until reviewed

SPECIAL RULES:
• Commits > 500 lines: Minimum 80% confidence
• Commits touching auth/security: Minimum 85% confidence
• Commits touching main branch: Minimum 90% confidence
• Multiple model commits: Require cross-verification
```

### **High-Risk Scenarios**

Commits affecting these areas REQUIRE higher confidence:

```
AREA                MIN CONFIDENCE  REASON
──────────────────────────────────────────────
Authentication      95%             Security-critical
Encryption          95%             Security-critical
Access Control      95%             Security-critical
Database Schema     90%             Data integrity
Core Logic          90%             System stability
API Endpoints       85%             Contract breaking
Configuration        85%             Environment impact
Dependencies         80%             Build stability
```

### **Commit Blockers**

Automatic blocks (commits CANNOT be made):

```
❌ BLOCKER: Confidence < 50% (always blocked)
❌ BLOCKER: Missing required fields
❌ BLOCKER: Failing tests
❌ BLOCKER: Syntax errors detected
❌ BLOCKER: Security issues found
❌ BLOCKER: Private keys/secrets detected

⚠️  WARNING: Can proceed but requires review
⚠️  WARNING: Low confidence (70-79%)
⚠️  WARNING: Large changes (> 500 lines)
⚠️  WARNING: Touching multiple modules
```

### **GPG Signing**

All AI commits MUST be GPG signed:

```
✓ Every AI commit signed with designated key
✓ Signature must be valid
✓ Key fingerprint logged
✓ Signature verification required before merge
✓ Failed signature blocks commit
```

## Implementation Guide

### **Step 1: Configure Git for AI Commits**

In `group_vars/all.yml`:

```yaml
# AI Commit Configuration
git_ai_commits_enabled: true
git_ai_commit_marker: "[AI]"
git_ai_model: "claude-3.5-sonnet"
git_ai_confidence_threshold: 70  # minimum % to allow
git_ai_require_review: true
git_ai_require_gpg_signing: true
git_ai_audit_logging: true
git_ai_auto_approve_threshold: 90  # auto-approve if confidence >= this

# High-risk areas requiring extra review
git_ai_high_risk_patterns:
  - "auth"
  - "security"
  - "encrypt"
  - "password"
  - "token"
  - "db/schema"
  - "api"
```

### **Step 2: Deploy AI Commit Hooks**

Create `~/.git-templates/hooks/ai-commit-validate.sh`:

```bash
#!/bin/bash
# Validates AI-generated commits

COMMIT_MSG_FILE=$1
CONFIDENCE=$(grep "^Confidence:" "$COMMIT_MSG_FILE" | grep -oE '[0-9]+')
MIN_CONFIDENCE=$(git config --get git.ai.confidence-threshold || 70)

# Check confidence threshold
if [ "$CONFIDENCE" -lt "$MIN_CONFIDENCE" ]; then
    echo "❌ Commit confidence ($CONFIDENCE%) below threshold ($MIN_CONFIDENCE%)"
    exit 1
fi

# Check for [AI] marker
if ! grep -q "\[AI\]" "$COMMIT_MSG_FILE"; then
    echo "❌ Missing [AI] marker in commit message"
    exit 1
fi

# Check for required fields
for field in "Generated-By" "Confidence" "Review-Status" "Commit-ID" "Timestamp"; do
    if ! grep -q "^$field:" "$COMMIT_MSG_FILE"; then
        echo "❌ Missing required field: $field"
        exit 1
    fi
done

exit 0
```

### **Step 3: Create AI Commit Logger**

Create `cli/ai_commit_manager.py`:

```python
#!/usr/bin/env python3
"""AI Commit Manager - Validation, logging, and audit trail"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

class AICommitManager:
    def __init__(self):
        self.home = Path.home()
        self.audit_file = self.home / ".devkit/git/ai-commits.log"
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)

    def parse_commit_message(self, message: str) -> dict:
        """Parse AI commit message into fields"""
        fields = {}
        for line in message.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                fields[key.strip()] = value.strip()
        return fields

    def validate_commit(self, message: str) -> tuple[bool, list]:
        """Validate AI commit message"""
        errors = []
        fields = self.parse_commit_message(message)

        # Check required fields
        required = ["Generated-By", "Confidence", "Review-Status", "Commit-ID", "Timestamp"]
        for field in required:
            if field not in fields:
                errors.append(f"Missing field: {field}")

        # Validate confidence
        try:
            confidence = int(fields.get("Confidence", "0"))
            if not (0 <= confidence <= 100):
                errors.append("Confidence must be 0-100")
        except ValueError:
            errors.append("Confidence must be a number")

        return len(errors) == 0, errors

    def log_commit(self, commit_hash: str, metadata: dict) -> None:
        """Log AI commit to audit trail"""
        entry = {
            "hash": commit_hash,
            "timestamp": datetime.now().isoformat(),
            **metadata
        }

        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_ai_commits(self, limit: int = 50) -> list:
        """Get recent AI commits"""
        commits = []
        if self.audit_file.exists():
            with open(self.audit_file, 'r') as f:
                for line in f:
                    commits.append(json.loads(line))
        return commits[-limit:]
```

### **Step 4: Create Commit Message Template**

Create `~/.git-templates/ai-commit-template.txt`:

```
type(scope): subject [AI]

Context: <what was changed and why>

Changes:
- <specific change 1>
- <specific change 2>

Reasoning: <AI explanation of rationale>

Generated-By: <ai_model>
Confidence: <0-100>%
Review-Status: pending
Commit-ID: ai-YYYYMMDD-{random}
Timestamp: <ISO8601>
```

## Examples

### **Example 1: Feature Commit**

```
feat(auth): add two-factor authentication [AI]

Context: Users requested two-factor authentication support for enhanced security.
This implementation adds TOTP-based 2FA as a second authentication factor.

Changes:
- Added `TwoFactorAuth` service class
- Added `/auth/2fa/setup` endpoint
- Added `/auth/2fa/verify` endpoint
- Updated user model to store 2FA secret
- Added database migration for new fields
- Added comprehensive test coverage

Reasoning: TOTP (Time-based One-Time Password) was chosen over SMS due to:
1. No external service dependency
2. Better security (not vulnerable to SIM swapping)
3. Industry standard (works with Authenticator apps)
4. Zero additional cost

Generated-By: claude-3.5-sonnet
Confidence: 95%
Review-Status: pending
Commit-ID: ai-20241030-feat-auth
Timestamp: 2024-10-30T15:30:45Z
Files-Changed: 8
Lines-Added: 450
Lines-Removed: 0
Tests-Passed: ✓ (87/87)
Complexity-Score: 8/10
```

### **Example 2: Bug Fix Commit**

```
fix(api): resolve race condition in session management [AI]

Context: Users were experiencing intermittent authentication failures during
concurrent requests. Root cause: unsynchronized access to session cache.

Changes:
- Added mutex lock to session cache access
- Converted to async-safe session operations
- Added request queuing for concurrent sessions
- Fixed memory leak in cached sessions
- Added unit tests for concurrent access

Reasoning: A mutex was selected over atomic operations because:
1. Session access patterns require atomic multi-step operations
2. Lock contention is minimal (µs-level)
3. Simpler to reason about correctness
4. Standard pattern for this type of issue

Generated-By: claude-3.5-sonnet
Confidence: 88%
Review-Status: pending
Commit-ID: ai-20241030-fix-race
Timestamp: 2024-10-30T16:15:22Z
Files-Changed: 4
Lines-Added: 85
Lines-Removed: 32
Tests-Passed: ✓ (45/45)
Complexity-Score: 6/10
```

### **Example 3: Refactor Commit**

```
refactor(config): simplify environment configuration loading [AI]

Context: Configuration loading logic was spread across multiple files with
duplicated code. Consolidated into single, reusable ConfigLoader class.

Changes:
- Created ConfigLoader service class
- Consolidated 3 separate loaders into one
- Removed 200 lines of duplicate code
- Improved error handling and validation
- Added comprehensive documentation

Reasoning: Consolidation improves:
1. Maintainability (single source of truth)
2. Testability (centralized logic)
3. Extensibility (easier to add new sources)
4. Code reuse (consistent interface)

Performance impact: Negligible (< 1% overhead)

Generated-By: claude-3.5-sonnet
Confidence: 92%
Review-Status: pending
Commit-ID: ai-20241030-refactor-config
Timestamp: 2024-10-30T17:00:11Z
Files-Changed: 6
Lines-Added: 180
Lines-Removed: 200
Tests-Passed: ✓ (92/92)
Complexity-Score: 5/10
```

## Policies & Guidelines

### **Do's**

✅ DO: Always include [AI] marker
✅ DO: Provide detailed context and reasoning
✅ DO: Use conventional commit format
✅ DO: Include test results
✅ DO: Sign all commits with GPG
✅ DO: Log all AI commits to audit trail
✅ DO: Request review for low-confidence commits
✅ DO: Document design decisions

### **Don'ts**

❌ DON'T: Omit required metadata fields
❌ DON'T: Make confidence too high artificially
❌ DON'T: Commit without tests
❌ DON'T: Skip review for high-risk areas
❌ DON'T: Merge low-confidence commits without review
❌ DON'T: Modify commit messages after signing
❌ DON'T: Ignore validation warnings
❌ DON'T: Automate away human judgment

### **High-Risk Scenarios**

Always require human review:

- ❌ Authentication/security changes
- ❌ Data migration scripts
- ❌ Database schema changes
- ❌ API contract changes
- ❌ Dependency updates
- ❌ Configuration changes
- ❌ Performance-critical code

## Integration with DevKit

### **Ansible Role Variables**

```yaml
# group_vars/all.yml
git_ai_commits_enabled: true
git_ai_commit_marker: "[AI]"
git_ai_model: "claude-3.5-sonnet"
git_ai_confidence_threshold: 70
git_ai_require_review: true
git_ai_require_gpg_signing: true
git_ai_audit_logging: true
```

### **Hook Integration**

Hooks will automatically:

1. Validate [AI] marker presence
2. Check confidence threshold
3. Verify required metadata
4. Log to audit trail
5. Sign with GPG key
6. Generate audit report

### **Commit-Msg Hook Extension**

Update git role's `commit-msg.sh.j2` to include:

```bash
# Check for AI commit
if echo "$COMMIT_MSG" | grep -q "\[AI\]"; then
    # Run AI commit validation
    python3 ~/devkit/cli/ai_commit_manager.py validate "$COMMIT_MSG_FILE"
    if [ $? -ne 0 ]; then
        echo "❌ AI commit validation failed"
        exit 1
    fi
fi
```

## Benefits

✅ **Traceability**: Every AI commit is logged and tracked
✅ **Quality**: Validation ensures consistent message format
✅ **Safety**: Confidence thresholds prevent risky commits
✅ **Auditability**: Complete audit trail for compliance
✅ **Reviewability**: Metadata helps reviewers understand context
✅ **Transparency**: Clear indication of AI-generated code
✅ **Accountability**: AI model and confidence tracked
✅ **Learning**: Metrics to understand AI performance

## Migration Path

### **Phase 1: Infrastructure** (Week 1)

- [ ] Deploy git role with AI-aware hooks
- [ ] Create audit logging system
- [ ] Set up AI commit template

### **Phase 2: Validation** (Week 2)

- [ ] Enable AI commit validation
- [ ] Configure confidence thresholds
- [ ] Set up review workflow

### **Phase 3: Automation** (Week 3)

- [ ] Enable GPG signing
- [ ] Auto-approve high-confidence commits
- [ ] Create reporting dashboards

### **Phase 4: Optimization** (Week 4)

- [ ] Analyze metrics
- [ ] Adjust thresholds
- [ ] Refine process based on experience

---

**Status**: Framework Complete ✅
**Version**: 1.0.0
**Created**: October 30, 2024
