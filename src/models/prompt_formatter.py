from typing import List, Dict, Optional


def prepare_prompt(
    messages: List[Dict[str, str]], 
    tokenizer, 
    max_length: int, 
    rag_context: Optional[str] = None
) -> str:
    """
    Prepare a prompt that fits within the model's context window
    
    Context allocation:
    - System prompt (index 0): always preserved
    - RAG context: injected after system prompt if provided
    - Chat history: fills remaining space, pruned as needed
    
    Pruning strategy:
        - Removes oldest messages after system/RAG prompts, one at a time
        - Re-checks token length after each removal
        - Continues until prompt fits within max_length
    
    Args:
        messages: List of chat messages
        tokenizer: The model's tokenizer with apply_chat_template support
        max_length: Maximum token length allowed
        rag_context: Optional RAG context to inject after system prompt
        
    Returns:
        str: Formatted prompt string ready for model input
    """
    # Build messages with RAG context if provided
    messages_to_format = _build_messages_with_rag(messages, rag_context)
    
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
        
        # Remove the oldest chat message
        if len(pruned_messages) > num_preserved:
            pruned_messages.pop(num_preserved)
    
    # If it still doesn't fit, try with just the last user message
    try:
        last_message = messages[-1] if messages else {"role": "user", "content": ""}
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
        if messages:
            prompt += f"<|{messages[-1]['role']}|>\n{messages[-1]['content']}</s>\n"
        prompt += "<|assistant|>\n"
        return prompt


def _build_messages_with_rag(
    messages: List[Dict[str, str]], 
    rag_context: Optional[str]
) -> List[Dict[str, str]]:
    """
    Build message list with RAG context injected after system prompt
    
    Structure:
    - messages[0]: system prompt (always present if configured)
    - messages[1]: RAG context (only if rag_context provided and not empty)
    - messages[2+]: chat history (user/assistant messages)
    
    Args:
        messages: Original message list
        rag_context: Optional RAG context string
        
    Returns:
        List of message dictionaries ready for formatting
    """
    if not rag_context or not rag_context.strip():
        # No RAG context, return messages as-is
        return messages.copy()
    
    messages_with_rag = []
    
    # Add system prompt if it exists
    if messages and messages[0].get("role") == "system":
        messages_with_rag.append(messages[0])
        chat_start_idx = 1
    else:
        chat_start_idx = 0
    
    # Inject RAG context as a system message
    messages_with_rag.append({
        "role": "system",
        "content": f"# Knowledge Base Context\n\n{rag_context}\n\n---\n\nUse the above context to help answer questions when relevant."
    })
    
    # Add remaining chat history
    messages_with_rag.extend(messages[chat_start_idx:])
    
    return messages_with_rag
