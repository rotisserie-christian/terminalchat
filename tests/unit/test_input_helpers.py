import pytest
import sys
from unittest.mock import MagicMock, patch
from src.settings.input_helpers import get_text_input, get_float_input, get_int_input

class TestInputHelpers:
    @patch('src.settings.input_helpers.PromptSession')
    def test_get_text_input(self, MockSession):
        mock_session_instance = MockSession.return_value
        mock_session_instance.prompt.return_value = "user input"
        
        mock_console = MagicMock()
        result = get_text_input(mock_console, "Label", "default")
        
        assert result == "user input"
        mock_console.print.assert_called()

    @patch('src.settings.input_helpers.PromptSession')
    def test_get_float_input_valid(self, MockSession):
        mock_session_instance = MockSession.return_value
        mock_session_instance.prompt.return_value = "1.5"
        
        mock_console = MagicMock()
        result = get_float_input(mock_console, "Label", 1.0, 0.0, 2.0)
        
        assert result == 1.5

    @patch('src.settings.input_helpers.PromptSession')
    def test_get_float_input_invalid_then_valid(self, MockSession):
        mock_session_instance = MockSession.return_value
        # First call invalid (out of range), second call valid
        mock_session_instance.prompt.side_effect = ["5.0", "1.5"]
        
        mock_console = MagicMock()
        result = get_float_input(mock_console, "Label", 1.0, 0.0, 2.0)
        
        assert result == 1.5
        assert mock_console.print.called

    @patch('src.settings.input_helpers.PromptSession')
    def test_get_int_input_valid(self, MockSession):
        mock_session_instance = MockSession.return_value
        mock_session_instance.prompt.return_value = "10"
        
        mock_console = MagicMock()
        result = get_int_input(mock_console, "Label", 5, 0, 20)
        
        assert result == 10

    @patch('src.settings.input_helpers.PromptSession')
    def test_get_int_input_invalid_string(self, MockSession):
        mock_session_instance = MockSession.return_value
        mock_session_instance.prompt.side_effect = ["not an int", "10"]
        
        mock_console = MagicMock()
        result = get_int_input(mock_console, "Label", 5, 0, 20)
        
        assert result == 10
        assert mock_console.print.called
