from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
API_URL: str = "https://api.tvmaze.com/shows"
TIMEOUT: float = 10
OUTPUT_PATH: Path = BASE_DIR / "data" / "processed" / "summary.json"
