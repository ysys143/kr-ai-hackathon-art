# 구현 로드맵

---

## MVP 구현 성공 확률

| 스코프 | 확률 |
|--------|------|
| Core (Lyria + Tolvera + 기본 피드백) | 85% |
| + Gemini 옴니모달 | 70% |
| + IML 학습 | 75% |
| + Ghost Replay | 80% |
| 전체 풀 스택 | 55~65% |

---

## 구현 우선순위

### Phase 1: Core Loop (~12h) - 없으면 데모 불가

1. **Tolvera 비주얼 베이스라인** (~3h)
   - `slime_flock` 패턴 (Physarum + Boids 합성)
   - 확정 설정: particles=4096, evaporate=0.97, 수동 색상

2. **Lyria 앰비언트 스트림** (~2h)
   - `"Ethereal Ambience"` 기본 프롬프트
   - density=0.2, brightness=0.3 시작값
   - 10분 세션 재연결 로직

3. **터치 → Tolvera 즉각 반응** (~2h)
   - 터치 → Boids 군집 폭발적 반응 (<50ms)
   - 드래그 → Physarum 경로 강화 (영양소 매핑)

4. **Tolvera → Lyria OSC 피드백** (~3h)
   - Boids 밀도 → `density` (±0.1 제한)
   - Physarum 연결성 → `brightness` (±0.1 제한)
   - 2~3초 간격, gain 0.3~0.5

5. **Meyda.js → Tolvera 피드백** (~2h)
   - `rms` → Boids 속도
   - `spectralCentroid` → Physarum 확산 속도
   - `spectralFlux` → Physarum 분기 트리거

### Phase 2: 데모 필수 요소 (~8h)

6. **Ghost Replay (evaporate_mask)** (~4h)
   - `slime.py` diffuse 커널 `evaporate_mask` 추가 (~20줄)
   - 메인 루프 트리거 시퀀스 (~30줄)
   - `G` 키 수동 트리거
   - `R` 키 전체 리셋

7. **WeightedPrompts 동적 전환** (~3h)
   - 터치 속도 → `density`
   - 터치 위치 → `brightness`
   - Boids 밀도 조건별 프롬프트 블렌딩

8. **기본 UI** (~1h)
   - "터치해보세요" 3초 fade-out
   - 씨앗 카드 4장

### Phase 3: Gemini 통합 (~8h)

9. **Gemini Live WebSocket** (~3h)
   - `canvas.captureStream()` 비디오 스트림
   - `AudioContext` 오디오 스트림
   - BidiGenerateContent 연결

10. **Structured Output** (~2h)
    - `response_schema` JSON 스키마 적용
    - 시스템 프롬프트 주입

11. **세션 내러티브 매니저** (~3h)
    - 30초 업데이트 백그라운드 스레드
    - `{{SESSION_CONTEXT}}` 교체 로직
    - Ghost Replay 오버레이

### Phase 4: IML 통합 (~8h)

12. **tv.iml 기본 연결** (~4h)
    - `touch2boids`, `touch2physarum` 설정
    - 0.5초 간격 쌍 추가 로직
    - MAX_PAIRS=50 슬라이딩 윈도우

13. **IML 색상 피드백** (~4h)
    - 학습 쌍 수에 따른 색상 변화 (학습 정도 시각화)

---

## Ghost Replay 구현 상세

### slime.py 수정 (~20줄)

```python
# evaporate_mask 필드 추가
evaporate_mask = ti.field(ti.f32, shape=(W, H))

@ti.kernel
def diffuse_with_memory():
    for x, y in pixels:
        # 기존 증발 계산
        base_evaporate = evaporate
        # 터치 경로 픽셀: 30% 느린 증발
        mask_factor = evaporate_mask[x, y]
        effective_evaporate = base_evaporate + (1.0 - base_evaporate) * mask_factor * 0.3
        pixels[x, y] *= effective_evaporate

@ti.kernel
def record_touch_path(tx: int, ty: int, radius: int):
    for dx, dy in ti.ndrange((-radius, radius+1), (-radius, radius+1)):
        nx, ny = tx + dx, ty + dy
        if 0 <= nx < W and 0 <= ny < H:
            if dx*dx + dy*dy <= radius*radius:
                evaporate_mask[nx, ny] = ti.min(evaporate_mask[nx, ny] + 0.1, 1.0)
```

### 메인 루프 트리거 (~30줄)

```python
ghost_state = GhostState()

class GhostState:
    def __init__(self):
        self.active        = False
        self.start_time    = 0
        self.duration      = 20  # 초
        self.brightness_target = 2.5

    def trigger(self):
        self.active     = True
        self.start_time = time.time()
        # mute_drums=False (드럼이 기억의 등장 선언)
        lyria.set_config(mute_drums=False)

    def tick(self, dt):
        if not self.active:
            return
        elapsed = time.time() - self.start_time
        if elapsed > self.duration:
            self.active = False
            return
        # 밝기 펄스: 0~3초 상승, 3~8초 유지, 8~20초 하강
        if elapsed < 3:
            factor = elapsed / 3.0
        elif elapsed < 8:
            factor = 1.0
        else:
            factor = 1.0 - (elapsed - 8) / 12.0
        target_brightness = 1.0 + 1.5 * factor  # 1.0 → 2.5
        slime.set_brightness_multiplier(target_brightness)

# 키 바인딩
def on_key(key):
    if key == 'G':
        ghost_state.trigger()
        narrative_manager.notify_ghost(ghost_state)
    elif key == 'R':
        full_reset()

def full_reset():
    tolvera.reset()
    iml.clear()
    lyria.reset_context()
    narrative_manager.reset()
    evaporate_mask.fill(0)
```

