---
name: tdd
description: Guide Test-Driven Development using Kent Beck's Red-Green-Refactor cycle. Use when writing tests, implementing features via TDD.
---

# INSTRUCTIONS

Follow Kent Beck's TDD and Tidy First principles using the three-phase workflow:

0. **START** - `/tdd:start` - Begin the TDD session (run once before the first cycle)
1. **RED** - `/tdd:red` - Write ONE small failing test
2. **GREEN** - `/tdd:green` - Make it pass with minimal code, then commit
3. **REFACTOR** - `/tdd:refactor` - Improve structure without changing behavior, commit each step
4. **END** - `/tdd:end` - Close the TDD session (run once after all cycles are complete)

## Workflow Pattern

```
/tdd:start
    ↓
/tdd:red → write failing test → /tdd:green → pass test → scripts/tdd-commit.sh green
                                                                        ↓
        ← next cycle ← /tdd:red ← satisfied? ← /tdd:refactor (scripts/tdd-commit.sh refactor)
                                       ↓
                                 all done? → /tdd:end
```

## Core Principles

- **One test at a time**: Each RED adds exactly ONE failing test
- **Minimal code**: GREEN phase writes just enough to pass
- **Never skip REFACTOR**: Every TDD cycle must complete all three phases
- **Tidy First**: Separate structural changes (refactor) from behavioral changes (feat/fix)
- **Small commits**: Commit after GREEN, commit after EACH refactor step

## Quality Standards

- Eliminate duplication between test and production code
- Express intent through clear naming
- Keep methods small and focused
- Run ALL tests after EVERY change
- **Precise assertions**: exact equality over partial matching; all struct fields over spot-checks
