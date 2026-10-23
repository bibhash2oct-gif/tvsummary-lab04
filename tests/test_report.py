import json
from pathlib import Path

from tvsummary.aggregations import TotalCountAggregation
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
