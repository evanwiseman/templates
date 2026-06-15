# Refresh Tokens & Auth Feature — Design & Implementation Plan

| Field      | Value                                                            |
| ---------- | ---------------------------------------------------------------- |
| **Date**   | 2026-06-12                                                       |
| **Status** | Draft — pending review                                           |
| **Scope**  | Remainder of option **B**: access JWT + DB-backed refresh tokens |

---

## Context

### Already done

| Piece                     | Location                                   | Notes                                             |
| ------------------------- | ------------------------------------------ | ------------------------------------------------- |
| Access JWT encode/decode  | `project_name/app/core/security/auth.py`   | `sub`, `iat`, `exp`, `type`, optional `iss`       |
| Access JWT tests          | `tests/app/core/security/test_auth.py`     | Round-trip, expiry, wrong secret/algorithm/issuer |
| Password hashing          | `project_name/app/core/security/auth.py`   | argon2 via `hash_password` / `verify_password`    |
| RefreshToken model (stub) | `project_name/app/features/auth/models.py` | Incomplete — see model changes below              |
| Users feature             | `project_name/app/features/users/`         | CRUD, no route protection                         |

### Not done (this plan)

- ~~JWT configuration (`JWT_SECRET`, TTLs, issuer)~~
- ~~Refresh token generation + hashing helpers~~
- ~~Alembic migration for `refresh_tokens`~~
- `features/auth/` service, schemas, router, errors
- `get_current_user` dependency
- Login / refresh / logout HTTP endpoints
- Auth integration tests
- `.env.example` / README auth notes

### Decisions locked from brainstorming

- **Token model:** Short-lived stateless access JWT + opaque refresh token stored hashed in PostgreSQL
- **Layout:** JWT primitives in `core/security/`; session workflow in `features/auth/`
- **Auth mechanism:** FastAPI dependencies (`CurrentUserDep`), not global middleware
- **Refresh tokens are not JWTs** — random opaque strings; DB row enables revoke/logout

---

## Architecture

```text
Client
  │  POST /auth/login      (username + password)
  │  POST /auth/refresh    (refresh_token)
  │  POST /auth/logout     (refresh_token)
  │  GET  /users/...       (Authorization: Bearer <access>)
  ▼
features/auth/router.py
  └── AuthService
        ├── User lookup + verify_password (users feature)
        ├── create_access_token (core/security)
        └── RefreshToken persistence (auth models)

dependencies/auth.py
  └── get_current_user
        ├── OAuth2PasswordBearer
        ├── decode_access_token
        └── UserService.get (optional DB load)
```

### Boundaries

| Unit                            | Responsibility                                               |
| ------------------------------- | ------------------------------------------------------------ |
| `core/security/auth.py`         | Password + access JWT only                                   |
| `core/security/tokens.py` (new) | `make_refresh_token()`, `hash_refresh_token()`               |
| `core/config/jwt.py` (new)      | `JWT_SECRET`, algorithm, access/refresh TTL, optional issuer |
| `features/auth/`                | Login/refresh/logout + `RefreshToken` model                  |
| `dependencies/`                 | Bearer extraction + current user                             |

---

## Model changes

Current `RefreshToken` stores a plain `token` string and has no primary key. Update before migration:

```python
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID]              # pk, uuid7 — match User pattern
    token_hash: Mapped[str]      # sha256 hex of opaque refresh token; unique, indexed
    user_id: Mapped[UUID]        # FK → users.id ON DELETE CASCADE
    expires_at: Mapped[datetime]
    revoked_at: Mapped[datetime | None] = mapped_column(default=None)
    created_at / updated_at      # same as User
```

**Why `token_hash`:** Client holds the raw token once; DB never stores it reversibly.

**Why `revoked_at`:** Logout and refresh rotation mark rows revoked without deleting history (optional; deletion works too — see approaches).

**Why `id` PK:** Consistent with `User`; `token_hash` remains the lookup key for refresh/logout.

---

## Approaches considered

### Refresh rotation (recommended)

On `POST /auth/refresh`: validate old refresh token → revoke old row → issue new access + new refresh token.

| Pros                                  | Cons                                     |
| ------------------------------------- | ---------------------------------------- |
| Stolen refresh token usable only once | Slightly more DB writes                  |
| Industry-standard for option B        | Client must replace stored refresh token |

