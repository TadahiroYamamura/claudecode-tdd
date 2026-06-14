---
description: Start the RED phase - Write a small, focused failing test
---

## TDD RED Phase: Write a Failing Test

You are entering the **RED** phase of Kent Beck's TDD cycle. Your goal is to write ONE small, focused failing test.

### Before Starting

Check `.tdd/PHASE`. If it contains `green`, REFACTOR is incomplete — run `/tdd:refactor` first. Do not write a new test until the previous cycle is fully closed.

After the test is written and confirmed failing, write `red` to `.tdd/PHASE`.

### Phase Rules

- **NO COMMIT** during RED phase (you are not in a safe state)
- This phase occurs **EXACTLY ONCE** per cycle
- Write **ONE** failing test or add **ONE** failing assertion to an existing test

### Writing Your Test

**1. Choose a test name that describes behavior:**
- Good: `shouldAuthenticateValidUser`, `test_empty_input_returns_error`
- Bad: `testAuth`, `test1`

**2. Keep the test small:**
- Test ONE specific behavior
- If you are thinking "and also...", stop - that is a second test

**3. The test must fail for the RIGHT reason:**
- Missing implementation (expected)
- NOT syntax errors or typos

### When to Split Into a New Test

Consider creating a separate test function when:
- You're testing a **different behavior** (not just another case of the same behavior)
- The new assertion requires **different setup** than existing assertions
- You're unsure which assertion would fail first (tests should have clear failure points)

### Did the Previous GREEN Use Fake It?

If yes, this RED is a **Triangulation** test. Write a test with **different concrete input values** that breaks the constant:

```python
# Previous: test_add_one_and_one → GREEN returned 2 (fake)
# Triangulation: different inputs that expose the fake
def test_add_two_and_three():
    assert add(2, 3) == 5  # breaks `return 2`, forces real implementation
```

Triangulation rule: **vary the inputs, not just the assertion**.

### Checklist Before Proceeding

- [ ] Test has a descriptive name explaining the expected behavior
- [ ] Test is small and focused on ONE thing
- [ ] Test FAILS (verify by running tests)
- [ ] Test fails for the RIGHT reason (not syntax/typo)

### Next Step

Once your test fails for the right reason, proceed to `/tdd:green` to make it pass.

---

**Remember**: Each RED phase adds exactly ONE failing test or ONE failing assertion. Keep iterations small!
