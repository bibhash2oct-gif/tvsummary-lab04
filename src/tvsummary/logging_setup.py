"""Logging configuration. main() calls configure_logging once per run."""

import logging
import sys

PACKAGE_LOGGER = "tvsummary"
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def configure_logging(level: str) -> None:
    """Send the package's log records to standard error at the given level.

    Only the "tvsummary" logger is configured, so the root logger and other
    libraries are left alone. Calling this again replaces the old handler
    instead of adding a second one.
    """
    level_name = level.upper()
    if level_name not in LEVELS:
        raise ValueError(f"Unknown log level {level!r}; use one of {LEVELS}")

    logger = logging.getLogger(PACKAGE_LOGGER)
    for old_handler in list(logger.handlers):
        logger.removeHandler(old_handler)

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    logger.setLevel(level_name)