### No rotation

Same refresh token until `expires_at`; only access JWT rotates.

| Pros            | Cons                                            |
| --------------- | ----------------------------------------------- |
| Simpler client  | Stolen refresh valid until expiry               |
| Fewer DB writes | Weaker security story for a production template |

### Revoke vs delete on logout

| Approach                           | Behavior                                     |
| ---------------------------------- | -------------------------------------------- |
| **Set `revoked_at`** (recommended) | Row kept; lookup checks `revoked_at IS NULL` |
| **Delete row**                     | Simpler queries; no audit trail              |

**Recommendation:** Rotation + `revoked_at`. Matches prior experience with option B and is appropriate for a production starter template.

---

## API design

### Endpoints

| Method | Path            | Auth   | Body                     | Response         |
| ------ | --------------- | ------ | ------------------------ | ---------------- |
| `POST` | `/auth/login`   | Public | `{ username, password }` | `TokenResponse`  |
| `POST` | `/auth/refresh` | Public | `{ refresh_token }`      | `TokenResponse`  |
| `POST` | `/auth/logout`  | Public | `{ refresh_token }`      | `204 No Content` |

**Register:** Keep `POST /users` as the registration endpoint (YAGNI — no duplicate `/auth/register` unless desired later).

**Users route policy (template default):** Leave `/users` public for now; document as demo scaffolding. Protecting routes with `CurrentUserDep` is a follow-up task once `get_current_user` exists — do not block refresh-token work on a full users auth policy change.

### Schemas (`features/auth/schemas.py`)

```python
class LoginRequest(BaseModel):
    username: str
    password: SecretStr

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

Use `SecretStr` for passwords; plain `str` for refresh token in request body.

### Errors (`features/auth/errors.py`)

| Domain error                     | HTTP                                                |
| -------------------------------- | --------------------------------------------------- |
| `InvalidCredentialsError`        | 401 — bad username/password on login                |
| `InvalidRefreshTokenError`       | 401 — missing, expired, revoked, or unknown refresh |
| `UserNotFoundError` (from users) | 404 — only if re-used outside login                 |

Login should return **401** for bad credentials (not 404) to avoid username enumeration.

---

## Config

New `JWTSettings` in `core/config/jwt.py`, nested on root `Settings`:

| Env var                     | Default      | Purpose                                    |
| --------------------------- | ------------ | ------------------------------------------ |
| `JWT_SECRET`                | **required** | HS256 signing key                          |
| `JWT_ALGORITHM`             | `HS256`      | Algorithm allowlist                        |
| `JWT_ACCESS_EXPIRE_MINUTES` | `15`         | Access token TTL                           |
| `JWT_REFRESH_EXPIRE_DAYS`   | `7`          | Refresh token TTL                          |
| `JWT_ISSUER`                | optional     | Maps to `APP_NAME` or explicit `iss` claim |

Add to `.env.example`:

```env
JWT_SECRET=change-me-in-production
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7
```

Test isolation: set `JWT_SECRET` in `tests/app/conftest.py` (same pattern as `DB_URL`).

---

## Core helpers

New `core/security/tokens.py`:

```python
def make_refresh_token() -> str:
    return secrets.token_urlsafe(32)

def hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
```

Export from `core/security/__init__.py`. Keep separate from `auth.py` (password + access JWT).

---

## AuthService flow

### Login

1. Look up `User` by `username` (add `UserService.get_by_username` or inline scalar query in auth service).
2. `verify_password` → else `InvalidCredentialsError`.
3. `create_access_token(user.id, secret=..., expires_minutes=..., issuer=...)`.
4. `raw = make_refresh_token()` → persist `hash_refresh_token(raw)` with `expires_at`.
5. Return `TokenResponse(access_token=..., refresh_token=raw)`.

### Refresh (with rotation)

1. `token_hash = hash_refresh_token(refresh_token)`.
2. Load row where `token_hash` matches, `revoked_at IS NULL`, `expires_at > now()`.
3. Else `InvalidRefreshTokenError`.
4. Set `revoked_at = now()` on old row.
5. Issue new access JWT + new refresh row (same as login steps 3–5).
6. Return new `TokenResponse`.

### Logout

1. Hash incoming refresh token; find active row.
2. Set `revoked_at = now()` (idempotent — unknown/already-revoked → still `204`).
3. Return `204`.

---

## Dependencies

New `project_name/app/dependencies/auth.py`:

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> UUID:
    payload = decode_access_token(token, secret=..., issuer=...)
    if payload.get("type") != "access":
        raise HTTPException(401, ...)
    return UUID(str(payload["sub"]))

def get_current_user(session: SessionDep, user_id: UUID = Depends(get_current_user_id)) -> User:
    ...
```

