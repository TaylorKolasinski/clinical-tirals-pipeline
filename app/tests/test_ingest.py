import unittest
from unittest.mock import patch
from app.ingest import ingest_data

class TestIngestData(unittest.TestCase):
    @patch("app.ingest.requests.get")
    def test_ingest_data_structure(self, mock_get):
        """Test if ingest_data returns data with the correct structure."""
        mock_get.return_value.json.return_value = {
            "studies": [{"nctId": "NCT123", "title": "Mocked Study"}],
            "nextPageToken": None
        }
        mock_get.return_value.status_code = 200

        data = ingest_data()
        self.assertIsInstance(data, list, "Ingested data should be a list.")
        self.assertGreater(len(data), 0, "Ingested data should not be empty.")
        self.assertIsInstance(data[0], dict, "Each study should be a dictionary.")
        self.assertIn("nctId", data[0], "Each study should contain 'nctId'.")

    @patch("app.ingest.requests.get")
    def test_ingest_data_non_empty(self, mock_get):
        """Test if ingest_data returns non-empty data."""
        mock_get.return_value.json.return_value = {
            "studies": [{"nctId": "NCT123", "title": "Mocked Study"}],
            "nextPageToken": None
        }
        mock_get.return_value.status_code = 200

        data = ingest_data()
        self.assertGreater(len(data), 0, "Ingested data should not be empty.")

    @patch("app.ingest.requests.get")
    def test_ingest_data_resilience(self, mock_get):
        """Test if ingest_data handles errors gracefully (mocked response)."""
        mock_get.side_effect = Exception("Mocked ingestion failure.")
        with self.assertRaises(Exception, msg="Ingest data did not handle failure as expected."):
            ingest_data()


if __name__ == "__main__":
    unittest.main()
