from pathlib import Path

# Fallback system prompt
DEFAULT_SYSTEM_PROMPT = "Keep your answers brief and concise, do not ramble."

# Prompts directory
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
# The active system prompt file
ACTIVE_PROMPT_PATH = PROMPTS_DIR / "system.md"


def load_system_prompt() -> str:
    """
    Load the active system prompt from prompts/system.md if present,
    otherwise return the default prompt
    """

    try:
        if ACTIVE_PROMPT_PATH.exists():
            text = ACTIVE_PROMPT_PATH.read_text(encoding="utf-8").strip()
            if text:
                return text
    except Exception:
        # Fallback to default prompt if there are file issues 
        pass
    
    return DEFAULT_SYSTEM_PROMPT


def get_default_prompt() -> str:
    """Return the built-in default prompt string."""
    return DEFAULT_SYSTEM_PROMPT