import pytest
import numpy as np
from src.rag.embeddings import chunk_text, cosine_similarity, EmbeddingModel
from unittest.mock import MagicMock, patch

def test_chunk_text_basic():
    text = "This is a test. This is only a test."
    chunks = chunk_text(text, chunk_size=15, overlap=0)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)

def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []

def test_chunk_text_with_overlap():
    text = "word1 word2 word3 word4"
    chunks = chunk_text(text, chunk_size=10, overlap=5)
    assert len(chunks) > 1

def test_cosine_similarity():
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    sims = cosine_similarity(v1, v2)
    assert np.allclose(sims, [1.0, 0.0])

class TestEmbeddingModel:
    @patch('src.rag.embeddings.SentenceTransformer')
    def test_load_success(self, MockST):
        model = EmbeddingModel("test-model")
        assert model.load() is True
        MockST.assert_called_once_with("test-model")
        assert model.model is not None

    @patch('src.rag.embeddings.SentenceTransformer')
    def test_load_failure(self, MockST):
        MockST.side_effect = Exception("Load failed")
        model = EmbeddingModel("test-model")
        assert model.load() is False

    @patch('src.rag.embeddings.SentenceTransformer')
    def test_encode(self, MockST):
        mock_instance = MockST.return_value
        mock_instance.encode.return_value = np.array([[0.1, 0.2]])
        
        model = EmbeddingModel()
        model.load()
        
        texts = ["hello"]
        embeddings = model.encode(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (1, 2)
        assert embeddings.dtype == np.float32

    @patch('src.rag.embeddings.SentenceTransformer')
    def test_encode_empty(self, MockST):
        model = EmbeddingModel()
        model.load()
        assert model.encode([]).size == 0

    @patch('src.rag.embeddings.SentenceTransformer')
    def test_encode_single(self, MockST):
        mock_instance = MockST.return_value
        mock_instance.encode.return_value = np.array([[0.1, 0.2]])
        
        model = EmbeddingModel()
        model.load()
        
        emb = model.encode_single("hello")
        assert emb.shape == (2,)
        assert emb.dtype == np.float32
