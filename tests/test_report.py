import json
from importlib import metadata
from pathlib import Path

import pytest

from tvsummary.aggregations import FeaturedShowsAggregation, TotalCountAggregation
from tvsummary.config import Settings
from tvsummary.errors import OutputError
from tvsummary.models import TVShow
from tvsummary.report import ReportBuilder, build_run_info


def test_report_writes_summary_json(
    tmp_path: Path, sample_records: list[TVShow]
) -> None:
    builder = ReportBuilder(
        [TotalCountAggregation(), FeaturedShowsAggregation(seed=1, sample_size=2)],
        output_dir=tmp_path,
    )

    builder.build_and_write(sample_records)

    written = json.loads((tmp_path / "summary.json").read_text())
    assert list(written) == ["total_shows", "featured_shows"]
    assert written["total_shows"] == 5
    assert len(written["featured_shows"]) == 2


def test_unwritable_output_raises_an_output_error(
    tmp_path: Path, sample_records: list[TVShow]
) -> None:
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("this is a file, so it cannot hold summary.json")
    builder = ReportBuilder([TotalCountAggregation()], output_dir=blocker)

    with pytest.raises(OutputError, match="Could not write"):
        builder.build_and_write(sample_records)


def test_run_info_records_settings_python_and_tool_versions(
    settings: Settings,
) -> None:
    builder = ReportBuilder([TotalCountAggregation()], output_dir=settings.output_dir)

    builder.write_run_info(settings)

    run_info = json.loads((settings.output_dir / "run_info.json").read_text())
    assert run_info["settings"] == settings.as_dict()
    assert run_info["settings"]["seed"] == 5005
    assert run_info["python_version"].count(".") == 2
    assert set(run_info["tool_versions"]) == {"pytest", "mypy", "ruff"}
    assert run_info["tool_versions"]["pytest"] == metadata.version("pytest")


def test_run_info_marks_a_missing_tool(
    settings: Settings, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_such_tool(name: str) -> str:
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(metadata, "version", no_such_tool)

    run_info = build_run_info(settings)

    assert run_info["tool_versions"] == {
        "pytest": "not installed",
        "mypy": "not installed",
        "ruff": "not installed",
    }
