"""Setup sequence for Terminal Chat configuration."""
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import src.config as config

class SetupSequence:
    def __init__(self):
        self.console = Console()
        config.load_config()
    
    def run(self):
        """Run the setup sequence."""
        self.console.print("\n[bold]Press Enter while blank to use the default option[/bold]\n")
        
        # Model
        self.console.print("[yellow]Model[/yellow]")
        current_model = config.MODEL_NAME
        new_model = Prompt.ask(
            f"Default = [blue]{current_model}[/blue]",
            default=current_model,
            show_default=False
        )
        if new_model.strip():
            config.MODEL_NAME = new_model.strip()
        
        # User display name
        self.console.print("\n[yellow]User Display Name[/yellow]")
        new_user_name = Prompt.ask(
            f"Default = [blue]{config.USER_DISPLAY_NAME}[/blue]",
            default=config.USER_DISPLAY_NAME,
            show_default=False
        )
        if new_user_name.strip():
            config.USER_DISPLAY_NAME = new_user_name.strip()
        
        # Model display name
        self.console.print("\n[yellow]Model Display Name[/yellow]")
        new_model_name = Prompt.ask(
            f"Default = [blue]{config.MODEL_DISPLAY_NAME}[/blue]",
            default=config.MODEL_DISPLAY_NAME,
            show_default=False
        )
        if new_model_name.strip():
            config.MODEL_DISPLAY_NAME = new_model_name.strip()
        
        # Save configuration
        if config.save_config():
            self.console.print(f"\n[green]✓ Configuration saved to {config.CONFIG_FILE}[/green]\n")
        else:
            self.console.print("\n[red]✗ Failed to save configuration[/red]\n")
        
        # Show summary
        self._show_summary()
    
    def _show_summary(self):
        """Display a summary of current configuration."""
        self.console.print(Panel.fit(
            f"[bold]Current Configuration[/bold]\n\n"
            f"Model: [cyan]{config.MODEL_NAME}[/cyan]\n"
            f"User Display: [cyan]{config.USER_DISPLAY_NAME}[/cyan]\n"
            f"Model Display: [cyan]{config.MODEL_DISPLAY_NAME}[/cyan]\n"
            f"Primary Color: [cyan]{config.PRIMARY_COLOR}[/cyan]\n"
            f"Secondary Color: [cyan]{config.SECONDARY_COLOR}[/cyan]",
            border_style="cyan"
        ))
        self.console.print()

