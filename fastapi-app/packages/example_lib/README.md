# example-lib

Optional uv workspace member. Copy this layout for internal libraries.

To wire into the app, add a workspace dependency in the root `pyproject.toml`:

```toml
[tool.uv.sources]
example-lib = { workspace = true }

[project]
dependencies = ["example-lib"]
```

Then run `uv lock` and `uv sync`.
