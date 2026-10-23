class TVShow:
    def __init__(self, raw_data):
        self.name = str(raw_data.get("name", "Unknown")).strip()
        self.status = str(raw_data.get("status", "Unknown")).strip()
        try:
            self.rating = float(raw_data.get("rating", {}).get("average"))
        except (ValueError, TypeError):
            self.rating = None

    def __str__(self):
        return f"TVShow(name='{self.name}', status='{self.status}')"