---

## Tolvera IML 구현 상세

```python
# 터치 입력 벡터 생성
def get_touch_vec():
    touch = get_latest_touch()
    return [
        touch.x / SCREEN_W,      # 정규화 x
        touch.y / SCREEN_H,      # 정규화 y
        touch.velocity / MAX_VEL, # 정규화 속도
        touch.dwell / MAX_DWELL   # 정규화 체류 시간
    ]

# IML 초기화
tv.iml.touch2boids = {
    'size': (4, 3),
    'io': (get_touch_vec, tv.s.flock_s.from_vec),
    'randomise': True,
    'lag': 0.4,
}
tv.iml.touch2physarum = {
    'size': (4, 3),
    'io': (get_touch_vec, tv.s.physarum_s.from_vec),
    'randomise': True,
    'lag': 0.5,
}

# 학습 루프 (0.5초 간격)
last_add_time = 0
last_touch_vec = None

def iml_update_loop():
    global last_add_time, last_touch_vec
    while running:
        now = time.time()
        if now - last_add_time > 0.5:
            current_vec = get_touch_vec()
            if last_touch_vec is not None:
                delta = np.linalg.norm(np.array(current_vec) - np.array(last_touch_vec))
                if delta > 0.05:
                    tv.iml.touch2boids.add(current_vec, tv.s.flock_s.to_vec())
                    tv.iml.touch2physarum.add(current_vec, tv.s.physarum_s.to_vec())
                    last_add_time = now
                    last_touch_vec = current_vec

                    # 슬라이딩 윈도우 망각
                    for iml in [tv.iml.touch2boids, tv.iml.touch2physarum]:
                        if iml.n_pairs > 50:
                            iml.remove_oldest(5)
        time.sleep(0.1)
```

---

## Lyria WeightedPrompts 동적 매핑

```python
def update_lyria_from_tolvera(boids_stats, physarum_stats):
    prompts = []

    # Boids 상태 → 프롬프트
    density = boids_stats.density
    if density > 0.7:
        prompts.append(WeightedPrompt(
            text="Warm pulse, rhythmic heartbeat, unified",
            weight=density
        ))
    elif density < 0.3:
        prompts.append(WeightedPrompt(
            text="Scattered rain, sparse piano, individual",
            weight=1.0 - density
        ))
    else:
        prompts.append(WeightedPrompt(
            text="Ethereal Ambience",
            weight=1.0
        ))

    # Physarum 상태 → 프롬프트 블렌딩
    complexity = physarum_stats.network_complexity
    if complexity > 0.6:
        prompts.append(WeightedPrompt(
            text="Dense forest texture, interwoven strings",
            weight=complexity * 0.6
        ))

    # density/brightness 파라미터
    new_density = clamp(
        lyria.density + (boids_stats.density - 0.5) * 0.3,
        0.0, 1.0
    )
    new_brightness = clamp(
        lyria.brightness + (physarum_stats.connectivity - 0.5) * 0.3,
        0.0, 1.0
    )

    lyria.set_weighted_prompts(prompts)
    lyria.set_config(density=new_density, brightness=new_brightness)


def clamp(val, lo, hi):
    return max(lo, min(hi, val))
```

---

## 구현 공수 요약

| 구성요소 | 공수 | 우선순위 |
|---------|------|---------|
| Tolvera 비주얼 베이스라인 | 3h | Must |
| Lyria 앰비언트 스트림 | 2h | Must |
| 터치 → Tolvera 반응 | 2h | Must |
| Tolvera → Lyria OSC | 3h | Must |
| Meyda.js → Tolvera | 2h | Must |
| Ghost Replay | 4h | Must |
| WeightedPrompts 동적 | 3h | Must |
| 기본 UI (힌트+키) | 1h | Must |
| **Phase 1+2 합계** | **~20h** | |
| Gemini Live 연결 | 3h | Should |
| Structured Output | 2h | Should |
| 세션 내러티브 매니저 | 3h | Should |
| IML 기본 통합 | 4h | Should |
| **Phase 3+4 합계** | **~12h** | |
| mute_bass/drums 레이어 | 2h | Could |
| spectralFlux 분기 | 5h | Could |
| IML 색상 피드백 | 4h | Could |
| 씨앗 카드 UI | 2h | Could |
| **전체 합계** | **~45h** | |

**48시간 해커톤 현실적 목표:** Phase 1+2 완료 (20h) + Phase 3 Gemini 기본 (8h) = 28h 코딩.
나머지 20h: 디버깅 + 데모 연습 + 슬라이드.

---

## 위험 요소 및 대응

| 위험 | 대응 |
|------|------|
| Lyria 세션 10분 자동 종료 | 재연결 로직 Phase 1에서 구현 필수 |
| Gemini Live 레이턴시 500ms | 3.5초 루프로 흡수. 즉각 반응은 Tolvera가 담당 |
| IML 랜덤 초기화 불안정 | `randomise=True`로 베이스라인 확보. 학습은 덤 |
| Ghost Replay 타이밍 | `G` 키 수동 트리거로 제어. 예열 30초 사전 준비 |
| Lyria mute_drums context reset | Phase 2에서 먼저 테스트. 필요 시 제외 |
| canvas.captureStream() 브라우저 지원 | Chrome 전용으로 제한 (해커톤에서 충분) |
