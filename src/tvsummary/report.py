import json
from .config import OUTPUT_PATH

class ReportBuilder:
    def __init__(self, aggregations):
        self.aggregations = aggregations
        self.output_path = OUTPUT_PATH

    def build_and_write(self, records):
        summary = {agg.key: agg.compute(records) for agg in self.aggregations}
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(summary, f, indent=2)