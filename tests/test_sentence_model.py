import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import torch
from sentence_transformers import SentenceTransformer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from src.embedding.embedding_models import EmbeddingModel

class TestEmbeddingModel(unittest.TestCase):
    """Unit tests for the EmbeddingModel class."""

    @patch("sentence_transformers.SentenceTransformer")
    def setUp(self, mock_model):
        """Set up the test environment."""
        self.mock_instance = MagicMock()
        mock_model.return_value = self.mock_instance
        self.embedding_model = EmbeddingModel()

    def test_model_initialization(self):
        """Test if the model initializes correctly."""
        self.assertIsNotNone(self.embedding_model.model)
    
    def test_embed_single_sentence(self):
        """Test embedding generation for a single sentence."""
        sample_text = "This is a test sentence."
        expected_embedding = torch.rand(384)  # Mocked tensor output with correct size
        self.mock_instance.encode.return_value = expected_embedding

        embedding = self.embedding_model.embed(sample_text)
        
        # Ensure the embedding is a tensor and has the correct size
        self.assertTrue(isinstance(embedding, torch.Tensor))
        self.assertEqual(embedding.shape[0], 384)  # Ensure correct embedding size

    def test_embed_list_of_sentences(self):
        """Test embedding generation for a list of sentences."""
        sample_texts = ["Sentence one.", "Sentence two."]
        expected_embedding = torch.rand(2, 384)  # Mocked tensor output with correct size
        self.mock_instance.encode.return_value = expected_embedding

        embedding = self.embedding_model.embed(sample_texts)
        
        # Ensure the embedding is a tensor and has the correct shape
        self.assertTrue(isinstance(embedding, torch.Tensor))
        self.assertEqual(embedding.shape[0], 2)  # Ensure correct number of sentences
        self.assertEqual(embedding.shape[1], 384)  # Ensure correct embedding size

    def test_embed_error_handling(self):
        """Test error handling when embedding generation fails."""
        self.mock_instance.encode.side_effect = Exception("Mocked error")
        sample_text = None

        embedding = self.embedding_model.embed(sample_text)
        self.assertIsNone(embedding)

if __name__ == "__main__":
    unittest.main()
