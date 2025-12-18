import logging
from pathlib import Path
from typing import List, Dict, Optional
from .exceptions import ChatSaveError, ChatLoadError

logger = logging.getLogger(__name__)

class ChatStorage:
    def __init__(self, chats_dir: str = "chats"):
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
            raise ChatSaveError(
                f"Cannot create chats directory: Permission denied"
            ) from e
        except OSError as e:
            logger.error(f"Failed to create chats directory: {e}", exc_info=True)
            raise ChatSaveError(
                f"Cannot create chats directory: {e}"
            ) from e
    
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

        if not messages:
            raise ValueError("Cannot save empty message list")
        
        if not isinstance(messages, list):
            raise ValueError(f"Messages must be a list, got {type(messages)}")
        
        # Validate message structure
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                raise ValueError(f"Message {i} must be a dict, got {type(msg)}")
            if 'role' not in msg or 'content' not in msg:
                raise ValueError(f"Message {i} missing 'role' or 'content' keys")
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = self.chats_dir / filename
        
        # Don't overwrite existing files without explicit filename
        if filepath.exists() and not filename:
            logger.warning(f"File {filename} already exists, generating new name")
            counter = 1
            while filepath.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_{timestamp}_{counter}.json"
                filepath = self.chats_dir / filename
                counter += 1
        
        try:
            # Write to temp file first (atomic write)
            temp_path = filepath.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_path.replace(filepath)
            
            logger.info(
                f"Chat saved successfully",
                extra={
                    'filename': filename,
                    'num_messages': len(messages),
                    'size_bytes': filepath.stat().st_size
                }
            )
            return filename
            
        except PermissionError as e:
            logger.error(f"Permission denied writing {filepath}")
            raise ChatSaveError(f"Cannot write chat file: Permission denied") from e
        except OSError as e:
            logger.error(f"OS error saving chat: {e}", exc_info=True)
            raise ChatSaveError(f"Failed to save chat: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error saving chat: {e}", exc_info=True)
            raise ChatSaveError(f"Failed to save chat: {e}") from e
    
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
        
        if not filepath.exists():
            raise FileNotFoundError(f"Chat file not found: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            if not isinstance(messages, list):
                raise ChatLoadError(
                    f"Invalid chat file format: expected list, got {type(messages)}"
                )
            
            logger.info(
                f"Chat loaded successfully",
                extra={'filename': filename, 'num_messages': len(messages)}
            )
            return messages
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}", exc_info=True)
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
            raise ChatLoadError(
                f"Cannot list chats: Permission denied"
            ) from e
        except OSError as e:
            logger.error(f"OS error listing chats: {e}", exc_info=True)
            raise ChatLoadError(f"Failed to list chats: {e}") from e