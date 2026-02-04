---
name: task-decomposition
description: Strategies for breaking large tasks into context-window-sized subtasks
tags: [planning, architecture]
---

# Task Decomposition Patterns

## The Context Window Rule

Each subtask must be completable within a single Claude Code context window:
- Maximum ~100k tokens of reading/exploration
- Maximum ~50 files modified
- Aim for 15-60 minutes of focused work

## Decomposition Strategies

### By Layer (Horizontal)

Split by architectural layer - good for full-stack features:

1. **Data Layer** - Database/model changes, migrations
2. **Business Logic** - Service layer, domain logic
3. **API Layer** - Endpoints, validation, serialization
4. **UI Layer** - Components, state management
5. **Integration** - End-to-end testing, wiring

### By Feature (Vertical)

Split by user-facing capability - good for isolated features:

1. **Core MVP** - Minimal working version
2. **Edge Cases** - Boundary conditions, error states
3. **Polish** - UX improvements, loading states
4. **Documentation** - User-facing docs, inline comments

### By Risk Level

Split by risk - good for refactoring:

1. **Foundation** - Low-risk infrastructure changes
2. **Core Changes** - Medium-risk feature code
3. **Integration Points** - High-risk connection points
4. **Verification** - Testing and cleanup

### By Dependency

Order subtasks so each can be completed independently:

1. Types and interfaces first
2. Utilities before features
3. Data models before business logic
4. Backend before frontend
5. Unit tests before integration tests

## Sizing Heuristics

### Too Small (Combine these)
- Changing a single constant
- Adding one import
- Fixing a typo
- Single-line changes

### Just Right
- Adding a function with tests (small)
- Creating a component with tests (medium)
- Implementing an API endpoint (medium)
- Refactoring a module (medium-large)

### Too Large (Break these down)
- "Implement authentication" - break into providers, session, UI
- "Add database support" - break into schema, migrations, queries
- "Create admin panel" - break into CRUD operations

## Dependency Ordering

```
[Types/Interfaces]
       │
       ▼
  [Utilities]
       │
       ▼
  [Data Layer]
       │
       ▼
[Business Logic]
       │
       ▼
   [API Layer]
       │
       ▼
   [UI Layer]
       │
       ▼
 [Integration]
```

## Subtask Template

```json
{
  "id": "st-001",
  "title": "Verb + Object (e.g., 'Add user model')",
  "description": "What to implement and why",
  "files": ["src/models/user.ts", "src/models/user.test.ts"],
  "tests": [
    "User model validates email format",
    "User model hashes password on creation"
  ],
  "acceptance_criteria": [
    "User model defined with id, email, passwordHash fields",
    "Validation rejects invalid email formats",
    "Password is never stored in plain text",
    "Unit tests pass"
  ],
  "dependencies": [],
  "complexity": "small"
}
```

## Red Flags

Watch for these signs a task needs more decomposition:

- Description says "and" multiple times
- Files list has more than 10 items
- Acceptance criteria has more than 5 items
- Dependencies list is complex
- You can't explain it in one sentence
