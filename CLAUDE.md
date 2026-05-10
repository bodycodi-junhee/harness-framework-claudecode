# 프로젝트: {프로젝트명}

## 기술 스택
- 언어: Kotlin / Java
- 빌드: Gradle (`./gradlew`) / Maven (`./mvnw`)
- 프레임워크: {예: Spring Boot 3.x}
- JDK: {예: 21}

## 아키텍처 경계
- CRITICAL: `{패키지/경로}`는 수정 금지 — 이유: {예: 공개 API 계약, 다른 팀 소유}
- CRITICAL: `{파일 경로}`는 읽지도 건드리지도 마라 — 이유: {예: 환경별 시크릿, 운영 설정}
- {레이어 규칙 예: Service는 Repository를 직접 참조하지 않는다. UseCase 인터페이스를 통해서만}

## Deny First 원칙
- 모르는 요구사항은 가정하지 않는다 — 명확하지 않으면 물어라
- 위험한 입력(음수 값, null 필수값, 허용되지 않은 상태)은 허용하지 않는다
- 애매한 정책은 코드 안에 숨기지 않는다 — 명시적으로 드러내라

## 빌드 & 테스트 명령어
```bash
./gradlew build     # 컴파일 + 전체 빌드
./gradlew test      # 단위 테스트
./gradlew check     # lint + test + 정적분석
# Maven: ./mvnw verify
```

## 개발 프로세스
- CRITICAL: 새 기능은 테스트를 먼저 작성하고 통과하는 구현을 작성할 것 (TDD)
- 커밋: conventional commits — `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- 브랜치: `feat-{task-id}` 형식 (예: `feat-CS25-1234`, `feat-DEV25-5678`)

## 전체 문서
- 아키텍처: `/docs/ARCHITECTURE.md`
- 설계 결정: `/docs/ADR.md`
- 기획: `/docs/PRD.md`

## 로컬 전용 설정
개인 환경·실험적 지침은 `CLAUDE.local.md`에 기록 (git 추적 제외).
