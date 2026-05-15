---
name: init-project
description: Bootstrap a new project with CLAUDE.md, docs/{ARCHITECTURE,ADR,PRD}.md, phases/, and stack auto-detection. Use when user starts a fresh repo, says "프로젝트 초기화", "harness 셋업", "init project", or works in a directory without CLAUDE.md/docs.
argument-hint: "[project-name] [--force]"
---

<Purpose>
새 프로젝트(또는 Harness 미적용 기존 repo)에 Harness 프레임워크를 설치한다.
산출물:
- `CLAUDE.md` (감지된 기술 스택으로 prefilled)
- `docs/{ARCHITECTURE,ADR,PRD}.md` 템플릿
- `phases/index.json` (빈 배열)
</Purpose>

<Use_When>
- 비어있거나 갓 만든 repo
- 기존 repo 인데 CLAUDE.md / docs/ 가 없음
- 사용자: "harness 셋업해줘", "이 프로젝트 초기화", "init project"
</Use_When>

<Do_Not_Use_When>
- 이미 CLAUDE.md 와 docs/ 가 채워져 있는 프로젝트 (덮어쓰면 기존 결정 사라짐)
- 단, `--force` 인자가 주어지면 진행 — 다만 사용자에게 한 번 더 확인
</Do_Not_Use_When>

<Steps>

## 1. 사전 점검

```bash
ls -1 CLAUDE.md docs/ARCHITECTURE.md docs/ADR.md docs/PRD.md 2>/dev/null
```

기존 파일이 있고 `--force` 없으면 **중단**, 사용자에게 어떤 파일이 존재하는지 보여주고 덮어쓸지 묻는다.

## 2. 스택 감지

```bash
python3 scripts/detect_stack.py
```

결과 JSON 예: `{"language": "Kotlin", "build": "gradle", "build_cmd": "./gradlew build", "test_cmd": "./gradlew test"}`

`language == "unknown"` 이면 사용자에게 묻는다 (`AskUserQuestion` 으로 Java/Kotlin/Node/Python/Go/Other).

## 3. 템플릿 복사

플러그인 templates 위치를 찾는다. Claude Code 가 plugin 을 설치한 경로는 다음 우선순위로:

```bash
# 우선순위 1: 이 skill 이 실행되는 plugin 자신의 templates
TEMPLATES_DIR="$(dirname "$0")/templates"
# 그게 없으면 cache 에서 찾기
[ -d "$TEMPLATES_DIR" ] || TEMPLATES_DIR="$HOME/.claude/plugins/cache/bodycodi-harness-marketplace/bodycodi-harness/$(ls -t $HOME/.claude/plugins/cache/bodycodi-harness-marketplace/bodycodi-harness/ | head -1)/skills/init-project/templates"
```

다음 4개를 프로젝트에 복사:
- `CLAUDE.md.tmpl` → `./CLAUDE.md`
- `ARCHITECTURE.md.tmpl` → `./docs/ARCHITECTURE.md`
- `ADR.md.tmpl` → `./docs/ADR.md`
- `PRD.md.tmpl` → `./docs/PRD.md`

`mkdir -p docs phases` 후 복사.

## 4. CLAUDE.md prefill

복사된 `CLAUDE.md` 의 `{프로젝트명}` 토큰을 인자로 받은 `project-name` 으로 치환.
`## 기술 스택` 섹션의 `{예: ...}` placeholder 들을 detect_stack 결과로 채운다:

| 토큰 | 치환 |
|---|---|
| `{예: Spring Boot 3.x}` | `{detect 결과의 추정 framework, 없으면 ?}` |
| `{예: 21}` | `?` (사용자에게 JDK 버전 묻기, Java/Kotlin 일 때만) |
| 빌드 라인 | `./gradlew build` 같은 detect 결과의 `build_cmd` |
| 테스트 라인 | detect 결과의 `test_cmd` |

## 5. phases 초기화

```bash
mkdir -p phases
echo '{"phases": []}' > phases/index.json
```

## 6. 결과 보고

```
✅ Harness 프레임워크 초기화 완료
  - CLAUDE.md (스택: {language} / {build})
  - docs/ARCHITECTURE.md
  - docs/ADR.md
  - docs/PRD.md
  - phases/index.json

다음 단계:
1. docs/ARCHITECTURE.md, ADR.md, PRD.md 의 {placeholder} 들을 프로젝트에 맞게 작성
2. 첫 작업: /bodycodi-harness:start <task-name>
   (요구사항이 흐릿하면: /bodycodi-harness:deep-interview <아이디어>)
```

</Steps>

<Templates_Layout>
이 skill 디렉토리 옆 `templates/` 에 위치:
- `templates/CLAUDE.md.tmpl`
- `templates/ARCHITECTURE.md.tmpl`
- `templates/ADR.md.tmpl`
- `templates/PRD.md.tmpl`

원본은 이 plugin 의 `CLAUDE.md`, `docs/*.md` 와 동일하다.
</Templates_Layout>

<Verification>
- `python3 -c "import json; json.load(open('phases/index.json'))"` 통과
- `grep -q '## 기술 스택' CLAUDE.md && grep -q '레이어 의존성 규칙' docs/ARCHITECTURE.md`
</Verification>

<Do_Not>
- 기존 CLAUDE.md / docs 를 묻지 않고 덮어쓰기
- detect_stack 결과 unknown 인데 임의로 "Spring Boot" 채우기 — 모르면 묻는다 (Deny First)
- placeholder ({…}) 를 가짜 값으로 채우기 — 사용자가 직접 채우도록 그대로 둔다
</Do_Not>
