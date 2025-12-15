import sys
import shutil
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
    """
    Handles all terminal UI interactions including menus, input, and output display.
    
    Manages Rich console for formatted output, prompt_toolkit for input,
    and questionary for interactive menus.
    """
    
    def __init__(self):
        # Rich console with custom theme
        custom_theme = Theme({
            "info": "dim cyan",
            "user": config.PRIMARY_COLOR,
            "assistant": config.SECONDARY_COLOR,
            "warning": "magenta",
            "danger": "bold red"
        })
        self.console = Console(theme=custom_theme)
        
        # Prompt toolkit session
        self.session = PromptSession(
            style=Style.from_dict({
                'prompt': f'ansi{config.PRIMARY_COLOR} bold',
                'bottom-toolbar': 'noinherit',
                'bottom-toolbar.text': 'fg:#909090'  # text color
            })
        )

        # Questionary menu style (used by all menus)
        self._menu_style = questionary.Style([
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
    
    def display_welcome(self):
        """
        Welcome box, displays title and portfolio link
        """

        self.console.print(
            Panel.fit(
                f"[bold {config.SECONDARY_COLOR}]Terminal Chat[/bold {config.SECONDARY_COLOR}]\n"
                f"[dim]christianwaters.dev[/dim]",
                border_style=config.SECONDARY_COLOR
            )
        )

    def get_input(self):
        """
        Get user input with keyboard shortcuts
        
        Shortcuts:
            Ctrl+C: Exit application
            Ctrl+R: Return to main menu
            Ctrl+S: Save chat
            
        Returns:
            str: User input, or special signals 'RETURN_TO_MENU'/'MANUAL_SAVE', 
                 or None on exit
        """
        bindings = KeyBindings()
        
        @bindings.add('c-r')
        def _(event):
            event.app.exit(result='RETURN_TO_MENU')
        
        @bindings.add('c-s')
        def _(event):
            event.app.exit(result='MANUAL_SAVE')
        
        try:
            def get_toolbar():
                return [('', 'Ctrl+C: Exit  |  Ctrl+R: Return to Menu  |  Ctrl+S: Save')]
            
            result = self.session.prompt(
                f"\n[{config.USER_DISPLAY_NAME}] > ",
                key_bindings=bindings,
                bottom_toolbar=get_toolbar
            )
            return result
        except (EOFError, KeyboardInterrupt):
            return None

    def display_model_stream(self, generator):
        """
        Display streaming response with word wrapping.
        
        Buffers tokens until whitespace/punctuation to avoid breaking words
        Manually wraps at terminal width to prevent mid-word breaks.
        
        Args:
            generator: Text token generator from model
            
        Returns:
            str: Complete assistant response
        """
        terminal_width = shutil.get_terminal_size().columns
        safe_width = terminal_width - 3
        
        # Print prefix
        prefix = f"\n[bold {config.SECONDARY_COLOR}]{config.MODEL_DISPLAY_NAME} >[/bold {config.SECONDARY_COLOR}] "
        self.console.print(prefix, end="")
        
        current_text = ""
        buffer = ""
        current_line_length = len(f"{config.MODEL_DISPLAY_NAME} > ")
        
        for token in generator:
            current_text += token
            buffer += token
            
            # Flush on whitespace/punctuation or when buffer gets long
            should_flush = (
                any(char in token for char in [' ', '\n', '\t', '.', ',', '!', '?', ';', ':']) 
                or len(buffer) > 20
            )
            
            if should_flush:
                # Check if buffer exceeds terminal width
                if current_line_length + len(buffer) > safe_width:
                    sys.stdout.write('\n')
                    current_line_length = 0
                
                sys.stdout.write(buffer)
                sys.stdout.flush()
                
                # Update line length tracker
                if '\n' in buffer:
                    last_newline_pos = buffer.rfind('\n')
                    current_line_length = len(buffer) - last_newline_pos - 1
                else:
                    current_line_length += len(buffer)
                
                buffer = ""
        
        # Flush remaining buffer
        if buffer:
            if current_line_length + len(buffer) > safe_width:
                sys.stdout.write('\n')
            sys.stdout.write(buffer)
            sys.stdout.flush()
        
        self.console.print()
        return current_text

    def display_system_message(self, message):
        """Display a dimmed system message."""
        self.console.print(f"[dim]{message}[/dim]")

    def display_error(self, message):
        """Display an error message."""
        self.console.print(f"[danger]Error: {message}[/danger]")

    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()

    def _show_menu(self, title, choices):
        """
        Menu display helper
        
        Args:
            title: Menu title string
            choices: List of strings (menu options)
            
        Returns:
            Selected choice string, or None if cancelled
        """
        try:
            choice = questionary.select(
                title,
                choices=choices,
                style=self._menu_style,
                use_arrow_keys=True
            ).ask()
            return choice
        except KeyboardInterrupt:
            return None

    def show_main_menu(self):
        """
        Display the main menu.
        
        Returns:
            str: Selected option ('New Chat', 'Load Chat', 'Settings', or 'Exit')
        """
        self.clear_screen()
        self.display_welcome()
        
        choice = self._show_menu(
            "Select an option:",
            ["New Chat", "Load Chat", "Settings", "Exit"]
        )
        return choice if choice else "Exit"

    def show_chat_selection(self, chats):
        """
        Display chat selection menu
        
        Args:
            chats: List of chat filenames
            
        Returns:
            str: Selected chat filename, or None if cancelled/no chats
        """
        if not chats:
            self.display_error("No saved chats found.")
            questionary.press_any_key_to_continue().ask()
            return None
        
        choices = chats + ["< Back"]
        choice = self._show_menu("Select a chat to load:", choices)
        
        if choice == "< Back" or choice is None:
            return None
        return choice