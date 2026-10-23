"""The record class: one TV show from the TVMaze API."""

from collections.abc import Mapping
from typing import Any

UNKNOWN = "Unknown"


class TVShow:
    """One show, cleaned from a raw TVMaze dictionary.

    Missing or unusable values never raise here. A missing name or status
    becomes "Unknown", a missing or bad rating becomes None, and a missing
    genre list becomes an empty list.
    """

    def __init__(self, raw_data: Mapping[str, Any]) -> None:
        self.name: str = _clean_text(raw_data.get("name"))
        self.status: str = _clean_text(raw_data.get("status"))
        self.rating: float | None = _parse_rating(raw_data.get("rating"))
        self.genres: list[str] = _parse_genres(raw_data.get("genres"))

    def __str__(self) -> str:
        return f"TVShow(name='{self.name}', status='{self.status}')"


def _clean_text(value: object) -> str:
    """Strip a text field, using "Unknown" when it is missing or blank."""
    if value is None:
        return UNKNOWN
    text = str(value).strip()
    return text or UNKNOWN


def _parse_rating(value: object) -> float | None:
    """Read rating.average as a float, or None when it is missing or bad."""
    if not isinstance(value, Mapping):
        return None
    average = value.get("average")
    if average is None or isinstance(average, bool):
        return None
    try:
        return float(average)
    except (TypeError, ValueError):
        return None


def _parse_genres(value: object) -> list[str]:
    """Keep the non-blank text genres, or return [] when the list is missing."""
    if not isinstance(value, list):
        return []
    return [
        genre.strip() for genre in value if isinstance(genre, str) and genre.strip()
    ]
