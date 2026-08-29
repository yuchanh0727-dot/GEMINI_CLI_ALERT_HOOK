# Gemini CLI Alert Hook

[English](./README.en.md) | 한국어

*Gemini needs you. You need alert.*

Gemini CLI가 응답을 끝내거나 도구 권한을 요청할 때 **소리(차임벨) + 음성(TTS) 요약**으로
알려주는 훅입니다. Gemini CLI의 Hooks 시스템(`AfterAgent`, `Notification`)을 이용해 만들었습니다.

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
git clone https://github.com/yuchanh0727-dot/GEMINI_CLI_ALERT_HOOK.git
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

### 2-5. (선택) 프로젝트마다 복사하지 않고 전역(글로벌)으로 쓰기 ⭐

위 2-2, 2-4는 **프로젝트 하나에만** 적용하는 방법입니다. 매번 새 프로젝트마다
`.gemini`를 복사하고 `GEMINI.md`를 새로 만들기 번거롭다면, **사용자 홈 폴더**에 딱
한 번만 설정해두면 모든 프로젝트에서 자동으로 적용됩니다.

Gemini CLI는 설정을 아래 우선순위로 읽습니다: **프로젝트 설정(`./.gemini/`) >
사용자 전역 설정(`~/.gemini/`) > 시스템 기본값**. 즉 프로젝트 폴더에 `.gemini`가
없으면 사용자 전역 설정이 그대로 적용됩니다.

**1) `.gemini` 폴더와 `GEMINI.md`를 홈 폴더로 복사**

macOS / Linux:
```bash
cp -r gemini-cli-alert-hook/.gemini ~/.gemini
cp gemini-cli-alert-hook/GEMINI.md.example ~/GEMINI.md
```

Windows (cmd, `홍길동`은 본인 사용자 계정명으로 교체):
```bat
xcopy "gemini-cli-alert-hook\.gemini" "C:\Users\홍길동\.gemini" /E /I /H
copy "gemini-cli-alert-hook\GEMINI.md.example" "C:\Users\홍길동\GEMINI.md"
```

**2) `.gemini/settings.json`의 `command` 경로를 절대경로로 수정 (필수)**

전역으로 쓰면 `gemini`를 어느 폴더에서 실행하든 훅이 동작해야 하므로, 상대경로
(`.gemini/hooks/...`)는 더 이상 작동하지 않습니다. 반드시 **절대경로**로 바꿔야
합니다.

macOS / Linux 예시:
```json
"command": "python3 -u /Users/홍길동/.gemini/hooks/alert/scripts/alert.py"
```

