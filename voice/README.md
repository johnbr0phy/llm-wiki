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

## Setup (macOS)

1. **Python 3.10+** and PortAudio (for the audio library):
   ```bash
   brew install portaudio
   cd voice
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **API key:**
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

3. **Grant permissions** to the app you run this from (Terminal, iTerm, etc.) in
   **System Settings → Privacy & Security**:
   - **Microphone** (to capture your voice)
   - **Accessibility** (so the global hotkey works system-wide)

## Run

```bash
python wiki_voice.py
```

- Press the hotkey (**Ctrl + Option (⌥) + W** by default) to **toggle listening**.
- Speak; pause when done — server-side voice detection ends your turn and the
  model replies out loud. Keep talking for a back-and-forth conversation.
- Start talking while it's speaking to **interrupt** (barge-in).
- Toggle the hotkey again to mute. **Ctrl + C** to quit.

### Options

```bash
# In hotkey strings, <alt> = the Option (⌥) key on macOS, <cmd> = Command (⌘).
python wiki_voice.py --hotkey '<ctrl>+<alt>+space'   # = Ctrl + Option + Space
python wiki_voice.py --voice cedar                   # change the voice
python wiki_voice.py --model gpt-realtime-2          # change the model
python wiki_voice.py --debug                         # print raw server events
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
