"""
detect_stack.py 단위 테스트.
각 stack 시그니처에서 정확한 결과를 반환하는지 검증한다.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import detect_stack as ds


def test_kotlin_gradle_kts(tmp_path):
    (tmp_path / "build.gradle.kts").write_text("plugins {}")
    (tmp_path / "settings.gradle.kts").write_text("")
    result = ds.detect(tmp_path)
    assert result["language"] == "Kotlin"
    assert result["build"] == "gradle"
    assert result["build_cmd"] == "./gradlew build"
    assert result["test_cmd"] == "./gradlew test"


def test_java_gradle_groovy(tmp_path):
    (tmp_path / "build.gradle").write_text("plugins {}")
    result = ds.detect(tmp_path)
    assert result["language"] == "Java"
    assert result["build"] == "gradle"
    assert result["build_cmd"] == "./gradlew build"


def test_java_maven(tmp_path):
    (tmp_path / "pom.xml").write_text("<project/>")
    (tmp_path / "mvnw").write_text("#!/bin/sh")
    result = ds.detect(tmp_path)
    assert result["language"] == "Java"
    assert result["build"] == "maven"
    assert result["build_cmd"] == "./mvnw verify"
    assert result["test_cmd"] == "./mvnw test"


def test_node_npm(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "x"}')
    result = ds.detect(tmp_path)
    assert result["language"] == "Node"
    assert result["build"] == "npm"
    assert result["test_cmd"] == "npm test"


def test_node_pnpm_detected_by_lockfile(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "x"}')
    (tmp_path / "pnpm-lock.yaml").write_text("")
    result = ds.detect(tmp_path)
    assert result["build"] == "pnpm"
    assert result["test_cmd"] == "pnpm test"


def test_node_yarn_detected_by_lockfile(tmp_path):
    (tmp_path / "package.json").write_text('{"name": "x"}')
    (tmp_path / "yarn.lock").write_text("")
    result = ds.detect(tmp_path)
    assert result["build"] == "yarn"
    assert result["test_cmd"] == "yarn test"


def test_python_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'")
    result = ds.detect(tmp_path)
    assert result["language"] == "Python"
    assert result["test_cmd"] == "pytest"


def test_python_requirements(tmp_path):
    (tmp_path / "requirements.txt").write_text("pytest")
    result = ds.detect(tmp_path)
    assert result["language"] == "Python"
    assert result["test_cmd"] == "pytest"


def test_go(tmp_path):
    (tmp_path / "go.mod").write_text("module example.com/x")
    result = ds.detect(tmp_path)
    assert result["language"] == "Go"
    assert result["build_cmd"] == "go build ./..."
    assert result["test_cmd"] == "go test ./..."


def test_unknown_returns_unknown(tmp_path):
    result = ds.detect(tmp_path)
    assert result["language"] == "unknown"
    assert result["build"] == "unknown"
    assert result["build_cmd"] is None
    assert result["test_cmd"] is None


def test_priority_gradle_over_pom(tmp_path):
    """gradle 과 pom.xml 이 둘 다 있으면 gradle 우선."""
    (tmp_path / "build.gradle.kts").write_text("")
    (tmp_path / "pom.xml").write_text("<project/>")
    result = ds.detect(tmp_path)
    assert result["build"] == "gradle"


def test_cli_outputs_json(tmp_path, capsys):
    (tmp_path / "go.mod").write_text("module x")
    ds.main([str(tmp_path)])
    captured = capsys.readouterr()
    import json as _json
    parsed = _json.loads(captured.out)
    assert parsed["language"] == "Go"
