import json
import logging
from pathlib import Path
from typing import Optional
from ..exceptions import ConfigError
from .defaults import CONFIG_FILE
from .validators import validate_config
from . import state


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
    path = Path(config_path) if config_path else Path(CONFIG_FILE)
    
    if not path.exists():
        logger.info(f"Config file not found at {path}, using defaults")
        state.reset_to_defaults()
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
    
    # Validate configuration
    errors = validate_config(config)
    if errors:
        error_msg = "; ".join(errors)
        logger.error(f"Invalid config values: {error_msg}")
        raise ConfigError(f"Config contains invalid values: {error_msg}")
    
    # Update state with validated config
    state.update_state(config)
    
    logger.info(f"Config loaded successfully from {path}")
    return True


def save_config(config_path: Optional[Path] = None) -> None:
    """
    Save current configuration to file
    
    Args:
        config_path: Optional path to save config. Uses CONFIG_FILE if None
        
    Raises:
        ConfigError: If config cannot be saved
    """
    path = Path(config_path) if config_path else Path(CONFIG_FILE)
    
    # Get current state
    config = state.get_state()
    
    try:
        # Write to temp file first, then rename (atomic write)
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
