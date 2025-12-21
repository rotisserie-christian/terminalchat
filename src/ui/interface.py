from .display import DisplayManager
from .input import InputManager
from .menus import MenuManager


class TerminalUI:
    """
    Handles all terminal UI interactions including menus, input, and output display
    
    Manages:
    - Rich console for formatted output
    - Prompt_toolkit for input
    - Questionary for interactive menus
    """
    
    def __init__(self):
        self._display = DisplayManager()
        self._input = InputManager()
        self._menus = MenuManager(self._display)
    
    # Expose console for backward compatibility
    @property
    def console(self):
        """Access to the Rich console instance"""
        return self._display.console
    
    # Display methods
    def display_welcome(self):
        """Welcome box, displays title and portfolio link"""
        self._display.display_welcome()
    
    def display_model_stream(self, generator):
        """
        Display streaming response with word wrapping
        
        Args:
            generator: Text token generator from model
            
        Returns:
            str: Complete assistant response
        """
        return self._display.display_model_stream(generator)
    
    def display_system_message(self, message):
        """Display a dimmed system message"""
        self._display.display_system_message(message)
    
    def display_error(self, message):
        """Display an error message"""
        self._display.display_error(message)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        self._display.clear_screen()
    
    # Input methods
    def get_input(self):
        """
        Get user input with keyboard shortcuts
        
        Returns:
            str: User input, or special signals 'RETURN_TO_MENU'/'MANUAL_SAVE', 
                 or None on exit
        """
        return self._input.get_input()
    
    # Menu methods
    def show_main_menu(self):
        """
        Display the main menu
        
        Returns:
            str: Selected option ('New Chat', 'Load Chat', 'Settings', or 'Exit')
        """
        return self._menus.show_main_menu()
    
    def show_chat_selection(self, chats):
        """
        Display chat selection menu
        
        Args:
            chats: List of chat filenames
            
        Returns:
            str: Selected chat filename, or None if cancelled/no chats
        """
        return self._menus.show_chat_selection(chats)

