# Configuration for Terminal Chat
import json
import os

# Default values
DEFAULT_MODEL_NAME = "Qwen/Qwen3-0.6B"
DEFAULT_USER_DISPLAY_NAME = "Me"
DEFAULT_MODEL_DISPLAY_NAME = "Model"
DEFAULT_PRIMARY_COLOR = "green"
DEFAULT_SECONDARY_COLOR = "blue"

# Configuration values (will be loaded from file or use defaults)
MODEL_NAME = DEFAULT_MODEL_NAME
USER_DISPLAY_NAME = DEFAULT_USER_DISPLAY_NAME
MODEL_DISPLAY_NAME = DEFAULT_MODEL_DISPLAY_NAME
PRIMARY_COLOR = DEFAULT_PRIMARY_COLOR
SECONDARY_COLOR = DEFAULT_SECONDARY_COLOR

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from file, or use defaults if file doesn't exist."""
    global MODEL_NAME, USER_DISPLAY_NAME, MODEL_DISPLAY_NAME, PRIMARY_COLOR, SECONDARY_COLOR
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                MODEL_NAME = config.get("model_name", DEFAULT_MODEL_NAME)
                USER_DISPLAY_NAME = config.get("user_display_name", DEFAULT_USER_DISPLAY_NAME)
                MODEL_DISPLAY_NAME = config.get("model_display_name", DEFAULT_MODEL_DISPLAY_NAME)
                PRIMARY_COLOR = config.get("primary_color", DEFAULT_PRIMARY_COLOR)
                SECONDARY_COLOR = config.get("secondary_color", DEFAULT_SECONDARY_COLOR)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
    else:
        # Use defaults
        MODEL_NAME = DEFAULT_MODEL_NAME
        USER_DISPLAY_NAME = DEFAULT_USER_DISPLAY_NAME
        MODEL_DISPLAY_NAME = DEFAULT_MODEL_DISPLAY_NAME
        PRIMARY_COLOR = DEFAULT_PRIMARY_COLOR
        SECONDARY_COLOR = DEFAULT_SECONDARY_COLOR

def save_config():
    """Save current configuration to file."""
    config = {
        "model_name": MODEL_NAME,
        "user_display_name": USER_DISPLAY_NAME,
        "model_display_name": MODEL_DISPLAY_NAME,
        "primary_color": PRIMARY_COLOR,
        "secondary_color": SECONDARY_COLOR
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Load config on import
load_config()
