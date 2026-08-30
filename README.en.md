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

### 2-5. (Optional) Use it globally instead of copying it into every project ⭐

Steps 2-2 and 2-4 above only apply the hook to **one project**. If copying
`.gemini` and creating `GEMINI.md` for every new project feels tedious, set
it up **once, in your home folder**, and it'll apply to every project
automatically.

Gemini CLI reads settings in this order of precedence: **project settings
(`./.gemini/`) > user settings (`~/.gemini/`) > system defaults**. So if a
project folder has no `.gemini`, your user-level settings apply as-is.

**1) Copy `.gemini` and `GEMINI.md` into your home folder**

macOS / Linux:
```bash
cp -r gemini-cli-alert-hook/.gemini ~/.gemini
cp gemini-cli-alert-hook/GEMINI.md.example ~/GEMINI.md
```

Windows (cmd, replace `YourName` with your actual Windows user name):
```bat
xcopy "gemini-cli-alert-hook\.gemini" "C:\Users\YourName\.gemini" /E /I /H
copy "gemini-cli-alert-hook\GEMINI.md.example" "C:\Users\YourName\GEMINI.md"
```

**2) Change the `command` path in `.gemini/settings.json` to an absolute path (required)**

Since the hook now needs to work no matter which folder you run `gemini`
from, the relative path (`.gemini/hooks/...`) will no longer resolve. You
must change it to an **absolute path**.

macOS / Linux example:
```json
"command": "python3 -u /Users/YourName/.gemini/hooks/alert/scripts/alert.py"
```

Windows example (backslashes must be doubled (`\\`) inside JSON strings):
```json
"command": "python -u \"C:\\Users\\YourName\\.gemini\\hooks\\alert\\scripts\\alert.py\""
```

Do the same for the `command` in the `Notification` hook.

**3) Verify**

Test from a brand-new folder that has no `.gemini` of its own. If you hear
the sound, the global setup worked.
```bash
cd ~/Desktop   # or any new folder
gemini
```

> 💡 If a project already has its own `.gemini` copied in, you can leave it
> as-is — project settings take precedence over user settings, so there's
> no conflict. Delete it if you no longer need it there.

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
| **Delay of several seconds (up to ~20s) between the bell and the TTS voice** | See the [Playback Delay FAQ](#bell--tts-playback-delay-faq) below |

Check the debug log:
```bash
cat .gemini/hooks/alert/scripts/alert_debug.json   # macOS/Linux
type .gemini\hooks\alert\scripts\alert_debug.json  # Windows
```

---

## Changelog

### v1.1 — Major playback delay fix (Windows)

The initial version played mp3 files on Windows by **spawning a new
PowerShell process each time** and polling
`System.Windows.Media.MediaPlayer` for the playback duration. In real-world
use, this turned out to have serious problems:

- `MediaPlayer` opens files asynchronously, so if you poll
  `NaturalDuration` before it's ready, the code fell back to a
  **hardcoded 5-second wait**
- On top of that, starting a new PowerShell process and loading the .NET
  assembly (`Add-Type -AssemblyName presentationCore`) added further
  overhead — in practice, playing a single 1-second bell sound could take
  **over 9 seconds** (worse on machines where antivirus software scans
  every PowerShell invocation)

**v1.1 removes PowerShell entirely** and instead calls Windows' built-in
`winmm.dll` (MCI, Media Control Interface) directly via Python's `ctypes`.
The `play ... wait` command blocks for exactly the real duration of the
file, with no separate process startup cost and no need to guess the
duration.

The bell/notification sound and the TTS generation (an edge-tts network
request) also now run **in parallel**, cutting the perceived delay further.

| | v1.0 (initial) | v1.1 |
|---|---|---|
| Windows playback method | PowerShell + MediaPlayer polling | Direct `winmm.dll` MCI call |
| Playing a 1-second bell file | Up to 9+ seconds | About 1–1.3 seconds |
| Bell playback vs. TTS generation | Sequential | Parallel |

| | v1.1 | v1.3 (Current) |
| ---- | ---- | -------- |
| Windows playback method | `winmm.dll` MCI direct call | `winmm.dll` MCI direct call |
| Ringtone ↔ TTS volume | Cannot be adjusted separately | **Can be adjusted separately** |
| Ringtone volume | Fixed/shared setting | **Separate setting available** |
| TTS volume | Fixed/shared setting | **Separate setting available** |
In previous versions, the ringtone and TTS voice **shared the same volume setting or could not be adjusted separately**, which caused the ringtone to sound relatively louder than the TTS voice.

**In v1.3, the code was modified to allow the ringtone and TTS volume to be adjusted independently.**

This allows users to set the ringtone and TTS voice volume separately according to their environment, reducing the issue where the ringtone could interfere with the TTS voice.


---

## Bell / TTS playback delay FAQ

These are questions that came up while diagnosing the bell-to-TTS delay
issue in real use. If you're seeing similar symptoms, this may help.

**Q. The bell plays instantly, but the TTS voice takes forever after that.**

First figure out whether `edge-tts` itself is slow, or whether playback is
the bottleneck. Time TTS generation alone with:
```bash
python -c "import time; t=time.time(); import asyncio, edge_tts; asyncio.run(edge_tts.Communicate('Hello world', 'en-GB-SoniaNeural', rate='+30%').save('test.mp3')); print(f'Elapsed: {time.time()-t:.2f}s')"
```
1–3 seconds is normal. If it's much slower than that, it's likely a
network/firewall issue. If this is fast but the overall delay is still
large, the problem is in the playback step (see below).

**Q. Nothing shows up in `alert_debug.json`.**

This means the hook itself isn't running at all. Double-check that the
`command` path in `.gemini/settings.json` is correct (especially if you're
using the global/user-level setup — it must be an absolute path, not a
relative one), and confirm the project folder you're testing from is
actually picking up that `.gemini` config.

**Q. `alert_debug.json` shows `bell playback took` 5+ seconds.**

This was a common symptom in the v1.0 (PowerShell + MediaPlayer polling)
version. As explained in the [Changelog](#changelog) above, it was a bug
where the code couldn't read the real playback duration in time and fell
back to a hardcoded 5-second wait. Updating to v1.1 fixes this.

**Q. I use conda (or another virtual environment) — where should I run `pip install edge-tts`?**

Install it into whichever environment is active when you run `gemini`. For
example, if you run `gemini` after `conda activate myenv`:
```bash
conda activate myenv
pip install edge-tts
```
Verify with `python -c "import edge_tts"` in that same environment. If you
install it into a different environment (e.g. your system Python), the
hook may silently fail because `gemini` is calling a different `python`.

**Q. On Windows, `where.exe python` shows a path under `WindowsApps\python.exe`.**

That's not a real Python install — it's a dummy stub (App Execution Alias)
that redirects to the Microsoft Store. Go to Settings → Apps → Advanced app
settings → App execution aliases and turn off `python.exe`, and/or point
the `command` in `.gemini/settings.json` directly at the full path of your
real (or conda) Python.

**Q. Does this delay issue also happen on macOS/Linux?**

The delay bug that was fixed here was specific to the Windows PowerShell
playback path. macOS (`afplay`) and Linux (`mpv`) already just block until
playback naturally finishes, with no polling involved, so this particular
issue doesn't apply there. If you do see delays on those platforms, check
the `TIMING:` lines in `alert_debug.json` first to see whether TTS
generation or playback is the slow step.

---

## License

MIT
