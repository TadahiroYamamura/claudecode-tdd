---
description: Start a TDD session - activates the commit guard
---

## TDD Session Start

Run `scripts/tdd-start.sh` to start the session:

```bash
scripts/tdd-start.sh
```

This appends a guard block to `.git/hooks/pre-commit` that blocks direct `git commit` calls for the duration of the session. If a pre-commit hook already exists, the block is appended without modifying the existing content.

Once started, begin the first cycle with `/tdd:red`.
