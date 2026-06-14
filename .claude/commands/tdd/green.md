---
description: Complete the GREEN phase - Make the test pass with minimal code
---

## TDD GREEN Phase: Make the Test Pass

You are entering the **GREEN** phase. Your goal is to make the failing test pass with **minimal code**.

### Phase Rules

- This phase occurs **EXACTLY ONCE** per cycle
- Do NOT add unnecessary functionality
- Ignore code quality temporarily - that is for REFACTOR phase

### Beck's Strategies

#### 1. Fake It (Till You Make It)

```python
# Test: assert add(1, 1) == 2
def add(a, b):
    return 2  # return the expected constant
```

Return a constant that makes the test pass.

#### 2. Obvious Implementation

```python
# Tests: add(1,1)==2 AND add(2,3)==5 already exist
def add(a, b):
    return a + b  # the only implementation that satisfies all tests
```

Write the real implementation when it is uniquely determined.

- **Warning**: If it fails, fall back to Fake It

### Strategy Selection Criteria

**Ask: "Could multiple implementations pass this test?"**

| Answer | Strategy |
|--------|----------|
| Yes | **Fake It** — return a constant |
| No | **Obvious Implementation** — write the real solution |

**Use Fake It when:**
- A constant or trivial value would pass the test
- You are unsure which inputs the next test will add
- Algorithm correctness depends on cases not yet tested

**Use Obvious Implementation when:**
- Existing tests already constrain the implementation (you've been triangulating)
- The rule is universal and self-evident: `return len(s)` for `assert count("abc") == 3`
- The implementation is a direct, one-to-one translation of the assertion

> ⚠️ **After Fake It**: The next RED phase must be a Triangulation test.
> Add different input values that break the constant and force generalization.

### Checklist Before Commit

- [ ] Test passes (run all tests to confirm)
- [ ] Implementation is minimal (no extra features)
- [ ] Strategy chosen correctly: Fake It if multiple implementations could pass, Obvious if uniquely determined

### Commit Your Progress

**GREEN = SAFE**. You now have a working checkpoint you can always return to.

Run `/git:commit` to commit this behavioral change. The commit will be typed as:
- `feat:` for new functionality
- `fix:` for bug fixes
- `test:` for test additions

### Next Step

After committing, proceed to `/tdd:refactor` to improve code quality while keeping tests green.

---

**Remember**: Do NOT refactor yet! Get to green first, commit, THEN improve the code.
