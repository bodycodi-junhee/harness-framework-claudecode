---
name: start
description: Start a Harness phased TDD workflow — explore docs, design steps, generate phases/{task}/index.json and step{N}.md, then run via execute.py. Use when user starts a new feature/task with a ticket id (CS25-*, DEV25-*) or says "harness 시작", "작업 시작".
argument-hint: "<task-name>"
pipeline: [deep-interview, start]
---

<Purpose>
Harness 5단계 워크플로우(Explore → Brainstorm → Plan → Implement → Verify)를 시작한다.
산출물: `phases/{task}/index.json` + `phases/{task}/step{N}.md` 들.
실제 step 실행은 `python3 scripts/execute.py {task}` 가 담당한다.
</Purpose>

<Use_When>
- 새 기능 구현, 기존 코드 큰 수정, refactor 시작
- 사용자가 `feat-CS25-1234`, `feat-DEV25-5678` 같은 티켓 기반 작업을 요청
- "harness 시작", "step 설계해줘", "작업 시작" 류 트리거
</Use_When>

<Do_Not_Use_When>
- 단순 오타·작은 설정 변경·테스트 보강 등 1회성 수정 (직접 수정으로 충분)
- 요구사항이 흐릿한 경우 — 먼저 `/bodycodi-harness:deep-interview` 로 spec 확정 후 호출
</Do_Not_Use_When>

<Steps>

## 0단계: 요구사항 명확화 체크

다음 중 하나라도 해당하면 **먼저 `/bodycodi-harness:deep-interview` 호출 후 그 산출물(`phases/{slug}/_spec.md`)을 가지고 1단계로**:
- 목표가 흐릿하다 ("이거 개선해줘" 수준)
- 범위를 확신할 수 없다
- 완료 기준이 없다
- 여러 도메인/서비스에 걸쳐 있다

명확하면 1단계로 직진.

## 1단계: 스택 감지

```bash
python3 scripts/detect_stack.py
```
결과의 `build_cmd`, `test_cmd` 를 step{N}.md 의 Acceptance Criteria 에 사용한다.

## 2단계: 탐색 (A)

`/docs/` 하위 문서(PRD, ARCHITECTURE, ADR) 를 읽고 프로젝트 기획·아키텍처·설계 의도를 파악한다.
범위가 넓으면 Explore 에이전트를 병렬로 사용.

## 3단계: 논의 (B)

기술적으로 결정이 필요한 사항은 사용자에게 제시하고 합의를 얻는다.
Plan-First 발동 신호 3가지 중 하나라도 해당하면 코드 들어가기 전에 계획만 먼저 확정한다:
1. 영향 범위 확신 못함
2. 여러 디렉토리/서비스/모듈 얽힘
3. 레거시라 연쇄 영향 위험

## 4단계: Step 설계 (C)

설계 원칙:
1. **Scope 최소화** — 한 step = 한 레이어/모듈
2. **자기완결성** — 각 step.md 는 독립 세션에서 실행됨. "이전 대화에서…" 같은 외부 참조 금지
3. **사전 준비 강제** — 읽어야 할 파일 경로 명시
4. **시그니처 수준 지시** — 인터페이스만, 내부 구현은 에이전트 재량. 단, Deny First / 멱등성 / 보안은 명시
5. **AC 는 실행 가능한 커맨드** — 1단계의 `build_cmd && test_cmd` 사용
6. **주의사항은 구체적으로** — "X 하지 마라. 이유: Y" 형식
7. **네이밍** — kebab-case slug (`domain-model`, `service-layer`, `api-controller`)
8. **불명확 시 인터뷰 우선** — 신규 기능에서 잘 모르거나 설명이 부족한 부분은 임의로 구현하지 않는다. 해당 부분을 인터뷰 형식으로 먼저 물어보고 답변을 받은 뒤 작업한다

## 5단계: 파일 생성 (D)

사용자 승인 후, 아래 3가지 파일을 생성한다.

