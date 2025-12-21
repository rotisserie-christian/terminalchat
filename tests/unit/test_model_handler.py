
import pytest
from unittest.mock import MagicMock, patch
from src.models import ModelHandler
import src.config as config

@pytest.fixture
def mock_tokenizer():
    tokenizer = MagicMock()
    tokenizer.return_value = {"input_ids": MagicMock()}
    tokenizer.model_max_length = 2048
    return tokenizer

@pytest.fixture
def mock_model():
    model = MagicMock()
    model.config.max_position_embeddings = 2048
    return model

@pytest.fixture
def model_handler(mock_tokenizer, mock_model):
    with patch("src.models.handler.AutoTokenizer.from_pretrained", return_value=mock_tokenizer), \
         patch("src.models.handler.AutoModelForCausalLM.from_pretrained", return_value=mock_model):
        handler = ModelHandler()
        return handler

class TestModelHandler:
    
    def test_init_defaults(self):
        handler = ModelHandler()
        assert handler.model_name == "HuggingFaceTB/SmolLM-135M-Instruct"
        assert handler.context_window == 2048  # Default
        
    @patch("src.models.handler.torch.cuda.is_available", return_value=True)
    def test_init_cuda_available(self, mock_cuda):
        handler = ModelHandler()
        assert handler.device == "cuda"
        
    @patch("src.models.handler.torch.cuda.is_available", return_value=False)
    def test_init_cpu_only(self, mock_cuda):
        handler = ModelHandler()
        assert handler.device == "cpu"

    @patch("src.models.handler.AutoTokenizer.from_pretrained")
    @patch("src.models.handler.AutoModelForCausalLM.from_pretrained")
    def test_load_success(self, mock_model_cls, mock_tokenizer_cls):
        handler = ModelHandler()
        # Setup mocks to ensure no exceptions
        mock_model = MagicMock()
        mock_model_cls.return_value = mock_model
        mock_tokenizer = MagicMock()
        mock_tokenizer.model_max_length = 2048
        mock_tokenizer_cls.return_value = mock_tokenizer
        
        success = handler.load()
        
        # If it failed, we can't see the exception easily in this test structure, 
        # but we can assert success is True. 
        # Common failure point: mock_model.to() if on CPU. MagicMock handle this.
        assert success is True
        assert handler.model is not None
        assert handler.tokenizer is not None
        mock_tokenizer_cls.assert_called_once()
        mock_model_cls.assert_called_once()
        
    @patch("src.models.handler.AutoTokenizer.from_pretrained", side_effect=Exception("Download failed"))
    def test_load_failure(self, mock_tokenizer_cls):
        handler = ModelHandler()
        success = handler.load()
        
        assert success is False
        assert handler.model is None
        assert handler.tokenizer is None

    def test_detect_context_window_tokenizer(self, model_handler, mock_tokenizer):
        mock_tokenizer.model_max_length = 4096
        # Start with empty window
        model_handler.context_window = 0
        model_handler.tokenizer = mock_tokenizer
        
        # Call internal method directly to avoid network calls from load()
        model_handler._detect_context_window()
        assert model_handler.context_window == 4096
        
    def test_detect_context_window_model_config(self, model_handler, mock_tokenizer, mock_model):
        del mock_tokenizer.model_max_length # Remove attribute from tokenizer to force fallback
        mock_model.config.max_position_embeddings = 8192
        
        model_handler.tokenizer = mock_tokenizer
        model_handler.model = mock_model
        model_handler.model.config = mock_model.config
        
        model_handler._detect_context_window()
        assert model_handler.context_window == 8192

    def test_detect_context_window_cap(self, model_handler, mock_tokenizer):
        mock_tokenizer.model_max_length = 1000000000000
        model_handler.tokenizer = mock_tokenizer
        model_handler._detect_context_window()
        assert model_handler.context_window == 4096

    def test_generate_stream(self, model_handler):
        model_handler.load()
        
        # We need to mock the streamer within src.models.streamer
        with patch("src.models.streamer.TextIteratorStreamer") as MockStreamer, \
             patch("src.models.streamer.Thread") as MockThread:
            
            streamer_instance = MockStreamer.return_value
            streamer_instance.__iter__.return_value = ["Hello", " world", "<|im_end|>"]
            
            generator = model_handler.generate_stream("Test prompt")
            
            # Since generate_stream calls stream_response which is generator, this should work
            results = list(generator)
            assert results == ["Hello", " world"]
            
            MockThread.assert_called_once()
            call_kwargs = MockThread.call_args[1]['kwargs']
            assert call_kwargs['max_new_tokens'] == config.MAX_NEW_TOKENS
            assert call_kwargs['temperature'] == config.TEMPERATURE
