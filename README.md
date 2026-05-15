# bodycodi-harness

Claude Code 용 phased TDD 워크플로우 플러그인. 흐릿한 아이디어를 명확한 spec 으로 만들고 → step 단위로 자동 실행하고 → Harness 10원칙으로 리뷰까지 한 흐름으로 묶는다.

## 무엇을 제공하나

| Skill | 호출 | 역할 |
|---|---|---|
| `deep-interview` | `/bodycodi-harness:deep-interview <아이디어>` | Socratic 질문으로 모호한 요구사항을 명확한 spec 으로 결정화. `phases/{slug}/_spec.md` 생성 |
| `start` | `/bodycodi-harness:start <task-name>` | Harness 5단계(Explore → Brainstorm → Plan → Implement → Verify) 시작. `phases/{task}/index.json` + `step{N}.md` 생성 |
| `review` | `/bodycodi-harness:review` | 변경 사항을 ARCHITECTURE / ADR / Deny First 기준 10개 항목으로 검증 |
| `init-project` | `/bodycodi-harness:init-project <project-name>` | 새 프로젝트에 CLAUDE.md / docs / phases 초기화 (언어/빌드툴 자동 감지) |

## 설치 (로컬)

이 repo 자체가 Claude Code plugin 이다. Claude Code 안에서:

```
/plugin marketplace add /Users/ijunhui/bodycodi/tech/harness-framework-claudecode
/plugin install bodycodi-harness@bodycodi-harness-marketplace
```

설치 후 다른 프로젝트 디렉토리에서도 `/bodycodi-harness:*` 호출 가능.

## 권장 사용 흐름

```
[흐릿한 아이디어]
        │
        ▼
/bodycodi-harness:deep-interview "결제 환불 정책 정리"
        │  → phases/refund-policy-cleanup/_spec.md 생성
        ▼
/bodycodi-harness:start refund-policy-cleanup
        │  → phases/refund-policy-cleanup/index.json + step{N}.md 생성
        ▼
python3 scripts/execute.py refund-policy-cleanup
        │  → step 들 순차 자동 실행, branch/commit/타임스탬프 자동 관리
        ▼
/bodycodi-harness:review
        │  → 10개 체크리스트 ✅/❌ 표 출력
        ▼
PR / merge
```

## 다른 프로젝트에서 처음 쓸 때

```
/bodycodi-harness:init-project my-new-service
```

비어있는 프로젝트에 다음을 생성:
- `CLAUDE.md` (감지된 stack 으로 prefilled)
- `docs/ARCHITECTURE.md`, `docs/ADR.md`, `docs/PRD.md` (템플릿)
- `phases/index.json` (빈 배열)

이후 docs/*.md 의 `{placeholder}` 를 프로젝트에 맞게 채우면 준비 완료.

## 디렉토리 구조

```
harness-framework-claudecode/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── deep-interview/SKILL.md
│   ├── start/SKILL.md
│   ├── review/SKILL.md
│   └── init-project/
│       ├── SKILL.md
│       └── templates/
├── scripts/
│   ├── execute.py            # step 자동 실행 엔진 (기존)
│   └── detect_stack.py       # 언어/빌드툴 자동 감지
└── .claude/commands/         # 기존 /harness, /review (호환 유지, deprecated)
```

## 기존 명령어와의 관계

| 기존 (v0) | 신규 (v1, plugin) | 상태 |
|---|---|---|
| `/harness` | `/bodycodi-harness:start` | v1 까지 공존, 이후 제거 예정 |
| `/review` | `/bodycodi-harness:review` | 동일 |
| (없음) | `/bodycodi-harness:deep-interview` | 신규 |
| (없음) | `/bodycodi-harness:init-project` | 신규 |

데이터 호환: 둘 다 동일한 `phases/`, `docs/` 구조를 쓰므로 섞어 써도 안전.

## 개발

- 매니페스트 검증: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"`
- detect_stack 테스트: `python3 -m pytest scripts/test_detect_stack.py -v`
- execute.py 테스트: `python3 -m pytest scripts/test_execute.py -v`

## 향후 (v2 이상)

- pipeline auto-dispatch (deep-interview 끝나면 start 자동 실행)
- GitHub marketplace 공개
- 추가 skill: changelog, release-notes, post-incident-review 등

## 라이센스

MIT
