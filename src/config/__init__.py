"""
Configuration module

Provides centralized configuration management with validation and persistence.
"""

# Re-export defaults
from .defaults import *

# Re-export state variables
from .state import (
    MODEL_NAME,
    TEMPERATURE,
    TOP_K,
    TOP_P,
    MAX_NEW_TOKENS,
    USER_DISPLAY_NAME,
    MODEL_DISPLAY_NAME,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    AUTOSAVE_ENABLED,
    RAG_ENABLED,
    RAG_CONTEXT_PERCENTAGE,
    RAG_TOP_K,
)

# Re-export manager functions
from .manager import load_config, save_config

# Load config on import (maintains backward compatibility)
load_config()
