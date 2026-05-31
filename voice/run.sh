#!/usr/bin/env bash
# Launch Wiki Voice. Run ./setup.sh first. Extra args pass through, e.g.
#   ./run.sh --voice cedar --debug
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  echo "No .venv yet — run ./setup.sh first." >&2
  exit 1
fi

if [[ -f .env ]] && grep -q "^OPENAI_API_KEY=sk-\.\.\.$" .env; then
  echo "Your OpenAI API key isn't set yet — edit voice/.env and replace sk-..." >&2
  exit 1
fi

exec ./.venv/bin/python wiki_voice.py "$@"