Export `CurrentUserDep` from `dependencies/__init__.py`. Not wired to `/users` routes in this phase.

---

## Testing strategy

Explicit test cases (no parametrization), matching `test_auth.py` style.

| File                                       | Cases                                                                                                                        |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| `tests/app/core/security/test_tokens.py`   | `make_refresh_token` uniqueness; hash stable/different inputs                                                                |
| `tests/app/features/auth/test_services.py` | login success; bad password; refresh success + rotation; expired refresh; revoked refresh; logout revokes; logout idempotent |
| `tests/app/features/auth/test_router.py`   | HTTP mapping for 200/401/204 via `client` fixture                                                                            |
| `tests/app/core/config/test_jwt.py`        | defaults; required secret; env override                                                                                      |

Use `expires` manipulation (negative TTL or backdated `expires_at` on DB row) — never `time.sleep`.

---

## File checklist

| Action | Path                                                                  |
| ------ | --------------------------------------------------------------------- |
| Create | `project_name/app/core/config/jwt.py`                                 |
| Create | `project_name/app/core/security/tokens.py`                            |
| Create | `project_name/app/features/auth/errors.py`                            |
| Create | `project_name/app/features/auth/schemas.py`                           |
| Create | `project_name/app/features/auth/services.py`                          |
| Create | `project_name/app/features/auth/router.py`                            |
| Create | `project_name/app/features/auth/__init__.py`                          |
| Create | `project_name/app/dependencies/auth.py`                               |
| Create | `project_name/app/database/versions/YYYYMMDD_*_add_refresh_tokens.py` |
| Create | `tests/app/core/security/test_tokens.py`                              |
| Create | `tests/app/features/auth/test_services.py`                            |
| Create | `tests/app/features/auth/test_router.py`                              |
| Create | `tests/app/core/config/test_jwt.py`                                   |
| Modify | `project_name/app/features/auth/models.py`                            |
| Modify | `project_name/app/core/config/settings.py`                            |
| Modify | `project_name/app/core/config/__init__.py`                            |
| Modify | `project_name/app/core/security/__init__.py`                          |
| Modify | `project_name/app/dependencies/__init__.py`                           |
| Modify | `project_name/app/main.py`                                            |
| Modify | `project_name/app/features/users/services.py` (add `get_by_username`) |
| Modify | `.env.example`                                                        |
| Modify | `tests/app/conftest.py`                                               |
| Modify | `README.md` (auth section)                                            |

---

## Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans. Steps use checkbox syntax.

**Goal:** Complete option-B auth: login, refresh with rotation, logout, and DB-backed refresh tokens wired to existing access JWT helpers.

**Architecture:** Opaque refresh tokens hashed in `refresh_tokens`; access JWT stays stateless; auth workflow lives in `features/auth/`; bearer validation in `dependencies/`.

**Tech stack:** FastAPI, SQLAlchemy 2, Alembic, PyJWT, argon2, pytest

---

### Task 1: JWT settings

**Files:**

- Create: `project_name/app/core/config/jwt.py`
- Modify: `project_name/app/core/config/settings.py`, `__init__.py`
- Create: `tests/app/core/config/test_jwt.py`
- Modify: `tests/app/conftest.py`, `.env.example`

- [x] Write failing tests for `JWTSettings` (required secret, defaults, env override)
- [x] Implement `JWTSettings` with `env_prefix="JWT_"`
- [x] Nest on `Settings`; export from config `__init__`
- [x] Set test env vars in conftest; update `.env.example`
- [x] Run `uv run pytest tests/app/core/config/test_jwt.py -q`

---

### Task 2: Refresh token helpers

**Files:**

