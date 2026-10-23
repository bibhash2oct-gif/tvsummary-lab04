"""Builds the summary from the aggregations and writes it as JSON."""

import json
import logging
from collections.abc import Sequence

from .aggregations import Aggregation
from .config import OUTPUT_PATH
from .errors import OutputError
from .models import TVShow

logger = logging.getLogger(__name__)


class ReportBuilder:
    def __init__(self, aggregations: Sequence[Aggregation]) -> None:
        self.aggregations = list(aggregations)
        self.output_path = OUTPUT_PATH

    def build_and_write(self, records: list[TVShow]) -> dict[str, object]:
        summary = {agg.key: agg.compute(records) for agg in self.aggregations}
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
        except OSError as error:
            raise OutputError(
                f"Could not write the summary to {self.output_path}: {error}"
            ) from error
        logger.info("Wrote summary to %s", self.output_path)
        return summary
