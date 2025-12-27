from typing import List, Dict, Optional
from .system import load_system_prompt
from .prompt_formatter import prepare_prompt


# Sentinel value to distinguish between "not provided" and "explicitly None"
_USE_DEFAULT = object()


class ContextManager:
    """
    Manages conversation history with automatic context window pruning
    
    Formats messages for the model and removes oldest messages when the
    context exceeds the model's limits. System prompt is always preserved.
    Supports optional RAG context injection.
    """

    def __init__(self, system_prompt=_USE_DEFAULT):
        """
        Initialize the ContextManager with the system prompt
        """
        if system_prompt is _USE_DEFAULT:
            prompt = load_system_prompt()
        else:
            prompt = system_prompt
        self.system_prompt = prompt
        self.messages: List[Dict[str, str]] = []
        if prompt:
            self.messages.append({"role": "system", "content": prompt})

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_messages(self):
        return self.messages

    def prepare_prompt(self, tokenizer, max_length, rag_context: Optional[str] = None):
        """
        Prepare a prompt that fits within the model's context window
        
        Delegates the logic to prompt_formatter.py
        
        Args:
            tokenizer: The model's tokenizer with apply_chat_template support
            max_length: Maximum token length allowed
            rag_context: Optional RAG context to inject after system prompt
            
        Returns:
            str: Formatted prompt string ready for model input
        """
        return prepare_prompt(self.messages, tokenizer, max_length, rag_context)
