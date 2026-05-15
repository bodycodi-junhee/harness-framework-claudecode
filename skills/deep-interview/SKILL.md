---
name: deep-interview
description: Socratic deep interview with ambiguity gating — turns vague ideas into a Harness-ready spec (Input/Output/제약/변경가능성 4요소). Use when user says "deep interview", "요구사항 명확화", "interview me", "이거 좀 더 좋게 만들어줘" 류 흐릿한 요청, or before starting Harness on an unclear task.
argument-hint: "[--quick|--standard|--deep] <vague idea>"
pipeline: [deep-interview, start]
next-skill: start
handoff: phases/{slug}/_spec.md
---

<Purpose>
사용자의 흐릿한 아이디어를 Socratic 질문을 통해 명확한 요구사항으로 결정화한다.
산출물은 `phases/{slug}/_spec.md` 한 개의 파일이며, 이는 곧 `bodycodi-harness:start` 가 step 분해에 그대로 사용한다.

흐릿한 상태에서 바로 코드로 들어갈 때 생기는 "이거 내가 원한 게 아닌데" 비용을 사전에 차단한다.
</Purpose>

<Use_When>
- 사용자 발화에 다음 키워드: "deep interview", "interview me", "요구사항 명확화", "ouroboros", "ask me everything"
- 사용자의 요청이 모호함: "이거 개선해줘", "더 좋게", "정리해줘"
- 범위·완료기준이 분명하지 않음
- 여러 도메인/서비스를 가로지르는 작업
- 사용자가 명시적으로 `/bodycodi-harness:deep-interview <아이디어>` 호출
</Use_When>

<Do_Not_Use_When>
- 단일 오타 수정, 함수명 변경 같은 1줄 작업
- 사용자가 이미 step 단위로 구체화한 요구사항을 줬을 때
- 사용자가 "그냥 빨리 해줘" 명시적 요청 — 이때는 한 번 경고만 하고 패스
</Do_Not_Use_When>

<Why_This_Exists>
OMC 의 `/oh-my-claudecode:deep-interview` 컨셉을 Harness 워크플로우에 통합한 버전이다.
원본은 ambiguity scoring 으로 자동 게이팅하지만, 이 버전은 4가지 Harness 차원(Input / Output / 제약 / 변경가능성) 의 명시성을 기준으로 한다.
</Why_This_Exists>

<Steps>

## Phase 1: Initialize

### 1.1 모드 결정
인자에서 모드 추출 (기본: `--standard`):
- `--quick`: 5~7개 질문, 가장 큰 모호성만
- `--standard`: 10~15개, 4차원 골고루
- `--deep`: 무제한, 모호성이 임계 아래로 떨어질 때까지

### 1.2 슬러그 생성
사용자 아이디어 → `kebab-case-slug` (예: "결제 환불 정책 정리" → `refund-policy-cleanup`).
TodoWrite/TaskCreate 로 5개 phase 작업을 등록한다.

### 1.3 베이스라인 모호성 평가

4차원으로 0~10 점수 (10이 가장 모호):
| 차원 | 질문 |
|---|---|
| Input | 입력값의 타입·출처·범위·필수성이 명확한가? |
| Output | 출력 형식·허용범위·금지값(예: 음수)이 명확한가? |
| 제약 | 깨지면 안 되는 불변 조건이 명시되어 있는가? |
| 변경가능성 | 정책적으로 바뀔 부분이 식별되어 있는가? |

각 차원 점수와 합계 (0~40) 를 사용자에게 보여주고 "이 정도면 충분히 흐릿하니 인터뷰 진행"임을 알린다.

## Phase 2: Interview Loop

`AskUserQuestion` 도구를 활용하되, 한 번에 1~3개 질문을 묶고 multiSelect 가능한 옵션을 우선 제시한다. 자유 응답은 "Other" 로.

질문 우선순위:
1. **가장 모호한 차원부터** (점수 높은 순)
2. 차원 안에서는 가장 **결정의존성이 높은 것**부터
3. 한 차원이 ≤ 2점으로 떨어지면 다음 차원으로

각 응답 후:
- 그 차원 점수를 재평가
- 총합이 임계 아래로 떨어졌는지 확인:
  - quick: ≤ 16
  - standard: ≤ 12
  - deep: ≤ 8
- 임계 미달이면 Phase 3 으로

## Phase 3: Challenge

사용자 응답을 그대로 받아들이지 않는다. 답변 안에 모순/공백이 있으면 짚어낸다.

