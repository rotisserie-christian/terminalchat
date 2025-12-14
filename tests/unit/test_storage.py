import pytest
import os
import time
from src.storage import ChatStorage


class TestChatStorage:
    
    def test_save_chat_with_filename(self, temp_chats_dir, sample_messages):
        storage = ChatStorage()
        filename = storage.save_chat(sample_messages, "test_chat.json")
        
        assert filename == "test_chat.json"
        assert os.path.exists(os.path.join(temp_chats_dir, "test_chat.json"))
    
    def test_save_chat_auto_generates_filename(self, temp_chats_dir, sample_messages):
        storage = ChatStorage()
        filename = storage.save_chat(sample_messages)
        
        assert filename.startswith("chat_")
        assert filename.endswith(".json")
        assert os.path.exists(os.path.join(temp_chats_dir, filename))
    
    def test_save_chat_adds_json_extension(self, temp_chats_dir, sample_messages):
        storage = ChatStorage()
        filename = storage.save_chat(sample_messages, "test_chat")
        
        assert filename == "test_chat.json"
    
    def test_load_chat_returns_messages(self, temp_chats_dir, sample_messages):
        storage = ChatStorage()
        storage.save_chat(sample_messages, "test_chat.json")
        
        loaded = storage.load_chat("test_chat.json")
        
        assert len(loaded) == 2
        assert loaded[0]["role"] == "user"
        assert loaded[0]["content"] == "Hello"
        assert loaded[1]["role"] == "assistant"
        assert loaded[1]["content"] == "Hi there"
    
    def test_load_chat_handles_missing_file(self, temp_chats_dir):
        storage = ChatStorage()
        loaded = storage.load_chat("nonexistent.json")
        
        assert loaded == []
    
    def test_load_chat_adds_json_extension(self, temp_chats_dir, sample_messages):
        storage = ChatStorage()
        storage.save_chat(sample_messages, "test_chat.json")
        
        loaded = storage.load_chat("test_chat")
        assert len(loaded) == 2
    
    def test_list_chats_returns_json_files(self, temp_chats_dir, sample_messages):
        storage = ChatStorage()
        storage.save_chat(sample_messages, "chat1.json")
        storage.save_chat(sample_messages, "chat2.json")
        
        chats = storage.list_chats()
        
        assert len(chats) == 2
        assert "chat1.json" in chats
        assert "chat2.json" in chats
    
    def test_list_chats_sorts_newest_first(self, temp_chats_dir, sample_messages):
        storage = ChatStorage()
        
        storage.save_chat(sample_messages, "chat1.json")
        time.sleep(0.1)  # Ensure different timestamps
        storage.save_chat(sample_messages, "chat2.json")
        
        chats = storage.list_chats()
        assert chats[0] == "chat2.json"