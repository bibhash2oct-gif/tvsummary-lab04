from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
API_URL = "https://api.tvmaze.com/shows"
TIMEOUT = 10
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "summary.json"