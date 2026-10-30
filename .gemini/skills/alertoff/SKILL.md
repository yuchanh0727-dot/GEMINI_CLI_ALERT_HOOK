---
name: alertoff
description: Use when the user says "/alertoff", "/skilloff", "turn off alert", "mute alert", "silence alert", "알림 꺼줘", "알림 꺼", or "alert off". Disables the alert hook audio notifications so no chime or TTS plays.
---

Run the following command using the available shell or execution tool:

```bash
python .gemini/hooks/alert/scripts/alert_sound.py off
```

> **Note on path:** If running under a global installation, locate `alert_sound.py` under the user's `.gemini` directory (e.g. `~/.gemini/hooks/alert/scripts/alert_sound.py`).

Report the output to the user and confirm that the alert hook sound is now **DISABLED / MUTED** 🔕.
Both bell chime and TTS speech are suppressed on task completion and permission requests.
The state persists across sessions until re-enabled via `/alerton` (or `/skillon`).