### D-1. `phases/index.json` (top-level, 없으면 신규)
```json
{
  "phases": [
    { "dir": "{task-name}", "status": "pending" }
  ]
}
```
이미 존재하면 새 항목 append.

### D-2. `phases/{task-name}/index.json`
```json
{
  "project": "<프로젝트명 from CLAUDE.md>",
  "phase": "<task-name>",
  "steps": [
    { "step": 0, "name": "domain-model", "status": "pending" },
    { "step": 1, "name": "service-layer", "status": "pending" }
  ]
}
```

상태 전이와 자동 기록 필드 (execute.py 가 채움):
| 전이 | 기록되는 필드 |
|---|---|
| → completed | `completed_at`, `summary` |
| → error | `failed_at`, `error_message` |
| → blocked | `blocked_at`, `blocked_reason` |

`created_at`, `started_at` 은 execute.py 가 자동 기록 — 생성 시 넣지 않음.

### D-3. `phases/{task-name}/step{N}.md` (각 step 1개)

템플릿:
```markdown
# Step {N}: {이름}

## 읽어야 할 파일
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`
- {이전 step 산출 파일}

## Context Harness
- **Input**: {입력값, 타입, 범위}
- **Output**: {출력 형식, 불가 값}
- **제약**: {깨지면 안 되는 불변 조건}
- **변경가능성**: {정책적 변경 부분}

## 작업
{구체 지시. 파일 경로, 시그니처, 로직. 핵심 규칙(Deny First / 멱등성 / 보안)은 명확히}

## Acceptance Criteria
```bash
{build_cmd}
{test_cmd}
```

## 검증 절차
1. AC 커맨드 실행
2. Verification 5레이어 확인 (타입/입력/정책/결과/테스트)
3. 아키텍처 체크리스트 (레이어, 스택, CRITICAL 준수)
4. 상태 업데이트:
   - 성공 → `"status": "completed"`, `"summary": "산출물 한 줄"`
   - 3회 재시도 후 실패 → `"status": "error"`, `"error_message"`
   - 사용자 개입 필요 → `"status": "blocked"`, `"blocked_reason"` 후 중단

## 수정 가능 범위
- {파일/패키지 목록}

## 수정 금지 범위
- {절대 건드리지 말 것 + 이유: Y}

## 금지사항
- {"X 하지 마라. 이유: Y" 형식}
- 신규 기능 중 명확하지 않거나 설명이 부족한 부분을 임의로 구현하지 마라. 이유: 잘못된 가정은 설계 의도와 어긋나 전체 phase 를 오염시킴. 반드시 인터뷰 형식으로 사용자에게 확인 후 작업한다
```

## 6단계: 실행 (E)

```bash
python3 scripts/execute.py {task-name}        # 순차 실행
python3 scripts/execute.py {task-name} --push  # 실행 후 push
```

execute.py 자동 처리:
- `feat-{task-name}` 브랜치 생성/checkout
- 가드레일 주입 (CLAUDE.md + docs/*.md 매 step 프롬프트에)
- 컨텍스트 누적 (이전 step summary 다음에 전달)
- 자가 교정 (실패 시 최대 3회 재시도)
- 2단계 커밋 (feat 코드 + chore 메타)
- 타임스탬프 자동 기록
- `HARNESS_AUTOMATED=1` 주입 (Stop hook 중복 방지)

에러 복구:
- **error**: `index.json` 의 해당 step `status` 를 `"pending"`, `error_message` 삭제 후 재실행
- **blocked**: `blocked_reason` 해결 후 `status` `"pending"`, `blocked_reason` 삭제 후 재실행

</Steps>

<Verification>
- `phases/{task}/index.json` 이 valid JSON 으로 파싱되는가?
- 각 step{N}.md 가 7가지 설계 원칙(Scope/자기완결성/사전준비/시그니처/AC/주의사항/네이밍) 을 모두 만족하는가?
- AC 의 빌드 명령이 detect_stack 결과와 일치하는가?
</Verification>
