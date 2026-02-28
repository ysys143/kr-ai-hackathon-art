# 기술 아키텍처

---

## 전체 시스템 다이어그램

```
[사용자 터치]
     │ <50ms
     ▼
┌─────────────────────────────────────┐
│         Tolvera (Python, Taichi)    │
│  Boids (flock.py) + Physarum (slime.py) │
│  + IML (tv.iml, anguilla kNN)       │
│  + evaporate_mask (Ghost Replay)    │
└────────┬──────────────┬─────────────┘
         │ OSC          │ canvas.captureStream()
         │ params       │ (video MediaStream)
         ▼              ▼
┌─────────────┐   ┌──────────────────────────┐
│ Lyria 3     │   │      Gemini Live          │
│ RealTime    │◄──│  (gemini-2.5-flash-live)  │
│ WebSocket   │   │  input: video + audio     │
│ 48kHz PCM   │   │  output: structured JSON  │
│ 2s chunks   │   │  loop: 3.5s               │
└──────┬──────┘   └──────────────────────────┘
       │ audio stream
       ▼
┌─────────────────┐
│   Meyda.js      │  오디오 분석 (브라우저)
│  rms / spectralCentroid / spectralFlux │
└────────┬────────┘
         │ OSC 피드백
         ▼
   Tolvera 에이전트 행동 갱신
```

---

## Gemini 옴니모달 아키텍처

### 핵심 전환

기존 잘못된 접근 (text-only):
```
Tolvera 수치 (boids_density: 0.72, ...) → 텍스트 → Gemini → 프롬프트
```
→ Gemini를 glorified switch-case로 쓰는 것. 폐기.

**올바른 접근 (옴니모달):**
```
canvas.captureStream() → Tolvera 시각 (실시간 video)  ↘
                                                        Gemini Live → structured actions
AudioContext stream    → Lyria 음악 (실시간 audio)     ↗
```

Gemini가 Tolvera 화면을 **직접 보고** Lyria 음악을 **직접 들으면서**
두 시스템을 동시에 제어하는 진짜 에이전트.

### Gemini Live 루프 (3.5초)

```
[3.5초 루프]
Tolvera canvas (video frame) + Lyria audio (2초 청크)
  → Gemini Live (gemini-2.5-flash-preview-native-audio-dialog)
  → structured JSON 출력:

{
  "lyria_prompts": [
    {"text": "Warm pulse, rhythmic heartbeat", "weight": 0.7},
    {"text": "Dense forest texture, strings",  "weight": 0.3}
  ],
  "density": 0.6,
  "brightness": 0.4,
  "reasoning": "Boids forming tight vortex → rhythmic cohesion needed"
}
```

3.5초 루프가 Lyria 2초 청크와 자연스럽게 정합.

### Gemini Live API 상세

```
모델: models/gemini-2.5-flash-preview-native-audio-dialog
프로토콜: WebSocket BidiGenerateContent
응답 형식: response_modalities: ["TEXT"]
구조화 출력: response_mime_type: "application/json" + response_schema
레이턴시: ~500ms
```

### VLA 연결

Google의 VLA(Vision-Language-Action) 계보:
```
시각 입력 → 언어 이해 → 행동 출력
```

우리 시스템:
```
Tolvera 화면 → Gemini 이해 → {Lyria params + Tolvera params} 행동
```

피치: "Lyria가 음악을 만들고, Gemini가 무엇을 만들지 결정합니다. Lyria와 Gemini의 공생 — Google이기 때문에 가능한 경험."

---

## Lyria 3 RealTime API

### 핵심 스펙

```
엔드포인트: wss://generativelanguage.googleapis.com/ws/...
모델: models/lyria-realtime-exp
출력: 48kHz stereo 16-bit PCM, 2초 청크
세션 제한: 10분 자동 종료 → 재연결 로직 필수
```

### 제어 가능한 파라미터

```python
from google.generativeai.types import LiveMusicGenerationConfig, WeightedPrompt

# 프롬프트 (가장 강력한 제어)
prompts = [
    WeightedPrompt(text="Ethereal Ambience", weight=1.0),
    WeightedPrompt(text="Warm Pulse, rhythmic heartbeat", weight=0.7),
]

# 수치 파라미터
config = LiveMusicGenerationConfig(
    density=0.2,      # 0.0~1.0 (음악 밀도)
    brightness=0.3,   # 0.0~1.0 (음색 밝기)
    temperature=1.1,  # 기본값 (다양성)
    guidance=4.0,     # 0~6 (프롬프트 준수도)
    mute_bass=False,
    mute_drums=False,
)
```

### 제약 사항 (중요)

- BPM 변경 → `reset_context()` 필요 (하드컷 발생) → **BPM 매핑 제외**
- 빈 프롬프트 불가 → 최소 1개 WeightedPrompt 항상 유지
- `setWeightedPrompts()` API로 세션 중 프롬프트 변경 가능

### 기본 앰비언트 설정 (확정)

