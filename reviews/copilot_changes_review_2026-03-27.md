# Copilot changes review (2026-03-27)

Scope reviewed:
- authentication and user registration flow
- JWT handling
- test setup

## Findings

### 1) Duplicate-registration race can return 500 instead of 400 (High)
**Where:** `app/api/auth.py` in `register()`.

The endpoint checks for existing email/username and then inserts. Under concurrent requests, two requests can pass pre-checks and race on DB uniqueness constraints, causing an unhandled `IntegrityError` and a 500 response.

**Impact:** user-facing intermittent 500s and noisy error logs under concurrent signups.

**Recommendation:** wrap commit in `try/except IntegrityError`, rollback, and return controlled 400/409.

### 2) JWT invalidation tied to mutable username claim (Medium)
**Where:** `app/api/auth.py` login token payload (`sub = user.username`) and `get_current_user()` lookup by username.

If username is ever made editable, existing tokens become unusable because subject lookup uses username instead of immutable user id.

**Impact:** unintended logout behavior after username changes; harder long-term token semantics.

**Recommendation:** use immutable `user.id` in token subject and resolve user by id.

### 3) Test database uses file-based SQLite in repo root (Low)
**Where:** `tests/conftest.py` with `sqlite:///./test.db`.

Using a file-backed DB can cause stale lock/state issues across interrupted runs, and it leaves artifacts in working directories.

**Impact:** occasional flaky local tests and leftover files.

**Recommendation:** prefer in-memory SQLite (`sqlite://`) with shared connection fixture, or place file under a dedicated temp directory.

## Overall assessment
The structure is clear and test coverage for happy paths is good. Addressing the race condition should be prioritized before production use.
