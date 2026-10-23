import requests
from .config import API_URL, TIMEOUT
from .models import TVShow

class TVShowDataSource:
    def fetch(self):
        response = requests.get(API_URL, timeout=TIMEOUT)
        response.raise_for_status()
        return [TVShow(show) for show in response.json()]