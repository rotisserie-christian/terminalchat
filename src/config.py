import logging
from pathlib import Path
from typing import Optional
from .exceptions import ConfigError


logger = logging.getLogger(__name__)


def load_config(config_path: Optional[Path] = None) -> bool:
    """
    Load configuration from file
    
    Args:
        config_path: Optional path to config file. Uses CONFIG_FILE if None
        
    Returns:
        True if config loaded successfully, False if using defaults
        
    Raises:
        ConfigError: If config file exists but is corrupted beyond recovery
    """
    
    global MODEL_NAME, USER_DISPLAY_NAME, MODEL_DISPLAY_NAME
    global PRIMARY_COLOR, SECONDARY_COLOR, AUTOSAVE_ENABLED
    global RAG_ENABLED, RAG_CONTEXT_PERCENTAGE, RAG_TOP_K
    
    path = Path(config_path) if config_path else Path(CONFIG_FILE)
    
    if not path.exists():
        logger.info(f"Config file not found at {path}, using defaults")
        _set_defaults()
        return False
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(
            f"Config file is not valid JSON: {e}",
            exc_info=True,
            extra={'config_path': str(path)}
        )
        raise ConfigError(
            f"Config file at {path} is corrupted. "
            f"Please fix or delete it. Error: {e}"
        ) from e
    except PermissionError as e:
        logger.error(f"Permission denied reading config: {path}")
        raise ConfigError(f"Cannot read config file: {e}") from e
    except OSError as e:
        logger.error(f"OS error reading config: {e}", exc_info=True)
        raise ConfigError(f"Failed to read config file: {e}") from e
    
    # Validate and load with defaults for missing keys
    try:
        MODEL_NAME = config.get("model_name", DEFAULT_MODEL_NAME)
        USER_DISPLAY_NAME = config.get("user_display_name", DEFAULT_USER_DISPLAY_NAME)
        MODEL_DISPLAY_NAME = config.get("model_display_name", DEFAULT_MODEL_DISPLAY_NAME)
        PRIMARY_COLOR = config.get("primary_color", DEFAULT_PRIMARY_COLOR)
        SECONDARY_COLOR = config.get("secondary_color", DEFAULT_SECONDARY_COLOR)
        AUTOSAVE_ENABLED = config.get("autosave_enabled", DEFAULT_AUTOSAVE_ENABLED)
        RAG_ENABLED = config.get("rag_enabled", DEFAULT_RAG_ENABLED)
        RAG_CONTEXT_PERCENTAGE = config.get("rag_context_percentage", DEFAULT_RAG_CONTEXT_PERCENTAGE)
        RAG_TOP_K = config.get("rag_top_k", DEFAULT_RAG_TOP_K)
        
        # Validate types and ranges
        _validate_config()
        
        logger.info(f"Config loaded successfully from {path}")
        return True
        
    except (TypeError, ValueError) as e:
        logger.error(f"Invalid config values: {e}", exc_info=True)
        raise ConfigError(f"Config contains invalid values: {e}") from e


def _set_defaults():
    """Set all config values to defaults"""

    global MODEL_NAME, USER_DISPLAY_NAME, MODEL_DISPLAY_NAME
    global PRIMARY_COLOR, SECONDARY_COLOR, AUTOSAVE_ENABLED
    global RAG_ENABLED, RAG_CONTEXT_PERCENTAGE, RAG_TOP_K
    
    MODEL_NAME = DEFAULT_MODEL_NAME
    USER_DISPLAY_NAME = DEFAULT_USER_DISPLAY_NAME
    MODEL_DISPLAY_NAME = DEFAULT_MODEL_DISPLAY_NAME
    PRIMARY_COLOR = DEFAULT_PRIMARY_COLOR
    SECONDARY_COLOR = DEFAULT_SECONDARY_COLOR
    AUTOSAVE_ENABLED = DEFAULT_AUTOSAVE_ENABLED
    RAG_ENABLED = DEFAULT_RAG_ENABLED
    RAG_CONTEXT_PERCENTAGE = DEFAULT_RAG_CONTEXT_PERCENTAGE
    RAG_TOP_K = DEFAULT_RAG_TOP_K


def _validate_config():
    """Validate that config values are within acceptable ranges"""

    if not isinstance(AUTOSAVE_ENABLED, bool):
        raise ValueError(f"autosave_enabled must be boolean, got {type(AUTOSAVE_ENABLED)}")
    
    if not isinstance(RAG_ENABLED, bool):
        raise ValueError(f"rag_enabled must be boolean, got {type(RAG_ENABLED)}")
    
    if not (0.0 <= RAG_CONTEXT_PERCENTAGE <= 1.0):
        raise ValueError(
            f"rag_context_percentage must be between 0.0 and 1.0, "
            f"got {RAG_CONTEXT_PERCENTAGE}"
        )
    
    if not (1 <= RAG_TOP_K <= 100):
        raise ValueError(f"rag_top_k must be between 1 and 100, got {RAG_TOP_K}")


def save_config(config_path: Optional[Path] = None) -> None:
    """
    Save current configuration to file
    
    Args:
        config_path: Optional path to save config. Uses CONFIG_FILE if None
        
    Raises:
        ConfigError: If config cannot be saved
    """

    path = Path(config_path) if config_path else Path(CONFIG_FILE)
    
    config = {
        "model_name": MODEL_NAME,
        "user_display_name": USER_DISPLAY_NAME,
        "model_display_name": MODEL_DISPLAY_NAME,
        "primary_color": PRIMARY_COLOR,
        "secondary_color": SECONDARY_COLOR,
        "autosave_enabled": AUTOSAVE_ENABLED,
        "rag_enabled": RAG_ENABLED,
        "rag_context_percentage": RAG_CONTEXT_PERCENTAGE,
        "rag_top_k": RAG_TOP_K
    }
    
    try:
        # Write to temp file first, then rename (atomic operation)
        temp_path = path.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        temp_path.replace(path)
        logger.info(f"Config saved to {path}")
    except PermissionError as e:
        logger.error(f"Permission denied writing config: {path}")
        raise ConfigError(f"Cannot write config file: {e}") from e
    except OSError as e:
        logger.error(f"OS error writing config: {e}", exc_info=True)
        raise ConfigError(f"Failed to save config: {e}") from e