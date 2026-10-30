---
name: alerton
description: Use when the user says "/alerton", "/skillon", "turn on alert", "enable alert sound", "알림 켜줘", "알림 켜", or "alert on". Enables the alert hook audio notifications (bell chime and TTS summary).
---

Run the following command using the available shell or execution tool:

```bash
python .gemini/hooks/alert/scripts/alert_sound.py on
```

> **Note on path:** If running under a global installation, locate `alert_sound.py` under the user's `.gemini` directory (e.g. `~/.gemini/hooks/alert/scripts/alert_sound.py`).

Report the output to the user and confirm that the alert hook sound is now **ENABLED** 🔔.
Audio notifications (bell chime and TTS summary) will now play on task completion and permission requests.
The state persists across sessions until disabled via `/alertoff` (or `/skilloff`).
