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
  (mutagen only needed as a rare fallback; not required for normal use)
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
import threading
import time


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

# Individual volume settings (MCI volume range: 0 ~ 1000)
BELL_VOLUME = 200  # Notification bell volume
TTS_VOLUME = 1000   # TTS speech volume

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_duration_seconds(path: str) -> float:
    """Read the real playback duration of an mp3 file using mutagen.
    Falls back to a conservative estimate if mutagen isn't available."""
    try:
        from mutagen.mp3 import MP3
        return float(MP3(path).info.length)
    except Exception as e:
        debug_log(f"DURATION_FALLBACK: {type(e).__name__}: {e}")
        # Fallback: rough estimate from file size (mp3 ~ 16KB/sec at typical bitrate).
        try:
            size = os.path.getsize(path)
            return max(1.0, size / 16000)
        except Exception:
            return 2.0


def _play_windows_mci(path: str, volume: int) -> None:
    """Play an mp3 file on Windows using the built-in MCI API directly
    (winmm.dll), instead of spawning a PowerShell process. This avoids the
    multi-second overhead of starting PowerShell and loading .NET assemblies
    (Add-Type), and 'play ... wait' blocks for exactly the real duration."""
    import ctypes

    winmm = ctypes.windll.winmm
    alias = f"alert{threading.get_ident()}{int(time.time() * 1000)}"
    try:
        winmm.mciSendStringW(f'open "{path}" type mpegvideo alias {alias}', None, 0, None)
        winmm.mciSendStringW(f'setaudio {alias} volume to {volume}', None, 0, None)
        winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
    finally:
        winmm.mciSendStringW(f'close {alias}', None, 0, None)


def _play_blocking(path: str, volume: int = 1000) -> None:
    """Play an audio file and wait for it to finish."""
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["afplay", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif system == "Windows":
        try:
            _play_windows_mci(path, volume)
        except Exception as e:
            debug_log(f"MCI_ERROR: {type(e).__name__}: {e}")
            # Fallback to the PowerShell approach if MCI fails for some reason.
            duration = _get_duration_seconds(path)
            ps = (
                "Add-Type -AssemblyName presentationCore;"
                "$p = New-Object System.Windows.Media.MediaPlayer;"
                f"$p.Open([uri]'{path}');"
                f"$p.Volume = {volume / 1000.0:.2f};"
                "$p.Play();"
                f"Start-Sleep -Seconds {duration + 0.3:.2f};"
                "$p.Stop(); $p.Close()"
            )
            subprocess.run(["powershell", "-Command", ps], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["mpv", "--no-video", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def play(path: str, volume: int = 1000) -> None:
    """Play an audio file and wait for it to finish (blocking)."""
    _play_blocking(path, volume)


def play_async(path: str, volume: int = 1000) -> threading.Thread:
    """Start playing an audio file in the background; returns immediately."""
    t = threading.Thread(target=_play_blocking, args=(path, volume), daemon=True)
    t.start()
    return t


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
    """Play a notification sound while generating TTS in parallel, then play the TTS.

    The bell/noti sound and the TTS generation (which is a network round-trip
    to edge-tts) run at the same time instead of one after another, so the
    perceived delay is roughly max(bell duration, TTS generation time)
    instead of the sum of both.
    """
    t_start = time.time()
    message = sanitize(message)
    sound_path = NOTI_PATH if sound == "noti" else BELL_PATH

    # Start the notification sound immediately, without waiting for it.
    bell_thread = play_async(sound_path, volume=BELL_VOLUME)
    t_bell_started = time.time()
    debug_log(f"TIMING: bell thread launched at +{t_bell_started - t_start:.2f}s")

    # Generate the TTS audio while the bell is playing.
    tmp_path = None
    try:
        import edge_tts

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        communicate = edge_tts.Communicate(message, VOICE, rate=RATE)
        asyncio.run(communicate.save(tmp_path))
        t_tts_done = time.time()
        debug_log(f"TIMING: TTS generated at +{t_tts_done - t_start:.2f}s "
                   f"(took {t_tts_done - t_bell_started:.2f}s)")
    except Exception as e:
        debug_log(f"TTS_ERROR: {type(e).__name__}: {e}")
        t_tts_done = time.time()

    # Make sure the bell has finished before the TTS starts, so they don't
    # overlap (usually already true, since TTS generation takes longer).
    bell_thread.join()
    t_bell_done = time.time()
    debug_log(f"TIMING: bell finished at +{t_bell_done - t_start:.2f}s "
               f"(bell playback took {t_bell_done - t_bell_started:.2f}s)")

    if tmp_path and os.path.exists(tmp_path):
        try:
            play(tmp_path, volume=TTS_VOLUME)
            t_tts_played = time.time()
            debug_log(f"TIMING: TTS playback finished at +{t_tts_played - t_start:.2f}s "
                       f"(playback took {t_tts_played - t_bell_done:.2f}s)")
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass

    debug_log(f"TIMING: total elapsed {time.time() - t_start:.2f}s")


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
