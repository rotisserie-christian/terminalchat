"""
Utilities for loading the system prompt from a file with a sane default,
and managing a collection of system prompts.
"""
from pathlib import Path
from typing import Optional, List

# Default fallback if file is missing or unreadable
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant. Keep your answers brief and concise. "
    "Do not ramble."
)

# Resolve to repo root: src/ is one level below project root
# Prompts directory
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
# The active system prompt file
ACTIVE_PROMPT_PATH = PROMPTS_DIR / "system.md"


def load_system_prompt() -> str:
    """
    Load the active system prompt from prompts/system.md if present,
    otherwise return the default prompt.
    """
    text = _read_file(ACTIVE_PROMPT_PATH)
    if text is not None:
        return text
    return DEFAULT_SYSTEM_PROMPT


def get_default_prompt() -> str:
    """Return the built-in default prompt string."""
    return DEFAULT_SYSTEM_PROMPT


def get_active_prompt_path() -> Path:
    """Return the path to the active prompt file."""
    return ACTIVE_PROMPT_PATH

def list_prompts() -> List[str]:
    """List all available system prompt files (stems) in the prompts directory."""
    if not PROMPTS_DIR.exists():
        return []
    return [p.stem for p in PROMPTS_DIR.glob("*.md")]

def load_prompt(name: str) -> Optional[str]:
    """Load a specific prompt by name (filename stem)."""
    path = PROMPTS_DIR / f"{name}.md"
    return _read_file(path)

def save_prompt_to_file(name: str, text: str) -> bool:
    """
    Save the provided text to a specific prompt file in the prompts directory.
    If name is 'system', it updates the active prompt.
    """
    try:
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        path = PROMPTS_DIR / f"{name}.md"
        path.write_text(text.strip() + "\n", encoding="utf-8")
        return True
    except Exception:
        return False

def delete_prompt_file(name: str) -> bool:
    """
    Delete a specific prompt file. Returns True if deleted or absent.
    """
    try:
        path = PROMPTS_DIR / f"{name}.md"
        if path.exists():
            path.unlink()
        return True
    except Exception:
        return False

def set_active_prompt(name: str) -> bool:
    """
    Set the prompt with the given name as the active system prompt
    by copying its content to system.md.
    """
    content = load_prompt(name)
    if content is None:
        return False
    return save_prompt_to_file("system", content)

def _read_file(path: Path) -> Optional[str]:
    """Internal helper to read a file if present and non-empty."""
    try:
        if path.exists():
            text = path.read_text(encoding="utf-8").strip()
            if text:
                return text
    except Exception:
        return None
    return None

