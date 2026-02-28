# Track 1 Art: 자기 진화 (Self-Evolution)

> 상태: 기획 확정 (2026-02-28)
> 해커톤: Track 1 Entertainment (Google Gemini Hackathon)
> 스택: Lyria 3 RealTime + Tolvera + Gemini Live (옴니모달)

---

## 한 줄 설명

**화면 속 생명체가 스스로 진화한다. 당신이 개입하면 다르게 진화한다. 당신이 떠나도 당신의 흔적이 남는다.**

---

## 문서 구조

| 파일 | 내용 |
|------|------|
| [`concept.md`](concept.md) | 예술 선언, 경험 아크, "와" 순간 설계 |
| [`architecture.md`](architecture.md) | 전체 기술 아키텍처 (Gemini + Lyria + Tolvera + IML) |
| [`prompts.md`](prompts.md) | Gemini 시스템 프롬프트 + 세션 내러티브 아키텍처 |
| [`implementation.md`](implementation.md) | 구현 우선순위 + 코드 스니펫 + 설정값 |

---

## 핵심 예술 선언

> "생명체는 당신 없이도 진화한다. 당신이 개입할 때, 다르게 진화한다."

---

## 시스템 한눈에 보기

```
[터치]
  │ <50ms
  ▼
[Tolvera - GPU 에이전트]
  Boids (군집) + Physarum (슬라임) + IML (학습)
  │                          │
  │ OSC params               │ canvas.captureStream()
  ▼                          ▼
[Lyria 3 RealTime]    [Gemini Live 옴니모달]
  음악 생성                  시각+음악 인식
  2초 청크                   → structured actions
  │                          │
  │ Meyda.js 오디오 분석      │ WeightedPrompts + params
  ▼                          ▼
[Tolvera 피드백]      [Lyria + Tolvera 동시 제어]
```

---

## 버전 계보

- **v1**: AI 라이브 퍼포머 — 단방향 파이프라인 (사용자→Lyria→Tolvera)
- **v2**: Symbiosis — 삼각 피드백 루프 (기술 구조 확정)
- **v3**: 자기 진화 — 에이전트가 주체, 사용자는 방문자 (현재)

---

## 심사 기준별 전략

| 기준 | 가중치 | 전략 |
|------|--------|------|
| **Demo** | 50% | 60초 압축 아크: 발견→개입→흡수→계시(Ghost Replay). 터치 즉각 반응(<50ms) |
| **Impact** | 25% | 라이브 VJ/DJ를 위한 AI 공연 파트너. 실시간 A/V 퍼포먼스 민주화 |
| **Creativity** | 15% | P1(멀티모달) + P8(Google API 극한 활용). 생물학적 공생 서사 |
| **Pitch** | 10% | "Lyria + Gemini = Google이기 때문에 가능한 경험" |
