import pytest
import sys
from unittest.mock import MagicMock, patch
from src.settings.manage_settings import ManageSettings
import src.config as config

class TestManageSettings:
    def test_init(self):
        mock_console = MagicMock()
        with patch('src.config.load_config'):
            manager = ManageSettings(mock_console)
            assert manager.console == mock_console
            assert manager.params_menu is not None
            assert manager.rag_menu is not None

    @patch('questionary.select')
    def test_run_back(self, mock_select):
        mock_console = MagicMock()
        # Mock choice "Back"
        mock_select.return_value.ask.return_value = "Back"
        
        with patch('src.config.load_config'):
            with patch('src.config.save_config', return_value=True):
                manager = ManageSettings(mock_console)
                manager.run()
                
                assert mock_select.called
                mock_console.clear.assert_called_once()

    @patch('questionary.select')
    @patch('src.settings.manage_settings.get_text_input')
    def test_run_user_display_name(self, mock_text_input, mock_select):
        mock_console = MagicMock()
        # Mock choices: first "User Display Name", then "Back"
        mock_select.return_value.ask.side_effect = ["User Display Name", "Back"]
        mock_text_input.return_value = "New Name"
        
        with patch('src.config.load_config'):
            with patch('src.config.save_config', return_value=True):
                manager = ManageSettings(mock_console)
                manager.run()
                
                assert config.USER_DISPLAY_NAME == "New Name"

    @patch('questionary.select')
    def test_configure_model_select(self, mock_select):
        mock_console = MagicMock()
        # Mock "Select from popular models", then "google/gemma-2b-it"
        mock_select.return_value.ask.side_effect = ["Select from popular models", "google/gemma-2b-it"]
        
        manager = ManageSettings(mock_console)
        manager._configure_model(style={})
        
        assert config.MODEL_NAME == "google/gemma-2b-it"

    @patch('questionary.confirm')
    def test_configure_autosave(self, mock_confirm):
        mock_console = MagicMock()
        mock_confirm.return_value.ask.return_value = True
        
        manager = ManageSettings(mock_console)
        manager._configure_autosave(style={})
        
        assert config.AUTOSAVE_ENABLED is True
