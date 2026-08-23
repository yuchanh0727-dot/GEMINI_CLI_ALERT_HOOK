"""
Gemini CLI alert hook.

AfterAgent hook: reads the AfterAgent JSON from stdin, parses the
<!-- tts: {"m": "..."} --> tag from `prompt_response`, then plays
bell.mp3 followed by TTS audio.

Notification hook: called with --message/--sound directly to announce
tool-permission requests.

Manual test: python alert.py --message "your text here"

Dependencies:
  pip install edge-tts
"""

import argparse
import asyncio
import json
import os
import platform
import re
import subprocess
import sys
import tempfile


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK_DIR = os.path.dirname(SCRIPT_DIR)
BELL_PATH = os.path.join(HOOK_DIR, "sounds", "bell.mp3")
NOTI_PATH = os.path.join(HOOK_DIR, "sounds", "noti.mp3")
DEBUG_PATH = os.path.join(SCRIPT_DIR, "alert_debug.json")

VOICE = "en-GB-SoniaNeural"
RATE = "+30%"
FALLBACK_MESSAGE = "Done. Task completed."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def play(path: str) -> None:
    """Play an audio file and wait for it to finish."""
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["afplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif system == "Windows":
        ps = (
            "Add-Type -AssemblyName presentationCore;"
            "$p = New-Object System.Windows.Media.MediaPlayer;"
            f"$p.Open([uri]'{path}');"
            "Start-Sleep -Milliseconds 200;"
            "$p.Play();"
            "Start-Sleep -Milliseconds 200;"
            "$d = $p.NaturalDuration;"
            "if ($d.HasTimeSpan) {"
            "  while ($p.Position -lt $d.TimeSpan) { Start-Sleep -Milliseconds 50 }"
            "} else {"
            "  Start-Sleep -Seconds 5"
            "};"
            "$p.Stop(); $p.Close()"
        )
        subprocess.run(["powershell", "-Command", ps], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["mpv", "--no-video", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def parse_tts_tag(text: str) -> str:
    """Extract the message from <!-- tts: {"m": "..."} --> tag."""
    if not text:
        return ""
    match = re.search(r'<!--\s*tts:\s*(\{.*?\})\s*-->', text, re.DOTALL)
    if not match:
        return ""
    try:
        data = json.loads(match.group(1))
        return data.get("m", "")
    except (json.JSONDecodeError, TypeError):
        return ""


def sanitize(text: str) -> str:
    """Remove surrogate characters that break edge_tts UTF-8 encoding."""
    return text.encode("utf-8", errors="surrogatepass").decode("utf-8", errors="replace")


def debug_log(msg: str, mode: str = "a") -> None:
    """Write to the debug log."""
    try:
        with open(DEBUG_PATH, mode, encoding="utf-8") as f:
            if mode == "a":
                f.write(f"\n{msg}\n")
            else:
                f.write(msg)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# TTS
# ---------------------------------------------------------------------------

def speak(message: str, sound: str = "bell") -> None:
    """Play a notification sound then TTS for the given message."""
    message = sanitize(message)

    tmp_path = None
    try:
        import edge_tts

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        communicate = edge_tts.Communicate(message, VOICE, rate=RATE)
        asyncio.run(communicate.save(tmp_path))
    except Exception as e:
        debug_log(f"TTS_ERROR: {type(e).__name__}: {e}")

    sound_path = NOTI_PATH if sound == "noti" else BELL_PATH
    play(sound_path)
    if tmp_path and os.path.exists(tmp_path):
        try:
            play(tmp_path)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI alert hook")
    parser.add_argument("--message", "-m", type=str, default=None,
                        help="Message to speak directly (skips tag parsing, used for Notification hook)")
    parser.add_argument("--sound", "-s", type=str, default="bell",
                        choices=["bell", "noti"],
                        help="Notification sound to play (default: bell)")
    args = parser.parse_args()

    if args.message:
        # Called directly from the Notification hook (permission requests).
        speak(args.message, sound=args.sound)
        # Gemini CLI expects a JSON object on stdout (silence is mandatory
        # otherwise). Emit an empty, valid hook response.
        print(json.dumps({}))
        return

    # AfterAgent hook mode: parse hook JSON from stdin.
    data = {}
    try:
        raw = sys.stdin.read()
        if raw.strip():
            data = json.loads(raw)
    except Exception:
        pass

    # Debug log
    try:
        debug_log(json.dumps(data, indent=2, ensure_ascii=False), mode="w")
    except Exception:
        pass

    # Gemini CLI's AfterAgent hook provides the final text in
    # `prompt_response` (Claude Code called this `last_assistant_message`).
    assistant_msg = data.get("prompt_response", "")
    message = parse_tts_tag(assistant_msg) or FALLBACK_MESSAGE

    debug_log(f"TTS_MESSAGE: {message}")
    speak(message, sound=args.sound)

    # Required: print valid JSON to stdout so Gemini CLI doesn't warn.
    print(json.dumps({}))


if __name__ == "__main__":
    main()
