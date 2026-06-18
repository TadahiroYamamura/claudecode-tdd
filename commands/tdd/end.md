---
description: End a TDD session - deactivates the commit guard
---

## TDD Session End

Run `scripts/tdd-end.sh` to end the session:

```bash
scripts/tdd-end.sh
```

This removes the TDD guard block from `.git/hooks/pre-commit` and deactivates the session. Normal `git commit` usage is restored. Any other content in the hook is left intact.
