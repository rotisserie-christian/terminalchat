from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
import src.config as config


class InputManager:
    """Manages user input with keyboard shortcuts"""

    def __init__(self):
        # Prompt toolkit session
        self.session = PromptSession(
            style=Style.from_dict({
                'prompt': f'ansi{config.PRIMARY_COLOR} bold',
                'bottom-toolbar': 'noinherit',
                'bottom-toolbar.text': 'fg:#909090'  # text color
            })
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
