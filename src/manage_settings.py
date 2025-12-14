from rich.console import Console
from rich.panel import Panel
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style as PtStyle
import questionary
import sys
import src.config as config


class ManageSettings:
    """
    Allows user to manage these settings:

    - Model (select from list/enter manually)
    - User Display Name (enter manually)
    - Model Display Name (enter manually)
    - Model Parameters (temperature, top-k, top-p, max tokens)
    - Autosave Chat (enabled/disabled)

    Settings are persisted to config.json
    """
    
    def __init__(self, console):
        self.console = console
        config.load_config()
    
    def _get_input_with_esc(self, label: str, default: str) -> str | None:
        """
        Gets input for options that require manual entry 
        Esc key support to cancel.
        """
        bindings = KeyBindings()

        @bindings.add(Keys.Escape)
        def _(event):
            event.app.exit(result=None)

        style = PtStyle.from_dict({
            'prompt': f'ansi{config.PRIMARY_COLOR} bold',
        })
        
        session = PromptSession(key_bindings=bindings, style=style)
        
        try:
            self.console.print(f"\n[yellow]{label}[/yellow]")
            self.console.print(f"[dim]Current: {default} (Press Esc to go back)[/dim]")
            
            result = session.prompt(f"> ", default=default)
            return result
        except KeyboardInterrupt:
            sys.exit(0)
    
    def _get_float_input(self, label: str, current: float, min_val: float, max_val: float) -> float | None:
        """
        Get validated float input within a range.
        
        Args:
            label: Parameter name to display
            current: Current value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            float: Valid input value, or None if cancelled
        """
        bindings = KeyBindings()

        @bindings.add(Keys.Escape)
        def _(event):
            event.app.exit(result=None)

        style = PtStyle.from_dict({
            'prompt': f'ansi{config.PRIMARY_COLOR} bold',
        })
        
        session = PromptSession(key_bindings=bindings, style=style)
        
        while True:
            try:
                self.console.print(f"\n[yellow]{label}[/yellow]")
                self.console.print(f"[dim]Current: {current} | Range: {min_val}-{max_val} (Press Esc to go back)[/dim]")
                
                result = session.prompt(f"> ", default=str(current))
                
                if result is None:
                    return None
                
                # Try to parse as float
                try:
                    value = float(result)
                    
                    # Validate range
                    if value < min_val or value > max_val:
                        self.console.print(f"[red]Value must be between {min_val} and {max_val}[/red]")
                        continue
                    
                    return value
                    
                except ValueError:
                    self.console.print(f"[red]Invalid number. Please enter a value between {min_val} and {max_val}[/red]")
                    continue
                    
            except KeyboardInterrupt:
                sys.exit(0)
    
    def _get_int_input(self, label: str, current: int, min_val: int, max_val: int) -> int | None:
        """
        Get validated integer input within a range.
        
        Args:
            label: Parameter name to display
            current: Current value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            int: Valid input value, or None if cancelled
        """
        bindings = KeyBindings()

        @bindings.add(Keys.Escape)
        def _(event):
            event.app.exit(result=None)

        style = PtStyle.from_dict({
            'prompt': f'ansi{config.PRIMARY_COLOR} bold',
        })
        
        session = PromptSession(key_bindings=bindings, style=style)
        
        while True:
            try:
                self.console.print(f"\n[yellow]{label}[/yellow]")
                self.console.print(f"[dim]Current: {current} | Range: {min_val}-{max_val} (Press Esc to go back)[/dim]")
                
                result = session.prompt(f"> ", default=str(current))
                
                if result is None:
                    return None
                
                # Try to parse as int
                try:
                    value = int(result)
                    
                    # Validate range
                    if value < min_val or value > max_val:
                        self.console.print(f"[red]Value must be between {min_val} and {max_val}[/red]")
                        continue
                    
                    return value
                    
                except ValueError:
                    self.console.print(f"[red]Invalid number. Please enter an integer between {min_val} and {max_val}[/red]")
                    continue
                    
            except KeyboardInterrupt:
                sys.exit(0)
    
    def _configure_model_parameters(self, style):
        """Configure model generation parameters submenu."""
        while True:
            self.console.clear()
            self._show_parameters_summary()
            
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
                new_temp = self._get_float_input("Temperature", config.TEMPERATURE, 0.0, 2.0)
                if new_temp is not None:
                    config.TEMPERATURE = new_temp
            
            elif choice == "Top-k":
                new_top_k = self._get_int_input("Top-k", config.TOP_K, 1, 100)
                if new_top_k is not None:
                    config.TOP_K = new_top_k
            
            elif choice == "Top-p":
                new_top_p = self._get_float_input("Top-p", config.TOP_P, 0.0, 1.0)
                if new_top_p is not None:
                    config.TOP_P = new_top_p
            
            elif choice == "Max New Tokens":
                new_max_tokens = self._get_int_input("Max New Tokens", config.MAX_NEW_TOKENS, 1, 4096)
                if new_max_tokens is not None:
                    config.MAX_NEW_TOKENS = new_max_tokens

    def run(self):
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
            
            elif choice == "Model Parameters":
                self._configure_model_parameters(style)

            elif choice == "Autosave Chat":
                current_state = "enabled" if config.AUTOSAVE_ENABLED else "disabled"
                toggle_result = questionary.confirm(
                    f"Autosave is currently {current_state}. Enable autosave?",
                    default=config.AUTOSAVE_ENABLED,
                    style=style
                ).ask()
                
                if toggle_result is None:
                    sys.exit(0)
                
                config.AUTOSAVE_ENABLED = toggle_result

        # Save configuration
        if config.save_config():
            self.console.print(f"\n[green]✓ Configuration saved to {config.CONFIG_FILE}[/green]\n")
        else:
            self.console.print("\n[red]✗ Failed to save configuration[/red]\n")
    
    def _show_summary(self):
        """Display a summary of current configuration."""
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
    
    def _show_parameters_summary(self):
        """Display current model parameters."""
        self.console.print(Panel.fit(
            f"[bold]Model Parameters[/bold]\n\n"
            f"Temperature: [cyan]{config.TEMPERATURE}[/cyan]\n"
            f"Top-k: [cyan]{config.TOP_K}[/cyan]\n"
            f"Top-p: [cyan]{config.TOP_P}[/cyan]\n"
            f"Max New Tokens: [cyan]{config.MAX_NEW_TOKENS}[/cyan]",
            border_style="cyan"
        ))