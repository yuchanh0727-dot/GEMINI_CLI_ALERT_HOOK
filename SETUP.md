# Gemini CLI Alert Hook — Setup Guide

Instructions for AI Agents (Gemini CLI, Antigravity CLI) and users to automatically or manually set up this hook.

When a user asks:
```
Setup this hook: https://github.com/yuchanh0727-dot/GEMINI_CLI_ALERT_HOOK.git
```
Follow the steps below to complete the setup.

---

## 1. Install Dependencies

Install `edge-tts` in the active Python environment:

```bash
pip install -r requirements.txt
```
*(or `pip install edge-tts`)*

Verify that Python and edge-tts are working:
```bash
python -c "import edge_tts; print('edge-tts ok')"
```

---

## 2. Determine Installation Scope

Decide where to install the hook:
- **Global Installation (Recommended):**
  - Works across all workspaces and projects.
  - Target directory: `~/.gemini/` (Windows: `%USERPROFILE%\.gemini`, macOS/Linux: `~/.gemini`)
  - Target rules file: `~/.gemini/GEMINI.md`
- **Workspace/Local Installation:**
  - Works only for the current project.
  - Target directory: `<workspace>/.gemini/`
  - Target rules file: `<workspace>/GEMINI.md`

*Unless the user specifies workspace-only, Global Installation is recommended.*

---

## 3. Copy Hook and Skill Files

Copy the `.gemini/` folder from this repository into `<target_dir>/.gemini/`:

```
<target_dir>/
  .gemini/
    hooks/
      alert/
        scripts/
          alert.py             # Main notification script
          alert_sound.py       # Cross-platform sound on/off toggle script
          alert_sound.sh       # Bash sound on/off toggle script
          alert_voice.py       # Cross-platform TTS voice picker / sample script
          alert_voice.sh       # Bash TTS voice picker / sample script
        sounds/
          bell.mp3             # Task completion chime
          noti.mp3             # Permission request chime
    skills/
      alerton/
        SKILL.md               # /alerton command to unmute
      alertoff/
        SKILL.md               # /alertoff command to mute
```

---

## 4. Register Hooks in `settings.json`

Merge the following hook configuration into `<target_dir>/.gemini/settings.json` (create the file if it does not exist):

```json
{
  "hooks": {
    "AfterAgent": [
      {
        "hooks": [
          {
            "type": "command",
            "name": "alert-bell-tts",
            "description": "Plays a chime and speaks a summary when Gemini finishes responding.",
            "command": "python -u <HOOK_PATH>/alert.py",
            "timeout": 30000
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "ToolPermission",
        "hooks": [
          {
            "type": "command",
            "name": "alert-permission-noti",
            "description": "Plays a chime and says 'Permission needed.' when Gemini asks for tool permission.",
            "command": "python -u <HOOK_PATH>/alert.py --message \"Permission needed.\" --sound noti",
            "timeout": 15000
          }
        ]
      }
    ]
  }
}
```

> **Note on `<HOOK_PATH>`:**
> - For **Workspace install**: Use relative path `.gemini/hooks/alert/scripts/alert.py`
> - For **Global install**: Use the absolute path (e.g., `C:/Users/username/.gemini/hooks/alert/scripts/alert.py` or `/home/username/.gemini/hooks/alert/scripts/alert.py`)
>
> **Windows PowerShell Quote Warning:**
> Gemini CLI runs hook commands through PowerShell. Do NOT wrap the entire command in double quotes unless prefixed with `& `.

---

## 5. Add the TTS Tag Rule to `GEMINI.md`

Add the following rule to `GEMINI.md` (either workspace `./GEMINI.md` or global `~/.gemini/GEMINI.md`):

````markdown
### Alert Hook — TTS tag requirement

**Every response MUST end with a `<!-- tts: ... -->` tag** on its own line. The AfterAgent hook parses this tag to generate a spoken notification. If the tag is missing, the user hears only a generic "Task completed" bell.

Format:
```
<!-- tts: {"m": "Done. Short summary of what was done."} -->
```

Rules:
- `m` value must be a single English sentence, max 15 words.
- Start with "Done." followed by a brief summary.
- NEVER include file paths, URLs, code snippets, or slashes.
- Be conversational and natural — this is read aloud.
- Even for simple Q&A or conversational replies, include the tag.
````

---

## 6. Verify

Run a quick test to verify the audio and TTS:
```bash
python <HOOK_PATH>/alert.py --message "Alert hook setup complete." --sound noti
```
You should hear the notification chime followed by the spoken words: *"Alert hook setup complete."*

---

## 7. Mute & Unmute Commands (Skills)

Users can toggle sound output anytime using slash commands or conversational prompts:

| Action | Slash Command | Prompt Example |
|---|---|---|
| Unmute (Sound ON) | `/alerton` | "alert on", "turn on alert sound", "알림 켜줘" |
| Mute (Sound OFF) | `/alertoff` | "alert off", "mute alert", "알림 꺼줘" |

The state is preserved in `alert_sound.state` and persists across sessions.