확인할 패턴:
- Input 답변과 제약 답변이 충돌 (예: "음수 허용" + "결과는 항상 양수")
- 변경가능성 답변에 정책 변경 channel 부재 (어떻게 정책이 바뀔지 절차가 없음)
- Output 의 happy path 만 정의, edge case 미정의

발견 시 후속 질문 1~2개. 모두 해결되면 Phase 4.

## Phase 4: Crystallize Spec

`phases/{slug}/_spec.md` 를 생성한다. 템플릿:

```markdown
# Spec: {한 줄 요약}

생성: deep-interview (`{mode}`), 슬러그: `{slug}`

## 목표
{문제 해결 1~2문장}

## 사용자/이해관계자
{누가 영향 받는지}

## Context Harness 4요소

### Input
- 타입: {…}
- 출처: {…}
- 허용 범위: {…}
- 필수성: {…}

### Output
- 형식: {…}
- 허용 범위: {…}
- 금지 값: {예: 음수 불가, null 불가}

### 제약 (불변 조건)
1. {…}
2. {…}

### 변경가능성 (정책적으로 바뀔 부분)
1. {…} — 어떻게/누가 바꾸는가: {channel}
2. {…}

## 완료 기준 (DoD)
- [ ] {검증 가능한 조건 1}
- [ ] {검증 가능한 조건 2}

## 범위 (Scope)
**포함**: {…}
**제외 (MVP 안 함)**: {…}

## 위험 / 미해결 질문
- {남은 불확실성}

## Step 분해 시드 (start skill 가 이걸로 step 만든다)
1. {step 0 후보} — 입출력 한 줄
2. {step 1 후보}
3. {step 2 후보}
```

## Phase 5: Handoff

화면에:
1. spec 파일 경로 출력
2. 사용자에게 검토 요청 ("이대로 step 만들까요?")
3. 승인 시 다음 명령 안내:
   ```
   /bodycodi-harness:start {slug}
   ```
   (`start` skill 이 이 spec 의 "Step 분해 시드" 를 읽고 step{N}.md 들을 생성)

</Steps>

<Tool_Usage>
- `AskUserQuestion`: 모든 질문은 이걸로. 한 번에 1~3개 묶기
- `Write`: `phases/{slug}/_spec.md` 생성
- `Bash` (`mkdir -p phases/{slug}`): 디렉토리 준비
- `Skill("bodycodi-harness:start", ...)`: 사용자가 승인 시 다음 skill 호출 (자동 dispatch 는 v2 이후, 일단 안내만)
</Tool_Usage>

<Examples>

### Good
> "결제 환불 정책 정리"
1. 슬러그: `refund-policy-cleanup`
2. 베이스라인: Input 7 / Output 6 / 제약 8 / 변경가능성 9 = 30 (standard 임계 12 까지)
3. 우선 변경가능성부터 질문 ("환불 정책이 무엇으로 트리거되어 바뀌나요?")
4. 4~5 라운드 후 임계 미달 → spec 작성 → "/bodycodi-harness:start refund-policy-cleanup" 안내

### Bad
- 사용자가 "버튼 색깔만 빨강으로 바꿔줘" 라고 했는데 deep-interview 발동 → 과잉. 이 skill 안 써야 함
- 첫 라운드부터 모든 차원 4개를 동시에 물어봄 → 인지 부담. 모호한 차원부터 순차 진행
- spec 에 "Output: 적절히" 같은 모호어 → 모호성 미해결, Challenge 단계로 돌아가야 함

</Examples>

<Stop_Conditions>
- 사용자가 "그만, 그냥 시작하자" → Phase 4 로 점프해서 현재까지의 답변만으로 spec 작성, 남은 불확실성은 "위험" 섹션에 명시
- 사용자가 3번 연속 "모르겠다" → 그 차원을 변경가능성 으로 분류하고 다음 차원으로
- 임계 미달이면 즉시 종료, 더 캐묻지 않음
</Stop_Conditions>

<Final_Checklist>
- [ ] `phases/{slug}/_spec.md` 가 위 템플릿 모든 섹션 채워졌음
- [ ] 4차원 모두 점수 ≤ 임계 (또는 미달 사유가 위험 섹션에 명시)
- [ ] "Step 분해 시드" 가 ≥ 2개 항목, 각 항목이 입출력 한 줄로 표현됨
- [ ] 사용자에게 다음 호출 명령 (`/bodycodi-harness:start {slug}`) 안내됨
</Final_Checklist>
