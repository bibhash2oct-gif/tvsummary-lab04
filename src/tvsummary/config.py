"""Settings: read the TOML settings file into a frozen Settings object."""

import tomllib
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from .errors import SettingsError
from .logging_setup import LEVELS

DEFAULT_CONFIG_PATH = Path("config") / "tvsummary.toml"


@dataclass(frozen=True)
class Settings:
    """Every value the program reads from the settings file."""

    source_url: str
    timeout: float
    output_dir: Path
    seed: int
    sample_size: int
    log_level: str

    def as_dict(self) -> dict[str, object]:
        """Plain JSON-friendly values, for run_info.json."""
        return {
            "source_url": self.source_url,
            "timeout": self.timeout,
            "output_dir": self.output_dir.as_posix(),
            "seed": self.seed,
            "sample_size": self.sample_size,
            "log_level": self.log_level,
        }


SETTING_NAMES = tuple(field.name for field in fields(Settings))


def load_settings(path: Path | str = DEFAULT_CONFIG_PATH) -> Settings:
    """Read and check the settings file.

    Raises SettingsError when the file is missing, is not valid TOML, has a
    missing or unknown key, or has a value of the wrong type or range.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise SettingsError(f"Settings file not found: {config_path}")

    try:
        with config_path.open("rb") as handle:
            data = tomllib.load(handle)
    except tomllib.TOMLDecodeError as error:
        raise SettingsError(
            f"Settings file {config_path} is not valid TOML: {error}"
        ) from error
    except OSError as error:
        raise SettingsError(
            f"Could not read settings file {config_path}: {error}"
        ) from error

    missing = [name for name in SETTING_NAMES if name not in data]
    if missing:
        raise SettingsError(
            f"Settings file {config_path} is missing: {', '.join(missing)}"
        )
    unknown = sorted(set(data) - set(SETTING_NAMES))
    if unknown:
        raise SettingsError(
            f"Settings file {config_path} has unknown settings: {', '.join(unknown)}"
        )

    return Settings(
        source_url=_text(data, "source_url"),
        timeout=_positive_number(data, "timeout"),
        output_dir=Path(_text(data, "output_dir")),
        seed=_whole_number(data, "seed"),
        sample_size=_sample_size(data),
        log_level=_log_level(data),
    )


def _text(data: dict[str, Any], key: str) -> str:
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise SettingsError(f"Setting '{key}' must be non-empty text")
    return value.strip()


def _whole_number(data: dict[str, Any], key: str) -> int:
    value = data[key]
    # bool is a subclass of int, so true/false must be ruled out by hand.
    if isinstance(value, bool) or not isinstance(value, int):
        raise SettingsError(f"Setting '{key}' must be a whole number")
    return value


def _positive_number(data: dict[str, Any], key: str) -> float:
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, int | float) or value <= 0:
        raise SettingsError(f"Setting '{key}' must be a number above 0")
    return float(value)


def _sample_size(data: dict[str, Any]) -> int:
    value = _whole_number(data, "sample_size")
    if value < 0:
        raise SettingsError("Setting 'sample_size' cannot be negative")
    return value


def _log_level(data: dict[str, Any]) -> str:
    value = _text(data, "log_level").upper()
    if value not in LEVELS:
        raise SettingsError(f"Setting 'log_level' must be one of {', '.join(LEVELS)}")
    return value
