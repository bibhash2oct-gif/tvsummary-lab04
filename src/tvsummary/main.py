"""Entry point: python -m tvsummary.main [--config PATH].

Exit codes: 0 when the summary was written, 1 when an expected failure
stopped the run (one "Error: ..." line on standard error, no traceback).
"""

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from .aggregations import FeaturedShowsAggregation, TotalCountAggregation
from .config import DEFAULT_CONFIG_PATH, Settings, load_settings
from .errors import SettingsError, TVSummaryError
from .logging_setup import configure_logging
from .report import ReportBuilder
from .sources import TVShowDataSource

logger = logging.getLogger(__name__)

# Used only when the settings file (which holds the real level) cannot be read.
FALLBACK_LOG_LEVEL = "INFO"


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m tvsummary.main",
        description="Download the TVMaze show list and write a JSON summary.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"path to the TOML settings file (default: {DEFAULT_CONFIG_PATH})",
    )
    return parser.parse_args(argv)


def run(settings: Settings) -> ReportBuilder:
    """Fetch, summarise and write both JSON files. Returns the builder used."""
    logger.info(
        "Starting run: seed=%s, sample_size=%s", settings.seed, settings.sample_size
    )
    records = TVShowDataSource(settings.source_url, settings.timeout).fetch()
    builder = ReportBuilder(
        [
            TotalCountAggregation(),
            FeaturedShowsAggregation(settings.seed, settings.sample_size),
        ],
        output_dir=settings.output_dir,
    )
    builder.build_and_write(records)
    builder.write_run_info(settings)
    logger.info("Run finished")
    return builder


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        settings = load_settings(args.config)
    except SettingsError as error:
        configure_logging(FALLBACK_LOG_LEVEL)
        return _fail(error)

    configure_logging(settings.log_level)
    try:
        builder = run(settings)
    except TVSummaryError as error:
        return _fail(error)

    summary_text = builder.summary_path.read_text(encoding="utf-8")
    print(f"Summary written to {builder.summary_path}\n{summary_text}", end="")
    return 0


def _fail(error: TVSummaryError) -> int:
    """Log the failure, show one Error: line on standard error, return 1."""
    logger.error("Run failed: %s", error)
    print(f"Error: {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
