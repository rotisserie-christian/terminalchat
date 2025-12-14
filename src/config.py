"""
Loads and saves user settings from config.json 

Configuration values are stored as module-level globals, automatically loaded on import

Available settings:
- MODEL_NAME: HuggingFace model identifier
- USER_DISPLAY_NAME: Name shown for user messages
- MODEL_DISPLAY_NAME: Name shown for model messages  
- PRIMARY_COLOR: Main UI color theme
- SECONDARY_COLOR: Accent UI color theme
- AUTOSAVE_ENABLED: save chat after each message
"""


import json
import os


# Default values (model)
DEFAULT_MODEL_NAME = "Qwen/Qwen3-0.6B"
DEFAULT_TEMPERATURE = 0.9
DEFAULT_TOP_K = 50
DEFAULT_TOP_P = 0.95
DEFAULT_MAX_NEW_TOKENS = 128
# Default values (UI + chat)
DEFAULT_USER_DISPLAY_NAME = "Me" 
DEFAULT_MODEL_DISPLAY_NAME = "Model"
DEFAULT_PRIMARY_COLOR = "green"
DEFAULT_SECONDARY_COLOR = "blue"
DEFAULT_AUTOSAVE_ENABLED = False 


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


CONFIG_FILE = "config.json"


def load_config():
    """Load configuration from file, or use defaults if file doesn't exist"""

    global MODEL_NAME, USER_DISPLAY_NAME, MODEL_DISPLAY_NAME, PRIMARY_COLOR, SECONDARY_COLOR, AUTOSAVE_ENABLED
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                MODEL_NAME = config.get("model_name", DEFAULT_MODEL_NAME)
                USER_DISPLAY_NAME = config.get("user_display_name", DEFAULT_USER_DISPLAY_NAME)
                MODEL_DISPLAY_NAME = config.get("model_display_name", DEFAULT_MODEL_DISPLAY_NAME)
                PRIMARY_COLOR = config.get("primary_color", DEFAULT_PRIMARY_COLOR)
                SECONDARY_COLOR = config.get("secondary_color", DEFAULT_SECONDARY_COLOR)
                AUTOSAVE_ENABLED = config.get("autosave_enabled", DEFAULT_AUTOSAVE_ENABLED)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
    else:
        # Use defaults
        MODEL_NAME = DEFAULT_MODEL_NAME
        USER_DISPLAY_NAME = DEFAULT_USER_DISPLAY_NAME
        MODEL_DISPLAY_NAME = DEFAULT_MODEL_DISPLAY_NAME
        PRIMARY_COLOR = DEFAULT_PRIMARY_COLOR
        SECONDARY_COLOR = DEFAULT_SECONDARY_COLOR
        AUTOSAVE_ENABLED = DEFAULT_AUTOSAVE_ENABLED

def save_config():
    """Save current configuration to file"""

    config = {
        "model_name": MODEL_NAME,
        "user_display_name": USER_DISPLAY_NAME,
        "model_display_name": MODEL_DISPLAY_NAME,
        "primary_color": PRIMARY_COLOR,
        "secondary_color": SECONDARY_COLOR,
        "autosave_enabled": AUTOSAVE_ENABLED
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
