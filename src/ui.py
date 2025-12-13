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
import shutil 

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

    import shutil

    def display_assistant_stream(self, generator):
        width = shutil.get_terminal_size().columns

        prefix = f"[bold {config.SECONDARY_COLOR}]{config.MODEL_DISPLAY_NAME} >[/bold {config.SECONDARY_COLOR}] "
        self.console.print(f"\n{prefix}", end="")

        current_line_len = len(config.MODEL_DISPLAY_NAME) + 3
        current_text = ""
        buffer = ""

        for token in generator:
            buffer += token

            while " " in buffer:
                word, buffer = buffer.split(" ", 1)
                word += " "

                if current_line_len + len(word) > width:
                    self.console.print()
                    current_line_len = 0

                self.console.print(word, end="")
                current_text += word
                current_line_len += len(word)

        # Print remaining text
        if buffer:
            if current_line_len + len(buffer) > width:
                self.console.print()
            self.console.print(buffer, end="")
            current_text += buffer

        self.console.print()
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
        try:
            choice = questionary.select(
                "Select an option:",
                choices=["New Chat", "Load Chat", "Settings", "Exit"],
                style=style,
                use_arrow_keys=True
            ).ask()
            if choice is None:
                return "Exit"
            return choice
        except KeyboardInterrupt:
            return "Exit"

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
        
        try:
            choice = questionary.select(
                "Select a chat to load:",
                choices=choices,
                style=style,
                use_arrow_keys=True
            ).ask()
            if choice is None:
                return None
        except KeyboardInterrupt:
            return None
        
        if choice == "< Back":
            return None
        return choice



    def select_system_prompt(self, prompts):
        self.clear_screen()
        if not prompts:
             self.display_error("No prompt files found in prompts/ directory.")
             questionary.press_any_key_to_continue().ask()
             return None

        choices = prompts + ["< Back"]
        style = questionary.Style([
            ('qmark', 'fg:cyan bold'),
            ('question', 'bold'),
            ('answer', 'fg:cyan bold'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan bold'),
            ('selected', 'fg:cyan bold'),
        ])
        try:
            choice = questionary.select(
                "Select Active System Prompt",
                choices=choices,
                style=style,
                use_arrow_keys=True
            ).ask()
            if choice is None:
                return None
            return choice
        except KeyboardInterrupt:
            return None

    def display_prompt_panel(self, title: str, content: str):
        # Clear to avoid clutter and show the prompt cleanly.
        self.clear_screen()
        self.console.print(Panel(Markdown(content), title=title, border_style=config.SECONDARY_COLOR))
        questionary.press_any_key_to_continue("Press any key to return").ask()
        self.clear_screen()


