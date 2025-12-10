"""Shared pytest fixtures for all tests."""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch

@pytest.fixture
def temp_chats_dir(monkeypatch):
    """Create a temporary chats directory for testing."""
    temp_dir = tempfile.mkdtemp()
    # Patch the CHATS_DIR constant in storage module
    import src.storage as storage_module
    original_dir = storage_module.CHATS_DIR
    storage_module.CHATS_DIR = temp_dir
    yield temp_dir
    shutil.rmtree(temp_dir)
    storage_module.CHATS_DIR = original_dir

@pytest.fixture
def sample_messages():
    """Sample chat messages for testing."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file path for testing."""
    return str(tmp_path / "config.json")

