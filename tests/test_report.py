import json
from pathlib import Path

import pytest

from tvsummary.aggregations import TotalCountAggregation
from tvsummary.errors import OutputError
from tvsummary.models import TVShow
from tvsummary.report import ReportBuilder


def test_report_writes_summary_json(
    tmp_path: Path, sample_records: list[TVShow]
) -> None:
    builder = ReportBuilder([TotalCountAggregation()])
    builder.output_path = tmp_path / "summary.json"

    builder.build_and_write(sample_records)

    written = json.loads((tmp_path / "summary.json").read_text())
    assert written == {"total_shows": 5}


def test_unwritable_output_raises_an_output_error(
    tmp_path: Path, sample_records: list[TVShow]
) -> None:
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("this is a file, so it cannot hold summary.json")
    builder = ReportBuilder([TotalCountAggregation()])
    builder.output_path = blocker / "summary.json"

    with pytest.raises(OutputError, match="Could not write the summary"):
        builder.build_and_write(sample_records)
