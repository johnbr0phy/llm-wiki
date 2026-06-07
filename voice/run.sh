#!/usr/bin/env bash
# Launch Wiki Voice. Run ./setup.sh first. Extra args pass through, e.g.
#   ./run.sh --voice cedar --debug
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "No .venv yet — run ./setup.sh first." >&2
  exit 1
fi

if [[ -f .env ]]; then
  # Load via Python so <alt>+<space> isn't parsed as shell redirection.
  eval "$(./.venv/bin/python - <<'PY'
import shlex
from pathlib import Path
for line in Path(".env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    key, _, val = line.partition("=")
    val = val.strip().strip("'").strip('"')
    print(f"export {key}={shlex.quote(val)}")
PY
)"
fi

if [[ -z "${OPENAI_API_KEY:-}" || "${OPENAI_API_KEY}" == "sk-..." ]]; then
  echo "Your OpenAI API key isn't set yet — edit voice/.env and replace sk-..." >&2
  exit 1
fi

exec ./.venv/bin/python wiki_voice.py "$@"