Windows 예시 (경로 구분자 `\`는 JSON에서 `\\`로 두 번 씀):
```json
"command": "python -u \"C:\\Users\\홍길동\\.gemini\\hooks\\alert\\scripts\\alert.py\""
```

`Notification` 훅 쪽의 `command`도 동일하게 절대경로로 바꿔주세요.

**3) 확인**

`.gemini`가 전혀 없는 새 폴더에서 테스트해보세요. 소리가 들리면 전역 설정 성공입니다.
```bash
cd ~/Desktop   # 또는 아무 새 폴더
gemini
```

> 💡 각 프로젝트에 이미 복사해둔 `.gemini`가 있다면 그대로 둬도 됩니다 — 프로젝트
> 설정이 전역 설정보다 우선 적용되니 충돌하지 않습니다. 필요 없어졌다면 지워도
> 됩니다.

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
| **벨소리와 TTS 음성 사이 딜레이가 몇 초~20초씩 김** | 아래 [벨소리 재생 딜레이 관련 FAQ](#벨소리--tts-재생-딜레이-관련-faq) 참고 |

디버그 로그 확인:
```bash
cat .gemini/hooks/alert/scripts/alert_debug.json   # macOS/Linux
type .gemini\hooks\alert\scripts\alert_debug.json  # Windows
```

---

## 개선 내역

### v1.1 — 재생 딜레이 대폭 개선 (Windows)

초기 버전은 Windows에서 mp3를 재생할 때마다 **PowerShell 프로세스를 새로 띄우고
`System.Windows.Media.MediaPlayer`로 재생 길이를 폴링**하는 방식이었는데, 실제 사용 중
아래 문제들이 확인됐습니다.

- `MediaPlayer`가 파일을 비동기로 열기 때문에, 재생 길이(`NaturalDuration`)를 아직
  읽지 못한 상태에서 폴링하면 **무조건 5초를 강제로 대기**하는 폴백 코드로 빠짐
- 여기에 PowerShell 프로세스 시작 + `Add-Type -AssemblyName presentationCore`
  (.NET 어셈블리 로딩) 오버헤드까지 더해져서, 1초짜리 벨소리 하나 재생하는 데
  **9초 이상** 걸리는 경우가 실제로 있었음 (백신 프로그램이 매번 PowerShell 실행을
  검사하는 환경에서는 더 심함)

**v1.1에서는 PowerShell을 아예 쓰지 않고**, Windows에 내장된 `winmm.dll`(MCI, Media
Control Interface)을 파이썬 `ctypes`로 직접 호출하도록 바꿨습니다. `play ... wait`
명령이 실제 재생 길이만큼 정확히 블로킹되기 때문에, 별도 프로세스 시작 비용이나
길이 추측 로직 없이 훨씬 빠르고 정확하게 재생됩니다.

또한 벨/알림음 재생과 TTS 음성 생성(edge-tts, 네트워크 요청)을 **동시에 진행**하도록
바꿔서, 체감 딜레이를 한 번 더 줄였습니다.

| | v1.0 (초기) | v1.1 (현재) |
|---|---|---|
| Windows 재생 방식 | PowerShell + MediaPlayer 폴링 | `winmm.dll` MCI 직접 호출 |
| 벨소리(1초 파일) 재생 시간 | 최대 9초 이상 | 약 1~1.3초 |
| 벨소리 재생 ↔ TTS 생성 | 순차 진행 | 병렬 진행 |

---

## 벨소리 · TTS 재생 딜레이 관련 FAQ

이 훅을 실제로 쓰면서 벨소리와 TTS 음성 사이 딜레이 문제를 진단하는 과정에서 나온
질문들을 정리했습니다. 비슷한 증상을 겪으신다면 참고하세요.

**Q. 벨소리는 바로 나는데 TTS 음성까지 너무 오래 걸려요.**

먼저 `edge-tts` 자체가 느린 건지, 재생 단계가 느린 건지 구분해야 합니다. 아래 명령어로
edge-tts 생성 시간만 단독으로 측정해보세요:
```bash
python -c "import time; t=time.time(); import asyncio, edge_tts; asyncio.run(edge_tts.Communicate('Hello world', 'en-GB-SoniaNeural', rate='+30%').save('test.mp3')); print(f'Elapsed: {time.time()-t:.2f}s')"
```
보통 1~3초면 정상입니다. 이보다 훨씬 오래 걸리면 네트워크/방화벽 문제, 정상 범위인데도
전체 딜레이가 크다면 재생 단계(아래 항목) 문제입니다.

**Q. `alert_debug.json`에 아무것도 안 남아요.**

훅 자체가 실행되지 않고 있다는 뜻입니다. `.gemini/settings.json`의 `command` 경로가
정확한지 (특히 사용자 전역 설정으로 쓸 경우 상대경로가 아니라 절대경로여야 함),
그리고 지금 프로젝트 폴더가 실제로 그 `.gemini` 설정을 참조하고 있는 폴더가 맞는지
확인하세요.

**Q. `alert_debug.json`을 열어보니 `bell playback took`이 5초 이상 찍혀요.**

v1.0(PowerShell + MediaPlayer 폴링) 버전에서 흔했던 증상입니다. 위
[개선 내역](#개선-내역)에서 설명한 것처럼, 재생 길이를 못 읽어서 강제 5초 대기
폴백으로 빠지는 버그였습니다. v1.1로 업데이트하면 해결됩니다.

**Q. conda 같은 가상환경을 쓰는데, `pip install edge-tts`를 어디에 해야 하나요?**

`gemini` 명령어를 실행할 때 활성화되어 있는 그 환경에 설치해야 합니다. 예를 들어
`conda activate myenv` 상태에서 `gemini`를 쓰신다면:
```bash
conda activate myenv
pip install edge-tts
```
`python -c "import edge_tts"`가 그 환경에서 에러 없이 통과하는지로 확인하세요. 다른
환경(예: 시스템 기본 Python)에 설치해두면, `gemini` 실행 시 참조하는 파이썬이 달라서
훅이 조용히 실패할 수 있습니다.

**Q. Windows에서 `where.exe python`을 쳤더니 `WindowsApps\python.exe`가 나와요.**

이건 진짜 Python이 아니라 Microsoft Store로 안내하는 더미 실행 파일(App Execution
Alias)입니다. 설정 → 앱 → 고급 앱 설정 → 앱 실행 별칭에서 `python.exe`를 꺼두고,
`.gemini/settings.json`의 `command`에 실제 Python(또는 conda 환경 Python)의 전체
경로를 직접 지정하는 걸 권장합니다.

**Q. macOS/Linux에서도 이 딜레이 문제가 있나요?**

이번에 확인된 딜레이 문제는 Windows의 PowerShell 재생 방식에 국한된 버그였습니다.
macOS(`afplay`), Linux(`mpv`)는 처음부터 별도 프로세스 폴링 없이 재생이 끝날 때까지
단순히 블로킹하는 방식이라 이 문제와는 무관합니다. 다만 딜레이를 겪으신다면
`alert_debug.json`의 `TIMING:` 로그로 어느 단계(TTS 생성 vs 재생)가 느린지 먼저
확인해보세요.

---

## License

MIT
