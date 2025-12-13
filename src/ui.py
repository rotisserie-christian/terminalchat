import os
import subprocess
import tempfile
import sys
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
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
        # Create key bindings for shortcuts
        bindings = KeyBindings()
        
        @bindings.add('c-r')
        def _(event):
            """Ctrl+R: Return to main menu"""
            event.app.exit(result='RETURN_TO_MENU')
        
        @bindings.add('c-s')
        def _(event):
            """Ctrl+S: Save chat"""
            event.app.exit(result='MANUAL_SAVE')
        
        try:
            # Display helpful labels below the input
            bottom_toolbar = HTML(
                f'<style fg="#909090">Ctrl+C: Exit  |  Ctrl+R: Return to Menu  |  Ctrl+S: Save</style>'
            )
            
            result = self.session.prompt(
                f"\n[{config.USER_DISPLAY_NAME}] > ",
                key_bindings=bindings,
                bottom_toolbar=bottom_toolbar
            )
            return result
        except (EOFError, KeyboardInterrupt):
            return None

    def display_user_message(self, message):
        pass


    def display_assistant_stream(self, generator):
        # Get terminal width
        terminal_width = shutil.get_terminal_size().columns
        # Leave a small margin to be safe
        safe_width = terminal_width - 3
        
        # Print the assistant prefix
        prefix = f"\n[bold {config.SECONDARY_COLOR}]{config.MODEL_DISPLAY_NAME} >[/bold {config.SECONDARY_COLOR}] "
        self.console.print(prefix, end="")
        
        current_text = ""
        buffer = ""
        # Track current line length (start with prefix length, rough estimate)
        current_line_length = len(f"{config.MODEL_DISPLAY_NAME} > ")
        
        for token in generator:
            current_text += token
            buffer += token
            
            # Print when we hit whitespace/punctuation OR buffer gets long
            should_flush = (
                any(char in token for char in [' ', '\n', '\t', '.', ',', '!', '?', ';', ':']) 
                or len(buffer) > 20
            )
            
            if should_flush:
                # Check if this buffer would exceed terminal width
                if current_line_length + len(buffer) > safe_width:
                    # Insert a newline before printing
                    sys.stdout.write('\n')
                    current_line_length = 0
                
                sys.stdout.write(buffer)
                sys.stdout.flush()
                
                # Update line length tracker
                if '\n' in buffer:
                    # Reset to length after the last newline
                    last_newline_pos = buffer.rfind('\n')
                    current_line_length = len(buffer) - last_newline_pos - 1
                else:
                    current_line_length += len(buffer)
                
                buffer = ""
        
        # Print any remaining buffered text
        if buffer:
            if current_line_length + len(buffer) > safe_width:
                sys.stdout.write('\n')
            sys.stdout.write(buffer)
            sys.stdout.flush()
        
        self.console.print()  # Newline at end
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


