"""
Utilities for loading the system prompt from a file with a sane default.
"""
from pathlib import Path
from typing import Optional

# Default fallback if file is missing or unreadable
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant. Keep your answers brief and concise. "
    "Do not ramble."
)

# Resolve to repo root: src/ is one level below project root
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system.md"


def load_system_prompt() -> str:
    """
    Load the system prompt from prompts/system.md if present,
    otherwise return the default prompt.
    """
    text = _read_prompt_file()
    if text is not None:
        return text
    return DEFAULT_SYSTEM_PROMPT


def get_default_prompt() -> str:
    """Return the built-in default prompt string."""
    return DEFAULT_SYSTEM_PROMPT


def get_prompt_path() -> Path:
    """Return the path to the prompt file."""
    return PROMPT_PATH


def save_prompt(text: str) -> bool:
    """
    Save the provided prompt text to the prompt file.
    Ensures parent directory exists.
    """
    try:
        PROMPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        PROMPT_PATH.write_text(text.strip() + "\n", encoding="utf-8")
        return True
    except Exception:
        return False


def delete_prompt() -> bool:
    """
    Delete the prompt file if it exists. Returns True if deleted or absent.
    """
    try:
        if PROMPT_PATH.exists():
            PROMPT_PATH.unlink()
        return True
    except Exception:
        return False


def _read_prompt_file() -> Optional[str]:
    """Internal helper to read the prompt file if present and non-empty."""
    try:
        if PROMPT_PATH.exists():
            text = PROMPT_PATH.read_text(encoding="utf-8").strip()
            if text:
                return text
    except Exception:
        return None
    return None

