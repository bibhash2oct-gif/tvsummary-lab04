import logging

import pytest

from tvsummary.logging_setup import configure_logging


def test_configure_logging_sets_level_and_one_handler() -> None:
    configure_logging("debug")
    configure_logging("WARNING")

    logger = logging.getLogger("tvsummary")
    assert logger.level == logging.WARNING
    assert len(logger.handlers) == 1


def test_configure_logging_rejects_an_unknown_level() -> None:
    with pytest.raises(ValueError, match="Unknown log level"):
        configure_logging("LOUD")
