# FastAPI Template — Production Readiness Review

| Field            | Value                                 |
| ---------------- | ------------------------------------- |
| **Date**         | 2026-06-11                            |
| **Title**        | FastAPI Template Production Readiness |
| **Repository**   | `fastapi-app`                         |
| **Review range** | `1e678c4` → `8346e8d`                 |
| **Reviewer**     | code-reviewer subagent                |
| **Verdict**      | No — fix first                        |

## Summary

The template is strong on structure, typing, testing, and tooling (53 passing tests, 100% coverage, strict lint/type gates). A team cloning this gets a credible FastAPI foundation.

However, **Alembic is broken out of the box** due to a stale `script_location` after the `project_name/` refactor — that alone blocks the database/migrations story, which is a core advertised feature. Combined with missing DB onboarding docs, no migration Makefile targets, public unauthenticated user APIs without warnings, and the suspicious `tests/app/core/config.py/` directory, a new team would hit real friction before their first successful deploy.

**Verdict: merge after fixes** — primarily the Alembic path, README database/migration docs, and duplicate-username handling.

---

## Strengths

- **Architecture evolution is coherent.** The refactor from flat `app/` to `project_name/app/features/users/` with shared `dependencies/`, `core/config`, and `core/security` is a solid, teachable layout for new teams.
- **Quality bar is high.** Strict basedpyright, Ruff with security rules, 80% coverage gate, pre-commit hooks, and a Makefile/CI split (`prek` vs `ci`) give strong guardrails out of the box.
- **Tests are excellent for a template.** 53 tests pass with **100% coverage** (`uv run pytest`). Router, service, config, auth, and session layers are all exercised with clear fixtures in `tests/app/conftest.py`.
- **Config management is well-designed.** Nested pydantic-settings (`APP_*`, `DB_*`, `LOG_LEVEL`), env validation (e.g. DB name required at `project_name/app/core/config/database.py:29-30`), and test isolation via env vars are good patterns.
- **Database layer has thoughtful touches.** Auto-discovery of feature models in `project_name/app/database/env.py:31-38`, timestamp revision IDs, and Alembic env wired to app settings (when the path is fixed) are strong template choices.
- **Users feature demonstrates clean layering.** Domain errors (`errors.py`), service layer, router HTTP mapping, and password hashing via argon2 are separated cleanly.
- **Pagination is integrated properly** via `fastapi-pagination` with `LimitOffsetPage` in the router and dependency aliases in `project_name/app/dependencies/__init__.py`.

---

## Issues

### Critical (Must Fix)

1. **`alembic.ini` points at the old path — migrations are broken.**
   - File: `alembic.ini:8`
   - Issue: `script_location = %(here)s/app/database`, but migrations live at `project_name/app/database/`. Running `uv run alembic current` fails with: _"Path doesn't exist: .../app/database"_.
   - Fix: Change to `script_location = %(here)s/project_name/app/database`.

2. **No duplicate-username handling on create.**
   - File: `project_name/app/features/users/services.py:99-101`, `models.py:21`
   - Issue: `User.username` is unique, but `UserService.create` does not catch `IntegrityError`. A duplicate POST returns an unhandled 500 instead of 409 Conflict.
   - Fix: Catch `IntegrityError` in the service and map to HTTP 409 in the router.

3. **User endpoints are fully public with no auth layer.**
   - File: `project_name/app/core/security/auth.py` (exists but unused for route protection)
   - Issue: No JWT/session middleware, no protected routes, and anyone can list/create/read users. For a production starter, this needs explicit documentation as demo-only scaffolding, or teams will ship it as-is.
   - Fix: Document auth scope clearly; label users CRUD as demo scaffolding.

### Important (Should Fix)

1. **README onboarding is incomplete for database setup.**
   - File: `README.md:21-27`
   - Issue: Covers rename/install/run but never mentions starting PostgreSQL, running `alembic upgrade head`, Makefile targets for migrations (none exist), or that `make run` requires a live DB because `engine` is created at import (`project_name/app/database/engine.py:8`).

2. **`project_name` rename checklist is too vague.**
   - File: `README.md:21`
   - Issue: Misses `alembic.ini`, `[project.scripts]`, ruff/basedpyright/coverage paths, Makefile `CHECK`, pre-commit paths, and all `project_name.app.*` imports in source.

