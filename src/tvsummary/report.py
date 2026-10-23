"""Builds the summary and run information, and writes them as JSON."""

import json
import logging
import platform
from collections.abc import Sequence
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

from .aggregations import Aggregation
from .config import Settings
from .errors import OutputError
from .models import TVShow

logger = logging.getLogger(__name__)

CHECK_TOOLS = ("pytest", "mypy", "ruff")


class ReportBuilder:
    """Runs each aggregation and writes summary.json to output_dir."""

    def __init__(self, aggregations: Sequence[Aggregation], output_dir: Path) -> None:
        self.aggregations = list(aggregations)
        self.output_dir = output_dir

    @property
    def summary_path(self) -> Path:
        return self.output_dir / "summary.json"

    @property
    def run_info_path(self) -> Path:
        return self.output_dir / "run_info.json"

    def build(self, records: list[TVShow]) -> dict[str, object]:
        return {agg.key: agg.compute(records) for agg in self.aggregations}

    def build_and_write(self, records: list[TVShow]) -> dict[str, object]:
        summary = self.build(records)
        write_json(self.summary_path, summary)
        logger.info("Wrote summary to %s", self.summary_path)
        return summary

    def write_run_info(self, settings: Settings) -> dict[str, object]:
        run_info = build_run_info(settings)
        write_json(self.run_info_path, run_info)
        logger.info("Wrote run information to %s", self.run_info_path)
        return run_info


def build_run_info(settings: Settings) -> dict[str, object]:
    """Everything a classmate needs to repeat this run."""
    return {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "python_version": platform.python_version(),
        "package_version": _installed_version("tvsummary"),
        "tool_versions": {tool: _installed_version(tool) for tool in CHECK_TOOLS},
        "settings": settings.as_dict(),
    }


def write_json(path: Path, data: dict[str, object]) -> None:
    """Write data as indented JSON, creating the folder if needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
    except OSError as error:
        raise OutputError(f"Could not write {path}: {error}") from error


def _installed_version(distribution: str) -> str:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return "not installed"
