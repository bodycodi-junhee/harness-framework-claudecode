# 아키텍처

## 디렉토리 구조

```
src/
├── main/
│   ├── kotlin/                          # (또는 java/)
│   │   └── com.example.{app}/
│   │       ├── domain/                  # 핵심 도메인 모델 & 비즈니스 규칙
│   │       ├── application/             # Use Case (서비스 레이어)
│   │       ├── infrastructure/          # DB, 외부 API, 메시지큐 구현체
│   │       └── presentation/            # Controller, DTO, Request/Response
│   └── resources/
│       ├── application.yml
│       └── application-{env}.yml        # 환경별 설정 — 직접 수정 금지
└── test/
    └── kotlin/                          # (또는 java/)
        └── com.example.{app}/
            ├── unit/                    # 단위 테스트
            └── integration/             # 통합 테스트
```

## 레이어 의존성 규칙

```
Presentation → Application → Domain
Infrastructure → Domain    (역방향 의존성 금지)
```

- `domain`은 외부 프레임워크(Spring, JPA 등) 의존성을 갖지 않는다
- `application`은 `infrastructure` 구현체를 직접 참조하지 않는다 — 인터페이스(Port)를 통해서만
- `presentation`은 도메인 객체를 직접 반환하지 않는다 — DTO로 변환 후 반환

## 패턴

{사용하는 설계 패턴 예시}
- Repository 패턴: 데이터 접근 추상화
- {기타 패턴}

## 데이터 흐름

```
HTTP Request
  → Presentation   (Controller: Request 파싱 → Command/Query 변환)
  → Application    (UseCase: 비즈니스 흐름 조율)
  → Domain         (Entity/Service: 핵심 비즈니스 규칙 실행)
  → Infrastructure (Repository/Adapter: DB/외부 API 처리)
  → 응답 반환      (DTO 변환 → HTTP Response)
```

## 에이전트 친화적 코드베이스 기준

Claude가 이 코드베이스에서 올바르게 작업하려면 아래 조건이 충족되어야 한다.
이 기준이 약하면 Claude가 잘못된 이해를 바탕으로 수정하고, 그 수정이 새로운 오류를 만드는 악순환이 생긴다.

1. **테스트 커버리지**: 핵심 비즈니스 로직은 단위 테스트로 보호되어야 한다
2. **문서-코드 일관성**: `docs/`의 내용이 실제 코드 구조와 어긋나지 않아야 한다
3. **설계 패턴 일관성**: 동일한 문제에는 프로젝트 전체에서 동일한 패턴을 사용한다
4. **빌드/실행 명확성**: `./gradlew build && ./gradlew test` 두 명령으로 언제나 검증 가능해야 한다
5. **스타일 안정성**: 코딩 컨벤션과 패키지 구조 규칙이 세션마다 흔들리면 안 된다