3. **`sqlalchemy` is not a direct dependency.**
   - File: `pyproject.toml:12-21`
   - Issue: Lists alembic but not sqlalchemy, even though the app imports it throughout. Works today as a transitive dep, but direct usage should be pinned explicitly.

4. **`tests/app/core/config.py/` is a misleading directory name.**
   - Issue: Mirrors the old module path and looks like a file named `config.py`. Should be `tests/app/core/config/` to match `project_name/app/core/config/`.

5. **Password/input validation is absent on schemas.**
   - File: `project_name/app/features/users/schemas.py:15-26`
   - Issue: `UserCreate`, `UserUpdate`, `UserDestroy` accept any string, including empty passwords. No username length/format constraints.

6. **`updated_at` never auto-updates.**
   - File: `project_name/app/features/users/models.py:24`
   - Issue: Sets `server_default=func.now()` but no `onupdate=func.now()`. Updates leave `updated_at` stale.

7. **Test DB dialect differs from production.**
   - File: `tests/app/conftest.py:34,58-63`
   - Issue: Tests use SQLite in-memory while production targets PostgreSQL. UUID defaults, constraints, and SQL behavior can diverge silently.

8. **README typo undermines credibility.**
   - File: `README.md:1`
   - Issue: `# fastaip-app` instead of `fastapi-app`.

9. **`database/README` is a one-liner.**
   - File: `project_name/app/database/README`
   - Issue: No migration workflow, autogenerate instructions, or model-registration notes.

10. **Empty lifespan with no engine cleanup.**
    - File: `project_name/app/main.py:21-23`
    - Issue: Yields immediately with no startup/shutdown hooks (e.g. `engine.dispose()`).

11. **`_apply_update` catches the wrong exceptions.**
    - File: `project_name/app/features/users/services.py:55-59`
    - Issue: Catches verify exceptions around `hash_password()`, but hashing raises different errors. The 500 path is only reachable via mocking.

### Minor (Nice to Have)

1. **`hash_password` missing return type** — `project_name/app/core/security/auth.py:12-13`
2. **`.env.example` formatting inconsistency** — spaces and quotes vs unquoted values in conftest
3. **`requires-python = ">=3.14"` is very aggressive** — `pyproject.toml:11`
4. **No health/readiness endpoint** (`/health`) for load balancers or k8s probes
5. **No docker-compose for local Postgres**
6. **DELETE with JSON body** — `router.py:139` is valid but unusual; worth documenting
7. **No global exception handler** for unhandled DB errors
8. **CI has no migration smoke test** — `.github/workflows/ci.yml` runs quality/build only

---

## Recommendations

1. **Fix Alembic immediately:** change `alembic.ini:8` to `script_location = %(here)s/project_name/app/database`, add `make migrate` / `make revision` targets, and document the workflow in README.
2. **Add a "First-time setup" section** covering: rename checklist (all files), PostgreSQL, `.env`, `alembic upgrade head`, `make run`, and `/docs`.
3. **Handle duplicate username:** catch `IntegrityError` in `UserService.create` and map to HTTP 409 in the router.
4. **Rename `tests/app/core/config.py/` → `tests/app/core/config/`.**
5. **Add `sqlalchemy>=2.0` to direct dependencies** in `pyproject.toml`.
6. **Add schema validation** (e.g. `Field(min_length=8)` on passwords, username constraints).
7. **Fix `updated_at`** with `onupdate=func.now()` or a SQLAlchemy event listener.
8. **Document auth scope clearly:** label users CRUD as "password demo, not session auth" and outline where JWT/OAuth would plug in.
9. **Consider** a `docker-compose.yml` with Postgres, a `/health` endpoint, and a CI step that runs `alembic upgrade head` against a service container.
10. **Add CI check** for Alembic path/config validity (even offline: `alembic history` or config parse).

---

## Assessment

**Ready to merge?** No — fix first.

**Reasoning:** Core implementation is solid with good architecture and tests. Critical issues (broken Alembic path, missing DB docs, duplicate-username 500s) block the template's primary value proposition as a database-backed FastAPI starter. Important items are polish for production readiness but should follow the critical fixes.
