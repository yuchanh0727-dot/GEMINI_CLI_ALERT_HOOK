#!/usr/bin/env bash
# Toggle the alert hook's sound playback on/off.
# State persists in alert_sound.state read by alert.py.
set -euo pipefail
HOOK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATE_FILE="$HOOK_DIR/alert_sound.state"
case "${1:-}" in
  on)     printf 'on\n'  > "$STATE_FILE"; echo "🔔 Alert sound ON  (state: $STATE_FILE)";;
  off)    printf 'off\n' > "$STATE_FILE"; echo "🔕 Alert sound OFF (state: $STATE_FILE)";;
  status) if [ -f "$STATE_FILE" ]; then cat "$STATE_FILE"; else echo "on (default)"; fi;;
  *)      echo "usage: alert_sound.sh {on|off|status}" >&2; exit 1;;
esac
