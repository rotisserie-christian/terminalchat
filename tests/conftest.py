"""Shared pytest fixtures for all tests."""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch

@pytest.fixture
def temp_chats_dir():
    """Create a temporary chats directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

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

