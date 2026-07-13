#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/.git/hooks"
cp "$ROOT/scripts/git-hooks/prepare-commit-msg" "$ROOT/.git/hooks/prepare-commit-msg"
chmod +x "$ROOT/.git/hooks/prepare-commit-msg"
echo "Installed prepare-commit-msg (strips Cursor co-author trailers)."
