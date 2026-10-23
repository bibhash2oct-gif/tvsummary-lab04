import pytest

from tvsummary.models import TVShow


def test_cleaning() -> None:
    show = TVShow({"name": "  Lost  ", "rating": {"average": "bad"}})
    assert show.name == "Lost"
    assert show.rating is None


def test_missing_rating_gives_none() -> None:
    show = TVShow({"name": "Lost"})
    assert show.rating is None


def test_missing_name_and_status_default_to_unknown() -> None:
    show = TVShow({})
    assert show.name == "Unknown"
    assert show.status == "Unknown"


@pytest.mark.parametrize(
    ("rating", "expected"),
    [
        ({"average": 8.5}, 8.5),
        ({"average": "7"}, 7.0),
        ({"average": None}, None),
        ({}, None),
    ],
)
def test_rating_is_parsed_to_float_or_none(
    rating: dict[str, object], expected: float | None
) -> None:
    show = TVShow({"name": "Lost", "rating": rating})
    assert show.rating == expected
