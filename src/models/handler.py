import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .streamer import stream_response
import src.config as config


logger = logging.getLogger(__name__)


class ModelHandler:
    """
    Handles:
    - Model + tokenizer loading
    - Device placement
    - Context window detection
    - Streaming text generation interface
    """

    def __init__(self, model_name="HuggingFaceTB/SmolLM-135M-Instruct"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.context_window = 2048  # Default fallback

    def load(self):
        """
        Load the model and tokenizer
            
        Returns:
            bool: True if successful, otherwise False
        """
        logger.info(f"Loading model {self.model_name} on {self.device}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, 
                dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            if self.device == "cpu":
                self.model.to(self.device)
            
            self._detect_context_window()
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False

    def _detect_context_window(self):
        """Determine the size of the context window"""
        if hasattr(self.tokenizer, "model_max_length"):
            self.context_window = self.tokenizer.model_max_length
        elif hasattr(self.model.config, "max_position_embeddings"):
            self.context_window = self.model.config.max_position_embeddings
        
        # Cap at a reasonable limit in case it reports something silly 
        if self.context_window > 1000000: 
            self.context_window = 4096
        
        logger.info(f"Detected context window: {self.context_window}")

    def generate_stream(self, prompt, max_new_tokens=None, temperature=None, top_k=None, top_p=None):
        """
        Generate streaming text
        
        Args:
            prompt: Formatted prompt string
            max_new_tokens: Max tokens to generate
            temperature: Sampling temperature
            top_k: Top-k sampling limit
            top_p: Nucleus sampling threshold
            
        Yields:
            str: Text tokens as they're produced
        """
        return stream_response(
            model=self.model,
            tokenizer=self.tokenizer,
            prompt=prompt,
            device=self.device,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p
        )
