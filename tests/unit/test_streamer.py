
import pytest
from unittest.mock import MagicMock, patch
from src.models.streamer import stream_response
import src.config as config

class TestStreamer:
    @pytest.fixture
    def mock_deps(self):
        """Mock all external dependencies for streaming"""
        with patch("src.models.streamer.TextIteratorStreamer") as MockStreamer, \
             patch("src.models.streamer.Thread") as MockThread:
            
            # Setup streamer iterator
            streamer_instance = MockStreamer.return_value
            streamer_instance.__iter__.return_value = ["Hello", " world", "<|im_end|>"]
            
            yield {
                "Streamer": MockStreamer,
                "Thread": MockThread,
                "streamer_instance": streamer_instance
            }

    def test_stream_response_yields_tokens(self, mock_deps):
        """Test basic token yielding"""
        model = MagicMock()
        tokenizer = MagicMock()
        prompt = "Test prompt"
        
        # Collect yielded tokens
        tokens = list(stream_response(model, tokenizer, prompt))
        
        assert tokens == ["Hello", " world"]
        # Verify thread started
        mock_deps["Thread"].return_value.start.assert_called_once()
        
        # Verify generation called with streamer
        # Inspect the kwargs passed to the Thread constructor
        thread_call_kwargs = mock_deps["Thread"].call_args[1]['kwargs']
        assert "streamer" in thread_call_kwargs

    def test_stream_response_stops_at_im_end(self, mock_deps):
        """Test that stream stops cleanly at end token"""
        # Setup specific token sequence
        mock_deps["streamer_instance"].__iter__.return_value = ["Start", "Middle", "<|im_end|>", "Ignored"]
        
        model = MagicMock()
        tokenizer = MagicMock()
        
        tokens = list(stream_response(model, tokenizer, "prompt"))
        
        assert tokens == ["Start", "Middle"]
        assert "Ignored" not in tokens

    def test_stream_response_uses_config_defaults(self, mock_deps):
        """Test usage of config values when args not provided"""
        model = MagicMock()
        tokenizer = MagicMock()
        
        # Override config temporarily
        with patch.object(config, 'MAX_NEW_TOKENS', 123), \
             patch.object(config, 'TEMPERATURE', 0.5):
            
            list(stream_response(model, tokenizer, "prompt"))
            
            # Check generation args passed to thread
            thread_call = mock_deps["Thread"].call_args
            gen_kwargs = thread_call[1]['kwargs']
            
            assert gen_kwargs['max_new_tokens'] == 123
            assert gen_kwargs['temperature'] == 0.5

    def test_stream_response_overrides_config(self, mock_deps):
        """Test explicit args override config"""
        model = MagicMock()
        tokenizer = MagicMock()
        
        list(stream_response(
            model, 
            tokenizer, 
            "prompt", 
            max_new_tokens=999, 
            temperature=0.1
        ))
        
        thread_call = mock_deps["Thread"].call_args
        gen_kwargs = thread_call[1]['kwargs']
        
        assert gen_kwargs['max_new_tokens'] == 999
        assert gen_kwargs['temperature'] == 0.1
