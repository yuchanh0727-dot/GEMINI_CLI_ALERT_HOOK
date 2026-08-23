# Gemini CLI Alert Hook

English | [한국어](./README.md)

*Gemini needs you. You need alert.*

A hook that notifies you with **a chime + a spoken (TTS) summary** whenever
Gemini CLI finishes a response or asks for tool permission. Built on top of
Gemini CLI's Hooks system (`AfterAgent`, `Notification`).

> This is also expected to work on **Antigravity CLI** (`agy`), which inherits
> Gemini CLI's Hooks system, but that hasn't been separately verified yet.

## What it does

- When a response finishes → a bell sound + a short spoken summary of what happened
- When a tool permission is requested → a different alert sound + "Permission needed."

So you don't have to keep staring at the terminal — you'll hear when Gemini
CLI is done while you do something else.

## Prerequisites

| Requirement | Check |
|---|---|
| Node.js 18+ | `node --version` |
| Python 3.8+ | `python --version` |
| Gemini CLI | see [Install](#1-install-gemini-cli) below |
| An audio player | macOS: `afplay` (built-in) · Windows: PowerShell (built-in) · Linux: `mpv` (`sudo apt install mpv`) |

---

## 1. Install Gemini CLI

```bash
npm install -g @google/gemini-cli
```

Authenticate after install:

```bash
gemini
```

On first run it'll ask how you want to authenticate. Sign in with a Google
account, or if you're using a paid API key, run `/auth` and choose the
`gemini-api-key` method.

> ⚠️ **Note**: As of June 18, 2026, Gemini CLI no longer serves free
> individual accounts. You'll need a paid API key or an enterprise Gemini
> Code Assist account. If you want a free option, check out the successor
> tool, [Antigravity CLI](https://antigravity.google) (`agy`).

Verify install:

```bash
gemini --version
```

---

## 2. Install this hook

### 2-1. Clone or download

```bash
git clone https://github.com/yuchanh0727-dot/GEMINI_CLI_ALERT_HOOK.git
```

### 2-2. Copy the `.gemini` folder into your project

Copy the `.gemini` folder into the root of whatever project you want this
hook active in (the folder where you normally run `gemini`).

```
your-project/
  .gemini/
    settings.json              # registers the AfterAgent and Notification hooks
    hooks/
      alert/
        scripts/
          alert.py             # plays the sound + TTS
        sounds/
          bell.mp3
          noti.mp3
```

macOS / Linux:
```bash
cp -r gemini-cli-alert-hook/.gemini your-project/
```

Windows (cmd):
```bat
xcopy "gemini-cli-alert-hook\.gemini" "your-project\.gemini" /E /I /H
```

### 2-3. Install the Python dependency

```bash
pip install edge-tts
```

> If you use conda or another virtual environment, install it into
> **whichever environment runs the `gemini` command**. Verify with
> `python -c "import edge_tts"` — it should run with no error.

### 2-4. Add the TTS tag rule to `GEMINI.md`

Add the following to your project's `GEMINI.md` (create it if it doesn't
exist). This makes Gemini always attach a spoken-summary tag to the end of
its responses.

````markdown
### Alert Hook — TTS tag requirement

**Every response MUST end with a `<!-- tts: ... -->` tag** on its own line.
The AfterAgent hook parses this tag to generate a spoken notification. If the
tag is missing, the user hears only a generic "Task completed" bell.

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

A ready-to-use template is also available at
[`GEMINI.md.example`](./GEMINI.md.example).

---

## 3. Verify

Start a new Gemini CLI session inside your project folder:

```bash
cd your-project
gemini
```

If you see a warning like this on startup, the hooks were detected correctly
(it's safe — you configured them yourself):

```
⚠ WARNING: The following project-level hooks have been detected in this workspace:
    - alert-bell-tts
    - alert-permission-noti
```

Send any message. When the response finishes you should hear a bell + spoken
summary, and when a tool permission is requested you should hear a different
chime + "Permission needed."

---

## Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| No sound at all | Check that an audio player (`afplay`/PowerShell/`mpv`) is installed |
| Bell plays but no voice | Check `edge-tts` is installed in the same environment that runs `gemini`. Check `.gemini/hooks/alert/scripts/alert_debug.json` for `TTS_ERROR` (usually a network issue) |
| Always hear "Task completed" | Check the TTS tag rule is actually in `GEMINI.md`, and that `GEMINI.md` is in the project root |
| `python` not recognized | Change the `command` value in `.gemini/settings.json` to `python3` or a full path |
| Hook seems to hang (timeout) | Increase the `timeout` value (milliseconds) in `.gemini/settings.json` |

Check the debug log:
```bash
cat .gemini/hooks/alert/scripts/alert_debug.json   # macOS/Linux
type .gemini\hooks\alert\scripts\alert_debug.json  # Windows
```

---

## License

MIT
