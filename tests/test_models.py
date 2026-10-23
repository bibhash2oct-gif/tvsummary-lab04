import unittest
from tvsummary.models import TVShow

class TestTVShow(unittest.TestCase):
    def test_cleaning(self):
        show = TVShow({"name": "  Lost  ", "rating": {"average": "bad"}})
        self.assertEqual(show.name, "Lost")
        self.assertIsNone(show.rating)