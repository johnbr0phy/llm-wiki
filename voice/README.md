# Wiki Voice 🎙️

Press a global hotkey, ask a question out loud, and hear your wiki answer back —
a realtime voice conversation grounded in this repo's `wiki/`.

It connects to OpenAI's **`gpt-realtime-2`** speech-to-speech model over a
WebSocket. The model is given a compact *map* of the wiki (all indexes + every
article's TLDR) and two tools — `search_wiki` and `read_article` — so it can
pull detail on demand. This mirrors the read-path in the repo's `CLAUDE.md`
(INDEX → section INDEX → TLDRs → full article). The Realtime API does not do
retrieval on its own; the tools are how the model reaches your wiki.

## Architecture

```
 hotkey ──toggle──► mic (24kHz PCM16) ──WebSocket──► gpt-realtime-2
                                                        │  speaks reply (audio)
   search_wiki / read_article  ◄──tool calls──────────┘  reads your wiki/*.md
        │
        └── wiki/  (markdown articles, the source of truth)
```

Everything runs locally on your Mac and in one process — no extra server.

## Quick start (macOS)

```bash
cd voice
./setup.sh                 # installs everything (portaudio, venv, deps), makes .env
# put your OpenAI API key in voice/.env (replace sk-...)
./run.sh                   # press Ctrl+Option+W to talk
```

That's it. `setup.sh` is idempotent — re-run it any time. The only thing you
provide is your **OpenAI API key**.

### Handing this to Claude

If you'd rather let Claude do it, open this folder in Claude Code and say:

> Set up and run the wiki voice. My OpenAI API key is `sk-...`

Claude will run `setup.sh`, drop your key into `.env`, and launch it.

### First-run permissions

The first time you run it, macOS prompts for **Microphone** (allow it). For the
global hotkey, grant your terminal app **Accessibility**: System Settings →
Privacy & Security → Accessibility → enable Terminal/iTerm, then relaunch.

<details>
<summary>Manual setup (if you prefer not to use the scripts)</summary>

```bash
brew install portaudio
cd voice
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
python wiki_voice.py
```
</details>

## Using it

```bash
./run.sh
```

- Press the hotkey (**Ctrl + Option (⌥) + W** by default) to **toggle listening**.
- Speak; pause when done — server-side voice detection ends your turn and the
  model replies out loud. Keep talking for a back-and-forth conversation.
- Start talking while it's speaking to **interrupt** (barge-in).
- Toggle the hotkey again to mute. **Ctrl + C** to quit.

### Options

```bash
# Flags pass through run.sh. In hotkey strings, <alt> = Option (⌥), <cmd> = Command (⌘).
./run.sh --hotkey '<ctrl>+<alt>+space'   # = Ctrl + Option + Space
./run.sh --voice cedar                   # change the voice
./run.sh --model gpt-realtime-2          # change the model
./run.sh --debug                         # print raw server events
```

Environment overrides: `WIKI_VOICE_MODEL`, `WIKI_VOICE_VOICE`,
`WIKI_VOICE_HOTKEY`, `WIKI_VOICE_WIKI_DIR`, `WIKI_VOICE_BETA_HEADER`.

## Cost note

`gpt-realtime-2` bills audio tokens (~$32/1M in, $64/1M out as of May 2026).
Voice chat adds up; the wiki map sits in the cached system prompt, and the tools
keep retrieved context tight to limit spend.

## Troubleshooting

- **Hotkey does nothing** → grant Accessibility permission and restart the app.
- **No audio in/out** → confirm `brew install portaudio` and Microphone
  permission; check your default input/output device.
- **API rejects a session field** → the Realtime wire format evolves. Run with
  `--debug` to see the `error` event, then adjust `_configure_session` in
  `wiki_voice.py` (e.g. nested `audio` config vs. the flat fields used here).
- **`additional_headers` error** → upgrade `websockets` (older versions used
  `extra_headers`).

## Files

- `wiki_voice.py` — realtime client: audio, hotkey, WebSocket, tool dispatch.
- `wiki_context.py` — wiki loading, the `search_wiki`/`read_article` tools, and
  the system instructions.
