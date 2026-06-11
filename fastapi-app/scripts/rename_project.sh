#!/usr/bin/env bash
set -euo pipefail

OLD_NAME="project_name"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
    echo "Usage: $(basename "$0") <new_package_name>" >&2
    echo "   or: make rename NAME=<new_package_name>" >&2
    exit 1
}

[[ $# -eq 1 ]] || usage

NEW_NAME="$1"

if [[ ! "$NEW_NAME" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Invalid package name '$NEW_NAME': use snake_case ([a-z][a-z0-9_]*)" >&2
    exit 1
fi

if [[ "$NEW_NAME" == "$OLD_NAME" ]]; then
    echo "Package is already named '$OLD_NAME'." >&2
    exit 1
fi

cd "$ROOT"

if [[ ! -d "$OLD_NAME" ]]; then
    echo "Directory '$OLD_NAME/' not found — already renamed?" >&2
    exit 1
fi

if [[ -e "$NEW_NAME" ]]; then
    echo "Target '$NEW_NAME/' already exists." >&2
    exit 1
fi

replace_in_file() {
    local file="$1"
    if [[ "$(uname -s)" == Darwin ]]; then
        sed -i '' "s/${OLD_NAME}/${NEW_NAME}/g" "$file"
    else
        sed -i "s/${OLD_NAME}/${NEW_NAME}/g" "$file"
    fi
}

echo "Renaming ${OLD_NAME}/ -> ${NEW_NAME}/"

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    && git -C "$ROOT" rev-parse --show-toplevel >/dev/null 2>&1; then
    repo_root="$(git -C "$ROOT" rev-parse --show-toplevel)"
    rel_old="${ROOT#"${repo_root}/"}"
    if [[ "$rel_old" == "$ROOT" ]]; then
        rel_old="$OLD_NAME"
        rel_new="$NEW_NAME"
    else
        rel_old="${rel_old}/${OLD_NAME}"
        rel_new="${rel_old%/${OLD_NAME}}/${NEW_NAME}"
    fi
    git -C "$repo_root" mv "$rel_old" "$rel_new"
else
    mv "$OLD_NAME" "$NEW_NAME"
fi

declare -a files=(
    pyproject.toml
    alembic.ini
    Makefile
    .pre-commit-config.yaml
    README.md
)

while IFS= read -r -d '' py_file; do
    files+=("$py_file")
done < <(find "$NEW_NAME" tests -name '*.py' -print0)

for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        replace_in_file "$file"
    fi
done

remaining="$(grep -r --exclude-dir=.venv --exclude-dir=.git --exclude-dir=docs \
    --exclude=rename_project.sh -l "$OLD_NAME" . 2>/dev/null || true)"

if [[ -n "$remaining" ]]; then
    echo "Warning: '$OLD_NAME' still appears in:" >&2
    echo "$remaining" >&2
fi

echo "Renamed to '$NEW_NAME'. Next: make install && make check"
echo "Delete scripts/rename_project.sh when done (one-time setup)."
