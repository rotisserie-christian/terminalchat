
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from src.utils.atomic_writes import (
    atomic_write_json,
    atomic_write_text,
    atomic_write_binary,
    atomic_write_pickle
)

class TestAtomicWrites:
    @pytest.fixture
    def temp_file(self, tmp_path):
        return tmp_path / "test_file"

    def test_atomic_write_json_success(self, temp_file):
        """Test successful JSON atomic write"""
        data = {"key": "value"}
        atomic_write_json(data, temp_file)
        
        assert temp_file.exists()
        assert not temp_file.with_suffix('.tmp').exists()
        # Verify content
        import json
        with open(temp_file) as f:
            assert json.load(f) == data

    def test_atomic_write_text_success(self, temp_file):
        """Test successful text atomic write"""
        content = "test content"
        atomic_write_text(content, temp_file)
        
        assert temp_file.exists()
        assert not temp_file.with_suffix('.tmp').exists()
        with open(temp_file) as f:
            assert f.read() == content

    def test_atomic_write_binary_success(self, temp_file):
        """Test successful binary atomic write"""
        data = b"binary data"
        atomic_write_binary(data, temp_file)
        
        assert temp_file.exists()
        with open(temp_file, 'rb') as f:
            assert f.read() == data

    def test_atomic_write_pickle_success(self, temp_file):
        """Test successful pickle atomic write"""
        import pickle
        data = {"key": "value"}
        atomic_write_pickle(data, temp_file)
        
        assert temp_file.exists()
        with open(temp_file, 'rb') as f:
            assert pickle.load(f) == data

    def test_atomic_write_overwrite_existing(self, temp_file):
        """Test overwriting an existing file works correctly"""
        # Create initial file
        atomic_write_text("initial", temp_file)
        assert temp_file.read_text() == "initial"
        
        # Overwrite
        atomic_write_text("new content", temp_file)
        assert temp_file.read_text() == "new content"
        assert not temp_file.with_suffix('.tmp').exists()

    def test_atomic_write_json_failure_cleans_up(self, temp_file):
        """Test that temp file is cleaned up if JSON dump fails"""
        # Object that fails serialization
        class Unserializable:
            pass
            
        with pytest.raises(Exception):
            atomic_write_json(Unserializable(), temp_file)
            
        assert not temp_file.exists()
        assert not temp_file.with_suffix('.tmp').exists()

    def test_atomic_write_permission_error_cleanup(self, temp_file):
        """Test cleanup when rename fails due to permissions"""
        data = {"test": "data"}
        
        # We allow the open() call but mock the rename to fail
        with patch('pathlib.Path.rename') as mock_rename:
            mock_rename.side_effect = PermissionError("Access denied")
            
            with pytest.raises(PermissionError):
                atomic_write_json(data, temp_file)
                
            # The original file shouldn't exist (rename failed)
            assert not temp_file.exists()
            # The temp file should be gone (cleanup in exception handler)
            assert not temp_file.with_suffix('.tmp').exists()
