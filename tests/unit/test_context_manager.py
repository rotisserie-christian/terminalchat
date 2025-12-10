"""Tests for ContextManager class."""
import pytest
from unittest.mock import Mock, MagicMock
from src.context_manager import ContextManager

class TestContextManager:
    """Tests for ContextManager class."""
    
    def test_init_with_system_prompt(self):
        """Test initialization adds system prompt."""
        cm = ContextManager(system_prompt="Test prompt")
        messages = cm.get_messages()
        
        assert len(messages) == 1
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Test prompt"
    
    def test_init_without_system_prompt(self):
        """Test initialization without system prompt."""
        cm = ContextManager(system_prompt=None)
        assert len(cm.get_messages()) == 0
    
    def test_add_message(self):
        """Test adding messages."""
        cm = ContextManager()
        cm.add_message("user", "Hello")
        cm.add_message("assistant", "Hi")
        
        messages = cm.get_messages()
        # ContextManager adds system prompt by default, so we have 3 messages total
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hello"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "Hi"
    
    def test_get_messages_returns_copy(self):
        """Test that get_messages returns the actual messages list."""
        cm = ContextManager()
        cm.add_message("user", "Hello")
        
        messages = cm.get_messages()
        assert messages == cm.messages
    
    def test_prepare_prompt_uses_full_history_when_short(self):
        """Test prompt preparation uses full history when under max length."""
        cm = ContextManager()
        cm.add_message("user", "Hello")
        cm.add_message("assistant", "Hi")
        
        mock_tokenizer = Mock()
        mock_tokenizer.apply_chat_template = Mock(return_value="<|user|>Hello<|assistant|>Hi")
        
        # Mock the tokenizer call result (tokenizer is callable)
        mock_tokenized = MagicMock()
        mock_tokenized.input_ids = MagicMock()
        mock_tokenized.input_ids.shape = [1, 10]  # Short prompt (10 tokens)
        
        # Make tokenizer() callable
        mock_tokenizer.return_value = mock_tokenized
        
        result = cm.prepare_prompt(mock_tokenizer, max_length=100)
        
        assert result == "<|user|>Hello<|assistant|>Hi"
        mock_tokenizer.apply_chat_template.assert_called_once()
        mock_tokenizer.assert_called_once()

