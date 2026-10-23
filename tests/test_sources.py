from typing import Any

import pytest
import requests

from tvsummary import sources
from tvsummary.errors import DataShapeError, SourceError
from tvsummary.models import TVShow


def test_fetch_turns_each_show_into_a_record(
    monkeypatch: pytest.MonkeyPatch,
    raw_shows: list[dict[str, Any]],
    fake_response_class: type,
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> Any:
        return fake_response_class(raw_shows)

    monkeypatch.setattr(sources.requests, "get", fake_get)

    records = sources.TVShowDataSource().fetch()

    assert len(records) == 5
    assert all(isinstance(record, TVShow) for record in records)
    assert records[0].name == "Under the Dome"


def test_a_failed_download_raises_a_source_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> Any:
        raise requests.ConnectionError("no network")

    monkeypatch.setattr(sources.requests, "get", fake_get)

    with pytest.raises(SourceError, match="reach") as caught:
        sources.download_shows("https://example.invalid", timeout=1)
    assert isinstance(caught.value.__cause__, requests.ConnectionError)


def test_a_timeout_raises_a_source_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> Any:
        raise requests.Timeout("too slow")

    monkeypatch.setattr(sources.requests, "get", fake_get)

    with pytest.raises(SourceError, match="Timed out after 1 seconds"):
        sources.download_shows("https://example.invalid", timeout=1)


def test_an_http_error_status_raises_a_source_error(
    monkeypatch: pytest.MonkeyPatch, fake_response_class: type
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> Any:
        return fake_response_class([], status_code=503)

    monkeypatch.setattr(sources.requests, "get", fake_get)

    with pytest.raises(SourceError, match="returned an error"):
        sources.download_shows("https://example.invalid", timeout=1)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (ValueError("not json"), "not valid JSON"),
        ({"name": "Lost"}, "Expected a list of shows"),
        ("just text", "Expected a list of shows"),
    ],
)
def test_a_badly_shaped_response_raises_a_data_shape_error(
    monkeypatch: pytest.MonkeyPatch,
    fake_response_class: type,
    payload: object,
    message: str,
) -> None:
    def fake_get(*args: Any, **kwargs: Any) -> Any:
        return fake_response_class(payload)

    monkeypatch.setattr(sources.requests, "get", fake_get)

    with pytest.raises(DataShapeError, match=message):
        sources.download_shows("https://example.invalid", timeout=1)


def test_parse_shows_skips_entries_that_are_not_objects(
    raw_shows: list[dict[str, Any]],
) -> None:
    records = sources.parse_shows([raw_shows[0], "oops", None, raw_shows[1]])
    assert [record.name for record in records] == [
        "Under the Dome",
        "Person of Interest",
    ]


def test_parse_shows_with_nothing_usable_raises() -> None:
    with pytest.raises(DataShapeError, match="no usable shows"):
        sources.parse_shows(["oops", 42])
