import json
import os
from datetime import datetime
from typing import List, Dict

CHATS_DIR = "chats"

class ChatStorage:
    def __init__(self):
        self.ensure_chats_directory()

    def ensure_chats_directory(self):
        if not os.path.exists(CHATS_DIR):
            os.makedirs(CHATS_DIR)

    def save_chat(self, messages: List[Dict[str, str]], filename: str = None) -> str:
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
        if not filename.endswith('.json'):
            filename += '.json'
            
        filepath = os.path.join(CHATS_DIR, filename)
        if not os.path.exists(filepath):
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_chats(self) -> List[str]:
        self.ensure_chats_directory()
        files = [f for f in os.listdir(CHATS_DIR) if f.endswith('.json')]
        # Sort by modification time, newest first
        files.sort(key=lambda x: os.path.getmtime(os.path.join(CHATS_DIR, x)), reverse=True)
        return files
