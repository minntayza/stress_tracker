import unittest

from app import _moving_average, _parse_entry_datetime


class TestHistorySeries(unittest.TestCase):
    def test_parse_entry_datetime_formats(self):
        self.assertIsNotNone(_parse_entry_datetime("2026-02-23 14:20:00"))
        self.assertIsNotNone(_parse_entry_datetime("2026-02-23T14:20:00"))
        self.assertIsNotNone(_parse_entry_datetime("2026-02-23"))
        self.assertIsNone(_parse_entry_datetime("bad-date"))

    def test_moving_average_skips_none(self):
        values = [10.0, None, 20.0, None, 30.0]
        result = _moving_average(values, window=3)
        self.assertEqual(result, [10.0, None, 15.0, None, 25.0])

    def test_moving_average_identity_for_window_one(self):
        values = [1.0, 2.0, None, 4.0]
        self.assertEqual(_moving_average(values, window=1), values)


if __name__ == "__main__":
    unittest.main()
