"""Setup sequence for Terminal Chat configuration."""
from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style as PtStyle
import questionary
import src.config as config

class SetupSequence:
    def __init__(self, console):
        self.console = console
        config.load_config()
    
    def _get_input_with_esc(self, label: str, default: str) -> str | None:
        """Get input with Esc key support to cancel."""
        bindings = KeyBindings()

        @bindings.add(Keys.Escape)
        def _(event):
            event.app.exit(result=None)

        # Style matching the app theme roughly
        style = PtStyle.from_dict({
            'prompt': f'ansi{config.PRIMARY_COLOR} bold',
        })
        
        session = PromptSession(key_bindings=bindings, style=style)
        
        try:
            # Print label manually using rich for consistency before the prompt
            self.console.print(f"\n[yellow]{label}[/yellow]")
            self.console.print(f"[dim]Current: {default} (Press Esc to go back)[/dim]")
            
            result = session.prompt(f"> ", default=default)
            return result
        except KeyboardInterrupt:
            return None # Treat Ctrl+C same as Esc/Cancel in this context if desired, or let it propagate.
            # Usually Ctrl+C exits app, but here we might just want to go back.
            # Let's return None to go back.
            return None

    def run(self):
        """Run the setup sequence."""
        # Common style for consistent UI
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

        while True:
            self.console.clear()
            self._show_summary()
            
            choice = questionary.select(
                "Settings Menu",
                choices=[
                    "Model",
                    "User Display Name",
                    "Model Display Name",
                    "Back"
                ],
                style=style,
                use_arrow_keys=True
            ).ask()

            if choice == "Back":
                break
            
            elif choice == "Model":
                model_choice = questionary.select(
                    "Model Selection",
                    choices=[
                        "Select from popular models",
                        "Enter manually",
                        "Back"
                    ],
                    style=style,
                    use_arrow_keys=True
                ).ask()

                if model_choice == "Select from popular models":
                    selected_model = questionary.select(
                        "Select Model",
                        choices=[
                            "Qwen/Qwen2.5-1.5B-Instruct",
                            "microsoft/phi-2",
                            "google/gemma-2b-it",
                            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                            "HuggingFaceTB/SmolLM-135M-Instruct",
                            "Back"
                        ],
                        style=style,
                        use_arrow_keys=True
                    ).ask()
                    
                    if selected_model != "Back":
                        config.MODEL_NAME = selected_model

                elif model_choice == "Enter manually":
                    new_model = self._get_input_with_esc("Model", config.MODEL_NAME)
                    if new_model and new_model.strip():
                         config.MODEL_NAME = new_model.strip()

            elif choice == "User Display Name":
                new_user_name = self._get_input_with_esc("User Display Name", config.USER_DISPLAY_NAME)
                if new_user_name and new_user_name.strip():
                    config.USER_DISPLAY_NAME = new_user_name.strip()

            elif choice == "Model Display Name":
                new_model_name = self._get_input_with_esc("Model Display Name", config.MODEL_DISPLAY_NAME)
                if new_model_name and new_model_name.strip():
                    config.MODEL_DISPLAY_NAME = new_model_name.strip()

        # Save configuration
        if config.save_config():
            self.console.print(f"\n[green]✓ Configuration saved to {config.CONFIG_FILE}[/green]\n")
        else:
            self.console.print("\n[red]✗ Failed to save configuration[/red]\n")
    
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

