from .defaults import (
    DEFAULT_MODEL_NAME,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_K,
    DEFAULT_TOP_P,
    DEFAULT_MAX_NEW_TOKENS,
    DEFAULT_USER_DISPLAY_NAME,
    DEFAULT_MODEL_DISPLAY_NAME,
    DEFAULT_PRIMARY_COLOR,
    DEFAULT_SECONDARY_COLOR,
    DEFAULT_AUTOSAVE_ENABLED,
    DEFAULT_RAG_ENABLED,
    DEFAULT_RAG_CONTEXT_PERCENTAGE,
    DEFAULT_RAG_TOP_K,
)

# Global variables (module-level state)
# Model
MODEL_NAME = DEFAULT_MODEL_NAME
TEMPERATURE = DEFAULT_TEMPERATURE
TOP_K = DEFAULT_TOP_K
TOP_P = DEFAULT_TOP_P
MAX_NEW_TOKENS = DEFAULT_MAX_NEW_TOKENS

# UI + chat
USER_DISPLAY_NAME = DEFAULT_USER_DISPLAY_NAME
MODEL_DISPLAY_NAME = DEFAULT_MODEL_DISPLAY_NAME
PRIMARY_COLOR = DEFAULT_PRIMARY_COLOR
SECONDARY_COLOR = DEFAULT_SECONDARY_COLOR
AUTOSAVE_ENABLED = DEFAULT_AUTOSAVE_ENABLED

# RAG
RAG_ENABLED = DEFAULT_RAG_ENABLED
RAG_CONTEXT_PERCENTAGE = DEFAULT_RAG_CONTEXT_PERCENTAGE
RAG_TOP_K = DEFAULT_RAG_TOP_K


def update_state(config: dict) -> None:
    """
    Update global state from configuration dictionary
    
    Args:
        config: Configuration dictionary with values to update
    """
    global MODEL_NAME, TEMPERATURE, TOP_K, TOP_P, MAX_NEW_TOKENS
    global USER_DISPLAY_NAME, MODEL_DISPLAY_NAME
    global PRIMARY_COLOR, SECONDARY_COLOR, AUTOSAVE_ENABLED
    global RAG_ENABLED, RAG_CONTEXT_PERCENTAGE, RAG_TOP_K
    
    # Model parameters
    MODEL_NAME = config.get("model_name", DEFAULT_MODEL_NAME)
    TEMPERATURE = config.get("temperature", DEFAULT_TEMPERATURE)
    TOP_K = config.get("top_k", DEFAULT_TOP_K)
    TOP_P = config.get("top_p", DEFAULT_TOP_P)
    MAX_NEW_TOKENS = config.get("max_new_tokens", DEFAULT_MAX_NEW_TOKENS)
    
    # UI + chat
    USER_DISPLAY_NAME = config.get("user_display_name", DEFAULT_USER_DISPLAY_NAME)
    MODEL_DISPLAY_NAME = config.get("model_display_name", DEFAULT_MODEL_DISPLAY_NAME)
    PRIMARY_COLOR = config.get("primary_color", DEFAULT_PRIMARY_COLOR)
    SECONDARY_COLOR = config.get("secondary_color", DEFAULT_SECONDARY_COLOR)
    AUTOSAVE_ENABLED = config.get("autosave_enabled", DEFAULT_AUTOSAVE_ENABLED)
    
    # RAG
    RAG_ENABLED = config.get("rag_enabled", DEFAULT_RAG_ENABLED)
    RAG_CONTEXT_PERCENTAGE = config.get("rag_context_percentage", DEFAULT_RAG_CONTEXT_PERCENTAGE)
    RAG_TOP_K = config.get("rag_top_k", DEFAULT_RAG_TOP_K)


def get_state() -> dict:
    """
    Get current configuration state as a dictionary
    
    Returns:
        Dictionary containing all current configuration values
    """
    return {
        "model_name": MODEL_NAME,
        "temperature": TEMPERATURE,
        "top_k": TOP_K,
        "top_p": TOP_P,
        "max_new_tokens": MAX_NEW_TOKENS,
        "user_display_name": USER_DISPLAY_NAME,
        "model_display_name": MODEL_DISPLAY_NAME,
        "primary_color": PRIMARY_COLOR,
        "secondary_color": SECONDARY_COLOR,
        "autosave_enabled": AUTOSAVE_ENABLED,
        "rag_enabled": RAG_ENABLED,
        "rag_context_percentage": RAG_CONTEXT_PERCENTAGE,
        "rag_top_k": RAG_TOP_K,
    }


def reset_to_defaults() -> None:
    """Reset all configuration values to defaults"""
    global MODEL_NAME, TEMPERATURE, TOP_K, TOP_P, MAX_NEW_TOKENS
    global USER_DISPLAY_NAME, MODEL_DISPLAY_NAME
    global PRIMARY_COLOR, SECONDARY_COLOR, AUTOSAVE_ENABLED
    global RAG_ENABLED, RAG_CONTEXT_PERCENTAGE, RAG_TOP_K
    
    MODEL_NAME = DEFAULT_MODEL_NAME
    TEMPERATURE = DEFAULT_TEMPERATURE
    TOP_K = DEFAULT_TOP_K
    TOP_P = DEFAULT_TOP_P
    MAX_NEW_TOKENS = DEFAULT_MAX_NEW_TOKENS
    USER_DISPLAY_NAME = DEFAULT_USER_DISPLAY_NAME
    MODEL_DISPLAY_NAME = DEFAULT_MODEL_DISPLAY_NAME
    PRIMARY_COLOR = DEFAULT_PRIMARY_COLOR
    SECONDARY_COLOR = DEFAULT_SECONDARY_COLOR
    AUTOSAVE_ENABLED = DEFAULT_AUTOSAVE_ENABLED
    RAG_ENABLED = DEFAULT_RAG_ENABLED
    RAG_CONTEXT_PERCENTAGE = DEFAULT_RAG_CONTEXT_PERCENTAGE
    RAG_TOP_K = DEFAULT_RAG_TOP_K
