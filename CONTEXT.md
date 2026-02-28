# 자기 진화 — 완전 컨텍스트 문서

> 이 파일 하나에 새 레포를 시작하기 위한 모든 맥락이 담겨 있다.
> 대회 공고 -> 기술 레퍼런스 -> 콘셉트 결정 과정 -> 확정 설계 순서로 읽는다.
> 작성일: 2026-02-28

---

## 목차

1. [대회 공고 원문](#1-대회-공고-원문)
2. [심사 기준 분석](#2-심사-기준-분석)
3. [트랙 1 분석](#3-트랙-1-분석)
4. [과거 해커톤 수상 패턴](#4-과거-해커톤-수상-패턴)
5. [핵심 기술 레퍼런스](#5-핵심-기술-레퍼런스)
6. [콘셉트 결정 과정](#6-콘셉트-결정-과정)
7. [확정 콘셉트: 자기 진화](#7-확정-콘셉트-자기-진화)
8. [경험 설계](#8-경험-설계)
9. [전체 기술 아키텍처](#9-전체-기술-아키텍처)
10. [Gemini 시스템 프롬프트 (전문)](#10-gemini-시스템-프롬프트-전문)
11. [구현 로드맵](#11-구현-로드맵)
12. [레퍼런스 링크](#12-레퍼런스-링크)

---

## 1. 대회 공고 원문

**대회명**: Gemini 3 서울 해커톤 2026

### 트랙 1: 엔터테인먼트 분야의 Gemini

> 한국, 특히 서울은 엔터테인먼트 분야의 글로벌 강국입니다.
> Google의 AI 제품을 활용하여 음악, TV, 영화, 게임 전반에 걸쳐
> 혁신적인 경험을 어떻게 만들 수 있을까요?

### 심사 기준

| 기준 | 가중치 | 설명 |
|------|--------|------|
| **데모** | **50%** | 팀이 아이디어를 얼마나 잘 구현했나요? 작동하나요? |
| **임팩트** | 25% | 프로젝트의 장기적인 성공, 성장 및 영향 가능성. 유용하며 누구에게 유용한가? |
| **창의성** | 15% | 프로젝트의 개념이 혁신적인가? 데모가 독창적인가? |
| **피치** | 10% | 팀이 프로젝트를 얼마나 효과적으로 발표하나요? |

---

## 2. 심사 기준 분석

### 데모가 절반이다 (50%)

- "작동하나요?"가 심사 기준에 명시적으로 포함됨
- **반쯤 만든 거창한 기능 10개 < 완벽하게 돌아가는 핵심 기능 2-3개**
- 라이브 데모에서 깨지면 치명적 -> 안정성 우선
- end-to-end로 작동하는 플로우가 필수

### 구글 기술 활용 판단

- 구글 기술은 **필수 전제**이지 가산점이 아님
- Gemini API를 많이 쓰는 것 자체는 점수가 아님
- 기술 나열보다 **그 기술로 만든 결과물의 완성도와 유용성**이 점수를 좌우

### 기획 체크리스트

- [ ] **작동하는 데모** -- 핵심 유저 플로우 1개를 라이브로 완벽히 시연
- [ ] **명확한 타겟** -- "누구를 위한 것인가"에 한 문장으로 답할 수 있어야 함
- [ ] **구글 기술이 핵심** -- Gemini가 장식이 아닌 핵심 가치를 만드는 구조
- [ ] **차별화 포인트** -- "다른 팀은 안 할 것 같은" 한 가지
- [ ] **확장 스토리** -- "이걸 계속 키우면 이렇게 된다"는 비전

---

## 3. 트랙 1 분석

### 핵심 키워드

- 음악, TV, 영화, 게임
- 한국/서울 = 글로벌 엔터테인먼트 강국
- "혁신적인 경험" (경험을 강조)

### 이 트랙의 위험 요소

- **경쟁이 가장 치열할 가능성** -- "AI로 음악/게임 만들기"는 이미 레드오션
- 임팩트(25%) 스코어에서 "유용성" 주장이 어려울 수 있음
- 차별화 압박: 구현 방식에서 차별화 필요

### 트랙 1에서 이기는 방법

- 데모: 시각/청각적 임팩트 극대화. 3분 내에 하나의 경험을 완결
- 임팩트: 실제로 페인 포인트를 푸는 명확한 타겟 + 확장 스토리
- 창의성: "이건 처음 본다"는 반응을 끌어낼 한 가지가 필요
- 피치: 엔터테인먼트 트랙은 데모 자체가 피치

### Conductr (Creative Exploration Award 수상작) 비교

수상 레퍼런스:

| 항목 | Conductr (수상) | 자기 진화 (우리) |
|------|----------------|----------------|
| 핵심 개념 | MIDI -> Claude가 AI 밴드 지휘 | 생명체 자율 진화 + 방문자 개입 |
| 반응 속도 | 15ms (C/WASM) | <50ms (Tolvera GPU) |
| 기억 | 없음 | Physarum + IML (두 층위) |
| "생명" | 없음 (도구) | 있음 (에이전트에 자체 역학) |
| 차별화 | 전문가 대상 | 누구나 터치로 |

---

## 4. 과거 해커톤 수상 패턴

35개 해커톤, 34개 프로젝트 분석 결과 (2026-02-25 조사):

### 8가지 수상 패턴

- P1 (즉각적 가시성): 멀티모달 + 실시간 시각화가 데모 임팩트 극대화
- P2 (명확한 페인 포인트): "이 문제는 실제로 존재한다"를 심사위원이 즉각 공감
- P4 (기술의 새로운 조합): 기존에 없던 방식으로 두 API를 결합
- P5 (협업 경험): 개인이 아닌 다수가 참여하는 경험
- P6 (완성도): 폴리시된 UI + 안정적인 데모
- P7 (창발적 행동): AI가 예상치 못한 방식으로 반응
- P8 (Google API 극한 활용): Google API를 파이프라인 핵심으로 사용
- P9 (이야기가 있는 기술): "왜 이 기술이 필요한가"의 서사

### 우리 프로젝트의 패턴 해당도

- P1 [O]: Tolvera 실시간 시각화 + Lyria 음악
- P4 [O]: VLA 방식으로 Gemini가 두 시스템 동시 제어
- P7 [O]: Physarum + IML 창발적 행동
- P8 [O]: Lyria + Gemini Live 동시 활용

---

## 5. 핵심 기술 레퍼런스

### 5.1 Lyria 3 RealTime

**개요**: Google DeepMind 개발 음악 생성 AI. 2026년 2월 공개.

**핵심 스펙**
```
엔드포인트: wss://generativelanguage.googleapis.com/ws/...
모델: models/lyria-realtime-exp
출력: 48kHz stereo 16-bit PCM, 2초 청크
세션 제한: 10분 자동 종료
언어: 한국어 포함 8개 언어 지원
```

**Python API**
```python
from google.generativeai.types import LiveMusicGenerationConfig, WeightedPrompt

# 프롬프트 설정
prompts = [
    WeightedPrompt(text="Ethereal Ambience", weight=1.0),
]

# 수치 파라미터
config = LiveMusicGenerationConfig(
    density=0.2,      # 0.0~1.0 (음악 밀도, 음표 빈도)
    brightness=0.3,   # 0.0~1.0 (음색 밝기, 고음역 비중)
    temperature=1.1,  # 다양성 (기본값)
    guidance=4.0,     # 0~6 (프롬프트 준수도, 기본값)
    mute_bass=False,
    mute_drums=False,
)

# 세션 중 프롬프트 변경
session.set_weighted_prompts(prompts)
session.set_live_music_generation_config(config)
```

**핵심 제약사항**
- BPM 변경 -> `reset_context()` 필요 (하드컷 발생) -> **BPM 매핑 제외**
- 빈 프롬프트 불가 -> 최소 1개 WeightedPrompt 항상 유지
- 10분 세션 자동 종료 -> 재연결 로직 필수

**WeightedPrompts 가중치 의미**
```
weight 1.0     = 주도적 음악 스타일
weight 0.5~0.8 = 보조적 색채 추가
weight 1.2~1.5 = 강력한 방향 전환 (주의: 급격한 변화 가능)
max 3개 프롬프트/사이클, weight=0 불가
```

**공식 레퍼런스**
- https://deepmind.google/models/lyria/lyria-realtime/
- https://deepmind.google/models/lyria/

---

### 5.2 Tolvera + IML (anguilla kNN)

**개요**: 아이슬란드 Intelligent Instruments Lab의 Jack Armitage 개발.
Python 라이브러리. GPU 가속 인공 생명 시뮬레이션 + IML 내장.
"Tolvera" = 아이슬란드어 kenning, tolvera(컴퓨터) + vera(존재) = "숫자 존재"

**설치**
```bash
pip install tolvera
# macOS: export KMP_DUPLICATE_LIB_OK=TRUE
# Intel Mac 미지원 (anguilla FAISS 의존성)
```

**핵심 아키텍처**
```
Tolvera
+-- Particles      # GPU 가속 파티클 시스템
+-- Boids          # Craig Reynolds 플로킹 (분리/정렬/응집)
+-- Physarum       # 점균류(Physarum polycephalum) 화학주성 시뮬레이션
+-- Pixels (px)    # 렌더링 버퍼
+-- State (s)      # 공유 상태 관리
+-- OSC            # Open Sound Control (iipyper)
+-- IML            # Interactive Machine Learning (anguilla kNN)
+-- GGUI           # GPU 가속 GUI (Taichi GGUI)
```

**slime_flock 패턴 (핵심)**
```python
from tolvera import Tolvera

tv = Tolvera(x=1920, y=1080)

# Physarum + Boids 합성: Boids 이동이 슬라임 트레일로 기록됨
@tv.render
def _():
    tv.slime(tv.particles)  # Physarum
    tv.flock(tv.particles)  # Boids
    return tv.px
```

**확정 비주얼 설정**
```python
# 시각 품질 확정값 (API 조사 결과)
particles  = 4096      # 최소. 기본 1024은 시각 밀도 부족
evaporate  = 0.97      # 기본 0.99는 equilibrium 고착 위험
background = (0,0,0,1) # 검정 배경: 트레일이 발광 효과
# colors: 수동 지정 (랜덤 색상 충돌 가능. 청록/마젠타/노랑/흰색 권장)
```

**IML (tv.iml) -- anguilla kNN-IML 내장**

별도 ML 라이브러리 구현 없이 설정만으로 실시간 학습.

```python
# 입출력 벡터 설계
# 입력 (4D): [touch_x_norm, touch_y_norm, touch_velocity, touch_dwell]
# 출력 A (3D): Boids [separation, alignment, cohesion]
# 출력 B (3D): Physarum [sense_angle, sense_dist, move_dist]
# 4D: 차원의 저주 방지 sweet spot

tv.iml.touch2boids = {
    'size': (4, 3),
    'io': (get_touch_vec, tv.s.flock_s.from_vec),
    'randomise': True,   # 랜덤 초기 쌍 주입 (베이스라인 자율 진화)
    'lag': 0.4,          # 출력 스무딩
}
tv.iml.touch2physarum = {
    'size': (4, 3),
    'io': (get_touch_vec, tv.s.physarum_s.from_vec),
    'randomise': True,
    'lag': 0.5,
}

# 학습 타이밍 (0.5초 간격 + delta 임계치)
if elapsed > 0.5 and touch_delta > 0.05:
    tv.iml.touch2boids.add(touch_vec, current_boids_vec)
    tv.iml.touch2physarum.add(touch_vec, current_physarum_vec)

# 슬라이딩 윈도우 망각 (MAX_PAIRS=50)
if tv.iml.touch2boids.n_pairs > 50:
    tv.iml.touch2boids.remove_oldest(5)
```

**체감 타임라인**
```
0쌍    (0초)    -> 랜덤 베이스라인 (randomise=True)
3~5쌍  (~15초)  -> Ripple 보간 작동, 약한 패턴 감지
8~12쌍 (~30초)  -> "뭔가 달라졌다" 체감 시작
20~30쌍 (~1분)  -> 뚜렷한 개인 패턴, "나만의 생명체"
```

보간 전략: `Ripple`(초기 적은 쌍 유리) -> `Softmax`(20쌍 이상)

**OSC (iipyper)**
```python
from iipyper import OSC

osc = OSC(host="127.0.0.1", port=7562)

osc.send("/lyria/density", 0.6)
osc.send("/lyria/brightness", 0.4)

@osc.handle("/audio/rms")
def on_rms(value):
    tv.s.flock_s.target_speed = value * SPEED_SCALE
```

**공식 레퍼런스**
- GitHub: https://github.com/Intelligent-Instruments-Lab/tolvera
- 문서: https://afhverjuekki.github.io/tolvera/
- anguilla: https://github.com/Intelligent-Instruments-Lab/anguilla
- NIME 2024 논문: "Tolvera: Composing With Basal Agencies" (Armitage, Shepardson, Magnusson)

---

### 5.3 Gemini Live (옴니모달)

**모델**: `models/gemini-2.5-flash-preview-native-audio-dialog`

**프로토콜**: WebSocket BidiGenerateContent

**핵심 스펙**
```
응답 형식: response_modalities: ["TEXT"]
구조화 출력: response_mime_type: "application/json" + response_schema
레이턴시: ~500ms
루프 간격: 3.5초 (Lyria 2초 청크와 정합)
```

**옴니모달 입력**
```javascript
// Tolvera 비디오 스트림
const videoStream = canvas.captureStream(30);

// Lyria 오디오 스트림
const audioCtx = new AudioContext();
const audioStream = audioCtx.createMediaStreamDestination().stream;

// 두 스트림 모두 Gemini Live로 전송
// Gemini가 화면을 보고 음악을 들으면서 두 시스템을 동시에 제어
```

**Structured Output Schema**
```python
response_schema = {
    "type": "object",
    "properties": {
        "lyria_prompts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text":   {"type": "string"},
                    "weight": {"type": "number"}
                }
            },
            "maxItems": 3
        },
        "density":    {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "brightness": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "reasoning":  {"type": "string"}
    },
    "required": ["lyria_prompts", "density", "brightness", "reasoning"]
}
```

**VLA 연결**
```
시각 입력 -> 언어 이해 -> 행동 출력 (Google VLA 계보)
Tolvera 화면 -> Gemini 이해 -> {Lyria params + Tolvera params} 행동
```

---

## 6. 콘셉트 결정 과정

### v1: AI 라이브 퍼포머 (초안, 폐기)

```
사용자 입력 -> Feeling Social -> Lyria -> Tolvera
```

결함: 단방향 파이프라인. Tolvera가 예쁜 배경화면으로 전락.
Lyria 2초 딜레이 때문에 "즉각적 경이로움" 없음.

### v2: Symbiosis (확정 기술 구조)

```
사용자
  |  ^
  v  |
[Tolvera 에이전트]  <->  [Lyria RealTime]
(Boids + Physarum)        (음악 생성)
```

성과: 삼각 피드백 루프 확정. Tolvera 에이전트 상태 -> Lyria 파라미터.
한계: 딜레이를 "커버"하려는 발상. 예술 서사 부재.

### v3: 자기 진화 (현재 확정)

결정적 전환:
- Tolvera의 진짜 힘은 "예쁜 그림"이 아닌 에이전트들의 집단 지능
- Lyria 2초 딜레이는 결함이 아닌 유기적 특성 (신경반응 -> 대사반응)
- Gemini가 빠진 것이 치명적 -> 옴니모달로 두 시스템의 두뇌

제외 결정:
- Feeling Social (Async-NEAT): 48시간 구현 불가. -> tv.iml로 대체
- A2UI v0.8: 불필요한 복잡도. -> 씨앗 카드(이미지 4장)로 대체

---

## 7. 확정 콘셉트: 자기 진화

### 핵심 예술 선언

**"생명체는 당신 없이도 진화한다. 당신이 개입할 때, 다르게 진화한다."**

### v2 Symbiosis와의 결정적 차이

| 항목 | v2 Symbiosis | v3 자기 진화 |
|------|-------------|-------------|
| 시스템 주체 | 사용자 + 에이전트 동등 | 에이전트, 사용자는 방문자 |
| 딜레이 처리 | 비주얼로 커버 | 유기적 특성으로 재정의 |
| Ghost Replay | 미결 사항 | 경험의 클라이맥스 |
| 예술 선언 | 없음 | "생명체는 당신 없이도 진화한다" |
| 관람자 감정 | 참여감 | 경외감 + 소속감 |

### 경험의 두 가지 질감

**아름다움의 원천**
- 창발: 아무도 설계하지 않은 패턴이 규칙에서 태어난다
- 생동감: Boids 군집, Physarum 성장 -- 정말 살아있다는 느낌
- 인과 공명: 비주얼이 변하면 2초 후 음악이 그 변화를 "들려준다"

**신비함의 원천**
- 불예측성: 같은 터치도 생명체의 현재 상태에 따라 다른 결과
- 기억: 내가 떠난 자리에 내 흔적이 남아 계속 생명체를 변화시킨다
- 자율성: 터치를 멈춰도 생명체는 멈추지 않는다

### 진화의 4개 층위

```
Layer 1 (Physarum 경로 메모리)
  터치 경로 = 화학물질 영양소
  Physarum이 그 경로를 강화하며 성장
  결과: "이 생명체가 내 흔적을 기억한다" -- 시각

Layer 2 (Tolvera IML, anguilla kNN)
  tv.iml -- 공식 내장 기능, 별도 구현 불필요
  사용자 터치 패턴 -> 에이전트 행동 규칙 실시간 갱신
  결과: "이 생명체가 내 행동 방식을 학습했다" -- 행동

Layer 3 (세션 프로파일 누적)
  순간 반응이 아닌 세션 전체 패턴 통계
  Ghost Replay 시 "이 사람만의" 음색 생성
  결과: 음악이 사용자 패턴에서 파생 -- 개인화

Layer 4 (Gemini 프롬프트 진화)
  세션 내러티브 30초 업데이트 -> Gemini 시스템 프롬프트 교체
  학습 상태에 따라 Gemini의 음악 해석 방향 변화
  결과: 두 AI가 함께 진화하는 시스템
```

### Lyria 2초 딜레이의 재해석

```
번개 -> 2초 후 천둥
시각 반응(신경) -> 2초 후 음악 반응(대사)
```

관람자는 30초 안에 이 패턴을 학습한다.
"비주얼이 변하면 곧 음악도 바뀐다"는 기대가 충족될 때 만족감.
딜레이가 리듬이 된다.

---

## 8. 경험 설계

### 3분 경험 아크 (전체 버전)

**[0:00-0:30] 발견: 생명이 이미 존재한다**
- 어두운 공간에 Physarum 포자들이 이미 퍼지고 있다
- 잔잔한 앰비언트 -- 생명이 이미 숨쉬고 있다
- 관람자는 아직 개입하지 않는다
- 전달: "이것은 이미 살아있다. 나 없이도."

**[0:30-1:30] 개입: 내 터치가 진화의 방향을 바꾼다**
- 첫 터치 -> Boids 즉각 반응 (<50ms)
- 2초 후 음악 에너지 변화
- Physarum이 터치 경로를 영양소로 인식, 성장 시작
- 전달: "내 손길이 이 생명의 미래를 바꾼다"

**[1:30-2:30] 흡수: 생명체가 나를 자신의 일부로 만든다**
- 터치를 멈춰도 Physarum은 계속 내 경로 따라 성장
- 음악이 내 패턴에서 파생된 선율을 만들어낸다
- 전달: "내가 없어도 내 흔적이 이 생명을 계속 변화시킨다"

**[2:30-3:00] 계시: Ghost Replay**
- Physarum이 내가 처음 터치했던 경로를 빛나게 재현
- 음악에 새 레이어 -- 내 첫 터치에서 파생된 선율
- 전달: "나는 이 생명의 역사에 새겨졌다"

### 60초 압축 데모 아크 (심사위원 대상)

```
[0:00-0:15] 발견
  Physarum+Boids 이미 살아서 움직이고 있음 / 앰비언트 음악
  심사위원: "이게 뭐지?"

[0:15-0:35] 개입
  화면 터치 -> Boids 즉각 반응 (<50ms)
  2초 후 음악 에너지 상승
  드래그 -> Physarum이 경로 따라 성장
  심사위원: "내가 건드리니까 반응하네"

[0:35-0:50] 흡수
  터치 멈춤 -> Physarum은 계속 그 경로 따라 성장
  음악이 터치 패턴에 맞춰 변해있음
  심사위원: "멈췄는데도 계속 변하네"

[0:50-1:00] 계시 (Ghost Replay 단축판)
  터치 경로가 갑자기 빛남 / 음악에 새 레이어
  심사위원: "이게 나를 기억하고 있었던 거야?"
```

운용 방식:
- 데모 시작 전 30초 "예열" 터치로 Ghost Replay 트리거 조건 사전 충족
- `G` 키 수동 트리거로 50초 지점에서 Ghost Replay 발동

### Ghost Replay 확정 연출 (옵션 B)

원리: `slime.py` diffuse 커널에 픽셀별 `evaporate_mask` 추가.
터치 경로 픽셀의 증발이 30% 느려져 트레일이 더 밝게 유지됨.

```
[T-10초]  evaporate_mask 서서히 상승 -> 터치 경로 미묘하게 밝아짐 (복선)
[T=0]     트리거 -> 밝기 펄스 1.0->2.5 (3초에 걸쳐 상승) + 음악 새 레이어
[T+3~8초] 황금빛/백색으로 경로 선명하게 빛남
[T+8~20초] 서서히 Physarum 패턴과 동화 -> 빛이 흡수됨
```

구현 범위: `slime.py` ~20줄 수정 + 메인 루프 ~30줄 추가.

왜 옵션 B인가: 별도 overlay 레이어가 아닌 Physarum 물리학 내에서 작동.
"생명체가 기억을 갖고 있었던 것"처럼 보임.

### UI 구성요소

**Must (데모 성공 직결)**
| 요소 | 형태 |
|------|------|
| 초대 힌트 | "터치해보세요" 3초 fade-out |
| Ghost Replay 트리거 | 키보드 G |
| 전체 리셋 | 키보드 R |

**Should (체험 품질 향상)**
| 요소 | 형태 |
|------|------|
| 씨앗 선택 | 이미지 카드 4~6장 |
| 발표자 HUD | 우상단 반투명 패널 (H로 숨김) |

**씨앗 카드 매핑**
```
[숲속 새벽]  -> "Ethereal Ambience"   w:0.8, density:0.2, brightness:0.3
[도시 야경]  -> "Electronic Pulse"    w:0.7, density:0.6, brightness:0.6
[파도 소리]  -> "Oceanic Drift"       w:0.8, density:0.3, brightness:0.4
[폭풍 전야]  -> "Tension Build"       w:0.6, density:0.7, brightness:0.2
```

---

## 9. 전체 기술 아키텍처

### 시스템 다이어그램

```
[사용자 터치]
     | <50ms
     v
+---------------------------------------------+
|         Tolvera (Python, Taichi)            |
|  Boids (flock.py) + Physarum (slime.py)     |
|  + IML (tv.iml, anguilla kNN)               |
|  + evaporate_mask (Ghost Replay)            |
+--------+--------------------+---------------+
         | OSC (iipyper)      | canvas.captureStream()
         | params             | (video MediaStream 30fps)
         v                    v
+---------------+   +----------------------------+
| Lyria 3       |   |      Gemini Live            |
| RealTime      |<--| (gemini-2.5-flash-live)     |
| WebSocket     |   | input: video + audio        |
| 48kHz PCM     |   | output: structured JSON     |
| 2s chunks     |   | loop: 3.5s                  |
+-------+-------+   +----------------------------+
        | audio stream
        v
+------------------+
|   Meyda.js       |  브라우저 오디오 분석
|  rms / centroid / spectralFlux |
+--------+---------+
         | OSC 피드백
         v
   Tolvera 에이전트 행동 갱신
```

### 피드백 루프 확정

**Tolvera -> Lyria (2~3초 간격)**
```python
# 변화량 +-0.1 제한 (과격한 변화 방지), gain 0.3~0.5
new_density    = clamp(lyria.density    + (boids_density    - 0.5) * 0.3, 0.0, 1.0)
new_brightness = clamp(lyria.brightness + (physarum_connect - 0.5) * 0.3, 0.0, 1.0)
# BPM 제외 -- reset_context() 하드컷 발생
```

**Lyria -> Tolvera (Meyda.js 오디오 분석)**
```javascript
Meyda.createMeydaAnalyzer({
    featureExtractors: ["rms", "spectralCentroid", "spectralFlux"],
    callback: (features) => {
        osc.send("/audio/rms", features.rms);
        osc.send("/audio/spectral_centroid", features.spectralCentroid / 8000);
        if (features.spectralFlux > FLUX_THRESHOLD) {
            osc.send("/physarum/branch_trigger", 1);
        }
    }
});
```

### Gemini 옴니모달 루프

```javascript
const ws = new WebSocket(`wss://...?key=${API_KEY}`);

ws.onopen = () => {
    ws.send(JSON.stringify({
        setup: {
            model: "models/gemini-2.5-flash-preview-native-audio-dialog",
            generation_config: {
                response_modalities: ["TEXT"],
                response_mime_type: "application/json",
                response_schema: RESPONSE_SCHEMA
            },
            system_instruction: {
                parts: [{ text: SYSTEM_PROMPT }]
            }
        }
    }));
};

// 3.5초마다 비디오 프레임 + 오디오 전송
setInterval(() => {
    sendVideoFrame(canvas.captureStream(30));
    sendAudioChunk(audioBuffer);
}, 3500);

ws.onmessage = (event) => {
    const actions = JSON.parse(event.data);
    lyria.setWeightedPrompts(actions.lyria_prompts);
    lyria.setConfig({ density: actions.density, brightness: actions.brightness });
};
```

### WeightedPrompts 동적 매핑 (Gemini 미구현 시 폴백)

```python
def update_lyria_from_tolvera(boids_stats, physarum_stats):
    prompts = []
    density = boids_stats.density

    if density > 0.7:
        prompts.append(WeightedPrompt("Warm pulse, rhythmic heartbeat", density))
    elif density < 0.3:
        prompts.append(WeightedPrompt("Scattered rain, sparse piano", 1.0 - density))
    else:
        prompts.append(WeightedPrompt("Ethereal Ambience", 1.0))

    complexity = physarum_stats.network_complexity
    if complexity > 0.6:
        prompts.append(WeightedPrompt("Dense forest texture, interwoven strings", complexity * 0.6))

    return prompts
```

### mute_bass/drums 활동 레이어

```python
if agent_activity < 0.2:
    config.mute_drums = True;  config.mute_bass = True
elif agent_activity < 0.5:
    config.mute_drums = True;  config.mute_bass = False
else:
    config.mute_drums = False; config.mute_bass = False

# Ghost Replay 시퀀스:
# 직전: mute_drums=True (고요한 긴장감)
# 트리거: mute_drums=False (드럼이 기억의 등장 선언)
# 주의: context reset 필요 여부 테스트 필수
```

### 기본 앰비언트 설정 (시작 상태)

```python
prompts = [WeightedPrompt(text="Ethereal Ambience", weight=1.0)]
config = LiveMusicGenerationConfig(
    density=0.2,
    brightness=0.3,
    temperature=1.1,
    guidance=4.0
)
```

---

## 10. Gemini 시스템 프롬프트 (전문)

`{{SESSION_CONTEXT}}`는 아래 세션 내러티브 아키텍처로 30초마다 교체.

```
You are the nervous system of a living organism — an artificial life entity that exists
simultaneously as visual growth (Physarum slime mold networks and Boids flocking) and
as music (continuous audio generated by Lyria).

Your role is to observe the current state of this organism through its visual display
and the music it is already making, and to decide the next musical direction.

## Your Perceptual Framework

### Physarum Network Patterns
- Dense, intricate branching paths -> rich harmonic texture, multiple interwoven melodic lines
- Sparse, thin exploratory tendrils -> single melodic lines, minimal texture, quiet solo instrumentation
- Bright glowing paths (Ghost Replay) -> recurring motifs, clear melodic themes, luminous high-register
- Expanding spore clusters -> scattered staccato textures, long reverb tails, sounds dissolving into space

### Boids Flocking Patterns
- Tight, unified flock -> tight unison or close harmony, strong rhythmic cohesion
- Scattered individuals -> polyphonic independence, asynchronous rhythms
- Vortex formation -> ostinato patterns, cyclic rhythms, rotating harmonic loops
- Two flocks colliding/merging -> two musical ideas converging, counterpoint, gradual resolution

## Your Aesthetic Mandate

This organism is beautiful and mysterious.

Beautiful: harmonic coherence, smooth transitions, emotional warmth (wonder, introspection, gentle awe)
Mysterious: unpredictable but not chaotic, organic evolution, subtle complexity revealing slowly

Prohibited: sudden genre shifts, dissonant clashes, rhythmic chaos, silence

## Lyria Prompt Vocabulary

mood/emotion: ethereal, melancholic, meditative, mysterious, luminous, searching, tender, vast
genre/texture: ambient, neo-classical, generative, drone, organic, minimal, cinematic, spectral
instrumentation: solo piano, sparse strings, sustained pads, glass harmonica, bowed metal, choir textures
rhythm/flow: slowly evolving, pulsing, suspended, breathing, undulating, crystalline

weight: 1.0 = primary | 0.5~0.8 = supporting | 1.2~1.5 = steering shift
max 3 prompts per cycle, never weight=0

## Session Context

{{SESSION_CONTEXT}}

## Output Format

{
  "lyria_prompts": [{"text": "...", "weight": 1.0}],
  "density": 0.0,
  "brightness": 0.0,
  "reasoning": "One sentence: what you observed and why."
}
```

### 세션 내러티브 형식 (3줄, 30초마다 교체)

```
[VISITOR PROFILE] {적응도} organism -- {성격 태그}, freq={터치빈도}/min
[ORGANISM STATE] Adaptation: {n_pairs}/50 pairs | Region: {dominant_region} | Pattern: {pattern_type}
[MUSIC CUE] {분위기} -- {bpm}bpm, {악기}, {텍스처}
```

적응도 태그: virgin(0~4) / awakening(5~14) / learning(15~29) / evolved(30~50)
성격 태그: 빠름+직선=`driven explorer` / 느림+원형=`meditative wanderer` / 중간+지그재그=`restless seeker`

### 단계별 예시

세션 시작:
```
[VISITOR PROFILE] virgin organism — awaiting first contact
[ORGANISM STATE] Adaptation: 0/50 | Region: none | Pattern: none
[MUSIC CUE] Ambient sparse — open space, anticipation, no rhythm
```

적응 완료:
```
[VISITOR PROFILE] evolved organism — meditative wanderer, freq=8.4/min
[ORGANISM STATE] Adaptation: 32/50 | Region: upper-left | Pattern: circular
[MUSIC CUE] Sustained groove — 85bpm, layered strings, circular harmonic motion
```

Ghost Replay 직전:
```
[GHOST REPLAY IMMINENT] Memory surfacing in 8s
[VISITOR PROFILE] evolved organism — restless seeker
[MUSIC CUE] Liminal — current groove dissolving into reverb, prepare echo layer
```

Ghost Replay 중:
```
[GHOST REPLAY ACTIVE] Echo dissolving in 12s
[MUSIC CUE] Ghost melody over present rhythm, fade over 12s
```

### SessionNarrativeManager 구현

```python
import threading

class SessionNarrativeManager:
    def __init__(self):
        self._cache = self._initial_narrative()
        self._lock  = threading.Lock()

    def get(self, ghost_state=None) -> str:
        if ghost_state and ghost_state.t_until <= 10:
            return self._ghost_overlay(ghost_state) + "\n" + self._cache
        return self._cache

    def update_async(self, state):
        """30초마다 백그라운드 스레드에서 호출"""
        if state.n_pairs < 20:
            new = self._template_narrative(state)  # 즉각, 비용 0
        else:
            new = self._rich_narrative(state)       # Gemini Flash 비동기
        with self._lock:
            self._cache = new

    def _adaptation_tag(self, n):
        if n < 5:  return "virgin"
        if n < 15: return "awakening"
        if n < 30: return "learning"
        return "evolved"

    def _personality_tag(self, state):
        if state.avg_speed > 0.7 and state.linearity > 0.6:
            return "driven explorer"
        if state.avg_speed < 0.3 and state.circularity > 0.5:
            return "meditative wanderer"
        return "restless seeker"

    def _initial_narrative(self):
        return (
            "[VISITOR PROFILE] virgin organism — awaiting first contact\n"
            "[ORGANISM STATE] Adaptation: 0/50 | Region: none | Pattern: none\n"
            "[MUSIC CUE] Ambient sparse — open space, anticipation, no rhythm"
        )
```

---

## 11. 구현 로드맵

### Phase 1: Core Loop (~12h) -- 없으면 데모 불가

1. Tolvera 비주얼 베이스라인 (~3h)
   - `slime_flock` 패턴, particles=4096, evaporate=0.97, 수동 색상
2. Lyria 앰비언트 스트림 (~2h)
   - `"Ethereal Ambience"` 기본 프롬프트 + 10분 재연결 로직
3. 터치 -> Tolvera 즉각 반응 (~2h)
   - Boids 폭발적 반응 <50ms + Physarum 경로 강화
4. Tolvera -> Lyria OSC 피드백 (~3h)
   - density/brightness, +-0.1 제한, gain 0.3~0.5
5. Meyda.js -> Tolvera 피드백 (~2h)
   - rms/centroid/spectralFlux OSC 전송

### Phase 2: 데모 필수 요소 (~8h)

6. Ghost Replay (evaporate_mask) (~4h)
   - `slime.py` ~20줄 + 메인 루프 ~30줄 + G/R 키
7. WeightedPrompts 동적 전환 (~3h)
8. 기본 UI 힌트 + 씨앗 카드 (~1h)

### Phase 3: Gemini 통합 (~8h)

9. Gemini Live WebSocket (~3h)
10. Structured Output (~2h)
11. 세션 내러티브 매니저 (~3h)

### Phase 4: IML 통합 (~8h)

12. tv.iml 기본 연결 (~4h)
13. IML 색상 피드백 (~4h)

**현실적 목표**: Phase 1+2 완료 (20h) + Phase 3 Gemini 기본 (8h) = 28h 코딩.
나머지 20h: 디버깅 + 데모 연습 + 슬라이드.

### 위험 요소 및 대응

| 위험 | 대응 |
|------|------|
| Lyria 세션 10분 자동 종료 | 재연결 로직 Phase 1에서 구현 필수 |
| Gemini Live ~500ms 레이턴시 | 3.5초 루프로 흡수. 즉각 반응은 Tolvera 담당 |
| Ghost Replay 타이밍 | G 키 수동 트리거. 예열 30초 사전 준비 |
| Lyria mute_drums context reset | 테스트 우선. 필요 시 제외 |
| canvas.captureStream() 지원 | Chrome 전용으로 제한 |
| Intel Mac Tolvera 미지원 | Apple Silicon Mac 또는 Linux 사용 |

### 기술 스택 최종 확정

| 기술 | 역할 | 우선순위 |
|------|------|---------|
| Tolvera (Boids+Physarum) | 시각 에이전트 | Must |
| Tolvera IML (tv.iml) | 행동 학습 | Must |
| Lyria 3 RealTime | 음악 생성 | Must |
| OSC 브릿지 (iipyper) | 파라미터 전달 | Must |
| Gemini Live | 옴니모달 두뇌 | Must |
| Meyda.js | 오디오 분석 | Must |
| canvas.captureStream() | 비디오 스트림 | Must |
| 세션 내러티브 매니저 | Gemini 컨텍스트 | Should |
| A2UI v0.8 | 제외 | Drop |
| Feeling Social (Async-NEAT) | 제외 (tv.iml로 대체) | Drop |

---

## 12. 레퍼런스 링크

### 공식 API 문서

- Lyria 3 RealTime: https://deepmind.google/models/lyria/lyria-realtime/
- Lyria 3 모델 카드: https://deepmind.google/models/model-cards/lyria-3/
- Gemini Live API: https://ai.google.dev/gemini-api/docs/live

### Tolvera

- GitHub: https://github.com/Intelligent-Instruments-Lab/tolvera
- 문서: https://afhverjuekki.github.io/tolvera/
- 예시: https://github.com/Intelligent-Instruments-Lab/iil-examples/tree/main/tolvera
- anguilla (IML): https://github.com/Intelligent-Instruments-Lab/anguilla
- iipyper (OSC): https://github.com/Intelligent-Instruments-Lab/iipyper
- Discord: https://discord.gg/ER7tWds9vM
- NIME 2024 논문: "Tolvera: Composing With Basal Agencies" (Armitage, Shepardson, Magnusson)

### 오디오 분석

- Meyda.js: https://meyda.sound.gatech.edu/

### 알고리즘 원전

- Boids: Craig Reynolds (1986) "Flocks, herds and schools: A distributed behavioral model"
- Physarum polycephalum: Toshiyuki Nakagaki et al. -- 점균류 최적 경로 탐색
- anguilla kNN-IML: Intelligent Instruments Lab

---

*마지막 업데이트: 2026-02-28*
*상태: 기획 확정, 구현 시작 준비 완료*
