# fastaip-app

Python 3.14 project template with strict typing using basedpyright, Ruff, pytest, and uv.

Requires [uv](https://docs.astral.sh/uv/).

```bash
project_name/          # rename after cloning
packages/example_lib/   # optional uv workspace library (example)
tests/
```

## Getting started

Clone templates, copy and paste fastapi-app.

```bash
git clone https://github.com/evanwiseman/templates.git
```

Rename the package, then finish setup:

```bash
make rename NAME=your_package   # one-time; rewrites config, source, and tests
make install                    # copies .env.example -> .env if missing
# start PostgreSQL and match DB_URL in .env (default: localhost:5432/fastapi_app)
uv run alembic upgrade head
make run              # needs live DB — engine connects at import
make check
```

### Database

App uses PostgreSQL via SQLAlchemy. No `docker-compose` or migration Makefile targets yet — run Alembic directly.

1. **Start PostgreSQL** — local install, Docker, or your own host. Create a database matching `DB_URL` in `.env` (see `.env.example`).
2. **Configure `.env`** — `make install` seeds `.env` from `.env.example` if absent. Set `DB_URL` (e.g. `postgresql+psycopg://user:pass@localhost:5432/fastapi_app`).
3. **Apply migrations** — from repo root:

   ```bash
   uv run alembic upgrade head
   ```

4. **Run the app** — `make run` calls `uv run main`. The SQLAlchemy `engine` is created when `project_name.app.database.engine` is imported, so PostgreSQL must already be reachable or startup fails before the server binds.

**New migrations** (no `make migrate` / `make revision` targets):

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

See `project_name/app/database/` for Alembic env and versions.

### Rename / refactor

```bash
make rename NAME=your_package
```

`scripts/rename_project.sh` renames `project_name/` and updates the paths below. Skips `docs/`, `uv.lock`, and `.venv`. Manual fallback:

**`project_name/`** — rename the directory.

**`pyproject.toml`**

- `[project] name`
- `[project.scripts] main`
- `[tool.hatch.build.targets.wheel] packages`
- `[tool.ruff] src` and `[tool.ruff.lint.isort] known-first-party`
- `[tool.basedpyright] include`
- pytest `--cov=` and `[tool.coverage.run] source` / `omit`

**`alembic.ini`** — `script_location` under `<package>/app/database`

**`Makefile`** — `CHECK` paths and `build-project --package`

**`.pre-commit-config.yaml`** — Ruff and basedpyright hook paths

**Source + tests** — `from project_name.app.*` / `import project_name.*` under `project_name/` and `tests/`

After rename: `make install`, `make check`, then delete `scripts/rename_project.sh` (one-time use).

## Usage

| Target                | Description                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| `make install`        | Install project + dev tools                                             |
| `make rename`         | Rename `project_name` (`NAME=your_package`)                             |
| `make run`            | Run the application                                                     |
| `make check`          | Local quality pipeline (format may autofix, then lint, typecheck, test) |
| `make ci`             | Read-only quality gate (same checks as GitHub Actions CI)               |
| `make format`         | Ruff format + fixes                                                     |
| `make lint`           | Ruff check                                                              |
| `make typecheck`      | basedpyright                                                            |
| `make test`           | pytest with coverage                                                    |
| `make skylos`         | Skylos (dead code, secrets, quality)                                    |
| `make prek`           | Run pre-commit hooks                                                    |
| `make lock`           | Refresh `uv.lock`                                                       |
| `make build`          | Build wheels/sdists                                                     |
| `make build-project`  | Build project only                                                      |
| `make build-packages` | Build workspace packages only                                           |
| `make clean`          | Remove caches, coverage, and build artifacts                            |
| `make help`           | List all targets                                                        |

## Tooling

| Concern                  | Tool                                    |
| ------------------------ | --------------------------------------- |
| Format + lint + security | Ruff (`S` rules)                        |
| Types                    | basedpyright (`strict` + extra reports) |
| Dead code / secrets      | Skylos                                  |
| Tests + coverage         | pytest                                  |

### Hooks vs CI

| Command     | When                            | What it runs                             |
| ----------- | ------------------------------- | ---------------------------------------- |
| `make prek` | Before each commit (fast)       | Ruff format/check, basedpyright          |
| `make ci`   | Before push / in GitHub Actions | Above + format `--check`, Skylos, pytest |

## Workspace libraries

`packages/example_lib/` demonstrates a uv workspace member. It is **not** linked to the app by default. See `packages/example_lib/README.md` to wire it in, or delete the directory and remove it from the `CHECK` paths in the `Makefile` if you do not need a monorepo layout.
