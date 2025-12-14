import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread


logger = logging.getLogger(__name__)


class ModelHandler:
    """
    Handles:

    - Model + tokenizer loading
    - Device placement
    - Context window detection
    - Streaming text generation
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
        """
        Determine the size of the context window
        """

        if hasattr(self.tokenizer, "model_max_length"):
            self.context_window = self.tokenizer.model_max_length
        elif hasattr(self.model.config, "max_position_embeddings"):
            self.context_window = self.model.config.max_position_embeddings
        
        # Cap at a reasonable limit in case it reports something silly 
        if self.context_window > 1000000: 
            self.context_window = 4096
        
        logger.info(f"Detected context window: {self.context_window}")

    def generate_stream(self, prompt, max_new_tokens=128):
        """
        Generate text from a prompt using streaming.
        
        Args:
            prompt: string (after formatting)
            max_new_tokens: int
            
        Yields:
            str: Text tokens as they're produced
        """
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        streamer = TextIteratorStreamer(
            self.tokenizer, 
            skip_prompt=True, 
            decode_kwargs={"skip_special_tokens": True}
        )
        generation_kwargs = dict(
            **inputs, 
            streamer=streamer, 
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.9,
            top_k=50,
            top_p=0.95,
        )
        
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        for new_text in streamer:
            # Filter out the specific end token if it leaks through
            if "<|im_end|>" in new_text:
                new_text = new_text.replace("<|im_end|>", "")
                yield new_text
                break
            yield new_text
