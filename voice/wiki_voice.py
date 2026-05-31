"""Talk to your wiki: press a global hotkey, speak, hear the answer.

A minimal terminal app that connects to OpenAI's gpt-realtime-2 over a
WebSocket, streams mic audio, and plays the model's spoken reply. The model
is grounded in your wiki via two tools (see wiki_context.py).

Usage:
    export OPENAI_API_KEY=sk-...
    python wiki_voice.py                 # press Ctrl+Option+W (⌥) to toggle listening
    python wiki_voice.py --debug         # print raw server events
    python wiki_voice.py --hotkey '<ctrl>+<alt>+space'

Requires macOS Accessibility + Microphone permission for your terminal app
(System Settings -> Privacy & Security). See README.md.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import sys
import threading

import sounddevice as sd
import websockets

import wiki_context

SAMPLE_RATE = 24000          # gpt-realtime audio is pcm16, 24 kHz, mono, LE
CHANNELS = 1
BLOCK = 1200                 # 50 ms per audio block
DEFAULT_MODEL = os.environ.get("WIKI_VOICE_MODEL", "gpt-realtime-2")
DEFAULT_VOICE = os.environ.get("WIKI_VOICE_VOICE", "marin")
DEFAULT_HOTKEY = os.environ.get("WIKI_VOICE_HOTKEY", "<ctrl>+<alt>+w")


class Player:
    """Continuous output stream fed from a thread-safe PCM16 buffer."""

    def __init__(self) -> None:
        self._buf = bytearray()
        self._lock = threading.Lock()
        self._stream = sd.RawOutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=BLOCK,
            callback=self._callback,
        )

    def start(self) -> None:
        self._stream.start()

    def add(self, pcm: bytes) -> None:
        with self._lock:
            self._buf.extend(pcm)

    def clear(self) -> None:
        """Drop queued audio (used for barge-in when the user interrupts)."""
        with self._lock:
            self._buf.clear()

    def _callback(self, outdata, frames, time_info, status) -> None:  # noqa: ANN001
        need = frames * 2  # bytes for int16 mono
        with self._lock:
            take = min(need, len(self._buf))
            chunk = bytes(self._buf[:take])
            del self._buf[:take]
        if take < need:
            chunk += b"\x00" * (need - take)
        outdata[:] = chunk


class WikiVoice:
    def __init__(self, model: str, voice: str, debug: bool) -> None:
        self.model = model
        self.voice = voice
        self.debug = debug
        self.listening = False
        self.player = Player()
        self.loop: asyncio.AbstractEventLoop | None = None
        self.audio_q: asyncio.Queue[bytes] = asyncio.Queue()
        self._assistant_line = ""

    # --- audio capture (runs in PortAudio thread) --------------------------
    def _mic_callback(self, indata, frames, time_info, status) -> None:  # noqa: ANN001
        if not self.listening or self.loop is None:
            return
        data = bytes(indata)
        self.loop.call_soon_threadsafe(self.audio_q.put_nowait, data)

    # --- hotkey (runs in pynput thread) ------------------------------------
    def toggle(self) -> None:
        self.listening = not self.listening
        if self.listening:
            print("\n🎙️  listening… (speak, then pause; toggle hotkey to stop)")
        else:
            print("\n⏸️  muted")
            self.player.clear()

    # --- websocket session -------------------------------------------------
    async def run(self) -> None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            sys.exit("OPENAI_API_KEY is not set.")

        self.loop = asyncio.get_running_loop()
        url = f"wss://api.openai.com/v1/realtime?model={self.model}"
        headers = {"Authorization": f"Bearer {api_key}"}
        if os.environ.get("WIKI_VOICE_BETA_HEADER", "1") == "1":
            headers["OpenAI-Beta"] = "realtime=v1"

        async with websockets.connect(url, additional_headers=headers, max_size=None) as ws:
            await self._configure_session(ws)
            self.player.start()
            mic = sd.RawInputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16",
                blocksize=BLOCK,
                callback=self._mic_callback,
            )
            mic.start()
            print(f"Connected to {self.model}. Toggle the hotkey to start talking. Ctrl+C to quit.")
            await asyncio.gather(self._sender(ws), self._receiver(ws))

    async def _configure_session(self, ws) -> None:  # noqa: ANN001
        session = {
            "modalities": ["audio", "text"],
            "instructions": wiki_context.build_instructions(),
            "voice": self.voice,
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "whisper-1"},
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 600,
                "create_response": True,
            },
            "tools": wiki_context.TOOL_SCHEMAS,
            "tool_choice": "auto",
        }
        await ws.send(json.dumps({"type": "session.update", "session": session}))

    async def _sender(self, ws) -> None:  # noqa: ANN001
        while True:
            data = await self.audio_q.get()
            if not self.listening:
                continue
            b64 = base64.b64encode(data).decode("ascii")
            await ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": b64}))

    async def _receiver(self, ws) -> None:  # noqa: ANN001
        async for raw in ws:
            event = json.loads(raw)
            etype = event.get("type", "")
            if self.debug:
                print(f"[event] {etype}")

            if etype in ("response.audio.delta", "response.output_audio.delta"):
                self.player.add(base64.b64decode(event["delta"]))

            elif etype in (
                "response.audio_transcript.delta",
                "response.output_audio_transcript.delta",
            ):
                self._assistant_line += event.get("delta", "")
                print(event.get("delta", ""), end="", flush=True)

            elif etype in (
                "response.audio_transcript.done",
                "response.output_audio_transcript.done",
                "response.done",
            ):
                if self._assistant_line:
                    print()
                    self._assistant_line = ""

            elif etype == "conversation.item.input_audio_transcription.completed":
                print(f"\n🗣️  you: {event.get('transcript', '').strip()}")

            elif etype == "input_audio_buffer.speech_started":
                # user started talking -> stop any current playback (barge-in)
                self.player.clear()

            elif etype == "response.function_call_arguments.done":
                await self._handle_tool_call(ws, event)

            elif etype == "error":
                print(f"\n⚠️  API error: {json.dumps(event.get('error', event))}")

    async def _handle_tool_call(self, ws, event) -> None:  # noqa: ANN001
        name = event.get("name", "")
        call_id = event.get("call_id", "")
        try:
            args = json.loads(event.get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}
        if self.debug:
            print(f"\n[tool] {name}({args})")
        result = wiki_context.call_tool(name, args)
        await ws.send(
            json.dumps(
                {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": result,
                    },
                }
            )
        )
        await ws.send(json.dumps({"type": "response.create"}))


def main() -> None:
    parser = argparse.ArgumentParser(description="Voice chat over your wiki.")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--hotkey", default=DEFAULT_HOTKEY,
                        help="pynput hotkey, e.g. '<ctrl>+<alt>+w'")
    parser.add_argument("--debug", action="store_true", help="print raw server events")
    args = parser.parse_args()

    app = WikiVoice(model=args.model, voice=args.voice, debug=args.debug)

    # Global hotkey listener (pynput) runs in its own thread.
    from pynput import keyboard

    hotkeys = keyboard.GlobalHotKeys({args.hotkey: app.toggle})
    hotkeys.start()
    # On macOS pynput's <alt> is the Option (⌥) key; show a friendly label.
    pretty = (
        args.hotkey.replace("<ctrl>", "Ctrl")
        .replace("<alt>", "Option(⌥)")
        .replace("<cmd>", "Cmd(⌘)")
        .replace("<shift>", "Shift")
        .replace("+", " + ")
        .replace("<", "")
        .replace(">", "")
    )
    print(f"Hotkey: {pretty}  (toggle listening)")

    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nbye 👋")
    finally:
        hotkeys.stop()


if __name__ == "__main__":
    main()
