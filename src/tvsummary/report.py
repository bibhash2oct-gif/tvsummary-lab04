import json

from .config import OUTPUT_PATH
from .errors import OutputError


class ReportBuilder:
    def __init__(self, aggregations):
        self.aggregations = aggregations
        self.output_path = OUTPUT_PATH

    def build_and_write(self, records):
        summary = {agg.key: agg.compute(records) for agg in self.aggregations}
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, "w") as f:
                json.dump(summary, f, indent=2)
        except OSError as error:
            raise OutputError(
                f"Could not write the summary to {self.output_path}: {error}"
            ) from error
        return summary
