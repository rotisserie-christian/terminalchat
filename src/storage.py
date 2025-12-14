import json
import os
from datetime import datetime
from typing import List, Dict

CHATS_DIR = "chats"

class ChatStorage:
    """
    Manages saving and loading chat history to/from JSON files.
    
    Stores chat sessions in the chats/ directory with timestamps.
    """

    def __init__(self):
        self.ensure_chats_directory()

    def ensure_chats_directory(self):
        """
        Create chats directory if it doesn't exist
        """

        if not os.path.exists(CHATS_DIR):
            os.makedirs(CHATS_DIR)

    def save_chat(self, messages: List[Dict[str, str]], filename: str = None) -> str:
        """
        Save chat messages to a JSON file
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' strings
            filename: Optional filename. If None, generates timestamp-based name
            
        Returns:
            str: The filename used (with .json extension)
        """

        self.ensure_chats_directory()
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_{timestamp}.json"
        
        # Ensure extension
        if not filename.endswith('.json'):
            filename += '.json'

        filepath = os.path.join(CHATS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        return filename

    def load_chat(self, filename: str) -> List[Dict[str, str]]:
        """
        Load chat messages from a JSON file
        
        Args:
            filename: Name of the chat file (with or without .json extension)
            
        Returns:
            List of message dictionaries, or empty list if file not found
        """

        # Ensure extension
        if not filename.endswith('.json'):
            filename += '.json'
            
        filepath = os.path.join(CHATS_DIR, filename)
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_chats(self) -> List[str]:
        """
        List all saved chat files
        
        Returns:
            List of filenames sorted by modification time (newest first)
        """

        self.ensure_chats_directory()
        files = [f for f in os.listdir(CHATS_DIR) if f.endswith('.json')]
        # Sort by modification time, newest first
        files.sort(key=lambda x: os.path.getmtime(os.path.join(CHATS_DIR, x)), reverse=True)
        return files
