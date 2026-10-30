#!/usr/bin/env bash
# Manage the alert hook's TTS voice (edge-tts).
# State persists in alert_voice.state read by alert.py's get_voice().
set -euo pipefail
HOOK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATE_FILE="$HOOK_DIR/alert_voice.state"
DEFAULT_VOICE="en-GB-SoniaNeural"
ALERT_PY="$HOOK_DIR/scripts/alert.py"

# name|label|preview line
VOICES=(
  "en-GB-SoniaNeural|Sonia (UK, female) — current default|Hello, this is Sonia."
  "en-GB-RyanNeural|Ryan (UK, male)|Hello, this is Ryan."
  "en-US-AriaNeural|Aria (US, female)|Hello, this is Aria."
  "en-US-GuyNeural|Guy (US, male)|Hello, this is Guy."
  "en-US-JennyNeural|Jenny (US, female)|Hello, this is Jenny."
  "en-AU-NatashaNeural|Natasha (Australia, female)|Hello, this is Natasha."
  "en-IE-ConnorNeural|Connor (Ireland, male)|Hello, this is Connor."
  "en-IN-NeerjaNeural|Neerja (India, female)|Hello, this is Neerja."
)

list() {
  local current
  current="$(status)"
  echo "Available voices:"
  for v in "${VOICES[@]}"; do
    IFS='|' read -r name label _ <<< "$v"
    if [ "$name" = "$current" ]; then
      echo "  * $name — $label  [current]"
    else
      echo "    $name — $label"
    fi
  done
}

status() {
  if [ -f "$STATE_FILE" ]; then
    local v
    v="$(cat "$STATE_FILE")"
    echo "${v:-$DEFAULT_VOICE}"
  else
    echo "$DEFAULT_VOICE"
  fi
}

set_voice() {
  local target="${1:-}"
  local found=""
  for v in "${VOICES[@]}"; do
    IFS='|' read -r name _ _ <<< "$v"
    if [ "$name" = "$target" ]; then
      found="$name"
      break
    fi
  done
  if [ -z "$found" ]; then
    echo "Unknown voice: $target" >&2
    echo "Run 'alert_voice.sh list' to see available voices." >&2
    exit 1
  fi
  printf '%s\n' "$found" > "$STATE_FILE"
  echo "Alert voice set to $found (state: $STATE_FILE)"
}

sample() {
  local target="${1:-}"
  local line=""
  for v in "${VOICES[@]}"; do
    IFS='|' read -r name _ preview <<< "$v"
    if [ "$name" = "$target" ]; then
      line="$preview"
      break
    fi
  done
  if [ -z "$line" ]; then
    echo "Unknown voice: $target" >&2
    exit 1
  fi
  python "$ALERT_PY" --message "$line" --voice "$target" --sound noti
}

case "${1:-}" in
  list)   list ;;
  status) status ;;
  set)    set_voice "${2:-}" ;;
  sample) sample "${2:-}" ;;
  *)      echo "usage: alert_voice.sh {list|status|set <voice>|sample <voice>}" >&2; exit 1 ;;
esac
