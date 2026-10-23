"""Shared fixtures for the tvsummary test suite.

Every fixture here is hand-made, so no test needs the network.
"""

import logging
from collections.abc import Iterator
from typing import Any

import pytest
import requests

from tvsummary.models import TVShow


class FakeResponse:
    """Stands in for requests.Response in tests."""

    def __init__(self, payload: Any, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Server Error")

    def json(self) -> Any:
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


@pytest.fixture
def raw_shows() -> list[dict[str, Any]]:
    """Five shows shaped like the TVMaze /shows response."""
    return [
        {
            "name": "Under the Dome",
            "status": "Ended",
            "genres": ["Drama", "Science-Fiction", "Thriller"],
            "rating": {"average": 6.5},
        },
        {
            "name": "Person of Interest",
            "status": "Ended",
            "genres": ["Action", "Crime", "Science-Fiction"],
            "rating": {"average": 8.8},
        },
        {
            "name": "Bitten",
            "status": "Ended",
            "genres": ["Drama", "Horror", "Romance"],
            "rating": {"average": 7.4},
        },
        {
            "name": "Arrow",
            "status": "Ended",
            "genres": ["Drama", "Action", "Science-Fiction"],
            "rating": {"average": 7.4},
        },
        {
            "name": "True Detective",
            "status": "Running",
            "genres": ["Drama", "Crime", "Thriller"],
            "rating": {"average": 8.1},
        },
    ]


@pytest.fixture
def sample_records(raw_shows: list[dict[str, Any]]) -> list[TVShow]:
    """The five raw shows turned into TVShow records."""
    return [TVShow(raw) for raw in raw_shows]


@pytest.fixture
def fake_response_class() -> type[FakeResponse]:
    """Gives tests the FakeResponse class without importing conftest."""
    return FakeResponse


@pytest.fixture(autouse=True)
def reset_package_logger() -> Iterator[None]:
    """Undo configure_logging after each test so tests stay independent."""
    yield
    logger = logging.getLogger("tvsummary")
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    logger.setLevel(logging.NOTSET)
