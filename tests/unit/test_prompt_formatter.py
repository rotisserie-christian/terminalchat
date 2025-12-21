
import pytest
from unittest.mock import MagicMock
from src.models.prompt_formatter import prepare_prompt, _build_messages_with_rag

class TestPromptFormatter:
    
    @pytest.fixture
    def mock_tokenizer(self):
        tokenizer = MagicMock()
        # Mock apply_chat_template to just join messages
        tokenizer.apply_chat_template.side_effect = lambda msgs, tokenize=False, add_generation_prompt=False: \
            " ".join([m['content'] for m in msgs])
        # Mock decode to just return the string
        tokenizer.decode.return_value = "decoded string"
        # Mock plain call to return input keys
        tokenizer.return_value = {"input_ids": [1, 2, 3]}
        return tokenizer

    def test_prepare_prompt_simple(self, mock_tokenizer):
        """Test simple prompt preparation without pruning or RAG"""
        messages = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "hello"}
        ]
        
        prompt = prepare_prompt(messages, mock_tokenizer, max_length=100)
        
        assert prompt == "sys hello"
        mock_tokenizer.apply_chat_template.assert_called()

    def test_prepare_prompt_with_rag(self, mock_tokenizer):
        """Test RAG context injection"""
        messages = [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "hello"}
        ]
        rag_context = "Relevant info"
        
        prompt = prepare_prompt(messages, mock_tokenizer, max_length=100, rag_context=rag_context)
        
        # In prepare_prompt, RAG is injected as a separate system message
        call_args = mock_tokenizer.apply_chat_template.call_args[0][0]
        
        # Should now have 3 messages: System, RAG System, User
        assert len(call_args) == 3
        # Check actual content from _build_messages_with_rag
        assert "# Knowledge Base Context" in call_args[1]['content']
        assert "Relevant info" in call_args[1]['content']

    def test_pruning_logic(self, mock_tokenizer):
        """Test that messages are pruned when exceeding max length"""
        # Create really long messages
        messages = [
            {"role": "system", "content": "sys"},  # Should keep
            {"role": "user", "content": "old"},    # Should prune
            {"role": "assistant", "content": "old_response"}, # Should prune
            {"role": "user", "content": "new"}     # Should keep
        ]
        
        # Mock tokenizer to return increasing lengths
        # 1. Full history -> Too long (150)
        # 2. Pruned 1 -> Still too long (120)
        # 3. Pruned 2 -> Fits (80)
        mock_input = MagicMock()
        mock_input.__getitem__.side_effect = [
            MagicMock(shape=[-1, 150]), # First check: 150 > 100
            MagicMock(shape=[-1, 120]), # Second check: 120 > 100
            MagicMock(shape=[-1, 80])   # Third check: 80 <= 100
        ]
        mock_tokenizer.return_value = mock_input
        
        final_prompt = prepare_prompt(messages, mock_tokenizer, max_length=100)
        
        # Verify apply_chat_template was called multiple times with shrinking lists
        assert mock_tokenizer.apply_chat_template.call_count >= 1
        
        # The final call should have system + last user message
        final_call_msgs = mock_tokenizer.apply_chat_template.call_args[0][0]
        assert final_call_msgs[0]['role'] == 'system'
        assert final_call_msgs[-1]['role'] == 'user'
        assert final_call_msgs[-1]['content'] == 'new'
        # Check that 'old' message is gone
        assert not any(m['content'] == 'old' for m in final_call_msgs)

    def test_build_messages_rag_formatting(self):
        """Test specific formatting of RAG injection"""
        messages = [{"role": "user", "content": "question"}]
        context = "fact"
        
        new_msgs = _build_messages_with_rag(messages, context)
        
        # Verify RAG system message is inserted
        rag_msg = new_msgs[0]
        assert rag_msg['role'] == 'system'
        assert "# Knowledge Base Context" in rag_msg['content']
        assert "fact" in rag_msg['content']
