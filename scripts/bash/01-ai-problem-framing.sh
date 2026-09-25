#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python_bin="$repo_root/.venv/bin/python"
if [[ ! -x "$python_bin" ]]; then
  echo "Missing repository environment: $python_bin" >&2
  echo "Create this guide's .venv as described in the preface, then install requirements.txt." >&2
  exit 1
fi
cd "$repo_root"
exec "$python_bin" "$repo_root/scripts/python/01-ai-problem-framing.py"
