---
name: todo
description: Maintain .tdd/TODO.md as the living source of truth for implementation work. Triggers when given multi-step instructions to build or change code.
---

# TODO Management

`.tdd/TODO.md` at the project root is the source of truth — not conversation memory.
Update it **before** announcing any completion or asking any question.

## Planning (new instruction)

Decompose into `- [ ]` items and write `.tdd/TODO.md`.
For ambiguous items: ask one clarifying question, update the item, then continue.
Do not start implementation until all items are actionable.

## Implementation (per item)

If complex, decompose into subtasks before starting.
Use `claudecode-tdd:tdd` skill to implement.
Mark done (`- [ ]` → `- [x]`) after REFACTOR completes, then show updated `.tdd/TODO.md`.

## Correction (user changes a task)

Update the item immediately; no confirmation needed.

## Format

```markdown
# TODO

- [x] Completed task
- [ ] Pending task
  - [x] subtask A
  - [ ] subtask B
```
