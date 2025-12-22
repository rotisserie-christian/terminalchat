import pytest
import os
import pickle
import numpy as np
from src.rag.embeddings_cache import EmbeddingsCache
from src.utils.exceptions import CacheError
from unittest.mock import MagicMock, patch, mock_open

class TestEmbeddingsCache:
    def test_init(self):
        cache = EmbeddingsCache("test_cache.pkl")
        assert cache.cache_file == "test_cache.pkl"
        assert cache.cache == {}

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=pickle.dumps({"file.md": {"timestamp": 1.0, "chunks": [], "embeddings": []}}))
    def test_load_success(self, mock_file, mock_exists):
        mock_exists.return_value = True
        cache = EmbeddingsCache()
        assert cache.load("dummy_dir") is True
        assert "file.md" in cache.cache

    @patch('os.path.exists')
    def test_load_no_file(self, mock_exists):
        mock_exists.return_value = False
        cache = EmbeddingsCache()
        assert cache.load("dummy_dir") is True
        assert cache.cache == {}

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"not a pickle")
    def test_load_corrupted(self, mock_file, mock_exists):
        mock_exists.return_value = True
        cache = EmbeddingsCache()
        with pytest.raises(CacheError):
            cache.load("dummy_dir")

    @patch('src.rag.embeddings_cache.atomic_write_pickle')
    @patch('os.makedirs')
    def test_save_success(self, mock_makedirs, mock_atomic_write):
        cache = EmbeddingsCache()
        cache.cache = {"test": "data"}
        assert cache.save("dummy_dir") is True
        mock_makedirs.assert_called_once()
        mock_atomic_write.assert_called_once()

    @patch('os.path.getmtime')
    def test_get_hit(self, mock_mtime):
        mock_mtime.return_value = 100.0
        cache = EmbeddingsCache()
        cache.cache = {
            "test.md": {
                "timestamp": 100.0,
                "chunks": ["chunk1"],
                "embeddings": [[0.1, 0.2]]
            }
        }
        result = cache.get("test.md", "path/to/test.md")
        assert result is not None
        chunks, embeddings = result
        assert chunks == ["chunk1"]
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.dtype == np.float32

    @patch('os.path.getmtime')
    def test_get_miss_modified(self, mock_mtime):
        mock_mtime.return_value = 200.0
        cache = EmbeddingsCache()
        cache.cache = {
            "test.md": {
                "timestamp": 100.0,
                "chunks": ["chunk1"],
                "embeddings": [[0.1, 0.2]]
            }
        }
        assert cache.get("test.md", "path/to/test.md") is None

    @patch('os.path.getmtime')
    def test_set(self, mock_mtime):
        mock_mtime.return_value = 100.0
        cache = EmbeddingsCache()
        cache.set("test.md", "path/to/test.md", ["chunk1"], np.array([[0.1, 0.2]]))
        assert "test.md" in cache.cache
        assert cache.cache["test.md"]["timestamp"] == 100.0
        assert cache.cache["test.md"]["embeddings"] == [[0.1, 0.2]]

    def test_invalidate(self):
        cache = EmbeddingsCache()
        cache.cache = {"test.md": {}}
        cache.invalidate("test.md")
        assert "test.md" not in cache.cache

    def test_clean(self):
        cache = EmbeddingsCache()
        cache.cache = {"exists.md": {}, "deleted.md": {}}
        cache.clean(["exists.md"])
        assert "exists.md" in cache.cache
        assert "deleted.md" not in cache.cache

    def test_clear(self):
        cache = EmbeddingsCache()
        cache.cache = {"a": 1}
        cache.clear()
        assert cache.cache == {}

    def test_get_stats(self):
        cache = EmbeddingsCache()
        cache.cache = {
            "f1.md": {"chunks": ["c1", "c2"]},
            "f2.md": {"chunks": ["c3"]}
        }
        stats = cache.get_stats()
        assert stats['num_files'] == 2
        assert stats['total_chunks'] == 3
        assert "f1.md" in stats['files']
