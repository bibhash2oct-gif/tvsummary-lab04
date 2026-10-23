"""tvsummary: download the TVMaze show list and write a JSON summary."""

from .aggregations import Aggregation, FeaturedShowsAggregation, TotalCountAggregation
from .config import Settings, load_settings
from .errors import (
    DataShapeError,
    OutputError,
    SettingsError,
    SourceError,
    TVSummaryError,
)
from .models import TVShow
from .report import ReportBuilder
from .sources import TVShowDataSource

__all__ = [
    "Aggregation",
    "DataShapeError",
    "FeaturedShowsAggregation",
    "OutputError",
    "ReportBuilder",
    "Settings",
    "SettingsError",
    "SourceError",
    "TVShow",
    "TVShowDataSource",
    "TVSummaryError",
    "TotalCountAggregation",
    "load_settings",
]
