#!/usr/bin/env bash
# Quick check that Caliper demo data is compiled and voice env is ready.
set -euo pipefail
cd "$(dirname "$0")"

echo "📚 Wiki demo check"
./.venv/bin/python - <<'PY'
import wiki_context
import wiki_compiler

ctx = wiki_context.build_system_context()
articles = [l for l in ctx.splitlines() if l.startswith("- `")]
pending = wiki_compiler.find_pending_sources()
print(f"  Articles in voice map: {len(articles)}")
print(f"  Pending raw files:     {len(pending)}")
if len(articles) < 10:
    raise SystemExit("  ❌ Expected 10+ articles — run compile or check wiki/")
if "caliper" not in ctx.lower():
    raise SystemExit("  ❌ Caliper content not found in wiki map")
print("  ✓ Caliper demo wiki looks good")
PY

if grep -q "^OPENAI_API_KEY=sk-\.\.\.$" .env 2>/dev/null; then
  echo
  echo "⚠️  Add your OpenAI API key to voice/.env, then:  ./run.sh"
  echo "   See DEMO.md for the voice demo script."
  exit 0
fi

echo
echo "✅ Ready to demo. Run:  ./run.sh"
echo "   See DEMO.md for suggested questions."