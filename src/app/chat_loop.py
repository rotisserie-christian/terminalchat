import logging
from typing import Optional
from src.app.session import ChatSession
from src.storage import ChatStorage
from src.ui import TerminalUI
from src.utils.exceptions import StorageError, ModelInferenceError
import src.config as config


logger = logging.getLogger(__name__)


class ChatLoop:
    """
    Handles the chat interaction loop
    
    Responsibilities:
    - Get user input
    - Generate responses
    - Save chat history
    - Handle special commands
    """
    
    def __init__(
        self,
        session: ChatSession,
        ui: TerminalUI,
        storage: ChatStorage,
        loaded_filename: Optional[str] = None
    ):
        """
        Initialize chat loop
        
        Args:
            session: Active chat session
            ui: Terminal UI instance
            storage: Chat storage instance
            loaded_filename: Optional loaded chat filename
        """

        self.session = session
        self.ui = ui
        self.storage = storage
        self.loaded_filename = loaded_filename
    
    def save_chat(self, auto: bool = False) -> bool:
        """
        Save current chat
        
        Args:
            auto: Whether this is an auto-save
            
        Returns:
            True if successful
        """

        try:
            saved_file = self.storage.save_chat(
                self.session.context_manager.get_messages(),
                self.loaded_filename
            )
            
            if self.loaded_filename is None:
                self.loaded_filename = saved_file
            
            msg = f"[dim]Auto-saved to {saved_file}[/dim]" if auto else f"Chat saved: {saved_file}"
            self.ui.display_system_message(msg)
            return True
            
        except StorageError as e:
            logger.warning(f"Save failed: {e}")
            self.ui.display_error(f"Failed to save: {e}")
            return False
    
    def handle_message(self, user_input: str) -> bool:
        """
        Process user message and generate response
        
        Args:
            user_input: User's message
            
        Returns:
            True to continue, False to exit
        """

        # Add user message
        self.session.context_manager.add_message("user", user_input)
        
        # Get RAG context
        rag_context = self.session.get_rag_context(user_input)
        if rag_context:
            tokens = len(self.session.model_handler.tokenizer.encode(rag_context))
            self.ui.display_system_message(f"[dim]Retrieved {tokens} tokens of context[/dim]")
        
        # Prepare prompt
        prompt = self.session.prepare_prompt(rag_context)
        
        # Generate response
        try:
            generator = self.session.generate_response(prompt)
            response = self.ui.display_model_stream(generator)
            self.session.context_manager.add_message("assistant", response)
            
            # Auto-save
            if config.AUTOSAVE_ENABLED:
                self.save_chat(auto=True)
            
            return True
            
        except KeyboardInterrupt:
            self.ui.display_system_message("\nGeneration interrupted.")
            return False
        except ModelInferenceError as e:
            self.ui.display_error(f"Generation failed: {e}")
            return True
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            self.ui.display_error(f"Error: {e}")
            return True
    
    def run(self) -> bool:
        """
        Run the chat loop
        
        Returns:
            True if should return to menu, False if should exit
        """

        while True:
            user_input = self.ui.get_input()
            
            # Special commands
            if user_input == 'MANUAL_SAVE':
                self.save_chat(auto=False)
                continue
            
            if user_input == 'RETURN_TO_MENU':
                self.ui.display_system_message("Returning to menu...")
                return True
            
            if user_input is None:
                return False
            
            if not user_input.strip():
                continue
            
            # Process message
            should_continue = self.handle_message(user_input)
            if not should_continue:
                return False