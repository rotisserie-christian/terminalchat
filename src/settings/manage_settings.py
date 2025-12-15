import sys
from rich.panel import Panel
import questionary
import src.config as config
from .input_helpers import get_text_input
from .model_parameters_menu import ModelParametersMenu


class ManageSettings:
    """
    Main settings configuration interface
    
    Allows user to manage:
    - Model (select from list/enter manually)
    - User Display Name
    - Model Display Name
    - Model Parameters (submenu)
    - Autosave Chat
    
    Settings are persisted to config.json
    """
    
    def __init__(self, console):
        self.console = console
        self.params_menu = ModelParametersMenu(console)
        config.load_config()
    
    def run(self):
        """Run the settings menu loop"""

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
                    "Model Parameters",
                    "Autosave Chat",
                    "Back"
                ],
                style=style,
                use_arrow_keys=True
            ).ask()

            if choice is None:
                sys.exit(0)
            
            if choice == "Back":
                break
            
            elif choice == "Model":
                self._configure_model(style)
            
            elif choice == "User Display Name":
                new_name = get_text_input(self.console, "User Display Name", config.USER_DISPLAY_NAME)
                if new_name and new_name.strip():
                    config.USER_DISPLAY_NAME = new_name.strip()

            elif choice == "Model Display Name":
                new_name = get_text_input(self.console, "Model Display Name", config.MODEL_DISPLAY_NAME)
                if new_name and new_name.strip():
                    config.MODEL_DISPLAY_NAME = new_name.strip()
            
            elif choice == "Model Parameters":
                self.params_menu.show(style)

            elif choice == "Autosave Chat":
                self._configure_autosave(style)

        # Save configuration
        if config.save_config():
            self.console.print(f"\n[green]✓ Configuration saved to {config.CONFIG_FILE}[/green]\n")
        else:
            self.console.print("\n[red]✗ Failed to save configuration[/red]\n")
    
    def _configure_model(self, style):
        """Handle model selection submenu"""

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

        if model_choice is None:
            sys.exit(0)

        if model_choice == "Select from popular models":
            selected_model = questionary.select(
                "Select Model",
                choices=[
                    "openai-community/gpt2-medium",
                    "openai-community/gpt2-large",
                    "google/gemma-2b-it",
                    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                    "HuggingFaceTB/SmolLM-135M-Instruct",
                    "Back"
                ],
                style=style,
                use_arrow_keys=True
            ).ask()
            
            if selected_model is None:
                sys.exit(0)
            
            if selected_model != "Back":
                config.MODEL_NAME = selected_model

        elif model_choice == "Enter manually":
            new_model = get_text_input(self.console, "Model", config.MODEL_NAME)
            if new_model and new_model.strip():
                config.MODEL_NAME = new_model.strip()
    
    def _configure_autosave(self, style):
        """Handle autosave toggle"""

        current_state = "enabled" if config.AUTOSAVE_ENABLED else "disabled"
        toggle_result = questionary.confirm(
            f"Autosave is currently {current_state}. Enable autosave?",
            default=config.AUTOSAVE_ENABLED,
            style=style
        ).ask()
        
        if toggle_result is None:
            sys.exit(0)
        
        config.AUTOSAVE_ENABLED = toggle_result
    
    def _show_summary(self):
        """Display current configuration summary"""

        autosave_status = "[green]Enabled[/green]" if config.AUTOSAVE_ENABLED else "[red]Disabled[/red]"
        self.console.print(Panel.fit(
            f"[bold]Current Configuration[/bold]\n\n"
            f"Model: [cyan]{config.MODEL_NAME}[/cyan]\n"
            f"User Display: [cyan]{config.USER_DISPLAY_NAME}[/cyan]\n"
            f"Model Display: [cyan]{config.MODEL_DISPLAY_NAME}[/cyan]\n"
            f"Primary Color: [cyan]{config.PRIMARY_COLOR}[/cyan]\n"
            f"Secondary Color: [cyan]{config.SECONDARY_COLOR}[/cyan]\n"
            f"Autosave: {autosave_status}",
            border_style="cyan"
        ))