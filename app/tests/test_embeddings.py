import unittest
from app.embeddings import generate_embeddings

class TestGenerateEmbeddings(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.trials = [
            {"title": "NSCLC Trial", "disease": "NSCLC", "intervention": "Drug X"},
            {"title": "Lung Cancer Study", "disease": "Lung Cancer", "intervention": "Drug Y"},
        ]

    def test_generate_embeddings_structure(self):
        """Test if embeddings are added to trials with correct keys."""
        enriched = generate_embeddings(self.trials)
        for trial in enriched:
            self.assertIn("title_embedding", trial, "Missing title_embedding in trial")
            self.assertIn("disease_embedding", trial, "Missing disease_embedding in trial")
            self.assertIn("intervention_embedding", trial, "Missing intervention_embedding in trial")

    def test_generate_embeddings_length(self):
        """Test if embeddings have the correct length."""
        enriched = generate_embeddings(self.trials)
        for trial in enriched:
            self.assertEqual(len(trial["title_embedding"]), 384, "Title embedding length is incorrect")
            self.assertEqual(len(trial["disease_embedding"]), 384, "Disease embedding length is incorrect")
            self.assertEqual(len(trial["intervention_embedding"]), 384, "Intervention embedding length is incorrect")

    def test_generate_embeddings_no_side_effects(self):
        """Test if the original trials are not modified except for added embeddings."""
        original_trials = [trial.copy() for trial in self.trials]
        generate_embeddings(self.trials)
        for original, modified in zip(original_trials, self.trials):
            for key in original:
                self.assertEqual(original[key], modified[key], f"Original key {key} was modified")

if __name__ == "__main__":
    unittest.main()