- Create: `project_name/app/core/security/tokens.py`
- Modify: `project_name/app/core/security/__init__.py`
- Create: `tests/app/core/security/test_tokens.py`

- [x] Test `hash_refresh_token` is deterministic and differs per input
- [x] Test `make_refresh_token` returns url-safe strings of sufficient length
- [x] Implement helpers with `secrets` + `hashlib.sha256`
- [x] Export from `core/security/__init__.py`
- [x] Run security tests

---

### Task 3: RefreshToken model + migration

**Files:**

- Modify: `project_name/app/features/auth/models.py`
- Create: Alembic revision under `project_name/app/database/versions/`

- [x] Update model: `id` (uuid7 pk), `token_hash`, `revoked_at`, timestamps
- [x] Run `uv run alembic revision --autogenerate -m "add refresh tokens"`
- [x] Review migration (FK cascade, unique index on `token_hash`)
- [x] Apply locally: `uv run alembic upgrade head`

---

### Task 4: Auth domain layer

**Files:**

- Create: `project_name/app/features/auth/errors.py`
- Create: `project_name/app/features/auth/schemas.py`
- Modify: `project_name/app/features/users/services.py` — add `get_by_username`

- [ ] Define `InvalidCredentialsError`, `InvalidRefreshTokenError`
- [ ] Define `LoginRequest`, `RefreshRequest`, `TokenResponse`
- [ ] Add `UserService.get_by_username(session, username) -> User` raising `UserNotFoundError`

---

### Task 5: AuthService (TDD)

**Files:**

- Create: `project_name/app/features/auth/services.py`
- Create: `tests/app/features/auth/test_services.py`

- [ ] **login:** success returns tokens; wrong password → `InvalidCredentialsError`; unknown user → `InvalidCredentialsError`
- [ ] **refresh:** success returns new pair; old row revoked; old refresh token rejected afterward
- [ ] **refresh:** expired / revoked / garbage token → `InvalidRefreshTokenError`
- [ ] **logout:** sets `revoked_at`; idempotent on unknown token
- [ ] Implement `AuthService.login`, `.refresh`, `.logout` using settings + core helpers
- [ ] Run service tests with `db_session` fixture

---

### Task 6: Auth router

**Files:**

- Create: `project_name/app/features/auth/router.py`
- Create: `project_name/app/features/auth/__init__.py`
- Create: `tests/app/features/auth/test_router.py`
- Modify: `project_name/app/main.py`

- [ ] Map domain errors → 401; success → 200 / 204
- [ ] `POST /auth/login`, `/auth/refresh`, `/auth/logout`
- [ ] Register `auth_router` in `main.py`
- [ ] Router tests via `client` fixture (create user, login, refresh, logout)
- [ ] Run router + full test suite

---

### Task 7: get_current_user dependency

**Files:**

- Create: `project_name/app/dependencies/auth.py`
- Modify: `project_name/app/dependencies/__init__.py`
- Create: `tests/app/dependencies/test_auth.py` (or test via a minimal protected test route)

- [ ] Implement `get_current_user_id` + `get_current_user` with `type == "access"` check
- [ ] Test valid bearer, missing bearer, expired access token, wrong type claim
- [ ] Export `CurrentUserDep`; **do not** wire to `/users` yet

---

### Task 8: Documentation

**Files:**

- Modify: `README.md`

- [ ] Add "Authentication" section: env vars, login/refresh/logout examples, note that `/users` remains demo-public until protected
- [ ] Document refresh rotation (client must store new refresh token)

---

## Out of scope (follow-ups)

- Protecting `/users` routes with `CurrentUserDep`
- `POST /auth/register` (use `POST /users`)
- Refresh token family / reuse detection (advanced rotation)
- Rate limiting on login
- Cookie-based refresh (httpOnly) — body token is fine for API template

---

## Spec self-review

- [x] No TBD placeholders
- [x] Consistent with prior brainstorming (option B, features/auth, no middleware)
- [x] Single implementation cycle — not decomposed further
- [x] Model uses `token_hash` not plain `token` (explicit)
- [x] Users route policy documented as unchanged in this phase

---

## Review

Please review this document at `docs/superpowers/brainstorming/2026-06-12-refresh-tokens.md`. Once approved, the next step is executing the implementation plan (Tasks 1–8) — no code changes until you sign off or request edits.
