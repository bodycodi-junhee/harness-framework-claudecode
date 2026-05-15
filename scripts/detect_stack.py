"""
프로젝트 루트의 시그니처 파일을 보고 언어/빌드툴을 감지한다.

CLI: python3 scripts/detect_stack.py [project_root]
출력: 한 줄 JSON {"language", "build", "build_cmd", "test_cmd"}
"""

import json
import sys
from pathlib import Path
from typing import Optional, TypedDict


class Stack(TypedDict):
    language: str
    build: str
    build_cmd: Optional[str]
    test_cmd: Optional[str]


UNKNOWN: Stack = {
    "language": "unknown",
    "build": "unknown",
    "build_cmd": None,
    "test_cmd": None,
}


def _detect_node(root: Path) -> Stack:
    if (root / "pnpm-lock.yaml").exists():
        manager = "pnpm"
    elif (root / "yarn.lock").exists():
        manager = "yarn"
    else:
        manager = "npm"
    return {
        "language": "Node",
        "build": manager,
        "build_cmd": f"{manager} run build",
        "test_cmd": f"{manager} test",
    }


def detect(root: Path) -> Stack:
    """루트 경로의 파일 시그니처로 stack 을 감지한다.

    우선순위: gradle > maven > node > python > go.
    근거: 한 repo 에 여러 시그니처가 공존할 때 JVM/Node 쪽이 주 빌드인 경우가 많고,
    Python/Go 는 보조 스크립트로 섞여 있을 가능성이 더 높다.
    """
    if (root / "build.gradle.kts").exists():
        return {
            "language": "Kotlin",
            "build": "gradle",
            "build_cmd": "./gradlew build",
            "test_cmd": "./gradlew test",
        }
    if (root / "build.gradle").exists():
        return {
            "language": "Java",
            "build": "gradle",
            "build_cmd": "./gradlew build",
            "test_cmd": "./gradlew test",
        }
    if (root / "pom.xml").exists():
        return {
            "language": "Java",
            "build": "maven",
            "build_cmd": "./mvnw verify",
            "test_cmd": "./mvnw test",
        }
    if (root / "package.json").exists():
        return _detect_node(root)
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        return {
            "language": "Python",
            "build": "pip",
            "build_cmd": None,
            "test_cmd": "pytest",
        }
    if (root / "go.mod").exists():
        return {
            "language": "Go",
            "build": "go",
            "build_cmd": "go build ./...",
            "test_cmd": "go test ./...",
        }
    return UNKNOWN.copy()


def main(argv: list[str]) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    print(json.dumps(detect(root), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