```python
prompts = [WeightedPrompt(text="Ethereal Ambience", weight=1.0)]
config = LiveMusicGenerationConfig(
    density=0.2,
    brightness=0.3,
    temperature=1.1,
    guidance=4.0
)
```

`"Ethereal Ambience"` 하나로 모델이 앰비언트 파라미터 자동 결정.

---

## Tolvera

### 핵심 구성요소

```
언어: Python
GPU: Taichi Lang (GPU 가속)
에이전트:
  - Boids (flock.py): 군집 시뮬레이션
  - Physarum (slime.py): 슬라임 곰팡이 경로 탐색
  - IML (tv.iml): anguilla kNN-IML 내장 학습
OSC: iipyper 라이브러리
```

### 확정 시각 설정

```python
particles  = 4096      # 최소값. 기본 1024은 시각 밀도 부족
evaporate  = 0.97      # 기본 0.99는 equilibrium 고착 위험
# 색상: 수동 지정 (랜덤 색상은 충돌 가능)
# 청록/마젠타/노랑/흰색 권장
# 배경: 검정(0,0,0,1) — 트레일이 발광 효과로 보임
# 구성: slime_flock (Physarum + Boids 합성) 필수
#       → Boids 이동이 슬라임 트레일로 기록됨
```

### Physarum 주요 파라미터

```python
SENSE_ANGLE = 45.0   # 탐색 각도 (낮을수록 방향성, 높을수록 탐색적)
SENSE_DIST  = 0.05   # 탐색 거리
MOVE_DIST   = 0.01   # 이동 거리
evaporate   = 0.97   # 증발 속도 (1.0에 가까울수록 트레일 오래 유지)
```

### Boids 주요 파라미터

```python
separation = 0.5    # 분리 힘 (너무 높으면 흩어짐)
alignment  = 0.5    # 정렬 힘 (군집 방향 통일)
cohesion   = 0.5    # 응집 힘 (군집 유지)
```

### OSC 인터페이스 (iipyper)

```python
# Tolvera → Lyria (파라미터 전송)
osc.send("/lyria/density", boids_density)
osc.send("/lyria/brightness", physarum_connectivity)

# Lyria → Tolvera (Meyda.js 분석 결과 수신)
@osc.handle("/audio/rms")
def on_rms(value): boids.target_speed = value * speed_scale

@osc.handle("/audio/spectral_centroid")
def on_centroid(value): physarum.sense_dist = value * dist_scale

@osc.handle("/physarum/branch_trigger")
def on_branch(value): physarum.trigger_branch()
```

---

## Tolvera IML (anguilla kNN-IML)

### 내장 ML 기능

Tolvera에 `tv.iml`로 접근 가능한 공식 내장 기능.
별도 ML 라이브러리 구현 없이 설정만으로 사용.

```python
# anguilla kNN 라이브러리 기반
# 9가지 매핑 타입 지원 (vec2vec, fun2vec 등)
# 보간 전략: Nearest / Mean / Softmax / Smooth / Ripple
```

### 입출력 벡터 설계

```
입력 (4D): [touch_x_norm, touch_y_norm, touch_velocity, touch_dwell]
출력 A (3D): Boids [separation, alignment, cohesion]
출력 B (3D): Physarum [sense_angle, sense_dist, move_dist]
```

4D 입력: 차원의 저주 방지 sweet spot.

### 설정

```python
tv.iml.touch2boids = {
    'size': (4, 3),
    'io': (get_touch_vec, tv.s.flock_s.from_vec),
    'randomise': True,   # 자동 랜덤 초기 쌍 주입 (베이스라인 자율 진화)
    'lag': 0.4,          # 갑작스러운 변화 완충
}
tv.iml.touch2physarum = {
    'size': (4, 3),
    'io': (get_touch_vec, tv.s.physarum_s.from_vec),
    'randomise': True,
    'lag': 0.5,          # Physarum은 더 느리게 반응
}
```

### 학습 타이밍

```python
# 0.5초 간격 + delta 임계치 0.05 필터
if elapsed > 0.5 and touch_delta > 0.05:
    iml.add(touch_vec, current_target_vec)

# 슬라이딩 윈도우 망각 (MAX_PAIRS=50)
if iml.n_pairs > 50:
    iml.remove_oldest(5)
```

### 체감 타임라인

| 터치 쌍 수 | 경과 시간 | 체감 |
|-----------|---------|------|
| 0쌍 | 0초 | 랜덤 베이스라인 (randomise=True) |
| 3~5쌍 | ~15초 | Ripple 보간 작동, 약한 패턴 |
| 8~12쌍 | ~30초 | **"뭔가 달라졌다" 체감 시작** |
| 20~30쌍 | ~1분 | 뚜렷한 개인 패턴, "나만의 생명체" |

보간 전략: `Ripple`(초기 적은 쌍 유리) → `Softmax`(20쌍 이상).

### Physarum + IML 시너지

