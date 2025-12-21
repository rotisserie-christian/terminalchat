import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from src.utils.exceptions import ChatSaveError, ChatLoadError
from src.utils.atomic_writes import atomic_write_json

logger = logging.getLogger(__name__)


def generate_chat_filename() -> str:
    """Generate a timestamped filename for a new chat"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"chat_{timestamp}.json"


def validate_chat_messages(messages: List[Dict[str, str]]) -> None:
    """
    Validate the structure of a message list
    
    Raises:
        ValueError: If structure is invalid
    """
    if not messages:
        raise ValueError("Cannot save empty message list")
    
    if not isinstance(messages, list):
        raise ValueError(f"Messages must be a list, got {type(messages)}")
    
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            raise ValueError(f"Message {i} must be a dict, got {type(msg)}")
        if 'role' not in msg or 'content' not in msg:
            raise ValueError(f"Message {i} missing 'role' or 'content' keys")


def save_chat_file(messages: List[Dict[str, str]], filepath: Path) -> None:
    """
    Save validated messages to the specified path using atomic write
    
    Raises:
        ChatSaveError: If saving fails
    """
    try:
        atomic_write_json(messages, filepath)
        
        logger.info(
            f"Chat saved successfully",
            extra={
                'chat_filename': filepath.name,
                'num_messages': len(messages),
                'size_bytes': filepath.stat().st_size if filepath.exists() else 0
            }
        )
    except PermissionError as e:
        logger.error(f"Permission denied writing {filepath}")
        raise ChatSaveError(f"Cannot write chat file: Permission denied") from e
    except OSError as e:
        logger.error(f"OS error saving chat: {e}", exc_info=True)
        raise ChatSaveError(f"Failed to save chat: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error saving chat: {e}", exc_info=True)
        raise ChatSaveError(f"Failed to save chat: {e}") from e


def load_chat_file(filepath: Path) -> List[Dict[str, str]]:
    """
    Load and validate messages from the specified path
    
    Returns:
        List of message dictionaries
        
    Raises:
        ChatLoadError: If loading fails or format is invalid
        FileNotFoundError: If file doesn't exist
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Chat file not found: {filepath.name}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        if not isinstance(messages, list):
            raise ChatLoadError(
                f"Invalid chat file format: expected list, got {type(messages)}"
            )
        
        logger.info(
            f"Chat loaded successfully",
            extra={
                'chat_filename': filepath.name,
                'num_messages': len(messages)
            }
        )
        return messages
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath.name}: {e}", exc_info=True)
        raise ChatLoadError(f"Chat file is corrupted: {e}") from e
    except PermissionError as e:
        logger.error(f"Permission denied reading {filepath}")
        raise ChatLoadError(f"Cannot read chat file: Permission denied") from e
    except OSError as e:
        logger.error(f"OS error loading chat: {e}", exc_info=True)
        raise ChatLoadError(f"Failed to load chat: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading chat: {e}", exc_info=True)
        raise ChatLoadError(f"Failed to load chat: {e}") from e
