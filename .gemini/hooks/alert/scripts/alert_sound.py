#!/usr/bin/env python3
"""
Toggle the alert hook's sound playback on/off.
State persists in alert_sound.state read by alert.py.

Usage:
  python alert_sound.py on
  python alert_sound.py off
  python alert_sound.py status
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOOK_DIR = os.path.dirname(SCRIPT_DIR)
STATE_FILE = os.path.join(HOOK_DIR, "alert_sound.state")


def set_state(state: str):
    state = state.strip().lower()
    if state == "on":
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write("on\n")
        print(f"🔔 Alert sound ON  (state: {STATE_FILE})")
    elif state == "off":
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write("off\n")
        print(f"🔕 Alert sound OFF (state: {STATE_FILE})")
    elif state == "status":
        current = "on (default)"
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    val = f.read().strip().lower()
                    if val in ("on", "off"):
                        current = val
            except Exception:
                pass
        icon = "🔔" if current.startswith("on") else "🔕"
        print(f"{icon} Alert sound is currently: {current}")
    else:
        print("Usage: python alert_sound.py {on|off|status}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    set_state(arg)
