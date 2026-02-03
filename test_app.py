import unittest
from app import app
import os

class TestPandaStressApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Stress Assessment', response.data)

    def test_analyze_flow(self):
        # Simulate a POST request with valid data
        response = self.app.post('/analyze', data={
            'sleep': '8',
            'study': '4',
            'journal': 'I feel good today.'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Analysis Results', response.data)
        # Check if stress score is displayed
        self.assertIn(b'Calculated Stress Score', response.data)
        # Check sentiment
        self.assertIn(b'Sentiment Analysis', response.data)

    def tearDown(self):
        # Clean up history if needed, though app uses the default 'history.json'
        # In a real test env we'd mock the file, but for this simple check it's fine.
        pass

if __name__ == '__main__':
    unittest.main()
