#!/usr/bin/env python3
"""
Manage the alert hook's TTS voice (edge-tts).
State persists in alert_voice.state read by alert.py's get_voice().

Usage:
  python alert_voice.py list
  python alert_voice.py status
  python alert_voice.py set <voice>
  python alert_voice.py sample <voice>
"""

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK_DIR = os.path.dirname(SCRIPT_DIR)
STATE_FILE = os.path.join(HOOK_DIR, "alert_voice.state")
DEFAULT_VOICE = "en-GB-SoniaNeural"
ALERT_PY = os.path.join(SCRIPT_DIR, "alert.py")

VOICES = [
    ("en-GB-SoniaNeural", "Sonia (UK, female) — current default", "Hello, this is Sonia."),
    ("en-GB-RyanNeural", "Ryan (UK, male)", "Hello, this is Ryan."),
    ("en-US-AriaNeural", "Aria (US, female)", "Hello, this is Aria."),
    ("en-US-GuyNeural", "Guy (US, male)", "Hello, this is Guy."),
    ("en-US-JennyNeural", "Jenny (US, female)", "Hello, this is Jenny."),
    ("en-AU-NatashaNeural", "Natasha (Australia, female)", "Hello, this is Natasha."),
    ("en-IE-ConnorNeural", "Connor (Ireland, male)", "Hello, this is Connor."),
    ("en-IN-NeerjaNeural", "Neerja (India, female)", "Hello, this is Neerja."),
]


def get_status() -> str:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                v = f.read().strip()
                if v:
                    return v
        except Exception:
            pass
    return DEFAULT_VOICE


def list_voices():
    current = get_status()
    print("Available voices:")
    for name, label, _ in VOICES:
        if name == current:
            print(f"  * {name} — {label}  [current]")
        else:
            print(f"    {name} — {label}")


def set_voice(target: str):
    if not target:
        print("Error: Voice name required. Run 'alert_voice.py list' to see available voices.", file=sys.stderr)
        sys.exit(1)

    found = None
    for name, _, _ in VOICES:
        if name.lower() == target.lower():
            found = name
            break

    # Also allow any custom edge-tts voice name
    if not found:
        found = target

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(found + "\n")
    print(f"Alert voice set to {found} (state: {STATE_FILE})")


def sample_voice(target: str):
    if not target:
        target = get_status()

    preview_line = "Hello, this is a voice sample."
    for name, _, line in VOICES:
        if name.lower() == target.lower():
            target = name
            preview_line = line
            break

    print(f"Sampling voice: {target} (\"{preview_line}\")")
    subprocess.run([sys.executable, ALERT_PY, "--message", preview_line, "--voice", target, "--sound", "noti"])


def main():
    if len(sys.argv) < 2:
        list_voices()
        return

    cmd = sys.argv[1].lower()
    if cmd == "list":
        list_voices()
    elif cmd == "status":
        print(get_status())
    elif cmd == "set":
        target = sys.argv[2] if len(sys.argv) > 2 else ""
        set_voice(target)
    elif cmd == "sample":
        target = sys.argv[2] if len(sys.argv) > 2 else ""
        sample_voice(target)
    else:
        print("Usage: alert_voice.py {list|status|set <voice>|sample <voice>}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
