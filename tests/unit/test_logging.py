import logging
import os
from pathlib import Path
from src.utils.logging import setup_logging
from unittest.mock import patch, MagicMock

def test_setup_logging():
    with patch('pathlib.Path.mkdir') as mock_mkdir:
        with patch('logging.handlers.RotatingFileHandler') as mock_handler:
            with patch('logging.getLogger') as mock_get_logger:
                mock_root_logger = MagicMock()
                mock_get_logger.return_value = mock_root_logger
                
                setup_logging(log_file="test.log", level="DEBUG")
                
                # Check if directory creation was called
                mock_mkdir.assert_called_with(parents=True, exist_ok=True)
                
                # Check if handlers were added
                assert mock_root_logger.addHandler.called
                
                # Check if levels were set (the last call to setLevel is for silencing libraries)
                # but we want to check the initial setLevel call.
                # Actually setup_logging calls setLevel(DEBUG) then later silences others.
                # The failure showed setLevel(30) which is WARNING. 
                # Let's just check if it was called with DEBUG at some point.
                mock_root_logger.setLevel.assert_any_call(logging.DEBUG)

def test_setup_logging_no_file():
    # Test with default arguments
    with patch('pathlib.Path.mkdir'):
        with patch('logging.handlers.RotatingFileHandler'):
            with patch('logging.getLogger'):
                setup_logging()
                # Should not crash
