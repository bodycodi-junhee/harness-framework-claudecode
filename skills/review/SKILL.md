---
name: review
description: 10-point Harness code review against ARCHITECTURE / ADR / Deny First. Use when user finishes implementation, wants change verification, or asks "리뷰", "review my changes".
argument-hint: "[optional: branch or path scope]"
---

<Purpose>
이 프로젝트의 변경 사항을 Harness 원칙에 따라 10개 항목으로 정량 검증한다.
출력은 표 형식의 체크리스트와 위반 시 구체적인 수정 방안이다.
</Purpose>

<Use_When>
- 사용자가 "리뷰해줘", "변경사항 점검", "review", "코드 검증" 등을 요청
- 구현 완료 후 PR/커밋 직전
- Harness step 의 검증 절차로
</Use_When>

<Steps>

## 1단계: 문서 읽기

먼저 다음 문서들을 읽어 프로젝트의 설계 의도를 확보한다:
- `/CLAUDE.md`
- `/docs/ARCHITECTURE.md`
- `/docs/ADR.md`

## 2단계: 빌드/테스트 명령 감지

```bash
python3 scripts/detect_stack.py
```
출력 JSON 의 `build_cmd`, `test_cmd` 를 이후 9번 체크리스트에서 사용한다.
스크립트가 없거나 `unknown` 이면 CLAUDE.md 의 명령 그대로 사용.

## 3단계: 변경 파일 확인 및 10개 체크리스트 검증

```bash
git status
git diff --stat
```

1. **아키텍처 준수**: ARCHITECTURE.md 디렉토리 구조와 레이어 의존성 규칙(Presentation → Application → Domain; Infrastructure → Domain)을 따르는가?
2. **기술 스택 준수**: ADR 선택을 벗어나지 않았는가?
3. **수정 범위**: 요구사항 범위에 맞는가? 건드리면 안 되는 파일(`.env`, GitHub workflows, public API 등) 미터치인가?
4. **Deny First 준수**: 모르는 요구사항 가정하지 않았는가? 위험 입력 거부하는가? 모호한 정책 코드에 숨기지 않았는가?
5. **CRITICAL 규칙**: CLAUDE.md CRITICAL 규칙 위반 없는가?
6. **검증 5레이어**:
   - 타입 제한
   - 입력값 검증 (음수·null·경계값)
   - 정책 검증 (할인·수수료·조건)
   - 결과 검증 (제약 만족)
   - 테스트 (happy + edge + invalid)
7. **테스트 존재**: 단위 + 통합 테스트 작성?
8. **검증 비어있음 금지**: "완료"인데 실제 빌드/테스트 검증 누락은 아닌가?
9. **빌드 가능**: 2단계에서 감지한 `build_cmd && test_cmd` 가 통과하는가?
10. **민감정보 노출 금지**: 비밀키, API Key, DB 접속정보, PII 가 코드/로그에 포함되지 않았는가?

## 4단계: Skills vs Tools 판단

리뷰 중 반복 패턴이 보이면:

| 상황 | 판단 |
|------|------|
| 같은 절차 3회 이상 반복 설명 | Skills 후보 |
| 외부 시스템 호출 필요 | Tools/MCP 후보 |
| 절차 표준화 필요, 외부 연결 불필요 | Skills |
| Claude가 절차는 알지만 실행 능력 없음 | Tools |

</Steps>

<Output_Format>

| 항목 | 결과 | 비고 |
|------|------|------|
| 아키텍처 준수 | ✅/❌ | {상세} |
| 기술 스택 준수 | ✅/❌ | {상세} |
| 수정 범위 | ✅/❌ | {상세} |
| Deny First 준수 | ✅/❌ | {상세} |
| CRITICAL 규칙 | ✅/❌ | {상세} |
| 검증 5개 레이어 | ✅/❌ | {상세} |
| 테스트 존재 | ✅/❌ | {상세} |
| 검증 비어있음 금지 | ✅/❌ | {상세} |
| 빌드 가능 | ✅/❌ | {상세} |
| 민감정보 노출 금지 | ✅/❌ | {상세} |

위반 사항이 있으면 수정 방안을 구체적으로 제시한다.

</Output_Format>

<Do_Not>
- 단순 "괜찮아 보입니다" 같은 모호한 평가
- 모든 항목 ✅ 라고 우선 적고 나중에 검증 — 항상 검증 후 마킹
- `git diff` 안 읽고 추측으로 평가
</Do_Not>
