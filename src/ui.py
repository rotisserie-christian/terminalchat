import os
import subprocess
import tempfile
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme
from rich.live import Live
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
import questionary
import src.config as config

class TerminalUI:
    def __init__(self):
        custom_theme = Theme({
            "info": "dim cyan",
            "user": config.PRIMARY_COLOR,
            "assistant": config.SECONDARY_COLOR,
            "warning": "magenta",
            "danger": "bold red"
        })
        self.console = Console(theme=custom_theme)
        # Prompt toolkit style needs a dictionary
        self.session = PromptSession(style=Style.from_dict({'prompt': f'ansi{config.PRIMARY_COLOR} bold'}))
    
    def display_welcome(self):
        self.console.print(Panel.fit(f"[bold {config.SECONDARY_COLOR}]Terminal Chat[/bold {config.SECONDARY_COLOR}]\n[dim]christianwaters.dev[/dim]", border_style=config.SECONDARY_COLOR))

    def get_input(self):
        try:
            return self.session.prompt(f"\n[{config.USER_DISPLAY_NAME}] > ")
        except (EOFError, KeyboardInterrupt):
            return None

    def display_user_message(self, message):
        pass

    def display_assistant_stream(self, generator):
        self.console.print(f"\n[bold {config.SECONDARY_COLOR}]{config.MODEL_DISPLAY_NAME} >[/bold {config.SECONDARY_COLOR}] ", end="")
        current_text = ""
        
        for token in generator:
            self.console.print(token, end="")
            current_text += token
        self.console.print() # Newline at end
        return current_text

    def display_system_message(self, message):
        self.console.print(f"[dim]{message}[/dim]")

    def display_error(self, message):
        self.console.print(f"[danger]Error: {message}[/danger]")

    def clear_screen(self):
        self.console.clear()

    def show_main_menu(self):
        self.clear_screen()
        self.display_welcome()
        
        style = questionary.Style([
            ('qmark', 'fg:cyan bold'),
            ('question', 'bold'),
            ('answer', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan bold'),
            ('selected', 'fg:cyan bold'),
            ('separator', 'fg:#cc5454'),
            ('instruction', 'fg:#909090'),
            ('text', ''),
            ('disabled', 'fg:#858585 italic')
        ])
        return questionary.select(
            "Select an option:",
            choices=["New Chat", "Load Chat", "System Prompt", "Settings", "Exit"],
            style=style,
            use_arrow_keys=True
        ).ask()

    def show_chat_selection(self, chats):
        if not chats:
            self.display_error("No saved chats found.")
            questionary.press_any_key_to_continue().ask()
            return None
        
        choices = chats + ["< Back"]
        
        style = questionary.Style([
            ('qmark', 'fg:cyan bold'),
            ('question', 'bold'),
            ('answer', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan bold'),
            ('selected', 'fg:cyan bold'),
        ])
        
        choice = questionary.select(
            "Select a chat to load:",
            choices=choices,
            style=style,
            use_arrow_keys=True
        ).ask()
        
        if choice == "< Back":
            return None
        return choice

    def show_system_prompt_menu(self):
        self.clear_screen()
        style = questionary.Style([
            ('qmark', 'fg:cyan bold'),
            ('question', 'bold'),
            ('answer', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan bold'),
            ('selected', 'fg:cyan bold'),
        ])
        return questionary.select(
            "System Prompt",
            choices=["Default Prompt", "New Prompt", "< Back"],
            style=style,
            use_arrow_keys=True
        ).ask()

    def display_prompt_panel(self, title: str, content: str):
        # Clear to avoid clutter and show the prompt cleanly.
        self.clear_screen()
        self.console.print(Panel(Markdown(content), title=title, border_style=config.SECONDARY_COLOR))
        questionary.press_any_key_to_continue("Press any key to return").ask()
        self.clear_screen()

    def edit_prompt_in_editor(self, initial_text: str) -> str | None:
        """
        Open a simple text editor workflow and return the edited text or None on failure/cancel.
        """
        editor = os.environ.get("EDITOR")
        if not editor:
            editor = "notepad" if os.name == "nt" else "nano"

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".md", encoding="utf-8") as tmp:
            tmp.write(initial_text or "")
            tmp.flush()
            tmp_path = Path(tmp.name)

        try:
            result = subprocess.run([editor, str(tmp_path)])
            if result.returncode != 0:
                self.display_error("Editor exited with a non-zero status. Changes discarded.")
                return None

            edited_text = tmp_path.read_text(encoding="utf-8").strip()
            return edited_text
        except FileNotFoundError:
            self.display_error(f"Editor '{editor}' not found. Set EDITOR env var to override.")
            return None
        except Exception as exc:
            self.display_error(f"Failed to open editor: {exc}")
            return None
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass

    def prompt_after_edit_action(self):
        return questionary.select(
            "What would you like to do?",
            choices=["Save", "Cancel", "Delete"],
        ).ask()

    def confirm_delete_prompt(self):
        return questionary.confirm("Delete the custom system prompt file?", default=False).ask()
