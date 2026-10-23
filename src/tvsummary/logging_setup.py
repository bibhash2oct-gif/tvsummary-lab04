"""Logging configuration. main() calls configure_logging once per run."""

import logging
import sys

HANDLER_NAME = "tvsummary"
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def configure_logging(level: str) -> None:
    """Send log records to standard error at the given level.

    The handler goes on the root logger so that every module's logger is
    covered, including main.py, whose logger is called "__main__" when it
    runs with python -m. Calling this again replaces our handler instead of
    adding a second one, and leaves other handlers alone.
    """
    level_name = level.upper()
    if level_name not in LEVELS:
        raise ValueError(f"Unknown log level {level!r}; use one of {LEVELS}")

    root = logging.getLogger()
    for old_handler in list(root.handlers):
        if old_handler.get_name() == HANDLER_NAME:
            root.removeHandler(old_handler)

    handler = logging.StreamHandler(sys.stderr)
    handler.set_name(HANDLER_NAME)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(handler)
    root.setLevel(level_name)
