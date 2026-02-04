---
name: test-first
description: Test-first development practices for high-quality code
tags: [testing, tdd, quality]
---

# Test-First Development

## The Red-Green-Refactor Cycle

```
    ┌─────────────────────────────────────┐
    │                                     │
    ▼                                     │
  [RED]                                   │
  Write a failing test                    │
    │                                     │
    ▼                                     │
  [GREEN]                                 │
  Write minimal code to pass              │
    │                                     │
    ▼                                     │
  [REFACTOR]                              │
  Improve code, keep tests green ─────────┘
```

## Phase 1: RED - Write a Failing Test

Before writing any implementation:

1. **Define the behavior** - What should happen?
2. **Write the test** - Assert the expected outcome
3. **Run the test** - Confirm it fails
4. **Verify the failure** - It should fail for the right reason

```typescript
// Good: Test defines behavior clearly
test('should reject invalid email', () => {
  const user = new User({ email: 'not-an-email' });
  expect(user.isValid()).toBe(false);
  expect(user.errors).toContain('Invalid email format');
});
```

## Phase 2: GREEN - Make It Pass

Write the simplest code that makes the test pass:

1. **Don't over-engineer** - Just make it work
2. **Don't optimize** - That comes later
3. **Don't add features** - Only what the test needs

```typescript
// Minimal implementation to pass the test
class User {
  isValid() {
    return this.email.includes('@');
  }
}
```

## Phase 3: REFACTOR - Improve the Code

With tests green, safely improve:

1. **Remove duplication** - DRY up the code
2. **Improve naming** - Make intent clear
3. **Simplify logic** - Reduce complexity
4. **Run tests after each change** - Stay green

```typescript
// Refactored with better validation
class User {
  private static EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  isValid() {
    return User.EMAIL_REGEX.test(this.email);
  }
}
```

## Test Structure: AAA Pattern

```typescript
test('descriptive name of behavior', () => {
  // Arrange - Set up test data
  const input = createTestInput();

  // Act - Execute the code under test
  const result = functionUnderTest(input);

  // Assert - Verify the outcome
  expect(result).toEqual(expectedOutput);
});
```

## What to Test

### Always Test
- Happy path (normal operation)
- Edge cases (empty, null, boundary values)
- Error cases (invalid input, failures)
- State transitions
- Public API contracts

### Sometimes Test
- Complex private methods (via public API)
- Integration points
- Performance-critical paths

### Never Test
- Third-party library behavior
- Trivial getters/setters
- Framework internals
- Implementation details

## Test Quality Checklist

- [ ] Test name describes the behavior, not implementation
- [ ] Test is independent (no shared mutable state)
- [ ] Test has one logical assertion
- [ ] Test fails for the right reason
- [ ] Test is deterministic (no flakiness)
- [ ] Test runs fast (< 100ms for unit tests)

## Common Patterns

### Testing Async Code

```typescript
test('fetches user data', async () => {
  const user = await fetchUser(123);
  expect(user.name).toBe('Alice');
});
```

### Testing Errors

```typescript
test('throws on invalid input', () => {
  expect(() => parseDate('invalid')).toThrow('Invalid date format');
});
```

### Testing Side Effects

```typescript
test('logs error on failure', () => {
  const mockLogger = jest.fn();
  processData(invalidData, { logger: mockLogger });
  expect(mockLogger).toHaveBeenCalledWith('Error processing data');
});
```

## Anti-Patterns to Avoid

- **Test implementation, not behavior** - Tests break on refactor
- **Multiple assertions testing different things** - Hard to diagnose
- **Shared mutable state** - Flaky, order-dependent tests
- **Testing private methods directly** - Couples to implementation
- **Excessive mocking** - Tests pass but code is broken
