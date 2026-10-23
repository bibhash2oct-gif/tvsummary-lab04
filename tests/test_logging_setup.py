import logging

import pytest

from tvsummary.logging_setup import HANDLER_NAME, configure_logging


def _our_handlers() -> list[logging.Handler]:
    return [h for h in logging.getLogger().handlers if h.get_name() == HANDLER_NAME]


def test_configure_logging_sets_level_and_one_handler() -> None:
    configure_logging("debug")
    configure_logging("WARNING")

    assert logging.getLogger().level == logging.WARNING
    assert len(_our_handlers()) == 1


def test_configure_logging_rejects_an_unknown_level() -> None:
    with pytest.raises(ValueError, match="Unknown log level"):
        configure_logging("LOUD")
