import dataclasses
from pathlib import Path

import pytest

from tvsummary.config import Settings, load_settings
from tvsummary.errors import SettingsError

REPO_CONFIG = Path(__file__).resolve().parents[1] / "config" / "tvsummary.toml"


def test_settings_are_read_into_a_frozen_dataclass(
    settings: Settings, tmp_path: Path
) -> None:
    assert settings.source_url == "https://example.invalid/shows"
    assert settings.timeout == 5.0
    assert settings.output_dir == tmp_path / "processed"
    assert settings.seed == 5005
    assert settings.sample_size == 3
    assert settings.log_level == "DEBUG"
    with pytest.raises(dataclasses.FrozenInstanceError):
        settings.seed = 1  # type: ignore[misc]  # writing to a frozen field is what this test checks


def test_the_shipped_settings_file_is_valid() -> None:
    settings = load_settings(REPO_CONFIG)
    assert settings.source_url == "https://api.tvmaze.com/shows"
    assert settings.output_dir == Path("data/processed")


def test_a_missing_settings_file_raises(tmp_path: Path) -> None:
    with pytest.raises(SettingsError, match="Settings file not found"):
        load_settings(tmp_path / "nope.toml")


def test_a_broken_settings_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "broken.toml"
    path.write_text("seed = = 3\n")
    with pytest.raises(SettingsError, match="not valid TOML"):
        load_settings(path)


def test_an_incomplete_settings_file_names_the_missing_keys(
    settings_file: Path,
) -> None:
    kept = [
        line
        for line in settings_file.read_text().splitlines()
        if not line.startswith(("seed", "sample_size"))
    ]
    settings_file.write_text("\n".join(kept))

    with pytest.raises(SettingsError, match="missing: seed, sample_size"):
        load_settings(settings_file)


def test_an_unknown_key_is_rejected(settings_file: Path) -> None:
    settings_file.write_text(settings_file.read_text() + "sead = 7\n")
    with pytest.raises(SettingsError, match="unknown settings: sead"):
        load_settings(settings_file)


@pytest.mark.parametrize(
    ("line", "message"),
    [
        ("timeout = 0", "'timeout' must be a number above 0"),
        ("timeout = true", "'timeout' must be a number above 0"),
        ('seed = "abc"', "'seed' must be a whole number"),
        ("sample_size = -2", "'sample_size' cannot be negative"),
        ('log_level = "LOUD"', "'log_level' must be one of"),
        ('source_url = ""', "'source_url' must be non-empty text"),
    ],
)
def test_a_bad_value_raises(settings_file: Path, line: str, message: str) -> None:
    key = line.split(" = ")[0]
    lines = [
        line if existing.startswith(f"{key} =") else existing
        for existing in settings_file.read_text().splitlines()
    ]
    settings_file.write_text("\n".join(lines))

    with pytest.raises(SettingsError, match=message):
        load_settings(settings_file)
