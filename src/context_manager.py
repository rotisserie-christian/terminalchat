from typing import List, Dict
from src.system_prompt import load_system_prompt


# Sentinel value to distinguish between "not provided" and "explicitly None"
_USE_DEFAULT = object()


class ContextManager:
    """
    Manages conversation history with automatic context window pruning
    
    Formats messages for the model and removes oldest messages when the
    context exceeds the model's limits. System prompt is always preserved
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

    def prepare_prompt(self, tokenizer, max_length):
        """
        Prepare a prompt that fits within the model's context window
        
        Pruning strategy:
            - System prompt (index 0) is always preserved
            - Removes oldest messages after system prompt one at a time
            - Re-checks token length after each removal
            - Continues until prompt fits within max_length
        
        Args:
            tokenizer: The model's tokenizer with apply_chat_template support
            max_length: Maximum token length allowed
            
        Returns:
        str: Formatted prompt string ready for model input
        """

        try:
            full_prompt = tokenizer.apply_chat_template(self.messages, tokenize=False, add_generation_prompt=True)
            tokenized = tokenizer(full_prompt, return_tensors='pt')
            if tokenized.input_ids.shape[1] <= max_length:
                return full_prompt
        except Exception:
            pass
            
        # Prune older messages
        pruned_messages = [self.messages[0]] + self.messages[1:]
        
        while len(pruned_messages) > 1:
            try:
                prompt = tokenizer.apply_chat_template(pruned_messages, tokenize=False, add_generation_prompt=True)
                tokenized = tokenizer(prompt, return_tensors='pt')
                if tokenized.input_ids.shape[1] < max_length:
                    return prompt
            except Exception:
                # Fallback implementation if chat template missing from library
                pass
            
            # Remove the oldest message after system prompt (which is at index 1 now)
            pruned_messages.pop(1)
            
        # Fallback if template fails
        try:
            # Trying only the last message
            return tokenizer.apply_chat_template([self.messages[-1]], tokenize=False, add_generation_prompt=True)
        except Exception:
             # Last resort manual formatting if fallback fails
             prompt = ""
             for msg in self.messages:
                 prompt += f"<|{msg['role']}|>\n{msg['content']}</s>\n"
             prompt += "<|assistant|>\n"
             return prompt
