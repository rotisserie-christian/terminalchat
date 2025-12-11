from typing import List, Dict
from src.system_prompt import load_system_prompt

class ContextManager:
    def __init__(self, system_prompt=None):
        prompt = system_prompt if system_prompt is not None else load_system_prompt()
        self.system_prompt = prompt
        self.messages: List[Dict[str, str]] = []
        if prompt:
            self.messages.append({"role": "system", "content": prompt})

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_messages(self):
        return self.messages

    def prepare_prompt(self, tokenizer, max_length):
        # Apply pruning strategy
        # Ideally, we used the tokenizer's apply_chat_template if available.
        # But we also need to respect max_length. 
        
        # Simple strategy: Keep system prompt, and as many recent messages as possible.
        
        # First, try full history
        try:
            full_prompt = tokenizer.apply_chat_template(self.messages, tokenize=False, add_generation_prompt=True)
            tokenized = tokenizer(full_prompt, return_tensors='pt')
            if tokenized.input_ids.shape[1] <= max_length:
                return full_prompt
        except Exception:
            # If apply_chat_template fails or is not available, we might need manual formatting.
            pass
            
        # If too long, prune older messages (keeping system prompt at index 0)
        pruned_messages = [self.messages[0]] + self.messages[1:]
        
        while len(pruned_messages) > 1:
            try:
                prompt = tokenizer.apply_chat_template(pruned_messages, tokenize=False, add_generation_prompt=True)
                tokenized = tokenizer(prompt, return_tensors='pt')
                if tokenized.input_ids.shape[1] < max_length:
                    return prompt
            except Exception:
                # Fallback implementation if chat template missing
                pass
            
            # Remove the oldest message after system prompt (which is at index 1 now)
            pruned_messages.pop(1)
            
        # Fallback if extremely tight or template fails
        try:
             return tokenizer.apply_chat_template([self.messages[-1]], tokenize=False, add_generation_prompt=True)
        except Exception:
             # Last resort manual formatting
             prompt = ""
             for msg in self.messages:
                 prompt += f"<|{msg['role']}|>\n{msg['content']}</s>\n"
             prompt += "<|assistant|>\n"
             return prompt