```
Layer 1 (Physarum 경로 메모리): "이 생명체가 내 흔적을 기억한다" — 시각
Layer 2 (IML 행동 학습):       "이 생명체가 내 행동 방식을 학습했다" — 행동

사용자가 느린 원형 드래그:
  → IML: Physarum sense_angle 넓어짐 (더 탐색적)
  → Physarum 트레일: 원형 경로 강화
  시각(경로) + 행동(탐색 방식) 양쪽에서 동시에 기억 형성
```

---

## 피드백 루프

### Tolvera → Lyria

```python
# 2~3초 간격, 피드백 gain 0.3~0.5
# 변화량 ±0.1 이내로 제한 (과격한 변화 방지)

new_density    = clamp(lyria_density    + (boids_density    - 0.5) * 0.3, 0.0, 1.0)
new_brightness = clamp(lyria_brightness + (physarum_connect - 0.5) * 0.3, 0.0, 1.0)

# BPM 제외 — 변경 시 reset_context() 필요 (하드컷 발생)
```

### Lyria → Tolvera (Meyda.js)

```javascript
// 브라우저에서 오디오 분석 (288 ops/sec)
const analyzer = Meyda.createMeydaAnalyzer({
    audioContext: audioCtx,
    source: audioSource,
    bufferSize: 512,
    featureExtractors: ["rms", "spectralCentroid", "spectralFlux"],
    callback: (features) => {
        // rms → Boids 목표 속도
        osc.send("/audio/rms", features.rms);

        // spectralCentroid → Physarum 확산 속도
        osc.send("/audio/spectral_centroid", features.spectralCentroid / 8000);

        // spectralFlux → Physarum 분기 트리거 (임계값 초과 시)
        if (features.spectralFlux > FLUX_THRESHOLD) {
            osc.send("/physarum/branch_trigger", 1);
        }
    }
});
```

### 주의사항

```
Lyria 세션 10분 자동 종료 → 재연결 로직 필수
피드백 루프 간격: 2-3초 (Lyria 2초 청크와 정합)
gain 값: 0.3~0.5 (과도한 피드백 발산 방지)
BPM 매핑: 제외 (하드컷 발생)
```

---

## 패턴 파생 선율 매핑

터치 특성 → Lyria 파라미터 매핑:

```python
# 즉각 반응 (레벨 1, ~4h)
new_density    = 0.1 + touch_speed_norm * 0.8    # 빠른 터치 → dense
new_brightness = 1.0 - (touch_y / screen_height) # 위쪽 터치 → bright

# 누적 빈도 (레벨 2, ~8h 추가)
if session_touch_freq > HIGH_THRESHOLD:
    prompts.append({"text": "energetic rhythm, percussion", "weight": touch_freq_ratio})
elif session_touch_freq < LOW_THRESHOLD:
    prompts.append({"text": "ambient, atmospheric, sparse", "weight": 1.0 - touch_freq_ratio})

# 드래그 패턴 (원형)
if drag_circularity > 0.7:
    config.guidance = 2.0    # 더 자유로운 음악 탐색

# 세션 프로파일 (레벨 3, ~12h 추가)
# Ghost Replay 시: 세션 프로파일 기반 "이 사람만의" 음색
if ghost_replay_triggered:
    apply_session_profile_to_prompts(session_profile)
```

---

## mute_bass/drums 활동 레이어

```python
if agent_activity < 0.2:
    config.mute_drums = True
    config.mute_bass  = True
elif agent_activity < 0.5:
    config.mute_drums = True
    config.mute_bass  = False
else:
    config.mute_drums = False
    config.mute_bass  = False

# Ghost Replay 시퀀스
# 직전: mute_drums=True (고요한 긴장감)
# 트리거: mute_drums=False + 새 레이어 (드럼이 기억의 등장을 선언)
# 주의: context reset 필요 여부 먼저 테스트
```

---

## 기술 스택 요약

| 기술 | 역할 | 우선순위 | 레이턴시 |
|------|------|---------|---------|
| **Tolvera (Boids+Physarum)** | 시각 에이전트 시뮬레이션 | Must | <50ms |
| **Tolvera IML (tv.iml)** | 행동 학습 (anguilla kNN) | Must | 0.4~0.5s lag |
| **Lyria 3 RealTime** | 음악 생성 (WebSocket) | Must | 2s 청크 |
| **OSC 브릿지 (iipyper)** | Tolvera ↔ Lyria 파라미터 전달 | Must | <10ms |
| **Gemini Live** | 옴니모달 두뇌 (video+audio→actions) | Must | ~500ms |
| **Meyda.js** | 브라우저 오디오 분석 | Must | ~3ms |
| **canvas.captureStream()** | Tolvera → Gemini 비디오 스트림 | Must | ~0ms |
| **세션 내러티브 매니저** | 학습 상태 → Gemini 컨텍스트 | Should | 30s 업데이트 |
| **A2UI v0.8** | 제외 (씨앗 카드로 대체) | Drop | — |
| **Feeling Social (Async-NEAT)** | 제외 (tv.iml로 대체) | Drop | — |
