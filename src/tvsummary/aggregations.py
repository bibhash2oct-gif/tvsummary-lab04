"""Aggregations: each one turns the list of records into one summary value."""

from abc import ABC, abstractmethod

from .models import TVShow


class Aggregation(ABC):
    """Base class. key is the summary.json key; compute gives its value."""

    def __init__(self, key: str) -> None:
        self.key = key

    @abstractmethod
    def compute(self, records: list[TVShow]) -> object:
        """Return a JSON-friendly value for these records."""


class TotalCountAggregation(Aggregation):
    """How many shows arrived."""

    def __init__(self) -> None:
        super().__init__("total_shows")

    def compute(self, records: list[TVShow]) -> int:
        return len(records)
