# Premiere Auto Editor

Adobe Premiere Pro 안에서 여는 AI 자동 편집 패널. 원본 영상을 넣고 지시를 적으면:

1. **로컬 Python 엔진**이 ffmpeg + faster-whisper로 영상을 분석하고,
2. **Claude(Anthropic API)**가 대본과 지시를 보고 어디를 잘라낼지 / 자막을 어떻게 다듬을지 판단하고,
3. 결과를 **FCP7 XML 시퀀스 + SRT 자막**으로 만들어서 Premiere 프로젝트로 자동 임포트합니다.

Premiere를 실시간으로 조작하는 대신, Premiere가 오래전부터 안정적으로 지원하는 "XML 시퀀스 가져오기" 기능을 이용하는 방식이라 UXP 편집 API의 버전별 차이에 덜 취약합니다.

## 전체 구조

```
premiere-auto-editor/
├── manifest.json, index.html, css/, js/   ← Premiere UXP 패널 (Premiere 안에서 로드)
├── server/                                 ← 로컬 Node.js 서버 (패널의 요청을 받아 엔진 실행)
│   └── server.js, package.json, .env
└── engine/                                 ← 로컬 Python 엔진 (실제 분석/편집 계획/XML 생성)
    └── main.py, transcribe.py, claude_plan.py, xml_writer.py, ...
```

패널(Premiere 안) → HTTP → Node 서버(로컬) → Python 엔진 실행 → 결과 XML/SRT → 패널이 다시 Premiere로 임포트, 순서로 동작합니다.

## 요구 사항 (Windows)

- Adobe Premiere Pro **24.2 이상**
- [Adobe UXP Developer Tool](https://developer.adobe.com/creative-cloud/uxp/)
- [Node.js](https://nodejs.org/) 18 이상
- [Python](https://www.python.org/downloads/windows/) 3.10~3.12, 설치 시 "Add python.exe to PATH" 체크
- [ffmpeg for Windows](https://www.gyan.dev/ffmpeg/builds/) 다운로드 후 PATH에 추가 (`ffmpeg`, `ffprobe` 명령이 아무 폴더에서나 실행되어야 함)
- Anthropic API 키 ([console.anthropic.com](https://console.anthropic.com)에서 발급)

Whisper 음성 인식은 Apple Silicon 전용인 `mlx-whisper`가 아니라, Windows/GPU 없는 환경에서도 동작하는 `faster-whisper`를 사용합니다. GPU(NVIDIA + CUDA)가 있으면 훨씬 빠르고, 없어도 CPU로 동작합니다 (느림).

## 설치

### 1. Python 엔진

```powershell
cd engine
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Node 서버

```powershell
cd server
npm install
copy .env.example .env
```

`server/.env` 파일을 열어 `ANTHROPIC_API_KEY`를 채워주세요. Python 가상환경을 쓴다면 `PYTHON_BIN`을 가상환경의 `python.exe` 전체 경로로 지정하세요 (예: `PYTHON_BIN=C:\...\engine\venv\Scripts\python.exe`).

### 3. UXP 패널 로드

1. UXP Developer Tool에서 "Add Plugin" → 이 저장소 폴더(`manifest.json`이 있는 곳) 선택
2. Premiere Pro 실행 후 UXP Developer Tool에서 **Load**
3. Premiere Pro `Window > Extensions (UXP) > Auto Editor` 패널 열기

## 사용 방법

1. 매번 작업 전에 `server` 폴더에서 `npm start` (또는 `node server.js`)로 로컬 서버를 켭니다.
2. Premiere의 Auto Editor 패널에서 "원본 영상 파일 선택"으로 편집할 원본 클립(mp4/mov 등)을 고릅니다.
3. 지시 문장을 입력합니다. 예: `말 더듬는 부분과 긴 침묵을 잘라내고, 자막은 짧게 끊어서 다듬어줘`
4. "AI 자동 편집 실행"을 누릅니다. 진행 상황은 패널 하단 로그에 실시간으로 표시됩니다 (영상 길이에 따라 수 분 소요).
5. 완료되면 새 시퀀스가 자동으로 프로젝트에 임포트됩니다. Project 패널에서 확인 후 필요하면 자막(.srt)을 별도로 임포트해 캡션 트랙에 배치하세요.

## 기타 기능 (수동)

| 버튼 | 동작 |
|---|---|
| 선택 클립으로 새 시퀀스 만들기 | Project 패널에서 선택한 클립들로 새 시퀀스를 생성합니다. |
| CUT 마커 구간 잘라내기 | 시퀀스에 직접 `CUT` 마커를 찍어두고 수동으로 리플 삭제할 때 사용합니다 (AI 자동 편집과는 별개의 수동 도구). |
| .srt 자막 파일 가져오기 | 로컬 `.srt`/`.vtt` 파일을 프로젝트로 임포트합니다. |
| 현재 설치된 API 구조 살펴보기 | 설치된 Premiere 버전의 `premierepro` 모듈 실제 메서드 목록을 로그로 출력하는 디버그 도구. |

## 알려진 한계 / 검증 필요 사항

이 프로젝트는 실제 Premiere Pro 환경 없이 작성되었습니다. 특히 아래 항목은 **직접 테스트하며 조정이 필요**할 가능성이 높습니다:

- **FCP7 XML 스키마**: `engine/xml_writer.py`가 생성하는 xmeml v5 구조는 잘 알려진 패턴을 따랐지만, Premiere 버전에 따라 세부 태그 순서/요구 필드가 다를 수 있습니다. 임포트 시 오류가 나면 오류 메시지를 알려주시면 XML 구조를 수정하겠습니다. 우선 짧은 샘플 영상(1분 이내)으로 테스트해보세요.
- **오디오/비디오 링크**: 생성된 XML은 V1(비디오)과 A1(오디오)에 같은 구간을 각각 클립으로 넣습니다. 임포트 후 두 트랙이 어긋나 보이면 두 클립을 선택해 우클릭 → Link로 재연결하세요.
- **faster-whisper 모델 크기**: 기본값은 `medium`입니다. 속도가 너무 느리면 `engine/main.py` 실행 시 `--whisper-model small` 등으로 낮출 수 있습니다 (Node 서버를 거치지 않고 직접 `python main.py ...`로 실행할 때 옵션 전달 가능; 서버 경유 시에는 `server/server.js`의 spawn 인자에 옵션을 추가해주세요).
- **UXP `premierepro` 모듈 API**: `js/premiere.js`, `js/sequence.js`, `js/trim.js`의 메서드 이름은 버전마다 다를 수 있습니다. 오류가 나면 "현재 설치된 API 구조 살펴보기" 버튼으로 실제 메서드명을 확인하세요.

## 로드맵

- BGM 자동 생성/삽입 (음악 생성 API 연동 — 아직 미구현)
- 오디오 러프니스 정규화(loudnorm)
- 자막 스타일(폰트/색상/위치) 자동 적용
