import logging
from pathlib import Path
from typing import List, Dict, Optional

from src.utils.exceptions import ChatSaveError, ChatLoadError
from .file_io import (
    generate_chat_filename, 
    validate_chat_messages, 
    save_chat_file, 
    load_chat_file
)

logger = logging.getLogger(__name__)


class ChatStorage:
    """
    Manages saving and loading chat history to/from JSON files
    
    This manager handles:
    - Directory management (creation/listing)
    - Filename resolution
    - Resolving paths for pure IO functions
    """
    
    def __init__(self, chats_dir: str = "chats"):
        """
        Initialize chat storage
        
        Args:
            chats_dir: Directory for storing chat files
        """
        self.chats_dir = Path(chats_dir)
        self._ensure_chats_directory()
    
    def _ensure_chats_directory(self) -> None:
        """
        Create chats directory if it doesn't exist
        
        Raises:
            ChatSaveError: If directory cannot be created
        """
        try:
            self.chats_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error(f"Permission denied creating {self.chats_dir}")
            raise ChatSaveError(f"Cannot create chats directory: Permission denied") from e
        except OSError as e:
            logger.error(f"Failed to create chats directory: {e}", exc_info=True)
            raise ChatSaveError(f"Cannot create chats directory: {e}") from e
    
    def save_chat(
        self,
        messages: List[Dict[str, str]],
        filename: Optional[str] = None
    ) -> str:
        """
        Save chat messages to a JSON file
        
        Args:
            messages: List of message dictionaries
            filename: Optional filename. Auto-generated if None
            
        Returns:
            str: The filename used (with .json extension)
            
        Raises:
            ChatSaveError: If chat cannot be saved
            ValueError: If messages list is invalid
        """
        # Validation
        validate_chat_messages(messages)
        
        # Filename Resolution
        if not filename:
            filename = generate_chat_filename()
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.chats_dir / filename
        
        # Execution
        save_chat_file(messages, filepath)
        
        return filename
    
    def load_chat(self, filename: str) -> List[Dict[str, str]]:
        """
        Load chat messages from a JSON file
        
        Args:
            filename: Name of the chat file
            
        Returns:
            List of message dictionaries
            
        Raises:
            ChatLoadError: If chat cannot be loaded
            FileNotFoundError: If chat file doesn't exist
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.chats_dir / filename
        
        return load_chat_file(filepath)
    
    def list_chats(self) -> List[str]:
        """
        List all saved chat files
        
        Returns:
            List of filenames sorted by modification time (newest first)
            
        Raises:
            ChatLoadError: If chats directory cannot be read
        """
        try:
            files = [
                f.name for f in self.chats_dir.glob('*.json')
                if f.is_file()
            ]
            
            # Sort by modification time, newest first
            files.sort(
                key=lambda x: (self.chats_dir / x).stat().st_mtime,
                reverse=True
            )
            
            logger.debug(f"Found {len(files)} chat files")
            return files
            
        except PermissionError as e:
            logger.error(f"Permission denied reading {self.chats_dir}")
            raise ChatLoadError(f"Cannot list chats: Permission denied") from e
        except OSError as e:
            logger.error(f"OS error listing chats: {e}", exc_info=True)
            raise ChatLoadError(f"Failed to list chats: {e}") from e
