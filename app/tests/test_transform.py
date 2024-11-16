import unittest
from app.transform import transform_data

class TestTransformData(unittest.TestCase):
    def setUp(self):
        """Set up raw data for testing."""
        self.raw_data = {
            "FullStudiesResponse": {
                "FullStudies": [
                    {
                        "Study": {
                            "ProtocolSection": {
                                "IdentificationModule": {
                                    "NCTId": "NCT123",
                                    "BriefTitle": "Trial Title"
                                },
                                "DesignModule": {
                                    "PhaseList": {
                                        "Phase": "Phase 3"
                                    }
                                },
                                "ArmsInterventionsModule": {
                                    "InterventionList": {
                                        "Intervention": [
                                            {"InterventionName": "Drug"}
                                        ]
                                    }
                                },
                                "StatusModule": {
                                    "OverallStatus": "Completed",
                                    "LastUpdatePostDateStruct": {
                                        "LastUpdatePostDate": "2023-11-14"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }

    def test_transform_data_structure(self):
        """Test if transform_data returns a list of transformed trials."""
        transformed = transform_data(self.raw_data)
        self.assertIsInstance(transformed, list, "Transformed data should be a list.")
        self.assertEqual(len(transformed), 1, "Transformed data should contain one trial.")

    def test_transform_data_content(self):
        """Test if transform_data correctly maps fields."""
        transformed = transform_data(self.raw_data)
        self.assertEqual(transformed[0]['nct_number'], "NCT123", "NCT number mismatch.")
        self.assertEqual(transformed[0]['title'], "Trial Title", "Title mismatch.")
        self.assertEqual(transformed[0]['phase'], "Phase 3", "Phase mismatch.")
        self.assertEqual(transformed[0]['intervention'], "Drug", "Intervention mismatch.")
        self.assertEqual(transformed[0]['status'], "Completed", "Status mismatch.")
        self.assertEqual(str(transformed[0]['last_update']), "2023-11-14", "Last update mismatch.")

    def test_transform_data_missing_fields(self):
        """Test if transform_data handles missing optional fields gracefully."""
        incomplete_data = {
            "FullStudiesResponse": {
                "FullStudies": [
                    {
                        "Study": {
                            "ProtocolSection": {
                                "IdentificationModule": {
                                    "NCTId": "NCT456",
                                    "BriefTitle": "Incomplete Trial"
                                }
                            }
                        }
                    }
                ]
            }
        }
        transformed = transform_data(incomplete_data)
        self.assertEqual(len(transformed), 1, "Transformed data should contain one trial.")
        self.assertEqual(transformed[0]['nct_number'], "NCT456", "NCT number mismatch for incomplete trial.")
        self.assertEqual(transformed[0]['title'], "Incomplete Trial", "Title mismatch for incomplete trial.")
        self.assertEqual(transformed[0]['phase'], "N/A", "Default phase mismatch for incomplete trial.")
        self.assertEqual(transformed[0]['intervention'], "N/A", "Default intervention mismatch for incomplete trial.")
        self.assertEqual(transformed[0]['status'], "N/A", "Default status mismatch for incomplete trial.")
        self.assertIsNone(transformed[0]['last_update'], "Last update should be None for incomplete trial.")

    def test_transform_data_empty_input(self):
        """Test if transform_data handles empty input gracefully."""
        empty_data = {"FullStudiesResponse": {"FullStudies": []}}
        transformed = transform_data(empty_data)
        self.assertIsInstance(transformed, list, "Transformed data should be a list.")
        self.assertEqual(len(transformed), 0, "Transformed data should be empty for empty input.")


if __name__ == "__main__":
    unittest.main()
