[English](./README.en.md) | 한국어
# Gemini CLI Alert Hook

Gemini CLI가 응답을 끝내거나 도구 권한을 요청할 때 **소리(차임벨) + 음성(TTS) 요약**으로
알려주는 훅입니다. [ClaudeCode-Alert-Hook](https://github.com/sangwonme/ClaudeCode-Alert-Hook)을
Gemini CLI의 Hooks 시스템(`AfterAgent`, `Notification`)에 맞게 이식한 버전입니다.

> Gemini CLI Hooks 시스템을 그대로 계승한 **Antigravity CLI**(`agy`)에서도 대부분 동일하게
> 동작할 것으로 예상되지만, 아직 별도로 검증하지는 않았습니다.

## 무엇을 하나요?

- 응답이 끝나면 → 벨소리 + 응답 내용을 짧게 요약한 영어 음성 안내
- 도구 실행 권한을 요청하면 → 다른 알림음 + "Permission needed." 음성 안내

터미널을 계속 쳐다보지 않아도, 다른 작업을 하다가 Gemini CLI가 끝났는지 소리로 알 수 있습니다.

## 사전 준비물

| 항목 | 확인 방법 |
|---|---|
| Node.js 18+ | `node --version` |
| Python 3.8+ | `python --version` |
| Gemini CLI | 아래 [설치](#1-gemini-cli-설치) 참고 |
| 오디오 재생 도구 | macOS: `afplay`(기본 내장) · Windows: PowerShell(기본 내장) · Linux: `mpv` (`sudo apt install mpv`) |

---

## 1. Gemini CLI 설치

```bash
npm install -g @google/gemini-cli
```

설치 후 인증:

```bash
gemini
```

처음 실행하면 인증 방법을 물어봅니다. Google 계정으로 로그인하거나, 유료 API 키를 쓰신다면
`/auth` 명령어로 `gemini-api-key` 인증 방식을 선택하시면 됩니다.

> ⚠️ **참고**: Gemini CLI는 2026년 6월 18일부터 무료 개인 계정 지원을 종료했습니다. 유료 API 키
> 또는 엔터프라이즈 Gemini Code Assist 계정이 필요합니다. 무료로 쓰고 싶다면 후속 도구인
> [Antigravity CLI](https://antigravity.google)(`agy`)를 확인해보세요.

설치 확인:

```bash
gemini --version
```

---

## 2. 이 훅 설치

### 2-1. 클론 또는 다운로드

```bash
git clone https://github.com/yuchanh0727-dot/gemini-cli-alert-hook.git
```

### 2-2. `.gemini` 폴더를 프로젝트에 복사

이 훅을 적용하고 싶은 프로젝트 루트(평소 `gemini` 명령어를 실행하는 폴더)에
`.gemini` 폴더를 복사하세요.

```
your-project/
  .gemini/
    settings.json              # AfterAgent, Notification 훅 등록
    hooks/
      alert/
        scripts/
          alert.py             # 소리 + TTS 재생 스크립트
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

### 2-3. Python 의존성 설치

```bash
pip install edge-tts
```

> conda 등 가상환경을 쓰신다면, **`gemini` 명령어를 실행하는 그 환경**에 설치해야 합니다.
> `python -c "import edge_tts"`가 에러 없이 통과하는지로 확인하세요.

### 2-4. `GEMINI.md`에 TTS 태그 규칙 추가

프로젝트 루트의 `GEMINI.md`(없으면 새로 생성)에 아래 내용을 추가하세요. Gemini가 응답 끝에
음성으로 읽을 요약을 항상 붙이도록 하는 규칙입니다.

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

바로 쓸 수 있는 템플릿이 [`GEMINI.md.example`](./GEMINI.md.example)에 있습니다.

---

## 3. 확인

프로젝트 폴더에서 새 Gemini CLI 세션을 시작하세요:

```bash
cd your-project
gemini
```

시작 시 다음과 같은 경고가 뜨면 훅이 정상적으로 인식된 것입니다 (직접 설정한 훅이므로
안전합니다):

```
⚠ WARNING: The following project-level hooks have been detected in this workspace:
    - alert-bell-tts
    - alert-permission-noti
```

아무 메시지나 보내보세요. 응답이 끝나면 벨소리 + 음성 요약이, 도구 권한을 요청하면
다른 차임벨 + "Permission needed."가 들려야 합니다.

---

## 문제 해결

| 증상 | 원인 / 해결 |
|---|---|
| 소리가 전혀 안 남 | 오디오 재생 도구(`afplay`/PowerShell/`mpv`) 설치 여부 확인 |
| 벨은 울리는데 음성이 안 나옴 | `edge-tts`가 `gemini`를 실행하는 환경에 설치됐는지 확인. `.gemini/hooks/alert/scripts/alert_debug.json`에서 `TTS_ERROR` 확인 (대개 네트워크 문제) |
| 항상 "Task completed"만 들림 | `GEMINI.md`에 TTS 태그 규칙이 제대로 들어갔는지, 프로젝트 루트에 위치하는지 확인 |
| `python`이 인식 안 됨 | `.gemini/settings.json`의 `command` 값을 `python3` 또는 파이썬 전체 경로로 수정 |
| 훅이 멈춘 것처럼 느림 (timeout) | `.gemini/settings.json`의 `timeout`(밀리초) 값을 늘리기 |

디버그 로그 확인:
```bash
cat .gemini/hooks/alert/scripts/alert_debug.json   # macOS/Linux
type .gemini\hooks\alert\scripts\alert_debug.json  # Windows
```

---

## 훅 이벤트 매핑 (원본 Claude Code 버전 대비)

| Claude Code | Gemini CLI |
|---|---|
| `Stop` (응답 완료) | `AfterAgent` |
| `PermissionRequest` | `Notification` (matcher: `ToolPermission`) |
| stdin의 `last_assistant_message` | stdin의 `prompt_response` |

## 출처

[ClaudeCode-Alert-Hook](https://github.com/sangwonme/ClaudeCode-Alert-Hook)의 아이디어와
사운드 자산을 기반으로 Gemini CLI용으로 이식했습니다.

## License

MIT
