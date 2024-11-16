import unittest 
from unittest.mock import patch, MagicMock
from app.search import search_trials


class TestSearchTrials(unittest.TestCase):
    def setUp(self):
        """Set up mock data for testing."""
        self.mock_trials = [
            (1, "NSCLC Immunotherapy Trial", "NSCLC", "Drug A"),
            (2, "Lung Cancer Study", "Lung Cancer", "Drug B"),
        ]

    @patch("app.search.psycopg2.connect")  # Mock database connection
    def test_search_trials_no_results(self, mock_connect):
        """Test if search_trials handles cases with no matching results."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []  # Simulate no results
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        results = search_trials(query="Unknown query", top_k=5)

        self.assertIsInstance(results, list, "Results should be a list.")
        self.assertEqual(len(results), 0, "Results should be empty for unmatched queries.")


if __name__ == "__main__":
    unittest.main()
