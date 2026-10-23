"""Aggregations: each one turns the list of records into one summary value."""

import logging
import random
from abc import ABC, abstractmethod

from .models import TVShow

logger = logging.getLogger(__name__)


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


class FeaturedShowsAggregation(Aggregation):
    """A repeatable random pick of show names, driven by a seed.

    Names are de-duplicated and sorted before sampling, so the pick depends
    only on the seed and the set of names, not on the order they arrived in.
    """

    def __init__(self, seed: int, sample_size: int) -> None:
        super().__init__("featured_shows")
        if sample_size < 0:
            raise ValueError("sample_size cannot be negative")
        self.seed = seed
        self.sample_size = sample_size

    def compute(self, records: list[TVShow]) -> list[str]:
        names = sorted({record.name for record in records})
        size = min(self.sample_size, len(names))
        if size < self.sample_size:
            logger.warning(
                "Asked for %d featured shows but only %d names exist; using all",
                self.sample_size,
                len(names),
            )
        featured = random.Random(self.seed).sample(names, size)
        logger.debug("Featured shows for seed %s: %s", self.seed, featured)
        return featured
