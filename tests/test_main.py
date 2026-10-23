import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import requests

from tvsummary import sources
from tvsummary.main import main


def _error_lines(stderr: str) -> list[str]:
    return [line for line in stderr.splitlines() if line.startswith("Error:")]


def test_main_with_a_missing_settings_file_fails_cleanly(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["--config", str(tmp_path / "missing.toml")])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert _error_lines(captured.err) == [
        f"Error: Settings file not found: {tmp_path / 'missing.toml'}"
    ]
    assert captured.err.splitlines()[-1].startswith("Error:")
    assert "Traceback" not in captured.err


def test_main_with_a_failed_download_returns_1(
    settings_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> Any:
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(sources.requests, "get", fake_get)

    exit_code = main(["--config", str(settings_file)])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert _error_lines(captured.err) == [
        "Error: Could not reach https://example.invalid/shows. "
        "Check your internet connection."
    ]
    assert "Traceback" not in captured.err
    assert [r.levelname for r in caplog.records if r.levelname == "ERROR"] == ["ERROR"]
    assert not (tmp_path / "processed" / "summary.json").exists()


def test_main_with_a_bad_response_shape_returns_1(
    settings_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_response_class: type,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> Any:
        return fake_response_class({"message": "not a list"})

    monkeypatch.setattr(sources.requests, "get", fake_get)

    assert main(["--config", str(settings_file)]) == 1
    errors = _error_lines(capsys.readouterr().err)
    assert len(errors) == 1
    assert errors[0].startswith("Error: Expected a list of shows")


def test_main_success_writes_both_files_and_returns_0(
    settings_file: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    fake_response_class: type,
    raw_shows: list[dict[str, Any]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> Any:
        return fake_response_class(raw_shows)

    monkeypatch.setattr(sources.requests, "get", fake_get)

    first_code = main(["--config", str(settings_file)])
    first = json.loads((tmp_path / "processed" / "summary.json").read_text())
    second_code = main(["--config", str(settings_file)])
    second = json.loads((tmp_path / "processed" / "summary.json").read_text())

    captured = capsys.readouterr()
    assert (first_code, second_code) == (0, 0)
    assert list(first) == ["total_shows", "featured_shows"]
    assert first["total_shows"] == 5
    assert len(first["featured_shows"]) == 3
    assert first == second
    assert (tmp_path / "processed" / "run_info.json").exists()
    assert captured.out.startswith("Summary written to")
    assert _error_lines(captured.err) == []


def test_python_dash_m_runs_the_entry_point(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tvsummary.main",
            "--config",
            str(tmp_path / "missing.toml"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert result.stderr.splitlines()[-1].startswith("Error: Settings file not found")
    assert "Traceback" not in result.stderr
