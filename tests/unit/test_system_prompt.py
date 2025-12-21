from unittest.mock import patch
from src.system_prompt import load_system_prompt, get_default_prompt, DEFAULT_SYSTEM_PROMPT


class TestSystemPrompt:
    
    def test_load_system_prompt_returns_file_content(self, tmp_path):
        """Test loading system prompt from file"""
        prompt_file = tmp_path / "system.md"
        prompt_file.write_text("Custom system prompt", encoding="utf-8")
        
        with patch('src.system_prompt.ACTIVE_PROMPT_PATH', prompt_file):
            result = load_system_prompt()
            assert result == "Custom system prompt"
    
    def test_load_system_prompt_returns_default_when_file_missing(self, tmp_path):
        """Test fallback to default when file doesn't exist"""
        nonexistent_file = tmp_path / "nonexistent.md"
        
        with patch('src.system_prompt.ACTIVE_PROMPT_PATH', nonexistent_file):
            result = load_system_prompt()
            assert result == DEFAULT_SYSTEM_PROMPT
    
    def test_load_system_prompt_returns_default_when_file_empty(self, tmp_path):
        """Test fallback to default when file is empty"""
        empty_file = tmp_path / "empty.md"
        empty_file.write_text("   \n  \t  ", encoding="utf-8")  # Whitespace only
        
        with patch('src.system_prompt.ACTIVE_PROMPT_PATH', empty_file):
            result = load_system_prompt()
            assert result == DEFAULT_SYSTEM_PROMPT
    
    
    def test_get_default_prompt_returns_constant(self):
        """Test that get_default_prompt returns the default"""
        result = get_default_prompt()
        assert result == DEFAULT_SYSTEM_PROMPT
        assert result == "Keep your answers brief and concise, do not ramble."
