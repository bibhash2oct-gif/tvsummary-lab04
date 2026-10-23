from typing import Any

import pytest

from tvsummary import sources
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
