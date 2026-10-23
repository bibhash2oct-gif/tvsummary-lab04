# tvsummary

Downloads the TVMaze show list (`https://api.tvmaze.com/shows`) and writes a small JSON summary: how many shows arrived, plus a repeatable random list of featured shows chosen from a seed.

## Setup

```bash
conda env create -f environment.yml
conda activate tvsummary
pip install -r requirements.txt
pip install -e .
```

## Run

Run from the repository root, so the default settings file and output folder are found.

```bash
python -m tvsummary.main
python -m tvsummary.main --config config/tvsummary.toml
```

A successful run writes `data/processed/summary.json` and `data/processed/run_info.json`, prints where the summary went and what it contains, and exits with code 0. Log messages go to standard error.

## Check it

```bash
python -m ruff format --check .
python -m ruff check .
python -m mypy
python -m pytest
```

All four pass. The tests need no network.

## Settings

All settings live in `config/tvsummary.toml`. Every key is required, and an unknown key is an error.

- `source_url`: the address the show list is downloaded from.
- `timeout`: seconds to wait for the server before giving up (a number above 0).
- `output_dir`: the folder for `summary.json` and `run_info.json`, relative to where you run the command.
- `seed`: the whole number given to `random.Random`, which decides `featured_shows`.
- `sample_size`: how many featured shows to pick (0 or more).
- `log_level`: how much to log: `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`.

## Errors and exit codes

Every expected failure is a subclass of `TVSummaryError` (in `src/tvsummary/errors.py`). Only `main()` catches them. It logs the failure at ERROR level, prints one line starting `Error:` to standard error, and returns 1. You never see a traceback for these.

| Error class | When it is raised | What the user sees |
|---|---|---|
| `SettingsError` | The settings file is missing or is not valid TOML. Also when a key is missing or unknown, or a value has the wrong type or range. | `Error: Settings file not found: config/tvsummary.toml`, or `Error: Settings file ... is missing: seed` |
| `SourceError` | The server cannot be reached, times out, or answers with an HTTP error. | `Error: Could not reach https://api.tvmaze.com/shows. Check your internet connection.` |
| `DataShapeError` | The response is not valid JSON, is not a list, or contains no usable shows. | `Error: Expected a list of shows from https://api.tvmaze.com/shows, got dict` |
| `OutputError` | `summary.json` or `run_info.json` cannot be written, for example when the output path is a file. | `Error: Could not write data/processed/summary.json: ...` |

Exit codes:

- `0`: success. Both JSON files were written.
- `1`: an expected failure from the table above stopped the run.
- `2`: the command line itself was wrong, for example an unknown option. argparse reports this, not the package.

Any other exception is a bug. It is left uncaught on purpose, so its traceback shows where to look.

## Reproducing a run

- The seed is in `config/tvsummary.toml` (`seed = 5005`), next to `sample_size = 5`.
- `run_info.json` records:
  - the time of the run
  - the Python version
  - the package version
  - the installed versions of pytest, mypy and ruff
  - every setting used, including the seed
- To get exactly the same `featured_shows` list, a classmate needs:
  - the same `seed` and `sample_size`
  - the same Python minor version (3.11, from `environment.yml`). Python guarantees the same `random()` sequence for a seed across versions, but not the same `random.sample` picks.
  - the same set of show names from TVMaze. Names are sorted and de-duplicated before sampling, so the order they arrive in does not matter, but a renamed or added show would change the pick.
- The test `test_same_seed_gives_the_same_featured_shows` proves that the same seed gives the same list. `test_main_success_writes_both_files_and_returns_0` runs the whole program twice and gets the same summary.

## What the tests cover

There are 51 tests in `tests/`, with shared hand-made data in `tests/conftest.py`. They protect this behaviour:

- **The `TVShow` record.** Names are trimmed. A missing, null or bad rating becomes `None`. A missing genre list becomes `[]`.
- **Each aggregation.** `TotalCountAggregation` counts records. `FeaturedShowsAggregation` gives the same list for the same seed, copes with a sample bigger than the data, and rejects a negative size. The base class cannot be used directly.
- **The source.** `requests.get` is replaced with `monkeypatch`. A lost connection, a timeout, an HTTP error, bad JSON and a non-list body each raise the right error, checked with `pytest.raises(..., match=...)`. Bad entries are skipped with a WARNING, checked with `caplog`.
- **Settings.** The shipped TOML file loads. Missing, broken, incomplete and badly typed files raise `SettingsError`. The `Settings` object cannot be changed.
- **The report.** `summary.json` and `run_info.json` are written with `tmp_path`, and an unwritable folder raises `OutputError`.
- **`main()`.** Exit code 1 and a single `Error:` line for a missing settings file, a failed download and a bad response. Exit code 0 and both files for a good run. `python -m tvsummary.main` works as a real command.

Not tested: the live TVMaze API. A test that needs the internet fails whenever the wifi does, and the API's data changes over time, so every network call is replaced with a fake response instead. The real download is checked by running the program, which produced the committed files in `data/processed/`.

## Known limitations

- Only the first page of `/shows` (about 240 shows) is downloaded, the same as in Lab 03.
- The raw download is not saved to `data/raw/`, so a later run can only repeat `featured_shows` if TVMaze still sends the same names.
- There is no retry when the network fails. One failure ends the run with exit code 1.
- `output_dir` is relative to the folder you run from, so run commands from the repository root.
- `TVShow.genres` is parsed and tested but not yet used in the summary, which keeps `summary.json` identical to Lab 03 apart from `featured_shows`.
