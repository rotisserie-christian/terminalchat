import sys
from rich.panel import Panel
import questionary
import src.config as config
from .input_helpers import get_float_input, get_int_input


class ModelParametersMenu:
    """Handles the model parameters submenu."""
    
    def __init__(self, console):
        self.console = console
    
    def show(self, style):
        """
        Display and handle the model parameters submenu.
        
        Args:
            style: Menu styling object
        """
        while True:
            self.console.clear()
            self._show_summary()
            
            choice = questionary.select(
                "Model Parameters",
                choices=[
                    "Temperature",
                    "Top-k", 
                    "Top-p",
                    "Max New Tokens",
                    "Back"
                ],
                style=style,
                use_arrow_keys=True
            ).ask()
            
            if choice is None:
                sys.exit(0)
            
            if choice == "Back":
                break
            
            elif choice == "Temperature":
                new_temp = get_float_input(self.console, "Temperature", config.TEMPERATURE, 0.0, 2.0)
                if new_temp is not None:
                    config.TEMPERATURE = new_temp
            
            elif choice == "Top-k":
                new_top_k = get_int_input(self.console, "Top-k", config.TOP_K, 1, 100)
                if new_top_k is not None:
                    config.TOP_K = new_top_k
            
            elif choice == "Top-p":
                new_top_p = get_float_input(self.console, "Top-p", config.TOP_P, 0.0, 1.0)
                if new_top_p is not None:
                    config.TOP_P = new_top_p
            
            elif choice == "Max New Tokens":
                new_max_tokens = get_int_input(self.console, "Max New Tokens", config.MAX_NEW_TOKENS, 1, 4096)
                if new_max_tokens is not None:
                    config.MAX_NEW_TOKENS = new_max_tokens
    
    def _show_summary(self):
        """Display current model parameters."""
        self.console.print(Panel.fit(
            f"[bold]Model Parameters[/bold]\n\n"
            f"Temperature: [cyan]{config.TEMPERATURE}[/cyan]\n"
            f"Top-k: [cyan]{config.TOP_K}[/cyan]\n"
            f"Top-p: [cyan]{config.TOP_P}[/cyan]\n"
            f"Max New Tokens: [cyan]{config.MAX_NEW_TOKENS}[/cyan]",
            border_style="cyan"
        ))