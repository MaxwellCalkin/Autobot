---
name: quality-gates
description: Quality checkpoints required before marking work complete
tags: [quality, verification]
---

# Quality Gates

## Overview

Quality gates are mandatory checkpoints that must pass before work can be considered complete. Autobot enforces these automatically via hooks, but understanding them helps you write code that passes on the first try.

## Gate 1: Tests Pass

**Command:** Auto-detected (npm test, pytest, cargo test, go test)

**Requirements:**
- All tests must pass (exit code 0)
- No skipped tests for new code
- Test output should be clean (no warnings about coverage)

**Before You Code:**
- Run the test suite to establish baseline
- Ensure you're not starting with failing tests

**Common Failures:**
- Forgot to update snapshots
- Async tests not properly awaited
- Environment variables not set in test

## Gate 2: No Linting Errors

**Command:** Project-specific (npm run lint, flake8, cargo clippy)

**Requirements:**
- Zero errors in modified files
- Warnings should be addressed if feasible
- New code should not introduce new warnings

**Autofix Available:**
- `npm run lint -- --fix`
- `black .` (Python)
- `cargo fmt` (Rust)

**Common Failures:**
- Unused imports
- Inconsistent formatting
- Missing semicolons (JS)
- Line too long

## Gate 3: Type Check (if applicable)

**Command:** `npm run typecheck`, `mypy`, `cargo check`

**Requirements:**
- No type errors in modified files
- No implicit any (TypeScript strict mode)
- Generic types properly constrained

**Common Failures:**
- Missing return type
- Null/undefined not handled
- Wrong generic type argument

## Gate 4: Documentation

**Requirements:**
- Public APIs have JSDoc/docstrings
- Complex logic has inline comments
- README updated for user-facing changes
- CHANGELOG updated for releases

**What Needs Docs:**
```typescript
// Public function - needs JSDoc
/**
 * Creates a new user with the given properties.
 * @param props - User properties including email and name
 * @returns The created user with generated ID
 * @throws {ValidationError} If email is invalid
 */
export function createUser(props: UserProps): User {
```

**What Doesn't Need Docs:**
```typescript
// Private helper - self-explanatory name is enough
function isValidEmail(email: string): boolean {
  return EMAIL_REGEX.test(email);
}
```

## Gate 5: Code Review (Optional)

**When to Use:**
- Complex or critical changes
- Security-sensitive code
- Public API changes
- After completing all subtasks

**Use the Reviewer Subagent:**
```
/task reviewer "Review the completed authentication subtask"
```

## Subtask Completion Checklist

Before marking a subtask complete:

```markdown
- [ ] All acceptance criteria met
- [ ] Tests written and passing
- [ ] No linting errors
- [ ] No type errors
- [ ] Complex logic commented
- [ ] No TODOs referencing this subtask
- [ ] No console.log/print statements left in
- [ ] No hardcoded values that should be config
```

## Task Completion Checklist

Before writing EXIT_SIGNAL: COMPLETE:

```markdown
- [ ] All subtasks marked complete
- [ ] Full test suite passes
- [ ] Integration tests pass (if any)
- [ ] No regression in existing functionality
- [ ] Documentation updated
- [ ] Code reviewed (for complex tasks)
- [ ] Ready for production
```

## Failure Recovery

### Tests Failing

1. Read the error message carefully
2. Check `.autobot/observations.jsonl` for similar failures
3. Use the fixer subagent if stuck after 2 attempts
4. Document the fix in `.autobot/progress.md`

### Lint Errors

1. Run autofix first
2. Fix remaining errors manually
3. If rule seems wrong, document why in comments

### Type Errors

1. Don't use `any` to silence errors
2. Add proper type annotations
3. Use type guards for narrowing
4. Check if types are outdated

## Metrics Tracked

The hooks track quality metrics in `.autobot/metrics.json`:

```json
{
  "total_test_runs": 45,
  "total_test_passes": 42,
  "total_test_failures": 3,
  "consecutive_test_failures": 0
}
```

Use these to identify patterns:
- High failure rate → tests too fragile or code quality issues
- Many consecutive failures → fundamental misunderstanding
