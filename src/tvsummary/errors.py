"""Errors the tvsummary package raises on purpose.

Every expected failure is a subclass of TVSummaryError, so main() can catch
the whole family in one place and anything else still shows a traceback.
"""


class TVSummaryError(Exception):
    """Base class for every error this package raises on purpose."""


class SourceError(TVSummaryError):
    """The show list could not be downloaded (network, timeout, HTTP status)."""


class DataShapeError(TVSummaryError):
    """The download worked, but the response is not the shape we expect."""


class SettingsError(TVSummaryError):
    """The settings file is missing, unreadable, incomplete or has bad values."""


class OutputError(TVSummaryError):
    """summary.json or run_info.json could not be written."""
