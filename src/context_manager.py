from typing import List, Dict, Optional
from src.system_prompt import load_system_prompt


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
        
        Context allocation:
        - System prompt (index 0): always preserved
        - RAG context: injected after system prompt if provided
        - Chat history: fills remaining space, pruned as needed
        
        Pruning strategy:
            - System prompt (index 0) is always preserved
            - RAG context (index 1 if present) is always preserved
            - Removes oldest messages after system/RAG prompts one at a time
            - Re-checks token length after each removal
            - Continues until prompt fits within max_length
        
        Args:
            tokenizer: The model's tokenizer with apply_chat_template support
            max_length: Maximum token length allowed
            rag_context: Optional RAG context to inject after system prompt
            
        Returns:
            str: Formatted prompt string ready for model input
        """
        
        # Build messages with RAG context if provided
        messages_to_format = self._build_messages_with_rag(rag_context)
        
        # Try full prompt first
        try:
            full_prompt = tokenizer.apply_chat_template(
                messages_to_format, 
                tokenize=False, 
                add_generation_prompt=True
            )
            tokenized = tokenizer(full_prompt, return_tensors='pt')
            if tokenized.input_ids.shape[1] <= max_length:
                return full_prompt
        except Exception:
            pass
        
        # Need to prune - start removing oldest chat messages
        # Determine how many messages to preserve (system + optional RAG)
        num_preserved = 2 if rag_context else 1
        
        # Start with all messages, then prune oldest chat messages
        pruned_messages = messages_to_format.copy()
        
        while len(pruned_messages) > num_preserved:
            try:
                prompt = tokenizer.apply_chat_template(
                    pruned_messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
                tokenized = tokenizer(prompt, return_tensors='pt')
                if tokenized.input_ids.shape[1] < max_length:
                    return prompt
            except Exception:
                pass
            
            # Remove the oldest chat message (right after preserved messages)
            if len(pruned_messages) > num_preserved:
                pruned_messages.pop(num_preserved)
        
        # If we still don't fit, try with just the last user message
        try:
            last_message = self.messages[-1] if self.messages else {"role": "user", "content": ""}
            minimal_messages = messages_to_format[:num_preserved] + [last_message]
            return tokenizer.apply_chat_template(
                minimal_messages, 
                tokenize=False, 
                add_generation_prompt=True
            )
        except Exception:
            # Last resort: manual formatting
            prompt = ""
            for msg in messages_to_format[:num_preserved]:
                prompt += f"<|{msg['role']}|>\n{msg['content']}</s>\n"
            if self.messages:
                prompt += f"<|{self.messages[-1]['role']}|>\n{self.messages[-1]['content']}</s>\n"
            prompt += "<|assistant|>\n"
            return prompt
    
    def _build_messages_with_rag(self, rag_context: Optional[str]) -> List[Dict[str, str]]:
        """
        Build message list with RAG context injected after system prompt.
        
        Structure:
        - messages[0]: system prompt (always present if configured)
        - messages[1]: RAG context (only if rag_context provided and not empty)
        - messages[2+]: chat history (user/assistant messages)
        
        Args:
            rag_context: Optional RAG context string
            
        Returns:
            List of message dictionaries ready for formatting
        """
        if not rag_context or not rag_context.strip():
            # No RAG context, return messages as-is
            return self.messages.copy()
        
        messages_with_rag = []
        
        # Add system prompt if it exists
        if self.messages and self.messages[0].get("role") == "system":
            messages_with_rag.append(self.messages[0])
            chat_start_idx = 1
        else:
            chat_start_idx = 0
        
        # Inject RAG context as a system message
        messages_with_rag.append({
            "role": "system",
            "content": f"# Knowledge Base Context\n\n{rag_context}\n\n---\n\nUse the above context to help answer questions when relevant."
        })
        
        # Add remaining chat history
        messages_with_rag.extend(self.messages[chat_start_idx:])
        
        return messages_with_rag