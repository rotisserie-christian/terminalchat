"""Terminal Chat - Main entry point."""

import sys
import logging

from src.storage import ChatStorage
from src.ui import TerminalUI
from src.settings import ManageSettings
import src.config as config
from src.exceptions import ConfigError

# Import app components after config is loaded
logger = logging.getLogger(__name__)


def start_chat_session(
    ui: TerminalUI,
    storage: ChatStorage,
    loaded_filename: str = None
) -> bool:
    """
    Start a chat session.
    
    Returns:
        True to return to menu, False to exit
    """
    # Import here to avoid circular imports
    from src.app import (
        ChatSession, ChatLoop,
        ModelInitializer, RAGInitializer, ChatHistoryLoader
    )
    
    # Initialize components
    model_init = ModelInitializer(ui)
    rag_init = RAGInitializer(ui)
    history_loader = ChatHistoryLoader(ui, storage)
    
    # Load model
    model_handler = model_init.load(config.MODEL_NAME)
    if not model_handler:
        return True  # Return to menu
    
    # Load RAG
    rag_manager = rag_init.load()
    
    # Create session
    session = ChatSession(model_handler, rag_manager)
    
    # Load history if requested
    if loaded_filename:
        history_loader.load(loaded_filename, session.context_manager)
    
    # Run chat loop
    chat_loop = ChatLoop(session, ui, storage, loaded_filename)
    return chat_loop.run()


def main():
    """Main entry point."""
    # Basic logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info("Terminal Chat starting...")
    
    # Load config FIRST, before creating UI
    try:
        config.load_config()
    except ConfigError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    
    # NOW create UI (after config is loaded)
    ui = TerminalUI()
    storage = ChatStorage()
    
    # Main menu loop
    while True:
        choice = ui.show_main_menu()
        
        if choice == "Exit":
            sys.exit(0)
        
        elif choice == "Settings":
            ManageSettings(ui.console).run()
            config.load_config()
        
        elif choice == "Load Chat":
            chats = storage.list_chats()
            selected = ui.show_chat_selection(chats)
            if selected:
                should_return = start_chat_session(ui, storage, selected)
                if not should_return:
                    sys.exit(0)
        
        elif choice == "New Chat":
            should_return = start_chat_session(ui, storage)
            if not should_return:
                sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        print(f"\nFatal error: {e}")
        sys.exit(1)