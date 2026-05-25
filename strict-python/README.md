# strict-python

Python 3.12 project template with strict typing using basedpyright, Ruff, pytest, and uv.

Requires [uv](https://docs.astral.sh/uv/).

```
strict_python/          # application package (rename after cloning)
packages/example_lib/   # optional uv workspace library (example)
tests/
```

## Getting started

Clone and enter the project:

```bash
git clone https://github.com/evanwiseman/templates.git
cd templates/strict-python
```

Rename the package and project metadata (`strict_python/`, `pyproject.toml` `name`, imports in `tests/`). Then:

```bash
make install
make run    # exits 0; logging is not configured (see note below)
make check
```

Copy `.env.example` to `.env` when you add settings that read from the environment.
```bash
cp .env.example .env
```

## Tooling

| Concern | Tool |
|---------|------|
| Format + lint + security | Ruff (`S` rules) |
| Types | basedpyright (`strict` + extra reports) |
| Dead code / secrets | Skylos |
| Tests + coverage | pytest |

### Hooks vs CI

| Command | When | What it runs |
|---------|------|----------------|
| `make prek` | Before each commit (fast) | Ruff format/check, basedpyright |
| `make ci` | Before push / in GitHub Actions | Above + format `--check`, Skylos, pytest |

### `make run` and logging

The sample entrypoint uses the stdlib `logging` module but does not call `logging.basicConfig()`. Tests capture logs with pytest; a bare `make run` prints nothing at INFO. Configure logging in your entrypoint when you are ready.

## Workspace libraries

`packages/example_lib/` demonstrates a uv workspace member. It is **not** linked to the app by default. See `packages/example_lib/README.md` to wire it in, or delete the directory and remove it from the `CHECK` paths in the `Makefile` if you do not need a monorepo layout.

## Strictness tuning

Defaults are intentionally strict. When you add third-party dependencies, you may need to adjust or add stubs:

| Symptom | Knob |
|---------|------|
| Missing stubs for a library | `reportMissingTypeStubs` in `[tool.basedpyright]`, or add types/stubs |
| Noisy `Unknown*` reports on untyped libs | Relax `reportUnknownArgumentType`, `reportUnknownMemberType`, or `reportUnknownVariableType` |
| Test-only noise | `[tool.ruff.lint.per-file-ignores]` for `tests/**` (already has some) |
| Coverage below 80% as the codebase grows | `--cov-fail-under` in `[tool.pytest.ini_options]` |

Prefer targeted overrides over disabling `typeCheckingMode = "strict"`.

## Usage

| Target | Description |
|--------|-------------|
| `make install` | Install project + dev tools |
| `make run` | Run the application |
| `make check` | Local quality pipeline (format may autofix, then lint, typecheck, test) |
| `make ci` | Read-only quality gate (same checks as GitHub Actions CI) |
| `make format` | Ruff format + fixes |
| `make lint` | Ruff check |
| `make typecheck` | basedpyright |
| `make test` | pytest with coverage |
| `make skylos` | Skylos (dead code, secrets, quality) |
| `make prek` | Run pre-commit hooks |
| `make lock` | Refresh `uv.lock` |
| `make build` | Build wheels/sdists (app + workspace packages) |
| `make build-app` | Build app only |
| `make build-packages` | Build workspace packages only |
| `make clean` | Remove caches, coverage, and build artifacts |
| `make help` | List all targets |

## CI

GitHub Actions runs on push and pull requests to `main`:

- **Quality** — `make ci`
- **Build** — `make build` (app + workspace packages)

Workflow file: `.github/workflows/ci.yml`. If this project lives in a monorepo subdirectory, add a root workflow with `working-directory` set to this folder (see the parent `templates` repo).
