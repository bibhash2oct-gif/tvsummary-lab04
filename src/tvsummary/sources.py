"""Fetching show data. This is the only module that uses requests."""

from typing import Any

import requests

from .config import API_URL, TIMEOUT
from .errors import DataShapeError, SourceError
from .models import TVShow


def download_shows(url: str, timeout: float) -> list[Any]:
    """Download the raw show list from url.

    Raises SourceError when the server cannot be reached or answers with an
    error, and DataShapeError when the body is not a JSON list.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.Timeout as error:
        raise SourceError(
            f"Timed out after {timeout} seconds waiting for {url}"
        ) from error
    except requests.ConnectionError as error:
        raise SourceError(
            f"Could not reach {url}. Check your internet connection."
        ) from error
    except requests.HTTPError as error:
        raise SourceError(f"The server at {url} returned an error: {error}") from error
    except requests.RequestException as error:
        raise SourceError(f"The download from {url} failed: {error}") from error

    try:
        payload = response.json()
    except ValueError as error:
        raise DataShapeError(f"The response from {url} is not valid JSON") from error

    if not isinstance(payload, list):
        raise DataShapeError(
            f"Expected a list of shows from {url}, got {type(payload).__name__}"
        )
    return payload


def parse_shows(payload: list[Any]) -> list[TVShow]:
    """Turn the downloaded list into TVShow records.

    Entries that are not objects are skipped. Raises DataShapeError when no
    usable show is left.
    """
    records = [TVShow(item) for item in payload if isinstance(item, dict)]
    if not records:
        raise DataShapeError("The response contained no usable shows")
    return records


class TVShowDataSource:
    """Downloads the TVMaze show list and returns TVShow records."""

    def __init__(self, url: str = API_URL, timeout: float = TIMEOUT) -> None:
        self.url = url
        self.timeout = timeout

    def fetch(self) -> list[TVShow]:
        return parse_shows(download_shows(self.url, self.timeout))
