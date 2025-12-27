import sys
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme
import src.config as config


class DisplayManager:
    """Manages all display output using Rich console"""
    
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
    
    def display_welcome(self):
        """Welcome box, displays title and portfolio link"""
        self.console.print(
            Panel.fit(
                f"[bold {config.SECONDARY_COLOR}]Terminal Chat[/bold {config.SECONDARY_COLOR}]\n"
                f"[dim]christianwaters.dev[/dim]",
                border_style=config.SECONDARY_COLOR
            )
        )

    def display_model_stream(self, generator):
        """
        Display streaming response with word wrapping
        
        Buffers tokens until whitespace/punctuation to avoid breaking words
        Manually wraps at terminal width to prevent mid-word breaks
        
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
        """Display a dimmed system message"""
        self.console.print(f"[dim]{message}[/dim]")

    def display_error(self, message):
        """Display an error message"""
        self.console.print(f"[danger]Error: {message}[/danger]")

    def clear_screen(self):
        """Clear the terminal screen"""
        self.console.clear()
