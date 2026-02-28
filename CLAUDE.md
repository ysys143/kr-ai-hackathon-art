
---

## Karpathy Coding Guidelines

> Behavioral guidelines to reduce common LLM coding mistakes. These apply to ALL code-writing agents.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

### 5. Commit Often

**작업 단위를 작게 유지하고, 자주 커밋한다.**

- 한 커밋에 여러 의도를 섞지 않는다.
- "여기까지 되돌릴 수 있으면 좋겠다" 싶은 지점에서 끊는다.
- 여러 파일을 수정하거나 기능 단위 작업이면 브랜치를 딴다.

> 브랜치명·커밋 메시지·PR 포맷은 git 플러그인 스킬을 따른다:
> `git:branch-name-convention`, `git:commit-message-convention`, `git:pr-convention`

---

*These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.*

---

## Kent Beck Coding Guidelines

> TDD와 Tidy First 원칙. 테스트 주도 개발과 구조/행동 분리를 통해 코드 품질을 유지한다.
> These apply to ALL code-writing agents.

### 1. Red → Green → Refactor

**실패하는 테스트 → 통과시키기 → 정리. 이 순서를 지킨다.**

- 작은 기능 단위로 실패하는 테스트를 먼저 작성한다.
- 테스트를 통과시키는 최소한의 코드만 구현한다.
- 테스트가 통과한 후에만 리팩토링한다.
- 리팩토링 후 반드시 테스트를 다시 돌린다.

### 2. Tidy First

**구조 변경과 행동 변경을 섞지 않는다.**

- 구조 변경 (리네이밍, 메서드 추출, 코드 이동) → 행동은 안 바뀜
- 행동 변경 (기능 추가, 수정) → 구조는 안 바뀜
- 둘 다 필요하면: 구조 먼저, 행동은 그 다음
- 각각 별도 커밋으로 분리한다

### 3. Make It Work, Make It Right, Make It Fast

**동작 → 정리 → 최적화. 순서를 건너뛰지 않는다.**

- 먼저 동작하게 만든다 (simplest thing that works)
- 그 다음 코드를 정리한다 (중복 제거, 의도 드러내기)
- 필요할 때만 최적화한다 (추측으로 최적화하지 않는다)

### 4. Commit Discipline

**테스트가 통과할 때만 커밋한다.**

- 모든 테스트 통과 + 린터 경고 해결 후 커밋
- 한 커밋 = 하나의 논리적 변경 단위
- 커밋 메시지에 구조 변경인지 행동 변경인지 명시

> 브랜치명·커밋 메시지·PR 포맷은 git 플러그인 스킬을 따른다:
> `git:branch-name-convention`, `git:commit-message-convention`, `git:pr-convention`

---

*These guidelines are working if: tests are written before implementation, structural and behavioral changes never appear in the same commit, and "make it work" always precedes "make it right".*

---

## Boris Cherny Coding Guidelines

> 워크플로우 오케스트레이션 원칙. 분할-학습-우아함-자율성을 통해 작업 품질을 높인다.
> Karpathy(코드 품질), Kent Beck(TDD)과 상호보완적으로 적용된다.
> These apply to ALL code-writing agents.

### 1. Divide and Conquer

**복잡한 문제는 분할하여 병렬로 공략한다.**

- 서브에이전트를 적극 활용하여 메인 컨텍스트를 깨끗하게 유지한다.
- 리서치, 탐색, 분석은 서브에이전트에게 위임한다.
- 하나의 서브에이전트 = 하나의 집중된 목표.

### 2. Learn from Every Mistake

**사용자 교정 후 반드시 교훈을 기록한다.**

- 같은 실수를 방지하는 규칙을 스스로 작성한다.
- 실수율이 떨어질 때까지 교훈을 반복 개선한다.
- 세션 시작 시 관련 프로젝트의 교훈을 검토한다.

### 3. Demand Elegance, But Know When to Stop

**비자명한 변경에는 "더 우아한 방법이 있는가?"를 자문한다.**

- 핵이 느껴지면: "지금까지 알게 된 모든 것을 종합해 우아한 해법을 구현한다."
- 단순하고 명백한 수정에는 이 과정을 건너뛴다 — 과잉 설계 금지.
- 제출 전에 자신의 작업에 도전한다.

### 4. Fix Bugs Autonomously

**버그 리포트를 받으면 그냥 고친다. 사용자에게 방법을 묻지 않는다.**

- 로그, 에러, 실패 테스트를 가리키고 — 해결한다.
- 사용자의 컨텍스트 스위칭을 제로로 유지한다.
- CI 실패도 지시 없이 스스로 수정한다.

---

*These guidelines are working if: complex tasks are divided among subagents, mistakes lead to documented lessons, and bugs are fixed autonomously without asking the user how.*
