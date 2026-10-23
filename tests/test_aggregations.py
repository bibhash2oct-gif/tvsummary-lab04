from tvsummary.aggregations import TotalCountAggregation
from tvsummary.models import TVShow


def test_total_count_counts_every_record(sample_records: list[TVShow]) -> None:
    aggregation = TotalCountAggregation()
    assert aggregation.key == "total_shows"
    assert aggregation.compute(sample_records) == 5


def test_total_count_of_no_records_is_zero() -> None:
    assert TotalCountAggregation().compute([]) == 0
