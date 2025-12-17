import sys
from rich.panel import Panel
import questionary
import src.config as config
from .input_helpers import get_float_input, get_int_input


class RAGSettingsMenu:
    """Handles the RAG settings submenu."""
    
    def __init__(self, console):
        self.console = console
    
    def show(self, style):
        """
        Display and handle the RAG settings submenu.
        
        Args:
            style: Menu styling object
        """
        while True:
            self.console.clear()
            self._show_summary()
            
            choice = questionary.select(
                "RAG Settings",
                choices=[
                    "Enable/Disable RAG",
                    "Context Percentage",
                    "Top-K Retrieval",
                    "Back"
                ],
                style=style,
                use_arrow_keys=True
            ).ask()
            
            if choice is None:
                sys.exit(0)
            
            if choice == "Back":
                break
            
            elif choice == "Enable/Disable RAG":
                self._toggle_rag(style)
            
            elif choice == "Context Percentage":
                new_percentage = get_float_input(
                    self.console, 
                    "RAG Context Percentage (0.10 = 10%, 0.50 = 50%)", 
                    config.RAG_CONTEXT_PERCENTAGE, 
                    0.05, 
                    0.50
                )
                if new_percentage is not None:
                    config.RAG_CONTEXT_PERCENTAGE = new_percentage
            
            elif choice == "Top-K Retrieval":
                new_top_k = get_int_input(
                    self.console, 
                    "Top-K (number of chunks to consider)", 
                    config.RAG_TOP_K, 
                    1, 
                    50
                )
                if new_top_k is not None:
                    config.RAG_TOP_K = new_top_k
    
    def _toggle_rag(self, style):
        """Handle RAG enable/disable toggle."""
        current_state = "enabled" if config.RAG_ENABLED else "disabled"
        toggle_result = questionary.confirm(
            f"RAG is currently {current_state}. Enable RAG?",
            default=config.RAG_ENABLED,
            style=style
        ).ask()
        
        if toggle_result is None:
            sys.exit(0)
        
        config.RAG_ENABLED = toggle_result
    
    def _show_summary(self):
        """Display current RAG settings."""
        rag_status = "[green]Enabled[/green]" if config.RAG_ENABLED else "[red]Disabled[/red]"
        percentage_display = f"{int(config.RAG_CONTEXT_PERCENTAGE * 100)}%"
        
        self.console.print(Panel.fit(
            f"[bold]RAG Settings[/bold]\n\n"
            f"Status: {rag_status}\n"
            f"Context Percentage: [cyan]{percentage_display}[/cyan]\n"
            f"Top-K Retrieval: [cyan]{config.RAG_TOP_K}[/cyan]\n\n"
            f"[dim]RAG uses files from the /memory directory to provide\n"
            f"context-aware responses based on your knowledge base.[/dim]",
            border_style="cyan"
        ))