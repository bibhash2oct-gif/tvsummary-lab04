class Aggregation:
    def __init__(self, key):
        self.key = key

    def compute(self, records):
        pass

class TotalCountAggregation(Aggregation):
    def __init__(self):
        self.key = "total_shows"

    def compute(self, records):
        return len(records)