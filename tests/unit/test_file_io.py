
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.storage.file_io import (
    generate_chat_filename,
    validate_chat_messages,
    save_chat_file,
    load_chat_file
)
from src.utils.exceptions import ChatSaveError, ChatLoadError

class TestFileIO:
    @pytest.fixture
    def valid_messages(self):
        return [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"}
        ]

    # --- Filename Generation ---
    def test_generate_chat_filename_format(self):
        """Test that generated filename matches expected timestamp format"""
        filename = generate_chat_filename()
        assert filename.startswith("chat_")
        assert filename.endswith(".json")
        # Check basic length: chat_YYYYMMDD_HHMMSS.json is 20+ chars
        assert len(filename) > 15

    # --- Validation ---
    def test_validate_valid_messages(self, valid_messages):
        """Test validation with correct input does not raise error"""
        validate_chat_messages(valid_messages)

    def test_validate_empty_list(self):
        """Test validation fails with empty list"""
        with pytest.raises(ValueError, match="Cannot save empty message list"):
            validate_chat_messages([])

    def test_validate_not_a_list(self):
        """Test validation fails with non-list input"""
        with pytest.raises(ValueError, match="must be a list"):
            validate_chat_messages("not a list")

    def test_validate_invalid_message_dict(self):
        """Test validation fails with invalid message dict"""
        messages = [{"role": "user"}] # Missing content
        with pytest.raises(ValueError, match="missing 'role' or 'content'"):
            validate_chat_messages(messages)

    def test_validate_non_dict_message(self):
        """Test validation fails with non-dict message"""
        messages = ["string message"]
        with pytest.raises(ValueError, match="must be a dict"):
            validate_chat_messages(messages)

    # --- Load/Save ---
    def test_save_chat_file_calls_atomic_write(self, tmp_path, valid_messages):
        """Test that save_chat_file delegates to atomic_write_json"""
        filepath = tmp_path / "test_chat.json"
        
        with patch("src.storage.file_io.atomic_write_json") as mock_write:
            save_chat_file(valid_messages, filepath)
            mock_write.assert_called_once_with(valid_messages, filepath)

    def test_save_chat_file_handles_error(self, tmp_path, valid_messages):
        """Test that save_chat_file wraps exceptions in ChatSaveError"""
        filepath = tmp_path / "test_chat.json"
        
        with patch("src.storage.file_io.atomic_write_json") as mock_write:
            mock_write.side_effect = OSError("Disk full")
            
            with pytest.raises(ChatSaveError, match="Failed to save chat"):
                save_chat_file(valid_messages, filepath)

    def test_load_chat_file_success(self, tmp_path, valid_messages):
        """Test loading a valid chat file"""
        import json
        filepath = tmp_path / "test_chat.json"
        with open(filepath, 'w') as f:
            json.dump(valid_messages, f)
            
        loaded = load_chat_file(filepath)
        assert loaded == valid_messages

    def test_load_chat_file_not_found(self, tmp_path):
        """Test loading non-existent file"""
        filepath = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            load_chat_file(filepath)

    def test_load_chat_file_corrupted(self, tmp_path):
        """Test loading corrupted JSON raises ChatLoadError"""
        filepath = tmp_path / "bad.json"
        with open(filepath, 'w') as f:
            f.write("{ invalid json")
            
        with pytest.raises(ChatLoadError, match="Chat file is corrupted"):
            load_chat_file(filepath)

    def test_load_chat_file_invalid_format(self, tmp_path):
        """Test loading valid JSON that isn't a list raises ChatLoadError"""
        filepath = tmp_path / "params.json"
        import json
        with open(filepath, 'w') as f:
            json.dump({"key": "value"}, f) # Dict, not list
            
        with pytest.raises(ChatLoadError, match="Invalid chat file format"):
            load_chat_file(filepath)
