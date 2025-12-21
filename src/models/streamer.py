from threading import Thread
from transformers import TextIteratorStreamer
import src.config as config

def stream_response(
    model, 
    tokenizer, 
    prompt, 
    device="cuda",
    max_new_tokens=None, 
    temperature=None, 
    top_k=None, 
    top_p=None
):
    """
    Generate streaming text
    All generation parameters default to config values if not provided
    
    Args:
        model: Loaded model instance
        tokenizer: Loaded tokenizer instance
        prompt: Formatted prompt string
        device: Device to run generation on
        max_new_tokens: Max tokens to generate (None = use config default)
        temperature: Sampling temperature (None = use config default)
        top_k: Top-k sampling limit (None = use config default)
        top_p: Nucleus sampling threshold (None = use config default)
        
    Yields:
        str: Text tokens as they're produced
    """

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    streamer = TextIteratorStreamer(
        tokenizer, 
        skip_prompt=True, 
        decode_kwargs={"skip_special_tokens": True}
    )
    
    # Use passed params or fall back to config
    max_new_tokens = max_new_tokens if max_new_tokens is not None else config.MAX_NEW_TOKENS
    temperature = temperature if temperature is not None else config.TEMPERATURE
    top_k = top_k if top_k is not None else config.TOP_K
    top_p = top_p if top_p is not None else config.TOP_P
    
    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
    )
    
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    
    for new_text in streamer:
        if "<|im_end|>" in new_text:
            new_text = new_text.replace("<|im_end|>", "")
            if new_text:
                yield new_text
            break
        if new_text:
            yield new_text
