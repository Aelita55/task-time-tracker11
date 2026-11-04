import unittest
from datetime import datetime, timedelta
from time_tracker import TimeTracker

class TestTimeTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = TimeTracker()

    def test_start_and_stop_timer(self):
        self.tracker.start_timer(1)
        self.assertIn(1, self.tracker.active_timers)
        duration = self.tracker.stop_timer(1)
        self.assertIsInstance(duration, timedelta)

    def test_multiple_sessions(self):
        self.tracker.start_timer(1)
        self.tracker.stop_timer(1)
        self.tracker.start_timer(1)
        self.tracker.stop_timer(1)
        self.assertEqual(len(self.tracker.logs[1]), 2)

    def test_double_start_raises_error(self):
        self.tracker.start_timer(1)
        with self.assertRaises(ValueError):
            self.tracker.start_timer(1)

    def test_stop_without_start_raises_error(self):
        with self.assertRaises(ValueError):
            self.tracker.stop_timer(99)

    def test_report_generation(self):
        self.tracker.start_timer(1)
        self.tracker.stop_timer(1)
        report = self.tracker.generate_report()
        self.assertEqual(len(report["tasks"]), 1)
