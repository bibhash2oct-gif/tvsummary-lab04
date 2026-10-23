import pytest

from tvsummary.aggregations import (
    Aggregation,
    FeaturedShowsAggregation,
    TotalCountAggregation,
)
from tvsummary.models import TVShow


def test_total_count_counts_every_record(sample_records: list[TVShow]) -> None:
    aggregation = TotalCountAggregation()
    assert aggregation.key == "total_shows"
    assert aggregation.compute(sample_records) == 5


def test_total_count_of_no_records_is_zero() -> None:
    assert TotalCountAggregation().compute([]) == 0


def test_the_base_aggregation_cannot_be_used_directly() -> None:
    base: type = Aggregation
    with pytest.raises(TypeError, match="abstract"):
        base("anything")


def test_same_seed_gives_the_same_featured_shows(
    sample_records: list[TVShow],
) -> None:
    first = FeaturedShowsAggregation(seed=5005, sample_size=3).compute(sample_records)
    second = FeaturedShowsAggregation(seed=5005, sample_size=3).compute(
        list(reversed(sample_records))
    )

    assert first == second
    assert len(first) == 3
    assert len(set(first)) == 3
    assert set(first) <= {record.name for record in sample_records}


def test_different_seeds_can_give_different_featured_shows(
    sample_records: list[TVShow],
) -> None:
    picks = {
        tuple(FeaturedShowsAggregation(seed, 3).compute(sample_records))
        for seed in range(10)
    }
    assert len(picks) > 1


def test_featured_shows_uses_every_name_when_sample_is_too_big(
    sample_records: list[TVShow], caplog: pytest.LogCaptureFixture
) -> None:
    featured = FeaturedShowsAggregation(seed=1, sample_size=50).compute(sample_records)

    assert sorted(featured) == sorted(record.name for record in sample_records)
    assert "only 5 names exist" in caplog.text


def test_featured_shows_rejects_a_negative_sample_size() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        FeaturedShowsAggregation(seed=1, sample_size=-1)
