#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYPROJECT="$REPO_ROOT/pyproject.toml"
INIT_PY="$REPO_ROOT/src/claudelint/__init__.py"

current_version=$(sed -n 's/^version = "\(.*\)"/\1/p' "$PYPROJECT")

if [[ -z "$current_version" ]]; then
    echo "Error: could not determine current version from $PYPROJECT" >&2
    exit 1
fi

if [[ $# -eq 1 ]]; then
    new_version="$1"
else
    IFS='.' read -r major minor patch <<< "$current_version"
    new_version="$major.$minor.$((patch + 1))"
fi

echo "Bumping version: $current_version -> $new_version"

sed -i '' "s/^version = \"$current_version\"/version = \"$new_version\"/" "$PYPROJECT"
sed -i '' "s/^__version__ = \"$current_version\"/__version__ = \"$new_version\"/" "$INIT_PY"

echo "Updated:"
echo "  $PYPROJECT"
echo "  $INIT_PY"
