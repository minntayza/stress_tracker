import unittest
from visual_analytics import StressVisualizer
from stress_history import StressHistory
import os

class TestVisualAnalytics(unittest.TestCase):
    def setUp(self):
        self.visualizer = StressVisualizer()
        
    def test_generate_recovery_arc(self):
        # Create dummy history data
        history_data = [
            {"date": "2023-10-01 10:00:00", "stress_score": 85, "recommendation": "Sleep"},
            {"date": "2023-10-02 10:00:00", "stress_score": 75, "recommendation": "Sleep"},
            {"date": "2023-10-03 10:00:00", "stress_score": 55, "recommendation": "Good job"}
        ]
        
        plot_base64 = self.visualizer.generate_recovery_arc(history_data)
        
        self.assertIsNotNone(plot_base64)
        self.assertIsInstance(plot_base64, str)
        self.assertTrue(len(plot_base64) > 100) # Check if it's a substantial string

    def test_empty_history(self):
        plot_base64 = self.visualizer.generate_recovery_arc([])
        self.assertIsNone(plot_base64)

if __name__ == '__main__':
    unittest.main()
