import pytest
import json
from unittest.mock import patch, mock_open
import src.config as config


class TestConfig:
    
    
    def test_load_config_from_file(self):
        test_config = {
            "model_name": "test-model",
            "user_display_name": "TestUser",
            "model_display_name": "TestModel",
            "primary_color": "red",
            "secondary_color": "yellow"
        }
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(test_config))):
                config.load_config()
                assert config.MODEL_NAME == "test-model"
                assert config.USER_DISPLAY_NAME == "TestUser"
                assert config.MODEL_DISPLAY_NAME == "TestModel"
                assert config.PRIMARY_COLOR == "red"
                assert config.SECONDARY_COLOR == "yellow"
    
    def test_load_config_handles_partial_config(self):
        partial_config = {"model_name": "custom-model"}
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(partial_config))):
                config.load_config()
                assert config.MODEL_NAME == "custom-model"
                assert config.USER_DISPLAY_NAME == config.DEFAULT_USER_DISPLAY_NAME
                assert config.PRIMARY_COLOR == config.DEFAULT_PRIMARY_COLOR
    
    def test_load_config_handles_invalid_json(self):
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="invalid json{[")):
                with pytest.raises(config.ConfigError):
                    config.load_config()
    
    def test_save_config_creates_file(self, tmp_path):
        config_file = tmp_path / "config.json"
        
        with patch('src.config.CONFIG_FILE', str(config_file)):
            config.MODEL_NAME = "test-model"
            config.USER_DISPLAY_NAME = "TestUser"
            config.MODEL_DISPLAY_NAME = "TestModel"
            config.PRIMARY_COLOR = "green"
            config.SECONDARY_COLOR = "blue"
            
            config.save_config()
            
            # save_config returns None on success
            assert config_file.exists()
            
            with open(config_file) as f:
                data = json.load(f)
                assert data["model_name"] == "test-model"
                assert data["user_display_name"] == "TestUser"
                assert data["model_display_name"] == "TestModel"
                assert data["primary_color"] == "green"
                assert data["secondary_color"] == "blue"
    
    def test_save_config_handles_write_error(self):
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(config.ConfigError):
                config.save_config()