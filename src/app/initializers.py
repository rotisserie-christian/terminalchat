import logging
from typing import Optional
from src.models import ModelHandler
from src.rag import RAGManager
from src.ui import TerminalUI
from src.exceptions import ModelLoadError, RAGError
import src.config as config

logger = logging.getLogger(__name__)


class ModelInitializer:
    """Handles model loading"""
    
    def __init__(self, ui: TerminalUI):
        self.ui = ui
    
    def load(self, model_name: str) -> Optional[ModelHandler]:
        """
        Load model
        
        Args:
            model_name: Model identifier
            
        Returns:
            ModelHandler if successful, None otherwise
        """

        self.ui.display_system_message(f"Initializing model: {model_name}")
        
        handler = ModelHandler(model_name)
        
        try:
            with self.ui.console.status("[bold green]Loading model..."):
                handler.load()
            
            logger.info(f"Model loaded: {model_name}")
            return handler
            
        except ModelLoadError as e:
            self.ui.display_error(f"Failed to load model: {e}")
            self.ui.display_system_message(
                "Check your model name in settings or internet connection."
            )
            return None
        except Exception as e:
            logger.critical(f"Unexpected error: {e}", exc_info=True)
            self.ui.display_error(f"Fatal error: {e}")
            return None


class RAGInitializer:
    """Handles RAG initialization"""
    
    def __init__(self, ui: TerminalUI):
        self.ui = ui
    
    def load(self) -> Optional[RAGManager]:
        """
        Initialize RAG system if enabled
        
        Returns:
            RAGManager if successful, None if disabled or failed
        """

        if not config.RAG_ENABLED:
            self.ui.display_system_message("RAG disabled (enable in Settings)")
            return None
        
        self.ui.display_system_message("Initializing RAG system...")
        manager = RAGManager()
        
        try:
            with self.ui.console.status("[bold green]Loading knowledge base..."):
                if not manager.load(show_progress=False):
                    return None
            
            stats = manager.get_stats()
            
            if stats['num_chunks'] == 0:
                self.ui.display_system_message(
                    "⚠ No files in /memory directory. RAG disabled."
                )
                return None
            
            self.ui.display_system_message(
                f"✓ RAG enabled: {stats['num_chunks']} chunks "
                f"from {stats['num_files']} files"
            )
            
            if stats['files']:
                self.ui.display_system_message(
                    f"  Files: {', '.join(stats['files'])}"
                )
            
            return manager
            
        except RAGError as e:
            logger.warning(f"RAG initialization failed: {e}")
            self.ui.display_error(f"RAG failed: {e}")
            self.ui.display_system_message("Continuing without RAG.")
            return None
        except Exception as e:
            logger.error(f"Unexpected RAG error: {e}", exc_info=True)
            self.ui.display_error("RAG system error.")
            return None


class ChatHistoryLoader:
    """Handles loading chat history"""
    
    def __init__(self, ui: TerminalUI, storage):
        self.ui = ui
        self.storage = storage
    
    def load(self, filename: str, context_manager) -> bool:
        """
        Load chat history into context manager
        
        Args:
            filename: Chat filename
            context_manager: Context manager to load into
            
        Returns:
            True if successful
        """

        try:
            messages = self.storage.load_chat(filename)
            context_manager.messages = messages
            
            self.ui.display_system_message(f"Chat loaded: {filename}")
            
            # Replay history
            for msg in messages:
                if msg['role'] == 'user':
                    self.ui.console.print(
                        f"\n[{config.USER_DISPLAY_NAME}] > {msg['content']}"
                    )
                elif msg['role'] == 'assistant':
                    self.ui.console.print(
                        f"\n[bold {config.SECONDARY_COLOR}]"
                        f"{config.MODEL_DISPLAY_NAME} >"
                        f"[/bold {config.SECONDARY_COLOR}] {msg['content']}"
                    )
            
            logger.info(f"Chat history loaded: {filename}")
            return True
            
        except FileNotFoundError:
            self.ui.display_error(f"Chat file not found: {filename}")
            return False
        except Exception as e:
            self.ui.display_error(f"Failed to load chat: {e}")
            return False