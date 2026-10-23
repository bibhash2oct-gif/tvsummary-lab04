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


def test_null_rating_object_gives_none() -> None:
    # TVMaze can send "rating": null; Lab 03 crashed here with AttributeError.
    show = TVShow({"name": "Lost", "rating": None})
    assert show.rating is None


def test_missing_genre_list_gives_empty_list() -> None:
    show = TVShow({"name": "Lost", "rating": {"average": 8.0}})
    assert show.genres == []


def test_genres_keep_only_non_blank_text() -> None:
    show = TVShow({"name": "Lost", "genres": [" Drama ", "", None, 3, "Mystery"]})
    assert show.genres == ["Drama", "Mystery"]


def test_record_built_from_full_show(sample_records: list[TVShow]) -> None:
    show = sample_records[1]
    assert show.name == "Person of Interest"
    assert show.status == "Ended"
    assert show.rating == 8.8
    assert show.genres == ["Action", "Crime", "Science-Fiction"]
