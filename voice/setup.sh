#!/usr/bin/env bash
# One-command setup for Wiki Voice. Idempotent - safe to re-run.
# Usage:
#   ./setup.sh                       # set up the environment
#   OPENAI_API_KEY=sk-... ./setup.sh # also write your key into .env
set -euo pipefail
cd "$(dirname "$0")"

echo "🎙️  Setting up Wiki Voice…"

# 1. PortAudio (needed by the audio library). macOS via Homebrew.
if [[ "$(uname)" == "Darwin" ]]; then
  if command -v brew >/dev/null 2>&1; then
    if brew list portaudio >/dev/null 2>&1; then
      echo "✓ portaudio already installed"
    else
      echo "→ installing portaudio…"
      brew install portaudio
    fi
  else
    echo "⚠️  Homebrew not found. Install it from https://brew.sh, then re-run." >&2
    echo "   (PortAudio is required for microphone/speaker access.)" >&2
    exit 1
  fi
else
  echo "ℹ️  Non-macOS: install PortAudio with your package manager if audio fails"
  echo "   (e.g. 'sudo apt-get install libportaudio2')."
fi

# 2. Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 not found. Install it (macOS: 'brew install python') and re-run." >&2
  exit 1
fi
echo "✓ $(python3 --version)"

# 3. Virtual environment
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  echo "✓ created .venv"
else
  echo "✓ .venv already exists"
fi

# 4. Dependencies
./.venv/bin/python -m pip install --quiet --upgrade pip
./.venv/bin/python -m pip install --quiet -r requirements.txt
echo "✓ dependencies installed"

# 5. .env from template
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "✓ created .env from template"
else
  echo "✓ .env already exists"
fi

# 6. If a key was provided in the environment, write it into .env
if [[ -n "${OPENAI_API_KEY:-}" && "${OPENAI_API_KEY}" != "sk-..." ]]; then
  ./.venv/bin/python - "$OPENAI_API_KEY" <<'PY'
import sys, pathlib
key = sys.argv[1]
p = pathlib.Path(".env")
lines = p.read_text().splitlines()
out, done = [], False
for line in lines:
    if line.startswith("OPENAI_API_KEY="):
        out.append(f"OPENAI_API_KEY={key}"); done = True
    else:
        out.append(line)
if not done:
    out.append(f"OPENAI_API_KEY={key}")
p.write_text("\n".join(out) + "\n")
PY
  echo "✓ wrote OPENAI_API_KEY into .env"
fi

echo
if grep -q "^OPENAI_API_KEY=sk-\.\.\.$" .env 2>/dev/null; then
  echo "👉 Last step: put your OpenAI API key in voice/.env (replace the sk-... placeholder)."
  echo "   Then run:  ./run.sh"
else
  echo "✅ Ready. Run:  ./run.sh"
fi
