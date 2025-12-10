from src.storage import ChatStorage
import os
import shutil

def test_storage():
    print("Testing ChatStorage...")
    storage = ChatStorage()
    
    # Clean up chats dir for test
    if os.path.exists("chats"):
        # Don't delete if there are real chats, but maybe backup?
        # For this test, we'll just check if we can save and load unique file
        pass

    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]
    
    filename = "test_chat.json"
    print(f"Saving chat to {filename}...")
    saved_name = storage.save_chat(messages, filename)
    
    assert saved_name == filename
    assert os.path.exists(os.path.join("chats", filename))
    
    print("Loading chat...")
    loaded_messages = storage.load_chat(saved_name)
    assert len(loaded_messages) == 2
    assert loaded_messages[0]["content"] == "Hello"
    
    print("Listing chats...")
    chats = storage.list_chats()
    assert filename in chats
    
    # Clean up
    os.remove(os.path.join("chats", filename))
    print("Storage tests passed!")

if __name__ == "__main__":
    test_storage()
