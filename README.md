# Premiere Auto Editor

Adobe Premiere Pro용 UXP 패널 플러그인. 컷 편집, 자막(.srt) 삽입, 선택 클립으로 시퀀스 구성을 자동화합니다.

이 플러그인은 Claude(코딩 어시스턴트)가 사용자의 Premiere Pro 앱을 직접 조작할 수 없기 때문에 만들어졌습니다. 대신 이 패널을 Premiere Pro 안에 로드해서, 패널의 버튼을 눌러 반복 작업을 자동화하는 방식입니다.

## 요구 사항

- Adobe Premiere Pro **24.2 이상** (UXP 플러그인 지원 버전)
- [Adobe UXP Developer Tool](https://developer.adobe.com/creative-cloud/uxp/) (플러그인을 로컬에서 로드/디버그하기 위해 필요)

## 설치 및 로드 방법

1. 이 저장소를 로컬에 클론합니다.
2. UXP Developer Tool을 실행하고, "Add Plugin"으로 이 저장소 폴더(`manifest.json`이 있는 폴더)를 선택합니다.
3. Premiere Pro를 실행한 뒤, UXP Developer Tool에서 해당 플러그인 옆의 **Load** 버튼을 누릅니다.
4. Premiere Pro 메뉴에서 `Window > Extensions (UXP) > Auto Editor` 패널을 엽니다.

코드를 수정한 뒤에는 UXP Developer Tool의 **Reload** 버튼으로 다시 불러올 수 있습니다.

## 기능

| 버튼 | 동작 |
|---|---|
| 선택 클립으로 새 시퀀스 만들기 | Project 패널에서 선택한 클립들로 새 시퀀스를 생성합니다. |
| CUT 마커 구간 잘라내기 | 활성 시퀀스에서 이름이 `CUT`로 시작하는 마커 구간과 겹치는 모든 트랙의 클립을 리플 삭제합니다. |
| .srt 자막 파일 가져오기 | 로컬 `.srt`/`.vtt` 파일을 선택해 프로젝트로 임포트합니다. (타임라인 배치는 수동으로 드래그) |
| 현재 설치된 API 구조 살펴보기 | 설치된 Premiere 버전의 `premierepro` 모듈, `Project`, `Sequence` 객체가 실제로 어떤 메서드를 제공하는지 로그로 출력합니다. |

## 중요: API 안정성에 대한 주의

Premiere Pro의 UXP 스크립팅 API(`premierepro` 모듈)는 비교적 최근에 도입되었고 버전마다 메서드 이름/시그니처가 바뀔 수 있습니다. 이 플러그인의 `js/*.js` 코드는 Adobe 공식 문서와 샘플 코드의 패턴(`project.lockedAccess`, `project.executeTransaction`, `sequence.createRemoveItemAction` 등)을 기반으로 작성했지만, **실제 설치된 Premiere 버전에서 직접 검증되지 않았습니다** (이 코드는 Premiere Pro가 없는 서버 환경에서 작성됨).

버튼을 눌렀을 때 `~is not a function` 같은 오류가 나면:

1. 패널 하단 "현재 설치된 API 구조 살펴보기" 버튼을 눌러 실제 메서드 목록을 확인하세요.
2. 로그에 출력된 이름과 `js/sequence.js`, `js/trim.js`, `js/subtitles.js` 안의 메서드 이름을 비교해서 맞게 고쳐주세요.
3. UXP Developer Tool의 콘솔에서도 동일한 오류/스택트레이스를 볼 수 있습니다.

## CUT 마커 워크플로우

1. 타임라인에서 잘라내고 싶은 구간의 시작-끝에 걸쳐 마커를 만들고, 마커 이름을 `CUT`(또는 `CUT ...`)로 지정합니다.
2. 패널에서 "CUT 마커 구간 잘라내기"를 누르면 해당 구간과 겹치는 모든 비디오/오디오 트랙의 클립이 리플 삭제됩니다.

무음 구간 자동 감지(무음 검출 → 마커 자동 생성)는 아직 포함되어 있지 않습니다. 추후 별도 스크립트(예: ffmpeg 기반 무음 분석)로 마커를 자동 생성하는 기능을 추가할 수 있습니다.

## 자막 워크플로우

현재는 `.srt`/`.vtt` 파일을 프로젝트 패널로 가져오는 것까지만 자동화되어 있습니다. Premiere의 캡션 트랙 API는 버전에 따라 제공 범위가 달라서, 가져온 자막 클립을 시퀀스의 캡션 트랙에 자동 배치하는 기능은 다음 단계로 남겨두었습니다.
